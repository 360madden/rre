"""Regression tests for WA-005 publication bounds and JSON Unicode scalars.

All files are synthetic, local and temporary. No game/process/network activity.
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[3]
SPEC = importlib.util.spec_from_file_location("world_inspector_boundaries", ROOT / "tools/world-inspector.py")
assert SPEC and SPEC.loader
M = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(M)


def snapshot() -> dict:
    return {"schemaVersion": 1, "sourceMode": "SyntheticFixture", "nearbyUnits": []}


class PublicationBoundaryTests(unittest.TestCase):
    def test_unicode_expansion_rejected_before_directory_creation(self):
        # Valid 2.44 MiB-scale UTF-8 input expands above the verifier's 8 MiB cap
        # because the JSON report duplicates observations and escapes astral text.
        symbol = "\U0001f680"
        data = snapshot()
        data["nearbyUnits"] = [
            {"id": "u" + str(i) + symbol * 150, "name": symbol * 512,
             "zone": symbol * 512, "coord": {"x": i, "y": 0, "z": 0}}
            for i in range(512)
        ]
        raw = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.assertLess(len(raw), M.MAX_BYTES)
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            source = root / "input.json"
            source.write_bytes(raw)
            output = root / "report"
            with self.assertRaisesRegex(ValueError, "report.json.*8 MiB"):
                M.inspect_file(source, "readerbridge", output)
            self.assertFalse(output.exists())
            self.assertEqual(source.read_bytes(), raw)

    def test_html_bound_uses_encoded_bytes_not_character_count(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            source = root / "input.json"
            source.write_text(json.dumps(snapshot()), encoding="utf-8")
            output = root / "report"
            with patch.object(M, "MAX_BYTES", 32768), patch.object(M, "render_html", return_value="é" * 16385):
                with self.assertRaisesRegex(ValueError, "report.html"):
                    M.inspect_file(source, "readerbridge", output)
            self.assertFalse(output.exists())

    def test_exact_output_byte_limit_publishes_and_verifies(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            source = root / "input.json"
            source.write_text(json.dumps(snapshot()), encoding="utf-8")
            output = root / "report"
            with patch.object(M, "MAX_BYTES", 32768), patch.object(M, "render_html", return_value="é" * 16384):
                M.inspect_file(source, "readerbridge", output)
                self.assertEqual((output / "report.html").stat().st_size, 32768)
                self.assertTrue(M.verify_publication(output)["publicationComplete"])

    def test_maximum_record_count_with_small_strings_remains_supported(self):
        data = snapshot()
        data["nearbyUnits"] = [{"id": "u" + str(i)} for i in range(512)]
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            source = root / "input.json"
            source.write_text(json.dumps(data), encoding="utf-8")
            report = M.inspect_file(source, "readerbridge", root / "report")
            self.assertEqual(report["counts"]["distinctIds"], 512)
            self.assertTrue(M.verify_publication(root / "report")["publicationComplete"])


class JsonUnicodeScalarTests(unittest.TestCase):
    def assert_invalid_before_output(self, data: dict):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            source = root / "input.json"
            raw = json.dumps(data, ensure_ascii=True).encode("utf-8")
            source.write_bytes(raw)
            with self.assertRaisesRegex(ValueError, "Unicode"):
                M.inspect_file(source, "readerbridge", root / "report")
            self.assertFalse((root / "report").exists())
            self.assertEqual(source.read_bytes(), raw)

    def test_lone_surrogate_in_ignored_value_rejected(self):
        for bad in ("\ud800", "\udfff"):
            with self.subTest(codepoint=ord(bad)):
                data = snapshot()
                data["legacyExtra"] = bad
                self.assert_invalid_before_output(data)

    def test_lone_surrogate_in_ignored_key_rejected(self):
        data = snapshot()
        data["\ud800"] = "ignored"
        self.assert_invalid_before_output(data)

    def test_lone_surrogate_nested_in_ignored_array_rejected(self):
        data = snapshot()
        data["legacyExtra"] = [{"valid": ["ok", {"bad": "\udfff"}]}]
        self.assert_invalid_before_output(data)

    def test_valid_surrogate_pair_and_legacy_controls_remain_ignored(self):
        data = snapshot()
        data["legacyExtra"] = ["\U0001f680", "line\nwith\ttabs", {"\U0001f680": "ok"}]
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            source = root / "input.json"
            source.write_text(json.dumps(data, ensure_ascii=True), encoding="utf-8")
            report = M.inspect_file(source, "readerbridge", root / "report")
            self.assertEqual(report["counts"]["distinctIds"], 0)
            self.assertNotIn("legacyExtra", report)
            self.assertTrue(M.verify_publication(root / "report")["publicationComplete"])

    def test_invalid_ignored_camera_scalar_rejected_before_output(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            source = root / "input.json"
            raw = json.dumps(snapshot()).encode("utf-8")
            source.write_bytes(raw)
            camera = {"schemaVersion": 1, "sourceSha256": hashlib.sha256(raw).hexdigest(),
                      "evidenceKind": "synthetic", "convention": M.CONVENTION,
                      "viewProjection": [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1],
                      "viewport": {"x": 0, "y": 0, "width": 800, "height": 600},
                      "legacyExtra": "\ud800"}
            camera_path = root / "camera.json"
            camera_path.write_text(json.dumps(camera), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "Unicode"):
                M.inspect_file(source, "readerbridge", root / "report", camera_path)
            self.assertFalse((root / "report").exists())


if __name__ == "__main__":
    unittest.main()
