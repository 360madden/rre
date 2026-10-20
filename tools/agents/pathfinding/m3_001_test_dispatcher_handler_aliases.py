"""Read-only pinned-source regression tests for native job-type dispatch indexing.

These qualify static original code/RTTI only. They do not exercise Rift.
"""
from __future__ import annotations

import hashlib
from pathlib import Path
import tempfile
import unittest

from m3_001_verify_dispatcher_handler_aliases import BUILD_SHA, SOURCE, verify


class TypedDispatcherAliasTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = verify()

    def test_static_source_identity(self):
        self.assertEqual(self.result["status"], "PASS")
        self.assertEqual(self.result["buildSha256"], BUILD_SHA)
        self.assertEqual(hashlib.sha256(SOURCE.read_bytes()).hexdigest(), BUILD_SHA)

    def test_type_byte_and_stride_exactly_32(self):
        record = self.result["queueDispatch"]
        self.assertEqual(record["typeByteReadRva"], "0xf4184")
        self.assertEqual(record["typeIndexShiftRva"], "0xf4194")
        self.assertEqual(record["typeTableSlotBytes"], 32)
        self.assertEqual(record["typeTableBaseDisplacement"], "0x130")
        self.assertEqual(int("0x130", 16) + 7 * 32, int(record["computedType7SlotDisplacement"], 16))

    def test_subtype_callback_index_is_distinct_from_type(self):
        record = self.result["queueDispatch"]
        self.assertEqual(record["subtypeByteReadRva"], "0xf4189")
        self.assertEqual(record["subtypeCallbackCallRva"], "0xf41a3")
        self.assertEqual(self.result["verifiedInstructions"]["0xf41a3"]["asm"],
                         "call qword ptr [rax + r8*8]")

    def test_exact_handler_source_bytes(self):
        checks = {
            "0xf3fbe": "488bf9",
            "0xf4184": "0fb64c2421",
            "0xf4189": "440fb6442420",
            "0xf4194": "48c1e105",
            "0xf4198": "488b843930010000",
            "0xf41a3": "42ff14c0",
        }
        for rva, expected in checks.items():
            with self.subTest(rva=rva):
                self.assertEqual(self.result["verifiedInstructions"][rva]["bytes"], expected)

    def test_motion_pointer_is_rtti_qualified_not_job_handler(self):
        candidate = next(x for x in self.result["rejectedOrUnqualifiedCandidates"]
                         if x["rva"] == "0x76363")
        self.assertEqual(candidate["classification"], "disproved-as-job-type1-handler")
        self.assertEqual(candidate["rtti"]["className"], ".?AVhkpMaxSizeMotion@@")
        self.assertEqual(candidate["rtti"]["vtableRva"], "0x2723418")
        self.assertEqual(candidate["rtti"]["locatorRva"], "0x2d745c8")
        self.assertTrue(candidate["rtti"]["selfRvaValid"])

    def test_other_130_writes_not_overqualified(self):
        candidates = {x["rva"]: x for x in self.result["rejectedOrUnqualifiedCandidates"]}
        self.assertEqual(candidates["0x268ab"]["classification"], "unqualified-local-structure-copy")
        self.assertEqual(candidates["0x40179"]["classification"], "unqualified-foreign-global-object")
        self.assertEqual(self.result["verifiedInstructions"]["0x40179"]["asm"],
                         "mov qword ptr [rax + 0x130], rbx")

    def test_complete_pe_unwind_windows(self):
        windows = self.result["qualifiedInstructionWindows"]
        self.assertEqual(len(windows), 4)
        self.assertTrue(all(w["completeFromPeUnwindStart"] for w in windows))
        self.assertTrue(all(w["instructionCount"] > 0 for w in windows))

    def test_no_claim_of_registered_type_seven(self):
        self.assertFalse(self.result["queueDispatch"]["registeredCallbackForType7Proven"])
        self.assertFalse(self.result["queueDispatch"]["typedJobProducerProven"])
        self.assertFalse(self.result["type7Operational"])

    def test_nonactuating_source_and_no_game_process(self):
        self.assertFalse(self.result["liveProcessAttached"])
        self.assertFalse(self.result["gameInputSent"])
        self.assertFalse(self.result["binaryModified"])

    def test_invalid_binary_fails_before_decoding(self):
        with tempfile.TemporaryDirectory() as temp:
            bad = Path(temp) / "fake-rift.exe"
            bad.write_bytes(b"synthetic not-actual-rift-binary")
            with self.assertRaisesRegex(ValueError, "hash mismatch"):
                verify(bad)

    def test_semantically_identical_repeat(self):
        self.assertEqual(verify(), self.result)


if __name__ == "__main__":
    unittest.main()
