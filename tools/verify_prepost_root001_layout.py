#!/usr/bin/env python3
"""Offline, fail-closed OLD/NEW RIFT ROOT001 B layout comparison.

Exact archived PE provenance and source-byte/target checks only. No game, process,
runtime receiver identity, or behavioral qualification is implied.
"""
from __future__ import annotations

import json
import struct
import sys
from pathlib import Path

from rift_update_analyzer import (
    FailClosedParser, InspectionError, bytes_at_rva, inspect_pe, sha_range, stamp,
)

ARCHIVE_ROOT = Path("C:/work/RIFT-Build-Baselines")
OLD_SHA256 = "1935a05c9db6d468e34e0055014a4a99c1b5afceb1695884e24600f5c20a4be8"
NEW_SHA256 = "df954b798331e18359be62a31cc74b49fc3f50b87385ebb080a5448256322c01"
IMAGE_BASE = 0x140000000

# Each checked RVA is a *source* RVA, not an address in a running game.
BUILDS = {
    "old": {
        "sha256": OLD_SHA256, "bytes": 60493640,
        "opcodes": (
            ("B_compare_state_at_20", 0xFCAA6F, "83782001"),
            ("B_or_flag_01_at_10", 0xFCAA75, "83481001"),
            ("B_write_state_at_20", 0xFCAA79, "c7402001000000"),
            ("helper_allocate_A8", 0x1C162F3, "b9a8000000"),
            ("constructor_vptr_store", 0x1C0BC99, "488901"),
        ),
        "calls": (
            ("B_calls_helper", 0xFCAA65, 0x1C162C0),
            ("helper_calls_allocator", 0x1C162F8, 0x126EB88),
            ("helper_calls_constructor", 0x1C16305, 0x1C0BC80),
        ),
        "lea": ("constructor_loads_vtable", 0x1C0BC92, 0x2A1CFB0),
        "vtable": 0x2A1CFB0,
        "slots": (
            (0x08, 0x14170AE40),
            (0x18, 0x140F45B00),
            (0x20, 0x14170AD90),
            (0x28, 0x14170E8E0),
        ),
        "allocation": 0xA8, "stateField": 0x20, "dirtyMask": 0x01,
    },
    "new": {
        "sha256": NEW_SHA256, "bytes": 60574536,
        "opcodes": (
            ("B_compare_state_at_18", 0xFCAA3F, "83781801"),
            ("B_or_flag_80_at_10", 0xFCAA45, "81481080000000"),
            ("B_write_state_at_18", 0xFCAA4C, "c7401801000000"),
            ("helper_allocate_A0", 0x1C1AEC3, "b9a0000000"),
            ("constructor_vptr_store", 0x1C103AC, "488901"),
        ),
        "calls": (
            ("B_calls_helper", 0xFCAA35, 0x1C1AE90),
            ("helper_calls_allocator", 0x1C1AEC8, 0x126EB58),
            ("helper_calls_constructor", 0x1C1AED5, 0x1C10390),
        ),
        "lea": ("constructor_loads_vtable", 0x1C103A5, 0x2A293E8),
        "vtable": 0x2A293E8,
        "slots": (
            (0x08, 0x1417097D0),
            (0x18, 0x140F45AD0),
            (0x20, 0x141709720),
            (0x28, 0x141718890),
        ),
        "allocation": 0xA0, "stateField": 0x18, "dirtyMask": 0x80,
    },
}


class GateError(Exception):
    """Archived source diverged from a pinned OLD/NEW observation."""


def require_bytes(read, rva: int, expected: bytes, label: str) -> None:
    observed = read(rva, len(expected))
    if observed != expected:
        raise GateError(
            f"{label} at RVA 0x{rva:X}: expected {expected.hex()}, "
            f"observed {observed.hex() if observed is not None else 'unmapped'}"
        )


