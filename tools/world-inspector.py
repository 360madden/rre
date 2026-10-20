#!/usr/bin/env python3
"""File-only RIFT world inspector. No game, process, input, Lua or network access.

Read docs/world-awareness-contract.md. Saved data never becomes current live truth.
Python standard library only; outputs are created in a new directory, never replaced.
"""
from __future__ import annotations

import argparse
import hashlib
import html
import json
import math
from pathlib import Path
import re
import sys
from typing import Any

VERSION = "1.0.0"
MAX_BYTES = 8 * 1024 * 1024
MAX_UNITS = 512
NUMBER_LIMIT = 1e12
CONVENTION = "row-major-column-vector-zero-to-one"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def integer(value: Any, label: str, minimum: int = 0, maximum: int = 2**63 - 1) -> int:
    require(type(value) is int and minimum <= value <= maximum, f"{label}: invalid integer")
    return value


def finite(value: Any, label: str) -> float:
    require(type(value) in (int, float), f"{label}: expected a number, not a boolean")
    try:
        number = float(value)
    except (ValueError, OverflowError) as exc:
        raise ValueError(f"{label}: invalid numeric range") from exc
    require(math.isfinite(number) and abs(number) <= NUMBER_LIMIT,
            f"{label}: nonfinite or outside supported numeric range")
    return number


def text(value: Any, label: str, *, nullable: bool = True) -> str | None:
    if value is None and nullable:
        return None
    require(isinstance(value, str) and 0 < len(value) <= 512,
            f"{label}: expected a nonempty bounded string")
    require(not any(ord(c) < 32 or 0xD800 <= ord(c) <= 0xDFFF for c in value),
            f"{label}: control characters or invalid Unicode scalar forbidden")
    return value


def entity_id(value: Any, label: str) -> str:
    result = text(value, label, nullable=False)
    assert result is not None
    require(result.strip() == result and len(result) <= 160, f"{label}: invalid ID")
    require(not re.fullmatch(r"(?:player|target|focus|mouseover)(?:\..*)?|(?:group|raid)\d+|0x[0-9a-f]+",
                             result, re.IGNORECASE), f"{label}: unit specifier/address is not an entity ID")
    return result


def object_value(value: Any, label: str) -> dict:
    require(isinstance(value, dict), f"{label}: expected object")
    return value


def schema_one(value: dict, label: str) -> None:
    object_value(value, label)
    require(type(value.get("schemaVersion")) is int and value["schemaVersion"] == 1,
            f"{label}: unsupported schemaVersion")


def strict_load(path: Path) -> tuple[dict, bytes]:
    def pairs(items: list[tuple[str, Any]]) -> dict:
        result = {}
        for key, value in items:
            require(key not in result, f"Duplicate JSON key: {key}")
            result[key] = value
        return result

    def reject_constant(value: str) -> None:
        raise ValueError(f"Nonfinite JSON constant: {value}")

    def parse_float(value: str) -> float:
        result = float(value)
        require(math.isfinite(result), "Nonfinite JSON exponent")
        return result

    with path.open("rb") as stream:
        raw = stream.read(MAX_BYTES + 1)
    require(0 < len(raw) <= MAX_BYTES, "Input is empty or exceeds 8 MiB")
    try:
        data = json.loads(raw.decode("utf-8"), object_pairs_hook=pairs,
                          parse_constant=reject_constant, parse_float=parse_float)
    except (UnicodeDecodeError, json.JSONDecodeError, RecursionError) as exc:
        raise ValueError(f"Invalid UTF-8 JSON: {exc}") from exc
    return object_value(data, "input"), raw


def position(value: Any, label: str) -> list[float] | None:
    if value is None:
        return None
    obj = object_value(value, label)
    if all(obj.get(axis) is None for axis in "xyz"):
        return None
    require(all(obj.get(axis) is not None for axis in "xyz"), f"{label}: partial coordinate")
    return [finite(obj[axis], f"{label}.{axis}") for axis in "xyz"]


def unit(value: Any, role: str, path: str, expected_id: Any = None) -> dict:
    obj = object_value(value, path)
    key = entity_id(obj.get("id"), path + ".id")
    if expected_id is not None:
        require(key == entity_id(expected_id, path + " root ID"), path + ": root/record ID mismatch")
    is_player = obj.get("player")
    require(is_player is None or type(is_player) is bool, path + ".player: expected nullable bool")
    return {"id": key, "role": role, "sourcePath": path,
            "name": text(obj.get("name"), path + ".name"),
            "zone": text(obj.get("zone"), path + ".zone"),
            "kind": "player-character" if is_player is True else
                    "non-player-unit" if is_player is False else None,
            "position": position(obj.get("coord"), path + ".coord")}


