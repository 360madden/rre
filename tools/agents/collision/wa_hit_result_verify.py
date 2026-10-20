#!/usr/bin/env python3
"""WA-003 original-file verification; no RIFT process access or native calls.

The V7 run accounts for five anchors but only two have PE unwind entries.
Three direct-call-qualified supplemental entry windows are bounded to 96 bytes;
reading to the first RET does not assert complete source-function boundaries.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import struct
import sys

ROOT = Path(__file__).resolve().parents[3]
EXE = Path(r"C:\Program Files (x86)\Glyph\Games\RIFT\Live\rift_x64.exe")
BUILD = "7c356c9dde9e12fcbff3c08d953b0630b48b1510a0ffb36e4ec164606e7b17bd"
BASE = 0x140000000
ARTIFACT = "artifacts/wa-hit-result-20261020-01.json"
MANIFEST = "artifacts/wa-hit-result-20261020-01-manifest.json"
ART_SHA = "388ce76ffb959dc5da0f9b4f938edaf1502baf58e0e951b9238d6dbc875f877d"
MAN_SHA = "0b77c1dd0b24df35507ba888ab30857a6b163a588318e3d6d7361506ad1a733b"
PINS = {
    0xf671e4: "488bac2460010000", 0xf6722c: "4533e4",
    0xf67242: "480f45df", 0xf67254: "488d054d36e001",
    0xf6729e: "e82dd24600", 0xf672a3: "4c396360",
    0xf672db: "4c8d4310", 0xf672ec: "e88fbe4600",
    0xf67314: "4885ed", 0xf67319: "488b4360",
    0xf67322: "80782801", 0xf67328: "480fbe4820",
    0xf6732d: "4803c8", 0xf67332: "4c896500",
    0xf67336: "486381b8000000", 0xf67341: "4c8b89b0000000",
    0xf67351: "8139ffff0000", 0xf6735c: "4883c110",
    0xf67393: "498b44c108", 0xf67398: "488b4808",
    0xf673a1: "488b4908", 0xf673a8: "488d41f8",
    0xf673ac: "490f44c4", 0xf673b0: "48894500",
    0xf673bb: "48894500", 0xf673c3: "32c0",
    0x13d44d6: "488b4908", 0x13d44dd: "e83a46cafe",
}
LEAF_PREFIXES = {
    0x13d3180: "0f104210488bc10f5c02f3410f1050100fc6d2000f59d00f58120f1111c3",
    0x13d2ba0: "0f100a488bc10f28c1f30f11090fc6c1550fc6c9aaf30f114908f30f114104c3",
    0x13d2bd0: "f30f105208488bc1f20f101a0f16da0f1119c3",
}


def check(value, message):
    if not value:
        raise ValueError(message)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def verify(binary=EXE, root=ROOT):
    import pefile
    import capstone
    raw = Path(binary).read_bytes()
    check(sha(raw) == BUILD, "Original executable SHA mismatch")
    a_bytes = (root / ARTIFACT).read_bytes(); m_bytes = (root / MANIFEST).read_bytes()
    check(sha(a_bytes) == ART_SHA and sha(m_bytes) == MAN_SHA, "Immutable V7 receipt changed")
    art = json.loads(a_bytes); man = json.loads(m_bytes)
    check(art["sha256"] == BUILD and man["source"]["sha256"] == BUILD, "Receipt source mismatch")
    check(man["status"] == "completed" and man["invocation"]["exitCode"] == 0, "V7 run failed")
    check(man["artifact"]["sha256"] == ART_SHA, "Artifact/manifest hash disagreement")
    check(len(art["functions"]) == 2 and len(art["unresolvedAnchors"]) == 3, "Coverage changed")
    check(man["coverage"]["boundedCaptureComplete"] and art["queueRemaining"] == 0, "Incomplete recording")
    pe = pefile.PE(data=raw, fast_load=True)
    try:
        check(pe.FILE_HEADER.Machine == 0x8664 and pe.OPTIONAL_HEADER.ImageBase == BASE, "Wrong PE target")
        decoder = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_64)
        native_rows = {}; regions = []; targets = set()
        for region in art["functions"]:
            first = int(region["beginRva"], 16); last = int(region["endRvaExclusive"], 16)
            blob = pe.get_data(first, last-first)
            check(sha(blob) == region["windowSha256"], "Native window changed")
            decoded = list(decoder.disasm(blob, BASE+first))
            check(decoded and decoded[-1].address+decoded[-1].size == BASE+last, "Window decode incomplete")
            expected = region["instructions"]
            check(len(decoded) == len(expected), "Instruction row count differs")
            for ins, saved in zip(decoded, expected):
                check(ins.address-BASE == int(saved["rva"],16) and ins.bytes.hex() == saved["bytes"], "Instruction mismatch")
                native_rows[ins.address-BASE] = saved
            targets.update(int(c["targetRva"],16) for c in region["directAndIndirectCalls"] if c["kind"] == "direct")
            regions.append({"begin":hex(first),"endExclusive":hex(last),"rows":len(decoded)})
        for rva, expected in PINS.items():
            check(rva in native_rows and native_rows[rva]["bytes"] == expected, "Data-flow pin changed: "+hex(rva))
        leaves = []
        for rva, expected in LEAF_PREFIXES.items():
            check(rva in targets, "Supplemental window lacks qualified direct-call entry")
            blob = pe.get_data(rva,96)
            check(blob.startswith(bytes.fromhex(expected)), "Supplemental entry bytes changed")
            rows = []
            for ins in decoder.disasm(blob,BASE+rva):
                rows.append({"rva":hex(ins.address-BASE),"bytes":ins.bytes.hex(),"instruction":ins.mnemonic+" "+ins.op_str})
                if ins.mnemonic in ("ret","jmp"):
                    break
            check(rows and rows[-1]["instruction"].strip() == "ret", "No bounded straight-line return")
            leaves.append({"entryRva":hex(rva),"fixedWindowBytes":96,"fixedWindowSha256":sha(blob),
                           "fullFunctionBoundaryQualified":False,"rows":rows})
        vft = 0x2d6a8a8
        col = struct.unpack("<Q", pe.get_data(vft-8,8))[0]-BASE
        check(col == 0x2d800d8, "Unexpected collector RTTI locator")
        locator = struct.unpack("<6I", pe.get_data(col,24))
        check(locator[0] == 1 and locator[5] == col, "Invalid self-relative RTTI locator")
        name = pe.get_data(locator[3]+16,180).split(b"\0",1)[0].decode("ascii")
        check(name == ".?AVhkpClosestRayHitCollector@@", "Unexpected collector class")
        return {"schemaVersion":1,"taskId":"WA-003","status":"verified-static-evidence",
                "buildSha256":BUILD,"artifactSha256":ART_SHA,"manifestSha256":MAN_SHA,
                "verifierSourceSha256":sha(Path(__file__).read_bytes()),
                "capturedUnwindRegions":regions,"unresolvedPeUnwindAnchors":art["unresolvedAnchors"],
                "supplementalBoundedEntries":leaves,
                "collector":{"vftRva":hex(vft),"locatorRva":hex(col),"typeDescriptorRva":hex(locator[3]),"rttiName":name},
                "dataFlowPins":{hex(rva):native_rows[rva] for rva in PINS},
                "findings":[
                    "Stack collector installs RTTI-linked hkpClosestRayHitCollector VFT; an optional caller collector can replace it.",
                    "13D3180 computes start + (end-start)*scalar. In this caller the scalar is collector+0x20; this is specific to this ray path, not all collision collectors.",
                    "Bounded pack/unpack entries preserve the first three float lanes without a visible axis swap or scale in these entries; real world units/calibration remain unknown.",
                    "Optional RBP output traverses hit-associated pointer+0x60, type-byte guard, signed-relative adjustment, 16-byte keyed records (0xFFFF), two pointer dereferences and -8 adjustment.",
                    "Several successful early exits occur before clearing the optional output; AL=1 does not guarantee a fresh nonnull pointer result."
                ],
                "entityIdentityQualified":False,"worldFrameQualified":False,"callableInterfaceQualified":False,
                "limitations":["Final backlink class and logical entity ID are unresolved; pointer is not a persistent object identity.",
                               "Three supplemental entries lack PE unwind boundaries; capped direct-entry disassembly is not exhaustive function/CFG proof.",
                               "The 825 existing pefile warnings remain in the V7 manifest; recording completion is not complete helper disassembly.",
                               "No runtime hit, live scene, collision layer, normal convention, player clearance or route was observed."],
                "offlineOnly":True,"gameInputSent":False,"gameProcessAttached":False,"nativeFunctionsCalled":False}
    finally:
        pe.close()


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument("--output",type=Path)
    args=parser.parse_args()
    try:
        result=verify()
        encoded=json.dumps(result,indent=2,sort_keys=True)+"\n"
        if args.output:
            with args.output.open("x",encoding="utf-8",newline="\n") as stream: stream.write(encoded)
        print(encoded)
        return 0
    except (OSError,ValueError,KeyError,TypeError) as exc:
        print(json.dumps({"status":"failed","error":str(exc)}),file=sys.stderr);return 1


if __name__=="__main__": raise SystemExit(main())
