"""Inspect one SHA-gated, linked RIFT TWAD language CDS entry without writing files.

Only the named archive's 20-byte header, bounded 44-byte table and one
compressed entry are read. No RIFT process, full archive or VMware access.
This inventories keys and record framing; it does NOT decode Huffman/DAT text.
"""
import argparse
import hashlib
import json
import re
import socket
import struct
import zlib
from pathlib import Path

TWAD_HEADER = struct.Struct("<4sIIII")
TWAD_ENTRY = struct.Struct("<8sIIIHH20s")
MAX_ROWS = 4096
MAX_TABLE_BYTES = 262144
MAX_PACKED = 16 * 1024 * 1024
MAX_EXPANDED = 32 * 1024 * 1024
MAX_ENTRIES = 200000
MAX_RECORD = 16 * 1024 * 1024
HEX_SHA256 = re.compile(r"[0-9a-fA-F]{64}\Z")
HEX_ID = re.compile(r"[0-9a-fA-F]{16}\Z")


def read_uleb32(data: bytes, position: int) -> tuple[int, int]:
    value = 0
    for shift in range(0, 35, 7):
        if position >= len(data):
            raise ValueError("truncated unsigned LEB128")
        byte = data[position]
        position += 1
        if shift == 28 and byte > 15:
            raise ValueError("unsigned LEB128 exceeds 32 bits")
        value |= (byte & 127) << shift
        if not byte & 128:
            return value, position
    raise ValueError("unterminated unsigned LEB128")


def inventory_cds(data: bytes) -> dict:
    """Validate every CDS key, offset and framed Huffman record, not record text."""
    if len(data) < 1028:
        raise ValueError("CDS header truncated")
    (count,) = struct.unpack_from("<i", data)
    if count < 1 or count > MAX_ENTRIES or 1028 + 7 * count > len(data):
        raise ValueError("CDS entry count violates size or count cap")
    frequencies = struct.unpack_from("<256I", data, 4)
    position = 1028
    keys = []
    offsets = []
    previous_key = None
    ascending = True
    for _ in range(count):
        if position + 4 > len(data):
            raise ValueError("truncated CDS key")
        (key,) = struct.unpack_from("<i", data, position)
        position += 4
        offset, position = read_uleb32(data, position)
        if previous_key is not None and key <= previous_key:
            ascending = False
        previous_key = key
        keys.append(key)
        offsets.append(offset)
    if len(set(keys)) != count:
        raise ValueError("duplicate CDS key")
    records_start = position
    total_unpacked = 0
    max_packed = 0
    max_unpacked = 0
    zero_records = 0
    for record_index in range(count):
        # The real English asset's offsets equal the beginning of each record
        # frame relative to this section; enforce rather than silently ignoring.
        if offsets[record_index] != position - records_start:
            raise ValueError("CDS index offset does not match record frame")
        packed, position = read_uleb32(data, position)
        unpacked, position = read_uleb32(data, position)
        if packed > MAX_RECORD or unpacked > MAX_RECORD:
            raise ValueError("CDS per-record size limit exceeded")
        if packed > len(data) - position:
            raise ValueError("CDS compressed record truncated")
        if packed == 0 or unpacked == 0:
            zero_records += 1
        total_unpacked += unpacked
        if total_unpacked > MAX_EXPANDED * 2:
            raise ValueError("CDS aggregate Huffman output cap exceeded")
        max_packed = max(max_packed, packed)
        max_unpacked = max(max_unpacked, unpacked)
        position += packed
    if position != len(data):
        raise ValueError("unexpected bytes after final CDS record")
    return {
        "entryCount": count,
        "uniqueKeys": count,
        "strictlyIncreasingKeys": ascending,
        "indexBytes": records_start - 1028,
        "framedRecordBytes": len(data) - records_start,
        "offsetsMatchingFrames": count,
        "firstKey": keys[0],
        "lastKey": keys[-1],
        "frequencySumLE": sum(frequencies),
        "totalAdvertisedHuffmanBytes": total_unpacked,
        "frequencySumMinusAdvertised": sum(frequencies) - total_unpacked,
        "emptySizedRecords": zero_records,
        "maxRecordPackedBytes": max_packed,
        "maxRecordUnpackedBytes": max_unpacked,
        "contentTextDecoded": False,
    }