def read_readerbridge(data: dict) -> tuple[list[dict], dict, dict, str]:
    schema_one(data, "ReaderBridge")
    mode = text(data.get("sourceMode"), "sourceMode", nullable=False)
    require(mode in ("DirectAPI", "ReaderBridge", "SyntheticFixture"), "Unsupported ReaderBridge sourceMode")
    for name in ("playerId", "targetId"):
        if data.get(name) is not None:
            entity_id(data[name], name)
    records = []
    for key, role in (("player", "local-player"), ("target", "selected-target")):
        if data.get(key) is not None:
            records.append(unit(data[key], role, key, data.get(key + "Id")))
    coverage = {"worldScenery": "unknown", "allEntities": "not-established"}
    for name, role in (("nearbyUnits", "nearby"), ("partyUnits", "party")):
        rows = data.get(name)
        require(rows is None or isinstance(rows, list), name + ": expected nullable array")
        coverage[name] = "unavailable-or-empty" if rows is None else (
            "reported-empty-scope-unverified" if not rows else "partial-reported")
        if rows is not None:
            require(len(records) + len(rows) <= MAX_UNITS, "More than 512 unit records")
            records.extend(unit(row, role, f"{name}[{i}]") for i, row in enumerate(rows))
    if mode == "ReaderBridge" and data.get("nearbyUnits") is None:
        coverage["nearbyUnits"] = "not-exported-by-bridge-mode"
    stamp = data.get("generatedAtRealtime")
    if stamp is not None:
        finite(stamp, "generatedAtRealtime")
    metadata = {"sourceMode": mode, "recordedRealtime": stamp,
                "clockMeaning": "source-relative; not converted to UTC",
                "recordedSession": None, "recordedScene": None,
                "snapshotCoherence": "not-established"}
    return records, coverage, metadata, "synthetic" if mode == "SyntheticFixture" else "recorded"


def read_rr2_receipt(data: dict) -> tuple[list[dict], dict, dict, str]:
    """Read only the inspected delivery-receipt shape, not arbitrary RR2 JSON."""
    schema_one(data, "receipt")
    outer = object_value(data.get("observation"), "receipt.observation")
    schema_one(outer, "outer observation")
    rr2 = object_value(outer.get("riftReader2"), "riftReader2")
    schema_one(rr2, "riftReader2")
    obs = object_value(rr2.get("observation"), "addon observation")
    schema_one(obs, "addon observation")
    require(obs.get("addonVersion") == "0.1.0", "Unsupported saved addon version")
    fields = object_value(obs.get("fields"), "fields")

    def typed(value: Any, label: str) -> tuple[str, Any]:
        row = object_value(value, label)
        state = row.get("status")
        require(state in ("ok", "unavailable", "invalid"), label + ": invalid typed status")
        if state == "ok":
            require(row.get("value") is not None, label + ": ok without value")
            return state, row["value"]
        require("value" not in row or row["value"] is None, label + ": failed status carries value")
        return state, None

    state, player_id = typed(obs.get("player"), "player")
    coords = [typed(fields.get("coord" + axis), "coord" + axis) for axis in "XYZ"]
    for i, (status, value) in enumerate(coords):
        if status == "ok":
            finite(value, "coord" + "XYZ"[i])
    records = []
    if state == "ok":
        obj = {"id": entity_id(player_id, "typed player ID"), "player": True,
               "coord": dict(zip("xyz", [value for _, value in coords]))
               if all(status == "ok" for status, _ in coords) else None}
        records.append(unit(obj, "local-player", "observation.riftReader2.observation.player"))
    target = object_value(outer.get("target"), "process target (not selected game entity)")
    digest = target.get("executableSha256")
    require(isinstance(digest, str) and re.fullmatch(r"[0-9a-fA-F]{64}", digest) is not None,
            "Invalid historical executable SHA256")
    pid = integer(target.get("processId"), "recorded processId", 1)
    ticks = integer(target.get("processStartUtcTicks"), "recorded processStartUtcTicks", 1)
    metadata = {"capturedAtUtc": text(outer.get("capturedAtUtc"), "capturedAtUtc", nullable=False),
                "receivedAtUtc": text(data.get("receivedAtUtc"), "receivedAtUtc", nullable=False),
                "recordedProcessId": pid, "recordedProcessStartTicks": str(ticks),
                "recordedExecutableSha256": digest.lower(),
                "recordedAddonEpoch": integer(obs.get("epoch"), "epoch"),
                "recordedAddonSequence": integer(obs.get("sequence"), "sequence"),
                "recordedBindingClaim": rr2.get("bindingStatus"),
                "recordedFreshnessClaim": rr2.get("freshnessStatus"),
                "coordinateFieldStatuses": [status for status, _ in coords],
                "currentValidity": "not-revalidated", "snapshotCoherence": "not-established"}
    return records, {"allEntities": "player-only", "nearbyUnits": "not-exported",
                     "partyUnits": "not-exported", "worldScenery": "unknown"}, metadata, "recorded"


