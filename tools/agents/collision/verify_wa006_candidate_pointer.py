#!/usr/bin/env python3
"""WA-006: fail-closed, static-only split-candidate-pointer data-flow check.

Reads the installed PE on disk; never attaches to a process, invokes game
functions, or writes source/evidence. This proves instruction-local flow only.
"""
import argparse
import hashlib
import json
from pathlib import Path

import pefile
from capstone import Cs, CS_ARCH_X86, CS_MODE_64

DEFAULT_PE = Path(r"C:\Program Files (x86)\Glyph\Games\RIFT\Live\rift_x64.exe")
PE_SHA = "1935a05c9db6d468e34e0055014a4a99c1b5afceb1695884e24600f5c20a4be8"
WRAPPER = (0x8E744, 169, "84493c16cc018b254698dd8a1d37406f6e7ee3150d1e407bc232cd5608014274")
PRODUCER = (0xD0944, 0x730, "2f37be6b71b566885610faa92f6bf0c1a210dc821a4c459ce985cf39d2b566fe")
SELECTOR = (0xA2514, 0x1BE, "ea78e0b39823e7ae154144f11e0d31a9acb794f8acfbfb9a4087e83255bba973")
VTABLE = (0x278C980, 64, "dea4f646f9944c1acf36b364687f96ff2e5476e2414c19197247067f08d9606f")

# Literal original-build opcodes, never offsets inferred from a different PE.
ANCHORS = {
    0x8E7C5: ("488b5128", "mov", "rdx, qword ptr [rcx + 0x28]"),
    0x8E7E0: ("e85f210400", "call", "0xd0944"),
    0xD09A6: ("4c8b7a20", "mov", "r15, qword ptr [rdx + 0x20]"),
    0xD0CBF: ("81e3ffffff7f", "and", "ebx, 0x7fffffff"),
    0xD0CC9: ("48c1e305", "shl", "rbx, 5"),
    0xD0CE0: ("4a8d5c3b14", "lea", "rbx, [rbx + r15 + 0x14]"),
    0xD0D4B: ("8b43f4", "mov", "eax, dword ptr [rbx - 0xc]"),
    0xD0D55: ("898424b8010000", "mov", "dword ptr [rsp + 0x1b8], eax"),
    0xD0D5C: ("8b03", "mov", "eax, dword ptr [rbx]"),
    0xD0D65: ("898424bc010000", "mov", "dword ptr [rsp + 0x1bc], eax"),
    0xD0E90: ("4c8b8424b8010000", "mov", "r8, qword ptr [rsp + 0x1b8]"),
    0xD0EA3: ("ff5008", "call", "qword ptr [rax + 8]"),
    0xA2527: ("498b38", "mov", "rdi, qword ptr [r8]"),
    0xA252A: ("498bf0", "mov", "rsi, r8"),
    0xA2646: ("488b07", "mov", "rax, qword ptr [rdi]"),
    0xA2649: ("4d85c9", "test", "r9, r9"),
    0xA264C: ("7425", "je", "0xa2673"),
    0xA2656: ("ff5048", "call", "qword ptr [rax + 0x48]"),
    0xA2659: ("c6450000", "mov", "byte ptr [rbp], 0"),
    0xA2673: ("4c8b4b20", "mov", "r9, qword ptr [rbx + 0x20]"),
    0xA2684: ("ff5040", "call", "qword ptr [rax + 0x40]"),
    0xA2687: ("80bc248000000000", "cmp", "byte ptr [rsp + 0x80], 0"),
    0xA2695: ("c6450001", "mov", "byte ptr [rbp], 1"),
    0xA2699: ("48897050", "mov", "qword ptr [rax + 0x50], rsi"),
}


def sha(data):
    return hashlib.sha256(data).hexdigest()


def require(condition, message):
    if not condition:
        raise ValueError(message)


