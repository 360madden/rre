import unittest, tempfile, pathlib, hashlib, json, sys, copy
sys.path.insert(0,"tools")
from navigation_evidence_assemble import assemble,NAMES
from navigation_stop_evidence import decode
from test_navigation_stop_evidence import fixture

def write(root,trace):
 files={}
 for k in NAMES:
  p=root/(k+".json");raw=json.dumps(trace[k]).encode();p.write_bytes(raw)
  files[k]={"path":p.name,"sha256":hashlib.sha256(raw).hexdigest()}
 return {"schemaVersion":1,"kind":trace["kind"],"files":files}
class AssembleTests(unittest.TestCase):
 def test_complete_synthetic(self):
  with tempfile.TemporaryDirectory() as t:
   root=pathlib.Path(t);out=assemble(write(root,fixture()),root)
   self.assertEqual(out["evaluation"]["verdict"],"movement-then-stationary")
   self.assertFalse(out["liveAccepted"])
 def test_recorded_label_is_not_authentication(self):
  with tempfile.TemporaryDirectory() as t:
   root=pathlib.Path(t);trace=fixture();trace["kind"]="recorded-normalized"
   out=assemble(write(root,trace),root);self.assertFalse(out["evaluation"]["provenanceAuthenticated"])
 def test_missing_source_fail(self):
  with tempfile.TemporaryDirectory() as t:
   root=pathlib.Path(t);m=write(root,fixture());m["files"].pop("samples")
   with self.assertRaises(ValueError):assemble(m,root)
 def test_corrupt_hash_fail(self):
  with tempfile.TemporaryDirectory() as t:
   root=pathlib.Path(t);m=write(root,fixture());(root/"samples.json").write_text("[]")
   with self.assertRaises(ValueError):assemble(m,root)
 def test_path_escape_rejected(self):
  with tempfile.TemporaryDirectory() as t:
   root=pathlib.Path(t);m=write(root,fixture());m["files"]["samples"]["path"]="../samples.json"
   with self.assertRaises(ValueError):assemble(m,root)
 def test_action_missing_does_not_autofill(self):
  with tempfile.TemporaryDirectory() as t:
   root=pathlib.Path(t);trace=fixture();trace["actions"]=[]
   out=assemble(write(root,trace),root)
   self.assertFalse(out["evaluation"]["telemetrySupportsStop"])
 def test_nonfinite_json(self):
  with self.assertRaises(ValueError):decode(b'{"x":NaN}')
if __name__=="__main__":unittest.main()