def merge_records(records: list[dict]) -> list[dict]:
    require(len(records) <= MAX_UNITS, "More than 512 unit records")
    grouped: dict[str, list[dict]] = {}
    for record in records:
        grouped.setdefault(record["id"], []).append(record)
    result = []
    for key in sorted(grouped):
        observations = grouped[key]
        out = {"id": key, "roles": sorted({r["role"] for r in observations}),
               "sourcePaths": [r["sourcePath"] for r in observations],
               "observationCount": len(observations), "conflicts": []}
        for field in ("name", "zone", "kind", "position"):
            values = []
            for r in observations:
                value = r[field]
                if value is not None and value not in values:
                    values.append(value)
            if len(values) > 1:
                out["conflicts"].append(field)
            out[field] = values[0] if len(values) == 1 else None
        out["status"] = "conflict" if out["conflicts"] else "recorded"
        if out["conflicts"]:
            out["position"] = None
        out["observations"] = observations  # No conflicting source value is discarded.
        out.update({name: "unknown" for name in ("visibility", "collision", "support", "reachability")})
        result.append(out)
    return result


def nonsingular(matrix: list[float]) -> bool:
    # Row normalization makes this check independent of a uniform projection scale.
    rows = [matrix[i:i + 4] for i in range(0, 16, 4)]
    for row in rows:
        scale = max(abs(v) for v in row)
        if scale == 0:
            return False
        for j in range(4):
            row[j] /= scale
    for column in range(4):
        pivot = max(range(column, 4), key=lambda i: abs(rows[i][column]))
        if abs(rows[pivot][column]) <= 1e-12:
            return False
        rows[column], rows[pivot] = rows[pivot], rows[column]
        for i in range(column + 1, 4):
            multiplier = rows[i][column] / rows[column][column]
            for j in range(column, 4):
                rows[i][j] -= multiplier * rows[column][j]
    return True


def validate_camera(camera: dict, input_sha: str, source_kind: str) -> dict:
    schema_one(camera, "camera")
    require(camera.get("sourceSha256") == input_sha, "Camera/input SHA256 mismatch")
    require(camera.get("convention") == CONVENTION, "Unsupported camera convention")
    kind = camera.get("evidenceKind")
    require(kind in ("synthetic", "candidate"), "Camera must be synthetic or candidate, not verified")
    require(not (kind == "synthetic" and source_kind != "synthetic"),
            "Synthetic camera cannot project recorded game evidence")
    values = camera.get("viewProjection")
    require(isinstance(values, list) and len(values) == 16, "Camera requires 16 matrix entries")
    matrix = [finite(value, "matrix entry") for value in values]
    require(nonsingular(matrix), "Singular or numerically unsupported camera matrix")
    viewport = object_value(camera.get("viewport"), "viewport")
    view = {"x": finite(viewport.get("x"), "viewport x"),
            "y": finite(viewport.get("y"), "viewport y"),
            "width": integer(viewport.get("width"), "viewport width", 1, 16384),
            "height": integer(viewport.get("height"), "viewport height", 1, 16384)}
    return {"matrix": matrix, "viewport": view, "evidenceKind": kind,
            "convention": CONVENTION, "calibration": "not-validated-against-game"}


def project(point: list[float], camera: dict) -> dict:
    require(len(point) == 3, "Projection needs XYZ")
    vec = [finite(value, "projection coordinate") for value in point] + [1.0]
    matrix = camera["matrix"]
    clip = [math.fsum(matrix[4 * i + j] * vec[j] for j in range(4)) for i in range(4)]
    require(all(math.isfinite(value) for value in clip), "Projection overflow")
    x, y, z, w = clip
    if w <= 0 or not (-w <= x <= w and -w <= y <= w and 0 <= z <= w):
        return {"status": "not-in-frustum", "visibility": "unknown", "screen": None}
    view = camera["viewport"]
    screen = [view["x"] + (x / w + 1) * view["width"] / 2,
              view["y"] + (1 - y / w) * view["height"] / 2]
    require(all(math.isfinite(value) for value in screen), "Viewport overflow")
    return {"status": "candidate-in-frustum", "visibility": "unknown", "screen": screen}


