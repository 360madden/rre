"""Extract and disassemble the hash-qualified physical RIFT SC-306 function.

LEGION-only and offline: no game process, VMware, or REA/Ghidra import.
REA 6.8 Windows Ghidra P0 does NOT admit raw x86-64 binaries (2026-11-09).
Use the installed iced-x86 decoder and preserve a unique evidence artifact.
"""
import argparse
import hashlib
import json
import re
import socket
from pathlib import Path

import pefile
from iced_x86 import Decoder, Formatter, FormatterSyntax, Mnemonic

ROOT = Path(__file__).resolve().parents[1]
SOURCE = Path(r"C:\Program Files (x86)\Glyph\Games\RIFT\Live\rift_x64.exe")
SOURCE_SHA = "1935a05c9db6d468e34e0055014a4a99c1b5afceb1695884e24600f5c20a4be8"
RVA, SIZE, IMAGE_BASE = 0x129CAC4, 452, 0x140000000
SLICE_SHA = "1d3b762a399fc53592032c11238eb151d41684b37fde0951713db760382f56e8"


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-id", required=True, help="Unique YYYYMMDD-token identifier")
    parser.add_argument("--dry-run", action="store_true", help="Verify source and disassembly; write nothing")
    args = parser.parse_args()
    if not re.fullmatch(r"[0-9]{8}-[A-Za-z0-9_-]{1,32}", args.run_id):
        parser.error("--run-id must match YYYYMMDD-token")
    if socket.gethostname().upper() != "LEGION":
        raise RuntimeError("LEGION physical-only source extraction refused on another host")

    original = SOURCE.read_bytes()
    if sha256(original) != SOURCE_SHA:
        raise RuntimeError("Physical RIFT executable hash changed; extraction refused")
    pe = pefile.PE(data=original, fast_load=True)
    try:
        if pe.FILE_HEADER.Machine != 0x8664 or pe.OPTIONAL_HEADER.ImageBase != IMAGE_BASE:
            raise RuntimeError("Physical RIFT PE image identity mismatch")
        code = pe.get_data(RVA, SIZE)
    finally:
        pe.close()
    if len(code) != SIZE or sha256(code) != SLICE_SHA:
        raise RuntimeError("SC-306 source RVA bytes differ from qualified evidence")

    address = IMAGE_BASE + RVA
    instructions = list(Decoder(64, code, ip=address))
    if sum(ins.len for ins in instructions) != SIZE or any(ins.mnemonic == Mnemonic.INVALID for ins in instructions):
        raise RuntimeError("Incomplete or invalid x64 instruction coverage")
    formatter = Formatter(FormatterSyntax.NASM)
    listing = "\n".join(f"{ins.ip:016X}: {formatter.format(ins)}" for ins in instructions) + "\n"
    listing_bytes = listing.encode("utf-8")
    out = ROOT / "artifacts" / ("sc306-legion-offline-" + args.run_id)
    manifest = {
        "schemaVersion": 1, "host": "LEGION", "mode": "hash-gated-offline-iced-x86",
        "source": str(SOURCE), "sourceSha256": SOURCE_SHA,
        "rvaBegin": hex(RVA), "sourceImageBase": hex(IMAGE_BASE),
        "entryAddress": hex(address), "size": SIZE, "sliceSha256": SLICE_SHA,
        "instructions": len(instructions), "decodedBytes": sum(ins.len for ins in instructions),
        "listingSha256": sha256(listing_bytes),
        "providerNote": "REA 6.8 Windows Ghidra P0 rejects raw-binary x86_64; no import attempted.",
        "limits": [
            "Raw bytes do not provide PE imports, symbols, resource data, or calling convention evidence.",
            "Sequential decode can include non-executed bytes; references and game behavior remain unverified.",
            "Not evidence of an Ability Queue enum choice table or values 0/2.",
        ],
        "gameProcessAccess": False, "vmwareAccess": False, "gameInput": False,
    }
    if args.dry_run:
        print(json.dumps({"dryRun": True, "outputWouldBe": str(out), **manifest}))
        return

    out.mkdir(parents=True, exist_ok=False)
    with (out / "sc306-label-register-delegate.bin").open("xb") as handle:
        handle.write(code)
    with (out / "sc306-label-register-delegate.asm").open("x", encoding="utf-8", newline="\n") as handle:
        handle.write(listing)
    with (out / "source-manifest.json").open("x", encoding="utf-8", newline="\n") as handle:
        json.dump(manifest, handle, indent=2)
        handle.write("\n")
    print(json.dumps({"created": str(out), "sliceSha256": SLICE_SHA,
                      "listingSha256": manifest["listingSha256"], "instructions": len(instructions)}))


if __name__ == "__main__":
    main()
