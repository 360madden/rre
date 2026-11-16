#!/usr/bin/env python3
"""WA-006 exact-build, offline-only verification of Havok raycaster descriptor RTTI.

Reads the installed PE *file* without opening a process or invoking a game API.
This identifies the stack-created query visitor's vtable, NOT the dynamic
candidate object's virtual +0x40 target or a gameplay/collision owner.
"""
import argparse
import hashlib
import json
import struct
from pathlib import Path

import pefile

from verify_wa006_candidate_pointer import DEFAULT_PE, PE_SHA

IMAGE_BASE = 0x140000000
# RVA, exact byte count, SHA-256 of the original current-build PE window.
WINDOWS = {
    "col_ref": (0x278C978, 8, "c9fa33a2411748b7c1cbd8c610ae5d34a8ac646af32d1de192d152848ef38bb5"),
    "vftable": (0x278C980, 64, "dea4f646f9944c1acf36b364687f96ff2e5476e2414c19197247067f08d9606f"),
    "col": (0x2DF1B10, 24, "25ae3c402885eac18647b6cfebe14a69cfabc5bf136ac816209054f009e11c64"),
    "hierarchy": (0x2DF1B38, 16, "9c3cab62c6d750cbc4696e4fa2ea45b53b8fc66969b2e137594bbfb66ddac188"),
    "type_descriptor": (0x2F993C8, 100, "847c0507e70e915ab0755fbf51aeaf7806ad903c02101790b97397a79c8422cb"),
    "base_array": (0x2DF1B50, 8, "0e26c371e1003883a23a75825b5b59d0acbe6601f9f9db729623f9c56ae80fda"),
    "self_bcd": (0x2DF1B68, 28, "62d9f3397726503004f702bd8d66fd04127bfc0f4fb5c79c212eda4754fe1796"),
    "base_bcd": (0x2DF1AE8, 28, "02684a6e507258f6894e73d60da8c6937346156b4866b4329187445bfd6a6225"),
    "base_type_descriptor": (0x2F99398, 44, "f1fec0515dad5d06f7413b0da2f89003ae90244eab3c053d409c5096e093b4b2"),
}
TYPE_NAME = b".?AVhkpKdTreeCollidableRaycaster@@"
BASE_NAME = b".?AVhkKdTreeCastCollector@@"
SELF_BCD_FIELDS = (WINDOWS["type_descriptor"][0], 1, 0, -1, 0, 0x40, WINDOWS["hierarchy"][0])
BASE_BCD_FIELDS = (WINDOWS["base_type_descriptor"][0], 0, 0, -1, 0, 0x40, 0x2DF1AC0)
COL_FIELDS = (1, 0, 0, WINDOWS["type_descriptor"][0], WINDOWS["hierarchy"][0], WINDOWS["col"][0])
HIERARCHY_FIELDS = (0, 0, 2, 0x2DF1B50)


def require(condition, detail):
    if not condition:
        raise ValueError(detail)