def inspect_data(data: dict, input_format: str, input_sha: str, camera_data: dict | None = None) -> dict:
    readers = {"readerbridge": read_readerbridge, "rr2-receipt": read_rr2_receipt}
    require(input_format in readers, "Unsupported input format")
    require(re.fullmatch(r"[0-9a-f]{64}", input_sha) is not None, "Invalid source SHA256")
    records, coverage, metadata, kind = readers[input_format](data)
    entities = merge_records(records)
    camera = validate_camera(camera_data, input_sha, kind) if camera_data is not None else None
    for row in entities:
        row["projection"] = project(row["position"], camera) if camera and row["position"] is not None else {
            "status": "unavailable", "visibility": "unknown", "screen": None}
    return {"schemaVersion": 1, "inspectorVersion": VERSION, "inputFormat": input_format,
            "sourceSha256": input_sha, "sourceKind": kind,
            "live": False, "currentBinding": "unverified", "freshness": "unverified-saved-data",
            "identityScope": "this input hash only; no cross-capture tracking",
            "coordinateFrame": "source XYZ; orientation/units/common scene not qualified",
            "coverage": coverage, "historicalMetadata": metadata,
            "camera": camera, "entities": entities,
            "counts": {"inputRecords": len(records), "distinctIds": len(entities),
                       "withPosition": sum(r["position"] is not None for r in entities),
                       "conflictingIds": sum(bool(r["conflicts"]) for r in entities)},
            "capabilities": {"gameObjectEnumerationProven": False, "collisionOwnerProven": False,
                             "cameraCalibrated": False, "nativeNavigationProven": False},
            "limitations": ["A saved receipt's old bound/fresh flags do not establish current validity.",
                            "Exact IDs are grouped only within one input; collection may not be atomic.",
                            "Source unit labels are not independently verified object classifications.",
                            "No terrain, scenery bounds, collision hits or routes are generated.",
                            "Raw X/Z plotting is not a ground map; separate Y and zone must be retained.",
                            "Frustum projection is not occlusion, clearance, support or reachability."]}


