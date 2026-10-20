"""Synthetic screenshot, provenance and publication tests; no live operations."""
from __future__ import annotations
import copy
import io
import json
from pathlib import Path
import random
import sys
import tempfile
import unittest
from unittest.mock import patch
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
from visual_evidence import cli, evidence as E, matcher as M

POINTS = [[32, 32], [96, 32], [32, 96], [96, 96]]
POLICY = {"patchRadius": 3, "searchRadius": 4, "sampleStep": 1}
VM = {"vmx": "C:/lab/RIFT-Lab-1.vmx", "pid": 100, "startTicks": 123456789012345678}


def pictures(mode="in"):
    rng = random.Random(41)
    a = Image.new("RGB", (128, 128))
    a.putdata([(v,v,v) for v in [rng.randrange(256) for _ in range(128*128)]])
    b = a.copy()
    for x, y in POINTS:
        dx, dy = (3 if x < 64 else -3), (3 if y < 64 else -3)
        if mode == "out": dx, dy = -dx, -dy
        if mode == "stationary": dx, dy = 0, 0
        if mode == "translation": dx, dy = 3, 0
        b.paste(a.crop((x-3,y-3,x+4,y+4)), (x-3+dx,y-3+dy))
    b.putpixel((0,0), (1,2,3))  # unrelated UI pixel, not a movement signal
    return a,b


def fixture(root, mode="in"):
    def save(name, value):
        raw = cli.encoded(value) if not isinstance(value, bytes) else value
        (root/name).write_bytes(raw)
        return {"path": name, "sha256": E.sha(raw)}
    images = []
    for image in pictures(mode):
        out = io.BytesIO(); image.save(out, format="PNG"); images.append(out.getvalue())
    target = {"machineName": "RIFT-LAB-1", "windowHandle": "0x123", "executablePath": "C:/RIFT/rift_x64.exe",
              "executableSha256": "a"*64, "processId": 300, "processStartUtcTicks": 639280390564351086,
              "clientWidth": 128, "clientHeight": 128, "clientX": 0, "clientY": 23, "isForeground": True}
    caps, frames = [], []
    for key, sec, raw in zip(("before", "after"), (0,3), images):
        cap = {"captureId": "capture-"+key, "capturedAtUtc": f"2026-10-20T13:00:0{sec}Z",
               "captureBackend": "synthetic-fixture", "sha256": E.sha(raw), "target": copy.deepcopy(target),
               "savedImage": {"path": key+".png", "sha256": E.sha(raw), "byteLength": len(raw)}}
        caps.append(cap)
        frames.append({"id": key, "image": save(key+".png",raw), "capture": save(key+".json",cap)})
    action = {"startedAtUtc": "2026-10-20T13:00:01Z", "completedAtUtc": "2026-10-20T13:00:02Z",
              "action": {"keys": [], "wheelNotches": -1}, "target": copy.deepcopy(target), "recoveryRequired": False,
              "result": {"deliverySucceeded": True, "releaseSucceeded": True, "cancelled": False,
                         "stateUncertain": False, "targetLost": False, "responseVerified": False}}
    def row(kind, value):
        return {"schemaVersion": 1, "recordedAtUtc": "2026-10-20T13:00:04Z", "evidenceKind": kind, "value": value}
    ctx = {"connected": True, "instanceId": "session-one", "machineName": "RIFT-LAB-1", "vmIdentity": VM}
    rows = [row("control-guest-connected/1", ctx), row("control-capture/1", caps[0]),
            row("control-command-request/1", {"id": "cmd-one", "operation": "action"}),
            row("control-command-response/1", {"id": "cmd-one", "operation": "action", "payload": action}),
            row("control-capture/1", caps[1])]
    journal = b"".join(cli.encoded(r).replace(b"\n", b"")+b"\n" for r in rows)
    spec = {"schemaVersion": 1, "kind": "rre-visual-evidence", "sourceKind": "synthetic", "experimentId": "synthetic-check",
            "expectedVm": copy.deepcopy(VM), "journal": save("journal.jsonl", journal), "frames": frames,
            "actions": [{"id": "move", "result": save("action.json", action)}],
            "comparisons": [{"id": "radial-check", "before": "before", "after": "after", "actionIds": ["move"],
                             "expectation": "radial-in", "points": POINTS, "settings": POLICY}]}
    save("spec.json",spec)
    return spec, caps, action, rows


