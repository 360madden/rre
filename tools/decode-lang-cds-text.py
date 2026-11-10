"""Source-faithful RIFT CDS Huffman decode plus narrowly admitted DAT string lookup.

Requires inspect-lang-cds.py integrity checks on exactly one selected archive
entry before decoding. DAT parser accepts only the documented, observed
root/object shape, and reports other shapes as unqualified (never empty text).
No files are written and no game, VM or process APIs are used.
"""
import argparse
import importlib.util
import json
import socket
import struct
from pathlib import Path

LOADER = Path(__file__).with_name("inspect-lang-cds.py")
SPEC = importlib.util.spec_from_file_location("rre_inspect_lang_cds", LOADER)
INSPECT = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(INSPECT)
SYMBOLS = 256
MAX_TREE_DEPTH = 31
MAX_TEXT_RECORD = 16384


def split_code(token: int) -> tuple[int, int]:
    code = token & 7
    if code != 7:
        return code, token >> 3
    extension = (token >> 3) & 7
    if extension > 4:
        raise ValueError("invalid extended DAT token")
    return extension + 8, token >> 6


def dat_text(record: bytes) -> bytes:
    """Parse a bounded 1-pair DAT map, signed key and nested class/string."""
    pos = 0

    def uleb():
        nonlocal pos
        value, pos = INSPECT.read_uleb32(record, pos)
        return value

    root_class = uleb()
    root_code, _root_member = split_code(uleb())
    if (root_class, root_code, _root_member) != (7707, 12, 2):
        raise ValueError("DAT root class/map different from qualified sample")
    pair_code = uleb()
    key_code, embedded = split_code(pair_code)
    value_code, pair_count = split_code(embedded)
    if (key_code, value_code, pair_count) != (3, 10, 1):
        raise ValueError("DAT map is not one signed-key/nested-class pair")
    signed_long_bits = uleb()  # observed signed-key encoding, not mapped to setting
    nested_class = uleb()
    if (signed_long_bits, nested_class) != (2, 7709):
        raise ValueError("DAT signed-key/class differs from qualified sample")
    string_code, string_index = split_code(uleb())
    if (string_code, string_index) != (6, 0):
        raise ValueError("first nested DAT child is not indexed string")
    byte_count = uleb()
    if byte_count > MAX_TEXT_RECORD or byte_count > len(record) - pos:
        raise ValueError("DAT text length invalid")
    raw = record[pos:pos + byte_count]
    pos += byte_count
    nested_end, _ = split_code(uleb())
    root_end, _ = split_code(uleb())
    if nested_end != 8 or root_end != 8 or pos != len(record):
        raise ValueError("DAT trailing or missing object end")
    return raw


