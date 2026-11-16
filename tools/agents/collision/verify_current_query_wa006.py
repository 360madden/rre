#!/usr/bin/env python3
"""WA-006 exact-build static spatial query check. Reads on-disk PE ONLY."""
import argparse
import hashlib
import json
from pathlib import Path

from capstone import Cs, CS_ARCH_X86, CS_MODE_64
import pefile

PE = Path(r"C:\Program Files (x86)\Glyph\Games\RIFT\Live\rift_x64.exe")
SHA = "1935a05c9db6d468e34e0055014a4a99c1b5afceb1695884e24600f5c20a4be8"
REGIONS = (
    ("callback", 0x6A62B1, 0x6A652E, 142, "e820bb56a8d8b4ed6f21d61314d40ce003e01ec4a17e3c5d795da0f2a1e1fa09"),
    ("query", 0xF7CD20, 0xF7CF47, 144, "ae78a6ae1c6bed37d01a2173c43a265a91c0d8c3c0bc28fd6f585e65c8d33564"),
    ("helper", 0x13E9FE0, 0x13EA007, 11, "03d9b554e958d1e590ec3e9ecc4f87df18d60ed3dd009a8b42e584197901ab12"),
    ("callee", 0x78B1C, 0x78C21, 63, "3d24fd605664f325b6e1006b6ec75a82efa426e0e13bd746e81974077024c088"),
    ("query-adapter", 0x8E744, 0x8E7ED, 35, "84493c16cc018b254698dd8a1d37406f6e7ee3150d1e407bc232cd5608014274"),
    ("geometry-candidate-producer", 0xD0944, 0xD1074, 443, "2f37be6b71b566885610faa92f6bf0c1a210dc821a4c459ce985cf39d2b566fe"),
    ("virtual-dispatch-adapter", 0x9FD68, 0x9FE88, 73, "1f044f797e13c5d773122a9e777038d5ff4bd3ebafaf2e621d55c4ee8f7c0372"),
    ("candidate-selector", 0xA2514, 0xA26D2, 119, "ea78e0b39823e7ae154144f11e0d31a9acb794f8acfbfb9a4087e83255bba973"),
    ("candidate-bool", 0xA24F4, 0xA2506, 6, "f71c676e712dcd3bedc4a1fac726fe81e28d5a504c5adce47c8db91e9ef17860"),
)
VTABLE_RVA = 0x278C980
VTABLE_SHA = "dea4f646f9944c1acf36b364687f96ff2e5476e2414c19197247067f08d9606f"
ANCHORS = (
    (0x6A64EC, "e82f688d00"), (0x6A64F1, "84c0"),
    (0xF7CDFE, "e8ddd14600"), (0xF7CE03, "4c396360"),
    (0xF7CE07, "0f8416010000"), (0xF7CE74, "4885ed"),
    (0xF7CE77, "744c"), (0xF7CE82, "80782801"),
    (0xF7CE86, "753d"), (0xF7CE92, "4c896500"),
    (0xF7CEB1, "8139ffff0000"), (0xF7CEC5, "b001"),
    (0xF7CF10, "48894500"), (0xF7CF14, "b001"),
    (0xF7CF23, "32c0"),
    (0x8E74B, "488d052ee26f02"), (0x8E75A, "4889442430"),
    (0xD0EA3, "ff5008"), (0xD101B, "ff5010"),
)
CALLS = ((0x6A64EC, 0xF7CD20), (0xF7CDFE, 0x13E9FE0),
         (0x78B8E, 0x8E744), (0x78BD0, 0x9FD68),
         (0x8E7E0, 0xD0944))


def digest(blob):
    return hashlib.sha256(blob).hexdigest()


def check(ok, message):
    if not ok:
        raise ValueError(message)


