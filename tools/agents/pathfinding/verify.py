"""Read-only validation of pathfinding report provenance and native excerpts."""
import hashlib
import json
import sys
from pathlib import Path

sys.dont_write_bytecode = True
import capstone
import pefile


def main():
    root = Path(__file__).resolve().parents[3]
    report = json.loads((root / "docs/agents/pathfinding.json").read_text(encoding="utf-8"))
    assert report["lane"] == "pathfinding"
    assert report["branch"] == "research/nav-pathfinding"
    raw = Path(report["build"]["binary"]).read_bytes()
    expected = "7c356c9dde9e12fcbff3c08d953b0630b48b1510a0ffb36e4ec164606e7b17bd"
    assert report["build"]["sha256"] == hashlib.sha256(raw).hexdigest() == expected
    assert len(raw) == report["build"]["bytes"]
    for source in report["sources"]:
        body = Path(source["path"]).read_bytes()
        assert len(body) == source["bytes"], source["path"]
        assert hashlib.sha256(body).hexdigest() == source["sha256"], source["path"]
    pe = pefile.PE(data=raw, fast_load=True)
    assert pe.FILE_HEADER.Machine == 0x8664
    base = pe.OPTIONAL_HEADER.ImageBase
    assert base == int(report["build"]["preferredImageBase"], 16) == 0x140000000
    md = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_64)
    seen = {}
    count = 0
    for window in report["nativeEvidence"]["windows"]:
        begin, end = (int(window[k], 16) for k in ("beginRva", "endRvaExclusive"))
        body = pe.get_data(begin, end - begin)
        assert hashlib.sha256(body).hexdigest() == window["windowSha256"]
        decoded = list(md.disasm(body, base + begin))
        assert decoded and decoded[-1].address + decoded[-1].size == base + end
        boundaries = {i.address - base: i for i in decoded}
        for row in window["excerpts"]:
            instruction = boundaries[int(row["rva"], 16)]
            assert bytes(instruction.bytes).hex() == row["bytes"], row
            assert f"{instruction.mnemonic} {instruction.op_str}".strip() == row["instruction"], row
            seen[row["rva"]] = row
            count += 1
    for finding in report["findings"]:
        assert all(rva in seen for rva in finding["rvas"]), finding["id"]
    for caller in report["callerReferences"]:
        assert caller["instructionBoundaryVerifiedFromPeRange"]
        begin, end = (int(x, 16) for x in caller["containingPeRange"])
        site = int(caller["siteRva"], 16)
        decoded = {i.address - base: i for i in md.disasm(pe.get_data(begin, site - begin + 5), base + begin)}
        instruction = decoded[site]
        assert instruction.mnemonic == "call"
        assert instruction.op_str == hex(base + int(caller["targetRva"], 16))
        assert site < end
    assert pe.get_data(0x2D51598, len(b"TtPathfinding\0")) == b"TtPathfinding\0"
    assert 0x130 + 7 * 0x20 == 0x210
    assert 0x130 + 3 * 0x20 == 0x190
    assert not any(report["population"][k] for k in (
        "type7HandlerEntriesObserved", "type7ProducerIdentified", "tableKnownNull",
        "tableKnownUnused", "playerConnectionEstablished",
    ))
    assert not report["validation"]["inGameSuccessClaimed"]
    print(json.dumps({"result": "PASS", "sourceHashes": len(report["sources"]),
                      "nativeWindows": len(report["nativeEvidence"]["windows"]),
                      "instructionExcerpts": count, "qualifiedCallSites": len(report["callerReferences"]),
                      "binarySha256": expected}))


if __name__ == "__main__":
    main()
