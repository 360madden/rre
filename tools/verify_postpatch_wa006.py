#!/usr/bin/env python3
"""Read-only, fail-closed new-build WA-006 source-window and direct-call verification.

Success validates only archived static bytes and rel32 edges. It is not live or owner evidence.
"""
from __future__ import annotations

import hashlib
import json
import struct
import sys
from pathlib import Path

from rift_update_analyzer import (FailClosedParser, InspectionError, bytes_at_rva,
                                  inspect_pe, sha_range, stamp)

BUILD_SHA256 = "df954b798331e18359be62a31cc74b49fc3f50b87385ebb080a5448256322c01"
BUILD_BYTES = 60574536
MANIFEST_SHA256 = "a8b8dbc2e5652af9b89849345c442ab6c9a6b50288d623237f45b9b5bd9b7f08"
DEFAULT_PE = Path("C:/work/RIFT-Build-Baselines") / BUILD_SHA256 / "rift_x64.exe"
DEFAULT_MANIFEST = Path(__file__).with_name("postpatch_wa006_source_map.json")
REQUIRED_WINDOWS = frozenset(("callback", "wrapper_ctor", "wrapper", "base_ctor",
                              "helper", "parent", "virtual_adapter"))
REQUIRED_CALLS = frozenset(("callback_to_wrapper_ctor", "callback_to_wrapper",
                            "wrapper_ctor_to_base_ctor", "wrapper_to_helper",
                            "helper_to_parent", "parent_to_query",
                            "parent_to_virtual_adapter"))


# The wrapper constructor points at 0x271E468. Five distinct constructor
# LEAs point eight bytes later, at 0x271E470. Method pointers in this shared
# region cannot establish which object dispatches through the method.
WRAPPER_VPTR_RVA = 0x271E468
WRAPPER_VPTR_LEA_RVA = 0xF7CC2E
WRAPPER_VPTR_STORE_RVA = 0xF7CC3F
ADJACENT_VPTR_RVA = 0x271E470
ADJACENT_CTOR_LEA_RVAS = (0xF7D735, 0xF7D9EC, 0xF7DACA, 0xF7DBAA, 0xF835A4)
OVERLAPPING_METHOD_POINTER_RVAS = (0x271E480, 0x271E498, 0x271E4C0)
CANDIDATE_METHOD_RVA = 0x78D920
CANDIDATE_METHOD_BYTES = bytes.fromhex("c7411800000000c74108eeff7f7fc3")


class GateError(Exception):
    pass


def parse_rva(value: str) -> int:
    if not isinstance(value, str) or not value.startswith("0x"):
        raise GateError("RVA must be a 0x-prefixed hexadecimal string")
    try:
        number = int(value, 16)
    except ValueError as exc:
        raise GateError("Invalid hexadecimal RVA") from exc
    if not 0x1000 <= number <= 0xFFFFFFFF:
        raise GateError("RVA outside bounded supported range")
    return number


