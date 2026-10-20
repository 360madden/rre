"""Strict file-only provenance checks for existing RR2 screenshot evidence."""
from __future__ import annotations
from datetime import datetime
import hashlib
import io
import json
from pathlib import Path, PurePosixPath
import re
import warnings
from PIL import Image
from .matcher import require

MAX_FILE = 32 * 1024 * 1024
MAX_JSON = 8 * 1024 * 1024
MAX_TOTAL = 128 * 1024 * 1024
MAX_PIXELS = 8_388_608


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def bounded_read(path, limit=MAX_FILE):
    require(path.is_file(), "Missing evidence file: " + path.name)
    with path.open("rb") as stream:
        raw = stream.read(limit + 1)
    require(0 < len(raw) <= limit, "Empty or oversized evidence file: " + path.name)
    return raw


def json_bytes(raw):
    require(len(raw) <= MAX_JSON, "JSON exceeds limit")
    def pairs(items):
        out = {}
        for key, value in items:
            require(key not in out, "Duplicate JSON key")
            out[key] = value
        return out
    def constant(_):
        raise ValueError("Nonfinite JSON")
    obj = json.loads(raw.decode("utf-8-sig"), object_pairs_hook=pairs, parse_constant=constant)
    # Validate escaped Unicode and exponent overflow even in ignored fields.
    json.dumps(obj, ensure_ascii=False, allow_nan=False).encode("utf-8")
    return obj


def token(value, label="ID"):
    require(isinstance(value, str) and re.fullmatch(r"[A-Za-z0-9_-]{1,100}", value), "Invalid " + label)
    return value


def digest(value):
    require(isinstance(value, str) and re.fullmatch(r"[0-9a-fA-F]{64}", value), "Invalid SHA256")
    return value.lower()


def integer(value, label, minimum=0, maximum=2**63-1):
    require(type(value) is int and minimum <= value <= maximum, "Invalid " + label)
    return value


def text(value, label):
    require(isinstance(value, str) and 0 < len(value) <= 1024 and not any(ord(c)<32 for c in value),
            "Invalid " + label)
    return value


def timestamp(value):
    result = datetime.fromisoformat(text(value, "timestamp").replace("Z", "+00:00"))
    require(result.tzinfo is not None, "Timestamp requires timezone")
    return result


def local_path(root, name):
    require(isinstance(name, str) and 0 < len(name) <= 512 and "\\" not in name, "Invalid relative path")
    parts = PurePosixPath(name).parts
    require(parts and all(re.fullmatch(r"[A-Za-z0-9_.-]+", p) and p not in (".", "..", ".git") for p in parts),
            "Unsafe evidence path")
    current = root
    for part in parts:
        current /= part
        require(not current.is_symlink() and not current.is_junction(), "Linked evidence paths forbidden")
    require(current.resolve().is_relative_to(root.resolve()), "Evidence path escapes root")
    return current


def target(value):
    require(isinstance(value, dict), "Missing target identity")
    result = {k: text(value.get(k), k) for k in ("machineName", "windowHandle", "executablePath")}
    result["executableSha256"] = digest(value.get("executableSha256"))
    for k in ("processId", "processStartUtcTicks"):
        result[k] = integer(value.get(k), k, 1)
    for k in ("clientWidth", "clientHeight"):
        result[k] = integer(value.get(k), k, 1, 4096)
    for k in ("clientX", "clientY"):
        result[k] = integer(value.get(k), k, -100000, 100000)
    require(type(value.get("isForeground")) is bool, "Missing foreground evidence")
    result["isForeground"] = value["isForeground"]
    return result


def vm_identity(value):
    require(isinstance(value, dict), "Missing VM identity")
    return {"vmx": text(value.get("vmx"), "vmx").replace("\\", "/").casefold(),
            "pid": integer(value.get("pid"), "VM PID", 1),
            "startTicks": integer(value.get("startTicks"), "VM start ticks", 1)}


def decode_image(raw):
    with warnings.catch_warnings():
        warnings.simplefilter("error", Image.DecompressionBombWarning)
        with Image.open(io.BytesIO(raw)) as image:
            require(image.format in ("BMP", "PNG", "JPEG"), "Unsupported image format")
            require(getattr(image, "n_frames", 1) == 1, "Animated images forbidden")
            w, h = image.size
            require(1 <= w <= 4096 and 1 <= h <= 4096 and w*h <= MAX_PIXELS, "Image dimension limit")
            image.load()  # Decode the same bytes whose hash was checked.
            return image.convert("RGB")