def verify_build(read, label: str) -> None:
    spec = BUILDS[label]
    for anchor, rva, hex_bytes in spec["opcodes"]:
        require_bytes(read, rva, bytes.fromhex(hex_bytes), f"{label}.{anchor}")

    for anchor, rva, expected_target in spec["calls"]:
        raw = read(rva, 5)
        if raw is None or len(raw) != 5 or raw[0] != 0xE8:
            raise GateError(f"{label}.{anchor}: direct rel32 CALL missing at 0x{rva:X}")
        target = rva + 5 + struct.unpack_from("<i", raw, 1)[0]
        if target != expected_target:
            raise GateError(
                f"{label}.{anchor}: call target 0x{target:X}, expected 0x{expected_target:X}"
            )

    anchor, rva, expected_target = spec["lea"]
    raw = read(rva, 7)
    if raw is None or len(raw) != 7 or raw[:3] != bytes.fromhex("488d05"):
        raise GateError(f"{label}.{anchor}: RIP-relative LEA missing at 0x{rva:X}")
    target = rva + 7 + struct.unpack_from("<i", raw, 3)[0]
    if target != expected_target:
        raise GateError(
            f"{label}.{anchor}: vtable target 0x{target:X}, expected 0x{expected_target:X}"
        )

    for offset, pointer in spec["slots"]:
        require_bytes(
            read, spec["vtable"] + offset, struct.pack("<Q", pointer),
            f"{label}.vtable_slot_0x{offset:X}",
        )


def verify_layout(old_read, new_read) -> dict:
    verify_build(old_read, "old")
    verify_build(new_read, "new")
    old, new = BUILDS["old"], BUILDS["new"]
    return {
        "status": "SOURCE_PINNED_ONLY",
        "oldBuildSha256": old["sha256"],
        "newBuildSha256": new["sha256"],
        "old": {
            "allocation": f"0x{old['allocation']:X}",
            "stateFieldOffset": f"+0x{old['stateField']:X}",
            "dirtyBitMask": f"0x{old['dirtyMask']:X}",
            "vtableRva": f"0x{old['vtable']:X}",
        },
        "new": {
            "allocation": f"0x{new['allocation']:X}",
            "stateFieldOffset": f"+0x{new['stateField']:X}",
            "dirtyBitMask": f"0x{new['dirtyMask']:X}",
            "vtableRva": f"0x{new['vtable']:X}",
        },
        "pinnedOpcodeAnchorsPerBuild": 5,
        "pinnedCallTargetsPerBuild": 3,
        "pinnedVtableSlotsPerBuild": 4,
        "layoutCompatible": False,
        "functionIdentityQualified": False,
        "runtimeQualified": False,
    }


def checked_archive(path: Path, label: str):
    expected = BUILDS[label]
    before = stamp(path)
    if before[0] != expected["bytes"]:
        raise GateError(
            f"{label}: wrong archive size {before[0]}, expected {expected['bytes']}"
        )
    digest = sha_range(path)
    if digest != expected["sha256"]:
        raise GateError(f"{label}: wrong archive SHA-256 {digest}")
    pe = inspect_pe(path, before[0])
    return before, lambda rva, size: bytes_at_rva(path, pe, rva, size)


def main(argv: list[str] | None = None) -> int:
    parser = FailClosedParser(description=__doc__)
    parser.add_argument(
        "--old-pe", type=Path, default=ARCHIVE_ROOT / OLD_SHA256 / "rift_x64.exe",
        help="Archived, offline OLD RIFT PE (SHA1935...)",
    )
    parser.add_argument(
        "--new-pe", type=Path, default=ARCHIVE_ROOT / NEW_SHA256 / "rift_x64.exe",
        help="Archived, offline NEW RIFT PE (SHA df954...)",
    )
    args = parser.parse_args(argv)
    try:
        old_before, old_read = checked_archive(args.old_pe, "old")
        new_before, new_read = checked_archive(args.new_pe, "new")
        result = verify_layout(old_read, new_read)
        for label, path, before in (
            ("old", args.old_pe, old_before),
            ("new", args.new_pe, new_before),
        ):
            if stamp(path) != before or sha_range(path) != BUILDS[label]["sha256"]:
                raise GateError(f"{label}: archive changed during verification")
        print(json.dumps(result, sort_keys=True))
        return 0
    except (GateError, InspectionError, OSError, ValueError, struct.error) as exc:
        print(json.dumps({
            "status": "ERROR",
            "functionIdentityQualified": False,
            "runtimeQualified": False,
            "message": str(exc),
        }, sort_keys=True), file=sys.stderr)
        return 3


if __name__ == "__main__":
    sys.exit(main())
