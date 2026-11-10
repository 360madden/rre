"""Hash-gated, metadata-only TWAM v3 filename lookup.

No game process, RIFT input, VMware, extraction, payload read, or file writes.
Requires caller-selected source, exact SHA-256 and a source-backed filename.
The ASCII filename case is proven on LEGION; do not infer an unproved name.
"""
import argparse
import hashlib
import json
import socket
import struct
from pathlib import Path

FNV_OFFSET = 0x811C9DC5
FNV_PRIME = 0x01000193


def hash_name(name: str) -> tuple[str, bytes, int]:
    normalized = name.replace("\\", "/").lower()
    try:
        data = normalized.encode("ascii")
    except UnicodeEncodeError as exc:
        raise ValueError("Only ASCII filename hashing has been verified") from exc
    if not data or len(data) > 512 or "\x00" in normalized:
        raise ValueError("Expected a nonempty filename of at most 512 bytes, without NUL")
    value = FNV_OFFSET
    for byte in data:
        value = ((value * FNV_PRIME) & 0xFFFFFFFF) ^ byte
    return normalized, data, value


def table_ref(blob: bytes, index: int) -> tuple[int, int, int, int]:
    offset, size, count, stride = struct.unpack_from("<IIII", blob, 16 + 16 * index)
    if not stride or offset < 64 or offset > len(blob) or size > len(blob) - offset or count > size // stride:
        raise ValueError(f"Invalid TWAM table {index} bounds")
    return offset, size, count, stride


def inspect(blob: bytes, name: str) -> dict:
    if len(blob) < 64 or blob[:4] != b"TWAM":
        raise ValueError("Not a TWAM manifest")
    major, minor = struct.unpack_from("<HH", blob, 4)
    if (major, minor) != (3, 0):
        raise ValueError("Only TWAM version 3.0 is admitted")
    t0, t1, t2 = (table_ref(blob, n) for n in range(3))
    if t0[3] != 53 or t1[3] != 58 or t2[3] != 12:
        raise ValueError("Unexpected TWAM v3 table stride")
    normalized, name_bytes, name_hash = hash_name(name)
    matches = []
    same_hash_count = 0
    for index in range(t1[2]):
        start = t1[0] + index * t1[3]
        if struct.unpack_from("<I", blob, start + 8)[0] != name_hash:
            continue
        same_hash_count += 1
        name_len = struct.unpack_from("<H", blob, start + 56)[0]
        if name_len != len(name_bytes):
            continue
        pak_index = struct.unpack_from("<H", blob, start + 24)[0]
        if pak_index >= t0[2]:
            raise ValueError("Matched asset's PAK index is outside Table 0")
        pak_entry = t0[0] + pak_index * t0[3]
        string_offset = struct.unpack_from("<I", blob, pak_entry)[0]
        if not (t0[0] + t0[2] * t0[3] <= string_offset < t0[0] + t0[1]):
            raise ValueError("PAK name offset is outside Table 0 strings")
        string_end = blob.find(b"\x00", string_offset, t0[0] + t0[1])
        if string_end == -1:
            raise ValueError("PAK name is not terminated")
        pak_name = blob[string_offset:string_end].decode("utf-8", errors="strict")
        matches.append({
            "table1Index": index,
            "nameLengthBytes": name_len,
            "languageCode": blob[start + 31],
            "assetIdPrefix": blob[start:start + 8].hex(),
            "pakIndex": pak_index,
            "virtualPakName": pak_name,
        })
    return {
        "format": "TWAM", "major": major, "minor": minor,
        "table0Count": t0[2], "table1Count": t1[2], "table2Count": t2[2],
        "normalizedFilename": normalized, "filenameBytes": len(name_bytes),
        "fnv1": f"0x{name_hash:08X}",
        "hashMatches": same_hash_count, "lengthMatches": len(matches),
        "matches": matches,
        "uniqueHashLengthCandidate": len(matches) == 1,
        "proofCeiling": "A unique FNV-1 plus length record is not plaintext filename proof; hash collisions remain possible.",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--sha256", required=True, help="Exact approved on-disk manifest SHA-256")
    parser.add_argument("--filename", required=True, help="Source-backed asset filename (not a UI label)")
    parser.add_argument("--expected-host", help="Optional machine identity gate")
    args = parser.parse_args()
    if args.expected_host and socket.gethostname().upper() != args.expected_host.upper():
        parser.error("Host does not match --expected-host")
    if len(args.sha256) != 64 or any(c not in "0123456789abcdefABCDEF" for c in args.sha256):
        parser.error("--sha256 must be a 64-digit hex digest")
    blob = args.manifest.read_bytes()
    actual = hashlib.sha256(blob).hexdigest()
    if actual != args.sha256.lower():
        parser.error("Manifest SHA-256 mismatch; refusing unqualified source")
    result = inspect(blob, args.filename)
    result.update({"source": str(args.manifest.resolve()), "sourceSha256": actual, "host": socket.gethostname()})
    print(json.dumps(result, indent=2))
    return 0 if result["uniqueHashLengthCandidate"] else 3


if __name__ == "__main__":
    raise SystemExit(main())
