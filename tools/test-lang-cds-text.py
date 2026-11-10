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


if __name__ == "__main__":
    unittest.main(verbosity=2)
