#!/usr/bin/env python3
"""M3-001 read-only triage of archived native-code disassembly.

This scans ONLY eleven locally saved schema-1 research artifacts. A memory
displacement alone NEVER proves a queue owner, typed handler, or job producer.
No live process, PE import, decompilation, input, or game memory is accessed.
"""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import re
import sys

BUILD_SHA = "7c356c9dde9e12fcbff3c08d953b0630b48b1510a0ffb36e4ec164606e7b17bd"
DIR = Path(__file__).resolve().parent
ARTIFACT_NAMES = tuple([f"_query{i}.json" for i in range(1, 6)] + [
    "m3-001-type3-producer-20261019.json",
    "m3-001-type1-producer-20261019.json",
    "m3-001-producer-address-refs-20261019.json",
    "m3-001-wrapper-owner-refs-20261019.json",
    "m3-001-physics-owner-table-refs-20261019.json",
    "m3-001-simulation-ctor-20261019.json",
])
OFFSETS = frozenset((0x160, 0x210, 0x130, 0x48, 0x50))
MEMORY = re.compile(r"\[([^\]]+)\]", re.I)
POSITIVE_DISP = re.compile(r"\+\s*0x([a-f0-9]+)\b", re.I)
HEX = re.compile(r"^(?:0x)?[0-9a-f]+$", re.I)
RMW = frozenset({"add", "sub", "and", "or", "xor", "inc", "dec",
                 "bts", "btr", "btc", "neg", "not", "xadd", "cmpxchg",
                 "shl", "shr", "sar", "rol", "ror"})
READ_ONLY = frozenset({"cmp", "test", "bt", "push", "call", "jmp", "prefetchnta",
                       "prefetcht0", "prefetcht1", "prefetcht2"})


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def classify_assembly(asm: str) -> list[dict]:
    """Find exact positive memory displacements; no text-only offset guessing.

    Access classes are instruction-operand syntactic classifications, not
    dynamic data flow. 'lea' computes an address, not a memory read.
    """
    if not isinstance(asm, str) or " " not in asm:
        return []
    mnemonic, operands = asm.strip().lower().split(None, 1)
    # Input artifacts have Intel syntax. A single read-modify-write instruction
    # can contain multiple memory references; do not assume impossible aliases.
    pair = operands.split(",", 1)
    lhs, rhs = pair[0].strip(), pair[1].strip() if len(pair) > 1 else ""
    matches = []
    for m in MEMORY.finditer(operands):
        expr = m.group(1)
        for o in POSITIVE_DISP.finditer(expr):
            displacement = int(o.group(1), 16)
            if displacement not in OFFSETS:
                continue
            # 'lea' is not a memory access; keep it as address-only evidence.
            in_left = m.start() < len(lhs)
            if mnemonic == "lea":
                access = "address-only"
            elif mnemonic in READ_ONLY or mnemonic.startswith("prefetch"):
                access = "read"
            elif mnemonic in RMW or mnemonic.startswith("lock"):
                access = "read-modify-write" if in_left else "read"
            elif mnemonic == "pop":
                access = "write"
            elif mnemonic == "xchg":
                access = "read-modify-write"
            elif (mnemonic.startswith("mov") or mnemonic in {"vmovaps", "stosb", "stosd", "stosq"}):
                access = "write" if in_left else "read"
            elif mnemonic in {"cmpxchg", "xadd"}:
                access = "read-modify-write"
            else:
                access = "ambiguous" if in_left else "read"
            # Only immediate-zero stores qualify automatically. Register
            # sources need explicit reaching-definition proof.
            zero = access == "write" and in_left and rhs in {"0", "0x0", "00h"}
            matches.append({"offsetLabel": hex(displacement),
                            "memoryExpression": expr,
                            "accessClass": access,
                            "nullOrZeroWrite": zero})
    return matches


def _verify_artifact(obj: dict, path: str) -> None:
    if not isinstance(obj, dict) or obj.get("schemaVersion") != 1:
        raise ValueError(f"Unexpected schema version in {path}")
    if obj.get("sha256") != BUILD_SHA:
        raise ValueError(f"Binary SHA mismatch in {path}")
    for name in ("reaDecompilation", "gameInputSent", "gameProcessAttached",
                 "targetExecuted"):
        if obj.get(name) is True:
            raise ValueError(f"Unsafe historical artifact marker in {path}: {name}")
    if "functions" in obj and not isinstance(obj["functions"], list):
        raise ValueError(f"Malformed functions in {path}")


def _neighbors(items: list, index: int, distance: int = 3) -> dict:
    result = {}
    for title, values in (("before", items[max(0, index-distance):index]),
                          ("after", items[index+1:index+distance+1])):
        result[title] = [{"rva": r.get("rva"), "instruction": r.get("instruction")}
                         for r in values]
    return result


