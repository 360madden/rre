"""Exact-build offline tests for WA-003, never a live-game test."""
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent))
import wa_hit_result_verify as V


class HitResultTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.proof = V.verify()

    def test_two_unwind_regions_are_155_exact_rows(self):
        self.assertEqual(len(self.proof['capturedUnwindRegions']), 2)
        self.assertEqual(sum(x['rows'] for x in self.proof['capturedUnwindRegions']), 155)

    def test_three_unresolved_anchors_remain_distinct_from_captured_functions(self):
        self.assertEqual(len(self.proof['unresolvedPeUnwindAnchors']), 3)
        self.assertEqual(len(self.proof['supplementalBoundedEntries']), 3)
        self.assertTrue(all(x['fullFunctionBoundaryQualified'] is False for x in self.proof['supplementalBoundedEntries']))
        self.assertEqual(sum(len(x['rows']) for x in self.proof['supplementalBoundedEntries']), 24)

    def test_local_collector_rtti_is_qualified_not_final_entity(self):
        self.assertEqual(self.proof['collector']['rttiName'], '.?AVhkpClosestRayHitCollector@@')
        self.assertEqual(self.proof['collector']['vftRva'], '0x2d6a8a8')
        self.assertFalse(self.proof['entityIdentityQualified'])

    def test_optional_output_clear_and_pointer_stores_are_present(self):
        pins = self.proof['dataFlowPins']
        self.assertEqual(pins['0xf67332']['instruction'], 'mov qword ptr [rbp], r12')
        self.assertEqual(pins['0xf673b0']['instruction'], 'mov qword ptr [rbp], rax')
        self.assertEqual(pins['0xf67351']['instruction'], 'cmp dword ptr [rcx], 0xffff')
        self.assertTrue(any('early exits' in x for x in self.proof['findings']))

    def test_no_live_or_callable_claim(self):
        for key in ['entityIdentityQualified', 'worldFrameQualified', 'callableInterfaceQualified',
                    'gameInputSent', 'gameProcessAttached', 'nativeFunctionsCalled']:
            self.assertIs(self.proof[key], False)
        self.assertIs(self.proof['offlineOnly'], True)

    def test_corrupted_binary_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)/'bad.exe'; path.write_bytes(b'not the original executable')
            with self.assertRaisesRegex(ValueError, 'SHA mismatch'):
                V.verify(binary=path)

    def test_changed_instruction_pin_rejected(self):
        with patch.dict(V.PINS, {0xf673b0: '90'}):
            with self.assertRaisesRegex(ValueError, 'pin changed'):
                V.verify()

    def test_missing_v7_receipt_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaises(FileNotFoundError): V.verify(root=Path(directory))

    def test_repeatability(self):
        self.assertEqual(self.proof, V.verify())


if __name__ == '__main__': unittest.main()
