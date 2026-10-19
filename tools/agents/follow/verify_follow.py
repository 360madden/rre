"""Read-only follow-lane evidence verification; run with the existing RRE Python -B.

No game process or imported RiftReader code is executed. No files are written.
"""
from __future__ import annotations

import bisect
import hashlib
import json
import struct
from pathlib import Path

import capstone
import pefile


def main() -> None:
    root = Path(__file__).resolve().parents[3]
    result = json.loads((root / "docs/agents/follow.json").read_text(encoding="utf-8"))
    assert result["lane"] == "follow"
    build = result["build"]
    data = Path(build["binary"]).read_bytes()
    assert hashlib.sha256(data).hexdigest() == build["sha256"]
    assert hashlib.sha256(Path(build["helper"]).read_bytes()).hexdigest() == build["helperSha256"]
    for source in result["sources"]:
        assert hashlib.sha256(Path(source["path"]).read_bytes()).hexdigest() == source["sha256"]
    for source in result["nameReferenceEvidence"]:
        assert hashlib.sha256(Path(source["helper"]).read_bytes()).hexdigest() == source["helperSha256"]

    pe = pefile.PE(data=data, fast_load=True)
    base = int(pe.OPTIONAL_HEADER.ImageBase)
    assert base == int(build["imageBase"], 16) == 0x140000000
    assert pe.FILE_HEADER.Machine == 0x8664
    md = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_64)
    count = 0
    for excerpts in result["codeEvidence"].values():
        for row in excerpts:
            rva, raw = int(row["rva"], 16), bytes.fromhex(row["bytes"])
            assert pe.get_data(rva, len(raw)) == raw, row
            instructions = list(md.disasm(raw, base + rva))
            assert len(instructions) == 1 and instructions[0].size == len(raw), row
            insn = instructions[0]
            assert f"{insn.mnemonic} {insn.op_str}".strip() == row["instruction"], row
            count += 1
    for row in result["dataEvidence"] + result["stringEvidence"]:
        expected = bytes.fromhex(row["bytes"])
        assert pe.get_data(int(row["rva"], 16), len(expected)) == expected, row
    for row in result["freshFunctionRanges"]:
        start = int(row["beginRva"], 16)
        size = min(int(row["endRvaExclusive"], 16) - start, 16384)
        assert hashlib.sha256(pe.get_data(start, size)).hexdigest() == row["windowSha256"], row

    pe.parse_data_directories(directories=[pefile.DIRECTORY_ENTRY["IMAGE_DIRECTORY_ENTRY_EXCEPTION"]])
    ranges = sorted((int(e.struct.BeginAddress), int(e.struct.EndAddress)) for e in pe.DIRECTORY_ENTRY_EXCEPTION)
    starts = [r[0] for r in ranges]
    callers = result["directCallers"]
    assert len(callers) == result["directCallerCount"] == 16
    assert len({c["siteRva"] for c in callers}) == 16
    for caller in callers:
        site = int(caller["siteRva"], 16)
        bounds = ranges[bisect.bisect_right(starts, site) - 1]
        assert bounds[0] <= site < bounds[1]
        assert [hex(x) for x in bounds] == caller["containingPeRange"]
        prefix = pe.get_data(bounds[0], site - bounds[0] + 5)
        insn = next((i for i in md.disasm(prefix, base + bounds[0]) if i.address == base + site), None)
        assert insn is not None and insn.mnemonic == "call"
        assert insn.op_str == "0x140534200"
        assert caller["instructionBoundaryVerifiedFromPeRange"] is True

    # Independently derive numeric action mappings from retained table bytes.
    table = struct.unpack("<15I", pe.get_data(0x6968A8, 60))
    assert table[:6] == (0x695A58, 0x695A58, 0x695A68, 0x695A68, 0x695A68, 0x695A68)
    assert table[7:9] == (0x695B43, 0x695B21)  # IDs 9 and 10
    assert struct.unpack("<Q", pe.get_data(0x264EBB0, 8))[0] == base + 0x6ADA60
    assert struct.unpack("<Q", pe.get_data(0x264EBA8, 8))[0] == base + 0x6ADA70
    assert pe.get_data(0x534339, 7) == bytes.fromhex("488d1548201102")
    assert 0x534339 + 7 + struct.unpack("<i", pe.get_data(0x53433C, 4))[0] == 0x2646388
    assert result["scope"]["offlineOnly"] is True
    assert all(value is False for key, value in result["scope"].items() if key != "offlineOnly")
    pe.close()
    print(json.dumps({"result": "PASS", "instructionExcerpts": count,
                      "directCallerPrefixes": len(callers),
                      "freshRegionHashes": len(result["freshFunctionRanges"]),
                      "sourceHashes": len(result["sources"]), "liveActions": 0}))


if __name__ == "__main__":
    main()
