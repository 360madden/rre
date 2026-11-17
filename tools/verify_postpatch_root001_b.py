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

# Postpatch host selector source chain (static only; active receiver not qualified).
SELECTOR_VTABLE_RVA = 0x26CD000
SELECTOR_VTABLE_CALL_OFFSET = 0xB8
SELECTOR_IMPL_RVA = 0x7664D0
SELECTOR_LEA_RVA = 0x75D4EE
SELECTOR_OPCODES = (
    ("host_vptr_store", 0x75D4F5, "488908"),
    ("host_selector_virtual_slot_B8", 0x776740, "ff90b8000000"),
    ("selector_add_registry_offset_240", 0x7664EC, "480540020000"),
)

# Normal host construction and two InGame activation paths. These are source-only
# anchors: even exact matches do not prove a currently running instance selected B.
HOST_STATE_OPCODES = (
    ("host_factory_allocation_0xA50", 0x762394, "b9500a0000"),
    ("host_constructor_vptr_store", 0x75BE8B, "488908"),
    ("ingame_A_local_SSO_RDX", 0xFCEFF7, "488d55df"),
    ("ingame_A_host_R13_RCX", 0xFCEFFB, "498bcd"),
    ("ingame_B_getter_result_RCX", 0xFCF5C7, "488bc8"),
    ("ingame_B_local_SSO_RDX", 0xFCF5CA, "488d542430"),
)
# Path A InGame guard control-flow anchors in SHA-pinned archived source.
# These pin observed native predicates/branches, not their gameplay meaning.
INGAME_A_GUARD_OPCODES = (
    ("ingame_A_entry_context_RSI", 0xFCE941, "488bf1"),
    ("ingame_A_entry_host_R13", 0xFCE944, "4c8bea"),
    ("ingame_A_r14_initial_zero", 0xFCEE87, "4532f6"),
    ("ingame_A_r15_reloaded", 0xFCEE9E, "4c8b7dd7"),
    ("ingame_A_r14_conditional_true", 0xFCEEED, "41b601"),
    ("ingame_A_r14_bypass_or_fallback", 0xFCEF24, "4584f67516"),
    ("ingame_A_r15_must_be_zero_in_fallback", 0xFCEF29, "4585ff0f8522010000"),
    ("ingame_A_fallback_predicate_required", 0xFCEF37, "84c00f8415010000"),
    ("ingame_A_state_value_two_required", 0xFCEF44, "8338020f8507010000"),
    ("ingame_A_context_field_48_and_null", 0xFCEF4D, "488b4e484885c9"),
    ("ingame_A_null_context_skips_predicate", 0xFCEF54, "740d"),
    ("ingame_A_context_predicate_required", 0xFCEF5B, "84c00f84f1000000"),
)
INGAME_A_GUARD_CALL_TARGETS = (
    ("ingame_A_r15_provider", 0xFCEA55, 0x1593510),
    ("ingame_A_r15_value", 0xFCEA5D, 0x1593070),
    ("ingame_A_fallback_predicate", 0xFCEF32, 0xFA3940),
    ("ingame_A_state_value_provider", 0xFCEF3F, 0x4C4180),
    ("ingame_A_context_predicate", 0xFCEF56, 0x81BFF0),
)

# Exact Path A context predicate internals; semantic meaning remains unknown.
INGAME_CONTEXT_PREDICATE_OPCODES = (
    ("context_override_byte_3A", 0x81BFF4, "80793a007527"),
    ("context_null_object_field_10", 0x81C002, "48837910ff0f95c0"),
    ("context_object_field_38", 0x81C00F, "807938007513"),
)
INGAME_CONTEXT_PREDICATE_CALL_TARGETS = (
    ("context_delegates_to_object_predicate", 0x81C018, 0x81F5F0),
)

# Path A state source: mutator called with 1 can take a guarded state-1
# branch whose helper writes 2. This is a source-only conditional path.
INGAME_A_STATE12_OPCODES = (
    ("ingame_A_mutator_receives_one", 0xFCEA3B, "488bc8ba01000000"),
    ("ingame_A_mutator_reads_prior_state", 0x9D57D7, "8b01"),
    ("ingame_A_prior_state_one_branch", 0x9D5818, "83f8017512"),
    ("ingame_A_helper_checks_state_one", 0x9D58C5, "833901"),
    ("ingame_A_helper_checks_pointer_8_null", 0x9D58D1, "48837908007519"),
    ("ingame_A_helper_writes_state_two", 0x9D58D8, "c70102000000"),
)
INGAME_A_STATE12_CALL_TARGETS = (
    ("ingame_A_prior_state_getter", 0xFCEA2F, 0x4C4180),
    ("ingame_A_mutator_target_getter", 0xFCEA36, 0x4C4180),
    ("ingame_A_state_mutator", 0xFCEA43, 0x9D57D0),
    ("ingame_A_state_one_helper", 0x9D5823, 0x9D58B0),
)

INGAME_STATE_MANAGER_OPCODES = (
    ("state_zero_guard", 0x9D5C85, "833900"),
    ("state_zero_to_one_write", 0x9D5CAD, "48c70101000000"),
    ("state_one_to_two_alternative_write", 0x9D5C14, "c70702000000"),
    ("state_two_to_three_write", 0x9D5839, "48c70303000000"),
    ("state_three_manager_guard", 0x9D5883, "83f803"),
    ("state_three_manager_receiver", 0x9D5888, "488bcb"),
    ("state_three_manager_postcall_zero", 0x9D5890, "833b00"),
    ("state_three_manager_retry_nonzero", 0x9D5893, "75f3"),
    ("state_three_helper_guard", 0x9D6FDE, "833903"),
    ("state_three_helper_saved_receiver", 0x9D6FE1, "488bf9"),
    ("state_three_helper_zero_esi", 0x9D76F9, "33f6"),
    ("state_three_helper_state_zero_write", 0x9D77C4, "8937"),
)
INGAME_STATE_MANAGER_CALL_TARGETS = (
    ("state_zero_initialization_helper", 0x9D580E, 0x9D5C60),
    ("state_three_cleanup_helper", 0x9D588B, 0x9D6FC0),
)

