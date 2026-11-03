"""Offline-only negative controls for the optional SC-103 Windows Lua 5.3 runner."""
from __future__ import annotations

import importlib.util
import io
import os
from pathlib import Path
import subprocess
import tempfile
import types
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "tools" / "run_sc103_lua53_offline.py"
SPEC = importlib.util.spec_from_file_location("sc103_lua53_runner_under_test", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
runner = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(runner)

GOOD = b"SC103_HOVER_PROBE_OFFLINE_TESTS_PASS 454\n"
HASHES = {"luaExe": runner.EXE_SHA256, "luaDll": runner.DLL_SHA256,
          "probe": "a" * 64, "fixture": "b" * 64, "copy": "c" * 64}


class TestResultContract(unittest.TestCase):
    def fail_code(self, code: str, exit_code: int = 0, out: bytes = GOOD,
                  err: bytes = b"") -> None:
        with self.assertRaises(runner.RunnerFailure) as caught:
            runner.verify_result(exit_code, out, err)
        self.assertEqual(str(caught.exception), code)

    def test_exact_pass_and_higher_count(self):
        self.assertEqual(runner.MIN_ASSERTIONS, 454)
        self.assertEqual(runner.verify_result(0, GOOD, b""), 454)
        self.assertEqual(runner.verify_result(0, b"SC103_HOVER_PROBE_OFFLINE_TESTS_PASS 455\r\n", b""), 455)

    def test_nonzero_exit_does_not_pass(self):
        self.fail_code("LUA_NONZERO_EXIT", 1)

    def test_stderr_does_not_pass(self):
        self.fail_code("LUA_STDERR_NOT_EMPTY", err=b"synthetic warning")

    def test_missing_marker_does_not_pass(self):
        self.fail_code("LUA_MARKER_INVALID", out=b"PASS 454\n")

    def test_partial_or_extra_output_does_not_pass(self):
        self.fail_code("LUA_MARKER_INVALID", out=b"prefix SC103_HOVER_PROBE_OFFLINE_TESTS_PASS 454\n")
        self.fail_code("LUA_MARKER_INVALID", out=GOOD + b"extra\n")

    def test_duplicate_marker_does_not_pass(self):
        self.fail_code("LUA_MARKER_INVALID", out=GOOD + GOOD)

    def test_lower_assertion_count_does_not_pass(self):
        self.fail_code("LUA_ASSERTION_COUNT_LOW", out=b"SC103_HOVER_PROBE_OFFLINE_TESTS_PASS 453\n")
        self.fail_code("LUA_ASSERTION_COUNT_LOW", out=b"SC103_HOVER_PROBE_OFFLINE_TESTS_PASS 430\n")

    def test_non_ascii_or_oversize_output_does_not_pass(self):
        self.fail_code("LUA_STDOUT_NOT_ASCII", out=b"\xff")
        self.fail_code("LUA_STDOUT_OVERSIZE", out=b"A" * 1025)

    def test_extra_carriage_returns_do_not_pass(self):
        self.fail_code("LUA_MARKER_INVALID", out=GOOD + b"\r\r")


class TestPreflight(unittest.TestCase):
    def test_runtime_executable_hash_mismatch(self):
        with tempfile.TemporaryDirectory() as folder:
            with self.assertRaises(runner.RunnerFailure) as caught:
                runner.check_runtime({**HASHES, "luaExe": "0" * 64},
                                     root=Path(folder), exe=Path(folder) / "lua.exe",
                                     dll=Path(folder) / "lua53-32.dll",
                                     windows_root=Path(folder))
            self.assertEqual(str(caught.exception), "LUA_EXE_HASH_MISMATCH")

    def test_runtime_dll_hash_mismatch(self):
        with tempfile.TemporaryDirectory() as folder:
            with self.assertRaises(runner.RunnerFailure) as caught:
                runner.check_runtime({**HASHES, "luaDll": "0" * 64},
                                     root=Path(folder), exe=Path(folder) / "lua.exe",
                                     dll=Path(folder) / "lua53-32.dll",
                                     windows_root=Path(folder))
            self.assertEqual(str(caught.exception), "LUA_DLL_HASH_MISMATCH")

    def test_unqualified_shadow_dll_blocks(self):
        with tempfile.TemporaryDirectory() as folder:
            base = Path(folder)
            exe_dir = base / "lua_extra"
            exe_dir.mkdir()
            (exe_dir / "lua53-32.dll").write_bytes(b"wrong synthetic DLL")
            with self.assertRaises(runner.RunnerFailure) as caught:
                runner.check_runtime(HASHES, root=base / "rre",
                                     exe=exe_dir / "lua.exe",
                                     dll=base / "lua53-32.dll",
                                     windows_root=base / "windows")
            self.assertEqual(str(caught.exception), "DLL_SHADOW_HASH_MISMATCH")

    def test_expected_checkpoint_hash_is_optional_and_exact(self):
        runner.check_expected(HASHES, {"probe": None, "fixture": "b" * 64})
        with self.assertRaises(runner.RunnerFailure) as caught:
            runner.check_expected(HASHES, {"probe": "d" * 64})
        self.assertEqual(str(caught.exception), "PROBE_HASH_MISMATCH")
        with self.assertRaises(runner.RunnerFailure) as caught:
            runner.check_expected(HASHES, {"probe": "xyz"})
        self.assertEqual(str(caught.exception), "EXPECTED_HASH_INVALID")

    def test_default_run_uses_reviewed_source_hashes(self):
        requested = {name: None for name in runner.SOURCES}
        self.assertEqual(runner.expected_sources(requested, True), runner.APPROVED_SOURCE_SHA256)
        drifted = {**HASHES, **runner.APPROVED_SOURCE_SHA256, "fixture": "0" * 64}
        with self.assertRaises(runner.RunnerFailure) as caught:
            runner.check_expected(drifted, runner.expected_sources(requested, True))
        self.assertEqual(str(caught.exception), "FIXTURE_HASH_MISMATCH")

    def test_partial_override_is_rejected_and_full_override_explicit(self):
        provided = {"probe": "a" * 64, "fixture": None, "copy": None}
        with self.assertRaises(runner.RunnerFailure) as caught:
            runner.expected_sources(provided, True)
        self.assertEqual(str(caught.exception), "EXPECTED_HASH_SET_INCOMPLETE")
        full = {"probe": "a" * 64, "fixture": "b" * 64, "copy": "c" * 64}
        self.assertEqual(runner.expected_sources(full, True), full)
        runner.check_expected(HASHES, full)
        self.assertEqual(runner.expected_sources(provided, False), provided)

    def test_missing_file_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            with self.assertRaises(runner.RunnerFailure) as caught:
                runner.digest(Path(folder) / "missing.lua")
            self.assertEqual(str(caught.exception), "FILE_MISSING")


class TestChildIsolation(unittest.TestCase):
    def test_check_mode_never_launches_child(self):
        with mock.patch.object(runner.os, "name", "nt"), \
             mock.patch.object(runner, "all_hashes", return_value=HASHES), \
             mock.patch.object(runner, "check_runtime"), \
             mock.patch.object(runner, "run_once") as launch, \
             mock.patch("sys.stdout", new_callable=io.StringIO):
            self.assertEqual(runner.main(["--check"]), 0)
            launch.assert_not_called()

    def test_default_run_rejects_drift_before_launch(self):
        drifted = {**HASHES, **runner.APPROVED_SOURCE_SHA256, "fixture": "0" * 64}
        with mock.patch.object(runner.os, "name", "nt"), \
             mock.patch.object(runner, "all_hashes", return_value=drifted), \
             mock.patch.object(runner, "check_runtime"), \
             mock.patch.object(runner, "run_once") as launch, \
             mock.patch("sys.stderr", new_callable=io.StringIO) as out:
            self.assertEqual(runner.main(["--run"]), 2)
            self.assertIn("FIXTURE_HASH_MISMATCH", out.getvalue())
            launch.assert_not_called()

    def test_launch_uses_fixed_fixture_and_child_only_path(self):
        before_path = os.environ.get("PATH")
        observed = {}

        def launch(argv, **kwargs):
            observed.update({"argv": argv, **kwargs})
            return types.SimpleNamespace(returncode=0, stdout=GOOD, stderr=b"")

        count = runner.run_once(HASHES, launcher=launch,
                                snapshot=lambda *args: HASHES)
        self.assertEqual(count, 454)
        self.assertEqual(os.environ.get("PATH"), before_path)
        self.assertEqual(observed["argv"][1], "tools/test_sc103_luapad_hover_probe.lua")
        self.assertEqual(observed["cwd"], runner.ROOT)
        self.assertFalse(observed["shell"])
        self.assertEqual(observed["stdin"], subprocess.DEVNULL)
        self.assertEqual(observed["timeout"], runner.TIMEOUT_SECONDS)
        self.assertTrue(observed["env"]["PATH"].startswith(str(runner.LUA_DLL.parent)))

    def test_mutated_source_or_runtime_invalidates_pass(self):
        changed = {**HASHES, "copy": "0" * 64}
        launcher = lambda *args, **kwargs: types.SimpleNamespace(
            returncode=0, stdout=GOOD, stderr=b"")
        with self.assertRaises(runner.RunnerFailure) as caught:
            runner.run_once(HASHES, launcher=launcher, snapshot=lambda *args: changed)
        self.assertEqual(str(caught.exception), "FILES_CHANGED_DURING_RUN")

    def test_timeout_does_not_pass(self):
        def timeout(*args, **kwargs):
            raise subprocess.TimeoutExpired("lua.exe", 30)
        with self.assertRaises(runner.RunnerFailure) as caught:
            runner.run_once(HASHES, launcher=timeout, snapshot=lambda *args: HASHES)
        self.assertEqual(str(caught.exception), "LUA_TIMEOUT")

    def test_launch_error_does_not_pass(self):
        def launch_error(*args, **kwargs):
            raise FileNotFoundError("synthetic missing interpreter")
        with self.assertRaises(runner.RunnerFailure) as caught:
            runner.run_once(HASHES, launcher=launch_error, snapshot=lambda *args: HASHES)
        self.assertEqual(str(caught.exception), "LUA_LAUNCH_FAILED")


if __name__ == "__main__":
    unittest.main()
