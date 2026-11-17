#!/usr/bin/env python3
"""No-game-process mutation tests for the SHA-pinned postpatch ROOT001 B source gate."""
import contextlib
import hashlib
import io
import json
import struct
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent))
import verify_postpatch_root001_b as gate
from rift_update_analyzer import bytes_at_rva, inspect_pe


class SourceGateTests(unittest.TestCase):
    def setUp(self):
        self.vptr = bytearray(56)
        struct.pack_into("<Q", self.vptr, 0x18, 0x140000000 + gate.EXPECTED_B_ENTRY)
        self.prefix = bytes([0x90]) * (gate.PREFIX_END_RVA - gate.EXPECTED_B_ENTRY)
        self.windows = {
            (rva, len(bytes.fromhex(opcode))): bytes.fromhex(opcode)
            for _, rva, opcode in gate.OPCODES + gate.STATE_DELTA_OPCODES
        }
        self.windows[(gate.VTABLE_RVA, 56)] = bytes(self.vptr)
        self.windows[(gate.EXPECTED_B_ENTRY, len(self.prefix))] = self.prefix
        self.windows[(0xFCA480, 5)] = bytes.fromhex("e87be67bff")
        self.windows[(0xFC918A, 7)] = bytes.fromhex("488d0587837501")
        self.windows[(0xFC9199, 3)] = bytes.fromhex("488903")
        self.windows[(0xFC939F, 7)] = bytes.fromhex("488d0572817501")
        self.windows[(0xFC93A9, 3)] = bytes.fromhex("488901")

    def verify(self):
        with patch.object(gate, "EXPECTED_VPTR_SHA", hashlib.sha256(self.windows[(gate.VTABLE_RVA, 56)]).hexdigest()), \
             patch.object(gate, "EXPECTED_B_PREFIX_SHA", hashlib.sha256(
                 self.prefix).hexdigest()):
            return gate.verify_source(lambda rva, length: self.windows.get((rva, length)))

    def test_valid_fixture_never_claims_runtime(self):
        report = self.verify()
        self.assertEqual(report["status"], "SOURCE_PINNED_ONLY")
        self.assertFalse(report["runtimeQualified"])
        self.assertFalse(report["functionIdentityQualified"])
        self.assertEqual(report["checkedStateDeltaOpcodes"], 6)

    def test_all_opcode_mutations_fail(self):
        for _, rva, opcode in gate.OPCODES:
            key = (rva, len(bytes.fromhex(opcode)))
            original = self.windows[key]
            self.windows[key] = bytes([original[0] ^ 1]) + original[1:]
            with self.subTest(rva=hex(rva)), self.assertRaises(gate.GateError):
                self.verify()
            self.windows[key] = original

    def test_all_state_delta_opcode_mutations_fail(self):
        for _, rva, opcode in gate.STATE_DELTA_OPCODES:
            key = (rva, len(bytes.fromhex(opcode)))
            original = self.windows[key]
            # The mutated bytes are in the operand/flag (not only the opcode).
            self.windows[key] = original[:-1] + bytes([original[-1] ^ 1])
            with self.subTest(rva=hex(rva)), self.assertRaises(gate.GateError):
                self.verify()
            self.windows[key] = original

    def test_missing_opcode_fails(self):
        self.windows.pop(next(iter(self.windows)))
        with self.assertRaises(gate.GateError):
            self.verify()

    def test_invalid_vptr_target_fails_even_with_matching_fixture_hash(self):
        bad = bytearray(self.vptr)
        struct.pack_into("<Q", bad, 0x18, 0x140000000 + gate.EXPECTED_B_ENTRY + 16)
        self.windows[(gate.VTABLE_RVA, 56)] = bytes(bad)
        with self.assertRaisesRegex(gate.GateError, "slot"):
            self.verify()

    def test_vptr_sha_change_rejected(self):
        self.windows[(gate.VTABLE_RVA, 56)] = bytes([0xFF]) * 56
        # Pin the real expected source hash, not our altered synthetic fixture hash.
        with patch.object(gate, "EXPECTED_B_PREFIX_SHA", hashlib.sha256(self.prefix).hexdigest()):
            with self.assertRaisesRegex(gate.GateError, "vtable source-window"):
                gate.verify_source(lambda rva, length: self.windows.get((rva, length)))

    def test_vptr_assignment_lea_target_shift_rejected(self):
        for rva in (0xFC918A, 0xFC939F):
            key = (rva, 7)
            original = self.windows[key]
            self.windows[key] = original[:-1] + bytes([original[-1] ^ 1])
            with self.subTest(rva=hex(rva)), self.assertRaisesRegex(gate.GateError, "LEA targets"):
                self.verify()
            self.windows[key] = original

    def test_vptr_assignment_store_mutation_rejected(self):
        for rva in (0xFC9199, 0xFC93A9):
            key = (rva, 3)
            original = self.windows[key]
            self.windows[key] = bytes([original[0] ^ 1]) + original[1:]
            with self.subTest(rva=hex(rva)), self.assertRaisesRegex(gate.GateError, "vptr store"):
                self.verify()
            self.windows[key] = original

    def test_call_target_shift_rejected(self):
        self.windows[(0xFCA480, 5)] = bytes.fromhex("e87ce67bff")
        with self.assertRaisesRegex(gate.GateError, "target"):
            self.verify()

    def test_prefix_hash_change_rejected(self):
        self.windows[(gate.EXPECTED_B_ENTRY, len(self.prefix))] = b"X" * len(self.prefix)
        with self.assertRaisesRegex(gate.GateError, "source-prefix"):
            self.verify()

    def test_wrong_file_size_exit3(self):
        with tempfile.TemporaryDirectory() as temp:
            bad = Path(temp) / "wrong.exe"
            bad.write_bytes(b"not a real RIFT binary")
            with contextlib.redirect_stderr(io.StringIO()):
                self.assertEqual(gate.main(["--pe", str(bad)]), 3)

    def test_invalid_cli_returns_structured_error_exit3(self):
        output = io.StringIO()
        with contextlib.redirect_stderr(output), self.assertRaises(SystemExit) as caught:
            gate.main(["--bogus"])
        self.assertEqual(caught.exception.code, 3)
        self.assertEqual(json.loads(output.getvalue())["status"], "ERROR")

    @unittest.skipUnless(gate.DEFAULT_PE.is_file(), "Archived physical RIFT baseline absent")
    def test_real_archived_build_is_source_only(self):
        path = gate.DEFAULT_PE
        pe = inspect_pe(path, path.stat().st_size)
        report = gate.verify_source(lambda rva, n: bytes_at_rva(path, pe, rva, n))
        self.assertFalse(report["runtimeQualified"])


if __name__ == "__main__":
    unittest.main()
