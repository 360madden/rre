"""Find one SHA-derived content-ID prefix in RIFT TWAD metadata only.

Reads only the 20-byte TWAD headers and bounded 44-byte entry tables of
explicitly selected assets.NNN / assets64.NNN files. Never reads payload bytes,
extracts, decompresses, modifies the game, or writes files.
"""
import argparse
import hashlib
import json
import re
import socket
import struct
from pathlib import Path

HEADER = struct.Struct("<4sIIII")
ENTRY = struct.Struct("<8sIIIHH20s")
SEGMENT = re.compile(r"assets(?:64)?\.[0-9]{3}", re.IGNORECASE)
MAX_SEGMENTS = 256
MAX_RECORDS = 4096
MAX_TABLE_BYTES = 262144


def content_id(value: str) -> bytes:
    if len(value) != 16 or any(c not in "0123456789abcdefABCDEF" for c in value):
        raise ValueError("Content ID prefix must be exactly 16 hexadecimal digits")
    return bytes.fromhex(value)


def scan_segment(path: Path, target: bytes) -> tuple[int, list[dict]]:
    size = path.stat().st_size
    with path.open("rb") as stream:
        head = stream.read(HEADER.size)
        if len(head) != HEADER.size:
            raise ValueError(f"{path.name}: truncated TWAD header")
        magic, version, table_offset, count, _first_linked = HEADER.unpack(head)
        table_size = count * ENTRY.size
        if (magic != b"TWAD" or version != 1 or table_offset < HEADER.size
                or count > MAX_RECORDS or table_size > MAX_TABLE_BYTES
                or table_offset + table_size > size):
            raise ValueError(f"{path.name}: unadmitted TWAD metadata layout")
        stream.seek(table_offset)
        table = stream.read(table_size)
        if len(table) != table_size:
            raise ValueError(f"{path.name}: truncated TWAD entry table")

    matches = []
    for index in range(count):
        row = table[index * ENTRY.size:(index + 1) * ENTRY.size]
        if row[:8] != target:
            continue
        asset_id, offset, stored_size, _unknown, _next_index, compression, sha = ENTRY.unpack(row)
        if offset < table_offset + table_size or stored_size > size - offset:
            raise ValueError(f"{path.name}: target entry payload metadata outside archive")
        matches.append({
            "segment": path.name,
            "segmentSize": size,
            "entryIndex": index,
            "contentIdPrefix": asset_id.hex(),
            "inspectedHeaderAndTableSha256": hashlib.sha256(head + table).hexdigest(),
            "recordedEntrySha1": sha.hex(),
            "payloadOffset": offset,
            "storedSize": stored_size,
            "compressionFlag": compression,
        })
    return count, matches


def inspect(folder: Path, target: bytes, expected_host: str | None = None) -> dict:
    host = socket.gethostname()
    if expected_host and host.upper() != expected_host.upper():
        raise ValueError("Host does not match --expected-host")
    if not folder.is_dir():
        raise ValueError("Assets directory does not exist")
    segments = sorted(
        (p for p in folder.iterdir() if not p.is_symlink() and p.is_file()
         and SEGMENT.fullmatch(p.name)), key=lambda p: p.name.lower()
    )
    if not segments or len(segments) > MAX_SEGMENTS:
        raise ValueError("No matching TWAD segments or segment count exceeds safety cap")
    matches = []
    count = 0
    for path in segments:
        row_count, found = scan_segment(path, target)
        count += row_count
        matches.extend(found)
    return {
        "host": host,
        "assetsDirectory": str(folder.resolve()),
        "targetContentIdPrefix": target.hex(),
        "segmentsInspected": len(segments),
        "metadataSlotsInspected": count,
        "matches": matches,
        "uniqueIdPrefixCandidate": len(matches) == 1,
        "proofCeiling": "This is a matching table slot, not proven linked/active; the 8-byte ID is only a prefix, recorded SHA-1 is unverified, and digest covers inspected metadata only.",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--assets-dir", required=True, type=Path)
    parser.add_argument("--content-id", required=True, help="Manifest-derived 8-byte prefix as 16 hex digits")
    parser.add_argument("--expected-host", help="Optional exact Windows host gate")
    args = parser.parse_args()
    try:
        result = inspect(args.assets_dir, content_id(args.content_id), args.expected_host)
    except (OSError, ValueError) as exc:
        parser.error(str(exc))
    print(json.dumps(result, indent=2))
    return 0 if result["uniqueIdPrefixCandidate"] else 3


if __name__ == "__main__":
    raise SystemExit(main())