class Assets:
    def __init__(self, root):
        self.root = root.resolve()
        self.raw = {}
        self.total = 0

    def get(self, ref):
        require(isinstance(ref, dict) and set(ref) == {"path", "sha256"}, "Invalid file reference")
        expected = digest(ref["sha256"])
        key = ref["path"]
        if key not in self.raw:
            raw = bounded_read(local_path(self.root, key))
            self.total += len(raw)
            require(self.total <= MAX_TOTAL and len(self.raw) < 40, "Evidence bundle limit")
            self.raw[key] = raw
        raw = self.raw[key]
        require(sha(raw) == expected, "Evidence hash mismatch: " + key)
        return raw

    def json(self, ref):
        return json_bytes(self.get(ref))


def load_frames(spec, assets):
    rows = spec.get("frames")
    require(isinstance(rows, list) and 2 <= len(rows) <= 8, "Require two to eight frames")
    frames = {}
    for row in rows:
        require(isinstance(row, dict) and set(row) == {"id", "image", "capture"}, "Invalid frame entry")
        key = token(row["id"])
        require(key not in frames, "Duplicate frame ID")
        raw = assets.get(row["image"])
        cap = assets.json(row["capture"])
        require(isinstance(cap, dict), "Invalid capture metadata")
        token(cap.get("captureId"), "capture ID")
        timestamp(cap.get("capturedAtUtc"))
        text(cap.get("captureBackend"), "capture backend")
        require(digest(cap.get("sha256")) == sha(raw), "Capture/image hash mismatch")
        saved = cap.get("savedImage")
        require(isinstance(saved, dict) and digest(saved.get("sha256")) == sha(raw) and
                integer(saved.get("byteLength"), "saved image size", 1, MAX_FILE) == len(raw), "Saved image mismatch")
        image = decode_image(raw)
        ident = target(cap.get("target"))
        require(image.size == (ident["clientWidth"], ident["clientHeight"]), "Capture dimensions mismatch")
        frames[key] = {"capture": cap, "image": image, "target": ident, "sha256": sha(raw), "ref": row}
    require(len({v["capture"]["captureId"] for v in frames.values()}) == len(frames), "Reused capture ID")
    return frames


def load_actions(spec, assets):
    rows = spec.get("actions")
    require(isinstance(rows, list) and len(rows) <= 8, "Invalid actions")
    actions = {}
    for row in rows:
        require(isinstance(row, dict) and set(row) == {"id", "result"}, "Invalid action entry")
        key = token(row["id"])
        require(key not in actions, "Duplicate action ID")
        data = assets.json(row["result"])
        require(isinstance(data, dict) and isinstance(data.get("result"), dict) and isinstance(data.get("action"), dict),
                "Invalid action result")
        require(timestamp(data.get("startedAtUtc")) <= timestamp(data.get("completedAtUtc")), "Action time reversed")
        target(data.get("target"))
        for k in ("deliverySucceeded", "releaseSucceeded", "stateUncertain", "targetLost", "cancelled", "responseVerified"):
            require(type(data["result"].get(k)) is bool, "Invalid action state: " + k)
        require(type(data.get("recoveryRequired")) is bool, "Invalid recovery state")
        actions[key] = data
    return actions


def journal_rows(ref, assets):
    if ref is None:
        return []
    raw = assets.get(ref)
    require(len(raw) <= MAX_JSON, "Journal exceeds limit")
    lines = raw.splitlines()
    require(len(lines) <= 20000, "Journal row limit")
    rows = []
    for line in lines:
        if line.strip():
            row = json_bytes(line)
            require(isinstance(row, dict) and type(row.get("schemaVersion")) is int and row["schemaVersion"] == 1,
                    "Unsupported journal schema")
            timestamp(row.get("recordedAtUtc"))
            rows.append(row)
    return rows


