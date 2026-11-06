"""Offline, no-model tests for the FreeBuff overlap supervisor."""
from __future__ import annotations
import importlib.util
from pathlib import Path
import unittest

MODULE = Path(__file__).with_name("freebuff-parallel-review.py")
spec = importlib.util.spec_from_file_location("rre_freebuff_parallel", MODULE)
review = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(review)

def sample(mode, start, end, *, accepted=True):
    return {
        "mode": mode, "state": "settled", "exitCode": 0,
        "promptSent": True, "markerObserved": accepted, "adapterCompletion": accepted,
        "markerMode": review.EXPECTED_MODEL_MODES[mode], "markerModeMatches": True,
        "ownedChildStopped": True, "tempFolderCleaned": True,
        "startedMonotonic": start, "endedMonotonic": end,
        "modelObservationSeconds": 28, "reviewLines": [],
    }

class SupervisorTests(unittest.TestCase):
    def test_missing_duplicate_or_single_worker_cannot_complete(self):
        one = sample("sc103", 1.0, 2.0)
        other = sample("rc30", 1.5, 2.5)
        self.assertEqual(review.clean_summary([])["status"], "incomplete")
        self.assertEqual(review.clean_summary([one])["status"], "incomplete")
        self.assertEqual(review.clean_summary([one, one])["status"], "incomplete")
        self.assertEqual(review.clean_summary([one, other])["status"], "completed")

    def test_partial_or_failed_worker_receipt_is_not_counted(self):
        a, b = sample("sc103", 1, 5), sample("rc30", 2, 6)
        b["exitCode"] = 2
        self.assertEqual(review.clean_summary([a, b])["completedReviewSessions"], 1)
        b["exitCode"] = 0
        b["state"] = "timed-out"
        self.assertEqual(review.clean_summary([a, b])["status"], "incomplete")
        self.assertEqual(review.clean_summary([a, b])["completedReviewSessions"], 1)
        b["state"] = "settled"
        b["promptSent"] = False
        self.assertEqual(review.clean_summary([a, b])["status"], "incomplete")

    def test_wrong_upstream_mode_cannot_complete_a_review(self):
        import json
        from unittest.mock import patch
        wrong_transport = {
            "mode": "freebuff-review-pilot", "review_final_marker_seen": True,
            "review_prompt_sent": True, "owned_process_stopped": True,
            "probe_folder_cleaned": True,
        }
        wrapper = {"rreReview": "rc30", "acceptedCompletion": True}
        class SyntheticChild:
            pid = 12345
            returncode = 0
            def communicate(self, timeout=None):
                return json.dumps(wrong_transport) + "\n" + json.dumps(wrapper) + "\n", ""
        with patch.object(review.subprocess, "Popen", return_value=SyntheticChild()):
            receipt = review.run_child("rc30", ["synthetic-only"], timeout=2)
        self.assertEqual(receipt["markerMode"], "freebuff-review-pilot")
        self.assertEqual(receipt["expectedMarkerMode"], "freebuff-lifecycle-review")
        self.assertTrue(receipt["adapterCompletion"])  # Wrapper alone is insufficient.
        self.assertFalse(receipt["markerModeMatches"])
        self.assertFalse(receipt["markerObserved"])
        self.assertEqual(review.clean_summary([
            receipt, sample("sc103", 1.0, 2.0)])["status"], "incomplete")

    def test_correct_upstream_mode_is_still_accepted(self):
        import json
        from unittest.mock import patch
        right_transport = {
            "mode": "freebuff-lifecycle-review", "review_final_marker_seen": True,
            "review_prompt_sent": True, "owned_process_stopped": True,
            "probe_folder_cleaned": True,
        }
        wrapper = {"rreReview": "rc30", "acceptedCompletion": True}
        class SyntheticChild:
            pid = 12345
            returncode = 0
            def communicate(self, timeout=None):
                return json.dumps(right_transport) + "\n" + json.dumps(wrapper) + "\n", ""
        with patch.object(review.subprocess, "Popen", return_value=SyntheticChild()):
            receipt = review.run_child("rc30", ["synthetic-only"], timeout=2)
        self.assertTrue(receipt["markerModeMatches"])
        self.assertTrue(receipt["markerObserved"])
        self.assertEqual(review.clean_summary([
            receipt, sample("sc103", 1.0, 2.0)])["status"], "completed")

    def test_tampered_mode_or_marker_fails_final_summary(self):
        a, b = sample("sc103", 1, 4), sample("rc30", 2, 5)
        self.assertEqual(review.clean_summary([a, b])["status"], "completed")
        a["markerMode"] = "freebuff-lifecycle-review"
        self.assertEqual(review.clean_summary([a, b])["status"], "incomplete")
        a["markerMode"] = "freebuff-review-pilot"
        a["markerModeMatches"] = False
        self.assertEqual(review.clean_summary([a, b])["status"], "incomplete")

    def test_failed_windows_taskkill_falls_back_to_own_child_kill(self):
        import subprocess
        from unittest.mock import patch
        class HungChild:
            pid = 12345
            returncode = None
            kills = 0
            def poll(self):
                return self.returncode
            def kill(self):
                self.kills += 1
                self.returncode = 1
            def communicate(self, timeout=None):
                if self.returncode is not None:
                    return "", "synthetic child terminated"
                raise subprocess.TimeoutExpired(["synthetic"], timeout or 1)

        fake = HungChild()
        with patch.object(review.subprocess, "Popen", return_value=fake), \
             patch.object(review.subprocess, "run",
                          return_value=subprocess.CompletedProcess(["taskkill"], 1)):
            result = review.run_child("synthetic", ["no child executed"], timeout=1)
        self.assertEqual(result["state"], "timed-out")
        self.assertEqual(fake.kills, 1)
        self.assertEqual(result["exitCode"], 1)
        self.assertEqual(result["cleanupFault"], "TASKKILL_FAILED")

    def test_taskkill_exception_still_falls_back_to_owned_child(self):
        import subprocess
        from unittest.mock import patch
        class Child:
            pid = 12345
            returncode = None
            killed = False
            def poll(self):
                return self.returncode
            def kill(self):
                self.killed = True
                self.returncode = 1
            def communicate(self, timeout=None):
                if self.killed:
                    return "", "taskkill crashed but fallback succeeded"
                raise subprocess.TimeoutExpired(["synthetic"], timeout or 1)

        child = Child()
        with patch.object(review.subprocess, "Popen", return_value=child), \
             patch.object(review.subprocess, "run",
                          side_effect=subprocess.TimeoutExpired(["taskkill"], 8)):
            result = review.run_child("synthetic", ["no child executed"], timeout=1)
        self.assertTrue(child.killed)
        self.assertEqual(result["state"], "timed-out")
        self.assertEqual(result["cleanupFault"], "TASKKILL_FAILED")

    def test_unkillable_child_returns_bounded_failed_receipt(self):
        import subprocess
        from unittest.mock import patch
        class Unkillable:
            pid = 12345
            returncode = None
            def poll(self):
                return None
            def kill(self):
                raise PermissionError("synthetic access denied")
            def communicate(self, timeout=None):
                raise subprocess.TimeoutExpired(["synthetic"], timeout or 1)

        with patch.object(review.subprocess, "Popen", return_value=Unkillable()), \
             patch.object(review.subprocess, "run",
                          return_value=subprocess.CompletedProcess(["taskkill"], 1)):
            result = review.run_child("synthetic", ["no child executed"], timeout=1)
        self.assertEqual(result["state"], "timed-out")
        self.assertIsNone(result["exitCode"])
        self.assertEqual(result["cleanupFault"], "CHILD_STILL_RUNNING")
        self.assertIn("CHILD_CLEANUP_UNCONFIRMED", result["errorTail"])

    def test_positive_overlap(self):
        a, b = sample("sc103", 4.0, 23.0), sample("rc30", 6.0, 20.0)
        self.assertEqual(review.overlap_seconds([a, b]), 14.0)
        self.assertEqual(review.clean_summary([a, b])["completedReviewSessions"], 2)
        self.assertEqual(review.clean_summary([a, b])["status"], "completed")
        summary = review.clean_summary([a, b])
        self.assertFalse(summary["modelInferenceOverlapIndependentlyProved"])
        self.assertFalse(summary["gameActionsRequested"])
        self.assertFalse(summary["modelOsSandboxVerified"])
        self.assertTrue(summary["reviewersUseDisposableSourceCopies"])

    def test_no_overlap_no_false_success(self):
        a, b = sample("sc103", 4, 6), sample("rc30", 8, 10, accepted=False)
        self.assertEqual(review.overlap_seconds([a, b]), 0.0)
        summary = review.clean_summary([a, b])
        self.assertEqual(summary["status"], "incomplete")
        self.assertEqual(summary["completedReviewSessions"], 1)

    def test_markers_alone_not_enough(self):
        a, b = sample("sc103", 4, 10), sample("rc30", 5, 11)
        b["ownedChildStopped"] = False
        self.assertEqual(review.clean_summary([a, b])["status"], "incomplete")
        b["ownedChildStopped"] = True
        a["exitCode"] = 2
        self.assertEqual(review.clean_summary([a, b])["status"], "incomplete")

    def test_screen_filters_ui_and_preserves_bounded_findings(self):
        result = review.relevant_lines({
            "review_visible_lines": [
                "May use data for AI training",
                "Defect: ui.lua:653 restores old baseline to new generation",
                "Working... analysing source",
                "NO_BLOCKERS: no remaining valid-ID regression",
            ],
            "review_visible_excerpt": [
                "Defect: ui.lua:653 restores old baseline to new generation",
                "Test: Pin then Undo should preserve valid entries",
            ],
        })
        self.assertEqual(len(result), 3)
        self.assertIn("ui.lua:653", result[0])
        self.assertTrue(all("May use data" not in x for x in result))

    def test_queue_and_channel_findings_survive_screen_filter(self):
        result = review.relevant_lines({
            "review_visible_lines": [
                "NO_MAPPING: ability queue raw value 1 has no current UI label",
                "Channel interruption cannot be inferred from a 105ms sampling interval",
                "Session active 30/30 hours remaining",
            ]
        })
        self.assertEqual(len(result), 2)
        self.assertTrue(result[0].startswith("NO_MAPPING"))
        self.assertIn("Channel interruption", result[1])

    def test_terminal_receipts_survive_windows_legacy_encoding(self):
        import json
        a, b = sample("sc103", 1.0, 9.0), sample("rc30", 2.0, 10.0)
        a["reviewLines"] = ["Defect: ui.lua:653 " + chr(0x2588) + " test"]
        summary = review.clean_summary([a, b])
        encoded = json.dumps(summary, ensure_ascii=True).encode("cp1252")
        self.assertIn("u2588", encoded.decode("ascii"))
        self.assertEqual(json.loads(encoded.decode("cp1252"))["status"], "completed")

    def test_review_source_copies_keep_original_repository_paths(self):
        adapter = Path(__file__).with_name("freebuff-rre-review.py").read_text(encoding="utf-8")
        self.assertIn("target = os.path.join(probe_dir, *parts)", adapter)
        self.assertIn("target = os.path.join(probe_dir, *source_parts)", adapter)
        self.assertIn("os.makedirs(os.path.dirname(target), exist_ok=True)", adapter)
        self.assertIn("FreeBuff copied-source layout is not preserved", adapter)
        self.assertIn("tools/sc103_luapad_hover_probe.lua", adapter)
        # The fixture dofile()s this helper; source-copy QA must not report it missing.
        self.assertIn('("tools", "sc103_luapad_copy_result.lua")', adapter)
        self.assertIn("addons/RRECollector/ui.lua", adapter)

    def test_fixed_independent_research_modes(self):
        self.assertEqual(review.RESEARCH_MODES, ("sc306", "sc503"))
        self.assertNotEqual(set(review.RESEARCH_MODES), set(review.MODES))
        self.assertEqual(
            review.clean_summary([sample("sc306", 1, 5), sample("sc503", 2, 6)],
                                 "rre-research-test")["runId"],
            "rre-research-test")
        adapter = Path(__file__).with_name("freebuff-rre-review.py")
        source = adapter.read_text(encoding="utf-8")
        for key in ("sc306", "sc503", "SC305-QUEUE-DOSSIER",
                    "SC306-QUEUE-ENUM-GAP", "SC303-TIMING-METADATA",
                    "SC502-OUTCOME", "NO_MAPPING"):
            self.assertIn(key, source)

    def test_snapshot_evidence_workers_are_fixed_and_independent(self):
        self.assertEqual(review.SNAPSHOT_AUDIT_MODES, ("slots", "file"))
        source = Path(__file__).with_name("freebuff-rre-review.py").read_text(encoding="utf-8")
        for item in ("rc30-saved-receipt.mjs", "test-rc30-saved-receipt.mjs",
                     "read-rrecollector-saved.mjs", '"slots"', '"file"'):
            self.assertIn(item, source)
        result = review.clean_summary(
            [sample("slots", 1, 8), sample("file", 2, 9)], "rre-snapshot-test")
        self.assertEqual(result["status"], "completed")
        self.assertEqual(result["runId"], "rre-snapshot-test")
        self.assertFalse(result["modelOsSandboxVerified"])

    def test_fixed_operator_proof_modes(self):
        self.assertEqual(review.OPERATOR_PROOF_MODES, ("operator", "ability"))
        text = Path(__file__).with_name("freebuff-rre-review.py").read_text(encoding="utf-8")
        for word in ("RC30-OPERATOR-ACCEPTANCE", "LEGENDARY-SELECTION",
                     '"operator"', '"ability"', "NO_GAPS", "NO_NEW_EVIDENCE"):
            self.assertIn(word, text)
        summary = review.clean_summary(
            [sample("operator", 1, 8), sample("ability", 2, 6)],
            "rre-operator-test")
        self.assertEqual(summary["status"], "completed")
        self.assertEqual(summary["runId"], "rre-operator-test")

    def test_freebuff_stale_probe_folder_isolated_without_deletion(self):
        import ast
        import os
        from unittest.mock import patch
        adapter_path = Path(__file__).with_name("freebuff-rre-review.py")
        tree = ast.parse(adapter_path.read_text(encoding="utf-8"))
        original = 'probe_dir = os.path.join(repo_root, "temp", probe_name)'
        replacements = [
            node.args[2].value for node in ast.walk(tree)
            if isinstance(node, ast.Call)
            and isinstance(node.func, ast.Name) and node.func.id == "replace_once"
            and len(node.args) == 3
            and isinstance(node.args[1], ast.Constant)
            and node.args[1].value == original
            and isinstance(node.args[2], ast.Constant)
        ]
        self.assertEqual(len(replacements), 1)
        assignment = replacements[0]
        self.assertIn("os.urandom(16).hex()", assignment)
        expr = compile(ast.parse(assignment.split(" = ", 1)[1], mode="eval"),
                       "<rre-probe-folder>", "eval")
        with patch.dict(os.environ, {"TEMP": os.path.abspath("C:/synthetic-temp")}):
            paths = [eval(expr, {"os": os, "probe_name": "fixed-review-pilot"})
                     for _ in range(3)]
        self.assertEqual(len(set(paths)), 3)
        self.assertTrue(all("rre-fixed-review-pilot-" in p for p in paths))
        # The upstream pre-existing-folder veto remains intact; no folder is
        # removed, reused or even created by this synthetic test.
        upstream = Path("C:/work/workbridge-mcp/scripts/freebuff-conpty-probe.py")
        source = upstream.read_text(encoding="utf-8")
        self.assertIn("if os.path.exists(probe_dir):", source)
        self.assertIn("raise FileExistsError(", source)

    def test_fake_children_actually_overlap(self):
        test_result = review.self_test()
        self.assertEqual(test_result["status"], "passed")
        self.assertEqual(test_result["fakeWorkers"], 2)
        self.assertGreater(test_result["childLifetimeOverlapSeconds"], 0.3)
        self.assertTrue(test_result["noModelCalls"])

if __name__ == "__main__":
    unittest.main()
