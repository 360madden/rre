"""Read-only provenance/byte audit of the six baseline artifacts; emits JSON.

Uses installed pefile/Capstone only, no wrapper rerun on the game and no REA.
"""
import hashlib
import importlib.metadata
import struct
import json
from pathlib import Path
import sys

sys.dont_write_bytecode = True
import capstone
from capstone.x86_const import X86_OP_IMM, X86_OP_MEM, X86_REG_RIP
import pefile

ROOT = Path(__file__).resolve().parents[3]
MAIN = Path(r"C:\work\rre")
BINARY = Path(r"C:\Program Files (x86)\Glyph\Games\RIFT\Live\rift_x64.exe")
EXPECTED = "7c356c9dde9e12fcbff3c08d953b0630b48b1510a0ffb36e4ec164606e7b17bd"


def sha(data):
    return hashlib.sha256(data).hexdigest()


def audit():
    data = BINARY.read_bytes()
    assert sha(data) == EXPECTED
    pe = pefile.PE(data=data, fast_load=True)
    pe.parse_data_directories(directories=[pefile.DIRECTORY_ENTRY["IMAGE_DIRECTORY_ENTRY_EXCEPTION"]])
    base = pe.OPTIONAL_HEADER.ImageBase
    assert base == 0x140000000 and pe.FILE_HEADER.Machine == 0x8664
    entries = {int(e.struct.BeginAddress): e for e in pe.DIRECTORY_ENTRY_EXCEPTION}
    decoder = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_64)
    decoder.detail = True
    manifest = json.loads((ROOT / "docs/navigation-findings.json").read_text())
    checks = []
    for expected in manifest["artifacts"]:
        path = MAIN / expected["path"]
        raw = path.read_bytes()
        assert sha(raw) == expected["sha256"], str(path)
        assert len(raw) == expected["bytes"]
        item = json.loads(raw)
        assert item["sha256"] == EXPECTED and int(item["imageBase"], 0) == base
        helper = Path(item["helper"])
        assert sha(helper.read_bytes()) == item["helperSha256"]
        summary = {"path": str(path), "sha256": sha(raw), "bytes": len(raw),
                   "helperHashVerified": True, "helper": str(helper), "helperSha256": item["helperSha256"]}
        if "functions" in item:
            instruction_count = call_count = rip_count = 0
            incomplete = []
            for f in item["functions"]:
                begin, end = int(f["beginRva"], 0), int(f["endRvaExclusive"], 0)
                assert entries[begin].struct.EndAddress == end
                window = pe.get_data(begin, min(end-begin, 16384))
                assert window and sha(window) == f["windowSha256"]
                decoded = list(decoder.disasm(window, base+begin))
                assert len(decoded) == len(f["instructions"])
                for insn, row in zip(decoded, f["instructions"]):
                    assert insn.address-base == int(row["rva"], 0)
                    assert bytes(insn.bytes).hex() == row["bytes"]
                    assert f"{insn.mnemonic} {insn.op_str}".strip() == row["instruction"]
                    instruction_count += 1
                assert int(f["decodedThroughRvaExclusive"], 0) == decoded[-1].address-base+decoded[-1].size
                if not f["instructionDecodingCoversWindow"]:
                    incomplete.append({"begin": hex(begin), "end": hex(end),
                                       "decodedEnd": f["decodedThroughRvaExclusive"]})
                actual_calls = []
                actual_rips = []
                for insn in decoded:
                    site = insn.address-base
                    if insn.mnemonic == "call" and insn.operands:
                        operand = insn.operands[0]
                        actual_calls.append((hex(site), hex(operand.imm-base) if operand.type == X86_OP_IMM else None))
                    for operand in insn.operands:
                        if operand.type == X86_OP_MEM and operand.mem.base == X86_REG_RIP:
                            actual_rips.append((hex(site), hex(site+insn.size+operand.mem.disp)))
                assert actual_calls == [(c["siteRva"], c.get("targetRva")) for c in f["directAndIndirectCalls"]]
                assert actual_rips == [(r["siteRva"], r["targetRva"]) for r in f["ripRelativeReferences"]]
                call_count += len(actual_calls)
                rip_count += len(actual_rips)
                root, seen = begin, set()
                while root is not None:
                    assert root not in seen
                    seen.add(root)
                    entry = entries.get(root)
                    if entry is None or entry.unwindinfo is None:
                        root = None
                    elif entry.unwindinfo.UNW_FLAG_CHAININFO:
                        ui = entry.unwindinfo
                        tail = entry.struct.UnwindData + 4 + ((ui.CountOfCodes + 1) & ~1) * 2
                        parent_begin, parent_end, parent_ui = struct.unpack("<III", pe.get_data(tail, 12))
                        assert parent_begin == int(ui.FunctionEntry)
                        if parent_begin in entries:
                            parent = entries[parent_begin].struct
                            assert (parent.BeginAddress, parent.EndAddress, parent.UnwindData) == (parent_begin, parent_end, parent_ui)
                        root = parent_begin
                    else:
                        break
                if "unwindChainRootRva" in f:
                    assert f["unwindChainRootRva"] == (hex(root) if root is not None else None)
            for ref in item.get("callerReferences", []):
                site, target = int(ref["siteRva"], 0), int(ref["targetRva"], 0)
                decoded = next(decoder.disasm(pe.get_data(site, 5), base+site, count=1))
                assert decoded.mnemonic == "call" and decoded.operands[0].imm-base == target
                if ref["instructionBoundaryVerifiedFromPeRange"]:
                    begin = int(ref["containingPeRange"][0], 0)
                    assert any(i.address-base == site for i in decoder.disasm(pe.get_data(begin, site-begin+5), base+begin))
            summary.update(regions=len(item["functions"]), chainRootsRecorded=all("unwindChainRootRva" in f for f in item["functions"]), instructions=instruction_count,
                           calls=call_count, ripReferences=rip_count,
                           callerCandidates=len(item.get("callerReferences", [])),
                           verifiedCallers=sum(r["instructionBoundaryVerifiedFromPeRange"] for r in item.get("callerReferences", [])),
                           callersByTarget={t: sum(r["targetRva"] == t for r in item.get("callerReferences", []))
                                            for t in sorted({r["targetRva"] for r in item.get("callerReferences", [])})},
                           emptyWindows=0, incompleteWindows=incomplete, queueRemaining=item["queueRemaining"],
                           unresolvedAnchors=item["unresolvedAnchors"])
        else:
            for hit in item["stringMatches"]:
                text = hit["text"].encode(hit["encoding"])
                rva = int(hit["rva"], 0)
                assert pe.get_data(rva, len(text)) == text
                assert pe.get_offset_from_rva(rva) == int(hit["fileOffset"], 0)
                assert not pe.get_section_by_rva(rva).Characteristics & 0x20000000
            for name in item["rttiNameMatches"]:
                raw_name = b"." + name["decoratedName"].encode("ascii")
                assert pe.get_data(int(name["rva"], 0), len(raw_name)) == raw_name
            for ref in item.get("references", []):
                site, target = int(ref["siteRva"], 0), int(ref["targetRva"], 0)
                if ref["kind"] == "stored absolute pointer":
                    assert int.from_bytes(pe.get_data(site, 8), "little") == base+target
                else:
                    insn = next(decoder.disasm(pe.get_data(site, 7), base+site, count=1))
                    assert bytes(insn.bytes).hex() == ref["bytes"]
                    assert insn.mnemonic == "lea"
                    assert any(o.type == X86_OP_MEM and o.mem.base == X86_REG_RIP
                               and site+insn.size+o.mem.disp == target for o in insn.operands)
                    if ref["instructionBoundaryVerifiedFromPeRange"]:
                        begin = int(ref["containingPeRange"][0], 0)
                        assert any(i.address-base == site for i in decoder.disasm(pe.get_data(begin, site-begin+7), base+begin))
            summary.update(strings=len(item["stringMatches"]), namePatterns=len(item["rttiNameMatches"]),
                           references=len(item.get("references", [])),
                           boundaryVerifiedReferences=sum(r.get("instructionBoundaryVerifiedFromPeRange", False) for r in item.get("references", [])),
                           unverifiedReferenceSites=[r["siteRva"] for r in item.get("references", []) if r.get("kind") == "RIP-relative LEA" and not r["instructionBoundaryVerifiedFromPeRange"]],
                           matchesTruncated=item["matchesTruncated"],
                           capstoneVersionRecorded="dependencies" in item)
        checks.append(summary)
    attempt = json.loads((ROOT / "docs/rea-import-attempt-2026-10-18.json").read_text())
    response = MAIN / attempt["diagnosticResponse"]
    assert sha(response.read_bytes()) == attempt["diagnosticResponseSha256"]
    folder = MAIN / "artifacts/navigation-20261018-01"
    identity = json.loads((folder / "identity.json").read_text())
    admission = json.loads((folder / "open-binary.json").read_text())["structuredContent"]["result"]
    snapshot = json.loads((folder / "analysis-snapshot.json").read_text())
    evidence = json.loads((folder / "evidence.json").read_text())
    assert admission["sha256"] == identity["sha256"] == snapshot["target"]["sha256"] == EXPECTED
    assert evidence["records"] == snapshot["evidence_bundle"]["records"] == []
    assert snapshot["entries"] == []
    close = json.loads((folder / "close-receipt.json").read_text())["structuredContent"]["result"]
    export = json.loads((folder / "export-receipt.json").read_text())["structuredContent"]["result"]
    assert close["bytes"] == len((folder / "analysis-snapshot.json").read_bytes())
    assert export["bytes"] == len((folder / "evidence.json").read_bytes())
    assert close["evidence_records"] == export["records"] == 0
    source_paths = [
        ROOT / "tools/inspect-navigation-static.py", ROOT / "tools/inspect-navigation-names.py",
        ROOT / "tools/rea-session.mjs", ROOT / "requirements-static.txt", ROOT / "tools/navigation-seeds.tsv",
        Path(r"C:\rift modding\RiftReader\scripts\workflow_common.py"),
        Path(r"C:\rift modding\RiftReader\scripts\postupdate_owner_root_rediscovery.py"),
    ]
    result = {
        "binary": {"path": str(BINARY), "sha256": EXPECTED, "bytes": len(data), "imageBase": hex(base)},
        "dependencies": {"pefile": pefile.__version__, "capstoneModuleVersion": capstone.__version__,
                         "capstoneDistributionVersion": importlib.metadata.version("capstone"),
                         "capstoneEngineVersion": list(capstone.cs_version())},
        "peParser": {"runtimeEntries": len(entries), "warningCount": len(pe.get_warnings()),
                     "firstWarnings": pe.get_warnings()[:3]},
        "artifacts": checks,
        "reaAttempt01": {"admissionAndSnapshotHashMatch": True, "records": 0,
                         "diagnosticSha256Verified": True, "closeExportByteCountsVerified": True,
                         "profileSeedHash": snapshot["binding"]["analysis_profile"]["parameters"]["analysis_seeds"]["sha256"]},
        "sourceHashes": [{"path": str(p), "sha256": sha(p.read_bytes())} for p in source_paths],
    }
    main_seed = (MAIN / "tools/navigation-seeds.tsv").read_bytes()
    worktree_seed = (ROOT / "tools/navigation-seeds.tsv").read_bytes()
    assert result["reaAttempt01"]["profileSeedHash"] == sha(main_seed)
    assert worktree_seed.replace(b"\r\n", b"\n") == main_seed
    result["reaAttempt01"]["seedLineEndings"] = {
        "mainBytes": len(main_seed), "worktreeBytes": len(worktree_seed),
        "mainSha256": sha(main_seed), "worktreeSha256": sha(worktree_seed),
        "normalizedBytesEqual": True,
    }
    result["currentWrapperCopies"] = []
    for name in ("inspect-navigation-static.py", "inspect-navigation-names.py", "rea-session.mjs"):
        a, b = (ROOT / "tools" / name).read_bytes(), (MAIN / "tools" / name).read_bytes()
        assert a.replace(b"\r\n", b"\n") == b.replace(b"\r\n", b"\n")
        result["currentWrapperCopies"].append({
            "name": name, "worktreeSha256": sha(a), "mainSha256": sha(b),
            "normalizedBytesEqual": True,
        })
    pe.close()
    return result


if __name__ == "__main__":
    print(json.dumps(audit(), indent=2))
