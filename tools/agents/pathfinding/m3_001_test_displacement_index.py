"""Bounded direct-RVA x64 field-index tests; source is not a live game."""
from __future__ import annotations

import pathlib
import unittest
import sys

sys.path.insert(0,str(pathlib.Path(__file__).resolve().parent))
from m3_001_displacement_index import classify, scan, BUILD_SHA, IMAGE_BASE, adjacent_zero_source_rva


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

    def test_adjacent_zero_reg_store_is_not_queued_as_nonnull_candidate(self):
        # Exact original PE and complete 0x6BA30..0x6BC69 unwind method.
        result=scan(0x6ba00,0x6bd00)
        rows=[r for r in result["records"] if r["rva"]=="0x6bb83"]
        self.assertEqual(len(rows),1)
        self.assertEqual(rows[0]["asm"],"mov qword ptr [rsi + 0x160], rdx")
        self.assertEqual(rows[0]["adjacentZeroSourceRva"],"0x6bb81")
        self.assertFalse(rows[0]["immediateZeroStore"])
        self.assertEqual(result["adjacentZeroRegisterWrites"],1)
        self.assertTrue(result["scanCompleteWithinPeUnwindMethod"])
        self.assertFalse(any(r["rva"]=="0x6bb83"
                             for r in result["potentialNonnullField160Writes"]))
        self.assertFalse(result["nonNullSimulationQueueWriterQualified"])
        self.assertFalse(result["type7HandlerQualified"])

    def test_adjacent_clear_is_conservative_and_requires_identical_source(self):
        import capstone
        md=capstone.Cs(capstone.CS_ARCH_X86,capstone.CS_MODE_64)
        md.detail=True
        source=bytes.fromhex("33d248899660010000")  # xor edx,edx; mov [rsi+160],rdx
        rows=list(md.disasm(source, IMAGE_BASE+0x2000))
        self.assertEqual(len(rows),2)
        self.assertEqual(adjacent_zero_source_rva(rows[0],rows[1],md),"0x2000")
        self.assertIsNone(adjacent_zero_source_rva(rows[0],rows[1],md,{0x2002}))
        mismatch=list(md.disasm(bytes.fromhex("33c948899660010000"),
                                IMAGE_BASE+0x2000))  # xor ecx,ecx; RDX store
        self.assertIsNone(adjacent_zero_source_rva(mismatch[0],mismatch[1],md))
        gap=list(md.disasm(bytes.fromhex("33d29048899660010000"),
                           IMAGE_BASE+0x2000))  # NOP between clear/store
        self.assertEqual(len(gap),3)
        self.assertIsNone(adjacent_zero_source_rva(gap[1],gap[2],md))

    def test_repeatable_window_output_ignoring_time(self):
        first=scan(0x70000,0xA0000)
        second=scan(0x70000,0xA0000)
        self.assertEqual(first,second)


if __name__=="__main__":
    unittest.main()
