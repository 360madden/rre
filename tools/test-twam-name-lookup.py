"""Offline synthetic regression checks for the bounded TWAM v3 name lookup."""
import importlib.util
import struct
import unittest
from pathlib import Path

SCRIPT = Path(__file__).with_name("lookup-twam-name.py")
SPEC = importlib.util.spec_from_file_location("twam_name_lookup", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def fake_manifest(filename="world_map.cdr", count=1, length_override=None):
    pak_string = b"assets/map/test.pak\x00"
    t0_offset, t0_size = 64, 53 + len(pak_string)
    t1_offset = t0_offset + t0_size
    t1_size = count * 58
    t2_offset, t2_size = t1_offset + t1_size, 36
    blob = bytearray(t2_offset + t2_size)
    struct.pack_into("<4sHH", blob, 0, b"TWAM", 3, 0)
    for table_index, fields in enumerate([
        (t0_offset, t0_size, 1, 53),
        (t1_offset, t1_size, count, 58),
        (t2_offset, t2_size, 3, 12),
    ]):
        struct.pack_into("<IIII", blob, 16 + 16 * table_index, *fields)
    struct.pack_into("<I", blob, t0_offset, t0_offset + 53)
    blob[t0_offset + 53:t0_offset + t0_size] = pak_string
    _, encoded, hashed = MODULE.hash_name(filename)
    for index in range(count):
        start = t1_offset + index * 58
        blob[start:start + 8] = index.to_bytes(8, "little")
        struct.pack_into("<I", blob, start + 8, hashed)
        struct.pack_into("<H", blob, start + 24, 0)
        struct.pack_into("<H", blob, start + 56,
                         length_override if length_override is not None else len(encoded))
    return bytes(blob)


class TwamNameLookupChecks(unittest.TestCase):
    def test_known_fnv1(self):
        self.assertEqual(MODULE.hash_name("WORLD_MAP.CDR")[2], 0x98AEBEEF)
        self.assertEqual(MODULE.hash_name("ART\\UI\\TEST.DDS")[0], "art/ui/test.dds")

    def test_non_ascii_filename_rejected(self):
        with self.assertRaisesRegex(ValueError, "ASCII"):
            MODULE.hash_name("café.dds")

    def test_single_match(self):
        result = MODULE.inspect(fake_manifest(), "world_map.cdr")
        self.assertTrue(result["uniqueHashLengthCandidate"])
        self.assertEqual(result["fnv1"], "0x98AEBEEF")
        self.assertIn("not plaintext filename proof", result["proofCeiling"])
        self.assertEqual(result["matches"][0]["virtualPakName"], "assets/map/test.pak")

    def test_wrong_length_does_not_qualify(self):
        result = MODULE.inspect(fake_manifest(length_override=12), "world_map.cdr")
        self.assertEqual(result["hashMatches"], 1)
        self.assertEqual(result["lengthMatches"], 0)
        self.assertFalse(result["uniqueHashLengthCandidate"])

    def test_duplicate_hash_and_length_rejected(self):
        result = MODULE.inspect(fake_manifest(count=2), "world_map.cdr")
        self.assertEqual(result["lengthMatches"], 2)
        self.assertFalse(result["uniqueHashLengthCandidate"])

    def test_missing_filename_rejected(self):
        result = MODULE.inspect(fake_manifest(), "unlisted.cdr")
        self.assertEqual(result["hashMatches"], 0)
        self.assertFalse(result["uniqueHashLengthCandidate"])

    def test_bad_manifest_header(self):
        data = bytearray(fake_manifest())
        data[0:4] = b"NOPE"
        with self.assertRaisesRegex(ValueError, "TWAM"):
            MODULE.inspect(bytes(data), "world_map.cdr")

    def test_bad_table_range(self):
        data = bytearray(fake_manifest())
        struct.pack_into("<I", data, 16 + 16, len(data) + 1)
        with self.assertRaisesRegex(ValueError, "bounds"):
            MODULE.inspect(bytes(data), "world_map.cdr")

    def test_bad_pak_string_pointer(self):
        data = bytearray(fake_manifest())
        struct.pack_into("<I", data, 64, 1)
        with self.assertRaisesRegex(ValueError, "PAK name offset"):
            MODULE.inspect(bytes(data), "world_map.cdr")


if __name__ == "__main__":
    unittest.main()
