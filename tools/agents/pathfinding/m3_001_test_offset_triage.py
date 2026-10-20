"""Synthetic regression tests for bounded archived disassembly triage.

Tests static parsing and integrity, not native queue registration or game use.
"""
from __future__ import annotations
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))
from m3_001_offset_triage import (
    BUILD_SHA, _verify_artifact, classify_assembly, collect
)


class OffsetTriageTests(unittest.TestCase):
    def assert_access(self, asm: str, offset: str, klass: str, zero: bool = False):
        v = classify_assembly(asm)
        self.assertEqual(len(v), 1, asm)
        self.assertEqual(v[0]["offsetLabel"], offset)
        self.assertEqual(v[0]["accessClass"], klass)
        self.assertIs(v[0]["nullOrZeroWrite"], zero)

    def test_exact_word_memory_write_is_not_a_handler_proof(self):
        self.assert_access("mov qword ptr [rcx + 0x210], r15", "0x210", "write")

    def test_explicit_immediate_zero_store(self):
        self.assert_access("mov qword ptr [rcx + 0x210], 0", "0x210", "write", True)

    def test_register_value_cannot_be_assumed_zero(self):
        self.assert_access("mov qword ptr [rcx + 0x160], r15", "0x160", "write", False)

    def test_load_of_simulation_queue_is_read(self):
        self.assert_access("mov rcx, qword ptr [rsi + 0x160]", "0x160", "read")

    def test_scalar_hkp_world_state_field_write(self):
        self.assert_access("mov dword ptr [rdi + 0x160], ecx", "0x160", "write")

    def test_compare_is_read_not_write(self):
        self.assert_access("cmp qword ptr [rcx + 0x160], r12", "0x160", "read")

    def test_memory_arithmetic_is_read_modify_write(self):
        self.assert_access("add qword ptr [rdx + 0x210], 1", "0x210", "read-modify-write")

    def test_lea_is_only_address_taken(self):
        self.assert_access("lea rax, [rcx + 0x210]", "0x210", "address-only")

    def test_stack_offset_is_not_a_queue_identity(self):
        self.assert_access("movss dword ptr [rsp + 0x160], xmm0", "0x160", "write")

    def test_unrelated_immediate_is_excluded(self):
        self.assertEqual(classify_assembly("mov eax, 0x210"), [])
        self.assertEqual(classify_assembly("mov rcx, 0x160"), [])
        self.assertEqual(classify_assembly("call 0x1400210"), [])

    def test_nonmatching_and_negative_displacements_excluded(self):
        self.assertEqual(classify_assembly("mov rax, [rcx + 0x1600]"), [])
        self.assertEqual(classify_assembly("mov rax, [rbp - 0x160]"), [])
        self.assertEqual(classify_assembly("lea rax, [rsp + 0x2100]"), [])

    def test_wrong_build_identity_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "SHA mismatch"):
            _verify_artifact({"schemaVersion":1,"sha256":"a"*64}, "synthetic.json")

    def test_wrong_schema_and_unsafe_execution_flags_rejected(self):
        with self.assertRaisesRegex(ValueError, "schema"):
            _verify_artifact({"schemaVersion":99,"sha256":BUILD_SHA}, "synthetic.json")
        with self.assertRaisesRegex(ValueError, "Unsafe"):
            _verify_artifact({"schemaVersion":1,"sha256":BUILD_SHA,
                              "gameInputSent":True}, "synthetic.json")

    def test_only_expected_eleven_archived_sources_are_scanned(self):
        result = collect()
        self.assertEqual(result["sourceFileCount"], 11)
        self.assertEqual(len(result["sourceFiles"]), 11)
        self.assertEqual(len({x["path"] for x in result["sourceFiles"]}), 11)
        self.assertTrue(all(len(x["rawSha256"])==64 for x in result["sourceFiles"]))
        self.assertEqual(result["buildSha256"], BUILD_SHA)
        self.assertFalse(result["type7Proven"])
        self.assertFalse(result["nonzeroSimulationQueuePointerWriterProven"])

    def test_exact_saved_evidence_keeps_provenance_and_no_overclaims(self):
        result = collect()
        candidates = result["candidateRecords"]
        def match(site: str, offset: str):
            return [c for c in candidates
                    if c["rva"]==site and c["offsetLabel"]==offset]
        world_queue_like = match("0x7a384", "0x210")
        world_state = match("0x7af8d", "0x160")
        self.assertEqual(len(world_queue_like), 1)
        self.assertEqual(world_queue_like[0]["accessClass"], "write")
        self.assertEqual(len(world_state), 1)
        self.assertEqual(world_state[0]["accessClass"], "write")
        self.assertFalse(world_queue_like[0]["qualifiedSameQueueOwner"])
        self.assertEqual(result["byOffset"]["0x210"], 3)
        self.assertEqual(result["byOffset"]["0x160"], 9)
        self.assertFalse(result["gameInputSent"])

    def test_repeated_archive_reports_are_deduplicated(self):
        result = collect()
        keys = [(r["rva"],r["offsetLabel"]) for r in result["candidateRecords"]]
        self.assertEqual(len(keys),len(set(keys)))

    def test_deterministic_json_and_no_new_artifacts(self):
        output1 = json.dumps(collect(),sort_keys=True,separators=(",",":"))
        output2 = json.dumps(collect(),sort_keys=True,separators=(",",":"))
        self.assertEqual(output1,output2)

    def test_missing_archive_is_not_silently_skipped(self):
        with tempfile.TemporaryDirectory() as temp:
            with self.assertRaises(FileNotFoundError):
                collect(Path(temp),("_query1.json",))


if __name__ == "__main__":
    unittest.main()
