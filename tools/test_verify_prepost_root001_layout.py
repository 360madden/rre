#!/usr/bin/env python3
"""Synthetic mutation tests for the offline cross-build ROOT001 B source gate."""
import contextlib
import io
import json
import struct
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent))
import verify_prepost_root001_layout as gate


class CrossBuildLayoutTests(unittest.TestCase):
    def setUp(self):
        self.windows = {}
        for label, spec in gate.BUILDS.items():
            windows = {}
            for _, rva, opcode in spec["opcodes"]:
                value = bytes.fromhex(opcode)
                windows[(rva, len(value))] = value
            for _, rva, target in spec["calls"]:
                windows[(rva, 5)] = b"\xE8" + struct.pack("<i", target - (rva + 5))
            _, rva, target = spec["lea"]
            windows[(rva, 7)] = b"\x48\x8d\x05" + struct.pack(
                "<i", target - (rva + 7)
            )
            for offset, pointer in spec["slots"]:
                windows[(spec["vtable"] + offset, 8)] = struct.pack("<Q", pointer)
            self.windows[label] = windows

    def verify(self):
        return gate.verify_layout(
            lambda rva, size: self.windows["old"].get((rva, size)),
            lambda rva, size: self.windows["new"].get((rva, size)),
        )

    def change(self, label, key, position=-1):
        original = self.windows[label][key]
        value = bytearray(original)
        value[position] ^= 0x01
        self.windows[label][key] = bytes(value)
        return original

    def test_matched_source_never_qualifies_runtime(self):
        result = self.verify()
        self.assertEqual(result["status"], "SOURCE_PINNED_ONLY")
        self.assertFalse(result["runtimeQualified"])
        self.assertFalse(result["functionIdentityQualified"])
        self.assertFalse(result["layoutCompatible"])
        self.assertEqual(result["old"]["allocation"], "0xA8")
        self.assertEqual(result["new"]["allocation"], "0xA0")
        self.assertEqual(result["old"]["stateFieldOffset"], "+0x20")
        self.assertEqual(result["new"]["stateFieldOffset"], "+0x18")
        self.assertEqual(result["old"]["dirtyBitMask"], "0x1")
        self.assertEqual(result["new"]["dirtyBitMask"], "0x80")
        self.assertEqual(result["oldBuildSha256"], gate.OLD_SHA256)
        self.assertEqual(result["newBuildSha256"], gate.NEW_SHA256)

    def test_all_opcode_mutations_fail_closed(self):
        for label, spec in gate.BUILDS.items():
            for name, rva, opcode in spec["opcodes"]:
                key = (rva, len(bytes.fromhex(opcode)))
                original = self.change(label, key)
                try:
                    with self.subTest(build=label, opcode=name):
                        with self.assertRaises(gate.GateError):
                            self.verify()
                finally:
                    self.windows[label][key] = original

    def test_call_targets_and_opcode_mutations_fail_closed(self):
        for label, spec in gate.BUILDS.items():
            for name, rva, _ in spec["calls"]:
                key = (rva, 5)
                for position in (0, 1):  # CALL opcode and rel32 operand
                    original = self.change(label, key, position)
                    try:
                        with self.subTest(build=label, call=name, byte=position):
                            with self.assertRaises(gate.GateError):
                                self.verify()
                    finally:
                        self.windows[label][key] = original

    def test_vtable_lea_prefix_and_target_mutations_fail(self):
        for label, spec in gate.BUILDS.items():
            _, rva, _ = spec["lea"]
            key = (rva, 7)
            for position in (0, 3):  # LEA opcode and RIP-relative displacement
                original = self.change(label, key, position)
                try:
                    with self.subTest(build=label, lea_byte=position):
                        with self.assertRaises(gate.GateError):
                            self.verify()
                finally:
                    self.windows[label][key] = original

    def test_all_vtable_slot_mutations_fail(self):
        for label, spec in gate.BUILDS.items():
            for offset, _ in spec["slots"]:
                key = (spec["vtable"] + offset, 8)
                original = self.change(label, key)
                try:
                    with self.subTest(build=label, slot=hex(offset)):
                        with self.assertRaises(gate.GateError):
                            self.verify()
                finally:
                    self.windows[label][key] = original

    def test_unmapped_window_fails(self):
        for label, spec in gate.BUILDS.items():
            _, rva, opcode = spec["opcodes"][0]
            key = (rva, len(bytes.fromhex(opcode)))
            original = self.windows[label].pop(key)
            try:
                with self.subTest(build=label), self.assertRaises(gate.GateError):
                    self.verify()
            finally:
                self.windows[label][key] = original

    def test_swapped_old_new_reader_fails(self):
        with self.assertRaises(gate.GateError):
            gate.verify_layout(
                lambda rva, n: self.windows["new"].get((rva, n)),
                lambda rva, n: self.windows["old"].get((rva, n)),
            )

    def test_wrong_sha_fails_before_pe_inspection(self):
        path = Path("synthetic_archive.exe")
        for label in gate.BUILDS:
            with self.subTest(build=label), \
                    patch.object(gate, "stamp", return_value=(gate.BUILDS[label]["bytes"], 0)), \
                    patch.object(gate, "sha_range", return_value="0" * 64), \
                    patch.object(gate, "inspect_pe") as inspect:
                with self.assertRaisesRegex(gate.GateError, "SHA-256"):
                    gate.checked_archive(path, label)
                inspect.assert_not_called()

    def test_invalid_archive_size_cli_fails_closed(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "tiny.exe"
            path.write_bytes(b"MZ")
            output = io.StringIO()
            with contextlib.redirect_stderr(output):
                code = gate.main(["--old-pe", str(path), "--new-pe", str(path)])
            self.assertEqual(code, 3)
            report = json.loads(output.getvalue())
            self.assertEqual(report["status"], "ERROR")
            self.assertFalse(report["runtimeQualified"])
            self.assertFalse(report["functionIdentityQualified"])

    def test_actual_archives_if_present(self):
        paths = {
            label: gate.ARCHIVE_ROOT / spec["sha256"] / "rift_x64.exe"
            for label, spec in gate.BUILDS.items()
        }
        if not all(path.is_file() for path in paths.values()):
            self.skipTest("Local old/new RIFT archives not available; synthetic checks still run")
        old_before, old_read = gate.checked_archive(paths["old"], "old")
        new_before, new_read = gate.checked_archive(paths["new"], "new")
        result = gate.verify_layout(old_read, new_read)
        self.assertEqual(result["status"], "SOURCE_PINNED_ONLY")
        for label, before in (("old", old_before), ("new", new_before)):
            self.assertEqual(gate.stamp(paths[label]), before)


if __name__ == "__main__":
    unittest.main()
