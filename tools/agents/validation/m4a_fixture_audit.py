from typing import Any, Dict, List, Optional, Set, Union
import math


TERMINAL_STATES = frozenset({"arrived", "cancelled", "target-unavailable", "target-changed",
    "scene-changed", "telemetry-stale", "height-unsafe", "no-progress", "moving-away",
    "invalid-sample", "unqualified-source"})
ALLOWED_STATUSES = TERMINAL_STATES | {"approach-intent"}


def validate_suite(contract: Dict[str, Any], corpus: Dict[str, Any]) -> Dict[str, Any]:
    errors: List[str] = []
    intentional_invalid_cases: List[str] = []
    
    if not _validate_contract(contract, errors):
        return {
            "ok": False,
            "errors": errors,
            "intentionalInvalidCases": intentional_invalid_cases,
            "caseCount": 0,
            "sampleCount": 0,
        }
    
    if not _validate_corpus_base(corpus, errors):
        return {
            "ok": False,
            "errors": errors,
            "intentionalInvalidCases": intentional_invalid_cases,
            "caseCount": 0,
            "sampleCount": 0,
        }
    
    cases = corpus.get("cases", [])
    case_count = len(cases)
    sample_count = 0
    
    if case_count < 8:
        errors.append(f"corpus must have at least 8 cases, got {case_count}")
    
    seen_ids: Set[str] = set()
    intentional_invalid_ids = {"invalid-coordinate", "nonmonotonic-time"}
    intentional_invalid_count = 0
    
    for case in cases:
        case_id = case.get("id")
        if not case_id or not isinstance(case_id, str):
            errors.append("case missing nonempty string id")
            continue
        
        if case_id in seen_ids:
            errors.append(f"duplicate case id: {case_id}")
        seen_ids.add(case_id)
        
        samples = case.get("samples", [])
        expected_states = case.get("expectedStates", [])
        expected_terminal = case.get("expectedTerminal")
        
        if case_id in intentional_invalid_ids:
            intentional_invalid_count += 1
            if not _validate_intentional_invalid_case(case, case_id, errors):
                pass
            intentional_invalid_cases.append(case_id)
            sample_count += len(samples) if isinstance(samples, list) else 0
            continue
        
        if not samples or not isinstance(samples, list):
            errors.append(f"case {case_id}: samples must be nonempty list")
            continue
        
        if len(samples) > 40:
            errors.append(f"case {case_id}: samples exceed max 40")
            continue
        
        if not expected_states or not isinstance(expected_states, list):
            errors.append(f"case {case_id}: expectedStates must be nonempty list")
            continue
        
        if len(expected_states) != len(samples):
            errors.append(f"case {case_id}: expectedStates length {len(expected_states)} != samples length {len(samples)}")
            continue
        
        if expected_terminal not in TERMINAL_STATES:
            errors.append(f"case {case_id}: expectedTerminal must be one of {TERMINAL_STATES}, got {expected_terminal}")
            continue
        
        if expected_terminal not in expected_states:
            errors.append(f"case {case_id}: expectedTerminal '{expected_terminal}' not found in expectedStates")
            continue
        
        sample_count += len(samples)
        _validate_samples(case_id, samples, expected_states, errors)
    
    if intentional_invalid_count > 2:
        errors.append(f"too many intentional invalid cases: {intentional_invalid_count}, max 2")
    elif intentional_invalid_count < 2:
        errors.append(f"expected exactly 2 intentional invalid cases, got {intentional_invalid_count}")
    
    ok = len(errors) == 0
    return {
        "ok": ok,
        "errors": errors,
        "intentionalInvalidCases": intentional_invalid_cases,
        "caseCount": case_count,
        "sampleCount": sample_count,
    }


