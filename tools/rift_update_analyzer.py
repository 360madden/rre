#!/usr/bin/env python3
"""Read-only, fail-closed RIFT PE update comparator. Python 3.9+, stdlib only."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import struct
import sys
from pathlib import Path

KNOWN_PREUPDATE_SHA256 = "1935a05c9db6d468e34e0055014a4a99c1b5afceb1695884e24600f5c20a4be8"
CHUNK_BYTES = 1024 * 1024
MAX_SECTION_COUNT = 96


class InspectionError(Exception):
    pass


class FailClosedParser(argparse.ArgumentParser):
    def error(self, message: str) -> None:
        print(json.dumps({"status": "ERROR", "nativeOffsetsQualified": False,
                          "message": message}, sort_keys=True), file=sys.stderr)
        self.exit(3)


def u16(data: bytes, offset: int) -> int:
    return struct.unpack_from("<H", data, offset)[0]


def u32(data: bytes, offset: int) -> int:
    return struct.unpack_from("<I", data, offset)[0]


def sha_range(path: Path, offset: int = 0, length: int | None = None) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        handle.seek(offset)
        remaining = length
        while remaining is None or remaining > 0:
            piece = handle.read(CHUNK_BYTES if remaining is None else min(CHUNK_BYTES, remaining))
            if not piece:
                if remaining is not None:
                    raise InspectionError("File truncated while hashing")
                break
            digest.update(piece)
            if remaining is not None:
                remaining -= len(piece)
    return digest.hexdigest()


def stamp(path: Path) -> tuple[int, int, int]:
    info = path.stat()
    if not path.is_file() or info.st_size == 0:
        raise InspectionError("Input is not a nonempty regular file: " + str(path))
    return info.st_size, info.st_mtime_ns, getattr(info, "st_ino", 0)


def inspect_pe(path: Path, size: int) -> dict:
    with path.open("rb") as handle:
        dos = handle.read(64)
        if len(dos) != 64 or dos[:2] != b"MZ":
            raise InspectionError("Not a DOS/PE executable: " + str(path))
        pe_offset = u32(dos, 0x3C)
        if not 64 <= pe_offset <= min(size - 24, 1024 * 1024):
            raise InspectionError("Invalid PE header offset")
        handle.seek(pe_offset)
        head = handle.read(24)
        if len(head) != 24 or head[:4] != b"PE\0\0":
            raise InspectionError("Invalid PE signature")
        machine = u16(head, 4)
        count = u16(head, 6)
        opt_size = u16(head, 20)
        if machine != 0x8664 or not 1 <= count <= MAX_SECTION_COUNT:
            raise InspectionError("Not a supported AMD64 PE or invalid section count")
        if not 0x70 <= opt_size <= 4096 or pe_offset + 24 + opt_size + count * 40 > size:
            raise InspectionError("Invalid optional header/section table bounds")
        optional = handle.read(opt_size)
        if u16(optional, 0) != 0x20B:
            raise InspectionError("Expected PE32+ optional header")
        image_size = u32(optional, 56)
        if image_size < 4096:
            raise InspectionError("Invalid PE image size")
        raw_sections = handle.read(count * 40)
        sections = []
        seen_names = {}
        raw_intervals = []
        virtual_intervals = []
        for index in range(count):
            s = raw_sections[index * 40:(index + 1) * 40]
            raw_name = s[:8].split(b"\x00", 1)[0]
            name = raw_name.decode("ascii", errors="backslashreplace")
            virtual_size, rva, raw_size, raw_offset = struct.unpack_from("<IIII", s, 8)
            characteristics = u32(s, 36)
            seen_names[name] = seen_names.get(name, 0) + 1
            key = name + "#" + str(seen_names[name])
            if rva == 0 or rva + max(virtual_size, raw_size) > image_size:
                raise InspectionError("Invalid virtual section range: " + key)
            if raw_size:
                if raw_offset < pe_offset + 24 + opt_size + count * 40 or raw_offset + raw_size > size:
                    raise InspectionError("Invalid file-backed section bounds: " + key)
                raw_intervals.append((raw_offset, raw_offset + raw_size, key))
            virtual_intervals.append((rva, rva + max(virtual_size, raw_size), key))
            sections.append({
                "id": key, "name": name, "index": index, "rva": rva,
                "virtualSize": virtual_size, "rawOffset": raw_offset, "rawSize": raw_size,
                "characteristics": characteristics, "executable": bool(characteristics & 0x20000000),
                "sha256": sha_range(path, raw_offset, raw_size),
            })
        for group, description in ((raw_intervals, "raw"), (virtual_intervals, "virtual")):
            group.sort()
            for left, right in zip(group, group[1:]):
                if left[1] > right[0]:
                    raise InspectionError("Overlapping " + description + " sections: " + left[2] + "/" + right[2])
        return {"architecture": "AMD64", "format": "PE32+", "sizeOfImage": image_size, "sections": sections}


def bytes_at_rva(path: Path, pe: dict, rva: int, size: int) -> bytes | None:
    for section in pe["sections"]:
        start = section["rva"]
        if start <= rva and rva + size <= start + section["rawSize"]:
            with path.open("rb") as handle:
                handle.seek(section["rawOffset"] + rva - start)
                found = handle.read(size)
                return found if len(found) == size else None
    return None


def compare_blocks(before: Path, after: Path, old: dict, new: dict, block_bytes: int, max_blocks: int) -> dict:
    common = min(old["rawSize"], new["rawSize"])
    changed = 0
    samples = []
    with before.open("rb") as source, after.open("rb") as target:
        source.seek(old["rawOffset"])
        target.seek(new["rawOffset"])
        for relative in range(0, common, block_bytes):
            span = min(block_bytes, common - relative)
            lhs = source.read(span)
            rhs = target.read(span)
            if len(lhs) != span or len(rhs) != span:
                raise InspectionError("File truncated while comparing section")
            if lhs != rhs:
                changed += 1
                if len(samples) < max_blocks:
                    samples.append({
                        "relativeOffset": relative,
                        "length": span,
                        "oldRva": old["rva"] + relative,
                        "newRva": new["rva"] + relative,
                    })
    if old["rawSize"] != new["rawSize"]:
        changed += 1
        if len(samples) < max_blocks:
            samples.append({
                "relativeOffset": common,
                "length": abs(old["rawSize"] - new["rawSize"]),
                "oldRva": old["rva"] + common,
                "newRva": new["rva"] + common,
                "sizeDifference": True,
            })
    return {"changedBlocks": changed, "blocks": samples, "blocksTruncated": changed > len(samples)}


def compare_sections(before: Path, after: Path, old_pe: dict, new_pe: dict, block_bytes: int, max_blocks: int) -> list[dict]:
    older = {s["id"]: s for s in old_pe["sections"]}
    newer = {s["id"]: s for s in new_pe["sections"]}
    results = []
    for key in list(older) + [key for key in newer if key not in older]:
        old, new = older.get(key), newer.get(key)
        if old is None or new is None:
            results.append({"id": key, "status": "added" if old is None else "removed",
                            "before": old, "after": new})
            continue
        same_bytes = old["sha256"] == new["sha256"] and old["rawSize"] == new["rawSize"]
        same_layout = (old["rva"], old["rawOffset"], old["virtualSize"], old["characteristics"]) == (
            new["rva"], new["rawOffset"], new["virtualSize"], new["characteristics"])
        verdict = "identical" if same_bytes and same_layout else (
            "bytes_same_layout_changed" if same_bytes else "bytes_changed")
        record = {"id": key, "status": verdict, "before": old, "after": new}
        if not same_bytes:
            record["difference"] = compare_blocks(before, after, old, new, block_bytes, max_blocks)
        results.append(record)
    return results


def check_anchors(path: Path | None, before: Path, after: Path, old_sha: str, old_pe: dict, new_pe: dict) -> list[dict]:
    if path is None:
        return []
    payload = json.loads(path.read_text(encoding="utf-8"))
    if payload.get("schemaVersion") != 1 or payload.get("sourceSha256", "").lower() != old_sha:
        raise InspectionError("Anchor manifest does not pin the exact baseline build")
    entries = payload.get("anchors")
    if not isinstance(entries, list) or not 1 <= len(entries) <= 1000:
        raise InspectionError("Invalid anchor count")
    results = []
    seen = set()
    for entry in entries:
        name = entry.get("id")
        if not isinstance(name, str) or not name or name in seen:
            raise InspectionError("Invalid or duplicated anchor identifier")
        seen.add(name)
        rva = int(entry["rva"], 0) if isinstance(entry["rva"], str) else entry["rva"]
        hex_text = entry["hex"]
        if not isinstance(rva, int) or rva < 0 or not isinstance(hex_text, str):
            raise InspectionError("Invalid anchor RVA or bytes")
        try:
            expected = bytes.fromhex(hex_text)
        except ValueError as ex:
            raise InspectionError("Invalid anchor hex for " + name) from ex
        if not 1 <= len(expected) <= 64:
            raise InspectionError("Invalid anchor byte length")
        original = bytes_at_rva(before, old_pe, rva, len(expected))
        if original != expected:
            raise InspectionError("Anchor baseline mismatch at " + name)
        current = bytes_at_rva(after, new_pe, rva, len(expected))
        results.append({
            "id": name, "rva": rva, "baselineHex": expected.hex(),
            "currentHex": current.hex() if current is not None else None,
            "status": "same_bytes_at_same_rva" if current == expected else (
                "unmapped" if current is None else "bytes_different_at_same_rva"),
            "runtimeQualified": False,
        })
    return results


def render_markdown(result: dict) -> str:
    lines = [
        "# RIFT executable update comparison",
        "",
        "**Verdict:** " + result["status"],
        "**Native offsets qualified for new build:** NO" if result["status"] == "CHANGED" else
        "**Native offsets qualified for live session:** NO (runtime identity requires separate proof)",
        "",
        "- Old SHA-256: " + result["before"]["sha256"],
        "- New SHA-256: " + result["after"]["sha256"],
        "- Old bytes: " + str(result["before"]["sizeBytes"]),
        "- New bytes: " + str(result["after"]["sizeBytes"]),
        "- PE section comparison is byte-level evidence only; it cannot resolve moved functions or prove runtime identity.",
        "",
        "| Section | Verdict | Old RVA | New RVA | Old bytes | New bytes | Changed blocks |",
        "| --- | --- | --- | --- | ---: | ---: | ---: |",
    ]
    for section in result["sections"]:
        old, new = section.get("before"), section.get("after")
        fmt = lambda value: "—" if value is None else "0x" + format(value, "X")
        lines.append("| " + section["id"] + " | " + section["status"] + " | " +
                     fmt(old["rva"] if old else None) + " | " + fmt(new["rva"] if new else None) +
                     " | " + str(old["rawSize"] if old else "—") + " | " +
                     str(new["rawSize"] if new else "—") + " | " +
                     str(section.get("difference", {}).get("changedBlocks", 0)) + " |")
    if result["anchors"]:
        lines += ["", "## SHA-bound RRE byte anchors", "", "| Anchor | RVA | Status |", "| --- | --- | --- |"]
        for anchor in result["anchors"]:
            lines.append("| " + anchor["id"] + " | 0x" + format(anchor["rva"], "X") +
                         " | " + anchor["status"] + " |")
    lines += ["", "## Safe next step", ""]
    if result["status"] == "MATCH":
        lines.append("The executable bytes match. Reconfirm the *current* physical process, loaded addon, scene and session before using any game-facing reader.")
    else:
        lines.append("STOP: old-build native RVAs, pointer chains, signature offsets and receiver assumptions are not qualified for this new executable. Preserve the original, rederive affected functions offline, and require fresh live evidence.")
    return "\n".join(lines) + "\n"


def execute(args: argparse.Namespace) -> int:
    before = args.before.resolve(strict=True)
    after = args.after.resolve(strict=True)
    out = args.output_dir.resolve(strict=False)
    if before == after or before.samefile(after):
        raise InspectionError("Before and after must be different immutable/file paths")
    if out.exists():
        raise InspectionError("Report destination already exists; refusing to overwrite: " + str(out))
    if out.is_relative_to(before.parent) or out.is_relative_to(after.parent):
        raise InspectionError("Report destination must be outside both executable directories")
    if not re.fullmatch(r"[a-fA-F0-9]{64}", args.expected_before_sha):
        raise InspectionError("Expected baseline SHA-256 must be 64 hex characters")
    initial_old, initial_new = stamp(before), stamp(after)
    before_sha, after_sha = sha_range(before), sha_range(after)
    if before_sha != args.expected_before_sha.lower():
        raise InspectionError("Baseline hash mismatch; refusing comparison against unexpected original")
    old_pe = inspect_pe(before, initial_old[0])
    new_pe = inspect_pe(after, initial_new[0])
    sections = compare_sections(before, after, old_pe, new_pe, args.block_bytes, args.max_blocks)
    anchors = check_anchors(args.anchors, before, after, before_sha, old_pe, new_pe)
    if (stamp(before), stamp(after)) != (initial_old, initial_new):
        raise InspectionError("An executable changed while being inspected (possible updater race)")
    if sha_range(before) != before_sha or sha_range(after) != after_sha:
        raise InspectionError("Executable bytes changed during inspection")
    result = {
        "schemaVersion": 1,
        "status": "MATCH" if before_sha == after_sha else "CHANGED",
        "nativeOffsetsQualified": False,
        "staticRvasByteCompatible": before_sha == after_sha,
        "requiresRuntimeRequalification": True,
        "before": {"path": str(before), "sha256": before_sha, "sizeBytes": initial_old[0], "pe": old_pe},
        "after": {"path": str(after), "sha256": after_sha, "sizeBytes": initial_new[0], "pe": new_pe},
        "sections": sections,
        "anchors": anchors,
        "blockBytes": args.block_bytes,
        "maxRecordedBlocksPerSection": args.max_blocks,
        "rawSectionsUnchangedButFileChanged": before_sha != after_sha and all(
            s["before"] is not None and s["after"] is not None and
            s["before"]["rawSize"] == s["after"]["rawSize"] and
            s["before"]["sha256"] == s["after"]["sha256"] for s in sections),
        "readOnlyInputs": True,
    }
    out.mkdir(parents=True, exist_ok=False)
    (out / "report.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (out / "report.md").write_text(render_markdown(result), encoding="utf-8")
    print(json.dumps({"status": result["status"], "oldSha256": before_sha,
                      "newSha256": after_sha, "reportDir": str(out),
                      "changedSections": sum(s["status"] != "identical" for s in sections),
                      "anchorsChecked": len(anchors)}, sort_keys=True))
    return 0 if result["status"] == "MATCH" else 2


def main() -> int:
    parser = FailClosedParser(description=__doc__)
    parser.add_argument("--before", type=Path, required=True, help="SHA-pinned preserved original rift_x64.exe")
    parser.add_argument("--after", type=Path, required=True, help="Actual physical installed rift_x64.exe")
    parser.add_argument("--output-dir", type=Path, required=True, help="NEW report directory; never overwrites")
    parser.add_argument("--expected-before-sha", default=KNOWN_PREUPDATE_SHA256)
    parser.add_argument("--anchors", type=Path, help="Optional SHA-pinned RRE original-byte anchor manifest")
    parser.add_argument("--block-bytes", type=int, default=65536)
    parser.add_argument("--max-blocks", type=int, default=128)
    args = parser.parse_args()
    if not 64 <= args.block_bytes <= CHUNK_BYTES or not 1 <= args.max_blocks <= 256:
        parser.error("block-bytes must be 64..1048576 and max-blocks must be 1..256")
    try:
        return execute(args)
    except (InspectionError, OSError, ValueError, KeyError, IndexError, struct.error, TypeError, AttributeError, UnicodeError) as ex:
        print(json.dumps({"status": "ERROR", "nativeOffsetsQualified": False,
                          "message": str(ex)}, sort_keys=True), file=sys.stderr)
        return 3


if __name__ == "__main__":
    sys.exit(main())
