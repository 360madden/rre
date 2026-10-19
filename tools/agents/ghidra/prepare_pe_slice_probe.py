"""Create one disposable PE container for the validated 603-byte Rift code slice.

Uses the EXISTING synthetic_pe helper from the RRE test suite; this checks only
REA's small-PE analysis path, not the original game's call graph or pathfinding.
"""
import argparse
import hashlib
import importlib.util
import json
import re
import sys
from pathlib import Path

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[3]
SOURCE = Path(r"C:\Program Files (x86)\Glyph\Games\RIFT\Live\rift_x64.exe")
SOURCE_SHA = "7c356c9dde9e12fcbff3c08d953b0630b48b1510a0ffb36e4ec164606e7b17bd"
SLICE_SHA = "6f31c492e5028ed20758e711746dc3152406e6db9b0273336f2b5224d6636e8b"
BEGIN, END = 0xF3FA4, 0xF41FF
DEFAULT_RUN_ID = "20261018-01"


def sha(data):
    return hashlib.sha256(data).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-id", default=DEFAULT_RUN_ID,
                        help="New isolated YYYYMMDD-token output namespace; existing output is never replaced")
    args = parser.parse_args()
    if not re.fullmatch(r"[0-9]{8}-[a-zA-Z0-9_-]{1,32}", args.run_id):
        parser.error("--run-id must be YYYYMMDD-token using only alphanumeric, _ and -")
    out = ROOT / "artifacts" / ("navigation-pe-slice-probe-" + args.run_id)
    import pefile
    original = SOURCE.read_bytes()
    if sha(original) != SOURCE_SHA:
        raise RuntimeError("Original Rift executable changed")
    original_pe = pefile.PE(data=original, fast_load=True)
    fragment = original_pe.get_data(BEGIN, END-BEGIN)
    if len(fragment) != 603 or sha(fragment) != SLICE_SHA:
        raise RuntimeError("Native code slice mismatch")
    fixture_file = ROOT / "tools" / "agents" / "validation" / "test_wrappers.py"
    spec = importlib.util.spec_from_file_location("rre_existing_synthetic_pe", fixture_file)
    fixture = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(fixture)
    mini_pe = fixture.synthetic_pe(fragment, ranges=((0x1000,0x1000+603,0x3100),))
    checked = pefile.PE(data=mini_pe, fast_load=True)
    if checked.FILE_HEADER.Machine != 0x8664 or checked.OPTIONAL_HEADER.ImageBase != 0x140000000:
        raise RuntimeError("Synthetic PE header mismatch")
    if checked.get_data(0x1000,603) != fragment:
        raise RuntimeError("PE text bytes differ from qualified slice")
    if out.exists():
        raise RuntimeError("Output namespace already exists; no overwrite")
    (out / "session" / "requests").mkdir(parents=True)
    file = out / "dispatcher-synthetic-pe.exe"
    with file.open("xb") as handle:
        handle.write(mini_pe)
    profile = {
        "binary":str(file),"expectedSha256":sha(mini_pe),
        "expectedReaVersion":"6.5.0","reaHome":r"C:\work\tools\rea",
        "ghidraHome":r"C:\work\tools\ghidra_12.1.2_PUBLIC",
        "javaHome":r"C:\Program Files\Eclipse Adoptium\jdk-21.0.11.10-hotspot",
        "outputDirectory":str(out / "session"),
        "durationSeconds":145,"startupTimeoutMs":60000
    }
    (out/"session-profile.json").write_text(json.dumps(profile,indent=2)+"\n",encoding="utf-8")
    manifest = {
        "schemaVersion":1,"mode":"synthetic-pe-container",
        "disclaimer":"This is not the original Rift executable; imported addresses and cross-references have been relocated into a toy PE with incomplete code/data.",
        "originalBinary":str(SOURCE),"originalSha256":SOURCE_SHA,
        "originalRvaBegin":hex(BEGIN),"originalRvaEndExclusive":hex(END),
        "fragmentSha256":SLICE_SHA,"fragmentBytes":603,
        "fixtureBuilder":str(fixture_file),"fixtureBuilderSha256":sha(fixture_file.read_bytes()),
        "syntheticPePath":str(file),"syntheticPeSha256":sha(mini_pe),
        "entryPoint":"0x140001000","size":len(mini_pe),
        "gameInputSent":False,"gameProcessAttached":False,"targetExecuted":False
    }
    (out/"source-manifest.json").write_text(json.dumps(manifest,indent=2)+"\n",encoding="utf-8")
    for name, request in {
        "01-resolve.json":{"tool":"resolve_containing_procedure",
                           "arguments":{"address":"0x140001000"},"timeoutMs":75000},
        "99-finish.json":{"finish":True}
    }.items():
        with (out/"session"/"requests"/name).open("x",encoding="utf-8") as handle:
            json.dump(request,handle,indent=2)
            handle.write("\n")
    print(json.dumps({"output":str(out),"syntheticSha256":sha(mini_pe),
                      "fileBytes":len(mini_pe),"originalSliceSha256":SLICE_SHA}))
    original_pe.close()
    checked.close()


if __name__ == "__main__":
    main()
