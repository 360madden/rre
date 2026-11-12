"""SC-306: validate a saved Ability Queue UI/native evidence bracket offline.

No game/process input. Works on the existing RRE reader JSON and original UI PNGs.
The user must independently inspect both images and supply the visible label and
capture times; this program cannot read the label from image pixels.
"""
from __future__ import annotations

import argparse
import base64
import hashlib
import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

KNOWN_BUILD_SHA = "1935A05C9DB6D468E34E0055014A4A99C1B5AFCEB1695884E24600F5C20A4BE8"
ROOT_RVA = 0x33958C0
FIELD_OFFSET = 0xA4
ALLOWED_LABELS = {"Full", "Short", "None"}
KNOWN_PAIR = (1, "Short")
EXPECTED_CAPTURE_VMX = r"c:\rift modding\vms\rift-lab-2\rift-lab.vmx"

# Exact-build source-qualified loaded windows from SC-305/SC-613.
CHUNKS = {
    0xBD2DA7: (39, "731E0502754E3DDE57EA0DB34A4EB4ADAD359BA70DDA34D1D5CC609B83EB79A3"),
    0xBD7153: (6, "655ABD11AB2C91FFB7C7B12CDA9E016F2B3D591EECC7AFF8D8C79AAE3F6506D2"),
    0x26ECC70: (24, "CBD78C94E03790876F2E2161BD40FAB077FE081F199C4BEF37D543D9392F9FF9"),
}


class EvidenceError(ValueError):
    pass


def check(condition: bool, reason: str) -> None:
    if not condition:
        raise EvidenceError(reason)


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest().upper()


def decode64(encoded: str, label: str) -> bytes:
    try:
        return base64.b64decode(encoded, validate=True)
    except (ValueError, TypeError) as exc:
        raise EvidenceError(f"{label}: invalid base64") from exc


def utc_time(text: str) -> datetime:
    try:
        value = datetime.fromisoformat(text.replace("Z", "+00:00"))
    except (ValueError, TypeError, AttributeError) as exc:
        raise EvidenceError(f"invalid UTC timestamp: {text}") from exc
    check(value.tzinfo is not None, "timestamps require a timezone")
    return value.astimezone(timezone.utc)


def read_json(path: Path) -> dict:
    try:
        value = json.loads(path.read_text(encoding="utf-8-sig"))
    except (ValueError, OSError) as exc:
        raise EvidenceError(f"{path}: unreadable JSON") from exc
    check(isinstance(value, dict), f"{path}: expected JSON object")
    return value


def check_issued_request(folder: Path, stem: str, declared_sha: str,
                         expected_kind: str) -> None:
    """Bind producer-declared hashes to exact guest-request bytes, not Git EOL."""
    raw = (folder / f"{stem}.request.json").read_bytes()
    # The original acquisition saved one terminal LF. A Windows Git checkout
    # may convert that single final LF to CRLF; the guest received neither.
    if raw.endswith(b"\r\n"):
        guest_bytes = raw[:-2]
    elif raw.endswith(b"\n"):
        guest_bytes = raw[:-1]
    else:
        raise EvidenceError(f"{stem}: saved request lacks one terminal newline")
    check(b"\n" not in guest_bytes and b"\r" not in guest_bytes,
          f"{stem}: saved request is not single-line compact JSON")
    try:
        request = json.loads(guest_bytes.decode("utf-8"))
    except (UnicodeError, ValueError) as exc:
        raise EvidenceError(f"{stem}: malformed saved request") from exc
    check(isinstance(request, dict)
          and request.get("evidenceKind") == expected_kind,
          f"{stem}: unexpected saved request kind")
    check(sha256(guest_bytes) == str(declared_sha).upper(),
          f"{stem}: request SHA mismatch")