def verify(blob, *, run_negative_controls=True):
    check(len(blob) == 60493640, "wrong executable size")
    check(digest(blob) == SHA, "wrong executable SHA-256")
    pe = pefile.PE(data=blob, fast_load=True)
    check(pe.FILE_HEADER.Machine == 0x8664 and
          pe.OPTIONAL_HEADER.Magic == 0x20b and
          pe.OPTIONAL_HEADER.ImageBase == 0x140000000, "unexpected PE image")
    def region(rva, length):
        section = next((s for s in pe.sections if
                        s.VirtualAddress <= rva and
                        rva + length <= s.VirtualAddress + s.SizeOfRawData), None)
        check(section is not None, "RVA not on original raw section")
        data = pe.get_data(rva, length)
        check(len(data) == length, "RVA read clipped")
        return data
    cs = Cs(CS_ARCH_X86, CS_MODE_64)
    for name, begin, end, count, expected in REGIONS:
        data = region(begin, end - begin)
        check(digest(data) == expected, "window hash changed: " + name)
        ins = list(cs.disasm(data, begin))
        check(len(ins) == count and ins[0].address == begin and
              ins[-1].address + ins[-1].size == end, "instruction boundary: " + name)
    vtable = region(VTABLE_RVA, 64)
    check(digest(vtable) == VTABLE_SHA, "candidate vtable hash changed")
    for slot, callee in ((0x08, 0xA2514), (0x10, 0xA24F4)):
        check(int.from_bytes(vtable[slot:slot + 8], "little") ==
              pe.OPTIONAL_HEADER.ImageBase + callee, "candidate vtable target mismatch")
    for rva, expected in ANCHORS:
        check(region(rva, len(expected)//2).hex() == expected, "opcode mismatch")
    for rva, target in CALLS:
        raw = region(rva, 5)
        check(raw[0] == 0xe8 and
              rva + 5 + int.from_bytes(raw[1:], "little", signed=True) == target,
              "call edge mismatch")
    # Exercise the ACTUAL verifier with two in-memory corruptions. No file writes.
    # Recursive invocations disable their own controls, so both must fail at
    # the top-level exact-executable SHA guard before any assertion is promoted.
    if run_negative_controls:
        modified = bytearray(blob)
        for offset in (0x40, pe.get_offset_from_rva(0xF7CE74)):
            modified[offset] ^= 1
            try:
                verify(bytes(modified), run_negative_controls=False)
            except ValueError as exc:
                check(str(exc) == "wrong executable SHA-256",
                      "tampered-executable rejection reason changed")
            else:
                raise ValueError("corrupted source accepted by full verifier")
            modified[offset] ^= 1
    return {"task": "WA-006", "status": "static-source-qualified",
            "executableSha256": SHA, "verifiedWindows": len(REGIONS),
            "verifiedInstructions": sum(x[3] for x in REGIONS),
            "anchors": len(ANCHORS), "callEdges": len(CALLS),
            "inMemoryNegativeControlsPassed": 2 if run_negative_controls else 0,
            "resultRecordOffset": "0x60",
            "successWithoutOwnerWrite": "0xF7CE77 -> 0xF7CEC5 (AL=1)",
            "wrongTypeWithoutOwnerWrite": "0xF7CE86 -> 0xF7CEC5 (AL=1)",
            "queryChildCallees": ["0x8E744", "0x9FD68"],
            "geometryCandidateProducerRva": "0xD0944",
            "indirectVirtualDispatchRva": "0x9FE36",
            "candidateRecordStride": "0x20",
            "candidateSelectorVtableRva": "0x278C980",
            "candidateSelectorRva": "0xA2514",
            "candidateBooleanReaderRva": "0xA24F4",
            "candidateScratchFieldOffset": "0x50",
            "candidateToResultPlus0x60Qualified": False,
            "runtimeHitQualified": False, "ownerQualified": False,
            "gameplayIdQualified": False, "worldInstanceQualified": False}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pe", type=Path, default=PE)
    args = parser.parse_args()
    try:
        result = verify(args.pe.read_bytes())
        print(json.dumps(result, indent=2, sort_keys=True))
    except (OSError, ValueError, pefile.PEFormatError) as error:
        print(json.dumps({"task": "WA-006", "status": "failed-closed",
                          "error": str(error)}))
        raise SystemExit(1)