def journal_index(rows):
    captures, actions, requests = {}, {}, []
    connection = None
    for index, row in enumerate(rows):
        kind, value = row.get("evidenceKind"), row.get("value")
        require(isinstance(value, dict), "Invalid journal value")
        if kind == "control-guest-connected/1":
            connection = value
        elif kind == "control-guest-disconnected/1":
            connection = None
        elif kind == "control-capture/1":
            captures.setdefault(value.get("captureId"), []).append((index, value, connection))
        elif kind == "control-command-response/1" and value.get("operation") == "action":
            actions.setdefault(value.get("id"), []).append((index, value.get("payload"), connection))
        elif kind == "control-command-request/1" and value.get("operation") == "action":
            requests.append((index, value.get("id")))
    return captures, actions, requests


def binding(before, after, selected, rows, expected_vm):
    """Return reasons rather than promoting an incomplete history to a valid trial."""
    reasons, command_ids = [], []
    if before["target"] != after["target"]:
        reasons.append("target-or-geometry-changed")
    if not before["target"]["isForeground"] or not after["target"]["isForeground"]:
        reasons.append("foreground-not-established")
    if before["capture"]["captureBackend"] != after["capture"]["captureBackend"]:
        reasons.append("capture-backend-changed")
    if before["sha256"] == after["sha256"]:
        reasons.append("identical-image-bytes-freshness-ambiguous")
    t0, t1 = (timestamp(f["capture"]["capturedAtUtc"]) for f in (before, after))
    if t1 <= t0 or (t1-t0).total_seconds() > 60:
        reasons.append("invalid-or-too-wide-capture-interval")
    for action in selected:
        if target(action["target"]) != before["target"]:
            reasons.append("action-target-mismatch")
        start, end = timestamp(action["startedAtUtc"]), timestamp(action["completedAtUtc"])
        if not t0 <= start <= end <= t1:
            reasons.append("action-not-bracketed-by-frames")
        r = action["result"]
        if not r["deliverySucceeded"] or not r["releaseSucceeded"] or r["stateUncertain"] or r["targetLost"] or r["cancelled"] or action["recoveryRequired"]:
            reasons.append("action-delivery-or-release-unqualified")
    if selected:
        if (timestamp(selected[0]["startedAtUtc"])-t0).total_seconds()>45 or (t1-timestamp(selected[-1]["completedAtUtc"])).total_seconds()>5:
            reasons.append("capture-action-gap-exceeds-policy")
    else:
        reasons.append("no-action-evidence")
    if not rows or expected_vm is None:
        return sorted(set(reasons + ["missing-journal-or-expected-vm"])), command_ids
    captures, actions, requests = journal_index(rows)
    contexts, positions = [], []
    for f in (before, after):
        cap = f["capture"]
        matches = captures.get(cap["captureId"], [])
        if len(matches) != 1:
            reasons.append("missing-or-ambiguous-journal-capture")
            continue
        index, entry, ctx = matches[0]
        if any(entry.get(k) != cap.get(k) for k in ("captureId", "sha256", "capturedAtUtc", "captureBackend", "target")):
            reasons.append("journal-capture-disagreement")
        contexts.append(ctx)
        positions.append(index)
    action_positions = []
    for selected_action in selected:
        matches = [(key, item) for key, group in actions.items() for item in group if item[1] == selected_action]
        if len(matches) != 1:
            reasons.append("missing-or-ambiguous-journal-action")
            continue
        key, (index, _, ctx) = matches[0]
        command_ids.append(key)
        contexts.append(ctx)
        action_positions.append(index)
    if len(positions) == 2:
        if not positions[0] < positions[1] or any(not positions[0] < i < positions[1] for i in action_positions):
            reasons.append("journal-order-mismatch")
        between = [key for i, key in requests if positions[0] < i < positions[1]]
        if between != command_ids:
            reasons.append("unaccounted-or-reordered-actions")
    instance_ids = []
    for ctx in contexts:
        if not isinstance(ctx, dict):
            reasons.append("missing-connection-context")
            continue
        try:
            if vm_identity(ctx.get("vmIdentity")) != vm_identity(expected_vm):
                reasons.append("wrong-vm-epoch")
            if ctx.get("machineName") != before["target"]["machineName"] or ctx.get("connected") is not True:
                reasons.append("guest-connection-mismatch")
            instance_ids.append(token(ctx.get("instanceId"), "receiver instance"))
        except ValueError:
            reasons.append("invalid-vm-connection-context")
    if len(set(instance_ids)) != 1:
        reasons.append("receiver-reconnected-or-unbound")
    return sorted(set(reasons)), command_ids
