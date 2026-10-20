#!/usr/bin/env python3
"""M3-001: prove typed dispatcher indexing and reject misleading handler slots.

Original pinned PE only, read-only. A handler *address calculation* is not
evidence that a callback was registered or that type-7 jobs are submitted.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import struct
import sys

SOURCE = Path(r"C:\Program Files (x86)\Glyph\Games\RIFT\Live\rift_x64.exe")
BUILD_SHA = "7c356c9dde9e12fcbff3c08d953b0630b48b1510a0ffb36e4ec164606e7b17bd"
BASE = 0x140000000

# RVAs and their pinned, byte-grounded semantic assertions; these are NOT
# runtime callability proofs.
DISPATCH_EXPECTED = {
    0xF3FBE: ("mov", "rdi, rcx"),
    0xF4184: ("movzx", "ecx, byte ptr [rsp + 0x21]"),
    0xF4189: ("movzx", "r8d, byte ptr [rsp + 0x20]"),
    0xF4194: ("shl", "rcx, 5"),
    0xF4198: ("mov", "rax, qword ptr [rcx + rdi + 0x130]"),
    0xF41A3: ("call", "qword ptr [rax + r8*8]"),
}
MOTION_EXPECTED = {
    0x7635C: ("lea", "rax, [rip + 0x26ad0b5]"),
    0x76363: ("mov", "qword ptr [rbx + 0x150], rax"),
}
OTHER_EXPECTED = {
    0x268A7: ("mov", "rax, qword ptr [rcx + 0x10]"),
    0x268AB: ("mov", "qword ptr [rbx + 0x130], rax"),
    0x40179: ("mov", "qword ptr [rax + 0x130], rbx"),
}


def _require(ok: bool, why: str) -> None:
    if not ok:
        raise ValueError(why)


def _rtti(pe, vft_rva: int) -> dict:
    ptr_bytes = pe.get_data(vft_rva - 8, 8)
    _require(len(ptr_bytes) == 8, "Truncated MSVC locator pointer")
    col_rva = struct.unpack("<Q", ptr_bytes)[0] - BASE
    _require(0 < col_rva < 0x3800000, "Complete Object Locator RVA outside pinned PE")
    col = pe.get_data(col_rva, 24)
    _require(len(col) == 24, "Truncated MSVC Complete Object Locator")
    sig, off, cd, type_rva, hierarchy, self_rva = struct.unpack("<6I", col)
    _require(sig == 1 and self_rva == col_rva, "MSVC locator signature/self-RVA mismatch")
    _require(type_rva < 0x3800000, "Invalid RTTI TypeDescriptor RVA")
    name = pe.get_data(type_rva + 16, 135).split(b"\0", 1)[0].decode("ascii")
    return {"className": name, "vtableRva": hex(vft_rva),
            "locatorRva": hex(col_rva), "typeDescriptorRva": hex(type_rva),
            "subobjectOffset": off, "selfRvaValid": True}


def _decode_windows(pe, targets: tuple[int, ...]) -> tuple[dict, dict]:
    import capstone
    pe.parse_data_directories(
        directories=[__import__("pefile").DIRECTORY_ENTRY["IMAGE_DIRECTORY_ENTRY_EXCEPTION"]])
    ranges = sorted(set((int(entry.struct.BeginAddress),
                         int(entry.struct.EndAddress))
                        for entry in pe.DIRECTORY_ENTRY_EXCEPTION))
    md = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_64)
    md.detail = True
    found, windows = {}, {}
    for target in targets:
        candidates = [pair for pair in ranges if pair[0] <= target < pair[1]]
        _require(bool(candidates), f"No qualified PE unwind region for {hex(target)}")
        begin, end = min(candidates, key=lambda p: p[1]-p[0])
        _require(0 < end-begin <= 16384, "Oversize/unbounded PE decode window")
        blob = pe.get_data(begin, end-begin)
        instructions = list(md.disasm(blob, BASE+begin))
        _require(bool(instructions) and
                 instructions[-1].address+instructions[-1].size == BASE+end,
                 "Incomplete PE-unwind-aligned instruction decode")
        target_insn = next((ins for ins in instructions
                            if ins.address-BASE == target), None)
        _require(target_insn is not None,
                 f"RVA {hex(target)} was not an instruction boundary")
        found[target] = target_insn
        windows[(begin, end)] = {"firstRva": hex(begin), "endRvaExclusive": hex(end),
                                 "instructionCount": len(instructions),
                                 "completeFromPeUnwindStart": True}
    return found, windows


def verify(binary: Path = SOURCE) -> dict:
    import pefile
    raw = binary.read_bytes()
    binary_sha = hashlib.sha256(raw).hexdigest()
    _require(binary_sha == BUILD_SHA, "Exact Rift source hash mismatch")
    pe = pefile.PE(data=raw, fast_load=True)
    try:
        _require(int(pe.FILE_HEADER.Machine) == 0x8664, "Not the x64 PE")
        _require(int(pe.OPTIONAL_HEADER.ImageBase) == BASE, "Unexpected PE static base")
        expected = {**DISPATCH_EXPECTED, **MOTION_EXPECTED, **OTHER_EXPECTED}
        actual, windows = _decode_windows(pe, tuple(expected))
        instructions = {}
        for rva, (mnemonic, operands) in expected.items():
            ins = actual[rva]
            _require((ins.mnemonic, ins.op_str) == (mnemonic, operands),
                     f"Instruction changed at RVA {hex(rva)}")
            instructions[hex(rva)] = {
                "bytes": ins.bytes.hex(),
                "asm": f"{ins.mnemonic} {ins.op_str}",
                "source": "original PE, instruction boundary qualified",
            }
        import capstone
        from capstone.x86_const import (X86_OP_MEM, X86_REG_RIP,
                                        X86_REG_RDI, X86_REG_RCX)
        indexed = actual[0xF4198]
        mem = indexed.operands[1].mem
        _require(mem.disp == 0x130 and mem.base == X86_REG_RCX and
                 mem.index == X86_REG_RDI and indexed.operands[1].size == 8,
                 "Dispatcher indexing is not the expected queue/shift expression")

        motion_lea = actual[0x7635C]
        _require(motion_lea.operands[1].type == X86_OP_MEM and
                 motion_lea.operands[1].mem.base == X86_REG_RIP,
                 "Motion vtable reference is not RIP relative")
        vft = (motion_lea.address + motion_lea.size +
               motion_lea.operands[1].mem.disp - BASE)
        _require(vft == 0x2723418, "hkpMaxSizeMotion table RVA changed")
        motion = _rtti(pe, vft)
        _require(motion["className"] == ".?AVhkpMaxSizeMotion@@",
                 "Non-handler source class changed")

        return {
            "status": "PASS",
            "taskId": "M3-001",
            "buildSha256": binary_sha,
            "sourceScope": "read-only exact-build saved-PE native code and RTTI",
            "staticBase": hex(BASE),
            "qualifiedInstructionWindows": sorted(windows.values(),
                key=lambda w: int(w["firstRva"], 0)),
            "verifiedInstructions": instructions,
            "queueDispatch": {
                "procedureRva": "0xf3fa4",
                "queueReceiverPreservedRva": "0xf3fbe",
                "typeByteReadRva": "0xf4184",
                "subtypeByteReadRva": "0xf4189",
                "typeIndexShiftRva": "0xf4194",
                "handlerPointerReadRva": "0xf4198",
                "subtypeCallbackCallRva": "0xf41a3",
                "typeTableBaseDisplacement": "0x130",
                "typeTableSlotBytes": 32,
                "computedType7SlotDisplacement": "0x210",
                "registeredCallbackForType7Proven": False,
                "typedJobProducerProven": False,
            },
            "rejectedOrUnqualifiedCandidates": [
                {
                    "rva": "0x76363",
                    "memOffset": "0x150",
                    "classification": "disproved-as-job-type1-handler",
                    "reason": "RTTI-qualified hkpMaxSizeMotion vtable is installed in an embedded member",
                    "rtti": motion,
                },
                {
                    "rva": "0x268ab",
                    "memOffset": "0x130",
                    "classification": "unqualified-local-structure-copy",
                    "reason": "Copies one qword from a local aggregate; job-queue receiver identity unproven",
                },
                {
                    "rva": "0x40179",
                    "memOffset": "0x130",
                    "classification": "unqualified-foreign-global-object",
                    "reason": "Source RBX can be an allocator result or zero; global receiver is not proven to be Havok job queue",
                },
            ],
            "limitations": [
                "Proves how dispatch computes addresses, NOT that the type-7 slot has a nonnull registered callback.",
                "The syntax/register tests and RTTI identify only selected PE-unwind windows, not global data flow.",
                "All bounds and aliases are static and may not execute in a live Rift session.",
                "Indexed-register writers without a literal +0x130 displacement may be missed by targeted scans.",
                "No same-object hkpMultiThreadedSimulation+0x160 nonnull queue assignment was discovered.",
                "No true type-7 job producer, route output, or player navigation link was verified.",
            ],
            "liveProcessAttached": False, "gameInputSent": False,
            "binaryModified": False, "type7Operational": False,
        }
    finally:
        pe.close()


if __name__ == "__main__":
    try:
        print(json.dumps(verify(), ensure_ascii=False, sort_keys=True, indent=2))
    except (OSError, TypeError, ValueError, KeyError) as exc:
        print(json.dumps({"status": "FAILED", "error": str(exc)},
                         ensure_ascii=False), file=sys.stderr)
        raise SystemExit(1)