def check_semantics(windows):
    """Check structure independently of the outer whole-PE/hash guards."""
    ref = windows["col_ref"]
    vftable = windows["vftable"]
    col = windows["col"]
    hierarchy = windows["hierarchy"]
    desc = windows["type_descriptor"]
    base_array = windows["base_array"]
    self_bcd = windows["self_bcd"]
    base_bcd = windows["base_bcd"]
    base_desc = windows["base_type_descriptor"]
    require(len(ref) == 8 and struct.unpack("<Q", ref)[0] == IMAGE_BASE + WINDOWS["col"][0],
            "vftable[-8] does not reference expected Complete Object Locator")
    require(len(vftable) >= 16 and struct.unpack_from("<Q", vftable, 8)[0] == IMAGE_BASE + 0xA2514,
            "descriptor +8 is not the verified candidate selector")
    require(len(col) == 24 and struct.unpack("<6I", col) == COL_FIELDS,
            "Complete Object Locator structure mismatch")
    require(len(hierarchy) == 16 and struct.unpack("<4I", hierarchy) == HIERARCHY_FIELDS,
            "class hierarchy descriptor mismatch")
    require(len(desc) >= 16 + len(TYPE_NAME) + 1 and
            desc[16:16 + len(TYPE_NAME) + 1] == TYPE_NAME + bytes([0]),
            "raycaster RTTI type name mismatch")
    require(len(base_array) == 8 and struct.unpack("<2I", base_array) ==
            (WINDOWS["self_bcd"][0], WINDOWS["base_bcd"][0]),
            "class hierarchy base-array references mismatch")
    require(len(self_bcd) == 28 and struct.unpack("<IIiiiII", self_bcd) == SELF_BCD_FIELDS,
            "raycaster self BaseClassDescriptor mismatch")
    require(len(base_bcd) == 28 and struct.unpack("<IIiiiII", base_bcd) == BASE_BCD_FIELDS,
            "collector BaseClassDescriptor mismatch")
    require(len(base_desc) == 16 + len(BASE_NAME) + 1 and
            base_desc[16:] == BASE_NAME + bytes([0]),
            "collector RTTI type name mismatch")


def verify(pe_bytes):
    require(len(pe_bytes) == 60493640, "unexpected executable size")
    require(hashlib.sha256(pe_bytes).hexdigest() == PE_SHA, "unexpected executable SHA-256")
    pe = pefile.PE(data=pe_bytes, fast_load=True)
    require(pe.FILE_HEADER.Machine == 0x8664 and
            pe.OPTIONAL_HEADER.Magic == 0x20B and
            pe.OPTIONAL_HEADER.ImageBase == IMAGE_BASE, "unexpected PE architecture/image base")
    original = {}
    for name, (rva, length, expected_hash) in WINDOWS.items():
        data = pe.get_data(rva, length)
        require(len(data) == length, f"missing RTTI window: {name}")
        require(hashlib.sha256(data).hexdigest() == expected_hash,
                f"original RTTI window checksum mismatch: {name}")
        original[name] = data
    check_semantics(original)

    # Exercise semantic checks on RAM-only changes; do not rely on the PE
    # or window SHA rejecting a corruption before the RTTI parser sees it.
    controls = (("col", 0), ("type_descriptor", 16), ("hierarchy", 8),
                ("base_array", 0), ("self_bcd", 0), ("base_bcd", 0),
                ("base_type_descriptor", 16))
    for name, offset in controls:
        changed = dict(original)
        block = bytearray(changed[name])
        block[offset] ^= 1
        changed[name] = bytes(block)
        try:
            check_semantics(changed)
        except ValueError:
            continue
        raise ValueError(f"in-memory RTTI mutation falsely accepted: {name}+{offset:#x}")
    return {
        "task": "WA-006",
        "evidenceTier": "exact-current-build static MSVC RTTI",
        "peSha256": PE_SHA,
        "className": TYPE_NAME.decode("ascii"),
        "baseTypeName": BASE_NAME.decode("ascii"),
        "visitorDescriptorVftableRva": "0x278c980",
        "completeObjectLocatorRva": "0x2df1b10",
        "typeDescriptorRva": "0x2f993c8",
        "classHierarchyRva": "0x2df1b38",
        "sourceWindows": {name: {"rva": hex(rva), "size": size, "sha256": digest}
                          for name, (rva, size, digest) in WINDOWS.items()},
        "negativeControls": len(controls),
        "unproven": [
            "candidate object concrete vptr or virtual +0x40 implementation",
            "runtime collision hit/miss", "gameplay object/unit owner",
            "current playable scene and world-instance identity",
        ],
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pe", type=Path, default=DEFAULT_PE)
    args = parser.parse_args()
    try:
        print(json.dumps(verify(args.pe.read_bytes()), sort_keys=True, indent=2))
    except (OSError, ValueError, pefile.PEFormatError) as exc:
        parser.exit(2, f"WA-006 RTTI verification failed: {exc}\\n")
