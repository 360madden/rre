#!/usr/bin/env python3
"""Fail-closed, offline-only source-byte gate for RIFT postpatch ROOT001 B route.

This gate does not establish runtime callback selection, object identity, or process compatibility.
"""
from __future__ import annotations

import hashlib
import json
import struct
import sys
from pathlib import Path

from rift_update_analyzer import FailClosedParser, InspectionError, bytes_at_rva, inspect_pe, sha_range, stamp

BUILD_SHA256 = "df954b798331e18359be62a31cc74b49fc3f50b87385ebb080a5448256322c01"
BUILD_BYTES = 60574536
DEFAULT_PE = Path("C:/work/RIFT-Build-Baselines") / BUILD_SHA256 / "rift_x64.exe"
EXPECTED_VPTR_SHA = "98e45c8e5dedb228c98e30cc58c17208fb094e0d7f23d788feb683351a00288e"
EXPECTED_B_PREFIX_SHA = "3069ebf7d3d72c4dd9882ebe0b5101edc8cbb831155909af619661443db3cbb8"
EXPECTED_CALL_TARGET = 0x788B00
EXPECTED_B_ENTRY = 0xFCA0A0
VTABLE_RVA = 0x2721518
PREFIX_END_RVA = 0xFCA485
# RIP-relative LEA followed by a separate vptr store (static constructor/cleanup candidates).
VTABLE_ASSIGNMENTS = (
    (0xFC918A, 0xFC9199, "488903"),
    (0xFC939F, 0xFC93A9, "488901"),
)

# Strict bytes at each mapped RVA: static evidence only, never a live address.
OPCODES = (
    ("dispatch_forwards_rdx_and_virtual_slot_18", 0x77A17D, "488b542450ff5018"),
    ("adapter_B_saves_host_R13", 0xFCA0EF, "4c8bea"),
    ("adapter_B_restores_RCX", 0xFCA47D, "498bcd"),
    ("processor_receiver_RBP_from_RCX", 0x788B1C, "488be9"),
    ("processor_reads_receiver_field_6A8", 0x788C04, "488b8da8060000"),
)


# Postpatch state-transition operand drift, independently compared to old build.
# These are exact NEW-build bytes, not a qualified object layout or gameplay meaning.
STATE_DELTA_OPCODES = (
    ("state_one_compare_field_18", 0xFCAA3F, "83781801"),
    ("state_one_mark_flag_80", 0xFCAA45, "81481080000000"),
    ("state_one_write_field_18", 0xFCAA4C, "c7401801000000"),
    ("state_zero_compare_field_18", 0xFCAA7B, "83781800"),
    ("state_zero_mark_flag_80", 0xFCAA81, "81481080000000"),
    ("state_zero_write_field_18", 0xFCAA88, "895818"),
)


class GateError(Exception):
    pass


def assert_bytes(read, rva: int, expected: bytes, label: str) -> None:
    actual = read(rva, len(expected))
    if actual != expected:
        raise GateError(f"{label} at RVA 0x{rva:X}: expected {expected.hex()}, "
                        f"observed {actual.hex() if actual is not None else 'unmapped'}")


def verify_source(read) -> dict:
    for label, rva, opcode in OPCODES + STATE_DELTA_OPCODES:
        assert_bytes(read, rva, bytes.fromhex(opcode), label)

    vptr = read(VTABLE_RVA, 56)
    if vptr is None or hashlib.sha256(vptr).hexdigest() != EXPECTED_VPTR_SHA:
        raise GateError("The exact seven-QWORD adapter B vtable source-window hash changed")
    pointer = struct.unpack_from("<Q", vptr, 0x18)[0]
    if pointer != 0x140000000 + EXPECTED_B_ENTRY:
        raise GateError("Adapter B slot +0x18 no longer targets the expected candidate entry")

    for lea_rva, store_rva, store_hex in VTABLE_ASSIGNMENTS:
        lea = read(lea_rva, 7)
        if lea is None or lea[:3] != bytes.fromhex("488d05"):
            raise GateError(f"Expected RIP-relative vptr LEA at 0x{lea_rva:X}")
        target = lea_rva + 7 + struct.unpack_from("<i", lea, 3)[0]
        if target != VTABLE_RVA:
            raise GateError(f"Vptr assignment LEA targets 0x{target:X}, not 0x{VTABLE_RVA:X}")
        assert_bytes(read, store_rva, bytes.fromhex(store_hex), "vptr store")

    prefix = read(EXPECTED_B_ENTRY, PREFIX_END_RVA - EXPECTED_B_ENTRY)
    if prefix is None or hashlib.sha256(prefix).hexdigest() != EXPECTED_B_PREFIX_SHA:
        raise GateError("Adapter B source-prefix hash changed")

    call_rva = 0xFCA480
    call = read(call_rva, 5)
    if call is None or call[0] != 0xE8:
        raise GateError("Adapter B processor call is not a direct rel32 CALL")
    target = call_rva + 5 + struct.unpack_from("<i", call, 1)[0]
    if target != EXPECTED_CALL_TARGET:
        raise GateError(f"Adapter B call target changed to 0x{target:X}")

    return {
        "status": "SOURCE_PINNED_ONLY",
        "newBuildSha256": BUILD_SHA256,
        "checkedOpcodes": len(OPCODES),
        "checkedStateDeltaOpcodes": len(STATE_DELTA_OPCODES),
        "vtableAssignmentCandidates": len(VTABLE_ASSIGNMENTS),
        "vtableRva": f"0x{VTABLE_RVA:X}",
        "vtableVirtualSlot": "+0x18",
        "adapterEntryCandidateRva": f"0x{EXPECTED_B_ENTRY:X}",
        "processorCandidateRva": f"0x{target:X}",
        "receiverFieldOffset": "+0x6A8",
        "functionIdentityQualified": False,
        "runtimeQualified": False,
    }


def main(argv: list[str] | None = None) -> int:
    parser = FailClosedParser(description=__doc__)
    parser.add_argument("--pe", type=Path, default=DEFAULT_PE, help="Archived, offline updated RIFT PE")
    args = parser.parse_args(argv)
    try:
        before = stamp(args.pe)
        if before[0] != BUILD_BYTES:
            raise GateError(f"Wrong file size {before[0]}, expected {BUILD_BYTES}")
        digest = sha_range(args.pe)
        if digest != BUILD_SHA256:
            raise GateError("Wrong build SHA-256: " + digest)
        pe = inspect_pe(args.pe, before[0])
        result = verify_source(lambda rva, length: bytes_at_rva(args.pe, pe, rva, length))
        if stamp(args.pe) != before or sha_range(args.pe) != BUILD_SHA256:
            raise GateError("Source file changed during verification")
        print(json.dumps(result, sort_keys=True))
        return 0
    except (GateError, InspectionError, OSError, ValueError, struct.error) as exc:
        print(json.dumps({"status": "ERROR", "runtimeQualified": False,
                          "functionIdentityQualified": False, "message": str(exc)},
                         sort_keys=True), file=sys.stderr)
        return 3


if __name__ == "__main__":
    sys.exit(main())
