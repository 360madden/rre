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
)
ANCHORS = (
    (0x6A64EC, "e82f688d00"), (0x6A64F1, "84c0"),
    (0xF7CDFE, "e8ddd14600"), (0xF7CE03, "4c396360"),
    (0xF7CE07, "0f8416010000"), (0xF7CE74, "4885ed"),
    (0xF7CE77, "744c"), (0xF7CE82, "80782801"),
    (0xF7CE86, "753d"), (0xF7CE92, "4c896500"),
    (0xF7CEB1, "8139ffff0000"), (0xF7CEC5, "b001"),
    (0xF7CF10, "48894500"), (0xF7CF14, "b001"),
    (0xF7CF23, "32c0"),
)
CALLS = ((0x6A64EC, 0xF7CD20), (0xF7CDFE, 0x13E9FE0),
         (0x78B8E, 0x8E744), (0x78BD0, 0x9FD68))


def digest(blob):
    return hashlib.sha256(blob).hexdigest()


def check(ok, message):
    if not ok:
        raise ValueError(message)


def verify(blob):
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
    for rva, expected in ANCHORS:
        check(region(rva, len(expected)//2).hex() == expected, "opcode mismatch")
    for rva, target in CALLS:
        raw = region(rva, 5)
        check(raw[0] == 0xe8 and
              rva + 5 + int.from_bytes(raw[1:], "little", signed=True) == target,
              "call edge mismatch")
    # Negative controls modify ONLY transient in-memory copies.
    modified = bytearray(blob)
    modified[0x40] ^= 1
    check(digest(modified) != SHA, "wrong-build negative control failed")
    sample = bytearray(region(0xF7CD20, 0x227))
    sample[0xF7CE74-0xF7CD20] ^= 1
    check(digest(sample) != REGIONS[1][4], "window negative control failed")
    return {"task": "WA-006", "status": "static-source-qualified",
            "executableSha256": SHA, "verifiedWindows": len(REGIONS),
            "verifiedInstructions": sum(x[3] for x in REGIONS),
            "anchors": len(ANCHORS), "callEdges": len(CALLS),
            "inMemoryNegativeControlsPassed": 2,
            "resultRecordOffset": "0x60",
            "successWithoutOwnerWrite": "0xF7CE77 -> 0xF7CEC5 (AL=1)",
            "wrongTypeWithoutOwnerWrite": "0xF7CE86 -> 0xF7CEC5 (AL=1)",
            "nextCallees": ["0x8E744", "0x9FD68"],
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