def collect(directory: Path = DIR, names: tuple[str, ...] = ARTIFACT_NAMES) -> dict:
    """Fail closed on missing input, conflicting bytes, unexpected build/schema."""
    source_files = []
    seen_bytes: dict[int, str] = {}
    candidates: dict[tuple[int, int], dict] = {}
    total_window_records = 0
    total_decoded_rows = 0
    for name in names:
        file = directory / name
        raw = file.read_bytes()  # intentionally propagates errors
        obj = json.loads(raw)
        _verify_artifact(obj, name)
        source_files.append({
            "path": f"tools/agents/pathfinding/{name}",
            "rawSha256": sha(raw),
            "regions": len(obj.get("functions", [])),
            "sourceSha256": obj["sha256"],
            "coverage": "bounded saved artifact; not exhaustive code",
        })
        for fun in obj.get("functions", []):
            instructions = fun.get("instructions", [])
            if not isinstance(instructions, list):
                raise ValueError(f"Malformed instructions in {name}")
            total_window_records += 1
            total_decoded_rows += len(instructions)
            for ix, row in enumerate(instructions):
                rva_s = row.get("rva")
                bytes_s = row.get("bytes")
                asm = row.get("instruction")
                if not isinstance(rva_s, str) or not isinstance(bytes_s, str) or not isinstance(asm, str):
                    raise ValueError(f"Invalid decoded row in {name}")
                if not HEX.fullmatch(rva_s) or not HEX.fullmatch(bytes_s) or not bytes_s:
                    raise ValueError(f"Invalid instruction hex in {name}: {rva_s}")
                rva = int(rva_s, 16)
                normalized = bytes_s.lower()
                if rva in seen_bytes and seen_bytes[rva] != normalized:
                    raise ValueError(f"Conflicting historical bytes at {rva_s}")
                seen_bytes[rva] = normalized
                for match in classify_assembly(asm):
                    offset = int(match["offsetLabel"], 16)
                    key = (rva, offset)
                    if key in candidates:
                        old = candidates[key]
                        if (old["bytes"] != normalized or old["instruction"] != asm):
                            raise ValueError(f"Conflicting saved disassembly at {rva_s}")
                        if name not in old["sourceArtifacts"]:
                            old["sourceArtifacts"].append(name)
                        continue
                    candidates[key] = {
                        "rva": hex(rva), "bytes": normalized, "instruction": asm,
                        **match,
                        "sourceArtifacts": [name],
                        "window": {"beginRva": fun.get("beginRva"),
                                   "endRvaExclusive": fun.get("endRvaExclusive")},
                        "neighbors": _neighbors(instructions, ix),
                        "qualifiedSameQueueOwner": False,
                    }
    records = [candidates[k] for k in sorted(candidates)]
    for rec in records:
        rec["sourceArtifacts"].sort()
    counts = Counter(x["offsetLabel"] for x in records)
    classes = Counter(x["accessClass"] for x in records)
    # Do not elevate known disproofs into leads.
    rejected = {
        0x7a384: "This +0x210 store zeros a hkpWorld field (separately verified RTTI), not a qualified queue type-7 handler.",
        0x7af8d: "This +0x160 dword write is a hkpWorld state field, not the simulation queue pointer.",
        0x89bd7: "Constructor zeroing of the simulation +0x160 field, not a non-null queue writer.",
    }
    options = [r for r in records if
               r["accessClass"] in ("write", "read-modify-write", "read", "ambiguous")
               and r["offsetLabel"] in ("0x160", "0x210")
               and int(r["rva"], 16) not in rejected]
    options.sort(key=lambda r: (
        0 if r["offsetLabel"] == "0x210" and r["accessClass"] == "write" else
        1 if r["offsetLabel"] == "0x160" and r["accessClass"] == "write" else
        2 if r["offsetLabel"] == "0x210" else 3,
        int(r["rva"], 16)))
    next_anchors = [{
        "rva": r["rva"], "offset": r["offsetLabel"],
        "accessClass": r["accessClass"],
        "hypothesisToTest": "Trace the receiver's same-object identity to the Havok job queue and establish any actual type-7 handler/producers.",
        "disproof": "A different receiver, stack/local state, read-only use, zero initialization, or subtype-only match rejects a pathfinding registration claim.",
    } for r in options[:8]]
    return {
        "schemaVersion": 1,
        "taskId": "M3-001",
        "scope": "saved offline native disassembly windows only",
        "buildSha256": BUILD_SHA,
        "sourceFiles": source_files,
        "sourceFileCount": len(source_files),
        "recordedRegionCount": total_window_records,
        "totalRecordedInstructionRowsIncludingOverlap": total_decoded_rows,
        "uniqueDecodedInstructionRvas": len(seen_bytes),
        "uniqueCandidateCount": len(records),
        "byOffset": dict(sorted(counts.items())),
        "byAccessClass": dict(sorted(classes.items())),
        "candidateRecords": records,
        "rejectedProvenanceRvas": {hex(k): v for k, v in rejected.items()},
        "topNextAnchors": next_anchors,
        "type7Proven": False,
        "nonzeroSimulationQueuePointerWriterProven": False,
        "limitations": [
            "Covers only eleven archived source files, not all native methods, indirect calls or runtime state.",
            "Instruction-access classes are conservative Intel-syntax heuristics, not register/data-flow proofs.",
            "A matching displacement cannot establish a queue identity or typed handler registration.",
            "Immediate-zero stores are directly recognized; registers containing zero require separate reaching-definition evidence.",
            "Subtype 7 in a type-3 job is not a type-7 job.",
            "Negative results here do not establish native type-7 pathfinding is absent.",
        ],
        "gameInputSent": False, "gameProcessAttached": False,
        "targetExecuted": False,
    }


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--summary", action="store_true", help="Compact report excluding full local contexts")
    args = p.parse_args(argv)
    try:
        result = collect()
    except (OSError, TypeError, ValueError, KeyError, json.JSONDecodeError) as error:
        print(json.dumps({"ok": False, "error": str(error), "type7Proven": False}), file=sys.stderr)
        return 2
    if args.summary:
        result["candidateRecords"] = [
            {k: row[k] for k in ("rva", "offsetLabel", "accessClass",
                                 "nullOrZeroWrite", "instruction", "sourceArtifacts")}
            for row in result["candidateRecords"][:20]]
        result["summaryTruncatedToFirst20Candidates"] = result["uniqueCandidateCount"] > 20
    print(json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
