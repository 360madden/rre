"""Portable tests for the file-only consumer; no game or native memory access."""
from __future__ import annotations
import ast
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[3]
SPEC = importlib.util.spec_from_file_location("world_inspector", ROOT / "tools/world-inspector.py")
assert SPEC and SPEC.loader
M = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(M)
SHA = "a" * 64


def actor(key="u-player", name="Example", xyz=(0, 0, 0), player=True):
    return {"id": key, "name": name, "player": player, "zone": "test-zone",
            "coord": dict(zip("xyz", xyz)) if xyz is not None else None}


def snapshot():
    return {"schemaVersion": 1, "sourceMode": "SyntheticFixture", "playerId": "u-player",
            "player": actor(), "target": None, "nearbyUnits": None, "partyUnits": None}


def camera():
    return {"schemaVersion": 1, "sourceSha256": SHA, "evidenceKind": "synthetic",
            "convention": M.CONVENTION,
            "viewProjection": [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1],
            "viewport": {"x": 10, "y": 20, "width": 800, "height": 600}}


def receipt():
    obs = {"schemaVersion": 1, "addonVersion": "0.1.0", "sequence": 2, "epoch": 1,
           "player": {"status": "ok", "value": "u-player"},
           "fields": {"coord" + axis: {"status": "ok", "value": n}
                      for axis, n in zip("XYZ", [1, 2, 3])}}
    return {"schemaVersion": 1, "receivedAtUtc": "2026-10-19T01:00:00Z",
            "observation": {"schemaVersion": 1, "capturedAtUtc": "2026-10-19T00:59:59Z",
                            "target": {"processId": 123, "processStartUtcTicks": 639279712871697793,
                                       "executableSha256": SHA},
                            "riftReader2": {"schemaVersion": 1, "bindingStatus": "bound",
                                            "freshnessStatus": "fresh", "observation": obs}}}


