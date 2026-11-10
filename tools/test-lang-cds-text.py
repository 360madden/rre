"""Synthetic tests for source-equivalent Huffman and narrow DAT text parser."""
import base64
import importlib.util
import struct
import unittest
from pathlib import Path

SOURCE = Path(__file__).with_name("decode-lang-cds-text.py")
SPEC = importlib.util.spec_from_file_location("decode_lang_cds_text", SOURCE)
MOD = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MOD)


def uleb(value):
    out = bytearray()
    while True:
        part = value & 127
        value >>= 7
        out.append(part | (128 if value else 0))
        if not value:
            return bytes(out)


def dat_string(value):
    # Root class 7707, 1-element pair (signed key, class 7709), string/end/end.
    return bytes.fromhex("9b3ca701bb05029d3c06") + uleb(len(value)) + value + b"\x07\x07"


def codes_from_tree(tree):
    result = {}
    def traverse(node, bits):
        left, right, symbol = tree[node]
        if symbol >= 0:
            result[symbol] = bits
            return
        traverse(left, bits + "0")
        traverse(right, bits + "1")
    traverse(0, "")
    return result


def encode_huffman(value, codes):
    bits = "".join(codes[b] for b in value)
    bits += "0" * ((-len(bits)) % 8)
    return bytes(int(bits[i:i + 8], 2) for i in range(0, len(bits), 8))



def indexed_asset(records, frequencies, codes):
    """CDS payload from (signed key, DAT bytes, optional advertised size)."""
    frames = []
    offsets = []
    size = 0
    for _key, record, advertised in records:
        packed = encode_huffman(record, codes)
        frame = uleb(len(packed)) + uleb(len(record) if advertised is None else advertised) + packed
        offsets.append(size)
        frames.append(frame)
        size += len(frame)
    index = b"".join(struct.pack("<i", key) + uleb(offset)
                     for (key, _record, _advertised), offset in zip(records, offsets))
    return (struct.pack("<i", len(records)) + struct.pack("<256I", *frequencies)
            + index + b"".join(frames))


class CdsTextTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.frequency = [1] * 256
        cls.tree = MOD.huffman_code_tree(tuple(cls.frequency))
        cls.codes = codes_from_tree(cls.tree)

    def test_real_nonuniform_huffman_sample(self):
        # Hash-gated LEGION assets.002:1211, first English CDS frame.
        freqs = struct.unpack("<256I", base64.b64decode("AQAAACOkAgBziwIAYwIAAB8GAAAjjgIAGJICAEMZBQDODQAAuhEAAIYpAABXFgAAwBoAACkdAACuHAAAZhwAAJEZAACUFgAAxhIAADcRAABYEAAA/wwAAGcNAAA2DAAA3wsAAOAKAABwCwAAOAsAAOYIAADJCAAAqwcAAC8GAAC2FwwA6xYAACYHAADkBAAAlwUAAAPgAACWBAAAaTcAAJ8HAAC5BgAAkwQAAHIEAAAhPwAAJxMAABIUAQB8CQAAaKgAAJJpAACoIwAANxwAAG8QAABtIQAAKwsAANUHAAB0BwAA2QYAAJYkAABPAgAArhYFANgCAAACCwAAUwQAANcBAABL8QAA2GMAAMOgAAB1DAEA258AANBMAABnggAALUYAAFzHAACUCAAACRQAAB1rAAATAAEAO5AAANpaAACOhwAAfAYAAAycAADzwwAAKL8AAE9RAADHLwAAqTsAACUrAAD1FgAA0wMAAN6qAAATAQAAmKoAADkBAACeXQAAvwAAACSaBgBb9QAAABYCACdrAgAZ3AgAhm4BAHzCAQDCcQIAFEkEAL4HAADSmQAAnzwDABz2AQCCfwQAxckEAPsOAQCXDgAA+6EEAH1OBACYZAUAdNQBAMyTAADCqQAA9ioAAK85AQCuEgAAlQAAAIgAAACwAAAA+AAAAKsAAADmAQAAhwAAAKwAAAC3AAAACAEAAH0AAABZAAAAoQAAAKIAAABbAAAAdAAAAGUAAACCAAAAXQAAAKYAAACLAAAAkQAAAJcAAACaAAAAowAAAH0AAABrAAAAgwAAAGwAAABhAAAA8AEAAGAAAAAKhwIAUQAAANSGAgBbAAAAXwAAAFQAAABrAAAAYAAAAFcAAACDAAAAWwAAAHMAAADEhgIAQwAAAD8AAAA9AAAAUwAAAHIAAABEAAAARwAAAB4AAABJAAAAQAAAAEAAAABWAAAAdwAAAFAAAAAiAAAAOgAAACsAAABJAAAAMAAAAJCGAgBYAAAAQQAAAEEAAAAlAAAAKgAAAFgAAAB1AAAAMAAAACwAAAA6AAAAOAAAADEAAAA/AAAAOQAAAEEAAAAvAAAAJAAAAEIAAAAtAAAATgAAAC8AAAAkAAAALgAAADMAAAA2AAAARAAAABYAAAApAAAAPwAAABIAAAAWAAAADgAAACQAAAAmAAAAQQAAABoAAAAtAAAAFQAAAM4BAAA4AAAAEAAAACcAAAAsAAAAMAAAABoAAAAaAAAAGwAAABkAAAANAAAAJgAAABoAAAAsAAAAHgAAADIAAAAOAAAAHQAAAA0AAAAaAAAADgAAABAAAAAjAAAAEAAAACYAAAAQAAAADQAAAB0AAAAgAAAAGQAAAA=="))
        self.assertGreater(max(freqs), min(freqs))
        tree = MOD.huffman_code_tree(freqs)
        raw = MOD.decode_huffman(bytes.fromhex("db9a7f9f9bebcf4771d5d00b078d6e6706caf5777a"), 29, tree)
        self.assertEqual(raw, bytes.fromhex("9b3ca701bb05029d3c0610566f6c7461696320466565646261636b0707"))
        self.assertEqual(MOD.dat_text(raw), b"Voltaic Feedback")

    def test_uniform_complete_tree(self):
        self.assertEqual(len(self.tree), 511)
        self.assertEqual(len(self.codes), 256)
        self.assertEqual(set(map(len, self.codes.values())), {8})

    def test_huffman_roundtrip_text(self):
        for value in (b"hello", b"Ability Queue:", bytes(range(256))):
            packed = encode_huffman(value, self.codes)
            self.assertEqual(MOD.decode_huffman(packed, len(value), self.tree), value)

    def test_real_sample_dat_structure(self):
        record = bytes.fromhex("9b3ca701bb05029d3c0610566f6c7461696320466565646261636b0707")
        self.assertEqual(MOD.dat_text(record), b"Voltaic Feedback")

    def test_dat_fixture_matches_reference(self):
        self.assertEqual(MOD.dat_text(dat_string(b"Ability Queue:")), b"Ability Queue:")

    def test_dat_missing_end_rejected(self):
        with self.assertRaises(ValueError):
            MOD.dat_text(dat_string(b"Ability Queue:")[:-1])

    def test_dat_extra_rejected(self):
        with self.assertRaisesRegex(ValueError, "trailing"):
            MOD.dat_text(dat_string(b"Text") + b"\x07")

    def test_dat_wrong_class_rejected(self):
        wrong = b"\x01" + dat_string(b"Text")[2:]
        with self.assertRaisesRegex(ValueError, "root class"):
            MOD.dat_text(wrong)

    def test_truncated_huffman_rejected(self):
        text = b"test"
        packed = encode_huffman(text, self.codes)
        with self.assertRaisesRegex(ValueError, "ended"):
            MOD.decode_huffman(packed[:-1], len(text), self.tree)

    def test_invalid_extended_code(self):
        with self.assertRaisesRegex(ValueError, "extended"):
            MOD.split_code(7 | (5 << 3))

    def test_invalid_frequency(self):
        with self.assertRaisesRegex(ValueError, "frequency"):
            MOD.huffman_code_tree(tuple([0] + [1] * 255))

    def test_search_exact_vs_contains(self):
        title = b"Ability Queue:"
        data = dat_string(title)
        compressed = encode_huffman(data, self.codes)
        frame = uleb(len(compressed)) + uleb(len(data)) + compressed
        asset = (struct.pack("<i", 1) + struct.pack("<256I", *self.frequency)
                 + struct.pack("<i", 2137386253) + b"\x00" + frame)
        self.assertEqual(MOD.INSPECT.inventory_cds(asset)["entryCount"], 1)
        exact = MOD.find_text(asset, ["Ability Queue:"], 1, 3, True)
        self.assertEqual(exact["matchCount"], 1)
        self.assertEqual(exact["unqualifiedDatShapes"], 0)
        self.assertTrue(exact["absenceQualified"])
        self.assertEqual(MOD.find_text(asset, ["Ability Queue"], 1, 3, True)["matchCount"], 0)
        self.assertEqual(MOD.find_text(asset, ["Ability Queue"], 1, 3, False)["matchCount"], 1)


    def test_non_ascii_never_qualifies_negative_absence(self):
        title = b"Caf\xc3\xa9"
        data = dat_string(title)
        packed = encode_huffman(data, self.codes)
        frame = uleb(len(packed)) + uleb(len(data)) + packed
        asset = (struct.pack("<i", 1) + struct.pack("<256I", *self.frequency)
                 + struct.pack("<i", 17) + b"\x00" + frame)
        result = MOD.find_text(asset, ["Unrelated"], 1, 3, True)
        self.assertEqual(result["nonAsciiTextRecords"], 1)
        self.assertFalse(result["absenceQualified"])

    def test_observed_key_zero_no_text_shape_is_separately_qualified(self):
        record = MOD.KEY_ZERO_NO_TEXT_DAT
        self.assertEqual(record.hex(), "9b3ca701bb05029d3c0707")
        packed = encode_huffman(record, self.codes)
        frame = uleb(len(packed)) + uleb(len(record)) + packed
        asset = (struct.pack("<i", 1) + struct.pack("<256I", *self.frequency)
                 + struct.pack("<i", 0) + b"\x00" + frame)
        self.assertEqual(MOD.INSPECT.inventory_cds(asset)["entryCount"], 1)
        result = MOD.find_text(asset, ["Ability Queue:"], 1, 3, True)
        self.assertEqual(result["qualifiedDatNoTextRecords"], 1)
        self.assertEqual(result["qualifiedDatTextRecords"], 0)
        self.assertEqual(result["unqualifiedDatShapes"], 0)
        self.assertEqual(result["matchCount"], 0)
        self.assertTrue(result["absenceQualified"])
        with self.assertRaises(ValueError):
            MOD.dat_text(record)  # no generic empty-string admission

    def test_nonzero_key_never_admits_the_observed_no_text_sentinel(self):
        record = MOD.KEY_ZERO_NO_TEXT_DAT
        packed = encode_huffman(record, self.codes)
        frame = uleb(len(packed)) + uleb(len(record)) + packed
        asset = (struct.pack("<i", 1) + struct.pack("<256I", *self.frequency)
                 + struct.pack("<i", 17) + b"\x00" + frame)
        result = MOD.find_text(asset, ["Ability Queue:"], 1, 3, True)
        self.assertEqual(result["qualifiedDatNoTextRecords"], 0)
        self.assertEqual(result["unqualifiedDatShapes"], 1)
        self.assertFalse(result["absenceQualified"])

    def test_opt_in_utf8_exact_unicode_search_and_absence(self):
        text = "Café".encode("utf-8")
        record = dat_string(text)
        packed = encode_huffman(record, self.codes)
        frame = uleb(len(packed)) + uleb(len(record)) + packed
        asset = (struct.pack("<i", 1) + struct.pack("<256I", *self.frequency)
                 + struct.pack("<i", 17) + b"\x00" + frame)
        result = MOD.find_text(asset, ["CAFÉ"], 1, 3, True, "utf8-strict")
        self.assertEqual(result["matchCount"], 1)
        self.assertEqual(result["boundedHits"][0]["textPreview"], "Café")
        self.assertEqual(result["nonAsciiTextRecords"], 1)
        self.assertEqual(result["invalidUtf8TextRecords"], 0)
        self.assertEqual(result["textDecodeMode"], "utf8-strict")
        self.assertTrue(result["absenceQualified"])
        missing = MOD.find_text(asset, ["No such text"], 1, 3, True, "utf8-strict")
        self.assertEqual(missing["matchCount"], 0)
        self.assertTrue(missing["absenceQualified"])
        reference = MOD.find_text(asset, ["CAFÉ"], 1, 3, True)
        self.assertEqual(reference["textDecodeMode"], "reference-ascii")
        self.assertEqual(reference["matchCount"], 0)
        self.assertFalse(reference["absenceQualified"])

    def test_invalid_utf8_is_reported_and_cannot_qualify_absence(self):
        record = dat_string(b"Caf\xff")
        packed = encode_huffman(record, self.codes)
        frame = uleb(len(packed)) + uleb(len(record)) + packed
        asset = (struct.pack("<i", 1) + struct.pack("<256I", *self.frequency)
                 + struct.pack("<i", 17) + b"\x00" + frame)
        result = MOD.find_text(asset, ["CAF"], 1, 3, False, "utf8-strict")
        self.assertEqual(result["matchCount"], 0)
        self.assertEqual(result["invalidUtf8TextRecords"], 1)
        self.assertEqual(result["qualifiedDatTextRecords"], 0)
        self.assertEqual(result["invalidUtf8Examples"], [{"index": 0, "key": 17}])
        self.assertFalse(result["absenceQualified"])

    def test_utf8_partial_scan_cannot_qualify_absence(self):
        record = dat_string("Café".encode("utf-8"))
        packed = encode_huffman(record, self.codes)
        frame = uleb(len(packed)) + uleb(len(record)) + packed
        asset = (struct.pack("<i", 2) + struct.pack("<256I", *self.frequency)
                 + struct.pack("<i", 17) + b"\x00"
                 + struct.pack("<i", 18) + uleb(len(frame)) + frame + frame)
        self.assertEqual(MOD.INSPECT.inventory_cds(asset)["entryCount"], 2)
        result = MOD.find_text(asset, ["Not present"], 1, 3, True, "utf8-strict")
        self.assertEqual(result["recordsChecked"], 1)
        self.assertFalse(result["absenceQualified"])

    def test_unknown_text_decode_mode_rejected_before_input_parse(self):
        with self.assertRaisesRegex(ValueError, "unsupported DAT string decoding mode"):
            MOD.find_text(b"", ["needle"], 1, 1, False, "unknown")



    def test_direct_key_last_record_skips_irrelevant_huffman(self):
        from unittest.mock import patch
        records = [
            (-5, b"not a qualified DAT string", None),
            (0, MOD.KEY_ZERO_NO_TEXT_DAT, None),
            (2147483647, dat_string(b"Target"), None),
        ]
        asset = indexed_asset(records, self.frequency, self.codes)
        self.assertEqual(MOD.INSPECT.inventory_cds(asset)["entryCount"], 3)
        with patch.object(MOD, "decode_huffman", wraps=MOD.decode_huffman) as decode:
            result = MOD.lookup_key(asset, 2147483647)
        self.assertEqual(decode.call_count, 1)
        self.assertEqual(result["recordIndex"], 2)
        self.assertEqual(result["text"], "Target")
        self.assertTrue(result["recordQualified"])
        self.assertFalse(result["keyAbsenceQualified"])
        self.assertEqual(result["huffmanRecordsDecoded"], 1)

    def test_direct_absent_key_qualifies_index_only_without_huffman(self):
        from unittest.mock import patch
        asset = indexed_asset([(0, MOD.KEY_ZERO_NO_TEXT_DAT, None),
                               (17, dat_string(b"Existing"), None)],
                              self.frequency, self.codes)
        with patch.object(MOD, "decode_huffman", side_effect=AssertionError("must not decode")):
            with patch.object(MOD, "huffman_code_tree",
                              side_effect=AssertionError("must not build tree")):
                result = MOD.lookup_key(asset, -1)
        self.assertFalse(result["keyFound"])
        self.assertTrue(result["keyAbsenceQualified"])
        self.assertIsNone(result["text"])
        self.assertEqual(result["huffmanRecordsDecoded"], 0)
        self.assertEqual(result["recordStatus"], "key-absent")

    def test_direct_signed_minimum_and_zero_no_text(self):
        asset = indexed_asset([(-(1 << 31), dat_string(b"Minimum"), None),
                               (0, MOD.KEY_ZERO_NO_TEXT_DAT, None)],
                              self.frequency, self.codes)
        self.assertEqual(MOD.lookup_key(asset, -(1 << 31))["text"], "Minimum")
        zero = MOD.lookup_key(asset, 0)
        self.assertTrue(zero["keyFound"])
        self.assertFalse(zero["keyAbsenceQualified"])
        self.assertTrue(zero["recordQualified"])
        self.assertEqual(zero["recordStatus"], "qualified-no-text")
        self.assertIsNone(zero["text"])
        self.assertIsNone(zero["textByteLength"])

    def test_nonzero_key_no_text_sentinel_not_empty_label(self):
        asset = indexed_asset([(17, MOD.KEY_ZERO_NO_TEXT_DAT, None)],
                              self.frequency, self.codes)
        result = MOD.lookup_key(asset, 17)
        self.assertTrue(result["keyFound"])
        self.assertEqual(result["recordStatus"], "unqualified-dat-shape")
        self.assertFalse(result["recordQualified"])
        self.assertIsNone(result["text"])

    def test_direct_utf8_strict_and_lossy_reference_ascii(self):
        asset = indexed_asset([(17, dat_string("Café".encode("utf-8")), None)],
                              self.frequency, self.codes)
        strict = MOD.lookup_key(asset, 17, "utf8-strict")
        self.assertEqual(strict["text"], "Café")
        self.assertFalse(strict["lossyAscii"])
        reference = MOD.lookup_key(asset, 17)
        self.assertEqual(reference["text"], "Caf��")
        self.assertTrue(reference["lossyAscii"])
        self.assertTrue(reference["recordQualified"])

    def test_direct_invalid_utf8_never_reports_empty_text(self):
        asset = indexed_asset([(17, dat_string(b"Caf\xff"), None)],
                              self.frequency, self.codes)
        result = MOD.lookup_key(asset, 17, "utf8-strict")
        self.assertEqual(result["recordStatus"], "unqualified-invalid-utf8")
        self.assertFalse(result["recordQualified"])
        self.assertIsNone(result["text"])
        self.assertFalse(result["keyAbsenceQualified"])

    def test_direct_target_huffman_truncation_is_error(self):
        asset = indexed_asset([(17, dat_string(b"Hi"), 100)],
                              self.frequency, self.codes)
        self.assertEqual(MOD.INSPECT.inventory_cds(asset)["entryCount"], 1)
        with self.assertRaisesRegex(ValueError, "ended"):
            MOD.lookup_key(asset, 17)

    def test_direct_key_range_and_encoding_checked(self):
        for bad_key in (-(1 << 31) - 1, 1 << 31, 1.5, True):
            with self.assertRaisesRegex(ValueError, "signed 32-bit"):
                MOD.lookup_key(b"", bad_key)
        with self.assertRaisesRegex(ValueError, "unsupported DAT"):
            MOD.lookup_key(b"", 17, "utf16")

    def test_direct_duplicate_keys_and_bad_offsets_cannot_prove_absence(self):
        asset = indexed_asset([(5, dat_string(b"A"), None),
                               (9, dat_string(b"B"), None)],
                              self.frequency, self.codes)
        duplicate = bytearray(asset)
        struct.pack_into("<i", duplicate, 1033, 5)
        with self.assertRaisesRegex(ValueError, "duplicate CDS key"):
            MOD.lookup_key(bytes(duplicate), 100)
        wrong_offset = bytearray(asset)
        wrong_offset[1037] = 0
        with self.assertRaisesRegex(ValueError, "index offset"):
            MOD.lookup_key(bytes(wrong_offset), 100)

    def test_key_and_contains_cli_are_mutually_exclusive(self):
        import contextlib
        import io
        import sys
        from unittest.mock import patch
        argv = ["prog", "--archive", "a", "--entry-index", "0",
                "--metadata-sha256", "0" * 64, "--content-id", "0" * 16,
                "--expected-host", "LEGION", "--key", "17",
                "--contains", "needle"]
        error = io.StringIO()
        with patch.object(sys, "argv", argv), contextlib.redirect_stderr(error):
            with self.assertRaises(SystemExit) as exit_status:
                MOD.main()
        self.assertEqual(exit_status.exception.code, 2)
        self.assertIn("not allowed with argument", error.getvalue())


if __name__ == "__main__":
    unittest.main(verbosity=2)
