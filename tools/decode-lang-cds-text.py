"""Source-faithful RIFT CDS Huffman decode plus narrowly admitted DAT string lookup.

String conversion defaults to the original C# reference's lossy ASCII mode;
explicit strict UTF-8 is a physical-asset-qualified improvement, not a claim
that the historical CStringConvertor.cs used UTF-8.

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
# Exact no-string DAT shape observed at English CDS key 0 on pinned LEGION asset.
# Keep this narrow: it is a valid framed object, NOT an inferred empty label.
KEY_ZERO_NO_TEXT_DAT = bytes.fromhex("9b3ca701bb05029d3c0707")


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



def lookup_key(data: bytes, key: int, text_encoding: str = "reference-ascii") -> dict:
    """Lookup one signed CDS key without Huffman-decoding unrelated records."""
    if type(key) is not int or not -(1 << 31) <= key < (1 << 31):
        raise ValueError("CDS key outside signed 32-bit range")
    if text_encoding not in ("reference-ascii", "utf8-strict"):
        raise ValueError("unsupported DAT string decoding mode")

    # The same complete key/frame integrity gate used by archive_entry. It
    # proves a missing key is absent; it does not decode every record's DAT.
    inventory = INSPECT.inventory_cds(data)
    count = inventory["entryCount"]
    position = 1028
    selected = None
    for index in range(count):
        (observed_key,) = struct.unpack_from("<i", data, position)
        position += 4
        offset, position = INSPECT.read_uleb32(data, position)
        if observed_key == key:
            selected = (index, offset)
    result = {
        "lookupMode": "signed-cds-key",
        "key": key,
        "keyFound": selected is not None,
        "keyAbsenceQualified": selected is None,
        "recordsIndexed": count,
        "huffmanRecordsDecoded": 0 if selected is None else 1,
        "recordIndex": selected[0] if selected else None,
        "recordStatus": "key-absent",
        "recordQualified": False,
        "textDecodeMode": text_encoding,
        "text": None,
        "textByteLength": None,
        "nonAsciiSource": None,
        "lossyAscii": False,
        "proofCeiling": ("Key presence/absence applies only to this validated CDS index. "
                         "Text requires the selected Huffman/DAT record; a missing or "
                         "unqualified record is not an empty label. No RIFT Ability "
                         "Queue numeric enum mapping is established."),
    }
    if selected is None:
        return result

    index, offset = selected
    position += offset  # CDS offsets are relative to the end of the key index.
    packed_size, position = INSPECT.read_uleb32(data, position)
    unpacked_size, position = INSPECT.read_uleb32(data, position)
    packed = data[position:position + packed_size]
    frequencies = struct.unpack_from("<256I", data, 4)
    decoded = decode_huffman(packed, unpacked_size, huffman_code_tree(frequencies))
    if key == 0 and decoded == KEY_ZERO_NO_TEXT_DAT:
        result.update(recordStatus="qualified-no-text", recordQualified=True)
        return result

    try:
        raw = dat_text(decoded)
    except ValueError as exc:
        result.update(recordStatus="unqualified-dat-shape", reason=str(exc))
        return result
    non_ascii = any(b > 127 for b in raw)
    result["nonAsciiSource"] = non_ascii
    result["textByteLength"] = len(raw)
    if text_encoding == "utf8-strict":
        try:
            text = raw.decode("utf-8", errors="strict")
        except UnicodeDecodeError:
            result["recordStatus"] = "unqualified-invalid-utf8"
            return result
    else:
        text = raw.decode("ascii", errors="replace")
        result["lossyAscii"] = non_ascii
    result.update(recordStatus="qualified-text", recordQualified=True, text=text)
    return result

def find_text(data: bytes, needles: list[str], max_records: int, max_hits: int,
              exact: bool = False, text_encoding: str = "reference-ascii") -> dict:
    # The caller must first use INSPECT.archive_entry(... include_payload=True).
    if text_encoding not in ("reference-ascii", "utf8-strict"):
        raise ValueError("unsupported DAT string decoding mode")
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
    no_text_records = 0
    non_ascii_strings = 0
    invalid_utf8_strings = 0
    invalid_utf8_examples = []
    rejected_samples = []
    checked = min(max_records, entry_count)
    terms = [term.lower() for term in needles]
    for index in range(checked):
        packed_size, pos = INSPECT.read_uleb32(data, pos)
        unpacked_size, pos = INSPECT.read_uleb32(data, pos)
        packed = data[pos:pos + packed_size]
        pos += packed_size
        decoded = decode_huffman(packed, unpacked_size, tree)
        if keys[index] == 0 and decoded == KEY_ZERO_NO_TEXT_DAT:
            no_text_records += 1
            continue
        try:
            text_bytes = dat_text(decoded)
        except ValueError as exc:
            dat_rejections += 1
            if len(rejected_samples) < 5:
                rejected_samples.append({"index": index, "key": keys[index], "reason": str(exc)})
            continue
        if any(b > 127 for b in text_bytes):
            non_ascii_strings += 1
        if text_encoding == "utf8-strict":
            try:
                txt = text_bytes.decode("utf-8", errors="strict")
            except UnicodeDecodeError:
                invalid_utf8_strings += 1
                if len(invalid_utf8_examples) < 5:
                    invalid_utf8_examples.append({"index": index, "key": keys[index]})
                continue
        else:
            txt = text_bytes.decode("ascii", errors="replace")
        if any((txt.lower() == term if exact else term in txt.lower()) for term in terms):
            matched += 1
            if len(hits) < max_hits:
                hits.append({"key": keys[index], "textPreview": txt[:180]})
    return {
        "recordsChecked": checked,
        "recordsTotal": entry_count,
        "qualifiedDatTextRecords": checked - dat_rejections - no_text_records - invalid_utf8_strings,
        "qualifiedDatNoTextRecords": no_text_records,
        "unqualifiedDatShapes": dat_rejections,
        "nonAsciiTextRecords": non_ascii_strings,
        "invalidUtf8TextRecords": invalid_utf8_strings,
        "invalidUtf8Examples": invalid_utf8_examples,
        "textDecodeMode": text_encoding,
        "unqualifiedExamples": rejected_samples,
        "queryTerms": needles,
        "matchMode": "exact" if exact else "contains",
        "matchCount": matched,
        "boundedHits": hits,
        "truncatedHits": matched > len(hits),
        "absenceQualified": (checked == entry_count and dat_rejections == 0
                             and (non_ascii_strings == 0 if text_encoding == "reference-ascii"
                                  else invalid_utf8_strings == 0)),
        "proofCeiling": ("Search scope is this one SHA-verified CDS asset and admitted DAT shapes only. "
                         "Reference C# converts strings using ASCII replacement; utf8-strict is "
                         "independently validated against this physical English asset, not C# parity. "
                         "No RIFT UI numeric enum relation is established."),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--archive", required=True, type=Path)
    parser.add_argument("--entry-index", required=True, type=int)
    parser.add_argument("--metadata-sha256", required=True)
    parser.add_argument("--content-id", required=True)
    parser.add_argument("--expected-host", required=True)
    target = parser.add_mutually_exclusive_group(required=True)
    target.add_argument("--contains", action="append", help="Search text labels")
    target.add_argument("--key", type=int, help="Look up one signed 32-bit CDS key (decimal)")
    parser.add_argument("--max-records", type=int, default=3)
    parser.add_argument("--max-hits", type=int, default=20)
    parser.add_argument("--exact", action="store_true", help="Case-insensitive whole-label match")
    parser.add_argument("--text-encoding", choices=("reference-ascii", "utf8-strict"),
                        default="reference-ascii", help="Reference C# ASCII or opt-in strict UTF-8")
    args = parser.parse_args()
    try:
        if socket.gethostname().upper() != args.expected_host.upper():
            raise ValueError("host does not match --expected-host")
        if args.key is None:
            if not 0 < args.max_records <= 200000 or not 0 < args.max_hits <= 50:
                raise ValueError("record/hit count outside cap")
            if any(not term or len(term) > 120 for term in args.contains):
                raise ValueError("empty or oversized search term")
        elif args.exact or args.max_records != 3 or args.max_hits != 20:
            raise ValueError("--exact/--max-records/--max-hits apply only to --contains")
        source, payload = INSPECT.archive_entry(
            args.archive, args.entry_index, args.metadata_sha256, args.content_id, True)
        if args.key is None:
            result = find_text(payload, args.contains, args.max_records, args.max_hits,
                               args.exact, args.text_encoding)
        else:
            result = lookup_key(payload, args.key, args.text_encoding)
    except (OSError, ValueError) as exc:
        parser.error(str(exc))
    print(json.dumps({"host": socket.gethostname(),
                      "contentIdPrefix": source["contentIdPrefix"], **result}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