def archive_entry(archive: Path, entry_index: int, metadata_sha256: str, content_id: str) -> dict:
    if not HEX_SHA256.fullmatch(metadata_sha256) or not HEX_ID.fullmatch(content_id):
        raise ValueError("expected metadata SHA256 or 8-byte content ID malformed")
    if archive.is_symlink() or not archive.is_file():
        raise ValueError("archive must be an existing regular non-link file")
    archive_size = archive.stat().st_size
    with archive.open("rb") as stream:
        header = stream.read(TWAD_HEADER.size)
        if len(header) != TWAD_HEADER.size:
            raise ValueError("TWAD header truncated")
        magic, version, table_offset, count, first_link = TWAD_HEADER.unpack(header)
        table_size = count * TWAD_ENTRY.size
        if (magic != b"TWAD" or version != 1 or not 0 < count <= MAX_ROWS
                or table_size > MAX_TABLE_BYTES or table_offset < 20
                or table_offset + table_size > archive_size):
            raise ValueError("unadmitted TWAD table layout")
        if entry_index < 0 or entry_index >= count:
            raise ValueError("entry index outside table")
        stream.seek(table_offset)
        table = stream.read(table_size)
        if len(table) != table_size:
            raise ValueError("TWAD table truncated")
        digest = hashlib.sha256(header + table).hexdigest()
        if digest != metadata_sha256.lower():
            raise ValueError("TWAD metadata SHA256 mismatch")
        seen = set()
        current = first_link - 1
        while current >= 0:
            if current >= count or current in seen:
                raise ValueError("invalid TWAD first/next linked chain")
            seen.add(current)
            (next_raw,) = struct.unpack_from("<H", table, current * 44 + 20)
            current = next_raw - 1
        if entry_index not in seen:
            raise ValueError("target not linked from TWAD header")
        id_bytes, offset, packed_size, _unknown, _next, flag, recorded_sha1 = (
            TWAD_ENTRY.unpack_from(table, entry_index * 44))
        if id_bytes.hex() != content_id.lower() or flag != 1:
            raise ValueError("content ID or compression flag mismatch")
        if packed_size == 0 or packed_size > MAX_PACKED or offset < table_offset + table_size or packed_size > archive_size - offset:
            raise ValueError("entry payload bounds or cap rejected")
        stream.seek(offset)
        decoder = zlib.decompressobj()
        packed_digest = hashlib.sha1()
        expanded_digest = hashlib.sha1()
        chunks = []
        expanded_size = 0
        remaining = packed_size
        while remaining:
            block = stream.read(min(65536, remaining))
            if not block:
                raise ValueError("short TWAD payload")
            remaining -= len(block)
            packed_digest.update(block)
            plain = decoder.decompress(block, MAX_EXPANDED - expanded_size + 1)
            expanded_size += len(plain)
            if expanded_size > MAX_EXPANDED or decoder.unconsumed_tail or decoder.unused_data:
                raise ValueError("TWAD zlib expansion cap or trailing bytes")
            chunks.append(plain)
            expanded_digest.update(plain)
        last = decoder.flush(MAX_EXPANDED - expanded_size + 1)
        expanded_size += len(last)
        if expanded_size > MAX_EXPANDED or not decoder.eof or decoder.unconsumed_tail or decoder.unused_data:
            raise ValueError("incomplete, oversized or trailing TWAD zlib stream")
        chunks.append(last)
        expanded_digest.update(last)
    if packed_digest.digest() != recorded_sha1:
        raise ValueError("TWAD compressed SHA1 does not match recorded entry digest")
    if expanded_digest.digest()[:8] != id_bytes:
        raise ValueError("TWAD decompressed SHA1 prefix does not match content ID")
    plain_data = b"".join(chunks)
    summary = inventory_cds(plain_data)
    summary.update({
        "archive": str(archive),
        "entryIndex": entry_index,
        "linkedToHeader": True,
        "linkedRows": len(seen),
        "metadataSha256": digest,
        "contentIdPrefix": content_id.lower(),
        "recordedCompressedSha1": recorded_sha1.hex(),
        "verifiedDecompressedSha1": expanded_digest.hexdigest(),
        "verifiedDecompressedSha256": hashlib.sha256(plain_data).hexdigest(),
        "packedBytes": packed_size,
        "expandedBytes": expanded_size,
        "readWholeArchive": False,
        "filesWritten": False,
        "proofCeiling": "Validated one linked TWAD payload and all CDS key/frame boundaries. No Huffman/DAT text or Ability Queue value mapping proven.",
    })
    return summary


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--archive", required=True, type=Path)
    parser.add_argument("--entry-index", required=True, type=int)
    parser.add_argument("--metadata-sha256", required=True)
    parser.add_argument("--content-id", required=True)
    parser.add_argument("--expected-host", required=True)
    args = parser.parse_args()
    try:
        if socket.gethostname().upper() != args.expected_host.upper():
            raise ValueError("host does not match --expected-host")
        result = archive_entry(args.archive, args.entry_index, args.metadata_sha256, args.content_id)
    except (OSError, ValueError, zlib.error) as exc:
        parser.error(str(exc))
    print(json.dumps({"host": socket.gethostname(), **result}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
