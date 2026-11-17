#!/usr/bin/env python3
"""Synthetic, no-RIFT-process tests for the offline update comparator."""
import hashlib
import json
import os
import struct
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).with_name("rift_update_analyzer.py")


def sample_pe(section_count=2):
    """Build a minimal valid AMD64 PE32+ with file-backed .text and .rdata."""
    data = bytearray(0x800 if section_count > 2 else 0x600)
    data[0:2] = b"MZ"
    struct.pack_into("<I", data, 0x3C, 0x80)
    data[0x80:0x84] = b"PE\0\0"
    struct.pack_into("<HHIIIHH", data, 0x84, 0x8664, section_count, 0, 0, 0, 0xF0, 0x22)
    opt = 0x98
    struct.pack_into("<H", data, opt, 0x20B)
    struct.pack_into("<I", data, opt + 56, 0x5000)
    struct.pack_into("<I", data, opt + 60, 0x200)
    base = opt + 0xF0
    for i, name in enumerate((b".text", b".rdata", b".data")[:section_count]):
        start = base + i * 40
        data[start:start + len(name)] = name
        struct.pack_into("<IIII", data, start + 8, 0x180, 0x1000 * (i + 1), 0x200, 0x200 * (i + 1))
        struct.pack_into("<I", data, start + 36, 0x60000020 if i == 0 else 0x40000040)
        data[0x200 * (i + 1):0x200 * (i + 2)] = bytes([0x90 + i]) * 0x200
    return data


class AnalyzerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        inputs = self.root / "inputs"
        inputs.mkdir()
        self.before = inputs / "old.exe"
        self.after = inputs / "new.exe"
        self.orig = sample_pe()
        self.before.write_bytes(self.orig)
        self.after.write_bytes(self.orig)
        self.sha = hashlib.sha256(self.orig).hexdigest()
        self.counter = 0

    def run_compare(self, extra=(), target=None, original=None):
        self.counter += 1
        report = self.root / "reports" / ("comparison-" + str(self.counter))
        args = [sys.executable, "-B", str(SCRIPT), "--before", str(original or self.before),
                "--after", str(target or self.after), "--expected-before-sha", self.sha,
                "--output-dir", str(report), *extra]
        result = subprocess.run(args, capture_output=True, text=True, timeout=20)
        return result, report

    def test_equal_bytes_are_match_independent_of_mtime(self):
        os.utime(self.after, ns=(1234567890123456, 1234567890123456))
        proc, report = self.run_compare()
        self.assertEqual(proc.returncode, 0, proc.stderr)
        data = json.loads((report / "report.json").read_text(encoding="utf8"))
        self.assertEqual(data["status"], "MATCH")
        self.assertTrue(all(s["status"] == "identical" for s in data["sections"]))
        self.assertTrue((report / "report.md").exists())
        self.assertTrue(data["requiresRuntimeRequalification"])

    def test_header_only_delta_still_blocks_old_offsets(self):
        changed = bytearray(self.orig)
        changed[0x98 + 64] = 1  # PE checksum header, not a mapped section
        self.after.write_bytes(changed)
        proc, report = self.run_compare()
        self.assertEqual(proc.returncode, 2, proc.stderr)
        data = json.loads((report / "report.json").read_text(encoding="utf8"))
        self.assertTrue(data["rawSectionsUnchangedButFileChanged"])
        self.assertFalse(data["nativeOffsetsQualified"])
        self.assertTrue(all(s["status"] == "identical" for s in data["sections"]))

    def test_section_write_permission_change_is_not_identical(self):
        changed = bytearray(self.orig)
        first_characteristics = 0x98 + 0xF0 + 36
        old_flags = struct.unpack_from("<I", changed, first_characteristics)[0]
        struct.pack_into("<I", changed, first_characteristics, old_flags | 0x80000000)
        self.after.write_bytes(changed)
        proc, report = self.run_compare()
        self.assertEqual(proc.returncode, 2, proc.stderr)
        data = json.loads((report / "report.json").read_text(encoding="utf8"))
        self.assertEqual(data["status"], "CHANGED")
        self.assertEqual(data["sections"][0]["status"], "bytes_same_layout_changed")
        self.assertEqual(data["sections"][0]["before"]["characteristics"], old_flags)
        self.assertEqual(data["sections"][0]["after"]["characteristics"], old_flags | 0x80000000)
        self.assertEqual(data["sections"][1]["status"], "identical")
        self.assertTrue(data["rawSectionsUnchangedButFileChanged"])
        self.assertFalse(data["nativeOffsetsQualified"])

    def test_text_byte_change_fails_closed_with_rva(self):
        changed = bytearray(self.orig)
        changed[0x217] ^= 1
        self.after.write_bytes(changed)
        proc, report = self.run_compare(("--block-bytes", "64"))
        self.assertEqual(proc.returncode, 2, proc.stderr)
        data = json.loads((report / "report.json").read_text(encoding="utf8"))
        self.assertEqual(data["status"], "CHANGED")
        self.assertFalse(data["nativeOffsetsQualified"])
        self.assertEqual(data["sections"][0]["status"], "bytes_changed")
        self.assertEqual(data["sections"][0]["difference"]["blocks"][0]["oldRva"], 0x1000)
        self.assertEqual(data["sections"][1]["status"], "identical")

    def test_many_changed_blocks_are_capped(self):
        changed = bytearray(self.orig)
        for offset in (0x201, 0x281, 0x301, 0x381):
            changed[offset] ^= 1
        self.after.write_bytes(changed)
        proc, report = self.run_compare(("--block-bytes", "64", "--max-blocks", "1"))
        self.assertEqual(proc.returncode, 2, proc.stderr)
        d = json.loads((report / "report.json").read_text(encoding="utf8"))
        info = d["sections"][0]["difference"]
        self.assertEqual(info["changedBlocks"], 4)
        self.assertEqual(len(info["blocks"]), 1)
        self.assertTrue(info["blocksTruncated"])

    def test_new_section_changes_image_without_fabricating_mapping(self):
        self.after.write_bytes(sample_pe(3))
        proc, report = self.run_compare()
        self.assertEqual(proc.returncode, 2, proc.stderr)
        d = json.loads((report / "report.json").read_text(encoding="utf8"))
        self.assertEqual(d["sections"][2]["id"], ".data#1")
        self.assertEqual(d["sections"][2]["status"], "added")

    def test_anchor_signature_must_match_original(self):
        changed = bytearray(self.orig)
        changed[0x205] ^= 2
        self.after.write_bytes(changed)
        manifest = self.root / "anchors.json"
        manifest.write_text(json.dumps({"schemaVersion": 1, "sourceSha256": self.sha, "anchors": [
            {"id": "synthetic-instruction", "rva": "0x1005", "hex": "90"}]}), encoding="utf8")
        proc, report = self.run_compare(("--anchors", str(manifest)))
        self.assertEqual(proc.returncode, 2, proc.stderr)
        d = json.loads((report / "report.json").read_text(encoding="utf8"))
        self.assertEqual(d["anchors"][0]["status"], "bytes_different_at_same_rva")
        manifest.write_text(json.dumps({"schemaVersion": 1, "sourceSha256": self.sha, "anchors": [
            {"id": "synthetic-instruction", "rva": "0x1005", "hex": "cc"}]}), encoding="utf8")
        proc, report = self.run_compare(("--anchors", str(manifest)))
        self.assertEqual(proc.returncode, 3)
        self.assertFalse(report.exists())

    def test_wrong_expected_baseline_fails(self):
        self.sha = "0" * 64
        proc, report = self.run_compare()
        self.assertEqual(proc.returncode, 3)
        self.assertFalse(report.exists())

    def test_invalid_cli_argument_is_error_not_changed(self):
        proc, report = self.run_compare(("--block-bytes", "8"))
        self.assertEqual(proc.returncode, 3)
        self.assertEqual(json.loads(proc.stderr)["status"], "ERROR")
        self.assertFalse(report.exists())

    def test_missing_and_same_path_fail(self):
        proc, report = self.run_compare(target=self.root / "missing.exe")
        self.assertEqual(proc.returncode, 3)
        self.assertFalse(report.exists())
        proc, report = self.run_compare(target=self.before)
        self.assertEqual(proc.returncode, 3)
        self.assertFalse(report.exists())

    def test_truncated_nonpe_and_wrong_machine_fail(self):
        for candidate in (b"", b"bad", b"MZ" + b"\0" * 30):
            self.after.write_bytes(candidate)
            proc, report = self.run_compare()
            self.assertEqual(proc.returncode, 3)
            self.assertFalse(report.exists())
        wrong = bytearray(self.orig)
        struct.pack_into("<H", wrong, 0x84, 0x014C)
        self.after.write_bytes(wrong)
        proc, report = self.run_compare()
        self.assertEqual(proc.returncode, 3)
        self.assertFalse(report.exists())

    def test_overlapping_raw_sections_fail(self):
        invalid = bytearray(self.orig)
        second = 0x98 + 0xF0 + 40
        struct.pack_into("<I", invalid, second + 20, 0x300)
        self.after.write_bytes(invalid)
        proc, report = self.run_compare()
        self.assertEqual(proc.returncode, 3)
        self.assertFalse(report.exists())

    def test_output_must_be_new_and_outside_inputs(self):
        proc, report = self.run_compare()
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.counter -= 1
        proc, _ = self.run_compare()
        self.assertEqual(proc.returncode, 3)
        self.counter += 1
        direct = [sys.executable, "-B", str(SCRIPT), "--before", str(self.before),
                  "--after", str(self.after), "--expected-before-sha", self.sha,
                  "--output-dir", str(self.before.parent / "danger")]
        proc = subprocess.run(direct, capture_output=True, text=True, timeout=20)
        self.assertEqual(proc.returncode, 3)
        self.assertFalse((self.before.parent / "danger").exists())


if __name__ == "__main__":
    unittest.main()
