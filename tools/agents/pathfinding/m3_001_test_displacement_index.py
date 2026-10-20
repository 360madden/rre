"""Bounded direct-RVA x64 field-index tests; source is not a live game."""
from __future__ import annotations

import pathlib
import unittest
import sys

sys.path.insert(0,str(pathlib.Path(__file__).resolve().parent))
from m3_001_displacement_index import classify, scan, BUILD_SHA


class DisplacementIndexTests(unittest.TestCase):
    def test_intel_qword_mov_destination_is_write(self):
        self.assertEqual(classify("mov",0,False),("write",False))

    def test_register_to_memory_immediate_zero(self):
        self.assertEqual(classify("mov",0,True),("write",True))

    def test_memory_source_is_read(self):
        self.assertEqual(classify("mov",1,False),("read",False))

    def test_cmp_memory_first_is_read_only(self):
        self.assertEqual(classify("cmp",0,False),("read",False))

    def test_and_memory_is_rmw_and_zero_can_null_field(self):
        self.assertEqual(classify("and",0,True),("read-modify-write",True))
        self.assertEqual(classify("and",0,False),("read-modify-write",False))

    def test_lea_is_address_only_not_actual_read(self):
        self.assertEqual(classify("lea",1,False),("address-only",False))

    def test_unknown_operand_is_not_promoted(self):
        self.assertEqual(classify("unrecognized-op",0,False),("unknown",False))

    def test_actual_window_stores_are_not_qualified_type7(self):
        # Bounded original PE index; no dynamic game process.
        result=scan(0x70000,0xA0000)
        self.assertEqual(result["buildSha256"],BUILD_SHA)
        rows={(r["rva"],r["field"]):r for r in result["records"]}
        self.assertIn(("0x79a9f","0x210"),rows)
        self.assertIn(("0x7a384","0x210"),rows)
        self.assertIn(("0x89bd7","0x160"),rows)
        self.assertEqual(rows[("0x79a9f","0x210")]["accessClass"],"write")
        self.assertEqual(rows[("0x7a384","0x210")]["accessClass"],"write")
        self.assertTrue(rows[("0x89bd7","0x160")]["immediateZeroStore"])
        self.assertFalse(result["type7HandlerQualified"])
        self.assertFalse(result["nonNullSimulationQueueWriterQualified"])
        self.assertFalse(result["gameInputSent"])
        self.assertFalse(result["gameProcessAttached"])

    def test_window_must_be_in_text(self):
        with self.assertRaisesRegex(ValueError, "within .text"):
            scan(0,0x100)

    def test_rbp_proven_frame_alias_is_not_heap_writer(self):
        result = scan(0x890000,0x894000)
        rows = [r for r in result["records"]
                if r["rva"]=="0x892c41" and r["field"]=="0x160"]
        self.assertEqual(len(rows),1)
        row=rows[0]
        self.assertEqual(row["baseRegister"],"rbp")
        self.assertTrue(row["stackBaseQualified"])
        self.assertEqual(row["stackBaseProvenance"],
                         "RBP-derived-from-RSP-in-current-unwind-range")
        self.assertFalse(any(r["rva"]=="0x892c41"
                             for r in result["potentialNonnullField160Writes"]))

    def test_different_rva_bands_not_same_simulation_owner(self):
        # 0x089BD7 (simulation field zero) and 0x89C605 (factory buffer
        # allocation) have similar digit strings, but are 8+ MiB apart.
        self.assertLess(0x89bd7,0x89a000)
        self.assertGreater(0x89c605,0x800000)
        result = scan(0x89a000,0x89d000)
        self.assertFalse(any(r["rva"]=="0x89bd7" for r in result["records"]))
        rows = [r for r in result["records"]
                if r["field"]=="0x160" and
                r["rva"] in ("0x89c605","0x89ca2a")]
        self.assertEqual({r["rva"] for r in rows},
                         {"0x89c605","0x89ca2a"})
        self.assertTrue(all(r["accessClass"]=="write" and
                            not r["stackBaseQualified"] for r in rows))
        self.assertFalse(result["type7HandlerQualified"])
        self.assertFalse(result["nonNullSimulationQueueWriterQualified"])

    def test_repeatable_window_output_ignoring_time(self):
        first=scan(0x70000,0xA0000)
        second=scan(0x70000,0xA0000)
        self.assertEqual(first,second)


if __name__=="__main__":
    unittest.main()