def _validate_contract(contract: Dict[str, Any], errors: List[str]) -> bool:
    ok = True
    if contract.get("schemaVersion") != 1:
        errors.append("contract schemaVersion must be 1")
        ok = False
    if contract.get("taskId") != "M4A-001":
        errors.append("contract taskId must be M4A-001")
        ok = False
    if contract.get("runMode") != "offline-replay-only":
        errors.append("contract runMode must be offline-replay-only")
        ok = False
    declared_states = contract.get("stateVocabulary")
    declared_terminal = contract.get("terminalStates")
    if declared_states is not None and (not isinstance(declared_states, list) or
                                        set(declared_states) != ALLOWED_STATUSES):
        errors.append("contract stateVocabulary differs from the locked M4A status contract")
        ok = False
    if declared_terminal is not None and (not isinstance(declared_terminal, list) or
                                          set(declared_terminal) != TERMINAL_STATES):
        errors.append("contract terminalStates differs from the locked M4A terminal codes")
        ok = False
    source = contract.get("source", {})
    if source.get("kind") != "synthetic-fixture":
        errors.append("contract source.kind must be synthetic-fixture")
        ok = False
    if source.get("replayOnly") is not True:
        errors.append("contract source.replayOnly must be true")
        ok = False
    return ok


def _validate_corpus_base(corpus: Dict[str, Any], errors: List[str]) -> bool:
    ok = True
    if corpus.get("schemaVersion") != 1:
        errors.append("corpus schemaVersion must be 1")
        ok = False
    if corpus.get("taskId") != "M4A-001":
        errors.append("corpus taskId must be M4A-001")
        ok = False
    source = corpus.get("source", {})
    if source.get("kind") != "synthetic-fixture":
        errors.append("corpus source.kind must be synthetic-fixture")
        ok = False
    if source.get("replayOnly") is not True:
        errors.append("corpus source.replayOnly must be true")
        ok = False
    if corpus.get("notRuntimeEvidence") is not True:
        errors.append("corpus notRuntimeEvidence must be true")
        ok = False
    if corpus.get("gameInputAuthorized") is not False:
        errors.append("corpus gameInputAuthorized must be false")
        ok = False
    return ok


def _validate_intentional_invalid_case(case: Dict[str, Any], case_id: str, errors: List[str]) -> bool:
    samples = case.get("samples", [])
    expected_states = case.get("expectedStates", [])
    expected_terminal = case.get("expectedTerminal")
    
    if expected_terminal != "invalid-sample":
        errors.append(f"intentional invalid case {case_id}: expectedTerminal must be 'invalid-sample'")
        return False
    
    if case_id == "invalid-coordinate":
        return _validate_invalid_coordinate(case, errors)
    elif case_id == "nonmonotonic-time":
        return _validate_nonmonotonic_time(case, errors)
    return False


def _validate_invalid_coordinate(case: Dict[str, Any], errors: List[str]) -> bool:
    samples = case.get("samples", [])
    expected_states = case.get("expectedStates", [])
    
    bad_index = -1
    for i, sample in enumerate(samples):
        player = sample.get("player", {})
        x = player.get("x")
        if not isinstance(x, (int, float)) or isinstance(x, bool) or not math.isfinite(x):
            bad_index = i
            break
    
    if bad_index == -1:
        errors.append("invalid-coordinate: no sample with nonnumeric player x found")
        return False
    
    if bad_index >= len(expected_states) or expected_states[bad_index] != "invalid-sample":
        errors.append(f"invalid-coordinate: expectedStates[{bad_index}] must be 'invalid-sample'")
        return False
    
    return True


def _validate_nonmonotonic_time(case: Dict[str, Any], errors: List[str]) -> bool:
    samples = case.get("samples", [])
    expected_states = case.get("expectedStates", [])
    
    if len(samples) < 2:
        errors.append("nonmonotonic-time: needs at least 2 samples")
        return False
    
    bad_index = -1
    for i in range(1, len(samples)):
        t_prev = samples[i-1].get("tMs")
        t_curr = samples[i].get("tMs")
        if not isinstance(t_prev, int) or isinstance(t_prev, bool) or t_prev < 0:
            continue
        if not isinstance(t_curr, int) or isinstance(t_curr, bool) or t_curr < 0:
            continue
        if t_curr <= t_prev:
            bad_index = i
            break
    
    if bad_index == -1:
        errors.append("nonmonotonic-time: no duplicate/rewind sample time found")
        return False
    
    if bad_index >= len(expected_states) or expected_states[bad_index] != "invalid-sample":
        errors.append(f"nonmonotonic-time: expectedStates[{bad_index}] must be 'invalid-sample'")
        return False
    
    return True


