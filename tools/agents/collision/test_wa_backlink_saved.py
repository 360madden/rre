"""Only previously retained evidence is read; no native capture or process access."""
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parent))
import wa_backlink_saved_verify as V

class SavedBacklinkTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.result=V.verify()
    def test_seven_regions_469_recorded_rows(self):
        self.assertEqual(len(self.result['regions']),7);self.assertEqual(self.result['retainedInstructionRows'],469)
    def test_lookup_chain_retained_without_entity_claim(self):
        self.assertIn('0x68e170',self.result['pins']);self.assertFalse(self.result['gameEntityIdentityQualified']);self.assertFalse(self.result['nativeBytesReverifiedNow'])
    def test_output_clear_differs_from_prior_optional_path(self):
        self.assertEqual(self.result['pins']['0xf674ef']['bytes'],'48891a')
    def test_saved_pin_tampering_rejected(self):
        with patch.dict(V.PINS,{'0xf67571':'90'}),self.assertRaisesRegex(ValueError,'pin mismatch'):V.verify()
    def test_missing_saved_capture_rejected(self):
        with tempfile.TemporaryDirectory() as d,self.assertRaises(FileNotFoundError):V.verify(Path(d))
    def test_blocked_next_capture_not_retried(self):
        self.assertTrue(self.result['nextCaptureToolBlocked']);self.assertFalse(self.result['blockedCaptureRetried']);self.assertFalse(self.result['liveBehaviorQualified'])
if __name__=='__main__':unittest.main()
