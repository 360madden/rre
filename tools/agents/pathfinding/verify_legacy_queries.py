"""Verify and preserve five older exact-build pathfinding query files.

Historical artifacts are read-only inputs. No Rift process, debugger, REA import,
input injection or new pathfinding implementation is involved.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[3]
BUILD = Path(r"C:\Program Files (x86)\Glyph\Games\RIFT\Live\rift_x64.exe")
BUILD_SHA = "7c356c9dde9e12fcbff3c08d953b0630b48b1510a0ffb36e4ec164606e7b17bd"
HELPER = Path(r"C:\rift modding\RiftReader\scripts\postupdate_static_access_chain.py")
HELPER_SHA = "c62d729ea027c271c8b4113c927ab039ae760d6db20f479166e7769dd4891319"
QUERIES = [
    ("_query1.json", "162427544c57d903e709051e9c2053d84a4bd2aa8b4b6ccf5cd5f6957601ef5f"),
    ("_query2.json", "f7fa7b08e9c9f51211023542409a09e9b4075cab3e26019535245f26658bb62c"),
    ("_query3.json", "427f7ff028765bd64c0f7dd3bda9c7d09037df28d593a197d346e5dc6446b5fe"),
    ("_query4.json", "7ee0da27a9f516f662f558445f6a1a7f336ae4a9f8d7386e918b3970814984b2"),
    ("_query5.json", "010e10df8d9792432db83e0ba3407d7db4ef385e34bb7c44259a6e295876f5a8")
]


def digest(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def main() -> None:
    import capstone
    import pefile

    raw = BUILD.read_bytes()
    assert digest(raw) == BUILD_SHA
    assert digest(HELPER.read_bytes()) == HELPER_SHA

    pe = pefile.PE(data=raw, fast_load=True)
    try:
        assert pe.FILE_HEADER.Machine == 0x8664
        base = pe.OPTIONAL_HEADER.ImageBase
        assert base == 0x140000000
        pe.parse_data_directories(
            directories=[pefile.DIRECTORY_ENTRY["IMAGE_DIRECTORY_ENTRY_EXCEPTION"]])
        exception = {
            (int(e.struct.BeginAddress), int(e.struct.EndAddress))
            for e in pe.DIRECTORY_ENTRY_EXCEPTION
        }
        md = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_64)
        md.detail = True
        coverage = []
        seen_begin = {}
        total_captured_regions = 0
        all_rows = 0
        all_unresolved = []
        caller_total = caller_qualified = 0
        for filename, expected_hash in QUERIES:
            file = ROOT / "tools" / "agents" / "pathfinding" / filename
            content = file.read_bytes()
            assert digest(content) == expected_hash, filename
            obj = json.loads(content)
            assert obj["schemaVersion"] == 1 and obj["sha256"] == BUILD_SHA
            assert obj["helperSha256"] == HELPER_SHA
            assert obj["imageBase"] == hex(base)
            assert not any(obj.get(s) for s in ("reaDecompilation", "gameInputSent",
                                                "gameProcessAttached", "targetExecuted"))
            assert obj["queueRemaining"] == 0
            assert obj["runtimeFunctionRangeCount"] == len(exception)
            assert obj["dependencies"]["pefile"] == pefile.__version__
            assert obj["dependencies"]["capstone"] == capstone.__version__

            decoded_count = 0
            for f in obj["functions"]:
                start = int(f["beginRva"], 0)
                end = int(f["endRvaExclusive"], 0)
                assert (start, end) in exception
                if start in seen_begin:
                    assert seen_begin[start] == (end, f["windowSha256"]), "Conflicting repeated window"
                else:
                    seen_begin[start] = (end, f["windowSha256"])
                total_captured_regions += 1
                size = min(end - start, 16384)
                blob = pe.get_data(start, size)
                assert blob and digest(blob) == f["windowSha256"]
                assert not f["windowTruncated"] and f["instructionDecodingCoversWindow"]
                decoded = list(md.disasm(blob, base + start))
                assert decoded and decoded[-1].address + decoded[-1].size == base + len(blob) + start
                assert len(decoded) == len(f["instructions"])
                for actual, item in zip(decoded, f["instructions"]):
                    assert item["rva"] == hex(actual.address - base)
                    assert item["bytes"] == bytes(actual.bytes).hex()
                    assert item["instruction"] == f"{actual.mnemonic} {actual.op_str}".strip()
                    decoded_count += 1
            all_rows += decoded_count
            unresolved = [e["rva"] for e in obj["unresolvedAnchors"]]
            all_unresolved.extend(unresolved)

            for caller in obj["callerReferences"]:
                caller_total += 1
                site, target = int(caller["siteRva"], 0), int(caller["targetRva"], 0)
                insn = next(md.disasm(pe.get_data(site, 5), base + site, count=1), None)
                assert insn and insn.mnemonic == "call" and insn.operands[0].imm == base + target
                if caller["instructionBoundaryVerifiedFromPeRange"]:
                    low, high = (int(x, 0) for x in caller["containingPeRange"])
                    assert low <= site < high
                    prefix = pe.get_data(low, site - low + 5)
                    assert any(x.address == base + site for x in md.disasm(prefix, base + low))
                    caller_qualified += 1

            coverage.append({
                "path": "tools/agents/pathfinding/" + filename,
                "sha256": expected_hash, "bytes": len(content),
                "capturedRanges": len(obj["functions"]), "decodedRows": decoded_count,
                "unresolvedAnchors": unresolved,
                "callerCandidates": len(obj["callerReferences"]),
                "pending": obj["queueRemaining"],
                "truncationObserved": False
            })
        assert total_captured_regions == 30, "Expected 30 historical region records (with overlaps)"
        assert all_rows == 2739, "Unexpected historic row total"
        assert all_unresolved == ["0xf3f94", "0x74490"]
        assert caller_total == 5
        print(json.dumps({
            "status": "PASS", "taskId": "M3-001-historical-evidence-recovery",
            "originalBuildSha256": BUILD_SHA,
            "files": coverage, "totalRegionRecords": total_captured_regions,
            "totalDistinctRanges": len(seen_begin),
            "totalInstructionRows": all_rows,
            "unresolved": all_unresolved,
            "callerSites": caller_total, "boundaryQualifiedCallers": caller_qualified,
            "parserWarnings": len(pe.get_warnings()),
            "qualifications": [
                "Old query files preserve code bytes; no new native pathfinding function is established.",
                "Raw artifacts do not carry V7 full CLI/source inventory and cannot be retroactively promoted.",
                "PE unwind region coverage is not a complete reachable call graph.",
                "Type-7 handler population and player navigation usage remain unresolved."
            ]
        }))
    finally:
        pe.close()


if __name__ == "__main__":
    main()
