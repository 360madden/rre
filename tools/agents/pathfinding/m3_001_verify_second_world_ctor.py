#!/usr/bin/env python3
"""Read-only second hkpWorld constructor alias proof for RRE M3-001.

Verifies that RVA 0x79A9F is a ZERO store on hkpWorld, not a registered
type-7 pathfinding queue callback. Does not launch or attach to the game.
"""
from __future__ import annotations
import hashlib
import json
import pathlib
import sys

from m3_001_verify_world_owner import BUILD_SHA, DEFAULT_EXE, PREFERRED_BASE, require, rtti_vft

EXPECTED = {
    0x799B9: "488bd9",           # rbx <- world this
    0x799BC: "488d0575a66a02",  # world virtual table
    0x799C9: "488901",           # world virtual table install
    0x799D1: "33c9",             # rcx <- zero via xor ecx,ecx
    0x79A9F: "48898b10020000",  # hkpWorld +0x210 <- zero rcx
}


def verify(binary: pathlib.Path = DEFAULT_EXE) -> dict:
    import capstone
    import pefile
    content = binary.read_bytes()
    digest = hashlib.sha256(content).hexdigest()
    require(digest == BUILD_SHA, "Original Rift binary hash mismatch")
    pe = pefile.PE(data=content,fast_load=True)
    try:
        require(int(pe.OPTIONAL_HEADER.ImageBase)==PREFERRED_BASE, "Unexpected PE preferred base")
        md = capstone.Cs(capstone.CS_ARCH_X86,capstone.CS_MODE_64)
        md.detail = True
        start,end=0x799A4,0x79B41
        rows=list(md.disasm(pe.get_data(start,end-start),PREFERRED_BASE+start))
        require(bool(rows) and rows[-1].address+rows[-1].size == PREFERRED_BASE+end,
                "Incomplete constructor-region instruction-boundary decoding")
        by_rva={x.address-PREFERRED_BASE:x for x in rows}
        for rva,blob in EXPECTED.items():
            require(rva in by_rva and by_rva[rva].bytes.hex()==blob,
                    f"Pinned instruction offset/bytes changed at {hex(rva)}")
        require(by_rva[0x799B9].op_str=="rbx, rcx","World object base alias changed")
        require(by_rva[0x799D1].op_str=="ecx, ecx" and
                by_rva[0x799D1].mnemonic=="xor","World +0x210 zero source changed")
        require(by_rva[0x79A9F].op_str=="qword ptr [rbx + 0x210], rcx",
                "World +0x210 store target/value changed")
        # Relevant code between XOR and store contains no RCX definition
        # and no call that could overwrite caller-saved RCX.
        i0=rows.index(by_rva[0x799D1]);i1=rows.index(by_rva[0x79A9F])
        require(i0<i1,"Reaching definition order changed")
        between=rows[i0+1:i1]
        require(all(ins.mnemonic!="call" for ins in between),
                "Unexpected call invalidates zero reaching definition")
        require(all(
            not(ins.operands and ins.operands[0].type==capstone.x86_const.X86_OP_REG and
                ins.operands[0].reg in (capstone.x86_const.X86_REG_RCX,
                                        capstone.x86_const.X86_REG_ECX,
                                        capstone.x86_const.X86_REG_CX,
                                        capstone.x86_const.X86_REG_CL))
            for ins in between
        ), "RCX overwritten before world+0x210 store")
        lea=by_rva[0x799BC]
        vft=lea.address+lea.size+lea.operands[1].mem.disp-PREFERRED_BASE
        require(vft==0x2724038,"hkpWorld virtual table no longer matches first constructor")
        owner=rtti_vft(pe,vft)
        require(owner["className"]==".?AVhkpWorld@@", "Not hkpWorld MSVC RTTI class")
        return {
            "status":"PASS", "sourceSha256":digest, "taskId":"M3-001",
            "scope":"complete PE-unwind method RVA 0x799A4..0x79B41 plus exact RTTI",
            "decodedInstructions":len(rows),"regionCoversAllInstructions":True,
            "worldVtable":owner,
            "zeroRegisterDefRva":"0x799d1",
            "fieldStoreRva":"0x79a9f",
            "fieldStoreBytes":EXPECTED[0x79A9F],
            "fieldStoreInstruction":"mov qword ptr [rbx + 0x210], rcx",
            "zeroReachingDefinitionConfirmed":True,
            "qualifiedWorldFieldZero":True,
            "qualifiedQueueType7Registration":False,
            "conclusion":"hkpWorld+0x210 is initialized to zero; matching +0x210 does not establish a queue handler",
            "limitations":[
                "This verifies one native constructor, not the origin of the actual job queue object.",
                "Original PE RTTI and linear instructions do not prove dynamic execution.",
                "A separate registered type-7 handler or job producer elsewhere is neither found nor excluded."
            ],
            "offlineOnly":True, "gameInputSent":False,"gameProcessAttached":False
        }
    finally:
        pe.close()


if __name__=="__main__":
    try:
        print(json.dumps(verify(),indent=2,sort_keys=True))
    except (OSError,ValueError,TypeError,KeyError) as error:
        print(json.dumps({"status":"FAILED","error":str(error)}),file=sys.stderr)
        raise SystemExit(1)
