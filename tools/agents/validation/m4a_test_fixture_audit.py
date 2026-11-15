import unittest
import json
from m4a_fixture_audit import validate_suite, ALLOWED_STATUSES, TERMINAL_STATES


def make_valid_contract():
    return {
        "schemaVersion": 1,
        "taskId": "M4A-001",
        "runMode": "offline-replay-only",
        "exactBuildSha256": "a" * 64,
        "stateVocabulary": sorted(ALLOWED_STATUSES),
        "terminalStates": sorted(TERMINAL_STATES),
        "policy": {"arrivalRadiusM": 1.5, "maximumVerticalDifferenceM": 2,
                   "staleAfterGapMs": 1200, "progressWindowMs": 1500,
                   "minimumProgressM": 0.25, "movingAwayToleranceM": 0.75,
                   "numericTolerance": 1e-9},
        "source": {
            "kind": "synthetic-fixture",
            "replayOnly": True
        }
    }


def make_valid_corpus_base():
    return {
        "schemaVersion": 1,
        "taskId": "M4A-001",
        "fixtureSetId": "rre-m4a-synthetic-test-v1",
        "source": {
            "kind": "synthetic-fixture",
            "replayOnly": True
        },
        "notRuntimeEvidence": True,
        "gameInputAuthorized": False,
        "cases": []
    }


def make_valid_sample(t_ms: int, scene_id: str, player_x: float, player_y: float, player_z: float,
                       target_id: str = None, target_x: float = 0, target_y: float = 0, target_z: float = 0,
                       cancel_requested: bool = False) -> dict:
    sample = {
        "tMs": t_ms,
        "sceneId": scene_id,
        "player": {"x": player_x, "y": player_y, "z": player_z},
        "cancelRequested": cancel_requested
    }
    if target_id is not None:
        sample["target"] = {"id": target_id, "x": target_x, "y": target_y, "z": target_z}
    else:
        sample["target"] = None
    return sample


def make_valid_case(case_id: str, samples: list, expected_states: list, expected_terminal: str) -> dict:
    return {
        "id": case_id,
        "samples": samples,
        "expectedStates": expected_states,
        "expectedTerminal": expected_terminal
    }


def make_invalid_coordinate_case():
    samples = [
        make_valid_sample(0, "s", 0, 0, 0),
        make_valid_sample(100, "s", "bad", 0, 0),
        make_valid_sample(200, "s", 2, 0, 0),
    ]
    expected = ["arrived", "invalid-sample", "arrived"]
    return make_valid_case("invalid-coordinate", samples, expected, "invalid-sample")


def make_nonmonotonic_time_case():
    samples = [
        make_valid_sample(0, "s", 0, 0, 0),
        make_valid_sample(100, "s", 1, 0, 0),
        make_valid_sample(50, "s", 2, 0, 0),
    ]
    expected = ["arrived", "arrived", "invalid-sample"]
    return make_valid_case("nonmonotonic-time", samples, expected, "invalid-sample")


def make_simple_valid_case(case_id: str, num_samples: int = 3):
    samples = [make_valid_sample(i * 100, f"scene{case_id}", 0.0, 0.0, 0.0) for i in range(num_samples)]
    expected = ["arrived"] * num_samples
    return make_valid_case(case_id, samples, expected, "arrived")


def make_corpus_with_intentional_invalids(extra_cases=None):
    """Create a corpus with the two required intentional invalid cases plus optional extra cases."""
    corpus = make_valid_corpus_base()
    cases = [make_invalid_coordinate_case(), make_nonmonotonic_time_case()]
    if extra_cases:
        cases.extend(extra_cases)
    corpus["cases"] = cases
    return corpus


