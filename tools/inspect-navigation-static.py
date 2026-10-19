#!/usr/bin/env python3
"""Exact-build offline navigation inspection; reuses RiftReader and installed libraries."""
from __future__ import annotations
import argparse
import bisect
import hashlib
import importlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.dont_write_bytecode = True

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--binary", type=Path, required=True)
    p.add_argument("--helper", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    p.add_argument("--expected-sha256", required=True)
    p.add_argument("--expected-helper-sha256", required=True)
    p.add_argument("--rva", action="append", required=True)
    p.add_argument("--depth", type=int, choices=(0, 1, 2), default=1)
    p.add_argument("--follow-unwind-chains", action="store_true")
    p.add_argument("--caller-rva", action="append", default=[])
    args = p.parse_args()
    if args.output.exists():
        raise RuntimeError("Output exists; choose a new evidence filename.")
    binary_bytes = args.binary.read_bytes()
    actual_hash = hashlib.sha256(binary_bytes).hexdigest()
    if actual_hash != args.expected_sha256.lower():
        raise RuntimeError("Exact-build SHA256 mismatch.")
    helper_hash = hashlib.sha256(args.helper.read_bytes()).hexdigest()
    if helper_hash != args.expected_helper_sha256.lower():
        raise RuntimeError("Existing helper changed; review it before import.")
    sys.path.insert(0, str(args.helper.parent))
    helper = importlib.import_module(args.helper.stem)
    if Path(helper.__file__).resolve() != args.helper.resolve():
        raise RuntimeError("Unexpected helper import location.")
    import pefile
    import capstone
    from capstone.x86_const import X86_OP_IMM, X86_OP_MEM, X86_REG_RIP
    pe = pefile.PE(data=binary_bytes, fast_load=True)
    if pe.FILE_HEADER.Machine != 0x8664:
        raise RuntimeError("Expected x64 PE.")
    pe.parse_data_directories(directories=[
        pefile.DIRECTORY_ENTRY["IMAGE_DIRECTORY_ENTRY_EXCEPTION"]
    ])
    ranges = sorted(
        (int(item.struct.BeginAddress), int(item.struct.EndAddress))
        for item in getattr(pe, "DIRECTORY_ENTRY_EXCEPTION", [])
        if int(item.struct.BeginAddress) < int(item.struct.EndAddress)
    )
    starts = [entry[0] for entry in ranges]
    exception_entries = {
        int(item.struct.BeginAddress): item
        for item in getattr(pe, "DIRECTORY_ENTRY_EXCEPTION", [])
    }
    chain_roots, chain_groups = {}, {}
    for begin in exception_entries:
        current, seen = begin, set()
        while current not in seen:
            seen.add(current)
            item = exception_entries.get(current)
            if item is None or item.unwindinfo is None:
                current = None
                break
            if not getattr(item.unwindinfo, "UNW_FLAG_CHAININFO", False):
                break
            current = int(item.unwindinfo.FunctionEntry)
        else:
            current = None
        chain_roots[begin] = current
        if current is not None:
            chain_groups.setdefault(current, []).append(begin)
    expanded_chains = set()
    image_base, sections, errors = helper.executable_sections(args.binary)
    if errors:
        raise RuntimeError(str(errors))
    if image_base != int(pe.OPTIONAL_HEADER.ImageBase):
        raise RuntimeError("PE image-base mismatch.")
    # The helper reads its own section buffers. Recheck the file after acquisition
    # to detect an updater changing the source between those reads.
    if hashlib.sha256(args.binary.read_bytes()).hexdigest() != actual_hash:
        raise RuntimeError("Binary changed while acquiring section buffers.")
    def containing(rva):
        index = bisect.bisect_right(starts, rva) - 1
        if index >= 0 and ranges[index][0] <= rva < ranges[index][1]:
            return ranges[index]
        return None
    decoder = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_64)
    decoder.detail = True
    pending = [(int(value, 0), 0, "requested anchor") for value in args.rva]
    caller_references = []
    for value in args.caller_rva:
        target = int(value, 0)
        candidates = helper.find_direct_call_sites(sections, target, max_sites=64)
        for candidate in candidates:
            site = int(candidate["callRva"], 0)
            bounds = containing(site)
            verified = False
            if bounds and site-bounds[0] < 65536:
                prefix = helper.read_section_bytes(sections, bounds[0], site-bounds[0]+5)
                for insn in decoder.disasm(prefix, image_base+bounds[0]):
                    if int(insn.address)-image_base == site:
                        verified = (insn.mnemonic == "call" and bool(insn.operands)
                                    and insn.operands[0].type == X86_OP_IMM
                                    and int(insn.operands[0].imm)-image_base == target)
                        break
            caller_references.append({
                "targetRva":hex(target), "siteRva":hex(site),
                "instructionBoundaryVerifiedFromPeRange":verified,
                "containingPeRange":[hex(x) for x in bounds] if bounds else None,
                "candidateLimit":64
            })
            if verified:
                pending.append((site,0,"verified direct caller of "+hex(target)))
    functions, unresolved, visited = [], [], set()
    while pending and len(functions) < 40:
        anchor, depth, reason = pending.pop(0)
        bounds = containing(anchor)
        if bounds is None:
            unresolved.append({"rva":hex(anchor), "reason":"No containing PE runtime-function entry; no guessed function boundary used."})
            continue
        begin, end = bounds
        chain_root = chain_roots.get(begin)
        if args.follow_unwind_chains and chain_root is not None and chain_root not in expanded_chains:
            expanded_chains.add(chain_root)
            siblings = sorted(chain_groups[chain_root])
            pending[0:0] = [(sibling, depth, "PE unwind-chain member of " + hex(chain_root))
                            for sibling in siblings if sibling != begin]
        if begin in visited:
            continue
        visited.add(begin)
        requested_size = end - begin
        size = min(requested_size, 16384)
        data = helper.read_section_bytes(sections, begin, size)
        rows, calls, rip_refs = [], [], []
        decoded_end = begin
        for insn in decoder.disasm(data, image_base + begin):
            rva = int(insn.address) - image_base
            row = {"rva":hex(rva), "bytes":bytes(insn.bytes).hex(),
                   "instruction":f"{insn.mnemonic} {insn.op_str}".strip()}
            rows.append(row)
            decoded_end = rva + insn.size
            if insn.mnemonic == "call" and insn.operands:
                operand = insn.operands[0]
                if operand.type == X86_OP_IMM:
                    target = int(operand.imm) - image_base
                    calls.append({"siteRva":hex(rva), "targetRva":hex(target), "kind":"direct"})
                    if depth < args.depth and helper.section_for_rva(sections, target):
                        pending.append((target, depth + 1, "direct callee of " + hex(begin)))
                else:
                    calls.append({"siteRva":hex(rva), "kind":"indirect", "operand":insn.op_str})
            for operand in insn.operands:
                if operand.type == X86_OP_MEM and operand.mem.base == X86_REG_RIP:
                    target = rva + insn.size + int(operand.mem.disp)
                    rip_refs.append({"siteRva":hex(rva), "targetRva":hex(target)})
        functions.append({
            "anchorRva":hex(anchor), "rangeSource":"PE IMAGE_DIRECTORY_ENTRY_EXCEPTION",
            "unwindChainRootRva":hex(chain_root) if chain_root is not None else None,
            "unwindFlags":int(exception_entries[begin].unwindinfo.Flags) if exception_entries[begin].unwindinfo else None,
            "beginRva":hex(begin), "endRvaExclusive":hex(end), "depth":depth, "reason":reason,
            "windowTruncated":requested_size > len(data),
            "decodedThroughRvaExclusive":hex(decoded_end),
            "instructionDecodingCoversWindow":decoded_end == begin + len(data),
            "windowSha256":hashlib.sha256(data).hexdigest(),
            "directAndIndirectCalls":calls, "ripRelativeReferences":rip_refs,
            "existingHelperSummary":helper.summarize_function_window(
                image_base=image_base, sections=sections, function_rva=begin,
                function_bytes=len(data), max_rows=128),
            "instructions":rows
        })
    result = {
        "schemaVersion":1, "createdAtUtc":datetime.now(timezone.utc).isoformat(),
        "method":"Offline PE metadata and Capstone; existing RiftReader summary helper",
        "reaDecompilation":False, "gameInputSent":False, "gameProcessAttached":False,
        "targetExecuted":False, "binary":str(args.binary), "sha256":actual_hash,
        "imageBase":hex(image_base), "helper":str(args.helper), "helperSha256":helper_hash,
        "dependencies":{"pefile":pefile.__version__, "capstone":capstone.__version__},
        "runtimeFunctionRangeCount":len(ranges), "followUnwindChains":args.follow_unwind_chains,
        "functions":functions,
        "unresolvedAnchors":unresolved, "queueRemaining":len(pending),
        "callerReferences":caller_references,
        "limitations":[
            "PE runtime-function ranges are unwind regions, not a guarantee of complete high-level function boundaries.",
            "Linear disassembly does not establish every instruction as runtime-reachable.",
            "Existing helper field labels are candidates; its register tracking is not full data-flow analysis.",
            "Indirect calls are recorded but not resolved; no route, collision or actual velocity semantics are implied.",
            "Leaf functions without PE runtime-function entries remain unresolved."
        ]
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("x", encoding="utf-8", newline="\n") as output:
        json.dump(result, output, indent=2)
        output.write("\n")
    print(json.dumps({"output":str(args.output), "sha256":actual_hash,
        "functions":len(functions), "unresolved":len(unresolved), "queueRemaining":len(pending),
        "ranges":[{"begin":f["beginRva"],"end":f["endRvaExclusive"],
                   "callCount":len(f["directAndIndirectCalls"])} for f in functions],
        "callerReferences":caller_references}))
    pe.close()

if __name__ == "__main__":
    main()
