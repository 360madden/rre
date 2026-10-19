r"""Verify retained M2-002 evidence against the exact file; no process access/writes.

Run with C:\work\rre\.venv\Scripts\python.exe -B. This validates bytes,
instruction boundaries, tables and the stated local ordering, not game behavior.
"""
from __future__ import annotations

import hashlib
import json
import struct
from pathlib import Path

import capstone
import pefile


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def main() -> None:
    root = Path(__file__).resolve().parents[3]
    report_bytes = (root / "docs/agents/follow.json").read_bytes()
    report = json.loads(report_bytes)
    result = report["followUps"][-1]
    assert result["taskId"] == "M2-002"
    previous = result["preservation"]
    prefix = report_bytes[:previous["jsonPrefixBytes"]]
    assert digest(prefix + b"}" + bytes.fromhex(previous["jsonSuffixHex"])) == previous["jsonSha256"]
    assert digest((root / "docs/agents/follow.md").read_bytes()[:previous["markdownBytes"]]) == previous["markdownSha256"]
    for source in result["sources"]:
        assert digest(Path(source["path"]).read_bytes()) == source["sha256"], source["path"]

    data = Path(report["build"]["binary"]).read_bytes()
    assert digest(data) == result["buildSha256"] == report["build"]["sha256"]
    pe = pefile.PE(data=data, fast_load=True)
    base = int(pe.OPTIONAL_HEADER.ImageBase)
    assert base == 0x140000000 and pe.FILE_HEADER.Machine == 0x8664
    pe.parse_data_directories(directories=[pefile.DIRECTORY_ENTRY["IMAGE_DIRECTORY_ENTRY_EXCEPTION"]])
    ranges = {(int(e.struct.BeginAddress), int(e.struct.EndAddress)) for e in pe.DIRECTORY_ENTRY_EXCEPTION}
    decoder = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_64)
    rows, starts, instruction_count = {}, set(), 0
    for artifact in result["artifacts"]:
        raw = (root / artifact["path"]).read_bytes()
        assert digest(raw) == artifact["sha256"]
        evidence = json.loads(raw)
        assert evidence["sha256"] == result["buildSha256"]
        assert evidence["queueRemaining"] == 0
        assert not any(evidence[k] for k in ("reaDecompilation", "gameInputSent", "gameProcessAttached", "targetExecuted"))
        for region in evidence["functions"]:
            start, end = int(region["beginRva"], 16), int(region["endRvaExclusive"], 16)
            assert start not in starts and (start, end) in ranges
            starts.add(start)
            window = pe.get_data(start, min(end - start, 16384))
            assert digest(window) == region["windowSha256"]
            decoded = list(decoder.disasm(window, base + start))
            assert len(decoded) == len(region["instructions"])
            for insn, row in zip(decoded, region["instructions"]):
                assert row == {"rva": hex(insn.address - base), "bytes": insn.bytes.hex(),
                               "instruction": f"{insn.mnemonic} {insn.op_str}".strip()}
                rows[insn.address - base] = row["instruction"]
                instruction_count += 1
    assert len(starts) == result["regionBudget"]["observedUniqueRegions"] == 25
    assert result["regionBudget"]["maximum"] == 25

    # These six table entries and instruction boundaries establish numeric IDs,
    # without assigning key names or treating table bytes as executable code.
    primary = struct.unpack("<15I", pe.get_data(0x6968A8, 60))
    secondary = struct.unpack("<6I", pe.get_data(0x6968E4, 24))
    assert primary[:6] == (0x695A58, 0x695A58, 0x695A68, 0x695A68, 0x695A68, 0x695A68)
    assert secondary == (0x695A8B, 0x695AAC, 0x695AE9, 0x695AF3, 0x695AD5, 0x695ADF)
    assert primary[7:9] == (0x695B43, 0x695B21)
    assert [r["inputBit"] for r in result["numericActionMap"]] == [4, 5, 3, 2, 6, 7]
    for index, bit in enumerate((4, 5, 3, 2, 6, 7)):
        assert any(rows[a] == f"bts eax, {bit}" for a in range(secondary[index], secondary[index] + 12) if a in rows)
    for sequence in result["orderedCallSites"]:
        sites = [int(x, 16) for x in sequence["sites"]]
        assert sites == sorted(sites)
        for site, target in zip(sites, sequence["targets"]):
            assert rows[site] == f"call {hex(base + int(target, 16))}"

    expected = {
        0x694315: "cmp byte ptr [rdx + 0x12c], 0",
        0x694322: "sete bl",
        0x694367: "movzx r9d, byte ptr [rsi + 0x12c]",
        0x695847: "movzx r12d, r9b",
        0x695A58: "test r12b, r12b",
        0x695A5B: "jne 0x140695a68",
        0x695A61: "mov byte ptr [rax + 0x39c], r15b",
        0x695A6C: "je 0x140695b08",
        0x6967E3: "mov byte ptr [rdi + 0x18], 1",
        0x696A17: "xor edx, edx",
        0x696A2D: "je 0x140696a48",
        0x697175: "jne 0x140697184",
        0x697184: "mov bl, 1",
        0x697199: "jne 0x140697634",
        0x697B05: "bts ecx, 4",
        0x697B09: "mov bpl, 1",
        0x697B15: "btr ecx, 4",
        0x697B19: "mov bpl, 1",
        0x7B22A8: "mov eax, dword ptr [rax + 0x14]",
        0x534A0E: "mov qword ptr [rbx + 0x70], rax",
        0x534A12: "mov qword ptr [rbx + 0x78], rax",
        0x534A29: "btr eax, 0",
        0x860585: "xor edx, edx",
        0x86057F: "cmp r9, qword ptr [rbx + 0x20]",
        0x8603F1: "call qword ptr [rax + 0x58]",
        0x8603F8: "mov byte ptr [rbx + 0x11], 0",
        0x86040E: "mov qword ptr [rdi + 0x338], rax",
        0x86046F: "mov qword ptr [rdi + 0x378], rcx",
    }
    for site, instruction in expected.items():
        assert rows[site] == instruction, hex(site)
    pe.close()
    print(json.dumps({"result": "PASS", "taskId": "M2-002", "uniqueRegions": len(starts),
                      "retainedDecodedRows": instruction_count, "semanticAnchors": len(expected),
                      "orderedSequences": len(result["orderedCallSites"]), "liveActions": 0,
                      "priorReportPreserved": True}))


if __name__ == "__main__":
    main()
