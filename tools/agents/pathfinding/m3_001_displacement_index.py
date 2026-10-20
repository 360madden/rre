#!/usr/bin/env python3
"""Bounded, original-PE x64 memory displacement index for RRE M3-001.

This is a *source locator*, never a proof of same-object job-queue ownership.
Only read the qualified on-disk executable; no native execution or I/O to RIFT.
"""
from __future__ import annotations

import argparse
import bisect
from collections import Counter
import hashlib
import json
from pathlib import Path
import struct
import sys

BUILD_SHA = "7c356c9dde9e12fcbff3c08d953b0630b48b1510a0ffb36e4ec164606e7b17bd"
BINARY = Path(r"C:\Program Files (x86)\Glyph\Games\RIFT\Live\rift_x64.exe")
IMAGE_BASE = 0x140000000
FIELDS = (0x160, 0x210)
WRITE_MNEMONICS = frozenset(("mov", "movabs", "movaps", "movups", "movdqu",
                              "movsd", "movss", "movq", "vmovdqu", "vmovups",
                              "vmovaps", "pop"))
RMW_MNEMONICS = frozenset(("and","or","xor","add","sub","inc","dec","xchg",
                           "xadd","cmpxchg","bts","btr","btc","shr","shl"))
READ_MNEMONICS = frozenset(("cmp","test","bt","call","jmp","push"))


def classify(mnemonic: str, op_index: int, immediate_zero: bool) -> tuple[str, bool]:
    """Syntactic access class only; excludes semantic object identity."""
    m = mnemonic.lower()
    if m == "lea":
        return "address-only", False
    if m in READ_MNEMONICS:
        return "read", False
    if op_index != 0:
        return "read", False
    if m in WRITE_MNEMONICS:
        return "write", immediate_zero
    if m in RMW_MNEMONICS:
        return "read-modify-write", immediate_zero and m in ("and",)
    return "unknown", False