class MatcherTests(unittest.TestCase):
    def result(self, mode="in", expectation="radial-in"):
        return M.compare(*pictures(mode), POINTS, expectation, POLICY)

    def test_known_inward_pattern(self): self.assertEqual(self.result()["status"], "passed")
    def test_known_outward_pattern(self): self.assertEqual(self.result("out", "radial-out")["status"], "passed")
    def test_opposite_direction_fails(self): self.assertEqual(self.result("out")["status"], "failed")
    def test_ui_pixel_change_is_not_zoom(self): self.assertEqual(self.result("stationary")["reason"], "no-measured-radial-motion")
    def test_stationary_predicate(self): self.assertEqual(self.result("stationary", "stationary")["status"], "passed")
    def test_stationary_predicate_detects_motion(self): self.assertEqual(self.result("in", "stationary")["status"], "failed")
    def test_translation_is_not_zoom(self): self.assertEqual(self.result("translation")["status"], "inconclusive")
    def test_blank_patch_inconclusive(self):
        image = Image.new("RGB", (128,128), "gray")
        self.assertEqual(M.compare(image,image,POINTS,"radial-in",POLICY)["status"], "inconclusive")
    def test_repeated_texture_is_ambiguous(self):
        a = Image.new("RGB", (128,128)); a.putdata([(255*(x%2),)*3 for y in range(128) for x in range(128)])
        self.assertEqual(M.compare(a,a,POINTS,"radial-in",POLICY)["patches"][0]["reason"], "ambiguous-match")
    def test_bad_match_is_inconclusive(self):
        a,b = pictures(); b = Image.new("RGB", b.size, "black")
        self.assertEqual(M.compare(a,b,POINTS,"radial-in",POLICY)["status"], "inconclusive")
    def test_bounds_rejected(self):
        points = copy.deepcopy(POINTS); points[0] = [1,1]
        with self.assertRaises(ValueError): M.compare(*pictures(),points,"radial-in",POLICY)
    def test_duplicate_patch_rejected(self):
        with self.assertRaises(ValueError): M.compare(*pictures(),[POINTS[0]]*4,"radial-in",POLICY)
    def test_boolean_setting_rejected(self):
        with self.assertRaises(ValueError): M.settings({"searchRadius": True})
    def test_nan_setting_rejected(self):
        with self.assertRaises(ValueError): M.settings({"maxMse": float("nan")})
    def test_false_settings_rejected(self):
        with self.assertRaises(ValueError): M.compare(*pictures(),POINTS,"radial-in",False)
    def test_too_small_search_rejected(self):
        with self.assertRaises(ValueError): M.settings({"searchRadius":2})
    def test_unknown_setting_rejected(self):
        with self.assertRaises(ValueError): M.settings({"maxMSE": 100})
    def test_wrong_dimensions_rejected(self):
        with self.assertRaises(ValueError): M.compare(pictures()[0],Image.new("RGB",(64,64)),POINTS,"radial-in",POLICY)


class EvidenceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(); self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name); self.spec,self.caps,self.action,self.rows = fixture(self.root)

    def evaluate(self): return cli.evaluate(self.spec,self.root)[0]["results"][0]
    def refresh(self, ref, value):
        raw = cli.encoded(value); (self.root/ref["path"]).write_bytes(raw); ref["sha256"] = E.sha(raw)
    def update_journal(self):
        raw = b"".join(json.dumps(r).encode()+b"\n" for r in self.rows)
        (self.root/"journal.jsonl").write_bytes(raw); self.spec["journal"]["sha256"] = E.sha(raw)
    def test_exact_recorded_linkage_passes(self): self.assertEqual(self.evaluate()["status"],"passed")
    def test_wrong_vm_is_inconclusive(self):
        self.spec["expectedVm"]["vmx"] = "C:/lab/RIFT-Lab-2.vmx"
        self.assertIn("wrong-vm-epoch",self.evaluate()["bindingReasons"])
    def test_wrong_vm_start_is_inconclusive(self):
        self.spec["expectedVm"]["startTicks"] += 1
        self.assertEqual(self.evaluate()["status"],"inconclusive")
    def test_missing_journal_is_not_pass(self):
        self.spec["journal"] = None
        self.assertEqual(self.evaluate()["status"],"inconclusive")
    def test_unlisted_action_blocks_acceptance(self):
        self.rows.insert(3,{"schemaVersion":1,"recordedAtUtc":"2026-10-20T13:00:02Z","evidenceKind":"control-command-request/1","value":{"id":"extra","operation":"action"}})
        self.update_journal(); self.assertIn("unaccounted-or-reordered-actions",self.evaluate()["bindingReasons"])
    def test_receiver_reconnect_blocks(self):
        self.rows.insert(4,copy.deepcopy(self.rows[0])); self.rows[4]["value"]["instanceId"]="session-two"
        self.update_journal(); self.assertIn("receiver-reconnected-or-unbound",self.evaluate()["bindingReasons"])
    def test_metadata_target_change_blocks(self):
        self.caps[1]["target"]["processId"] += 1
        self.refresh(self.spec["frames"][1]["capture"],self.caps[1])
        self.assertEqual(self.evaluate()["status"],"inconclusive")
    def test_capture_before_action_cannot_validate(self):
        self.caps[1]["capturedAtUtc"]="2026-10-20T13:00:00.5Z"
        self.refresh(self.spec["frames"][1]["capture"],self.caps[1])
        self.assertIn("action-not-bracketed-by-frames",self.evaluate()["bindingReasons"])
    def test_failed_delivery_cannot_pass(self):
        self.action["result"]["deliverySucceeded"]=False
        self.refresh(self.spec["actions"][0]["result"],self.action)
        self.assertIn("action-delivery-or-release-unqualified",self.evaluate()["bindingReasons"])
    def test_hash_tampering_rejected(self):
        (self.root/"before.png").write_bytes(b"changed")
        with self.assertRaisesRegex(ValueError,"hash mismatch"): self.evaluate()
    def test_missing_file_rejected(self):
        (self.root/"before.png").unlink()
        with self.assertRaisesRegex(ValueError,"Missing"): self.evaluate()
    def test_traversal_rejected(self):
        self.spec["frames"][0]["image"]["path"]="../outside.png"
        with self.assertRaises(ValueError): self.evaluate()
    def test_corrupt_image_rejected(self):
        ref=self.spec["frames"][0]["image"]; raw=b"not an image"
        (self.root/ref["path"]).write_bytes(raw); ref["sha256"]=E.sha(raw)
        self.caps[0]["sha256"]=E.sha(raw);self.caps[0]["savedImage"].update(sha256=E.sha(raw),byteLength=len(raw))
        self.refresh(self.spec["frames"][0]["capture"],self.caps[0])
        with self.assertRaises(OSError): self.evaluate()
    def test_duplicate_frame_ids_rejected(self):
        self.spec["frames"][1]["id"]="before"
        with self.assertRaises(ValueError): self.evaluate()
    def test_bool_schema_rejected(self):
        self.spec["schemaVersion"]=True
        with self.assertRaises(ValueError): self.evaluate()
    def test_duplicate_json_keys_rejected(self):
        with self.assertRaises(ValueError): E.json_bytes(b'{"a":1,"a":2}')
    def test_escaped_invalid_unicode_rejected(self):
        with self.assertRaises(ValueError): E.json_bytes(b'{"a":"\\ud800"}')
    def test_nonfinite_exponent_rejected(self):
        with self.assertRaises(ValueError): E.json_bytes(b'{"a":1e999}')
    def test_naive_timestamp_rejected(self):
        with self.assertRaises(ValueError): E.timestamp("2026-10-20T00:00:00")
    def test_metadata_dimensions_rejected(self):
        self.caps[0]["target"]["clientWidth"]=127
        self.refresh(self.spec["frames"][0]["capture"],self.caps[0])
        with self.assertRaisesRegex(ValueError,"dimension"): self.evaluate()
    def test_reference_is_context_only(self):
        self.spec["references"]=[{"id":"keybindings","image":self.spec["frames"][0]["image"],"note":"<script>example</script>"}]
        r=cli.evaluate(self.spec,self.root)[0]
        self.assertEqual(r["references"]["keybindings"]["qualification"],"context-only-unbound")
        self.assertNotIn(b"<script>",cli.render(r))
    def test_identical_image_bytes_never_establish_freshness(self):
        ref=self.spec["frames"][1]["image"];raw=(self.root/"before.png").read_bytes()
        (self.root/ref["path"]).write_bytes(raw);ref["sha256"]=E.sha(raw)
        self.caps[1]["sha256"]=E.sha(raw);self.caps[1]["savedImage"].update(sha256=E.sha(raw),byteLength=len(raw))
        self.refresh(self.spec["frames"][1]["capture"],self.caps[1])
        self.assertIn("identical-image-bytes-freshness-ambiguous",self.evaluate()["bindingReasons"])
    def test_no_live_or_independent_review_claim(self):
        r=cli.evaluate(self.spec,self.root)[0]
        self.assertFalse(r["live"]);self.assertFalse(r["gameplayValidated"])
        self.assertFalse(r["independentCodeReviewComplete"]);self.assertEqual(r["visionReview"],"not-attempted")