class TestM4AFixtureAudit(unittest.TestCase):
    
    def test_valid_minimal_corpus(self):
        contract = make_valid_contract()
        extra = [make_simple_valid_case(f"case{i}") for i in range(6)]
        corpus = make_corpus_with_intentional_invalids(extra)
        result = validate_suite(contract, corpus)
        self.assertTrue(result["ok"], msg=result["errors"])
        self.assertEqual(result["caseCount"], 8)
        self.assertEqual(result["sampleCount"], 24)
        self.assertEqual(len(result["intentionalInvalidCases"]), 2)
        self.assertIn("invalid-coordinate", result["intentionalInvalidCases"])
        self.assertIn("nonmonotonic-time", result["intentionalInvalidCases"])
    
    def test_missing_replay_required_fields_are_rejected(self):
        corpus = make_corpus_with_intentional_invalids([make_simple_valid_case(f"c{i}") for i in range(6)])
        for key in ("terminalStates", "stateVocabulary", "exactBuildSha256", "policy"):
            with self.subTest(contractMissing=key):
                contract = make_valid_contract()
                del contract[key]
                result = validate_suite(contract, corpus)
                self.assertFalse(result["ok"])
                self.assertIn("contract " + key, " ".join(result["errors"]))
        del corpus["fixtureSetId"]
        result = validate_suite(make_valid_contract(), corpus)
        self.assertFalse(result["ok"])
        self.assertIn("corpus fixtureSetId", " ".join(result["errors"]))

    def test_malformed_replay_contract_fields_are_rejected_without_exceptions(self):
        corpus = make_corpus_with_intentional_invalids([make_simple_valid_case(f"c{i}") for i in range(6)])
        bad_values = (("terminalStates", ["arrived", "arrived"]),
                      ("stateVocabulary", ["arrived", {}]),
                      ("exactBuildSha256", "g" * 64),
                      ("policy", {"arrivalRadiusM": -1}),
                      ("source", "invalid"))
        for key, invalid in bad_values:
            with self.subTest(contractKey=key):
                contract = make_valid_contract()
                contract[key] = invalid
                self.assertFalse(validate_suite(contract, corpus)["ok"])
        corpus["fixtureSetId"] = []
        self.assertFalse(validate_suite(make_valid_contract(), corpus)["ok"])

    def test_contract_wrong_schema_version(self):
        contract = make_valid_contract()
        contract["schemaVersion"] = 2
        corpus = make_corpus_with_intentional_invalids([make_simple_valid_case(f"c{i}") for i in range(6)])
        result = validate_suite(contract, corpus)
        self.assertFalse(result["ok"])
        self.assertIn("contract schemaVersion must be 1", result["errors"])
    
    def test_contract_wrong_task_id(self):
        contract = make_valid_contract()
        contract["taskId"] = "M4A-999"
        corpus = make_corpus_with_intentional_invalids([make_simple_valid_case(f"c{i}") for i in range(6)])
        result = validate_suite(contract, corpus)
        self.assertFalse(result["ok"])
        self.assertIn("contract taskId must be M4A-001", result["errors"])
    
    def test_contract_live_source_rejected(self):
        contract = make_valid_contract()
        contract["source"]["kind"] = "live-game"
        corpus = make_corpus_with_intentional_invalids([make_simple_valid_case(f"c{i}") for i in range(6)])
        result = validate_suite(contract, corpus)
        self.assertFalse(result["ok"])
        self.assertIn("contract source.kind must be synthetic-fixture", result["errors"])
    
    def test_corpus_wrong_schema_version(self):
        contract = make_valid_contract()
        corpus = make_corpus_with_intentional_invalids([make_simple_valid_case(f"c{i}") for i in range(6)])
        corpus["schemaVersion"] = 2
        result = validate_suite(contract, corpus)
        self.assertFalse(result["ok"])
        self.assertIn("corpus schemaVersion must be 1", result["errors"])
    
    def test_corpus_not_runtime_evidence_false(self):
        contract = make_valid_contract()
        corpus = make_corpus_with_intentional_invalids([make_simple_valid_case(f"c{i}") for i in range(6)])
        corpus["notRuntimeEvidence"] = False
        result = validate_suite(contract, corpus)
        self.assertFalse(result["ok"])
        self.assertIn("corpus notRuntimeEvidence must be true", result["errors"])
    
    def test_corpus_game_input_authorized_true(self):
        contract = make_valid_contract()
        corpus = make_corpus_with_intentional_invalids([make_simple_valid_case(f"c{i}") for i in range(6)])
        corpus["gameInputAuthorized"] = True
        result = validate_suite(contract, corpus)
        self.assertFalse(result["ok"])
        self.assertIn("corpus gameInputAuthorized must be false", result["errors"])
    
    def test_corpus_less_than_8_cases(self):
        contract = make_valid_contract()
        corpus = make_valid_corpus_base()
        corpus["cases"] = [make_simple_valid_case(f"c{i}") for i in range(5)]
        result = validate_suite(contract, corpus)
        self.assertFalse(result["ok"])
        self.assertIn("at least 8 cases", result["errors"][0])
    
    def test_duplicate_case_ids(self):
        contract = make_valid_contract()
        corpus = make_valid_corpus_base()
        base = make_simple_valid_case("dup")
        corpus["cases"] = [base] * 8
        result = validate_suite(contract, corpus)
        self.assertFalse(result["ok"])
        self.assertIn("duplicate case id: dup", result["errors"])
    
    def test_empty_case_id(self):
        contract = make_valid_contract()
        corpus = make_valid_corpus_base()
        base = make_valid_case("", [make_valid_sample(0, "s", 0, 0, 0)], ["arrived"], "arrived")
        corpus["cases"] = [base] * 8
        result = validate_suite(contract, corpus)
        self.assertFalse(result["ok"])
        self.assertIn("case missing nonempty string id", result["errors"])
    
    def test_samples_empty(self):
        contract = make_valid_contract()
        corpus = make_valid_corpus_base()
        case = make_valid_case("c1", [], ["arrived"], "arrived")
        corpus["cases"] = [case] * 8
        result = validate_suite(contract, corpus)
        self.assertFalse(result["ok"])
        self.assertIn("samples must be nonempty list", result["errors"][0])
    
    def test_samples_exceed_max_40(self):
        contract = make_valid_contract()
        corpus = make_valid_corpus_base()
        samples = [make_valid_sample(i, "s", 0, 0, 0) for i in range(41)]
        case = make_valid_case("c1", samples, ["arrived"] * 41, "arrived")
        corpus["cases"] = [case] * 8
        result = validate_suite(contract, corpus)
        self.assertFalse(result["ok"])
        self.assertIn("samples exceed max 40", result["errors"][0])
    
    def test_expected_states_length_mismatch(self):
        contract = make_valid_contract()
        corpus = make_valid_corpus_base()
        case = make_valid_case("c1", [make_valid_sample(0, "s", 0, 0, 0)] * 3, ["arrived", "arrived"], "arrived")
        corpus["cases"] = [case] * 8
        result = validate_suite(contract, corpus)
        self.assertFalse(result["ok"])
        self.assertIn("expectedStates length", result["errors"][0])
    
    def test_expected_terminal_not_in_terminal_states(self):
        contract = make_valid_contract()
        corpus = make_valid_corpus_base()
        case = make_valid_case("c1", [make_valid_sample(0, "s", 0, 0, 0)], ["arrived"], "flying")
        corpus["cases"] = [case] * 8
        result = validate_suite(contract, corpus)
        self.assertFalse(result["ok"])
        self.assertIn("expectedTerminal must be one of", result["errors"][0])
    
    def test_expected_terminal_not_in_expected_states(self):
        contract = make_valid_contract()
        corpus = make_valid_corpus_base()
        case = make_valid_case("c1", [make_valid_sample(0, "s", 0, 0, 0)] * 3, ["arrived", "arrived", "blocked"], "cancelled")
        corpus["cases"] = [case] * 8
        result = validate_suite(contract, corpus)
        self.assertFalse(result["ok"])
        self.assertIn("expectedTerminal 'cancelled' not found in expectedStates", result["errors"][0])
    
    def test_negative_tMs(self):
        contract = make_valid_contract()
        corpus = make_corpus_with_intentional_invalids([make_simple_valid_case(f"c{i}") for i in range(6)])
        samples = [make_valid_sample(-1, "s", 0, 0, 0), make_valid_sample(100, "s", 0, 0, 0)]
        case = make_valid_case("c1", samples, ["arrived", "arrived"], "arrived")
        corpus["cases"][2] = case
        result = validate_suite(contract, corpus)
        self.assertFalse(result["ok"])
        self.assertIn("tMs must be nonnegative int", result["errors"][0])
    
    def test_tMs_is_bool(self):
        contract = make_valid_contract()
        corpus = make_corpus_with_intentional_invalids([make_simple_valid_case(f"c{i}") for i in range(6)])
        samples = [make_valid_sample(0, "s", 0, 0, 0)]
        samples[0]["tMs"] = True
        case = make_valid_case("c1", samples, ["arrived"], "arrived")
        corpus["cases"][2] = case
        result = validate_suite(contract, corpus)
        self.assertFalse(result["ok"])
        self.assertIn("tMs must be nonnegative int", result["errors"][0])
    
    def test_player_non_numeric_x(self):
        contract = make_valid_contract()
        corpus = make_corpus_with_intentional_invalids([make_simple_valid_case(f"c{i}") for i in range(6)])
        samples = [make_valid_sample(0, "s", 0, 0, 0)]
        samples[0]["player"]["x"] = "not-a-number"
        case = make_valid_case("c1", samples, ["arrived"], "arrived")
        corpus["cases"][2] = case
        result = validate_suite(contract, corpus)
        self.assertFalse(result["ok"])
        self.assertIn("player.x must be finite numeric", result["errors"][0])
    
    def test_player_bool_coordinate(self):
        contract = make_valid_contract()
        corpus = make_corpus_with_intentional_invalids([make_simple_valid_case(f"c{i}") for i in range(6)])
        samples = [make_valid_sample(0, "s", 0, 0, 0)]
        samples[0]["player"]["x"] = True
        case = make_valid_case("c1", samples, ["arrived"], "arrived")
        corpus["cases"][2] = case
        result = validate_suite(contract, corpus)
        self.assertFalse(result["ok"])
        self.assertIn("player.x must be finite numeric", result["errors"][0])
    
    def test_player_infinite_coordinate(self):
        contract = make_valid_contract()
        corpus = make_corpus_with_intentional_invalids([make_simple_valid_case(f"c{i}") for i in range(6)])
        samples = [make_valid_sample(0, "s", float('inf'), 0, 0)]
        case = make_valid_case("c1", samples, ["arrived"], "arrived")
        corpus["cases"][2] = case
        result = validate_suite(contract, corpus)
        self.assertFalse(result["ok"])
        self.assertIn("player.x must be finite numeric", result["errors"][0])
    
    def test_target_none_allowed(self):
        contract = make_valid_contract()
        corpus = make_corpus_with_intentional_invalids([make_simple_valid_case(f"c{i}") for i in range(5)])
        samples = [make_valid_sample(0, "s", 0, 0, 0, target_id=None)]
        case = make_valid_case("target-none", samples, ["arrived"], "arrived")
        corpus["cases"].append(case)
        result = validate_suite(contract, corpus)
        self.assertTrue(result["ok"], msg=result["errors"])
    
    def test_target_missing_id(self):
        contract = make_valid_contract()
        corpus = make_corpus_with_intentional_invalids([make_simple_valid_case(f"c{i}") for i in range(6)])
        samples = [make_valid_sample(0, "s", 0, 0, 0)]
        samples[0]["target"] = {"x": 1, "y": 2, "z": 3}
        case = make_valid_case("c1", samples, ["arrived"], "arrived")
        corpus["cases"][2] = case
        result = validate_suite(contract, corpus)
        self.assertFalse(result["ok"])
        self.assertIn("target.id must be nonempty string", result["errors"][0])
    
    def test_target_non_numeric_coordinate(self):
        contract = make_valid_contract()
        corpus = make_corpus_with_intentional_invalids([make_simple_valid_case(f"c{i}") for i in range(6)])
        samples = [make_valid_sample(0, "s", 0, 0, 0, target_id="t1", target_x="bad")]
        case = make_valid_case("c1", samples, ["arrived"], "arrived")
        corpus["cases"][2] = case
        result = validate_suite(contract, corpus)
        self.assertFalse(result["ok"])
        self.assertIn("target.x must be finite numeric", result["errors"][0])
    
    def test_unknown_status_code(self):
        contract = make_valid_contract()
        corpus = make_corpus_with_intentional_invalids([make_simple_valid_case(f"c{i}") for i in range(6)])
        samples = [make_valid_sample(0, "s", 0, 0, 0), make_valid_sample(100, "s", 0, 0, 0)]
        case = make_valid_case("c1", samples, ["arrived", "teleported"], "arrived")
        corpus["cases"][2] = case
        result = validate_suite(contract, corpus)
        self.assertFalse(result["ok"])
        self.assertIn("unknown status 'teleported'", result["errors"][0])
    
    def test_cancel_requested_not_bool(self):
        contract = make_valid_contract()
        corpus = make_corpus_with_intentional_invalids([make_simple_valid_case(f"c{i}") for i in range(6)])
        samples = [make_valid_sample(0, "s", 0, 0, 0)]
        samples[0]["cancelRequested"] = "yes"
        case = make_valid_case("c1", samples, ["arrived"], "arrived")
        corpus["cases"][2] = case
        result = validate_suite(contract, corpus)
        self.assertFalse(result["ok"])
        self.assertIn("cancelRequested must be bool", result["errors"][0])
    
    def test_target_changed_valid(self):
        contract = make_valid_contract()
        extra = [make_simple_valid_case(f"c{i}") for i in range(5)]
        samples = [
            make_valid_sample(0, "s", 0, 0, 0, target_id="t1"),
            make_valid_sample(100, "s", 1, 0, 0, target_id="t2"),
            make_valid_sample(200, "s", 2, 0, 0, target_id="t2"),
        ]
        expected = ["arrived", "target-changed", "arrived"]
        case = make_valid_case("target-changed", samples, expected, "arrived")
        corpus = make_corpus_with_intentional_invalids(extra + [case])
        result = validate_suite(contract, corpus)
        self.assertTrue(result["ok"], msg=result["errors"])
    
    def test_scene_changed_valid(self):
        contract = make_valid_contract()
        extra = [make_simple_valid_case(f"c{i}") for i in range(5)]
        samples = [
            make_valid_sample(0, "scene1", 0, 0, 0),
            make_valid_sample(100, "scene2", 1, 0, 0),
            make_valid_sample(200, "scene2", 2, 0, 0),
        ]
        expected = ["arrived", "scene-changed", "arrived"]
        case = make_valid_case("scene-changed", samples, expected, "arrived")
        corpus = make_corpus_with_intentional_invalids(extra + [case])
        result = validate_suite(contract, corpus)
        self.assertTrue(result["ok"], msg=result["errors"])
    
    def test_terminal_latched_arrived_repeat(self):
        contract = make_valid_contract()
        extra = [make_simple_valid_case(f"c{i}") for i in range(5)]
        samples = [
            make_valid_sample(0, "s", 0, 0, 0),
            make_valid_sample(100, "s", 1, 0, 0),
            make_valid_sample(200, "s", 2, 0, 0),
        ]
        expected = ["arrived", "arrived", "arrived"]
        case = make_valid_case("latched", samples, expected, "arrived")
        corpus = make_corpus_with_intentional_invalids(extra + [case])
        result = validate_suite(contract, corpus)
        self.assertTrue(result["ok"], msg=result["errors"])
    
    def test_intentional_invalid_coordinate_accepted(self):
        contract = make_valid_contract()
        extra = [make_simple_valid_case(f"c{i}") for i in range(6)]
        corpus = make_corpus_with_intentional_invalids(extra)
        result = validate_suite(contract, corpus)
        self.assertTrue(result["ok"], msg=result["errors"])
        self.assertIn("invalid-coordinate", result["intentionalInvalidCases"])
    
    def test_intentional_nonmonotonic_time_accepted(self):
        contract = make_valid_contract()
        extra = [make_simple_valid_case(f"c{i}") for i in range(6)]
        corpus = make_corpus_with_intentional_invalids(extra)
        result = validate_suite(contract, corpus)
        self.assertTrue(result["ok"], msg=result["errors"])
        self.assertIn("nonmonotonic-time", result["intentionalInvalidCases"])
    
    def test_intentional_invalid_wrong_expected_terminal(self):
        contract = make_valid_contract()
        corpus = make_valid_corpus_base()
        
        samples = [
            make_valid_sample(0, "s", 0, 0, 0),
            make_valid_sample(100, "s", "bad", 0, 0),
        ]
        expected = ["arrived", "invalid-sample"]
        invalid_case = make_valid_case("invalid-coordinate", samples, expected, "arrived")
        
        other_cases = [make_simple_valid_case(f"c{i}") for i in range(6)]
        other_cases.append(make_nonmonotonic_time_case())
        corpus["cases"] = [invalid_case] + other_cases
        result = validate_suite(contract, corpus)
        self.assertFalse(result["ok"])
        self.assertIn("expectedTerminal must be 'invalid-sample'", result["errors"][0])
    
    def test_intentional_invalid_missing_bad_sample(self):
        contract = make_valid_contract()
        corpus = make_valid_corpus_base()
        
        samples = [
            make_valid_sample(0, "s", 0, 0, 0),
            make_valid_sample(100, "s", 1, 0, 0),
        ]
        expected = ["arrived", "invalid-sample"]
        invalid_case = make_valid_case("invalid-coordinate", samples, expected, "invalid-sample")
        
        other_cases = [make_simple_valid_case(f"c{i}") for i in range(6)]
        other_cases.append(make_nonmonotonic_time_case())
        corpus["cases"] = [invalid_case] + other_cases
        result = validate_suite(contract, corpus)
        self.assertFalse(result["ok"])
        self.assertIn("no sample with nonnumeric player x found", result["errors"][0])
    
    def test_too_many_intentional_invalid_cases(self):
        contract = make_valid_contract()
        corpus = make_valid_corpus_base()
        
        samples1 = [
            make_valid_sample(0, "s", 0, 0, 0),
            make_valid_sample(100, "s", "bad", 0, 0),
        ]
        expected1 = ["arrived", "invalid-sample"]
        invalid1 = make_valid_case("invalid-coordinate", samples1, expected1, "invalid-sample")
        
        samples2 = [
            make_valid_sample(0, "s", 0, 0, 0),
            make_valid_sample(100, "s", 1, 0, 0),
            make_valid_sample(50, "s", 2, 0, 0),
        ]
        expected2 = ["arrived", "arrived", "invalid-sample"]
        invalid2 = make_valid_case("nonmonotonic-time", samples2, expected2, "invalid-sample")
        
        samples3 = [
            make_valid_sample(0, "s", 0, 0, 0),
            make_valid_sample(100, "s", "bad", 0, 0),
            make_valid_sample(200, "s", 2, 0, 0),
        ]
        expected3 = ["arrived", "invalid-sample", "arrived"]
        invalid3 = make_valid_case("invalid-coordinate", samples3, expected3, "invalid-sample")
        
        other_cases = [make_simple_valid_case(f"c{i}") for i in range(5)]
        corpus["cases"] = [invalid1, invalid2, invalid3] + other_cases
        result = validate_suite(contract, corpus)
        self.assertFalse(result["ok"])
        self.assertIn("too many intentional invalid cases", " ".join(result["errors"]))
    
    def test_too_few_intentional_invalid_cases(self):
        contract = make_valid_contract()
        corpus = make_valid_corpus_base()
        
        samples1 = [
            make_valid_sample(0, "s", 0, 0, 0),
            make_valid_sample(100, "s", "bad", 0, 0),
        ]
        expected1 = ["arrived", "invalid-sample"]
        invalid1 = make_valid_case("invalid-coordinate", samples1, expected1, "invalid-sample")
        
        other_cases = [make_simple_valid_case(f"c{i}") for i in range(7)]
        corpus["cases"] = [invalid1] + other_cases
        result = validate_suite(contract, corpus)
        self.assertFalse(result["ok"])
        self.assertIn("expected exactly 2 intentional invalid cases", result["errors"][0])