def scan(start: int, end: int, max_ranges: int = 5000,
         max_bytes: int = 7500000) -> dict:
    import pefile
    import capstone
    from capstone.x86_const import (X86_OP_MEM, X86_OP_IMM, X86_OP_REG,
        X86_REG_RBP, X86_REG_EBP, X86_REG_BP, X86_REG_BPL,
        X86_REG_RSP, X86_REG_ESP)

    raw = BINARY.read_bytes()
    source_sha = hashlib.sha256(raw).hexdigest()
    if source_sha != BUILD_SHA:
        raise ValueError("Pinned binary SHA mismatch: no disassembly attempted")
    pe = pefile.PE(data=raw, fast_load=True)
    try:
        if int(pe.OPTIONAL_HEADER.ImageBase) != IMAGE_BASE:
            raise ValueError("Unexpected native PE image base")
        section = next((s for s in pe.sections
                        if s.Name.rstrip(b"\0")==b".text"), None)
        if section is None:
            raise ValueError("Executable .text section missing")
        base = int(section.VirtualAddress)
        section_end = base + min(int(section.SizeOfRawData),
                                 int(section.Misc_VirtualSize))
        if not (base <= start < end <= section_end):
            raise ValueError("Requested RVA window not fully within .text")
        code = pe.get_data(start,end-start)
        raw_hits = []
        for offset in FIELDS:
            pat = struct.pack("<I",offset)
            pos = 0
            while True:
                loc = code.find(pat,pos)
                if loc < 0: break
                raw_hits.append((start+loc,offset))
                pos=loc+1
        pe.parse_data_directories(
            directories=[pefile.DIRECTORY_ENTRY["IMAGE_DIRECTORY_ENTRY_EXCEPTION"]])
        ranges = sorted(set((int(e.struct.BeginAddress),
                             int(e.struct.EndAddress)) for e in pe.DIRECTORY_ENTRY_EXCEPTION))
        starts = [x[0] for x in ranges]
        chosen: set[tuple[int,int]] = set()
        no_unwind = 0
        for rva,_ in raw_hits:
            i = bisect.bisect_right(starts,rva)-1
            if i < 0 or not (ranges[i][0] <= rva < ranges[i][1]):
                no_unwind+=1
                continue
            chosen.add(ranges[i])
        md=capstone.Cs(capstone.CS_ARCH_X86,capstone.CS_MODE_64)
        md.detail=True
        scanned=0
        total_bytes=0
        decoded_rows=0
        skipped_large=0
        skipped_budget=0
        incomplete=0
        records={}
        for first,last in sorted(chosen):
            span=last-first
            if span<=0 or span>16384:
                skipped_large+=1
                continue
            if scanned>=max_ranges or total_bytes+span>max_bytes:
                skipped_budget+=1
                continue
            blob=pe.get_data(first,span)
            instructions=list(md.disasm(blob,IMAGE_BASE+first))
            if not instructions or instructions[-1].address+instructions[-1].size!=IMAGE_BASE+last:
                incomplete+=1
                continue
            scanned+=1
            total_bytes+=span
            decoded_rows+=len(instructions)
            # Track RBP only after a concrete same-region definition deriving it
            # from RSP. A later write invalidates the frame-alias qualification.
            # This is narrower than blindly labeling every RBP operand local.
            rbp_from_rsp=False
            for ix,ins in enumerate(instructions):
                ops=ins.operands
                if (ops and ops[0].type==X86_OP_REG and
                    ops[0].reg in (X86_REG_RBP,X86_REG_EBP,X86_REG_BP,X86_REG_BPL) and
                    ins.mnemonic not in ('push','cmp','test')):
                    is_lea=(ins.mnemonic=='lea' and len(ops)>1 and
                            ops[1].type==X86_OP_MEM and
                            ops[1].mem.base in (X86_REG_RSP,X86_REG_ESP))
                    is_mov=(ins.mnemonic=='mov' and len(ops)>1 and
                            ops[1].type==X86_OP_REG and
                            ops[1].reg in (X86_REG_RSP,X86_REG_ESP))
                    rbp_from_rsp=is_lea or is_mov
                for op_index,op in enumerate(ops):
                    if op.type != X86_OP_MEM or op.mem.disp not in FIELDS or op.size!=8:
                        continue
                    value = op.mem.disp
                    rhs = ins.operands[1] if len(ins.operands)>1 else None
                    immediate_zero = bool(rhs and rhs.type==X86_OP_IMM and rhs.imm==0)
                    access,null = classify(ins.mnemonic,op_index,immediate_zero)
                    key=(ins.address-IMAGE_BASE,value)
                    if key in records:
                        if records[key]["bytes"]!=bytes(ins.bytes).hex():
                            raise ValueError("Conflicting PE unwind disassembly at "+hex(key[0]))
                        continue
                    reg=md.reg_name(op.mem.base) if op.mem.base else None
                    idx=md.reg_name(op.mem.index) if op.mem.index else None
                    direct_stack=reg in ("rsp","esp")
                    qualified_rbp_frame=reg in ("rbp","ebp") and rbp_from_rsp
                    records[key]={
                        "rva":hex(ins.address-IMAGE_BASE),
                        "bytes":bytes(ins.bytes).hex(),
                        "asm":ins.mnemonic+" "+ins.op_str,
                        "field":hex(value),
                        "operandIndex":op_index,
                        "accessClass":access,
                        "immediateZeroStore":null,
                        "baseRegister":reg,
                        "indexRegister":idx,
                        "qwordBytes":8,
                        "stackByRsp":direct_stack,
                        "stackBaseQualified":direct_stack or qualified_rbp_frame,
                        "stackBaseProvenance":(
                            "direct-RSP" if direct_stack else
                            "RBP-derived-from-RSP-in-current-unwind-range"
                            if qualified_rbp_frame else None),
                        "unwindRange":[hex(first),hex(last)],
                        "neighbors":[{"rva":hex(x.address-IMAGE_BASE),"asm":x.mnemonic+" "+x.op_str}
                                     for x in instructions[max(0,ix-2):min(len(instructions),ix+3)]],
                        "sameHavokSimulationReceiverProven":False,
                        "registeredType7HandlerProven":False,
                    }
        ordered=[records[key] for key in sorted(records)]
        # Never present a stack-based write or read as a queue-pointer writer.
        potential=[r for r in ordered if
                   r["field"]=="0x160" and r["accessClass"] in ("write","read-modify-write")
                   and not r["stackBaseQualified"] and not r["immediateZeroStore"]]
        return {
            "schemaVersion":1,"taskId":"M3-001",
            "scope":"bounded original binary x64 PE-unwind code-source index (not complete dataflow)",
            "buildSha256":source_sha,"scanRvaRange":[hex(start),hex(end)],
            "rawFourByteDisplacementMatches":len(raw_hits),
            "distinctUnwindRangesMatchingRawBytes":len(chosen),
            "qualifiedDecodedRanges":scanned,
            "decodedInstructionCount":decoded_rows,
            "decodedCodeBytes":total_bytes,
            "rawMatchesWithoutSingleSelectedUnwindRange":no_unwind,
            "skippedRangesAbove16K":skipped_large,
            "skippedDueToRangeOrByteBudget":skipped_budget,
            "skippedIncompleteDecoding":incomplete,
            "byteAndRangeBudget":[max_ranges,max_bytes],
            "candidateCount":len(ordered),
            "byAccessClass":dict(sorted(Counter(x["accessClass"] for x in ordered).items())),
            "byField":dict(sorted(Counter(x["field"] for x in ordered).items())),
            "qualifiedStackFrameMatches":sum(x["stackBaseQualified"] for x in ordered),
            "potentialNonnullField160Writes":potential,
            "records":ordered,
            "type7HandlerQualified":False,
            "nonNullSimulationQueueWriterQualified":False,
            "scanCompleteWithinPeUnwindMethod":(skipped_large+skipped_budget+incomplete==0),
            "limitations":[
                "Byte literal matches include data/unaligned bytes; candidate instructions were decoded from PE unwind starts with a complete decode boundary.",
                "PE unwind metadata can miss leaf, indirect and alternate owner paths.",
                "A memory-first CMP is a read, not a write. RBP is marked stack-derived only after an exact RSP-relative definition in the same decoded unwind region with no intervening RBP overwrite.",
                "An unqualified RBP may still point to a stack frame or another object; lack of frame proof does not establish heap ownership.",
                "A syntactically nonzero register operand does not prove register value nonzero.",
                "Same hkpMultiThreadedSimulation receiver pointer is never inferred from matching +0x160 displacement alone.",
                "No player control, game process access, native execution, or actual type-7 producer is established.",
            ],
            "offlineOnly":True,"gameInputSent":False,"gameProcessAttached":False
        }
    finally:
        pe.close()


def main(argv:list[str]|None=None)->int:
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--start",type=lambda s:int(s,0),default=0x1000)
    p.add_argument("--end",type=lambda s:int(s,0),default=0x400000)
    p.add_argument("--summary",action="store_true")
    args=p.parse_args(argv)
    try:
        data=scan(args.start,args.end)
        if args.summary:
            # Summary retains every plausible syntactic non-stack +0x160 write,
            # but not the full source windows (which are reproducible on demand).
            data["records"]=data["records"][:28]
            data["shownRecordsTruncated"]=data["candidateCount"]>28
        print(json.dumps(data,indent=2,sort_keys=True))
        return 0 if data["scanCompleteWithinPeUnwindMethod"] else 1
    except (OSError,ValueError,TypeError) as exc:
        print(json.dumps({"status":"failed","error":str(exc),
                          "type7HandlerQualified":False}),file=sys.stderr)
        return 2


if __name__=="__main__":
    raise SystemExit(main())
