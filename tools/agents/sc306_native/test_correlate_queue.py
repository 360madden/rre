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
        self.save("native-inspection.json", {
            "schemaVersion": 1, "contractVersion": "native-target-inspection/1",
            "target": target, "implementation": {"bundleSha256": "B" * 64},
        })
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
        snapshot_request = {
            "schemaVersion": 1, "evidenceKind": "native-memory-snapshot-request/1",
            "target": {key: target[key] for key in (
                "processId", "processStartUtcTicks", "executableSha256")},
            "maxDurationMilliseconds": 5000,
            "ranges": [{"addressKind": "module-relative-rva",
                        "address": hex(rva), "byteLength": len(data)}
                       for rva, data in parts.items()],
        }
        snapshot_sha = self.save_request("loaded-code-and-settings-root-v2",
                                         snapshot_request)
        self.save("loaded-code-and-settings-root-v2.json", {
            "schemaVersion": 1, "evidenceKind": "native-memory-snapshot/1",
            "identity": identity,
            "source": {"requestEvidenceKind": "native-memory-snapshot-request/1",
                       "implementation": {"bundleSha256": "B" * 64},
                       "requestSha256": snapshot_sha,
                       "requestSha256Verification": "producer-declared"},
            "startedAtUtc": "2026-11-07T15:51:27.6632392Z",
            "completedAtUtc": "2026-11-07T15:51:27.7469719Z",
            "status": "complete", "chunks": chunks,
        })
        for suffix, timestamp in (
            ("a", "2026-11-07T15:51:38.9134000Z"),
            ("b", "2026-11-07T15:51:47.4376733Z"),
        ):
            name = f"queue-field-{suffix}-v2"
            follow_request = {
                "schemaVersion": 1, "evidenceKind": "native-pointer-follow-request/1",
                "target": {key: target[key] for key in (
                    "processId", "processStartUtcTicks", "executableSha256")},
                "rootRva": hex(ROOT_RVA), "offsets": [hex(164)],
                "terminalByteLength": 4, "maxDurationMilliseconds": 5000,
            }
            follow_sha = self.save_request(name, follow_request)
            self.save(f"{name}.json", {
                "schemaVersion": 1, "evidenceKind": "native-pointer-follow/1",
                "requestSha256": follow_sha,
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
        self.refresh_execution_receipts()
        vm = {"vmx": r"c:\rift modding\vms\rift-lab-2\rift-lab.vmx", "pid": 10}
        for name in ("queue-ui-pre-read", "queue-ui-post-read"):
            contents = f"synthetic pixel fixture: {name}".encode()
            (self.folder / name).mkdir()
            (self.folder / name / "before.png").write_bytes(contents)
            self.save(f"{name}/capture.json",
                      {"action": "capture", "imageSha256": sha256(contents)})
            self.save(f"{name}/result.json", {
                "action": "capture", "hostOnly": True, "inputMayHaveBeenSent": False,
                "status": "completed-awaiting-visual-review", "connectionClosed": True,
                "consoleMutexReleased": True, "beforeIdentity": vm, "afterIdentity": vm,
            })

    def save(self, path: str, value: dict) -> None:
        (self.folder / path).write_text(json.dumps(value), encoding="utf-8")

    def save_request(self, stem: str, value: dict) -> str:
        # Guest receives compact JSON with no newline; retained host file has
        # one trailing newline (CRLF in the Windows working checkout).
        guest_bytes = json.dumps(value, separators=(",", ":")).encode("utf-8")
        (self.folder / f"{stem}.request.json").write_bytes(guest_bytes + b"\r\n")
        return sha256(guest_bytes)

    def refresh_execution_receipts(self) -> None:
        names = (
            ("native-inspection", "native-inspection.json", "inspect-native"),
            ("loaded-code-and-settings-root-v2",
             "loaded-code-and-settings-root-v2.json", "snapshot-native"),
            ("queue-field-a-v2", "queue-field-a-v2.json", "follow-pointer"),
            ("queue-field-b-v2", "queue-field-b-v2.json", "follow-pointer"),
        )
        self.save("execution-receipts.json", {"steps": [
            {"name": name, "command": command, "exitCode": 0,
             "ownedRequestAndOutputCleaned": True,
             "outputSha256": sha256((self.folder / filename).read_bytes())}
            for name, filename, command in names
        ]})

    def mutate_request_and_receipts(self, stem: str, change) -> None:
        """Simulate mutually updated producer SHA and native command receipts."""
        path = self.folder / f"{stem}.request.json"
        original = path.read_bytes()
        self.assertTrue(original.endswith(b"\r\n"))
        request = json.loads(original[:-2])
        change(request)
        guest = json.dumps(request, separators=(",", ":")).encode("utf-8")
        path.write_bytes(guest + b"\r\n")
        report_name = f"{stem}.json"
        if stem == "loaded-code-and-settings-root-v2":
            self.mutate(report_name,
                        lambda r: r["source"].update({"requestSha256": sha256(guest)}))
        else:
            self.mutate(report_name,
                        lambda r: r.update({"requestSha256": sha256(guest)}))
        self.refresh_execution_receipts()

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
        self.assertEqual(answer["nativeExecutionReceiptFilesMatched"], 4)
        self.assertEqual(answer["nativeRequestHashesMatched"], 3)
        self.assertTrue(answer["labelMappingQualified"])
        self.assertEqual(answer["loadedCodeWindowsMatched"], 3)
        self.assertEqual(answer["originalImagesHashMatched"], 2)
        self.assertTrue(answer["status"].startswith("native_consistency_pass"))

    def test_git_lf_checkout_of_saved_requests_also_passes(self) -> None:
        for stem in ("loaded-code-and-settings-root-v2",
                     "queue-field-a-v2", "queue-field-b-v2"):
            path = self.folder / f"{stem}.request.json"
            self.assertTrue(path.read_bytes().endswith(b"\r\n"))
            path.write_bytes(path.read_bytes()[:-2] + b"\n")
        self.assertEqual(audit(self.folder, "Short", UI_BEFORE, UI_AFTER)
                         ["nativeRequestHashesMatched"], 3)

    def test_changed_snapshot_request_with_stale_producer_hash_rejected(self) -> None:
        path = self.folder / "loaded-code-and-settings-root-v2.request.json"
        contents = path.read_bytes()
        self.assertIn(b'"maxDurationMilliseconds":5000', contents)
        path.write_bytes(contents.replace(b'"maxDurationMilliseconds":5000',
                                          b'"maxDurationMilliseconds":5001'))
        with self.assertRaisesRegex(EvidenceError, "request SHA mismatch"):
            audit(self.folder, "Short", UI_BEFORE, UI_AFTER)

    def test_changed_pointer_request_with_stale_producer_hash_rejected(self) -> None:
        path = self.folder / "queue-field-b-v2.request.json"
        contents = path.read_bytes()
        self.assertIn(b'"terminalByteLength":4', contents)
        path.write_bytes(contents.replace(b'"terminalByteLength":4',
                                          b'"terminalByteLength":8'))
        with self.assertRaisesRegex(EvidenceError, "request SHA mismatch"):
            audit(self.folder, "Short", UI_BEFORE, UI_AFTER)

    def test_matching_hash_wrong_pointer_request_root_rejected(self) -> None:
        self.mutate_request_and_receipts(
            "queue-field-b-v2", lambda r: r.update({"rootRva": "0x1234"}))
        with self.assertRaisesRegex(EvidenceError, "follow request pointer/field"):
            audit(self.folder, "Short", UI_BEFORE, UI_AFTER)

    def test_matching_hash_wrong_pointer_request_process_rejected(self) -> None:
        self.mutate_request_and_receipts(
            "queue-field-b-v2", lambda r: r["target"].update({"processId": 9999}))
        with self.assertRaisesRegex(EvidenceError, "follow request target differs"):
            audit(self.folder, "Short", UI_BEFORE, UI_AFTER)

    def test_matching_hash_wrong_snapshot_range_rejected(self) -> None:
        self.mutate_request_and_receipts(
            "loaded-code-and-settings-root-v2",
            lambda r: r["ranges"][0].update({"byteLength": 38}))
        with self.assertRaisesRegex(EvidenceError, "snapshot request does not specify"):
            audit(self.folder, "Short", UI_BEFORE, UI_AFTER)

    def test_matching_hash_wrong_snapshot_target_rejected(self) -> None:
        self.mutate_request_and_receipts(
            "loaded-code-and-settings-root-v2",
            lambda r: r["target"].update({"processStartUtcTicks": 1}))
        with self.assertRaisesRegex(EvidenceError, "snapshot request target differs"):
            audit(self.folder, "Short", UI_BEFORE, UI_AFTER)

    def test_matching_hash_wrong_terminal_request_length_rejected(self) -> None:
        self.mutate_request_and_receipts(
            "queue-field-a-v2", lambda r: r.update({"terminalByteLength": 8}))
        with self.assertRaisesRegex(EvidenceError, "follow request pointer/field"):
            audit(self.folder, "Short", UI_BEFORE, UI_AFTER)

    def test_matching_hash_boolean_snapshot_request_schema_rejected(self) -> None:
        self.mutate_request_and_receipts(
            "loaded-code-and-settings-root-v2",
            lambda r: r.update({"schemaVersion": True}))
        with self.assertRaisesRegex(EvidenceError, "snapshot request schema/duration"):
            audit(self.folder, "Short", UI_BEFORE, UI_AFTER)

    def test_matching_hash_boolean_first_follow_request_schema_rejected(self) -> None:
        self.mutate_request_and_receipts(
            "queue-field-a-v2", lambda r: r.update({"schemaVersion": True}))
        with self.assertRaisesRegex(EvidenceError, "follow request pointer/field"):
            audit(self.folder, "Short", UI_BEFORE, UI_AFTER)

    def test_matching_hash_boolean_second_follow_request_schema_rejected(self) -> None:
        self.mutate_request_and_receipts(
            "queue-field-b-v2", lambda r: r.update({"schemaVersion": True}))
        with self.assertRaisesRegex(EvidenceError, "follow request pointer/field"):
            audit(self.folder, "Short", UI_BEFORE, UI_AFTER)

    def test_matching_hash_wrong_native_inspection_contract_rejected(self) -> None:
        self.mutate("native-inspection.json",
                    lambda x: x.update({"contractVersion": "unrelated-contract/99"}))
        self.refresh_execution_receipts()
        with self.assertRaisesRegex(EvidenceError, "inspection schema/contract"):
            audit(self.folder, "Short", UI_BEFORE, UI_AFTER)

    def test_matching_hash_wrong_snapshot_evidence_kind_rejected(self) -> None:
        self.mutate("loaded-code-and-settings-root-v2.json",
                    lambda x: x.update({"evidenceKind": "unrelated-snapshot/99"}))
        self.refresh_execution_receipts()
        with self.assertRaisesRegex(EvidenceError, "snapshot schema/evidence kind"):
            audit(self.folder, "Short", UI_BEFORE, UI_AFTER)

    def test_matching_hash_wrong_snapshot_request_kind_rejected(self) -> None:
        self.mutate("loaded-code-and-settings-root-v2.json",
                    lambda x: x["source"].update({"requestEvidenceKind": "wrong/99"}))
        self.refresh_execution_receipts()
        with self.assertRaisesRegex(EvidenceError, "snapshot schema/evidence kind"):
            audit(self.folder, "Short", UI_BEFORE, UI_AFTER)

    def test_matching_hash_wrong_follow_report_kind_rejected(self) -> None:
        self.mutate("queue-field-b-v2.json",
                    lambda x: x.update({"evidenceKind": "unrelated-follow/99"}))
        self.refresh_execution_receipts()
        with self.assertRaisesRegex(EvidenceError, "pointer report schema/evidence kind"):
            audit(self.folder, "Short", UI_BEFORE, UI_AFTER)

    def test_duplicate_native_status_with_matched_receipts_rejected(self) -> None:
        # Python's default JSON decoder silently keeps the last duplicate key.
        path = self.folder / "queue-field-b-v2.json"
        original = path.read_text(encoding="utf-8")
        self.assertIn('"status": "complete"', original)
        path.write_text(original.replace('"status": "complete"',
                                         '"status": "failed", "status": "complete"', 1),
                        encoding="utf-8")
        self.refresh_execution_receipts()
        with self.assertRaisesRegex(EvidenceError, "duplicate JSON key: status"):
            audit(self.folder, "Short", UI_BEFORE, UI_AFTER)

    def test_duplicate_saved_request_key_with_updated_hash_rejected(self) -> None:
        path = self.folder / "queue-field-b-v2.request.json"
        original = path.read_bytes()
        old_key = b'"evidenceKind":"native-pointer-follow-request/1"'
        self.assertIn(old_key, original)
        modified = original.replace(
            old_key, b'"evidenceKind":"wrong","evidenceKind":"native-pointer-follow-request/1"', 1)
        self.assertTrue(modified.endswith(b"\r\n"))
        path.write_bytes(modified)
        self.mutate("queue-field-b-v2.json",
                    lambda x: x.update({"requestSha256": sha256(modified[:-2])}))
        self.refresh_execution_receipts()
        with self.assertRaisesRegex(EvidenceError, "duplicate JSON key: evidenceKind"):
            audit(self.folder, "Short", UI_BEFORE, UI_AFTER)

    def test_changed_inspection_bytes_with_stale_receipt_rejected(self) -> None:
        self.mutate("native-inspection.json",
                    lambda x: x.update({"unboundProvenanceMarker": "different bytes"}))
        with self.assertRaisesRegex(EvidenceError, "receipt SHA mismatch"):
            audit(self.folder, "Short", UI_BEFORE, UI_AFTER)

    def test_missing_native_receipt_rejected(self) -> None:
        (self.folder / "execution-receipts.json").unlink()
        with self.assertRaisesRegex(EvidenceError, "execution-receipts"):
            audit(self.folder, "Short", UI_BEFORE, UI_AFTER)

    def test_missing_one_receipt_step_rejected(self) -> None:
        self.mutate("execution-receipts.json",
                    lambda x: x["steps"].pop())
        with self.assertRaisesRegex(EvidenceError, "execution receipt steps"):
            audit(self.folder, "Short", UI_BEFORE, UI_AFTER)

    def test_failed_receipt_step_rejected(self) -> None:
        self.mutate("execution-receipts.json",
                    lambda x: x["steps"][0].update({"exitCode": 1}))
        with self.assertRaisesRegex(EvidenceError, "execution receipt step incomplete"):
            audit(self.folder, "Short", UI_BEFORE, UI_AFTER)

    def test_wrong_label_rejected(self) -> None:
        with self.assertRaisesRegex(EvidenceError, "conflicts"):
            audit(self.folder, "Full", UI_BEFORE, UI_AFTER)

    def test_future_zero_full_candidate(self) -> None:
        for suffix in ("a", "b"):
            self.mutate(f"queue-field-{suffix}-v2.json",
                        lambda x: x["resolution"]["terminalRead"].update(
                            {"bytes": b64((0).to_bytes(4, "little"))}))
        self.refresh_execution_receipts()
        for label in ("Full", "None"):
            answer = audit(self.folder, label, UI_BEFORE, UI_AFTER)
            self.assertEqual(answer["nativeValue"], 0)
            self.assertFalse(answer["labelMappingQualified"])
            self.assertEqual(answer["status"], "native_value_consistent_mapping_unverified")

    def test_future_two_none_candidate(self) -> None:
        for suffix in ("a", "b"):
            self.mutate(f"queue-field-{suffix}-v2.json",
                        lambda x: x["resolution"]["terminalRead"].update(
                            {"bytes": b64((2).to_bytes(4, "little"))}))
        self.refresh_execution_receipts()
        for label in ("None", "Full"):
            answer = audit(self.folder, label, UI_BEFORE, UI_AFTER)
            self.assertEqual(answer["nativeValue"], 2)
            self.assertFalse(answer["labelMappingQualified"])
            self.assertEqual(answer["status"], "native_value_consistent_mapping_unverified")

    def test_changed_process_rejected(self) -> None:
        self.mutate("queue-field-b-v2.json",
                    lambda x: x["resolution"]["observedIdentity"].update({"processId": 3}))
        with self.assertRaisesRegex(EvidenceError, "identity mismatch"):
            audit(self.folder, "Short", UI_BEFORE, UI_AFTER)

    def test_malformed_process_identity_rejected(self) -> None:
        # A corrupt reader record must be rejected as evidence, not crash parsing.
        self.mutate("queue-field-a-v2.json",
                    lambda x: x["resolution"]["observedIdentity"].update(
                        {"processId": "not-a-number"}))
        with self.assertRaisesRegex(EvidenceError, "process identity mismatch"):
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

    def test_changed_inspection_bundle_rejected(self) -> None:
        self.mutate("native-inspection.json",
                    lambda x: x["implementation"].update({"bundleSha256": "A" * 64}))
        with self.assertRaisesRegex(EvidenceError, "inspection reader bundle differs"):
            audit(self.folder, "Short", UI_BEFORE, UI_AFTER)

    def test_missing_inspection_bundle_rejected(self) -> None:
        self.mutate("native-inspection.json",
                    lambda x: x.pop("implementation"))
        with self.assertRaisesRegex(EvidenceError, "inspection reader bundle differs"):
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

    def test_failed_capture_status_rejected(self) -> None:
        self.mutate("queue-ui-post-read/result.json",
                    lambda x: x.update({"status": "failed"}))
        with self.assertRaisesRegex(EvidenceError, "capture not completed"):
            audit(self.folder, "Short", UI_BEFORE, UI_AFTER)

    def test_missing_capture_status_rejected(self) -> None:
        self.mutate("queue-ui-pre-read/result.json",
                    lambda x: x.pop("status"))
        with self.assertRaisesRegex(EvidenceError, "capture not completed"):
            audit(self.folder, "Short", UI_BEFORE, UI_AFTER)

    def test_unclosed_capture_connection_rejected(self) -> None:
        self.mutate("queue-ui-post-read/result.json",
                    lambda x: x.update({"connectionClosed": False}))
        with self.assertRaisesRegex(EvidenceError, "capture not completed"):
            audit(self.folder, "Short", UI_BEFORE, UI_AFTER)

    def test_contradictory_failed_read_rejected(self) -> None:
        self.mutate("queue-field-b-v2.json",
                    lambda x: x["resolution"].update({
                        "failedRead": {"status": "failed", "reason": "access denied"}}))
        with self.assertRaisesRegex(EvidenceError, "conflicting failure metadata"):
            audit(self.folder, "Short", UI_BEFORE, UI_AFTER)

    def test_contradictory_failed_address_rejected(self) -> None:
        self.mutate("queue-field-b-v2.json",
                    lambda x: x["resolution"].update({
                        "failedReadAddress": PTR + 164}))
        with self.assertRaisesRegex(EvidenceError, "conflicting failure metadata"):
            audit(self.folder, "Short", UI_BEFORE, UI_AFTER)

    def test_contradictory_resolution_reason_rejected_with_matched_receipts(self) -> None:
        # A completed native read cannot simultaneously report a failure reason.
        self.mutate("queue-field-b-v2.json",
                    lambda x: x["resolution"].update({"reason": "access denied"}))
        self.refresh_execution_receipts()
        with self.assertRaisesRegex(EvidenceError, "conflicting failure metadata"):
            audit(self.folder, "Short", UI_BEFORE, UI_AFTER)

    def test_terminal_win32_error_rejected(self) -> None:
        self.mutate("queue-field-b-v2.json",
                    lambda x: x["resolution"]["terminalRead"].update({
                        "win32ErrorCode": 5}))
        with self.assertRaisesRegex(EvidenceError, "terminal read reports error"):
            audit(self.folder, "Short", UI_BEFORE, UI_AFTER)

    def test_terminal_failure_reason_rejected(self) -> None:
        self.mutate("queue-field-b-v2.json",
                    lambda x: x["resolution"]["terminalRead"].update({
                        "reason": "invalid read"}))
        with self.assertRaisesRegex(EvidenceError, "terminal read reports error"):
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