def _validate_samples(case_id: str, samples: List[Dict], expected_states: List[str], errors: List[str]) -> None:
    seen_target_ids: Dict[str, int] = {}
    seen_scene_ids: Dict[str, int] = {}
    
    for i, sample in enumerate(samples):
        state = expected_states[i]
        
        if state not in ALLOWED_STATUSES:
            errors.append(f"case {case_id} sample {i}: unknown status '{state}'")
            continue
        
        t_ms = sample.get("tMs")
        if not isinstance(t_ms, int) or isinstance(t_ms, bool) or t_ms < 0:
            errors.append(f"case {case_id} sample {i}: tMs must be nonnegative int, got {t_ms}")
        
        scene_id = sample.get("sceneId")
        if not scene_id or not isinstance(scene_id, str):
            errors.append(f"case {case_id} sample {i}: sceneId must be nonempty string")
        
        player = sample.get("player")
        if not _validate_player(player, case_id, i, errors):
            pass
        
        target = sample.get("target")
        if target is not None:
            if not _validate_target(target, case_id, i, errors):
                pass
            else:
                target_id = target.get("id")
                if target_id and target_id in seen_target_ids:
                    prev_i = seen_target_ids[target_id]
                    if state == "target-changed" and expected_states[prev_i] != "target-changed":
                        pass
                seen_target_ids[target_id] = i
        
        cancel_requested = sample.get("cancelRequested")
        if not isinstance(cancel_requested, bool):
            errors.append(f"case {case_id} sample {i}: cancelRequested must be bool")
        
        if scene_id and scene_id in seen_scene_ids:
            prev_i = seen_scene_ids[scene_id]
            if state == "scene-changed" and expected_states[prev_i] != "scene-changed":
                pass
        if scene_id:
            seen_scene_ids[scene_id] = i


def _validate_player(player: Any, case_id: str, sample_idx: int, errors: List[str]) -> bool:
    if not isinstance(player, dict):
        errors.append(f"case {case_id} sample {sample_idx}: player must be dict")
        return False
    for coord in ("x", "y", "z"):
        val = player.get(coord)
        if not isinstance(val, (int, float)) or isinstance(val, bool) or not math.isfinite(val):
            errors.append(f"case {case_id} sample {sample_idx}: player.{coord} must be finite numeric, got {val}")
            return False
    return True


def _validate_target(target: Any, case_id: str, sample_idx: int, errors: List[str]) -> bool:
    if not isinstance(target, dict):
        errors.append(f"case {case_id} sample {sample_idx}: target must be dict or None")
        return False
    target_id = target.get("id")
    if not target_id or not isinstance(target_id, str):
        errors.append(f"case {case_id} sample {sample_idx}: target.id must be nonempty string")
        return False
    for coord in ("x", "y", "z"):
        val = target.get(coord)
        if not isinstance(val, (int, float)) or isinstance(val, bool) or not math.isfinite(val):
            errors.append(f"case {case_id} sample {sample_idx}: target.{coord} must be finite numeric, got {val}")
            return False
    return True


if __name__ == "__main__":
    import sys
    import json
    
    if len(sys.argv) >= 3:
        fixture_path = sys.argv[1]
        contract_path = sys.argv[2]
        with open(fixture_path, "r") as f:
            corpus = json.load(f)
        with open(contract_path, "r") as f:
            contract = json.load(f)
        result = validate_suite(contract, corpus)
        print(json.dumps(result, indent=2))
        sys.exit(0 if result["ok"] else 1)
    else:
        print("Usage: python m4a_fixture_audit.py <fixture.json> <contract.json>")
        sys.exit(2)