class TestLockedRreM4ACorpus(unittest.TestCase):
    """Independent regression against Manager-locked, read-only actual fixture files."""

    def test_real_thirteen_fixture_cases(self):
        from pathlib import Path
        import json
        docs = Path(r"C:\work\rre\docs")
        contract = json.loads((docs / "m4a-offline-target-contract.json").read_text(encoding="utf-8"))
        corpus = json.loads((docs / "m4a-offline-target-fixtures.json").read_text(encoding="utf-8"))
        result = validate_suite(contract, corpus)
        self.assertTrue(result["ok"], msg=result["errors"])
        self.assertEqual(result["caseCount"], 13)
        self.assertEqual(result["sampleCount"], 24)
        self.assertEqual(set(result["intentionalInvalidCases"]),
                         {"invalid-coordinate", "nonmonotonic-time"})

    def test_wrong_contract_status_vocabulary_rejected(self):
        contract = make_valid_contract()
        contract["stateVocabulary"] = ["arrived", "blocked"]
        corpus = make_corpus_with_intentional_invalids(
            [make_simple_valid_case(f"c{i}") for i in range(6)]
        )
        result = validate_suite(contract, corpus)
        self.assertFalse(result["ok"])
        self.assertTrue(any("stateVocabulary" in e for e in result["errors"]))


if __name__ == "__main__":
    unittest.main()