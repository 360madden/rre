"""M3-001 synthetic + exact-file second hkpWorld constructor proof tests.

Proves a bounded native zero store and rejects corrupted sources; not an
executable type-7 handler nor runtime/gameplay evidence.
"""
from __future__ import annotations

import pathlib
import tempfile
import unittest
import sys

sys.path.insert(0,str(pathlib.Path(__file__).resolve().parent))
from m3_001_verify_second_world_ctor import (
    DEFAULT_EXE, EXPECTED, verify
)


class SecondWorldConstructorTests(unittest.TestCase):
    def test_world_vft_owner_and_zero_reaching_definition(self):
        r=verify()
        self.assertEqual(r["status"],"PASS")
        self.assertEqual(r["worldVtable"]["className"],".?AVhkpWorld@@")
        self.assertEqual(r["worldVtable"]["tableRva"],"0x2724038")
        self.assertTrue(r["zeroReachingDefinitionConfirmed"])
        self.assertEqual(r["fieldStoreRva"],"0x79a9f")
        self.assertFalse(r["qualifiedQueueType7Registration"])
        self.assertFalse(r["gameInputSent"])
        self.assertFalse(r["gameProcessAttached"])

    def test_native_disassembly_window_complete(self):
        r=verify()
        self.assertEqual(r["decodedInstructions"],79)
        self.assertTrue(r["regionCoversAllInstructions"])
        self.assertEqual(r["fieldStoreBytes"],"48898b10020000")
        self.assertEqual(r["zeroRegisterDefRva"],"0x799d1")

    def test_invalid_executable_rejected_before_pe_parse(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=pathlib.Path(tmp)/"fake_x64.exe"
            p.write_bytes(b"not-the-pinned-rift-executable")
            with self.assertRaisesRegex(ValueError,"hash mismatch"):
                verify(p)

    def test_expected_rvas_are_fixed_for_this_build(self):
        self.assertEqual(set(EXPECTED),
                         {0x799b9,0x799bc,0x799c9,0x799d1,0x79a9f})
        self.assertEqual(EXPECTED[0x79a9f],"48898b10020000")
        self.assertEqual(DEFAULT_EXE.name,"rift_x64.exe")


if __name__=="__main__":
    unittest.main()
