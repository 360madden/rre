#!/usr/bin/env python3
"""Synthetic negative checks + optional real archived PE for postpatch WA-006 source gate."""
import contextlib
import copy
import hashlib
import io
import json
import struct
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import verify_postpatch_wa006 as gate
from rift_update_analyzer import bytes_at_rva, inspect_pe


class PostpatchWa006Tests(unittest.TestCase):
    def setUp(self):
        self.manifest = json.loads(gate.DEFAULT_MANIFEST.read_text(encoding="utf-8"))
        self.windows = {}
        for i, window in enumerate(self.manifest["windows"]):
            rva = gate.parse_rva(window["rva"])
            n = window["length"]
            sample = (bytes([i + 1]) * n)
            self.windows[(rva, n)] = sample
            window["sha256"] = hashlib.sha256(sample).hexdigest()
        for call in self.manifest["directCalls"]:
            rva = gate.parse_rva(call["callRva"])
            target = gate.parse_rva(call["targetRva"])
            self.windows[(rva, 5)] = b"\xe8" + struct.pack("<i", target - (rva + 5))
        self.windows[(gate.DERIVED_VTABLE_LEA_RVA, 7)] = bytes.fromhex("488d0533187a01")
        self.windows[(gate.DERIVED_VPTR_STORE_RVA, 3)] = bytes.fromhex("488903")
        for slot in gate.DERIVED_METHOD_SLOTS:
            self.windows[(gate.DERIVED_VTABLE_RVA + slot, 8)] = struct.pack(
                "<Q", 0x140000000 + gate.DERIVED_METHOD_RVA)
        self.windows[(gate.DERIVED_METHOD_RVA, len(gate.DERIVED_METHOD_BYTES))] = gate.DERIVED_METHOD_BYTES

    def check(self):
        return gate.verify_source(lambda rva, n: self.windows.get((rva, n)), self.manifest)

    def test_valid_synthetic_evidence_is_static_only(self):
        result = self.check()
        self.assertEqual((result["sourceWindowsChecked"], result["directCallsChecked"]), (7, 7))
        self.assertFalse(result["ownerQualified"])
        self.assertFalse(result["runtimeQualified"])
        self.assertEqual(result["derivedVtableSlotsChecked"], 3)
        self.assertTrue(result["derivedField8SentinelStoreSourcePinned"])

    def test_all_window_mutations_rejected(self):
        for entry in self.manifest["windows"]:
            key = (gate.parse_rva(entry["rva"]), entry["length"])
            original = self.windows[key]
            self.windows[key] = bytes([original[0] ^ 1]) + original[1:]
            with self.subTest(id=entry["id"]), self.assertRaisesRegex(gate.GateError, "Source window"):
                self.check()
            self.windows[key] = original

    def test_all_call_target_mutations_rejected(self):
        for edge in self.manifest["directCalls"]:
            key = (gate.parse_rva(edge["callRva"]), 5)
            original = self.windows[key]
            self.windows[key] = original[:1] + bytes([original[1] ^ 1]) + original[2:]
            with self.subTest(id=edge["id"]), self.assertRaisesRegex(gate.GateError, "target"):
                self.check()
            self.windows[key] = original

    def test_all_noncall_opcode_mutations_rejected(self):
        for edge in self.manifest["directCalls"]:
            key = (gate.parse_rva(edge["callRva"]), 5)
            original = self.windows[key]
            self.windows[key] = b"\x90" + original[1:]
            with self.subTest(id=edge["id"]), self.assertRaisesRegex(gate.GateError, "opcode"):
                self.check()
            self.windows[key] = original

    def test_derived_wrapper_constructor_and_slots_mutations_fail(self):
        for key in [(gate.DERIVED_VTABLE_LEA_RVA, 7), (gate.DERIVED_VPTR_STORE_RVA, 3)] + [
            (gate.DERIVED_VTABLE_RVA + slot, 8) for slot in gate.DERIVED_METHOD_SLOTS
        ]:
            original = self.windows[key]
            self.windows[key] = original[:-1] + bytes([original[-1] ^ 1])
            try:
                with self.subTest(key=hex(key[0])), self.assertRaises(gate.GateError):
                    self.check()
            finally:
                self.windows[key] = original

    def test_derived_virtual_setter_nonzero_field8_mutation_fails(self):
        key = (gate.DERIVED_METHOD_RVA, len(gate.DERIVED_METHOD_BYTES))
        original = self.windows[key]
        self.windows[key] = original[:-2] + bytes([original[-2] ^ 1]) + original[-1:]
        with self.assertRaisesRegex(gate.GateError, "virtual source setter"):
            self.check()

    def test_missing_window_fails(self):
        entry = self.manifest["windows"][0]
        self.windows.pop((gate.parse_rva(entry["rva"]), entry["length"]))
        with self.assertRaisesRegex(gate.GateError, "Source window"):
            self.check()

    def test_manifest_scope_mutation_fails(self):
        for key in ("runtimeQualified", "ownerQualified"):
            manifest = copy.deepcopy(self.manifest)
            manifest[key] = True
            with self.subTest(key=key), self.assertRaisesRegex(gate.GateError, "scope"):
                gate.verify_source(lambda rva, n: self.windows.get((rva, n)), manifest)

    def test_missing_call_record_fails(self):
        self.manifest["directCalls"].pop()
        with self.assertRaisesRegex(gate.GateError, "Call IDs"):
            self.check()

    def test_malformed_root_rejected(self):
        with self.assertRaisesRegex(gate.GateError, "Manifest root"):
            gate.verify_source(lambda rva, n: b"", ["not-a-record"])

    def test_malformed_window_and_call_rejected(self):
        for name in ("windows", "directCalls"):
            manifest = copy.deepcopy(self.manifest)
            manifest[name][0] = "not-a-record"
            with self.subTest(name=name), self.assertRaisesRegex(gate.GateError, "object arrays"):
                gate.verify_source(lambda rva, n: self.windows.get((rva, n)), manifest)

    def test_invalid_rva_fails(self):
        self.manifest["windows"][0]["rva"] = "-1"
        with self.assertRaisesRegex(gate.GateError, "RVA"):
            self.check()

    def test_wrong_file_rejected(self):
        with tempfile.TemporaryDirectory() as temp, contextlib.redirect_stderr(io.StringIO()):
            path = Path(temp) / "wrong.exe"
            path.write_bytes(b"invalid")
            self.assertEqual(gate.main(["--pe", str(path)]), 3)

    def test_invalid_flag_structured_error_exit3(self):
        output = io.StringIO()
        with contextlib.redirect_stderr(output), self.assertRaises(SystemExit) as caught:
            gate.main(["--unsupported"])
        self.assertEqual(caught.exception.code, 3)
        self.assertEqual(json.loads(output.getvalue())["status"], "ERROR")

    @unittest.skipUnless(gate.DEFAULT_PE.is_file(), "Updated archived PE absent")
    def test_real_build_source_windows_and_calls(self):
        path = gate.DEFAULT_PE
        pe = inspect_pe(path, path.stat().st_size)
        manifest = json.loads(gate.DEFAULT_MANIFEST.read_text(encoding="utf-8"))
        result = gate.verify_source(lambda rva, n: bytes_at_rva(path, pe, rva, n), manifest)
        self.assertEqual(result["status"], "SOURCE_MAP_PINNED_ONLY")


if __name__ == "__main__":
    unittest.main()