class EntityTests(unittest.TestCase):
    def inspect(self, data=None, cam=None):
        return M.inspect_data(data or snapshot(), "readerbridge", SHA, cam)

    def test_self_target_is_one_entity_two_roles(self):
        x = snapshot(); x["targetId"] = "u-player"; x["target"] = copy.deepcopy(x["player"])
        r = self.inspect(x)
        self.assertEqual(r["counts"]["distinctIds"], 1)
        self.assertEqual(r["entities"][0]["roles"], ["local-player", "selected-target"])

    def test_same_name_and_position_different_ids_stay_distinct(self):
        x = snapshot(); x["nearbyUnits"] = [actor("u-other")]
        self.assertEqual(self.inspect(x)["counts"]["distinctIds"], 2)

    def test_same_id_different_positions_not_drawn(self):
        x = snapshot(); x["partyUnits"] = [actor(xyz=(1, 0, 0))]
        row = self.inspect(x)["entities"][0]
        self.assertIn("position", row["conflicts"])
        self.assertIsNone(row["position"])
        self.assertEqual(len(row["observations"]), 2)

    def test_name_zone_and_kind_conflicts_suppress_position(self):
        for field, value in (("name", "Other"), ("zone", "elsewhere"), ("player", False)):
            with self.subTest(field=field):
                x = snapshot(); duplicate = actor(); duplicate[field] = value
                x["partyUnits"] = [duplicate]
                self.assertIsNone(self.inspect(x)["entities"][0]["position"])

    def test_missing_position_is_not_origin(self):
        x = snapshot(); x["player"]["coord"] = None
        self.assertIsNone(self.inspect(x)["entities"][0]["position"])

    def test_partial_position_rejected(self):
        x = snapshot(); del x["player"]["coord"]["z"]
        with self.assertRaisesRegex(ValueError, "partial"):
            self.inspect(x)

    def test_unavailable_different_from_reported_empty(self):
        x = snapshot()
        self.assertEqual(self.inspect(x)["coverage"]["nearbyUnits"], "unavailable-or-empty")
        x["nearbyUnits"] = []
        self.assertEqual(self.inspect(x)["coverage"]["nearbyUnits"], "reported-empty-scope-unverified")

    def test_nonempty_never_exhaustive(self):
        x = snapshot(); x["nearbyUnits"] = [actor("u-other")]
        self.assertEqual(self.inspect(x)["coverage"]["nearbyUnits"], "partial-reported")

    def test_no_source_claim_enables_live_or_navigation(self):
        x = snapshot(); x.update(sourceMode="DirectAPI", live=True, freshness="fresh")
        r = self.inspect(x)
        self.assertFalse(r["live"])
        self.assertEqual(r["freshness"], "unverified-saved-data")
        self.assertTrue(all(v is False for v in r["capabilities"].values()))

    def test_no_fake_scenery_or_collision(self):
        r = self.inspect()
        self.assertEqual(r["coverage"]["worldScenery"], "unknown")
        for name in ("collision", "visibility", "support", "reachability"):
            self.assertEqual(r["entities"][0][name], "unknown")

    def test_root_id_disagreement_rejected(self):
        x = snapshot(); x["playerId"] = "u-other"
        with self.assertRaisesRegex(ValueError, "mismatch"):
            self.inspect(x)

    def test_unit_aliases_and_addresses_rejected(self):
        for key in ("player", "player.target", "group01", "0x123ABC", " target", ""):
            with self.subTest(key=key), self.assertRaises(ValueError):
                M.entity_id(key, "id")

    def test_missing_id_not_replaced_by_name(self):
        x = snapshot(); del x["player"]["id"]
        with self.assertRaises(ValueError):
            self.inspect(x)

    def test_numeric_bool_and_nonfinite_rejected(self):
        for value in (True, float("nan"), float("inf"), 10**400, "12"):
            with self.subTest(value=str(value)), self.assertRaises(ValueError):
                x = snapshot(); x["player"]["coord"]["x"] = value
                self.inspect(x)

    def test_schema_boolean_or_wrong_version_rejected(self):
        for value in (True, 2, "1", None):
            with self.subTest(value=value), self.assertRaises(ValueError):
                x = snapshot(); x["schemaVersion"] = value; self.inspect(x)

    def test_malformed_array_and_total_limit_rejected(self):
        for value in ({}, [actor("u" + str(i)) for i in range(512)]):
            with self.assertRaises(ValueError):
                x = snapshot(); x["nearbyUnits"] = value; self.inspect(x)

    def test_no_mutation_or_cross_capture_tracking(self):
        x = snapshot(); before = copy.deepcopy(x)
        r = self.inspect(x); self.assertEqual(x, before)
        x["player"]["coord"]["x"] = 20
        other = self.inspect(x)
        self.assertEqual(r["entities"][0]["position"][0], 0)
        self.assertEqual(other["entities"][0]["position"][0], 20)
        self.assertEqual(other["counts"]["conflictingIds"], 0)

    def test_input_order_stable_identity_sorting(self):
        x = snapshot(); x["nearbyUnits"] = [actor("u-z"), actor("u-a")]
        self.assertEqual([r["id"] for r in self.inspect(x)["entities"]], ["u-a", "u-player", "u-z"])

    def test_unknown_player_flag_not_assumed_npc(self):
        x = snapshot(); del x["player"]["player"]
        self.assertIsNone(self.inspect(x)["entities"][0]["kind"])

    def test_readerbridge_mode_is_supported_and_nearby_not_exported(self):
        x = snapshot(); x["sourceMode"] = "ReaderBridge"
        r = self.inspect(x)
        self.assertEqual(r["sourceKind"], "recorded")
        self.assertEqual(r["coverage"]["nearbyUnits"], "not-exported-by-bridge-mode")

    def test_unobserved_source_mode_is_not_invented(self):
        x = snapshot(); x["sourceMode"] = "JSHUD"
        with self.assertRaisesRegex(ValueError, "sourceMode"): self.inspect(x)

    def test_missing_camera_does_not_guess_projection(self):
        self.assertEqual(self.inspect()["entities"][0]["projection"]["status"], "unavailable")