def verify_source(read, manifest: dict) -> dict:
    if not isinstance(manifest, dict):
        raise GateError("Manifest root must be an object")
    if (manifest.get("schemaVersion") != 1 or
        manifest.get("buildSha256") != BUILD_SHA256 or
        manifest.get("buildBytes") != BUILD_BYTES or
        manifest.get("runtimeQualified") is not False or
        manifest.get("ownerQualified") is not False):
        raise GateError("Manifest build/scope identity differs from pinned new build")
    windows = manifest.get("windows")
    calls = manifest.get("directCalls")
    if (not isinstance(windows, list) or not isinstance(calls, list) or
        any(not isinstance(w, dict) for w in windows) or
        any(not isinstance(c, dict) for c in calls)):
        raise GateError("Source windows and rel32 calls must be object arrays")
    if {w.get("id") for w in windows} != REQUIRED_WINDOWS or len(windows) != len(REQUIRED_WINDOWS):
        raise GateError("Window IDs must match exact postpatch scope")
    if {c.get("id") for c in calls} != REQUIRED_CALLS or len(calls) != len(REQUIRED_CALLS):
        raise GateError("Call IDs must match exact postpatch scope")

    for window in windows:
        rva = parse_rva(window["rva"])
        length = window["length"]
        digest = window["sha256"]
        if type(length) is not int or not 1 <= length <= 4096 or not isinstance(digest, str) or len(digest) != 64:
            raise GateError("Invalid source window extent/hash")
        data = read(rva, length)
        if data is None or hashlib.sha256(data).hexdigest() != digest:
            raise GateError(f"Source window {window['id']} differs at 0x{rva:X}")

    for edge in calls:
        source = parse_rva(edge["callRva"])
        expected_target = parse_rva(edge["targetRva"])
        raw = read(source, 5)
        if raw is None or len(raw) != 5 or raw[0] != 0xE8:
            raise GateError(f"Direct CALL opcode absent for {edge['id']} at 0x{source:X}")
        target = source + 5 + struct.unpack_from("<i", raw, 1)[0]
        if target != expected_target:
            raise GateError(f"Direct CALL {edge['id']} target 0x{target:X}, expected 0x{expected_target:X}")

    def require_vptr_lea(source_rva: int, expected_target: int, label: str) -> None:
        lea = read(source_rva, 7)
        if lea is None or len(lea) != 7 or lea[:3] != bytes.fromhex("488d05"):
            raise GateError(f"{label} constructor vtable LEA absent")
        target = source_rva + 7 + struct.unpack_from("<i", lea, 3)[0]
        if target != expected_target:
            raise GateError(f"{label} constructor vtable target differs: 0x{target:X}")

    require_vptr_lea(WRAPPER_VPTR_LEA_RVA, WRAPPER_VPTR_RVA, "Wrapper")
    if read(WRAPPER_VPTR_STORE_RVA, 3) != bytes.fromhex("488903"):
        raise GateError("Wrapper constructor vptr store differs")
    for source_rva in ADJACENT_CTOR_LEA_RVAS:
        require_vptr_lea(source_rva, ADJACENT_VPTR_RVA, "Adjacent")
    for pointer_rva in OVERLAPPING_METHOD_POINTER_RVAS:
        entry = read(pointer_rva, 8)
        if entry is None or len(entry) != 8 or struct.unpack("<Q", entry)[0] != 0x140000000 + CANDIDATE_METHOD_RVA:
            raise GateError(f"Overlapping method pointer differs at 0x{pointer_rva:X}")
    if read(CANDIDATE_METHOD_RVA, len(CANDIDATE_METHOD_BYTES)) != CANDIDATE_METHOD_BYTES:
        raise GateError("Candidate virtual method source bytes differ")

    return {"status": "SOURCE_MAP_PINNED_ONLY", "newBuildSha256": BUILD_SHA256,
            "sourceWindowsChecked": len(windows), "directCallsChecked": len(calls),
            "adjacentConstructorLeasChecked": len(ADJACENT_CTOR_LEA_RVAS),
            "overlappingMethodPointersChecked": len(OVERLAPPING_METHOD_POINTER_RVAS),
            "candidateMethodBytesPinned": True,
            "sameWrapperField8WriterQualified": False,
            "ownerQualified": False, "runtimeQualified": False}


def main(argv: list[str] | None = None) -> int:
    parser = FailClosedParser(description=__doc__)
    parser.add_argument("--pe", type=Path, default=DEFAULT_PE)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    args = parser.parse_args(argv)
    try:
        old_stamp = stamp(args.pe)
        if old_stamp[0] != BUILD_BYTES or sha_range(args.pe) != BUILD_SHA256:
            raise GateError("Wrong archived executable version or hash")
        manifest_bytes = args.manifest.read_bytes()
        if len(manifest_bytes) > 1024 * 1024 or hashlib.sha256(manifest_bytes).hexdigest() != MANIFEST_SHA256:
            raise GateError("WA-006 evidence manifest hash differs")
        manifest = json.loads(manifest_bytes)
        pe = inspect_pe(args.pe, old_stamp[0])
        result = verify_source(lambda rva, length: bytes_at_rva(args.pe, pe, rva, length), manifest)
        if (stamp(args.pe) != old_stamp or sha_range(args.pe) != BUILD_SHA256 or
            sha_range(args.manifest) != MANIFEST_SHA256):
            raise GateError("Archived input changed during verification")
        print(json.dumps(result, sort_keys=True))
        return 0
    except (GateError, InspectionError, OSError, ValueError, KeyError, TypeError, struct.error) as exc:
        print(json.dumps({"status": "ERROR", "ownerQualified": False,
                          "runtimeQualified": False, "message": str(exc)}, sort_keys=True), file=sys.stderr)
        return 3


if __name__ == "__main__":
    sys.exit(main())
