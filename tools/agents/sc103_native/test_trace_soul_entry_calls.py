"""Focused standalone checks for SC-103 direct-relative-call detection."""
import importlib.util
import struct
import unittest
from pathlib import Path

SOURCE = Path(__file__).with_name("trace_soul_entry_calls.py")
spec = importlib.util.spec_from_file_location("sc103_trace", SOURCE)
module = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(module)


class DirectCallTests(unittest.TestCase):
    def test_positive_signed_backward_call(self):
        base, target = 0x1000, 0x900
        section = bytes((0x90, 0xE8)) + struct.pack("<i", target - (base + 6))
        self.assertEqual(module.rel32_calls(section, base, target), [base + 1])

    def test_no_false_match_to_neighbor(self):
        base, target = 0x1000, 0x900
        section = bytes((0x90, 0xE8)) + struct.pack("<i", target - (base + 6))
        self.assertEqual(module.rel32_calls(section, base, target + 1), [])

    def test_truncated_tail_does_not_overread(self):
        self.assertEqual(module.rel32_calls(bytes((0x90, 0xE8, 0x10)), 0x1000, 0x1016), [])

    def test_multiple_candidate_offsets_are_retained(self):
        base, target = 0x1000, 0x1800
        a = bytes((0xE8,)) + struct.pack("<i", target - (base + 5))
        b = bytes((0xE8,)) + struct.pack("<i", target - (base + 10))
        self.assertEqual(module.rel32_calls(a + b, base, target), [base, base + 5])

    def test_method_table_slot_reads_expected_pointer(self):
        table = bytes(0x60) + struct.pack("<Q", 0x140EAB4D0)
        self.assertEqual(module.method_pointer_at(table, 0x60), 0x140EAB4D0)

    def test_method_table_truncated_or_misaligned_fails_closed(self):
        table = bytes(0x60) + struct.pack("<Q", 0x140EAB4D0)
        for invalid_slot in (-8, 1, 0x68):
            with self.assertRaisesRegex(ValueError, "invalid or truncated"):
                module.method_pointer_at(table, invalid_slot)

    def test_pdata_sole_owner(self):
        pdata = struct.pack("<III", 0x1000, 0x1100, 0) + struct.pack("<III", 0x1100, 0x1200, 0)
        self.assertEqual(module.owner_range(pdata, 0x1100), (0x1100, 0x1200))

    def test_pdata_missing_owner_rejected(self):
        with self.assertRaisesRegex(ValueError, "expected one"):
            module.owner_range(struct.pack("<III", 0x1000, 0x1100, 0), 0x1200)

    def test_pdata_ambiguous_owner_rejected(self):
        pdata = struct.pack("<III", 0x1000, 0x1100, 0) * 2
        with self.assertRaisesRegex(ValueError, "expected one"):
            module.owner_range(pdata, 0x1001)


if __name__ == "__main__":
    unittest.main()
