"""Synthetic bounded TWAD metadata locator regressions (no RIFT payloads)."""
import importlib.util
import struct
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

SPEC = importlib.util.spec_from_file_location("twad_lookup", Path(__file__).with_name("lookup-twad-id.py"))
MOD = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MOD)
TARGET = bytes.fromhex("bbeea48a7564ed10")


def synthetic_segment(target=TARGET, version=1, magic=b"TWAD", count=2,
                      payload_offset=None, table_offset=20):
    table_size = count * 44
    payload_offset = payload_offset if payload_offset is not None else table_offset + table_size
    head = struct.pack("<4sIIII", magic, version, table_offset, count, 0)
    rows = bytearray(table_size)
    rows[:44] = struct.pack("<8sIIIHH20s", target, payload_offset, 16, 0, 0, 0, b"x" * 20)
    return head + b"\x00" * (table_offset - 20) + bytes(rows) + b"z" * 16


class TwadLookupChecks(unittest.TestCase):
    def test_valid_unique_match(self):
        with tempfile.TemporaryDirectory() as base:
            p = Path(base) / "assets.001"
            p.write_bytes(synthetic_segment())
            result = MOD.inspect(Path(base), TARGET)
            self.assertTrue(result["uniqueIdPrefixCandidate"])
            self.assertEqual(result["matches"][0]["entryIndex"], 0)
            self.assertEqual(result["matches"][0]["compressionFlag"], 0)
            self.assertEqual(result["matches"][0]["recordedEntrySha1"], (b"x" * 20).hex())
            self.assertIn("not proven linked/active", result["proofCeiling"])

    def test_matching_slot_does_not_prove_linked_membership(self):
        with tempfile.TemporaryDirectory() as base:
            p = Path(base) / "assets.001"
            p.write_bytes(synthetic_segment())  # first_linked=0; no linked traversal performed.
            result = MOD.inspect(Path(base), TARGET)
            self.assertTrue(result["uniqueIdPrefixCandidate"])
            self.assertIn("not proven linked/active", result["proofCeiling"])
            self.assertEqual(result["metadataSlotsInspected"], 2)

    def test_absent_is_not_unique(self):
        with tempfile.TemporaryDirectory() as base:
            (Path(base) / "assets.001").write_bytes(synthetic_segment(b"\x01" * 8))
            self.assertFalse(MOD.inspect(Path(base), TARGET)["uniqueIdPrefixCandidate"])

    def test_duplicates_are_not_unique(self):
        with tempfile.TemporaryDirectory() as base:
            for n in ("assets.001", "assets64.001"):
                (Path(base) / n).write_bytes(synthetic_segment())
            result = MOD.inspect(Path(base), TARGET)
            self.assertEqual(len(result["matches"]), 2)
            self.assertFalse(result["uniqueIdPrefixCandidate"])

    def test_same_segment_duplicate_is_not_unique(self):
        with tempfile.TemporaryDirectory() as base:
            p = Path(base) / "assets.001"
            data = bytearray(synthetic_segment())
            data[64:108] = data[20:64]
            p.write_bytes(data)
            result = MOD.inspect(Path(base), TARGET)
            self.assertEqual(len(result["matches"]), 2)
            self.assertFalse(result["uniqueIdPrefixCandidate"])

    def test_nonmatching_name_is_ignored(self):
        with tempfile.TemporaryDirectory() as base:
            (Path(base) / "assets.tmp").write_bytes(synthetic_segment())
            (Path(base) / "assets.001").write_bytes(synthetic_segment(b"\x01" * 8))
            self.assertEqual(MOD.inspect(Path(base), TARGET)["segmentsInspected"], 1)

    def test_reject_bad_signature(self):
        with tempfile.TemporaryDirectory() as base:
            p = Path(base) / "assets.001"
            p.write_bytes(synthetic_segment(magic=b"BAD!"))
            with self.assertRaisesRegex(ValueError, "layout"):
                MOD.inspect(Path(base), TARGET)

    def test_reject_bad_bounds(self):
        with tempfile.TemporaryDirectory() as base:
            p = Path(base) / "assets.001"
            p.write_bytes(synthetic_segment(payload_offset=1000000))
            with self.assertRaisesRegex(ValueError, "outside archive"):
                MOD.inspect(Path(base), TARGET)

    def test_reject_excessive_table(self):
        with tempfile.TemporaryDirectory() as base:
            p = Path(base) / "assets.001"
            p.write_bytes(struct.pack("<4sIIII", b"TWAD", 1, 20, 999999, 0))
            with self.assertRaisesRegex(ValueError, "layout"):
                MOD.inspect(Path(base), TARGET)

    def test_reject_nonhex_id(self):
        with self.assertRaisesRegex(ValueError, "hexadecimal"):
            MOD.content_id("BAD-ID")

    def test_wrong_host_is_fail_fast(self):
        with patch.object(MOD.socket, "gethostname", return_value="LEGION"):
            with self.assertRaisesRegex(ValueError, "Host does not match"):
                MOD.inspect(Path("nonexistent"), TARGET, "AMD-DESKTOP")


if __name__ == "__main__":
    unittest.main()
