#!/usr/bin/env python3
"""Find navigation-related string leads in an exact offline PE; no live access."""
import argparse
import bisect
import struct
import hashlib
import importlib
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.dont_write_bytecode = True
TERMS = [
    "pathfind", "navmesh", "navigationmesh", "waypoint", "walkable", "traversable",
    "clicktomove", "click to move", "click-to-move", "follow", "raycast",
    "linearcast", "characterproxy", "hkai", "collision", "groundheight"
]

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--binary", type=Path, required=True)
    p.add_argument("--helper", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    p.add_argument("--expected-sha256", required=True)
    p.add_argument("--expected-helper-sha256", required=True)
    p.add_argument("--reference-rva", action="append", default=[])
    a = p.parse_args()
    if a.output.exists():
        raise RuntimeError("Output exists; use a new evidence filename.")
    data = a.binary.read_bytes()
    digest = hashlib.sha256(data).hexdigest()
    helper_hash = hashlib.sha256(a.helper.read_bytes()).hexdigest()
    if digest != a.expected_sha256.lower() or helper_hash != a.expected_helper_sha256.lower():
        raise RuntimeError("Binary/helper hash mismatch.")
    sys.path.insert(0, str(a.helper.parent))
    helper = importlib.import_module(a.helper.stem)
    if Path(helper.__file__).resolve() != a.helper.resolve():
        raise RuntimeError("Unexpected helper import location.")
    import pefile
    pe = pefile.PE(data=data, fast_load=True)
    names = helper.scan_for_rtti(pe)
    name_matches = [
        {"decoratedName":e["name"], "rva":hex(e["rva"]), "section":e["section"]}
        for e in names if any(term in e["name"].lower() for term in TERMS)
    ]
    hits, counts, truncated = [], {term:0 for term in TERMS}, False
    scanned_sections = []
    for section in pe.sections:
        if section.Characteristics & 0x20000000:
            continue
        section_name = section.Name.rstrip(b"\0").decode("ascii", errors="replace")
        body = section.get_data()
        scanned_sections.append({"name":section_name, "bytes":len(body)})
        for encoding, pattern in [
            ("ascii", rb"[\x20-\x7e]{5,}"),
            ("utf-16-le", rb"(?:[\x20-\x7e]\x00){5,}")
        ]:
            for match in re.finditer(pattern, body):
                value = match.group().decode(encoding)
                terms = [term for term in TERMS if term in value.lower()]
                if not terms:
                    continue
                for term in terms:
                    counts[term] += 1
                if len(hits) < 500:
                    hits.append({
                        "rva":hex(int(section.VirtualAddress)+match.start()),
                        "fileOffset":hex(int(section.PointerToRawData)+match.start()),
                        "section":section_name, "encoding":encoding,
                        "terms":terms, "text":value[:512], "textTruncated":len(value)>512
                    })
                else:
                    truncated = True
    reference_targets = {int(value, 0) for value in a.reference_rva}
    references = []
    if reference_targets:
        import capstone
        from capstone.x86_const import X86_OP_MEM, X86_REG_RIP
        pe.parse_data_directories(directories=[
            pefile.DIRECTORY_ENTRY["IMAGE_DIRECTORY_ENTRY_EXCEPTION"]
        ])
        ranges = sorted((int(e.struct.BeginAddress), int(e.struct.EndAddress))
                        for e in getattr(pe, "DIRECTORY_ENTRY_EXCEPTION", []))
        starts = [r[0] for r in ranges]
        md = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_64)
        md.detail = True
        for section in pe.sections:
            body = section.get_data()
            base_rva = int(section.VirtualAddress)
            if section.Characteristics & 0x20000000:
                # Bounded candidate generator for common x64 LEA reg,[RIP+disp32].
                # Capstone verifies the operand and the PE unwind region's instruction boundary.
                for match in re.finditer(rb"[\x48-\x4f]\x8d[\x05\x0d\x15\x1d\x25\x2d\x35\x3d]", body):
                    offset = match.start()
                    if offset + 7 > len(body):
                        continue
                    site = base_rva + offset
                    target = site + 7 + struct.unpack_from("<i", body, offset+3)[0]
                    if target not in reference_targets:
                        continue
                    instructions = list(md.disasm(body[offset:offset+7],
                                                 int(pe.OPTIONAL_HEADER.ImageBase)+site, count=1))
                    if not instructions:
                        continue
                    insn = instructions[0]
                    valid_operand = any(
                        o.type == X86_OP_MEM and o.mem.base == X86_REG_RIP and
                        int(insn.address)+insn.size+int(o.mem.disp)-int(pe.OPTIONAL_HEADER.ImageBase) == target
                        for o in insn.operands
                    )
                    if not valid_operand:
                        continue
                    index = bisect.bisect_right(starts, site)-1
                    bounds = ranges[index] if index >= 0 and ranges[index][0] <= site < ranges[index][1] else None
                    boundary_verified = False
                    if bounds and site-bounds[0] < 65536:
                        prefix = pe.get_data(bounds[0], site-bounds[0]+7)
                        boundary_verified = any(
                            i.address == int(pe.OPTIONAL_HEADER.ImageBase)+site
                            for i in md.disasm(prefix, int(pe.OPTIONAL_HEADER.ImageBase)+bounds[0])
                        )
                    references.append({
                        "targetRva":hex(target), "siteRva":hex(site),
                        "kind":"RIP-relative LEA", "instruction":f"{insn.mnemonic} {insn.op_str}",
                        "bytes":bytes(insn.bytes).hex(),
                        "instructionBoundaryVerifiedFromPeRange":boundary_verified,
                        "containingPeRange":[hex(x) for x in bounds] if bounds else None
                    })
            else:
                for target in reference_targets:
                    needle = struct.pack("<Q", int(pe.OPTIONAL_HEADER.ImageBase)+target)
                    offset = body.find(needle)
                    while offset >= 0:
                        references.append({"targetRva":hex(target), "siteRva":hex(base_rva+offset),
                                           "kind":"stored absolute pointer", "section":section.Name.rstrip(b"\0").decode("ascii",errors="replace")})
                        offset = body.find(needle,offset+1)
    result = {
        "schemaVersion":1, "createdAtUtc":datetime.now(timezone.utc).isoformat(),
        "binary":str(a.binary), "sha256":digest, "imageBase":hex(pe.OPTIONAL_HEADER.ImageBase),
        "method":"Existing RiftReader RTTI-name matcher plus standard ASCII/UTF-16LE text search",
        "helper":str(a.helper), "helperSha256":helper_hash,
        "reaDecompilation":False, "gameProcessAttached":False, "gameInputSent":False,
        "queryTerms":TERMS, "scannedNonExecutableSections":scanned_sections,
        "referenceTargets":[hex(x) for x in sorted(reference_targets)], "references":references,
        "termCounts":counts, "stringMatches":hits, "matchesTruncated":truncated,
        "rttiNamePatternTotal":len(names), "rttiNameMatches":name_matches,
        "limitations":[
            "Names are static leads; no vtable, class layout, caller or actual usage is established.",
            "Existing RTTI matcher recognizes only a restricted MSVC class-name pattern.",
            "Text search covers printable ASCII and ASCII-range UTF-16LE in non-executable PE sections.",
            "Zero matches does not establish absence of a planner or collision implementation.",
            "Reference search covers common x64 RIP-relative LEA encodings and stored absolute pointers; it is not an exhaustive xref index."
        ]
    }
    a.output.parent.mkdir(parents=True, exist_ok=True)
    with a.output.open("x",encoding="utf-8",newline="\n") as out:
        json.dump(result,out,indent=2)
        out.write("\n")
    print(json.dumps({"output":str(a.output),"sha256":digest,"termCounts":counts,
        "matches":len(hits),"truncated":truncated,"references":references,"rttiNameMatches":name_matches}))
    pe.close()

if __name__ == "__main__":
    main()
