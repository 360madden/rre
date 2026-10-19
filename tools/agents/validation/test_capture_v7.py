"""V7 synthetic regression tests; never run or modify the game or installed tools."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import capture_v7 as v7


class CaptureV7Tests(unittest.TestCase):
    def test_zero_result_targets_are_explicit(self):
        result = {
            "schemaVersion": 1, "functions": [],
            "queueRemaining": 0, "unresolvedAnchors": [{"rva": "0xbeef", "reason": "No unwind range"}],
            "callerSearchSummary": [{
                "targetRva": "0xdead", "rawCandidatesScanned": 0,
                "qualifiedCandidates": 0, "qualifiedRetained": 0,
                "scanComplete": True, "qualifiedResultsTruncated": False
            }]}
        report = v7.describe_artifact("static", result, ["0xbeef"], ["0xdead"], [])
        self.assertEqual(report["requestedAnchors"], ["0xbeef"])
        self.assertEqual(report["callerCoverageByTarget"]["0xdead"]["qualifiedCandidates"], 0)
        self.assertTrue(report["boundedCaptureComplete"])
        self.assertEqual(report["pendingRegionQueue"], 0)

    def test_unreported_requested_anchor_is_incomplete(self):
        data = {"schemaVersion": 1, "functions": [], "queueRemaining": 0,
                "unresolvedAnchors": [], "callerSearchSummary": []}
        result = v7.describe_artifact("static", data, ["0x1234"], [], [])
        self.assertFalse(result["boundedCaptureComplete"])
        self.assertEqual(result["unaccountedRequestedAnchors"], ["0x1234"])

    def test_scanner_limit_and_decoding_gaps_dont_disappear(self):
        base = {
            "schemaVersion": 1, "functions": [{
                "beginRva": "0x1000", "decodedThroughRvaExclusive": "0x1003",
                "windowTruncated": True, "instructionDecodingCoversWindow": False
            }],
            "queueRemaining": 2, "unresolvedAnchors": [{"rva": "0x3000"}],
            "callerSearchSummary": [{
                "targetRva": "0x2000", "qualifiedCandidates": 66,
                "qualifiedRetained": 64, "scanComplete": True,
                "qualifiedResultsTruncated": True
            }]
        }
        report = v7.describe_artifact("static", base, ["0x1000"], ["0x2000"], [])
        self.assertFalse(report["boundedCaptureComplete"])
        self.assertEqual(report["pendingRegionQueue"], 2)
        self.assertEqual(report["qualifiedCallerResultsClipped"], ["0x2000"])
        self.assertEqual(len(report["incompleteWindows"]), 1)

    def test_missing_caller_summary_fails_closed(self):
        with self.assertRaisesRegex(ValueError, "summary"):
            v7.describe_artifact("static", {
                "schemaVersion": 1, "functions": [], "queueRemaining": 0
            }, ["0x1000"], ["0x2000"], [])

    def test_names_empty_reference_and_zero_terms(self):
        output = {
            "schemaVersion": 1, "referenceTargets": ["0x8000"],
            "references": [], "stringMatches": [], "matchesTruncated": False,
            "queryTerms": ["navmesh"], "termCounts": {"navmesh": 0}
        }
        report = v7.describe_artifact("names", output, [], [], ["0x8000"])
        self.assertEqual(report["referenceMatchesByTarget"], {"0x8000": 0})
        self.assertEqual(report["termsWithZeroMatches"], ["navmesh"])
        self.assertTrue(report["boundedCaptureComplete"])
        output["referenceTargets"] = []
        with self.assertRaisesRegex(ValueError, "reference"):
            v7.describe_artifact("names", output, [], [], ["0x8000"])

    def test_local_dependency_hashes_recurse_and_identify_roles(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            script, helper = root / "main.py", root / "helper.py"
            dep, later = root / "dep.py", root / "later.py"
            script.write_text("from dep import a\n", encoding="utf-8")
            helper.write_text("import later\n", encoding="utf-8")
            dep.write_text("a = 42\n", encoding="utf-8")
            later.write_text("b = 99\n", encoding="utf-8")
            inv = v7.inventory(script, helper)
            self.assertTrue(inv["completeWithinMethod"])
            self.assertEqual({Path(f["path"]).name for f in inv["files"]},
                             {"main.py", "helper.py", "dep.py", "later.py"})
            self.assertEqual(len({f["sha256"] for f in inv["files"]}), 4)

    def test_exclusive_preflight_refuses_existing_output(self):
        with tempfile.TemporaryDirectory() as tmp:
            d = Path(tmp)
            artifact = d / "original.json"
            artifact.write_text("NOT TO BE REPLACED", encoding="utf-8")
            manifest = d / "new-manifest.json"
            script = HERE / "capture_v7.py"
            run = subprocess.run([
                sys.executable, "-B", str(script), "--kind", "static",
                "--binary", str(d / "dummy.exe"), "--helper", str(d / "dummy.py"),
                "--expected-sha256", v7.EXPECTED_BUILD,
                "--expected-helper-sha256", "0" * 64,
                "--rva", "0x1000", "--artifact", str(artifact), "--manifest", str(manifest)
            ], capture_output=True, text=True, timeout=10)
            self.assertEqual(run.returncode, 2)
            self.assertEqual(artifact.read_text(encoding="utf-8"), "NOT TO BE REPLACED")
            self.assertFalse(manifest.exists())
            self.assertIn("preflight-rejected", run.stderr)

    def test_versions_keep_distribution_module_and_engine_distinct(self):
        obj = v7.environment_versions()
        self.assertTrue(obj["capstone"]["distributionVersion"])
        self.assertTrue(obj["capstone"]["moduleVersion"])
        self.assertEqual(len(obj["capstone"]["engineVersion"]), 3)
        self.assertTrue(obj["pefile"]["distributionVersion"])


if __name__ == "__main__":
    unittest.main()
