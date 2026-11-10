"""Source-pinned direct caller qualification for the SC-103 Soul Tree entry.

Offline only: reads a saved RIFT PE, never a live game process. Qualifies one
direct rel32 caller and two method-table installation sites against decoded
instruction boundaries, not class identity or a modern Legendary ability ID.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import struct
from pathlib import Path

import capstone
import pefile

SOURCE_SHA256 = "1935a05c9db6d468e34e0055014a4a99c1b5afceb1695884e24600f5c20a4be8"
SOURCE_SIZE = 60_493_640
SOUL_ENTRY_RVA = 0xEA2ED0
EXPECTED_CALL_RVA = 0xEAB54E
EXPECTED_OWNER = (0xEAB4D0, 0xEAB5DB)
EXPECTED_TABLE_RVA = 0x2704798
EXPECTED_METHOD_SLOT_BYTES = 0x60  # table index 12
EXPECTED_INSTALL_RVAS = (0xE8A9A3, 0xE8B6AA)

# RVAs and exact instruction representations are pinned to SOURCE_SHA256.
EXPECTED_INSTRUCTIONS = {
    0xEAB4DD: ("mov", "rdi, rcx"),  # incoming context is retained in RDI
    0xEAB4EE: ("call", "qword ptr [rax + 0xb8]"),
    0xEAB4FE: ("call", "qword ptr [rax + 0xc0]"),
    0xEAB53A: ("cmp", "byte ptr [rdi + 0x255], sil"),
    0xEAB541: ("je", "0xeab58b"),
    0xEAB543: ("mov", "rcx, rdi"),
    0xEAB546: ("call", "0xeab7d0"),
    0xEAB54B: ("mov", "rcx, rdi"),
    0xEAB54E: ("call", "0xea2ed0"),
    0xEAB553: ("mov", "byte ptr [rdi + 0x255], sil"),
    0xEAB55A: ("mov", "byte ptr [rdi + 0x2f2], sil"),
    0xE8A9A3: ("lea", "rax, [rip + 0x1879dee]"),
    0xE8A9AA: ("mov", "qword ptr [rdi], rax"),
    0xE8B6AA: ("lea", "rax, [rip + 0x18790e7]"),
    0xE8B6B3: ("mov", "qword ptr [rcx], rax"),
}


def rel32_calls(section: bytes, section_rva: int, target_rva: int) -> list[int]:
    """Find possible E8 rel32 call starts. Capstone must validate boundaries."""
    matches = []
    i = section.find(bytes((0xE8,)))
    while i >= 0:
        if i + 5 <= len(section):
            delta = struct.unpack_from("<i", section, i + 1)[0]
            if section_rva + i + 5 + delta == target_rva:
                matches.append(section_rva + i)
        i = section.find(bytes((0xE8,)), i + 1)
    return matches


def method_pointer_at(table: bytes, slot_bytes: int) -> int:
    """Read an aligned x64 pointer from a bounded method table."""
    if slot_bytes < 0 or slot_bytes % 8 or slot_bytes + 8 > len(table):
        raise ValueError("invalid or truncated x64 method-table slot")
    return struct.unpack_from("<Q", table, slot_bytes)[0]


def owner_range(pdata: bytes, rva: int) -> tuple[int, int]:
    owners = []
    for offset in range(0, len(pdata) - 11, 12):
        begin, end, _unwind = struct.unpack_from("<III", pdata, offset)
        if begin <= rva < end:
            owners.append((begin, end))
    if len(owners) != 1:
        raise ValueError(f"expected one .pdata owner of 0x{rva:X}; got {owners!r}")
    return owners[0]


def analyze(path: Path) -> dict:
    source = path.read_bytes()
    source_hash = hashlib.sha256(source).hexdigest()
    if len(source) != SOURCE_SIZE or source_hash != SOURCE_SHA256:
        raise ValueError(
            f"exact-build guard: got {len(source)} bytes SHA {source_hash}, "
            f"expected {SOURCE_SIZE} bytes SHA {SOURCE_SHA256}"
        )
    pe = pefile.PE(data=source, fast_load=True)
    if pe.FILE_HEADER.Machine != 0x8664:
        raise ValueError("expected x64 PE")
    executable_sections = [
        sec for sec in pe.sections if sec.Characteristics & 0x20000000
    ]
    if not executable_sections:
        raise ValueError("no executable PE section")
    candidates = sorted({
        rva
        for sec in executable_sections
        for rva in rel32_calls(
            source[sec.PointerToRawData:sec.PointerToRawData + sec.SizeOfRawData],
            sec.VirtualAddress,
            SOUL_ENTRY_RVA,
        )
    })
    if candidates != [EXPECTED_CALL_RVA]:
        raise ValueError(f"direct-call targets differ from pinned source: {candidates!r}")
    pdata = next(
        (sec for sec in pe.sections if sec.Name.rstrip(b"\0") == b".pdata"),
        None,
    )
    if pdata is None:
        raise ValueError("missing .pdata")
    pdata_bytes = source[pdata.PointerToRawData:pdata.PointerToRawData + pdata.SizeOfRawData]
    owner = owner_range(pdata_bytes, EXPECTED_CALL_RVA)
    if owner != EXPECTED_OWNER:
        raise ValueError(f"unexpected direct caller owner {owner!r}")
    # The direct caller is slot 12 in an exact-build method-pointer table.
    # Two independent code sites install the table pointer into an object.
    slot_pointer = method_pointer_at(
        pe.get_data(EXPECTED_TABLE_RVA, EXPECTED_METHOD_SLOT_BYTES + 8),
        EXPECTED_METHOD_SLOT_BYTES,
    )
    expected_pointer = pe.OPTIONAL_HEADER.ImageBase + EXPECTED_OWNER[0]
    if slot_pointer != expected_pointer:
        raise ValueError(
            f"method-pointer slot mismatch: 0x{slot_pointer:X}, expected 0x{expected_pointer:X}"
        )
    md = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_64)
    sites = (EXPECTED_CALL_RVA, *EXPECTED_INSTALL_RVAS)
    actual = {}
    owner_instructions = {}
    owners = {}
    for site in sites:
        bounds = owner_range(pdata_bytes, site)
        code = pe.get_data(bounds[0], bounds[1] - bounds[0])
        instructions = list(md.disasm(code, bounds[0]))
        if not instructions or instructions[-1].address + instructions[-1].size != bounds[1]:
            raise ValueError(f"owner of RVA 0x{site:X} not fully decoded")
        actual.update({ins.address: (ins.mnemonic, ins.op_str) for ins in instructions})
        owner_instructions[f"0x{site:X}"] = len(instructions)
        owners[f"0x{site:X}"] = [f"0x{rva:X}" for rva in bounds]
    mismatches = {
        f"0x{rva:X}": {"expected": expected, "actual": actual.get(rva)}
        for rva, expected in EXPECTED_INSTRUCTIONS.items()
        if actual.get(rva) != expected
    }
    if mismatches:
        raise ValueError(f"pinned instruction disagreement: {mismatches!r}")
    return {
        "source": str(path),
        "source_sha256": source_hash,
        "source_bytes": len(source),
        "target_entry_rva": f"0x{SOUL_ENTRY_RVA:X}",
        "direct_call_rvas": [f"0x{rva:X}" for rva in candidates],
        "caller_pdata_range": [f"0x{rva:X}" for rva in owner],
        "asserted_instruction_count": len(EXPECTED_INSTRUCTIONS),
        "decoded_site_owner_instructions": owner_instructions,
        "site_pdata_ranges": owners,
        "method_table_rva": f"0x{EXPECTED_TABLE_RVA:X}",
        "method_table_slot": EXPECTED_METHOD_SLOT_BYTES // 8,
        "method_table_slot_rva": f"0x{EXPECTED_TABLE_RVA + EXPECTED_METHOD_SLOT_BYTES:X}",
        "method_pointer_rva": f"0x{slot_pointer - pe.OPTIONAL_HEADER.ImageBase:X}",
        "method_table_install_lea_rvas": [f"0x{rva:X}" for rva in EXPECTED_INSTALL_RVAS],
        "observed_entry_argument": "caller RDI, copied from caller entry RCX",
        "observed_guard": "nonzero byte at caller RDI+0x255 selects 0xEAB54E call path",
        "observed_after_call": "clear caller RDI+0x255 and RDI+0x2F2 to zero",
        "unproved": [
            "formal class name, RTTI or actual UI object type for the method-pointer table",
            "Legendary counter or selection meaning of Soul Tree fields",
            "modern Protector's Fury variant ID",
            "execution of this path in a current game session",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("exe", type=Path, help="saved exact-build RIFT x64 executable")
    args = parser.parse_args()
    try:
        result = analyze(args.exe)
    except (OSError, ValueError, pefile.PEFormatError) as exc:
        parser.exit(2, f"SC-103 source qualification failed: {exc}\n")
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