def same_identity(a: dict, b: dict) -> bool:
    numbers = ("processId", "processStartUtcTicks", "moduleBaseAddress", "moduleSize")
    strings = ("executablePath", "executableSha256")
    try:
        return (all(int(str(a[k]), 0) == int(str(b[k]), 0) for k in numbers)
                and all(str(a[k]).casefold() == str(b[k]).casefold() for k in strings))
    except (KeyError, TypeError, ValueError):
        return False


def audit(folder: Path, label: str, ui_before_utc: str, ui_after_utc: str,
          *, read_record=read_json) -> dict:
    """Return a bounded machine-validity verdict; never OCR/claim image semantics."""
    check(label in ALLOWED_LABELS, "label must be Full, Short or None")
    first = utc_time(ui_before_utc)
    last = utc_time(ui_after_utc)
    check(first < last and last - first <= timedelta(minutes=5),
          "UI bracket must be ordered and at most five minutes")

    inspection = read_record(folder / "native-inspection.json")
    snap = read_record(folder / "loaded-code-and-settings-root-v2.json")
    target = inspection["target"]
    identity = snap["identity"]
    check(snap.get("status") == "complete", "loaded-byte snapshot incomplete")
    check(same_identity(target, identity), "inspection/snapshot identities differ")
    check(str(identity["executableSha256"]).upper() == KNOWN_BUILD_SHA,
          "unqualified executable SHA-256")
    module_base = int(str(target["moduleBaseAddress"]), 0)
    check(module_base == identity["moduleBaseAddress"], "module base differs")
    snap_started = utc_time(snap["startedAtUtc"])
    snap_completed = utc_time(snap["completedAtUtc"])
    check(first <= snap_started <= snap_completed <= last,
          "loaded-byte snapshot outside UI bracket")
    source = snap["source"]
    check(source.get("requestSha256Verification") == "producer-declared",
          "snapshot request provenance unqualified")
    check_issued_request(folder, "loaded-code-and-settings-root-v2",
                         source.get("requestSha256"),
                         "native-memory-snapshot-request/1")
    reader_sha = str(source["implementation"]["bundleSha256"]).upper()
    check(len(reader_sha) == 64 and all(c in "0123456789ABCDEF" for c in reader_sha),
          "unqualified reader bundle SHA")
    inspection_impl = inspection.get("implementation")
    check(isinstance(inspection_impl, dict)
          and str(inspection_impl.get("bundleSha256", "")).upper() == reader_sha,
          "inspection reader bundle differs")

    chunks = snap["chunks"]
    check(len(chunks) == 4, "expected exactly four loaded-byte chunks")
    by_rva = {}
    for item in chunks:
        check(item.get("status") == "success", "loaded-byte chunk failed")
        address = int(str(item["address"]), 0)
        rva = address - module_base
        data = decode64(item["bytesBase64"], "loaded chunk")
        check(item["bytesRead"] == len(data) == item["requestedByteLength"],
              f"chunk {rva:x}: partial read")
        check(sha256(data) == str(item["bytesSha256"]).upper(),
              f"chunk {rva:x}: SHA mismatch")
        check(rva not in by_rva, f"chunk {rva:x}: duplicate address")
        by_rva[rva] = data
    check(set(by_rva) == set(CHUNKS) | {ROOT_RVA}, "loaded chunk RVAs changed")
    for rva, (count, digest) in CHUNKS.items():
        check(len(by_rva[rva]) == count and sha256(by_rva[rva]) == digest,
              f"exact-build code/literal mismatch at {rva:x}")
    check(bytes.fromhex("8999a4000000") in by_rva[0xBD2DA7],
          "settings +A4 writer not present")
    check(by_rva[0xBD7153] == bytes.fromhex("8b98a4000000"),
          "settings +A4 getter not present")
    check(by_rva[0x26ECC70] == b"ActionBars_AbilityQueue\x00",
          "Ability Queue setting key changed")
    pointer_bytes = by_rva[ROOT_RVA]
    check(len(pointer_bytes) == 8, "settings root pointer not eight bytes")
    pointer_value = int.from_bytes(pointer_bytes, "little")
    check(pointer_value != 0, "settings root pointer is null")

    samples = []
    for filename in ("queue-field-a-v2.json", "queue-field-b-v2.json"):
        report = read_record(folder / filename)
        check_issued_request(folder, filename.removesuffix(".json"),
                             report.get("requestSha256"),
                             "native-pointer-follow-request/1")
        check(str(report["implementation"]["bundleSha256"]).upper() == reader_sha,
              f"{filename}: reader bundle differs")
        chain, resolution = report["chain"], report["resolution"]
        check(resolution.get("status") == "complete", f"{filename}: chain incomplete")
        check(resolution.get("failedRead") is None
              and resolution.get("failedReadAddress") is None,
              f"{filename}: conflicting failure metadata")
        check(same_identity(identity, resolution["expectedIdentity"])
              and same_identity(identity, resolution["observedIdentity"]),
              f"{filename}: process identity mismatch")
        check(chain["rootRva"] == ROOT_RVA and chain["offsets"] == [FIELD_OFFSET],
              f"{filename}: unexpected pointer chain")
        hops = resolution["hops"]
        check(len(hops) == 1, f"{filename}: expected one pointer hop")
        hop = hops[0]
        hop_bytes = decode64(hop["pointerBytes"], f"{filename} pointer")
        check(len(hop_bytes) == 8 and hop_bytes == pointer_bytes,
              f"{filename}: pointer differs from snapshot")
        check(hop["pointerAddress"] == module_base + ROOT_RVA
              and hop["pointerValue"] == pointer_value
              and hop["offset"] == FIELD_OFFSET
              and hop["resolvedAddress"] == pointer_value + FIELD_OFFSET
              and resolution["terminalAddress"] == pointer_value + FIELD_OFFSET,
              f"{filename}: inconsistent address arithmetic")
        terminal = resolution["terminalRead"]
        check(terminal.get("status") == "success", f"{filename}: terminal read failed")
        check(terminal.get("win32ErrorCode") is None
              and terminal.get("reason") is None,
              f"{filename}: terminal read reports error")
        value_bytes = decode64(terminal["bytes"], f"{filename} value")
        check(len(value_bytes) == 4, f"{filename}: expected four terminal bytes")
        timestamp = utc_time(report["completedAtUtc"])
        check(snap_completed <= timestamp <= last,
              f"{filename}: outside UI bracket or preceding loaded-byte snapshot")
        samples.append((timestamp, int.from_bytes(value_bytes, "little")))

    check(samples[0][0] < samples[1][0], "native samples out of order")
    check(samples[0][1] == samples[1][1], "native queue values changed")
    value = samples[0][1]
    check(value in (0, 1, 2), "queue value outside expected research candidates")
    check((value == KNOWN_PAIR[0]) == (label == KNOWN_PAIR[1]),
          "conflicts with independently observed 1 ↔ Short")

    # Only 1 ↔ Short was independently observed on this exact build.
    # Do not promote a future 0/2 screenshot label to a proven enum mapping.
    label_mapping_qualified = (value, label) == KNOWN_PAIR

    captures = []
    for name in ("queue-ui-pre-read", "queue-ui-post-read"):
        ui_dir = folder / name
        manifest = read_record(ui_dir / "capture.json")
        result = read_record(ui_dir / "result.json")
        image_bytes = (ui_dir / "before.png").read_bytes()
        check(sha256(image_bytes) == str(manifest["imageSha256"]).upper(),
              f"{name}: original image SHA mismatch")
        check(result.get("status") == "completed-awaiting-visual-review"
              and result.get("connectionClosed") is True,
              f"{name}: capture not completed or connection still open")
        check(manifest.get("action") == "capture"
              and result.get("action") == "capture"
              and result.get("hostOnly") is True
              and result.get("inputMayHaveBeenSent") is False
              and result.get("consoleMutexReleased") is True,
              f"{name}: not an input-free completed capture")
        check(result["beforeIdentity"] == result["afterIdentity"],
              f"{name}: VM identity changed during capture")
        vm_identity = result["beforeIdentity"]
        check(isinstance(vm_identity, dict)
              and isinstance(vm_identity.get("vmx"), str)
              and vm_identity["vmx"].casefold() == EXPECTED_CAPTURE_VMX,
              f"{name}: capture VMX does not match qualified Lab-2")
        captures.append((manifest["imageSha256"], vm_identity))
    check(captures[0][1] == captures[1][1], "different VM console identities")

    # Bind each parsed native report to the original successful command receipt.
    # The receipt is self-reported provenance, not independent authentication.
    receipt = read_record(folder / "execution-receipts.json")
    required_steps = (
        ("native-inspection", "native-inspection.json", "inspect-native"),
        ("loaded-code-and-settings-root-v2",
         "loaded-code-and-settings-root-v2.json", "snapshot-native"),
        ("queue-field-a-v2", "queue-field-a-v2.json", "follow-pointer"),
        ("queue-field-b-v2", "queue-field-b-v2.json", "follow-pointer"),
    )
    steps = receipt.get("steps")
    check(isinstance(steps, list) and len(steps) == len(required_steps)
          and all(isinstance(step, dict) and isinstance(step.get("name"), str)
                  for step in steps)
          and {step["name"] for step in steps} == {row[0] for row in required_steps},
          "execution receipt steps incomplete or duplicated")
    step_by_name = {step["name"]: step for step in steps}
    for name, filename, command in required_steps:
        step = step_by_name[name]
        check(step.get("command") == command
              and type(step.get("exitCode")) is int and step["exitCode"] == 0
              and step.get("ownedRequestAndOutputCleaned") is True,
              f"{name}: execution receipt step incomplete")
        check(str(step.get("outputSha256", "")).upper()
              == sha256((folder / filename).read_bytes()),
              f"{name}: execution receipt SHA mismatch")

    return {
        "status": ("native_consistency_pass_visual_label_operator_supplied"
                   if label_mapping_qualified else "native_value_consistent_mapping_unverified"),
        "labelMappingQualified": label_mapping_qualified,
        "executableSha256": KNOWN_BUILD_SHA,
        "nativeValue": value,
        "operatorReviewedUiLabel": label,
        "sampleCount": len(samples),
        "stableSettingsRoot": True,
        "loadedCodeWindowsMatched": len(CHUNKS),
        "originalImagesHashMatched": len(captures),
        "nativeExecutionReceiptFilesMatched": len(required_steps),
        "nativeRequestHashesMatched": 3,
        "captureVmxVerified": EXPECTED_CAPTURE_VMX,
        "uiBracketUtc": [first.isoformat(), last.isoformat()],
        "limits": [
            "Cannot read or authenticate the text displayed inside screenshots",
            "UI bracket times and label are supplied by the human reviewer",
            "Values 0 and 2 have no source-qualified Full/None mapping",
            "Sequential reads and images are not one atomic acquisition",
            "Native execution receipt hashes check consistency, not independent authenticity",
            "VMX consistency alone does not independently bind guest process to screenshot",
            "Actual cast queue behavior, GCD and server timing remain untested",
        ],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("evidence_dir", type=Path)
    parser.add_argument("--label", required=True, choices=sorted(ALLOWED_LABELS))
    parser.add_argument("--ui-before-utc", required=True)
    parser.add_argument("--ui-after-utc", required=True)
    args = parser.parse_args(argv)
    try:
        verdict = audit(args.evidence_dir, args.label,
                        args.ui_before_utc, args.ui_after_utc)
    except (EvidenceError, KeyError, TypeError, OSError) as exc:
        print(json.dumps({"status": "rejected", "reason": str(exc)}))
        return 2
    print(json.dumps(verdict, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