def render_html(report: dict) -> str:
    esc = lambda value: html.escape(str(value), quote=True)
    parts = ["<!doctype html><html lang='en'><meta charset='utf-8'>",
             "<meta name='viewport' content='width=device-width,initial-scale=1'>",
             "<meta http-equiv='Content-Security-Policy' content=\"default-src 'none'; style-src 'unsafe-inline'\">",
             "<title>RRE local world inspector</title><style>",
             "body{font:16px system-ui;margin:32px auto;max-width:1180px;padding:0 20px;color:#203047;background:#f6f8fa}",
             "h1,h2{color:#14273b}section{background:white;padding:22px;margin:20px 0;border:1px solid #d4dce5;border-radius:8px}",
             ".notice{background:#fff4d6;padding:16px;border-left:5px solid #a96800}table{border-collapse:collapse;width:100%;font-size:14px}",
             "td,th{padding:10px;border-bottom:1px solid #d4dce5;text-align:left;vertical-align:top}code{overflow-wrap:anywhere}",
             "svg{width:100%;max-height:480px;background:#f1f5f8}circle{fill:#235789}text{font:12px system-ui}small{color:#516478}</style>",
             "<h1>RRE local world inspector</h1>",
             f"<p class='notice'><strong>{esc(report['sourceKind'].upper())} / FILE-ONLY</strong> — not a live world map. "
             "Collision, visibility, support and reachability remain unknown.</p>",
             f"<p>Source SHA-256: <code>{esc(report['sourceSha256'])}</code><br>Format: {esc(report['inputFormat'])}; "
             f"distinct IDs: {report['counts']['distinctIds']}; conflicts: {report['counts']['conflictingIds']}.</p>",
             "<section><h2>Observed entity records</h2><table><thead><tr><th>ID / source roles</th><th>Name / kind</th>",
             "<th>XYZ / zone</th><th>Evidence status</th></tr></thead><tbody>"]
    for row in report["entities"]:
        coords = "unknown" if row["position"] is None else ", ".join(f"{v:.6g}" for v in row["position"])
        parts.append(f"<tr><td><code>{esc(row['id'])}</code><br>{esc(', '.join(row['roles']))}</td>"
                     f"<td>{esc(row['name'] or 'unknown')}<br><small>{esc(row['kind'] or 'unknown')}</small></td>"
                     f"<td>{esc(coords)}<br>{esc(row['zone'] or 'zone unknown')}</td>"
                     f"<td>{esc(row['status'])}<br>{esc(', '.join(row['conflicts']))}<br>"
                     f"<small>{esc('; '.join(row['sourcePaths']))}</small></td></tr>")
    parts.append("</tbody></table></section>")
    zones = sorted({r["zone"] or "unknown" for r in report["entities"] if r["position"] is not None})
    for zone in zones:
        rows = [r for r in report["entities"] if r["position"] is not None and (r["zone"] or "unknown") == zone]
        xs = [r["position"][0] for r in rows]; zs = [r["position"][2] for r in rows]
        x0, x1, z0, z1 = min(xs), max(xs), min(zs), max(zs)
        span = max(x1 - x0, z1 - z0, 1.0)
        parts.append(f"<section><h2>Raw X/Z diagnostic — {esc(zone)}</h2><p>Source units and ground orientation unqualified. "
                     "Dots are coordinate markers, not collision bounds. Heights remain separate.</p><svg viewBox='0 0 800 460' role='img' aria-label='Raw coordinate markers'>")
        for index, row in enumerate(rows):
            x, y, z = row["position"]
            sx = 400 + 360 * (x - (x0 + x1) / 2) / span
            sy = 230 - 360 * (z - (z0 + z1) / 2) / span
            label = f"{row['id']} | Y={y:.6g}"
            parts.append(f"<circle cx='{sx:.3f}' cy='{sy:.3f}' r='5'><title>{esc(label)}</title></circle>"
                         f"<text x='{sx + 8:.3f}' y='{sy - 8 - index % 3 * 14:.3f}'>{esc(label)}</text>")
        parts.append("</svg></section>")
    if report["camera"] is not None:
        view = report["camera"]["viewport"]
        parts.append("<section><h2>Candidate camera projection</h2><p>No screenshot calibration or occlusion check. "
                     "Only the explicit sidecar matrix is used.</p>"
                     f"<svg viewBox='{view['x']} {view['y']} {view['width']} {view['height']}' role='img' aria-label='Candidate projection'>")
        for row in report["entities"]:
            screen = row["projection"]["screen"]
            if screen is not None:
                parts.append(f"<circle cx='{screen[0]}' cy='{screen[1]}' r='5'/><text x='{screen[0] + 8}' y='{screen[1]}'>{esc(row['id'])}</text>")
        parts.append("</svg></section>")
    parts.append("<section><h2>Coverage and limitations</h2><pre>" + esc(json.dumps(report["coverage"], indent=2)) + "</pre><ul>")
    parts.extend("<li>" + esc(item) + "</li>" for item in report["limitations"])
    parts.append("</ul></section></html>\n")
    return "".join(parts)


def inspect_file(input_path: Path, input_format: str, output_directory: Path,
                 camera_path: Path | None = None) -> dict:
    data, raw = strict_load(input_path)
    camera, camera_raw = strict_load(camera_path) if camera_path is not None else (None, None)
    report = inspect_data(data, input_format, hashlib.sha256(raw).hexdigest(), camera)
    report["inputByteCount"] = len(raw)
    report["inspectorSourceSha256"] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    report["cameraSourceSha256"] = hashlib.sha256(camera_raw).hexdigest() if camera_raw else None
    json_text = json.dumps(report, indent=2, sort_keys=True, ensure_ascii=True, allow_nan=False) + "\n"
    html_text = render_html(report)
    # Atomic directory creation rejects existing outputs. Parents are not created implicitly.
    output_directory.mkdir(parents=False, exist_ok=False)
    with (output_directory / "report.json").open("x", encoding="utf-8", newline="\n") as stream:
        stream.write(json_text)
    with (output_directory / "report.html").open("x", encoding="utf-8", newline="\n") as stream:
        stream.write(html_text)
    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--input-format", choices=("readerbridge", "rr2-receipt"), required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--camera", type=Path)
    args = parser.parse_args(argv)
    try:
        report = inspect_file(args.input, args.input_format, args.output_dir, args.camera)
        print(json.dumps({"status": "completed", "sourceKind": report["sourceKind"],
                          "live": False, "counts": report["counts"],
                          "html": str(args.output_dir / "report.html"),
                          "json": str(args.output_dir / "report.json")}, sort_keys=True))
        return 0
    except (OSError, ValueError, TypeError, OverflowError, RecursionError) as exc:
        print(json.dumps({"status": "failed", "error": str(exc), "live": False}), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
