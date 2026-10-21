import unittest, copy, tempfile, pathlib, json, subprocess, sys
from tools.navigation_receipt_readiness import audit, load

def example():
 return {"observation":{"target":{"processId":42,"processStartUtcTicks":12345,"executableSha256":"a"*64},"riftReader2":{"bindingStatus":"bound","freshnessStatus":"fresh","observation":{"player":{"status":"ok","value":"player-1"},"fields":{"coordX":{"status":"ok","value":1.0},"coordY":{"status":"ok","value":2.0},"coordZ":{"status":"ok","value":3.0}}}}},"gameReady":True}
class TestReadiness(unittest.TestCase):
 def test_historical_positive_fields_do_not_grant_trial(self):
  r=audit(example());self.assertTrue(r["findings"]["historicalPlayerXYZPresent"]);self.assertFalse(r["trialReady"]);self.assertFalse(r["normalizedTrialProduced"])
 def test_saved_fresh_and_game_ready_do_not_grant_current(self):
  r=audit(example());self.assertFalse(r["findings"]["currentSessionFreshnessVerified"]);self.assertFalse(r["findings"]["liveApprovalVerified"])
 def test_process_target_is_not_selected_entity(self):
  r=audit(example());self.assertFalse(r["findings"]["reviewedGroundClickPointVerified"])
 def test_missing_position(self):
  d=example(); del d["observation"]["riftReader2"]["observation"]["fields"]["coordZ"]
  self.assertFalse(audit(d)["findings"]["historicalPlayerXYZPresent"])
 def test_unavailable_coordinate(self):
  d=example();d["observation"]["riftReader2"]["observation"]["fields"]["coordX"]={"status":"unavailable"}
  self.assertFalse(audit(d)["findings"]["historicalPlayerXYZPresent"])
 def test_nan_coordinate(self):
  d=example();d["observation"]["riftReader2"]["observation"]["fields"]["coordX"]["value"]=float("nan")
  self.assertFalse(audit(d)["findings"]["historicalPlayerXYZPresent"])
 def test_no_live_or_image_claims_even_though_extra_flags(self):
  d=example();d["observation"]["imageVerified"]=True;d["observation"]["liveAuthorization"]=True
  r=audit(d);self.assertFalse(r["findings"]["originalImageBytesAndActionAssociationVerified"]);self.assertFalse(r["findings"]["exclusiveLiveControlVerified"])
 def test_empty_receipt(self):self.assertFalse(audit({})["trialReady"])
 def test_duplicate_keys(self):
  with tempfile.TemporaryDirectory() as root:
   p=pathlib.Path(root)/"dup.json";p.write_text('{"observation":{},"observation":{}}')
   with self.assertRaises(ValueError):load(p)
 def test_nonstandard_json(self):
  with tempfile.TemporaryDirectory() as root:
   p=pathlib.Path(root)/"nan.json";p.write_text('{"observation":NaN}')
   with self.assertRaises(ValueError):load(p)
 def test_real_historical_receipt_remains_not_ready(self):
  p=pathlib.Path("C:/work/riftreader2/artifacts/live-validation/live-fresh-receipt.json")
  if not p.exists():self.skipTest("historical external fixture absent")
  r=audit(load(p));self.assertTrue(r["findings"]["historicalPlayerXYZPresent"]);self.assertFalse(r["trialReady"])
 def test_file_only_cli(self):
  with tempfile.TemporaryDirectory() as root:
   p=pathlib.Path(root)/"input.json";p.write_text(json.dumps(example()))
   q=pathlib.Path(root)/"report.json"
   result=subprocess.run([sys.executable,"-B","tools/navigation_receipt_readiness.py","--receipt",str(p),"--output",str(q)],capture_output=True,text=True,timeout=10)
   self.assertEqual(result.returncode,0,result.stderr);self.assertFalse(json.loads(q.read_text())["trialReady"])
   second=subprocess.run([sys.executable,"-B","tools/navigation_receipt_readiness.py","--receipt",str(p),"--output",str(q)],capture_output=True,text=True,timeout=10)
   self.assertEqual(second.returncode,2)
if __name__=="__main__":unittest.main()