HOST_RIP_LEA_TARGETS = (
    ("host_constructor_vtable", 0x75BE84, "488d0d", SELECTOR_VTABLE_RVA),
    ("ingame_A_literal", 0xFCEF8F, "488d15", 0x26B5FD0),
    ("ingame_B_literal", 0xFCF558, "488d15", 0x26B5FD0),
    ("host_global_getter", 0x766494, "488d0d", 0x3383CB0),
)
HOST_CALL_TARGETS = (
    ("host_factory_constructor", 0x7623B0, 0x75BE50),
    ("ingame_A_state_setter", 0xFCEFFE, 0x77DC50),
    ("ingame_B_host_getter", 0xFCF5C2, 0x766490),
    ("ingame_B_state_setter", 0xFCF5CF, 0x77DC50),
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
    for label, rva, opcode in (OPCODES + STATE_DELTA_OPCODES + SELECTOR_OPCODES
                               + HOST_STATE_OPCODES + INGAME_A_GUARD_OPCODES
                               + INGAME_A_STATE12_OPCODES + INGAME_CONTEXT_PREDICATE_OPCODES
                               + INGAME_STATE_MANAGER_OPCODES):
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

    selector_lea = read(SELECTOR_LEA_RVA, 7)
    if selector_lea is None or selector_lea[:3] != bytes.fromhex("488d0d"):
        raise GateError("Expected host selector vptr RIP-relative LEA")
    selector_table = SELECTOR_LEA_RVA + 7 + struct.unpack_from("<i", selector_lea, 3)[0]
    if selector_table != SELECTOR_VTABLE_RVA:
        raise GateError(f"Host selector LEA targets 0x{selector_table:X}, not 0x{SELECTOR_VTABLE_RVA:X}")
    selector_slot = read(SELECTOR_VTABLE_RVA + SELECTOR_VTABLE_CALL_OFFSET, 8)
    if selector_slot is None or struct.unpack("<Q", selector_slot)[0] != 0x140000000 + SELECTOR_IMPL_RVA:
        raise GateError("Host selector vtable +0xB8 target changed or is unmapped")

    for label, rva, lea_prefix, expected_target in HOST_RIP_LEA_TARGETS:
        lea = read(rva, 7)
        if lea is None or lea[:3] != bytes.fromhex(lea_prefix):
            raise GateError(f"{label}: expected RIP-relative LEA at 0x{rva:X}")
        target = rva + 7 + struct.unpack_from("<i", lea, 3)[0]
        if target != expected_target:
            raise GateError(f"{label}: LEA targets 0x{target:X}, expected 0x{expected_target:X}")
    assert_bytes(read, 0x26B5FD0, b"InGame\x00", "InGame state-key literal")
    for label, rva, expected_target in (HOST_CALL_TARGETS + INGAME_A_GUARD_CALL_TARGETS
                                               + INGAME_A_STATE12_CALL_TARGETS
                                                + INGAME_CONTEXT_PREDICATE_CALL_TARGETS
                                                + INGAME_STATE_MANAGER_CALL_TARGETS):
        call = read(rva, 5)
        if call is None or call[0] != 0xE8:
            raise GateError(f"{label}: expected direct call at 0x{rva:X}")
        target = rva + 5 + struct.unpack_from("<i", call, 1)[0]
        if target != expected_target:
            raise GateError(f"{label}: direct call targets 0x{target:X}, expected 0x{expected_target:X}")

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
        "checkedSelectorOpcodes": len(SELECTOR_OPCODES),
        "checkedHostStateOpcodes": len(HOST_STATE_OPCODES),
        "checkedHostLeaTargets": len(HOST_RIP_LEA_TARGETS),
        "checkedHostCallTargets": len(HOST_CALL_TARGETS),
        "checkedInGameAGuardOpcodes": len(INGAME_A_GUARD_OPCODES),
        "checkedInGameAGuardCallTargets": len(INGAME_A_GUARD_CALL_TARGETS),
        "inGameAGuardsSourcePinned": True,
        "checkedInGameAState12Opcodes": len(INGAME_A_STATE12_OPCODES),
        "checkedInGameAState12CallTargets": len(INGAME_A_STATE12_CALL_TARGETS),
        "inGameAState12SourcePinned": True,
        "checkedContextPredicateOpcodes": len(INGAME_CONTEXT_PREDICATE_OPCODES),
        "checkedContextPredicateCallTargets": len(INGAME_CONTEXT_PREDICATE_CALL_TARGETS),
        "contextPredicateSourcePinned": True,
        "checkedStateManagerOpcodes": len(INGAME_STATE_MANAGER_OPCODES),
        "checkedStateManagerCallTargets": len(INGAME_STATE_MANAGER_CALL_TARGETS),
        "stateManagerSourcePinned": True,
        "stateThreeToZeroSourcePinned": True,
        "hostConstructionSourcePinned": True,
        "inGameTransitionsSourcePinned": True,
        "selectorSourcePinned": True,
        "selectorVtableRva": f"0x{SELECTOR_VTABLE_RVA:X}",
        "selectorCandidateRva": f"0x{SELECTOR_IMPL_RVA:X}",
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
