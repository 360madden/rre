#!/usr/bin/env python3
"""Negative and positive fail-closed tests for the offline legacy PE selector."""
from __future__ import annotations

import hashlib
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import legacy_pe_fixture as fixture


class LegacyPeFixtureTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / "sample.exe"

    def test_missing_environment_rejected(self):
        with patch.dict(os.environ, {fixture.ENV_NAME: ""}):
            with self.assertRaisesRegex(ValueError, fixture.ENV_NAME):
                fixture.resolve_legacy_pe()

    def test_nonexistent_file_rejected(self):
        with self.assertRaisesRegex(ValueError, "Cannot read"):
            fixture.qualify_legacy_pe(self.path)

    def test_directory_rejected(self):
        with self.assertRaisesRegex(ValueError, "not a regular file"):
            fixture.qualify_legacy_pe(Path(self.temp.name))

    def test_incorrect_size_rejected_before_hash(self):
        self.path.write_bytes(b"not a RIFT binary")
        with self.assertRaisesRegex(ValueError, "size mismatch"):
            fixture.qualify_legacy_pe(self.path)

    def test_correct_size_wrong_sha_rejected(self):
        raw = b"controlled fixture sample"
        self.path.write_bytes(raw)
        with patch.object(fixture, "EXPECTED_SIZE", len(raw)):
            with self.assertRaisesRegex(ValueError, "SHA-256 mismatch"):
                fixture.qualify_legacy_pe(self.path)

    def test_exact_source_selection_and_environment(self):
        raw = b"controlled fixture sample"
        self.path.write_bytes(raw)
        digest = hashlib.sha256(raw).hexdigest()
        with patch.object(fixture, "EXPECTED_SIZE", len(raw)):
            with patch.object(fixture, "EXPECTED_SHA256", digest):
                qualified = fixture.qualify_legacy_pe(self.path)
                self.assertEqual(qualified, {"path": str(self.path.resolve()), "size": len(raw), "sha256": digest})
                with patch.dict(os.environ, {fixture.ENV_NAME: str(self.path)}):
                    self.assertEqual(fixture.resolve_legacy_pe(), self.path.resolve())


if __name__ == "__main__":
    unittest.main()
