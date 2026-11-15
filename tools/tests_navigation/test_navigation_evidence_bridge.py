import unittest,tempfile,pathlib,hashlib,copy,json,subprocess,sys
from tools.navigation_evidence_bridge import assess,obj
def pair(image):
 h=hashlib.sha256(image.read_bytes()).hexdigest()
 target=dict(processId=42,processStartUtcTicks=111,windowHandle="a",executableSha256="b"*64,clientWidth=800,clientHeight=600)
 capture=dict(savedImage=dict(sha256=h),target=target,capturedAtUtc="2026-10-20T12:00:00+00:00")
 action=dict(target=copy.deepcopy(target),startedAtUtc="2026-10-20T12:00:00.500+00:00",action=dict(mouseButton="left",keys=[],wheelNotches=0),result=dict(deliverySucceeded=True,releaseSucceeded=True))
 return capture,action
class BridgeTests(unittest.TestCase):
 def setup(self,fn):
  with tempfile.TemporaryDirectory() as d:
   p=pathlib.Path(d)/"image.bmp";p.write_bytes(b"synthetic-pixel-bytes")
   c,a=pair(p);return fn(c,a,p)
 def test_valid_image_and_identity_still_not_navigation(self):
  def check(c,a,p):
   r=assess(c,a,p);self.assertTrue(r["imageBytesVerified"]);self.assertTrue(r["targetIdentityMatches"]);self.assertFalse(r["trialReady"]);self.assertIn("no-reviewed-client-point-in-action",r["issues"])
  self.setup(check)
 def test_wrong_hash(self):
  self.setup(lambda c,a,p:self.assertIn("image-hash-mismatch",assess({**c,"savedImage":{"sha256":"0"*64}},a,p)["issues"]))
 def test_wrong_pid(self):
  def check(c,a,p):
   a["target"]["processId"]=100;self.assertIn("target-identity-mismatch",assess(c,a,p)["issues"])
  self.setup(check)
 def test_right_button_is_not_destination(self):
  def check(c,a,p):
   a["action"]["mouseButton"]="right";self.assertIn("not-a-ground-click-candidate",assess(c,a,p)["issues"])
  self.setup(check)
 def test_keyboard_is_not_destination(self):
  def check(c,a,p):
   a["action"]["mouseButton"]=None;a["action"]["keys"]=["w"];self.assertEqual(assess(c,a,p)["actionKind"],"keyboard")
  self.setup(check)
 def test_stale_frame(self):
  def check(c,a,p):
   a["startedAtUtc"]="2026-10-20T12:00:25+00:00";self.assertIn("capture-not-immediate",assess(c,a,p)["issues"])
  self.setup(check)
 def test_failed_input(self):
  def check(c,a,p):
   a["result"]["releaseSucceeded"]=False;self.assertIn("delivery-or-release-unconfirmed",assess(c,a,p)["issues"])
  self.setup(check)
 def test_duplicate_json(self):
  with tempfile.TemporaryDirectory() as d:
   p=pathlib.Path(d)/"x.json";p.write_text('{"a":1,"a":2}')
   with self.assertRaises(ValueError):obj(p)
 def test_nested_evidence_shapes_fail_closed(self):
  for owner,key in (("capture","savedImage"),("capture","target"),("action","target"),("action","action"),("action","result")):
   for invalid in (None,False,1,"scalar",[]):
    with self.subTest(owner=owner,key=key,invalid=invalid):
     def check(c,a,p):
      (c if owner=="capture" else a)[key]=invalid
      with self.assertRaisesRegex(ValueError,"must be an object"):assess(c,a,p)
     self.setup(check)
 def test_cli_returns_structured_error_without_traceback_for_bad_shape(self):
  with tempfile.TemporaryDirectory() as d:
   folder=pathlib.Path(d);image=folder/"image.bmp";image.write_bytes(b"synthetic-pixel-bytes")
   capture,action=pair(image);action["result"]=[True]
   capture_path=folder/"capture.json";action_path=folder/"action.json";output=folder/"receipt.json"
   capture_path.write_text(json.dumps(capture));action_path.write_text(json.dumps(action))
   script=pathlib.Path(__file__).resolve().parents[1]/"navigation_evidence_bridge.py"
   run=subprocess.run([sys.executable,str(script),"--capture",str(capture_path),"--action",str(action_path),"--image",str(image),"--output",str(output)],capture_output=True,text=True)
   self.assertEqual(run.returncode,2,run.stderr)
   self.assertEqual(json.loads(run.stdout)["trialReady"],False)
   self.assertEqual(json.loads(run.stdout)["gameInputSent"],False)
   self.assertNotIn("Traceback",run.stderr)
   self.assertFalse(output.exists())
 def test_historical_real_bundle(self):
  base=pathlib.Path("C:/work/riftreader2/artifacts/native-control-followup-20261020")
  if not base.exists():self.skipTest("historical optional source unavailable")
  c=obj(base/"button-only-before/capture.json");a=obj(base/"button-only-result.json")
  r=assess(c,a,base/"button-only-before/image.bmp")
  self.assertTrue(r["imageBytesVerified"]);self.assertTrue(r["targetIdentityMatches"])
  self.assertFalse(r["trialReady"]);self.assertIn("not-a-ground-click-candidate",r["issues"])
if __name__=="__main__":unittest.main()
