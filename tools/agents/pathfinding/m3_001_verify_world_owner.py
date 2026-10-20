#!/usr/bin/env python3
"""M3-001 qualified static disproof of a misleading 'type-7' offset match.

Reads only the pinned on-disk RIFT PE. No game launch, process handle, input,
memory modification, debugger or original binary write is performed.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import struct
import sys

BUILD_SHA = "7c356c9dde9e12fcbff3c08d953b0630b48b1510a0ffb36e4ec164606e7b17bd"
PREFERRED_BASE = 0x140000000
DEFAULT_EXE = Path(r"C:\Program Files (x86)\Glyph\Games\RIFT\Live\rift_x64.exe")
# RVA -> raw x64 instruction bytes, pinned to the qualified static build.
EXPECTED_INSTRUCTIONS = {
    0x7A261: "4533ff",                # zero r15d
    0x7A272: "488bf9",                # rdi receives hkpWorld-this
    0x7A28E: "488d05a39d6a02",        # hkpWorld vftable address
    0x7A295: "488901",                # object vftable installation
    0x7A384: "4c89b910020000",        # hkpWorld+0x210 <- zero r15
    0x7AF81: "0fbe8ed9000000",      # hkpWorld state source byte
    0x7AF8D: "898f60010000",          # hkpWorld+0x160 dword state
    0x7B0A3: "e814ea0000",            # call hkpMultiThreadedSimulation constructor
    0x7B0A8: "48894710",              # hkpWorld+0x10 <- simulation pointer
    0x89BD7: "4983a56001000000",     # simulation+0x160 <- zero
    0x8A9DF: "488b8e60010000",       # method loads simulation+0x160
    0x8A9E6: "e8b9950600",           # calls shared job dispatcher
}


def require(ok: bool, explanation: str) -> None:
    if not ok:
        raise ValueError(explanation)


def rtti_vft(pe, table: int) -> dict:
    ptr = struct.unpack("<Q", pe.get_data(table-8, 8))[0]
    locator = ptr - PREFERRED_BASE
    require(0 < locator < 0x3800000, "RTTI locator outside native image")
    payload = pe.get_data(locator, 24)
    require(len(payload) == 24, "Truncated MSVC RTTI Complete Object Locator")
    sig, off, cd, typ, hierarchy, self_ref = struct.unpack("<6I", payload)
    require(sig == 1 and off == 0 and self_ref == locator,
            "RTTI COL failed MSVC signature/self-RVA checks")
    name = pe.get_data(typ + 16, 130).split(b"\0",1)[0].decode("ascii")
    return {
        "tableRva": hex(table), "locatorRva": hex(locator),
        "typeDescriptorRva": hex(typ), "className": name, "subobjectOffset": off,
        "signature": sig, "selfRvaValid": self_ref == locator,
    }


def verify(binary: Path = DEFAULT_EXE) -> dict:
    import capstone
    import pefile
    raw = binary.read_bytes()
    source_hash = hashlib.sha256(raw).hexdigest()
    require(source_hash == BUILD_SHA, "Rift executable SHA mismatch")
    pe = pefile.PE(data=raw, fast_load=True)
    try:
        require(int(pe.FILE_HEADER.Machine)==0x8664, "Not x64 PE")
        require(int(pe.OPTIONAL_HEADER.ImageBase)==PREFERRED_BASE, "Unexpected image base")
        md = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_64)
        md.detail = True
        ins = {}
        for rva, expected in EXPECTED_INSTRUCTIONS.items():
            data = pe.get_data(rva, 16)
            inst = next(md.disasm(data,PREFERRED_BASE+rva,count=1),None)
            require(inst is not None and inst.address == PREFERRED_BASE+rva,
                    f"Failed to decode native instruction at {hex(rva)}")
            require(inst.bytes.hex()==expected,
                    f"Native instruction changed at {hex(rva)}")
            ins[rva]=inst
        # Validate constructor's initial register-zero reaching the field
        # assignment within a straight-line contiguous decoded sequence.
        start,end=0x7A248,0x7A38B
        instructions=list(md.disasm(pe.get_data(start,end-start),
                                    PREFERRED_BASE+start))
        positions={inst.address-PREFERRED_BASE:i for i,inst in enumerate(instructions)}
        require(all(r in positions for r in (0x7A261,0x7A272,0x7A28E,
                                              0x7A295,0x7A384)),
                "World constructor initialization has incomplete boundaries")
        segment=instructions[positions[0x7A261]:positions[0x7A384]+1]
        require(all(x.mnemonic!="call" for x in segment),
                "Intervening call invalidates simple zero reaching definition")
        # R15 source remains zero (no write to r15/r15d and no call) in this segment.
        require(all(
            not(x.address-PREFERRED_BASE>0x7A261 and
                x.operands and x.operands[0].type==capstone.x86_const.X86_OP_REG and
                x.operands[0].reg in (capstone.x86_const.X86_REG_R15,
                                      capstone.x86_const.X86_REG_R15D))
            for x in segment
        ), "r15 may be redefined before world +0x210 zero store")
        require(ins[0x7A261].mnemonic=="xor" and ins[0x7A261].op_str=="r15d, r15d",
                "Zeroing instruction changed")
        require(ins[0x7A272].mnemonic=="mov" and ins[0x7A272].op_str=="rdi, rcx",
                "World-this alias changed")
        require(ins[0x7A384].mnemonic=="mov" and
                ins[0x7A384].op_str=="qword ptr [rcx + 0x210], r15",
                "World +0x210 receiver instruction changed")
        require(ins[0x7AF8D].mnemonic=="mov" and
                ins[0x7AF8D].op_str=="dword ptr [rdi + 0x160], ecx",
                "World state width/receiver changed")
        require(ins[0x89BD7].mnemonic=="and" and
                ins[0x89BD7].op_str=="qword ptr [r13 + 0x160], 0",
                "Simulation initial zero write changed")
        require(ins[0x8A9DF].mnemonic=="mov" and
                ins[0x8A9DF].op_str=="rcx, qword ptr [rsi + 0x160]",
                "Simulation queue pointer read changed")
        require(ins[0x7B0A3].mnemonic=="call" and
                ins[0x7B0A3].op_str==hex(PREFERRED_BASE+0x89ABC),
                "World-to-simulation constructor call changed")
        require(ins[0x7B0A8].mnemonic=="mov" and
                ins[0x7B0A8].op_str=="qword ptr [rdi + 0x10], rax",
                "Simulation object pointer storage changed")
        require(ins[0x8A9E6].op_str==hex(PREFERRED_BASE+0xF3FA4),
                "Native shared dispatcher call changed")

        # Derive the hkpWorld vtable via RIP-relative LEA, not a literal guess.
        vft_lea=ins[0x7A28E]
        dst=vft_lea.address+vft_lea.size+vft_lea.operands[1].mem.disp-PREFERRED_BASE
        require(dst == 0x2724038,"hkpWorld vftable address changed")
        world=rtti_vft(pe,dst)
        require(world["className"]==".?AVhkpWorld@@",
                "World constructor has unrelated RTTI owner")
        simulation=rtti_vft(pe,0x2725568)
        require(simulation["className"]==".?AVhkpMultiThreadedSimulation@@",
                "Simulation vftable owner has changed")
        method=struct.unpack("<Q", pe.get_data(0x2725568+18*8,8))[0]
        require(method==PREFERRED_BASE+0x8A8D8,
                "Simulation VFT slot 18 no longer links to type-1 producer")
        return {
            "status":"PASS",
            "taskId":"M3-001",
            "evidenceClass":"bounded exact-build code-byte and MSVC RTTI proof",
            "sourceSha256":source_hash, "preferredBase":hex(PREFERRED_BASE),
            "worldRtti":world,"simulationRtti":simulation,
            "verifiedInstructionBytes":{
                hex(rva):{"bytes":v.bytes.hex(),"asm":v.mnemonic+" "+v.op_str}
                for rva,v in sorted(ins.items())
            },
            "findings":[
                {"rva":"0x7a384","claim":"hkpWorld receiver +0x210 receives zero from r15, not a demonstrated type-7 queue handler writer",
                 "proven":True},
                {"rva":"0x7af8d","claim":"hkpWorld receiver +0x160 receives 32-bit state derived from rsi+0xd9, not the separate simulation queue pointer",
                 "proven":True},
                {"rva":"0x7b0a8","claim":"hkpWorld +0x10 holds the newly constructed hkpMultiThreadedSimulation pointer",
                 "proven":True},
                {"rva":"0x89bd7","claim":"hkpMultiThreadedSimulation constructor zeroes its own +0x160 queue field",
                 "proven":True},
                {"rva":"0x8a9df","claim":"hkpMultiThreadedSimulation method reads own +0x160 and calls shared dispatcher at 0x8a9e6",
                 "proven":True}
            ],
            "qualifiedType7Handler":False, "qualifiedType7JobProducer":False,
            "nonNullSimulationQueueAssignment":False,
            "limitations":[
                "The zero and scalar state assignments concern hkpWorld, not the native typed queue handler.",
                "Only selected instructions and the world-constructor preamble were byte-verified, not the full client call graph.",
                "RTTI association qualifies object class statically; dynamic receiver identity and type-7 usage remain unproven.",
                "No evidence establishes type-7 pathfinding is absent, enabled, or player-usable."
            ],
            "gameInputSent":False, "gameProcessAttached":False,
            "targetExecuted":False, "binaryModified":False,
        }
    finally:
        pe.close()


if __name__=="__main__":
    try:
        print(json.dumps(verify(),indent=2,sort_keys=True))
    except (OSError,ValueError,TypeError,KeyError) as exc:
        print(json.dumps({"status":"FAILED", "error":str(exc)}),file=sys.stderr)
        raise SystemExit(1)
