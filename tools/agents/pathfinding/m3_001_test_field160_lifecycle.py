"""M3-001 narrow regression tests: source proof vs unproven queue alias.

The tests only read the pinned original executable and four pre-existing
write-once V7 artifacts. No Rift process is opened or controlled.
"""
from __future__ import annotations

import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))
from m3_001_verify_field160_lifecycle import BUILD_SHA, EXE, PINNED_V7, verify, validate_v7


class Field160LifecycleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.proof=verify()

    def test_pinned_build_and_four_original_captures(self):
        p=self.proof
        self.assertEqual(p["status"],"PASS")
        self.assertEqual(p["sourceBuildSha256"],BUILD_SHA)
        self.assertEqual(len(p["v7CapturePins"]),4)
        self.assertEqual(len(PINNED_V7),4)

    def test_alloc_call_immediately_stored_into_field160(self):
        a=self.proof["allocationCandidate"]
        self.assertEqual(a["sourceCallRva"],"0x89c600")
        self.assertEqual(a["storeRva"],"0x89c605")
        self.assertEqual(a["allocatorRva"],"0x77c230")
        self.assertTrue(a["potentiallyNonnull"])
        self.assertFalse(a["actualNonNullGuaranteed"])
        self.assertEqual(self.proof["pinnedInsns"]["0x89c605"]["bytes"],"48898760010000")

    def test_release_then_zero_of_same_field(self):
        r=self.proof["matchingReleaseCandidate"]
        self.assertEqual(r["loadRva"],"0x89ca17")
        self.assertEqual(r["releaseCallRva"],"0x89ca1e")
        self.assertEqual(r["releaseFunctionRva"],"0x77c240")
        self.assertEqual(r["clearRva"],"0x89ca2a")
        self.assertEqual(self.proof["pinnedInsns"]["0x89c9d5"]["asm"],"xor esi, esi")

    def test_wrappers_have_qualified_direct_calls(self):
        self.assertIn(["0x89ea8d","0x89c4f0"],self.proof["wrapperCallGraph"])
        self.assertIn(["0x89e89d","0x89c990"],self.proof["wrapperCallGraph"])
        self.assertIn(["0xfb524e","0x89ea80"],self.proof["wrapperCallGraph"])
        self.assertIn(["0x89eb20","0x89e6f0"],self.proof["wrapperCallGraph"])

    def test_singleton_factory_vs_world_simulation_are_distinct_paths(self):
        self.assertEqual(self.proof["globalFactory"]["requestedBytes"],0x1d8)
        self.assertEqual(self.proof["separateWorldSimulationConstruction"]["worldRequestedObjectBytes"],0x200)
        self.assertFalse(self.proof["separateWorldSimulationConstruction"]["sameAsGlobalFactoryObjectProven"])
        self.assertFalse(self.proof["globalFactory"]["objectClassQualified"])

    def test_native_type7_remains_unverified(self):
        self.assertFalse(self.proof["simulationOwnerVerifiedForTheseWrites"])
        self.assertFalse(self.proof["nonnullSimulationQueueWriterProven"])
        self.assertFalse(self.proof["type7HandlerProven"])
        self.assertFalse(self.proof["type7JobProducerProven"])
        self.assertFalse(self.proof["gameInputSent"])
        self.assertFalse(self.proof["processAttached"])
        self.assertFalse(self.proof["binaryModified"])

    def test_byte_identical_source_is_repeatable(self):
        second=verify()
        self.assertEqual(json.dumps(second,sort_keys=True),
                         json.dumps(self.proof,sort_keys=True))

    def test_corrupted_source_fails_closed(self):
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/"fixture.exe"
            path.write_bytes(b"not RIFT native PE")
            with self.assertRaisesRegex(ValueError,"SHA mismatch"):
                verify(binary=path)

    def test_missing_V7_capture_fails_closed(self):
        with tempfile.TemporaryDirectory() as folder:
            with self.assertRaises(FileNotFoundError):
                validate_v7(Path(folder))

    def test_original_game_binary_path_unmodified(self):
        self.assertEqual(EXE.name,"rift_x64.exe")
        self.assertTrue(self.proof["limitations"])


if __name__=="__main__":
    unittest.main()