class PackageTests(EvidenceTests):
    # Inherit fixture helpers, not the evidence tests themselves (see load_tests below).
    def test_package_roundtrip(self):
        r=cli.build(self.root/"spec.json",self.root,self.root/"package")
        self.assertTrue(cli.verify(self.root/"package")["publicationComplete"])
        replay=cli.build(self.root/"package/spec.json",self.root/"package",self.root/"replay")
        self.assertEqual(r["results"],replay["results"])
    def test_overwrite_rejected(self):
        cli.build(self.root/"spec.json",self.root,self.root/"package")
        old=E.sha((self.root/"package/complete.json").read_bytes())
        with self.assertRaises(FileExistsError): cli.build(self.root/"spec.json",self.root,self.root/"package")
        self.assertEqual(old,E.sha((self.root/"package/complete.json").read_bytes()))
    def test_modified_preview_rejected(self):
        cli.build(self.root/"spec.json",self.root,self.root/"package")
        (self.root/"package/preview-before.png").write_bytes(b"edited")
        with self.assertRaises(ValueError):cli.verify(self.root/"package")
    def test_missing_receipt_rejected(self):
        cli.build(self.root/"spec.json",self.root,self.root/"package")
        (self.root/"package/complete.json").unlink()
        with self.assertRaises(ValueError):cli.verify(self.root/"package")
    def test_receipt_cannot_omit_a_referenced_image(self):
        cli.build(self.root/"spec.json",self.root,self.root/"package")
        package=self.root/"package"
        spec=json.loads((package/"spec.json").read_text());name=spec["frames"][0]["image"]["path"]
        receipt=json.loads((package/"complete.json").read_text());receipt["files"].pop(name)
        (package/name).unlink();(package/"complete.json").write_bytes(cli.encoded(receipt))
        with self.assertRaises(ValueError):cli.verify(package)
    def test_receipt_cannot_omit_a_preview(self):
        cli.build(self.root/"spec.json",self.root,self.root/"package")
        package=self.root/"package";receipt=json.loads((package/"complete.json").read_text())
        receipt["files"].pop("preview-before.png");(package/"preview-before.png").unlink()
        (package/"complete.json").write_bytes(cli.encoded(receipt))
        with self.assertRaises(ValueError):cli.verify(package)
    def test_extra_package_file_rejected(self):
        cli.build(self.root/"spec.json",self.root,self.root/"package")
        (self.root/"package/extra.txt").write_text("extra")
        with self.assertRaises(ValueError):cli.verify(self.root/"package")
    def test_failed_html_write_has_no_receipt(self):
        original=Path.open
        def failing(path,*args,**kwargs):
            if path.name=="report.html" and args and args[0]=="xb":raise OSError("injected write failure")
            return original(path,*args,**kwargs)
        with patch.object(Path,"open",failing), self.assertRaises(OSError):
            cli.build(self.root/"spec.json",self.root,self.root/"package")
        self.assertTrue((self.root/"package").exists());self.assertFalse((self.root/"package/complete.json").exists())
    def test_bad_input_creates_no_package(self):
        self.spec["frames"][0]["image"]["sha256"]="0"*64
        (self.root/"spec.json").write_bytes(cli.encoded(self.spec))
        with self.assertRaises(ValueError):cli.build(self.root/"spec.json",self.root,self.root/"package")
        self.assertFalse((self.root/"package").exists())
    def test_cli_success_and_verify(self):
        self.assertEqual(cli.main(["run","--spec",str(self.root/"spec.json"),"--source-root",str(self.root),"--output-dir",str(self.root/"package"),"--require-pass"]),0)
        self.assertEqual(cli.main(["verify","--bundle",str(self.root/"package")]),0)
    def test_cli_inconclusive_exit(self):
        self.spec["journal"]=None;(self.root/"spec.json").write_bytes(cli.encoded(self.spec))
        self.assertEqual(cli.main(["run","--spec",str(self.root/"spec.json"),"--source-root",str(self.root),"--output-dir",str(self.root/"package"),"--require-pass"]),4)
    def test_cli_failed_predicate_exit(self):
        self.spec["comparisons"][0]["expectation"]="radial-out";(self.root/"spec.json").write_bytes(cli.encoded(self.spec))
        self.assertEqual(cli.main(["run","--spec",str(self.root/"spec.json"),"--source-root",str(self.root),"--output-dir",str(self.root/"package"),"--require-pass"]),3)
    def test_pin_path_only_recipe(self):
        for f in self.spec["frames"]:
            f["image"].pop("sha256"); f["capture"].pop("sha256")
        self.spec["journal"].pop("sha256");self.spec["actions"][0]["result"].pop("sha256")
        (self.root/"recipe.json").write_bytes(cli.encoded(self.spec))
        r=cli.pin(self.root/"recipe.json",self.root,self.root/"pinned.json")
        self.assertFalse(r["trialAccepted"])
        self.assertTrue(cli.build(self.root/"pinned.json",self.root,self.root/"package")["allPredicatesPassed"])
    def test_pin_does_not_overwrite(self):
        with self.assertRaises(FileExistsError):cli.pin(self.root/"spec.json",self.root,self.root/"spec.json")
    def test_pin_does_not_silently_refresh_wrong_hash(self):
        self.spec["frames"][0]["image"]["sha256"]="0"*64
        (self.root/"recipe.json").write_bytes(cli.encoded(self.spec))
        with self.assertRaises(ValueError):cli.pin(self.root/"recipe.json",self.root,self.root/"pinned.json")
        self.assertFalse((self.root/"pinned.json").exists())
    def test_reference_included_in_review_packet(self):
        self.spec["references"]=[{"id":"console","image":self.spec["frames"][0]["image"],"note":"Unbound reference"}]
        (self.root/"spec.json").write_bytes(cli.encoded(self.spec))
        cli.build(self.root/"spec.json",self.root,self.root/"package")
        packet=json.loads((self.root/"package/review-packet.json").read_text())
        self.assertEqual(packet["contextImages"][0]["qualification"],"context-only-unbound")
        self.assertEqual(packet["deliveryStatus"],"not-attempted")
    def test_cli_invalid_input_exit(self):
        self.assertEqual(cli.main(["verify","--bundle",str(self.root/"missing")]),2)


def load_tests(loader, tests, pattern):
    suite=unittest.TestSuite()
    for cls in (MatcherTests,EvidenceTests,PackageTests):
        for name in sorted(n for n in cls.__dict__ if n.startswith("test_")):
            suite.addTest(cls(name))
    return suite

if __name__ == "__main__": unittest.main()
