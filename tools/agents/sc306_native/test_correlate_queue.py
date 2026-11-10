"""Dependency-free regression tests for the SC-306 offline correlator."""
from __future__ import annotations

import base64
import json
import tempfile
import unittest
from pathlib import Path

from correlate_queue import EvidenceError, audit, sha256

BASE = 0x140000000
ROOT_RVA = 0x33958C0
PTR = 0x1B0000000
SHA = "1935A05C9DB6D468E34E0055014A4A99C1B5AFCEB1695884E24600F5C20A4BE8"
UI_BEFORE = "2026-11-07T15:51:21Z"
UI_AFTER = "2026-11-07T15:52:15Z"
SETTER = base64.b64decode("SIsNEit8AjuZpAAAAA+ELAMAAImZpAAAAA+2QRkPuugHiEEZ6RYD")


def b64(data: bytes) -> str:
    return base64.b64encode(data).decode("ascii")


class CorrelationTests(unittest.TestCase):
    def setUp(self) -> None:
        temp = tempfile.TemporaryDirectory(prefix="rre-sc306-test-")
        self.addCleanup(temp.cleanup)
        self.folder = Path(temp.name)
        target = {
            "processId": 9752, "processStartUtcTicks": 639294897826627677,
            "executablePath": r"C:\RIFT_TRANSFER\RIFT\rift_x64.exe",
            "executableSha256": SHA, "moduleBaseAddress": hex(BASE),
            "moduleSize": 63164416,
        }
        identity = {**target, "moduleBaseAddress": BASE}
        self.save("native-inspection.json", {"target": target})
        parts = {
            0xBD2DA7: SETTER,
            0xBD7153: bytes.fromhex("8b98a4000000"),
            0x26ECC70: b"ActionBars_AbilityQueue\x00",
            ROOT_RVA: PTR.to_bytes(8, "little"),
        }
        chunks = [
            {"address": hex(BASE + rva), "requestedByteLength": len(data),
             "status": "success", "bytesRead": len(data),
             "bytesBase64": b64(data), "bytesSha256": sha256(data)}
            for rva, data in parts.items()
        ]
        self.save("loaded-code-and-settings-root-v2.json", {
            "identity": identity, "source": {"implementation": {"bundleSha256": "B" * 64}},
            "startedAtUtc": "2026-11-07T15:51:27.6632392Z",
            "completedAtUtc": "2026-11-07T15:51:27.7469719Z",
            "status": "complete", "chunks": chunks,
        })
        for suffix, timestamp in (
            ("a", "2026-11-07T15:51:38.9134000Z"),
            ("b", "2026-11-07T15:51:47.4376733Z"),
        ):
            self.save(f"queue-field-{suffix}-v2.json", {
                "implementation": {"bundleSha256": "B" * 64},
                "completedAtUtc": timestamp,
                "chain": {"rootRva": ROOT_RVA, "offsets": [164]},
                "resolution": {
                    "status": "complete",
                    "expectedIdentity": identity, "observedIdentity": identity,
                    "hops": [{
                        "pointerAddress": BASE + ROOT_RVA,
                        "pointerBytes": b64(PTR.to_bytes(8, "little")),
                        "pointerValue": PTR,
                        "offset": 164, "resolvedAddress": PTR + 164,
                    }],
                    "terminalAddress": PTR + 164,
                    "terminalRead": {"status": "success", "bytes": b64((1).to_bytes(4, "little"))},
                },
            })
        vm = {"vmx": r"c:\rift modding\vms\rift-lab-2\rift-lab.vmx", "pid": 10}
        for name in ("queue-ui-pre-read", "queue-ui-post-read"):
            contents = f"synthetic pixel fixture: {name}".encode()
            (self.folder / name).mkdir()
            (self.folder / name / "before.png").write_bytes(contents)
            self.save(f"{name}/capture.json",
                      {"action": "capture", "imageSha256": sha256(contents)})
            self.save(f"{name}/result.json", {
                "action": "capture", "hostOnly": True, "inputMayHaveBeenSent": False,
                "consoleMutexReleased": True, "beforeIdentity": vm, "afterIdentity": vm,
            })

    def save(self, path: str, value: dict) -> None:
        (self.folder / path).write_text(json.dumps(value), encoding="utf-8")

    def mutate(self, path: str, fn) -> None:
        file = self.folder / path
        value = json.loads(file.read_text(encoding="utf-8"))
        fn(value)
        self.save(path, value)

    def test_source_bytes_match_pinned_build(self) -> None:
        self.assertEqual(
            sha256(SETTER),
            "731E0502754E3DDE57EA0DB34A4EB4ADAD359BA70DDA34D1D5CC609B83EB79A3",
        )

    def test_clean_native_correlator(self) -> None:
        answer = audit(self.folder, "Short", UI_BEFORE, UI_AFTER)
        self.assertEqual(answer["nativeValue"], 1)
        self.assertEqual(answer["loadedCodeWindowsMatched"], 3)
        self.assertEqual(answer["originalImagesHashMatched"], 2)
        self.assertTrue(answer["status"].startswith("native_consistency_pass"))

    def test_wrong_label_rejected(self) -> None:
        with self.assertRaisesRegex(EvidenceError, "conflicts"):
            audit(self.folder, "Full", UI_BEFORE, UI_AFTER)

    def test_future_zero_full_candidate(self) -> None:
        for suffix in ("a", "b"):
            self.mutate(f"queue-field-{suffix}-v2.json",
                        lambda x: x["resolution"]["terminalRead"].update(
                            {"bytes": b64((0).to_bytes(4, "little"))}))
        self.assertEqual(audit(self.folder, "Full", UI_BEFORE, UI_AFTER)["nativeValue"], 0)

    def test_future_two_none_candidate(self) -> None:
        for suffix in ("a", "b"):
            self.mutate(f"queue-field-{suffix}-v2.json",
                        lambda x: x["resolution"]["terminalRead"].update(
                            {"bytes": b64((2).to_bytes(4, "little"))}))
        self.assertEqual(audit(self.folder, "None", UI_BEFORE, UI_AFTER)["nativeValue"], 2)

    def test_changed_process_rejected(self) -> None:
        self.mutate("queue-field-b-v2.json",
                    lambda x: x["resolution"]["observedIdentity"].update({"processId": 3}))
        with self.assertRaisesRegex(EvidenceError, "identity mismatch"):
            audit(self.folder, "Short", UI_BEFORE, UI_AFTER)

    def test_changed_sample_rejected(self) -> None:
        self.mutate("queue-field-b-v2.json",
                    lambda x: x["resolution"]["terminalRead"].update(
                        {"bytes": b64((0).to_bytes(4, "little"))}))
        with self.assertRaisesRegex(EvidenceError, "values changed"):
            audit(self.folder, "Short", UI_BEFORE, UI_AFTER)

    def test_changed_reader_binary_rejected(self) -> None:
        self.mutate("queue-field-b-v2.json",
                    lambda x: x["implementation"].update({"bundleSha256": "A" * 64}))
        with self.assertRaisesRegex(EvidenceError, "reader bundle differs"):
            audit(self.folder, "Short", UI_BEFORE, UI_AFTER)

    def test_snapshot_after_samples_rejected(self) -> None:
        self.mutate("loaded-code-and-settings-root-v2.json",
                    lambda x: x.update({"completedAtUtc": "2026-11-07T15:51:49Z"}))
        with self.assertRaisesRegex(EvidenceError, "preceding loaded-byte snapshot"):
            audit(self.folder, "Short", UI_BEFORE, UI_AFTER)

    def test_changed_root_pointer_rejected(self) -> None:
        self.mutate("queue-field-b-v2.json",
                    lambda x: x["resolution"]["hops"][0].update({"pointerValue": PTR + 8}))
        with self.assertRaisesRegex(EvidenceError, "address arithmetic"):
            audit(self.folder, "Short", UI_BEFORE, UI_AFTER)

    def test_mutated_code_rejected(self) -> None:
        self.mutate("loaded-code-and-settings-root-v2.json",
                    lambda x: x["chunks"][0].update({"bytesBase64": b64(b"\x00" * 39)}))
        with self.assertRaisesRegex(EvidenceError, "SHA mismatch"):
            audit(self.folder, "Short", UI_BEFORE, UI_AFTER)

    def test_unqualified_build_rejected(self) -> None:
        self.mutate("loaded-code-and-settings-root-v2.json",
                    lambda x: x["identity"].update({"executableSha256": "0" * 64}))
        with self.assertRaisesRegex(EvidenceError, "identities differ"):
            audit(self.folder, "Short", UI_BEFORE, UI_AFTER)

    def test_bracket_too_early_rejected(self) -> None:
        with self.assertRaisesRegex(EvidenceError, "outside UI bracket"):
            audit(self.folder, "Short", "2026-11-07T15:51:21Z",
                  "2026-11-07T15:51:40Z")

    def test_image_manifest_mismatch_rejected(self) -> None:
        self.mutate("queue-ui-pre-read/capture.json",
                    lambda x: x.update({"imageSha256": "0" * 64}))
        with self.assertRaisesRegex(EvidenceError, "image SHA mismatch"):
            audit(self.folder, "Short", UI_BEFORE, UI_AFTER)

    def test_vm_identity_change_rejected(self) -> None:
        self.mutate("queue-ui-post-read/result.json",
                    lambda x: x["afterIdentity"].update({"pid": 999}))
        with self.assertRaisesRegex(EvidenceError, "VM identity changed"):
            audit(self.folder, "Short", UI_BEFORE, UI_AFTER)

    def test_two_matching_captures_from_wrong_vm_rejected(self) -> None:
        # Two mutually consistent screenshots still need an exact target VM.
        wrong_vmx = r"c:\rift modding\vms\rift-lab-1\rift-lab.vmx"
        for name in ("queue-ui-pre-read", "queue-ui-post-read"):
            path = f"{name}/result.json"
            record = json.loads((self.folder / path).read_text(encoding="utf-8"))
            record["beforeIdentity"]["vmx"] = wrong_vmx
            record["afterIdentity"]["vmx"] = wrong_vmx
            self.save(path, record)
        with self.assertRaisesRegex(EvidenceError, "capture VMX"):
            audit(self.folder, "Short", UI_BEFORE, UI_AFTER)

    def test_possible_mouse_input_rejected(self) -> None:
        self.mutate("queue-ui-pre-read/result.json",
                    lambda x: x.update({"inputMayHaveBeenSent": True}))
        with self.assertRaisesRegex(EvidenceError, "not an input-free"):
            audit(self.folder, "Short", UI_BEFORE, UI_AFTER)

    def test_unqualified_value_rejected(self) -> None:
        for suffix in ("a", "b"):
            self.mutate(f"queue-field-{suffix}-v2.json",
                        lambda x: x["resolution"]["terminalRead"].update(
                            {"bytes": b64((3).to_bytes(4, "little"))}))
        with self.assertRaisesRegex(EvidenceError, "outside expected"):
            audit(self.folder, "Short", UI_BEFORE, UI_AFTER)


if __name__ == "__main__":
    unittest.main()
