"""M1-002: bounded read-only pefile diagnosis; JSON stdout, no target execution.

Reuses the existing synthetic PE fixture. No installed sources are modified.
Directory-wide metadata census; at most 25 raw runtime-function regions.
"""
from collections import Counter, defaultdict
from datetime import datetime, timezone
import argparse
import hashlib
import inspect
import json
from pathlib import Path
import re
import struct
import sys

sys.dont_write_bytecode = True
import pefile
from test_wrappers import synthetic_pe

ROOT = Path(__file__).resolve().parents[3]
MAIN = Path(r"C:\work\rre")
BINARY = Path(r"C:\Program Files (x86)\Glyph\Games\RIFT\Live\rift_x64.exe")
EXPECTED = "7c356c9dde9e12fcbff3c08d953b0630b48b1510a0ffb36e4ec164606e7b17bd"
ORIGINAL_SET = pefile.UnwindInfo.set_chained_function_entry


def sha(data):
    return hashlib.sha256(data).hexdigest()


def parse(data):
    pe = pefile.PE(data=data, fast_load=True)
    pe.parse_data_directories(directories=[pefile.DIRECTORY_ENTRY["IMAGE_DIRECTORY_ENTRY_EXCEPTION"]])
    return pe


def guarded_set(ui, entry):
    """Experimental idempotent rebind only; conflicting entries still raise."""
    if ui.get_chained_function_entry() is entry:
        return
    return ORIGINAL_SET(ui, entry)


def synthetic_checks():
    ranges = ((0x1000, 0x1001, 0x3100), (0x1010, 0x1011, 0x3110),
              (0x1020, 0x1021, 0x3110))
    fixture = synthetic_pe(b"\xc3" * 0x21, ranges=ranges, chain=True)
    pe = parse(fixture)
    entries = pe.DIRECTORY_ENTRY_EXCEPTION
    assert len(pe.get_warnings()) == 1 and "Chained function entry cannot be changed" in pe.get_warnings()[0]
    assert entries[1].unwindinfo is entries[2].unwindinfo
    assert entries[1].unwindinfo.get_chained_function_entry() is entries[0]
    baseline_warning = pe.get_warnings()[0]
    pe.close()
    try:
        pefile.UnwindInfo.set_chained_function_entry = guarded_set
        pe = parse(fixture)
        assert pe.get_warnings() == []
        entries = pe.DIRECTORY_ENTRY_EXCEPTION
        assert entries[1].unwindinfo.get_chained_function_entry() is entries[0]
        try:
            guarded_set(entries[1].unwindinfo, entries[2])
        except pefile.PEFormatError as exc:
            assert "cannot be changed" in str(exc)
        else:
            raise AssertionError("Conflicting rebind was accepted")
        pe.close()
    finally:
        pefile.UnwindInfo.set_chained_function_entry = ORIGINAL_SET
    # Synthetic mutation only: a BeginAddress-only lookup ignores the full tail.
    bad = bytearray(fixture)
    locator = pefile.PE(data=fixture, fast_load=True)
    tail_offset = locator.get_offset_from_rva(0x3114)
    locator.close()
    struct.pack_into("<I", bad, tail_offset + 4, 0x1002)
    pe = parse(bytes(bad))
    assert pe.DIRECTORY_ENTRY_EXCEPTION[1].unwindinfo.get_chained_function_entry().struct.BeginAddress == 0x1000
    assert struct.unpack("<III", pe.get_data(0x3114, 12)) != ranges[0]
    pe.close()
    return {"checksPassed": 5, "fixtureSha256": sha(fixture),
            "sharedInfoWarning": baseline_warning, "guardedWarningCount": 0,
            "conflictingRebindRejected": True, "rawTripleMismatchDetected": True,
            "coverage": ["shared unwind object alias", "baseline duplicate warning",
                         "idempotent guard", "conflicting rebind rejection",
                         "BeginAddress-only resolution misses synthetic tail mismatch"]}