class ReceiptTests(unittest.TestCase):
    def inspect(self, data):
        return M.inspect_data(data, "rr2-receipt", SHA)

    def test_saved_fresh_receipt_remains_historical_player_only(self):
        r = self.inspect(receipt())
        self.assertEqual(r["historicalMetadata"]["recordedFreshnessClaim"], "fresh")
        self.assertFalse(r["live"])
        self.assertEqual(r["coverage"]["allEntities"], "player-only")
        self.assertEqual(r["counts"]["distinctIds"], 1)
        self.assertNotIn("selected-target", r["entities"][0]["roles"])
        self.assertEqual(r["entities"][0]["position"], [1, 2, 3])

    def test_ticks_preserved_as_decimal_string(self):
        self.assertEqual(self.inspect(receipt())["historicalMetadata"]["recordedProcessStartTicks"], "639279712871697793")

    def test_partial_typed_availability_produces_no_position(self):
        x = receipt(); x["observation"]["riftReader2"]["observation"]["fields"]["coordY"] = {"status": "unavailable"}
        self.assertIsNone(self.inspect(x)["entities"][0]["position"])

    def test_unavailable_player_not_fabricated(self):
        x = receipt(); x["observation"]["riftReader2"]["observation"]["player"] = {"status": "unavailable"}
        self.assertEqual(self.inspect(x)["counts"]["distinctIds"], 0)

    def test_bad_nested_schema_rejected(self):
        x = receipt(); x["observation"]["riftReader2"]["schemaVersion"] = 2
        with self.assertRaises(ValueError): self.inspect(x)

    def test_failed_status_with_value_rejected(self):
        x = receipt(); x["observation"]["riftReader2"]["observation"]["player"]["status"] = "invalid"
        with self.assertRaises(ValueError): self.inspect(x)


class CameraTests(unittest.TestCase):
    def valid(self, data=None):
        return M.validate_camera(data or camera(), SHA, "synthetic")

    def test_center_and_viewport_offset(self):
        p = M.project([0, 0, .5], self.valid())
        self.assertEqual(p["screen"], [410, 320])
        self.assertEqual(p["visibility"], "unknown")

    def test_top_left_and_bottom_right(self):
        self.assertEqual(M.project([-1, 1, 0], self.valid())["screen"], [10, 20])
        self.assertEqual(M.project([1, -1, 1], self.valid())["screen"], [810, 620])

    def test_clip_all_six_sides(self):
        for point in ([2, 0, .5], [-2, 0, .5], [0, 2, .5], [0, -2, .5], [0, 0, -.1], [0, 0, 1.1]):
            with self.subTest(point=point):
                self.assertEqual(M.project(point, self.valid())["status"], "not-in-frustum")

    def test_perspective_w_and_behind_rejection(self):
        x = camera(); x["viewProjection"] = [1,0,0,0, 0,1,0,0, 0,0,2,-2, 0,0,1,0]
        self.assertEqual(M.project([0,0,1.5], self.valid(x))["screen"], [410,320])
        self.assertIsNone(M.project([0,0,-1], self.valid(x))["screen"])
        self.assertIsNone(M.project([0,0,0], self.valid(x))["screen"])

    def test_hash_and_convention_mismatch_rejected(self):
        for key, value in (("sourceSha256", "b"*64), ("convention", "guessed")):
            with self.assertRaises(ValueError):
                x = camera(); x[key] = value; self.valid(x)

    def test_singular_or_wrong_size_matrix_rejected(self):
        for matrix in ([0]*16, [1]*16, [1]*15):
            with self.assertRaises(ValueError):
                x = camera(); x["viewProjection"] = matrix; self.valid(x)

    def test_nonfinite_and_boolean_matrix_rejected(self):
        for value in (True, float("nan"), float("inf")):
            with self.assertRaises(ValueError):
                x = camera(); x["viewProjection"][0] = value; self.valid(x)

    def test_no_synthetic_camera_on_real_input(self):
        with self.assertRaises(ValueError): M.validate_camera(camera(), SHA, "recorded")

    def test_candidate_not_calibrated(self):
        x = camera(); x["evidenceKind"] = "candidate"
        self.assertEqual(M.validate_camera(x, SHA, "recorded")["calibration"], "not-validated-against-game")

    def test_bad_viewport_dimensions_rejected(self):
        for width in (0, -1, True, 1.2, 16385):
            with self.assertRaises(ValueError):
                x = camera(); x["viewport"]["width"] = width; self.valid(x)

    def test_uniform_matrix_scaling_does_not_change_projection(self):
        x = camera(); x["viewProjection"] = [v*1e-10 for v in x["viewProjection"]]
        self.assertEqual(M.project([0,0,.5], self.valid(x))["screen"], [410,320])


