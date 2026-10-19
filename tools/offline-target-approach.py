#!/usr/bin/env python3
"""M4A deterministic, offline-only selected-target approach replay.

There is no Rift process access, input backend, IPC, memory read/write, or native
navigation function in this program. All distances are SYNTHETIC fixture units.
Source code and fixture evidence are kept separate from observed game behavior.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
import sys
from typing import Any

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
for lane in ("validation", "c2m", "follow", "collision"):
    sys.path.insert(0, str(ROOT / "tools" / "agents" / lane))

from m4a_fixture_audit import validate_suite
from m4a_geometry import classify_geometry
from m4a_guards import early_guard
from m4a_progress import classify_progress

SCHEMA_VERSION = 1
SOURCE_KIND = "synthetic-fixture"
MODE = "offline-replay-only"


def _hash(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _load_object(path: Path) -> tuple[dict[str, Any], str]:
    data = path.read_bytes()
    value = json.loads(data)
    if not isinstance(value, dict):
        raise ValueError(f"Expected a JSON object: {path}")
    return value, _hash(data)


def _case_result(case: dict[str, Any], policy: dict[str, Any],
                 source_kind: str, terminal_states: set[str]) -> dict[str, Any]:
    samples = case["samples"]
    initial = samples[0]
    initial_scene = initial["sceneId"]
    first_target = initial.get("target")
    initial_target = first_target.get("id") if isinstance(first_target, dict) else None
    previous_time: int | None = None
    previous_distance: float | None = None
    progress_time: int | None = None
    progress_baseline: float | None = None
    terminal: str | None = None
    trace: list[dict[str, Any]] = []

    for index, sample in enumerate(samples):
        already_terminal = terminal is not None
        distance: float | None = None
        height: float | None = None
        reason = "guard"
        if already_terminal:
            # Do not re-check a new target/scene after a safe stop.
            state = terminal
            reason = "ignored-after-terminal"
        else:
            state = early_guard(
                sample,
                initial_scene_id=initial_scene,
                initial_target_id=initial_target,
                previous_t_ms=previous_time,
                terminal_state=None,
                policy=policy,
                source_kind=source_kind,
            )
            if state is None:
                try:
                    geometric = classify_geometry(sample["player"], sample["target"], policy)
                    distance = geometric["distanceXZ"]
                    height = geometric["heightDelta"]
                    if not (math.isfinite(distance) and math.isfinite(height)):
                        raise ValueError("Distance overflow despite finite input coordinates")
                    state = geometric["state"]
                except (KeyError, TypeError, ValueError, OverflowError):
                    state = "invalid-sample"
                    reason = "invalid-geometry"
                else:
                    reason = "geometry"
                    if state == "approach-intent":
                        if progress_time is None:
                            progress_time = sample["tMs"]
                            progress_baseline = distance
                        if previous_distance is not None:
                            try:
                                progress_state = classify_progress(
                                    current_distance=distance,
                                    previous_distance=previous_distance,
                                    baseline_distance=progress_baseline,
                                    window_elapsed_ms=sample["tMs"] - progress_time,
                                    policy=policy,
                                )
                            except (KeyError, TypeError, ValueError, OverflowError):
                                state = "invalid-sample"
                                reason = "invalid-progress-input"
                            else:
                                if progress_state is not None:
                                    state = progress_state
                                    reason = "observed-progress"
                        if (state == "approach-intent" and
                            progress_baseline - distance >= policy["minimumProgressM"]):
                            # Reset the measurement window on qualified *observed*
                            # progress; do not infer velocity from target projection.
                            progress_time = sample["tMs"]
                            progress_baseline = distance
                    if state in ("height-unsafe", "arrived"):
                        reason = "height-or-arrival"
            elif state is not None:
                reason = "safety-guard"

        if state not in terminal_states and state != "approach-intent":
            # Unknown outputs never become a movement intention.
            state = "invalid-sample"
            reason = "unrecognized-worker-state"

        if state in terminal_states:
            terminal = state

        trace.append({
            "index": index,
            "tMs": sample.get("tMs"),
            "state": state,
            "terminal": state in terminal_states,
            "ignoredAfterTerminal": already_terminal,
            "distanceXZ": distance,
            "heightDelta": height,
            "reason": reason,
        })

        # All samples have been syntactically validated by the fixture auditor
        # except the two explicitly invalid test cases.
        value = sample.get("tMs")
        if isinstance(value, int) and not isinstance(value, bool):
            previous_time = value
        if distance is not None and math.isfinite(distance):
            previous_distance = distance

    actual = [entry["state"] for entry in trace]
    expected = case["expectedStates"]
    match = actual == expected and terminal == case["expectedTerminal"]
    return {
        "caseId": case["id"],
        "purpose": case.get("purpose", ""),
        "states": actual,
        "expectedStates": expected,
        "terminalState": terminal,
        "expectedTerminal": case["expectedTerminal"],
        "matchesExpected": match,
        "trace": trace,
    }


def replay(contract: dict[str, Any], suite: dict[str, Any],
           *, contract_hash: str | None = None,
           fixture_hash: str | None = None) -> dict[str, Any]:
    """Replay synthetic trajectories as decisions, never as emitted game inputs."""
    audit = validate_suite(contract, suite)
    if not audit["ok"]:
        return {
            "schemaVersion": SCHEMA_VERSION, "mode": MODE, "ok": False,
            "error": "locked-fixture-audit-failed", "validationErrors": audit["errors"],
            "gameInputSent": False, "commandsIssued": 0,
        }

    # Strong gate in addition to the worker's independent fixture validation.
    source = suite.get("source")
    expected_source = contract.get("source")
    if (source.get("kind") != SOURCE_KIND or
        expected_source.get("kind") != SOURCE_KIND or
        source.get("replayOnly") is not True or
        expected_source.get("replayOnly") is not True or
        suite.get("gameInputAuthorized") is not False):
        return {
            "schemaVersion": SCHEMA_VERSION, "mode": MODE, "ok": False,
            "error": "unqualified-source", "gameInputSent": False,
            "commandsIssued": 0,
        }

    terminal_states = set(contract["terminalStates"])
    cases = [
        _case_result(case, contract["policy"], SOURCE_KIND, terminal_states)
        for case in suite["cases"]
    ]
    passed = sum(bool(case["matchesExpected"]) for case in cases)
    return {
        "schemaVersion": SCHEMA_VERSION,
        "task": "M4A-offline-stationary-target-replay",
        "mode": MODE,
        "inputSource": SOURCE_KIND,
        "fixtureSetId": suite["fixtureSetId"],
        "contractSha256": contract_hash,
        "fixturesSha256": fixture_hash,
        "sourceBuildSha256": contract["exactBuildSha256"],
        "coordinateFrame": "synthetic XZ horizontal / Y vertical",
        "observedInGame": False,
        "nativePathfindingVerified": False,
        "gameInputSent": False,
        "commandsIssued": 0,
        "caseCount": len(cases),
        "totalSamples": sum(len(case["trace"]) for case in cases),
        "passedCases": passed,
        "failedCases": len(cases) - passed,
        "ok": passed == len(cases),
        "cases": cases,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--contract", type=Path,
                        default=ROOT / "docs" / "m4a-offline-target-contract.json")
    parser.add_argument("--fixtures", type=Path,
                        default=ROOT / "docs" / "m4a-offline-target-fixtures.json")
    parser.add_argument("--output", type=Path, help="Optional NEW JSON output under RRE artifacts/ only")
    args = parser.parse_args(argv)

    try:
        contract, contract_sha = _load_object(args.contract)
        suite, suite_sha = _load_object(args.fixtures)
        output = replay(contract, suite, contract_hash=contract_sha,
                        fixture_hash=suite_sha)
        json_text = json.dumps(output, indent=2, sort_keys=True,
                               ensure_ascii=False, allow_nan=False) + "\n"
        if args.output:
            root = (ROOT / "artifacts").resolve()
            target = args.output.resolve()
            if root not in target.parents:
                raise ValueError("Refusing output outside RRE artifacts/")
            target.parent.mkdir(parents=True, exist_ok=True)
            with target.open("x", encoding="utf-8", newline="\n") as destination:
                destination.write(json_text)
        else:
            sys.stdout.write(json_text)
        return 0 if output["ok"] else 1
    except (OSError, ValueError, TypeError, KeyError, json.JSONDecodeError) as exc:
        # A failed preflight never turns into a proposed movement.
        sys.stderr.write(json.dumps({
            "ok": False, "error": type(exc).__name__,
            "reason": str(exc), "mode": MODE,
            "gameInputSent": False, "commandsIssued": 0,
        }, ensure_ascii=False) + "\n")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