def audit():
    binary = BINARY.read_bytes()
    assert sha(binary) == EXPECTED, "Exact build mismatch"
    repeats = []
    counts = Counter()

    def observe_set(ui, entry):
        previous = ui.get_chained_function_entry()
        counts["attempts"] += 1
        if previous is not None:
            same = previous is entry
            counts["sameTargetRepeats" if same else "conflictingRepeats"] += 1
            repeats.append((ui.get_file_offset(), entry.struct.BeginAddress, same))
        return ORIGINAL_SET(ui, entry)

    try:
        pefile.UnwindInfo.set_chained_function_entry = observe_set
        pe = parse(binary)
    finally:
        pefile.UnwindInfo.set_chained_function_entry = ORIGINAL_SET
    assert pe.OPTIONAL_HEADER.ImageBase == 0x140000000 and pe.FILE_HEADER.Machine == 0x8664
    entries = pe.DIRECTORY_ENTRY_EXCEPTION
    by_begin = {e.struct.BeginAddress: e for e in entries}
    by_offset = {e.struct.get_file_offset(): e for e in entries}
    warnings = pe.get_warnings()
    pattern = re.compile(r"^Failed parsing FunctionEntry of UNWIND_INFO at ([0-9a-f]+): 'Chained function entry cannot be changed'$")
    assert len(warnings) == 825 and all(pattern.match(w) for w in warnings)
    assert len(entries) == 302344 and len(by_begin) == len(entries)
    assert counts["sameTargetRepeats"] == 825 and counts["conflictingRepeats"] == 0
    groups = defaultdict(list)
    for entry in entries:
        if entry.unwindinfo is not None and entry.unwindinfo.UNW_FLAG_CHAININFO:
            groups[entry.struct.UnwindData].append(entry)
    shared = {rva: group for rva, group in groups.items() if len(group) > 1}
    assert sum(len(group) - 1 for group in shared.values()) == 825
    for warning, (ui_offset, parent_begin, same) in zip(warnings, repeats):
        entry = by_offset[int(pattern.match(warning).group(1), 16)]
        group = shared[entry.struct.UnwindData]
        assert entry is not group[0] and entry.unwindinfo is group[0].unwindinfo
        assert ui_offset == entry.unwindinfo.get_file_offset()
        assert parent_begin == entry.unwindinfo.FunctionEntry and same

    inspected = {}

    def raw_entry(entry):
        begin = entry.struct.BeginAddress
        if begin in inspected:
            return inspected[begin]
        assert len(inspected) < 25, "Raw region inspection budget exhausted"
        offset = entry.struct.get_file_offset()
        triple = struct.unpack_from("<III", binary, offset)
        assert triple == (begin, entry.struct.EndAddress, entry.struct.UnwindData)
        ui = entry.unwindinfo
        assert ui is not None, "Low-bit indirect unwind unresolved"
        header = pe.get_data(triple[2], 4)
        assert len(header) == 4
        version, flags, count = header[0] & 7, header[0] >> 3, header[2]
        assert (version, flags, count) == (ui.Version, ui.Flags, ui.CountOfCodes)
        row = {"beginRva": hex(begin), "endRvaExclusive": hex(triple[1]),
               "runtimeEntryFileOffset": hex(offset), "runtimeEntryBytes": binary[offset:offset+12].hex(),
               "unwindInfoRva": hex(triple[2]), "headerBytes": header.hex(),
               "version": version, "flags": flags, "countOfCodes": count}
        inspected[begin] = row
        if flags & 4:
            tail = triple[2] + 4 + ((count + 1) & ~1) * 2
            raw = pe.get_data(tail, 12)
            assert len(raw) == 12
            parent_triple = struct.unpack("<III", raw)
            parent = by_begin.get(parent_triple[0])
            assert parent is not None
            assert parent_triple == (parent.struct.BeginAddress, parent.struct.EndAddress, parent.struct.UnwindData)
            assert parent_triple[0] == ui.FunctionEntry
            assert ui.get_chained_function_entry() is parent
            row.update(chainTailRva=hex(tail), chainTailBytes=raw.hex(),
                       parentTripleRva=[hex(v) for v in parent_triple], fullParentTripleMatches=True)
        return row

    samples = []
    for warning in warnings[:3]:
        entry = by_offset[int(pattern.match(warning).group(1), 16)]
        group = shared[entry.struct.UnwindData]
        row = raw_entry(entry)
        raw_entry(group[0])
        raw_entry(by_begin[int(row["parentTripleRva"][0], 16)])
        samples.append({"warning": warning, "beginRva": hex(entry.struct.BeginAddress),
                        "unwindInfoRva": hex(entry.struct.UnwindData),
                        "firstAliasBeginRva": hex(group[0].struct.BeginAddress),
                        "aliasCount": len(group), "sameUnwindObject": True})

    manifest = json.loads((ROOT / "docs/navigation-findings.json").read_bytes())
    artifact_checks = []
    baseline = None
    for expected in manifest["artifacts"]:
        path = MAIN / expected["path"]
        content = path.read_bytes()
        assert sha(content) == expected["sha256"] and len(content) == expected["bytes"]
        artifact_checks.append({"path": str(path), "sha256": sha(content), "bytes": len(content)})
        if path.name == "static-navigation-chains.json":
            baseline = json.loads(content)
    assert baseline is not None and len(baseline["functions"]) == 11
    saved_roots = []
    for function in baseline["functions"]:
        current, seen, path = int(function["beginRva"], 16), set(), []
        while True:
            assert current not in seen, "Chain cycle"
            seen.add(current)
            path.append(hex(current))
            row = raw_entry(by_begin[current])
            if not row["flags"] & 4:
                break
            current = int(row["parentTripleRva"][0], 16)
        assert hex(current) == function["unwindChainRootRva"]
        saved_roots.append({"beginRva": function["beginRva"], "rootRva": hex(current),
                            "rawTriplePath": path})
    sources = [Path(pefile.__file__), Path(__file__), Path(__file__).with_name("test_wrappers.py"),
               ROOT / "tools/inspect-navigation-static.py", ROOT / "tools/inspect-navigation-names.py",
               Path(r"C:\rift modding\RiftReader\scripts\postupdate_static_access_chain.py"),
               Path(r"C:\rift modding\RiftReader\scripts\anti-re\rtti_class_scanner.py")]
    assert sha(sources[-2].read_bytes()) == "c62d729ea027c271c8b4113c927ab039ae760d6db20f479166e7769dd4891319"
    assert sha(sources[-1].read_bytes()) == "3636e5ca9c39318c27a7c5fdbccfd01e3258ef079139a0d9df64f49961448331"
    result = {"taskId": "M1-002", "date": "2026-10-19", "createdAtUtc": datetime.now(timezone.utc).isoformat(),
              "binary": {"path": str(BINARY), "sha256": sha(binary), "bytes": len(binary),
                         "preferredImageBase": hex(pe.OPTIONAL_HEADER.ImageBase), "addressConvention": "RVA"},
              "pefileVersion": pefile.__version__, "pythonVersion": sys.version,
              "sourceHashes": [{"path": str(p), "sha256": sha(p.read_bytes())} for p in sources],
              "sourceLocations": {name: inspect.getsourcelines(obj)[1] for name, obj in
                                  [("set_chained_function_entry", ORIGINAL_SET),
                                   ("unpack_in_stages", pefile.UnwindInfo.unpack_in_stages),
                                   ("parse_exceptions_directory", pefile.PE.parse_exceptions_directory)]},
              "metadataCensus": {"runtimeEntries": len(entries), "warningCount": len(warnings),
                                 "allWarnings": warnings, "setterCalls": dict(counts),
                                 "chainEntryCount": sum(len(g) for g in groups.values()),
                                 "uniqueChainUnwindInfos": len(groups), "sharedChainUnwindInfos": len(shared),
                                 "sharedChainEntryCount": sum(len(g) for g in shared.values()),
                                 "lowBitIndirectEntries": sum(e.unwindinfo is None for e in entries)},
              "warningSamples": samples, "rawRegionBudget": 25, "rawRegionsInspected": len(inspected),
              "rawRegions": list(inspected.values()), "savedChainRoots": saved_roots,
              "savedArtifactHashesVerified": artifact_checks, "synthetic": synthetic_checks(),
              "scope": {"offlineOnly": True, "nativeInstructionDisassemblyRegions": 0,
                        "installedSourcesModified": False, "targetExecuted": False, "gameInput": False},
              "limitations": ["Directory-wide counts are metadata bookkeeping, not raw validation of every chain.",
                              "Only the listed raw regions and 11 saved roots received full-triple checks.",
                              "No complete CFG, runtime unwind validity, native call interface or gameplay success established."]}
    assert sha(BINARY.read_bytes()) == EXPECTED
    pe.close()
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--synthetic-only", action="store_true")
    args = parser.parse_args()
    print(json.dumps(synthetic_checks() if args.synthetic_only else audit(), indent=2))