def inspect_windows(wrapper, producer, selector):
    cs = Cs(CS_ARCH_X86, CS_MODE_64)
    insns = {}
    for start, data in ((WRAPPER[0], wrapper), (PRODUCER[0], producer),
                        (SELECTOR[0], selector)):
        disasm = list(cs.disasm(data, start))
        require(disasm and disasm[0].address == start and
                disasm[-1].address + disasm[-1].size == start + len(data),
                "instruction boundary mismatch")
        for instruction in disasm:
            insns[instruction.address] = instruction

    for rva, (raw, mnemonic, op_str) in ANCHORS.items():
        instruction = insns.get(rva)
        require(instruction is not None and instruction.bytes.hex() == raw and
                instruction.mnemonic == mnemonic and instruction.op_str == op_str,
                f"candidate pointer anchor mismatch at RVA {rva:#x}")

    # In this statically decoded interval there are no direct instructions
    # reassigning either half of the reconstructed qword before its load.
    direct_writes = [i.address for i in insns.values()
                     if 0xD0D65 < i.address < 0xD0E90 and
                     ("[rsp + 0x1b8]" in i.op_str or
                      "[rsp + 0x1bc]" in i.op_str)]
    require(not direct_writes, "intervening stack-slot references: " +
            ", ".join(hex(x) for x in direct_writes))
    return len(ANCHORS)


def verify(blob):
    require(len(blob) == 60493640, "unexpected PE length")
    require(sha(blob) == PE_SHA, "unexpected PE SHA-256")
    pe = pefile.PE(data=blob, fast_load=True)
    require(pe.FILE_HEADER.Machine == 0x8664 and
            pe.OPTIONAL_HEADER.Magic == 0x20B and
            pe.OPTIONAL_HEADER.ImageBase == 0x140000000, "unexpected PE type")
    windows = []
    for start, length, expected in (WRAPPER, PRODUCER, SELECTOR, VTABLE):
        section = next((s for s in pe.sections if s.VirtualAddress <= start
                        and start + length <= s.VirtualAddress + s.SizeOfRawData), None)
        require(section is not None, f"out-of-section window at {start:#x}")
        data = pe.get_data(start, length)
        require(len(data) == length and sha(data) == expected,
                f"original window SHA changed at {start:#x}")
        windows.append(data)
    wrapper, producer, selector, vtable = windows
    require(int.from_bytes(vtable[8:16], "little") == 0x1400A2514,
            "selector vtable slot +0x08 mismatch")
    count = inspect_windows(wrapper, producer, selector)

    # Mutation checks test the *anchor checker* on RAM copies, independently
    # of the PE SHA guard, to detect a changed source-store or virtual call.
    controls = ((0, 0x8E7C5, WRAPPER[0]), (1, 0xD0D55, PRODUCER[0]),
                (2, 0xA2684, SELECTOR[0]))
    for which, rva, base in controls:
        changed = bytearray(windows[which])
        changed[rva - base] ^= 1
        arguments = [wrapper, producer, selector]
        arguments[which] = bytes(changed)
        try:
            inspect_windows(*arguments)
        except ValueError:
            pass
        else:
            raise ValueError(f"in-memory mutation falsely accepted at {rva:#x}")
    return {
        "task": "WA-006", "evidenceTier": "exact-build static only",
        "peSha256": PE_SHA, "anchorCount": count, "negativeControls": 3,
        "sourceWindows": {"wrapperRva": hex(WRAPPER[0]),
                          "wrapperSha256": WRAPPER[2],
                          "producerRva": hex(PRODUCER[0]),
                          "producerSha256": PRODUCER[2],
                          "selectorRva": hex(SELECTOR[0]),
                          "selectorSha256": SELECTOR[2],
                          "vtableRva": hex(VTABLE[0]),
                          "vtableSha256": VTABLE[2]},
        "provenFlow": "wrapper [incoming RCX+0x28] -> producer [RDX+0x20] candidate buffer; 32-byte record [base+8] low32 and [base+0x14] high32 -> R8; selector dereferences R8; conditional +0x40 dispatch may store R8 at scratch+0x50",
        "notQualified": ["concrete candidate object vtable/class",
                         "runtime pointer validity", "physics hit", "gameplay owner",
                         "world-instance identity", "RR2 live player identity"],
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pe", type=Path, default=DEFAULT_PE)
    args = parser.parse_args()
    try:
        print(json.dumps(verify(args.pe.read_bytes()), indent=2, sort_keys=True))
    except (OSError, ValueError, pefile.PEFormatError) as error:
        print(json.dumps({"task": "WA-006", "status": "fail-closed",
                          "error": str(error)}))
        raise SystemExit(1)
