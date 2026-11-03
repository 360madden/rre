#!/usr/bin/env python3
r"""Run SC-103's synthetic Lua fixture with an existing, SHA-pinned Windows Lua 5.3.

From the RRE root:
  \.venv\Scripts\python.exe -B tools\run_sc103_lua53_offline.py --check
  \.venv\Scripts\python.exe -B tools\run_sc103_lua53_offline.py --run

The default --run requires the three reviewed Lua source hashes; an intentional
new source revision requires all three explicit --expect-*-sha values. The
approved fixture is synthetic and makes no game, network, or SavedVariables
calls. No installs, global PATH changes, or persistent copies are made.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
LUA_EXE = Path(r"C:\work\tools\cheat-engine-master\Cheat Engine\bin\lua_extra\lua.exe")
LUA_DLL = LUA_EXE.parent.parent / "lua53-32.dll"
EXE_SHA256 = "702502820320538d06409d7818754ce529087ef8ff608a723f49b1ccffdc2d6f"
DLL_SHA256 = "58b206ab9a3d84fdafb537b419f721ecdeade489707dbab227b043d5343db369"
SOURCES = {
    "probe": Path("tools/sc103_luapad_hover_probe.lua"),
    "fixture": Path("tools/test_sc103_luapad_hover_probe.lua"),
    "copy": Path("tools/sc103_luapad_copy_result.lua"),
}
# Reviewed 2026-11-03 source snapshot. Default --run is fail-closed against drift.
APPROVED_SOURCE_SHA256 = {
    "probe": "fbf1199a7fc85f126157e477211044762dc3fbc0fcb943c05726941c70d1c816",
    "fixture": "c196a950bdbd979c548db66ab34e272e4558b2dee50768ba3d4833a8c20075dc",
    "copy": "478e81c2d83d7406c7998f8f6ebe311c3785a2acf4b7ca37b7689ad338f06406",
}
MIN_ASSERTIONS = 430
TIMEOUT_SECONDS = 30
SUCCESS = re.compile(r"SC103_HOVER_PROBE_OFFLINE_TESTS_PASS ([1-9][0-9]*)")


class RunnerFailure(Exception):
    """A bounded, machine-readable failure without child or private payloads."""


def digest(path: Path) -> str:
    if not path.is_file():
        raise RunnerFailure("FILE_MISSING")
    try:
        return hashlib.sha256(path.read_bytes()).hexdigest()
    except OSError:
        raise RunnerFailure("FILE_UNREADABLE") from None


def pinned(name: str, actual: str, expected: str) -> None:
    if actual != expected:
        raise RunnerFailure(name + "_HASH_MISMATCH")


def all_hashes(root: Path = ROOT, exe: Path = LUA_EXE, dll: Path = LUA_DLL) -> dict[str, str]:
    result = {"luaExe": digest(exe), "luaDll": digest(dll)}
    for name, relative in SOURCES.items():
        result[name] = digest(root / relative)
    return result


def check_runtime(before: dict[str, str], root: Path = ROOT,
                  exe: Path = LUA_EXE, dll: Path = LUA_DLL,
                  windows_root: Path | None = None) -> None:
    pinned("LUA_EXE", before["luaExe"], EXE_SHA256)
    pinned("LUA_DLL", before["luaDll"], DLL_SHA256)
    if windows_root is None:
        windows_root = Path(os.environ.get("SystemRoot", r"C:\Windows"))
    # Windows may look in the executable/cwd/system directories before PATH.
    # Refuse an unqualified alternate DLL; this is a preflight, not a loaded-module proof.
    candidates = (exe.parent / dll.name, root / dll.name,
                  windows_root / dll.name, windows_root / "System" / dll.name,
                  windows_root / "System32" / dll.name,
                  windows_root / "SysWOW64" / dll.name)
    seen: set[str] = set()
    for candidate in candidates:
        key = str(candidate).casefold()
        if key in seen:
            continue
        seen.add(key)
        if candidate.is_file():
            pinned("DLL_SHADOW", digest(candidate), DLL_SHA256)


def check_expected(before: dict[str, str], values: dict[str, str | None]) -> None:
    for name, value in values.items():
        if value is not None:
            if re.fullmatch(r"[0-9a-fA-F]{64}", value) is None:
                raise RunnerFailure("EXPECTED_HASH_INVALID")
            pinned(name.upper(), before[name], value.lower())


def expected_sources(provided: dict[str, str | None], for_run: bool) -> dict[str, str | None]:
    supplied = sum(value is not None for value in provided.values())
    if for_run:
        if supplied not in (0, len(SOURCES)):
            raise RunnerFailure("EXPECTED_HASH_SET_INCOMPLETE")
        if supplied == 0:
            return dict(APPROVED_SOURCE_SHA256)
    return provided


def verify_result(returncode: int, stdout: bytes, stderr: bytes) -> int:
    if returncode != 0:
        raise RunnerFailure("LUA_NONZERO_EXIT")
    if stderr:
        raise RunnerFailure("LUA_STDERR_NOT_EMPTY")
    if len(stdout) > 1024:
        raise RunnerFailure("LUA_STDOUT_OVERSIZE")
    try:
        output = stdout.decode("ascii")
    except UnicodeDecodeError:
        raise RunnerFailure("LUA_STDOUT_NOT_ASCII") from None
    if output.endswith("\r\n"):
        line = output[:-2]
    elif output.endswith("\n"):
        line = output[:-1]
    else:
        line = output
    match = SUCCESS.fullmatch(line)
    if match is None:
        raise RunnerFailure("LUA_MARKER_INVALID")
    checks = int(match.group(1))
    if checks < MIN_ASSERTIONS:
        raise RunnerFailure("LUA_ASSERTION_COUNT_LOW")
    return checks


def run_once(before: dict[str, str], *, root: Path = ROOT,
             exe: Path = LUA_EXE, dll: Path = LUA_DLL,
             launcher=None, snapshot=None) -> int:
    if launcher is None:
        launcher = subprocess.run
    if snapshot is None:
        snapshot = all_hashes
    child_env = os.environ.copy()
    child_env["PATH"] = str(dll.parent) + os.pathsep + child_env.get("PATH", "")
    try:
        result = launcher(
            [str(exe), str(SOURCES["fixture"]).replace("\\", "/")],
            cwd=root, env=child_env, stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=False,
            timeout=TIMEOUT_SECONDS,
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
            check=False,
        )
    except subprocess.TimeoutExpired:
        raise RunnerFailure("LUA_TIMEOUT") from None
    except OSError:
        raise RunnerFailure("LUA_LAUNCH_FAILED") from None
    after = snapshot(root, exe, dll)
    if after != before:
        raise RunnerFailure("FILES_CHANGED_DURING_RUN")
    return verify_result(result.returncode, result.stdout, result.stderr)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument("--check", action="store_true", help="Hash preflight only; do not launch Lua")
    action.add_argument("--run", action="store_true", help="Run the synthetic Lua fixture")
    for name in SOURCES:
        parser.add_argument("--expect-" + name + "-sha", default=None,
                            help="Optional full three-hash approved override for --run")
    args = parser.parse_args(argv)
    try:
        if os.name != "nt":
            raise RunnerFailure("WINDOWS_REQUIRED")
        before = all_hashes()
        check_runtime(before)
        provided = {name: getattr(args, "expect_" + name + "_sha")
                    for name in SOURCES}
        check_expected(before, expected_sources(provided, args.run))
        payload: dict[str, object] = {
            "runtime": "Windows Lua 5.3.0 (hash-pinned)",
            "hashes": before, "scope": "synthetic-offline-only",
        }
        if args.run:
            payload["assertions"] = run_once(before)
        print(("SC103_LUA53_OFFLINE_PASS " if args.run else "SC103_LUA53_CHECK_PASS ")
              + json.dumps(payload, sort_keys=True))
        return 0
    except RunnerFailure as error:
        print("SC103_LUA53_BLOCKED " + str(error), file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
