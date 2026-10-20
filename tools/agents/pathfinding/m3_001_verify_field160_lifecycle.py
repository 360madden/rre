#!/usr/bin/env python3
"""M3-001: verify a +0x160 allocation/release pair without inventing its owner.

Pin the original RIFT PE, V7 exact-run scan receipts, Win64 call/operand
sequence, and distinct construction paths. This is read-only offline
source interpretation, NOT a usable Rift navigation or job-queue API.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys
from typing import Any

BUILD_SHA="7c356c9dde9e12fcbff3c08d953b0630b48b1510a0ffb36e4ec164606e7b17bd"
EXE=Path(r"C:\Program Files (x86)\Glyph\Games\RIFT\Live\rift_x64.exe")
MAIN=Path(r"C:\work\rre")
BASE=0x140000000
PINNED_V7={
 "m3-001-near-simulation-160-writers-20261020-01":(
  "3ae128a9683de6d02e8297970761c921245ddb6b51fa56fdd2c3bf790c2002e2",
  "1e983d9ef5de1d79c0067a0639ee396c400a6e4748b135073e3666f2162e5ee1"),
 "m3-001-havok-simulation-field160-callers-20261020-01":(
  "4b9f9f0652fbabe6ecab224789445f66d95b175020eb91ce4cf3462fe84439b2",
  "f0691d0a0981fa10a39f791bb2b06b2d095400d117b5a0dd701631abe1f5da5d"),
 "m3-001-havok160-wrapper-owner-calls-20261020-01":(
  "5cbe58516c22367a752daf53ebaf9f2d8c2328b5941c01524d94780054df6dc8",
  "c03332511484e0fbcd2c0b77f3bd4194e590414f0c3e6617f493588a5f57ff5f"),
 "m3-001-havok-field160-wrapper-factory-20261020-01":(
  "f9d93856493db511c2f70028a0a58d84085c4ebe1e911d47dae9bc09b21365f4",
  "055c911cd4d499f0db9aa31312893ae6a8b8a6be60457c9a496451ada6c47ad5")
}
# Expected machine op patterns require exact original bytes via checked PE hash,
# PLUS concrete opcode/operands at the annotated RVA.
PINNED_CODE={
 0x89c50c:("mov","rdi, rcx"),
 0x89c600:("call",hex(BASE+0x77c230)),
 0x89c605:("mov","qword ptr [rdi + 0x160], rax"),
 0x89c9b9:("mov","rdi, rcx"),
 0x89c9d5:("xor","esi, esi"),
 0x89ca17:("mov","rcx, qword ptr [rdi + 0x160]"),
 0x89ca1e:("call",hex(BASE+0x77c240)),
 0x89ca2a:("mov","qword ptr [rdi + 0x160], rsi"),
 0x89ea8a:("mov","rdi, rcx"),
 0x89ea8d:("call",hex(BASE+0x89c4f0)),
 0x89e89a:("mov","rcx, rbp"),
 0x89e89d:("call",hex(BASE+0x89c990)),
 0x89e5e4:("mov","ecx, 0x1d8"),
 0x89e5ee:("call",hex(BASE+0x77c210)),
 0x89e6cb:("mov",None), # RIP global singleton pointer write
 0xfb5246:("call",hex(BASE+0x89e5d0)),
 0xfb524b:("mov","rcx, rax"),
 0xfb524e:("call",hex(BASE+0x89ea80)),
 0x7b087:("mov","ebx, 0x200"),
 0x7b092:("mov","edx, ebx"),
 0x7b094:("call",hex(BASE+0x71204)),
 0x7b0a3:("call",hex(BASE+0x89abc)),
 0x7b0a8:("mov","qword ptr [rdi + 0x10], rax")
}
CALLER_EDGES={
 "m3-001-havok-simulation-field160-callers-20261020-01":[
  (0x89c4f0,0x89ea8d), (0x89c990,0x89e89d)],
 "m3-001-havok160-wrapper-owner-calls-20261020-01":[
  (0x89ea80,0xfb524e),(0x89e6f0,0x89eb20)]
}


def _sha(b:bytes)->str:
    return hashlib.sha256(b).hexdigest()

def check(flag:bool,msg:str)->None:
    if not flag:
        raise ValueError(msg)

def validate_v7(root:Path=MAIN)->dict:
    captures={}
    for tag,(expected_artifact,expected_manifest) in PINNED_V7.items():
        art_path=root/"artifacts"/(tag+".json")
        man_path=root/"artifacts"/(tag+"-manifest.json")
        bytes_art=art_path.read_bytes();bytes_man=man_path.read_bytes()
        check(_sha(bytes_art)==expected_artifact,"Pinned V7 capture changed: "+tag)
        check(_sha(bytes_man)==expected_manifest,"Pinned V7 manifest changed: "+tag)
        art=json.loads(bytes_art);man=json.loads(bytes_man)
        check(art.get("sha256")==BUILD_SHA,"Wrong native source in V7: "+tag)
        check(man.get("source",{}).get("sha256")==BUILD_SHA,"Wrong manifest native source: "+tag)
        check(man.get("status")=="completed" and man.get("coverage",{}).get("boundedCaptureComplete") is True,
              "V7 coverage incomplete: "+tag)
        check(man.get("invocation",{}).get("exitCode")==0,"V7 did not successfully run: "+tag)
        check(man.get("artifact",{}).get("sha256")==expected_artifact,"Receipt SHA disagreement: "+tag)
        captures[tag]={"artifact":art,"manifest":man,"artifactSha256":expected_artifact,
                        "manifestSha256":expected_manifest}
    for tag,edges in CALLER_EDGES.items():
        sites={(int(x["targetRva"],16),int(x["siteRva"],16))
               for x in captures[tag]["artifact"].get("callerReferences",[])
               if x.get("instructionBoundaryVerifiedFromPeRange") is True}
        for edge in edges:
            check(edge in sites,f"Qualified direct caller not in V7 evidence: {tag} {edge}")
    return captures


def verify(binary:Path=EXE,root:Path=MAIN,strict_capture:bool=True)->dict:
    import capstone
    import pefile
    from capstone.x86_const import X86_OP_REG,X86_REG_RSI,X86_REG_ESI,X86_REG_SI,X86_REG_SIL

    raw=binary.read_bytes();digest=_sha(raw)
    check(digest==BUILD_SHA,"Pinned RIFT PE SHA mismatch")
    pe=pefile.PE(data=raw,fast_load=True)
    try:
        check(int(pe.OPTIONAL_HEADER.ImageBase)==BASE and int(pe.FILE_HEADER.Machine)==0x8664,
              "Unexpected x64 PE identity")
        md=capstone.Cs(capstone.CS_ARCH_X86,capstone.CS_MODE_64);md.detail=True
        decoded={}
        for rva,(mnemonic,operands) in PINNED_CODE.items():
            insn=next(md.disasm(pe.get_data(rva,16),BASE+rva,count=1),None)
            check(insn is not None and insn.address==BASE+rva,f"Missing instruction boundary {hex(rva)}")
            check(insn.mnemonic==mnemonic and (operands is None or insn.op_str==operands),
                  f"Unexpected opcode/operand at {hex(rva)}")
            decoded[rva]={"bytes":insn.bytes.hex(),"asm":insn.mnemonic+" "+insn.op_str}
        def full_region(start:int,end:int):
            rows=list(md.disasm(pe.get_data(start,end-start),BASE+start))
            check(bool(rows) and rows[-1].address+rows[-1].size==BASE+end,
                  f"Incomplete unwind-bounded region {hex(start)}")
            return rows
        alloc_rows=full_region(0x89c4f0,0x89c746)
        release_rows=full_region(0x89c990,0x89cb27)
        wrapper_init=full_region(0x89ea80,0x89eacf)
        wrapper_cleanup=full_region(0x89e6f0,0x89e8a7)
        # Call->store is adjacent, with no instruction overwriting RAX.
        a={x.address-BASE:i for i,x in enumerate(alloc_rows)}
        check(a[0x89c605]==a[0x89c600]+1,
              "Allocator return is no longer immediately stored at +0x160")
        # Release method aliases this in RDI, takes field pointer in RCX,
        # passes it to release call, then assigns zero/nonvolatile RSI.
        b={x.address-BASE:i for i,x in enumerate(release_rows)}
        check(b[0x89ca1e]==b[0x89ca17]+1,
              "Release call is not immediately after +0x160 load")
        check(all(
          not(inst.operands and inst.operands[0].type==X86_OP_REG and
              inst.operands[0].reg in (X86_REG_RSI,X86_REG_ESI,X86_REG_SI,X86_REG_SIL))
          for inst in release_rows[b[0x89c9d5]+1:b[0x89ca2a]]),
          "RSI overwritten before field clear")
        check(decoded[0x89e6cb]["asm"].startswith("mov qword ptr [rip + "),
              "Factory global store signature changed")
        # This global factory code creates a 0x1D8 allocation. The world-
        # constructor code separately requests a 0x200 object before 0x89ABC.
        # Do not equate these two pointer identities without further proof.
        receipt=validate_v7(root) if strict_capture else {}
        return {
          "status":"PASS", "taskId":"M3-001", "sourceBuildSha256":digest,
          "scope":"bounded exact PE x64 source + V7 direct callers, not runtime class ownership",
          "fieldOffset":"0x160",
          "allocationCandidate":{"functionRva":"0x89c4f0",
            "storeRva":"0x89c605","sourceCallRva":"0x89c600",
            "allocatorRva":"0x77c230","receiverRegister":"rdi",
            "potentiallyNonnull":True,
            "actualNonNullGuaranteed":False},
          "matchingReleaseCandidate":{"functionRva":"0x89c990",
            "loadRva":"0x89ca17","releaseCallRva":"0x89ca1e",
            "releaseFunctionRva":"0x77c240","clearRva":"0x89ca2a",
            "clearValue":"RSI was zeroed at 0x89c9d5"},
          "wrapperCallGraph":[
             ["0xfb524e","0x89ea80"],
             ["0x89ea8d","0x89c4f0"],
             ["0x89e89d","0x89c990"],
             ["0x89eb20","0x89e6f0"]],
          "globalFactory":{"start":"0x89e5d0","requestedBytes":472,
                           "allocatorCall":"0x89e5ee","returnIntoInitCallSite":"0xfb5246->0xfb524e",
                           "objectClassQualified":False},
          "separateWorldSimulationConstruction":{
            "worldRequestedObjectBytes":512,
            "constructorRva":"0x89abc","worldSimulationPointerStoreRva":"0x7b0a8",
            "sameAsGlobalFactoryObjectProven":False},
          "pinnedInsns":{hex(k):v for k,v in sorted(decoded.items())},
          "decodedRegions":[{"beginRva":hex(first),"endRvaExclusive":hex(last),"instructionCount":len(rows)}
                for first,last,rows in [(0x89c4f0,0x89c746,alloc_rows),
                                       (0x89c990,0x89cb27,release_rows),
                                       (0x89ea80,0x89eacf,wrapper_init),
                                       (0x89e6f0,0x89e8a7,wrapper_cleanup)]],
          "v7CapturePins":[{"tag":name,"artifactSha256":r["artifactSha256"],
                            "manifestSha256":r["manifestSha256"]}
                    for name,r in receipt.items()],
          "simulationOwnerVerifiedForTheseWrites":False,
          "nonnullSimulationQueueWriterProven":False,
          "type7HandlerProven":False,"type7JobProducerProven":False,
          "limitations":[
             "One +0x160 field receives an allocator result and later is freed/zeroed, but caller chain reaches a separately initialized global object whose class is not qualified.",
             "Allocation success/nonnull is not guaranteed by observing a return register.",
             "The hkpWorld simulation object is constructed in a separate 0x200 allocation path; no dynamic object alias or same-class proof between that and the 0x1D8 global factory.",
             "V7 direct E8 call search is bounded; indirect/virtual/tail callers may be missing.",
             "No route generation, typed queue+0x210 registration, true job type 7, player movement or game behavior proved."
          ],
          "gameInputSent":False,"processAttached":False,"binaryModified":False
        }
    finally:
        pe.close()


if __name__=="__main__":
    try:
        print(json.dumps(verify(),sort_keys=True,indent=2))
    except (OSError,ValueError,TypeError,KeyError) as exc:
        print(json.dumps({"status":"FAILED","error":str(exc)}),file=sys.stderr)
        raise SystemExit(1)