class FileAndPresentationTests(unittest.TestCase):
    def test_duplicate_keys_malformed_utf8_and_constants_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            p = Path(folder)/"input.json"
            for raw in (b'{"a":1,"a":2}', b'{"v":NaN}', b'\xff', b'[]', b'{'):
                with self.subTest(raw=raw), self.assertRaises(ValueError):
                    p.write_bytes(raw); M.strict_load(p)

    def test_exponent_overflow_even_in_unused_field_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            p = Path(folder)/"input.json"; p.write_bytes(b'{"unused":1e9999}')
            with self.assertRaises(ValueError): M.strict_load(p)

    def test_invalid_surrogate_label_rejected_before_output(self):
        with tempfile.TemporaryDirectory() as folder:
            x = snapshot(); x["player"]["name"] = "\ud800"
            p = Path(folder)/"input.json"; p.write_text(json.dumps(x), encoding="utf-8")
            out = Path(folder)/"out"
            with self.assertRaises(ValueError): M.inspect_file(p, "readerbridge", out)
            self.assertFalse(out.exists())

    def test_schema_helper_rejects_non_object_with_clear_error(self):
        with self.assertRaises(ValueError): M.schema_one([], "bad")

    def test_oversized_file_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            p = Path(folder)/"big.json"; p.write_bytes(b' '*(M.MAX_BYTES+1))
            with self.assertRaises(ValueError): M.strict_load(p)

    def test_new_outputs_and_input_immutability(self):
        with tempfile.TemporaryDirectory() as folder:
            p = Path(folder)/"in.json"; raw = json.dumps(snapshot()).encode(); p.write_bytes(raw)
            out = Path(folder)/"new"
            r = M.inspect_file(p, "readerbridge", out)
            self.assertEqual(r["sourceSha256"], hashlib.sha256(raw).hexdigest())
            self.assertEqual(p.read_bytes(), raw)
            self.assertTrue((out/"report.html").is_file())
            old = (out/"report.json").read_bytes()
            with self.assertRaises(FileExistsError): M.inspect_file(p, "readerbridge", out)
            self.assertEqual((out/"report.json").read_bytes(), old)

    def test_invalid_input_creates_no_output(self):
        with tempfile.TemporaryDirectory() as folder:
            p = Path(folder)/"in.json"; p.write_text('{}'); out=Path(folder)/"new"
            with self.assertRaises(ValueError): M.inspect_file(p, "readerbridge", out)
            self.assertFalse(out.exists())

    def test_deterministic_json_and_html(self):
        r = M.inspect_data(snapshot(), "readerbridge", SHA)
        self.assertEqual(M.render_html(r), M.render_html(copy.deepcopy(r)))
        self.assertEqual(r, M.inspect_data(snapshot(), "readerbridge", SHA))

    def test_html_escapes_labels_and_has_no_script(self):
        x=snapshot(); x["player"]["name"]="<script>alert('x')</script>"
        output=M.render_html(M.inspect_data(x,"readerbridge",SHA))
        self.assertNotIn("<script",output)
        self.assertIn("&lt;script&gt;",output)
        self.assertIn("default-src 'none'",output)

    def test_all_heights_retained_at_same_xz(self):
        x=snapshot(); x["nearbyUnits"]=[actor("u-upper",xyz=(0,20,0))]
        r=M.inspect_data(x,"readerbridge",SHA)
        self.assertEqual({row["position"][1] for row in r["entities"]},{0,20})
        self.assertIn("Y=20",M.render_html(r))

    def test_no_game_network_or_execution_imports(self):
        tree=ast.parse((ROOT/"tools/world-inspector.py").read_text(encoding="utf-8"))
        names=set()
        for node in ast.walk(tree):
            if isinstance(node,ast.Import): names.update(a.name.split('.')[0] for a in node.names)
            if isinstance(node,ast.ImportFrom): names.add(node.module.split('.')[0])
            if isinstance(node,ast.Call) and isinstance(node.func,ast.Name):
                self.assertNotIn(node.func.id,{"eval","exec","__import__"})
        self.assertLessEqual(names,{"__future__","argparse","hashlib","html","json","math","pathlib","re","sys","typing"})


if __name__ == "__main__": unittest.main()