def huffman_code_tree(frequencies: tuple[int, ...]) -> list[list[int]]:
    """Port C# HuffmanReader.buildTree2/heapify2/maketable tie behavior."""
    if len(frequencies) != SYMBOLS or any(not 0 < f <= 0x7FFFFFFF for f in frequencies):
        raise ValueError("invalid Huffman frequency table")
    if sum(frequencies) > 0x7FFFFFFF:
        raise ValueError("Huffman frequency accumulator exceeds signed-int range")
    half = SYMBOLS
    heap = [0] * (half * 2)
    for i, frequency in enumerate(frequencies):
        heap[i] = i
        heap[half + i] = frequency

    def heapify(insert: int, weight: int, value: int, limit: int):
        child = insert * 2
        while child <= limit:
            if child < limit and heap[half + child - 1] > heap[half + child]:
                child += 1
            if weight <= heap[half + child - 1]:
                break
            heap[insert - 1] = heap[child - 1]
            heap[half + insert - 1] = heap[half + child - 1]
            insert = child
            child = insert * 2
        heap[insert - 1] = value
        heap[half + insert - 1] = weight

    for i in range(half // 2, 0, -1):
        heapify(i, heap[half + i - 1], heap[i - 1], half)

    previous_frequency = 0
    turn = 0
    limit = half
    while True:
        turn += 1
        if turn & 1:
            limit -= 1
            value = heap[limit]
            weight = heap[half + limit]
            heap[limit] = heap[0]
            if limit == 1:
                heap[half + 1] = value
                break
            previous_frequency = heap[half]
            heapify(1, weight, value, limit)
        else:
            value = -limit
            weight = previous_frequency + heap[half]
            heap[half + limit] = heap[0]
            heapify(1, weight, value, limit)

    codes = [0] * half
    lengths = [0] * half
    depth_nodes = [0] * 32
    depth_nodes[0] = 1
    depth = 0
    code_value = 0
    while depth >= 0:
        result = heap[(code_value & 1) * half + depth_nodes[depth]]
        while result < 0:
            code_value *= 2
            depth += 1
            if depth >= len(depth_nodes):
                raise ValueError("Huffman tree depth exceeds cap")
            depth_nodes[depth] = -result
            result = heap[-result]
        if result >= half or lengths[result]:
            raise ValueError("Huffman leaf symbol invalid/duplicate")
        codes[result] = code_value
        lengths[result] = depth + 1
        while depth >= 0 and code_value & 1:
            code_value >>= 1
            depth -= 1
        code_value |= 1

    tree = [[-1, -1, -1]]
    for symbol in range(half):
        length = lengths[symbol]
        if length < 1 or length > MAX_TREE_DEPTH:
            raise ValueError("missing/overlong Huffman code")
        node = 0
        for bit_index in range(length - 1, -1, -1):
            side = (codes[symbol] >> bit_index) & 1
            child = tree[node][side]
            if child < 0:
                child = len(tree)
                tree[node][side] = child
                tree.append([-1, -1, -1])
            node = child
            if bit_index and tree[node][2] >= 0:
                raise ValueError("Huffman prefix conflict")
        if tree[node][2] >= 0 or tree[node][0] >= 0 or tree[node][1] >= 0:
            raise ValueError("Huffman code collision")
        tree[node][2] = symbol
    if len(tree) != 511:
        raise ValueError("not a complete 256-leaf Huffman tree")
    return tree


def decode_huffman(packed: bytes, expected_size: int, tree: list[list[int]]) -> bytes:
    if expected_size < 1 or expected_size > MAX_TEXT_RECORD:
        raise ValueError("per-record Huffman output outside cap")
    output = bytearray()
    node = 0
    for byte in packed:
        for shift in range(7, -1, -1):
            node = tree[node][(byte >> shift) & 1]
            if node < 0:
                raise ValueError("invalid Huffman bit path")
            symbol = tree[node][2]
            if symbol >= 0:
                output.append(symbol)
                node = 0
                if len(output) == expected_size:
                    return bytes(output)
    raise ValueError("Huffman input ended before advertised decoded size")


def find_text(data: bytes, needles: list[str], max_records: int, max_hits: int,
              exact: bool = False) -> dict:
    # The caller must first use INSPECT.archive_entry(... include_payload=True).
    (entry_count,) = struct.unpack_from("<i", data)
    frequencies = struct.unpack_from("<256I", data, 4)
    tree = huffman_code_tree(frequencies)
    keys = []
    pos = 1028
    for _ in range(entry_count):
        (key,) = struct.unpack_from("<i", data, pos)
        pos += 4
        _index_offset, pos = INSPECT.read_uleb32(data, pos)
        keys.append(key)
    matched = 0
    hits = []
    dat_rejections = 0
    non_ascii_strings = 0
    rejected_samples = []
    checked = min(max_records, entry_count)
    terms = [term.lower() for term in needles]
    for index in range(checked):
        packed_size, pos = INSPECT.read_uleb32(data, pos)
        unpacked_size, pos = INSPECT.read_uleb32(data, pos)
        packed = data[pos:pos + packed_size]
        pos += packed_size
        decoded = decode_huffman(packed, unpacked_size, tree)
        try:
            text_bytes = dat_text(decoded)
        except ValueError as exc:
            dat_rejections += 1
            if len(rejected_samples) < 5:
                rejected_samples.append({"index": index, "key": keys[index], "reason": str(exc)})
            continue
        if any(b > 127 for b in text_bytes):
            non_ascii_strings += 1
        txt = text_bytes.decode("ascii", errors="replace")
        if any((txt.lower() == term if exact else term in txt.lower()) for term in terms):
            matched += 1
            if len(hits) < max_hits:
                hits.append({"key": keys[index], "textPreview": txt[:180]})
    return {
        "recordsChecked": checked,
        "recordsTotal": entry_count,
        "qualifiedDatTextRecords": checked - dat_rejections,
        "unqualifiedDatShapes": dat_rejections,
        "nonAsciiTextRecords": non_ascii_strings,
        "unqualifiedExamples": rejected_samples,
        "queryTerms": needles,
        "matchMode": "exact" if exact else "contains",
        "matchCount": matched,
        "boundedHits": hits,
        "truncatedHits": matched > len(hits),
        "absenceQualified": checked == entry_count and dat_rejections == 0 and non_ascii_strings == 0,
        "proofCeiling": "Text matches from source-equivalent Huffman and a narrow observed DAT map shape; no RIFT UI enum relation established.",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--archive", required=True, type=Path)
    parser.add_argument("--entry-index", required=True, type=int)
    parser.add_argument("--metadata-sha256", required=True)
    parser.add_argument("--content-id", required=True)
    parser.add_argument("--expected-host", required=True)
    parser.add_argument("--contains", action="append", required=True)
    parser.add_argument("--max-records", type=int, default=3)
    parser.add_argument("--max-hits", type=int, default=20)
    parser.add_argument("--exact", action="store_true", help="Case-insensitive whole-label match")
    args = parser.parse_args()
    try:
        if socket.gethostname().upper() != args.expected_host.upper():
            raise ValueError("host does not match --expected-host")
        if not 0 < args.max_records <= 200000 or not 0 < args.max_hits <= 50:
            raise ValueError("record/hit count outside cap")
        if any(not term or len(term) > 120 for term in args.contains):
            raise ValueError("empty or oversized search term")
        source, payload = INSPECT.archive_entry(
            args.archive, args.entry_index, args.metadata_sha256, args.content_id, True)
        result = find_text(payload, args.contains, args.max_records, args.max_hits, args.exact)
    except (OSError, ValueError) as exc:
        parser.error(str(exc))
    print(json.dumps({"host": socket.gethostname(),
                      "contentIdPrefix": source["contentIdPrefix"], **result}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
