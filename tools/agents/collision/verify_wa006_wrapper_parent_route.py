#!/usr/bin/env python3
"""WA-006 wrapper -> parent-query source verifier; offline PE only.

Does not establish a nonzero wrapper+8 writer, shared live parent,
WorldManager virtual dispatch, collision hit or gameplay owner.
"""
import hashlib
import json
import struct
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
PE = ROOT / "artifacts/lab2-live-20261107-0922/guest-rift_x64.exe"
SHA = "1935a05c9db6d468e34e0055014a4a99c1b5afceb1695884e24600f5c20a4be8"
# RVA, length, original-byte SHA256
WINDOWS = {
    "callback": (0x6A62B1, 637, "e820bb56a8d8b4ed6f21d61314d40ce003e01ec4a17e3c5d795da0f2a1e1fa09"),
    "query": (0x78B1C, 261, "3d24fd605664f325b6e1006b6ec75a82efa426e0e13bd746e81974077024c088"),
    "wrapper_ctor": (0xF7CC50, 160, "629270dc7a659a90a8aeaa98a1d0e90e539e36e8e27e7fedee7148348ee083d0"),
    "wrapper": (0xF7CD20, 551, "ae78a6ae1c6bed37d01a2173c43a265a91c0d8c3c0bc28fd6f585e65c8d33564"),
    "base_ctor": (0x13E9A60, 154, "7b34a14cc98573af4d0382f5486178081cf70c2990d5bcab1b72134e0bcabeaf"),
    "helper": (0x13E9FE0, 32, "290c957c8f9d99db42d880dd69f6d5cb3750f1ba6a5b01d385ef0d3486cace21"),
}
# Original instruction anchors (RVA -> exact bytes); no disassembler dependency.
ANCHORS = {
    0x6A6484: "b9 68 00 00 00",  # allocate wrapper (0x68)
    0x6A649B: "48 8b f8",        # save constructor result RAX in RDI
    0x6A64BC: "48 8b cf",        # callback passes RDI in RCX
    0xF7CD57: "48 8b f1",        # preserve input wrapper in RSI
    0xF7CD9C: "48 8b ce",        # restore RCX=RSI
    0x13E9A6A: "33 ff",          # zero EDI
    0x13E9A7B: "48 89 79 08",  # [wrapper+8]=zero
    0x13E9FE6: "48 8b 49 08",  # RCX=[wrapper+8]
    0x78B2E: "48 8b d9",        # save parent query receiver RCX in RBX
    0x78B6E: "48 8b 8b 88 00 00 00",  # RCX=[parent+0x88]
    0x78B77: "48 3b ca",        # parent pointer compared with zero
    0x78B7A: "74 19",           # null parent goes to descriptor fallback
    0x78B7C: "38 51 30",        # [WorldManager+0x30] state guard
    0x78B7F: "75 14",           # nonzero state goes to descriptor fallback
    0x78B93: "eb 40",           # WorldManager call skips fallback to common join
    0x78B95: "4c 8b 8b c8 00 00 00",  # fallback input from parent+0xC8
    0x78BBC: "48 8b 93 80 00 00 00", # fallback receiver from parent+0x80
}
CALLS = {
    0x6A6489: 0x78E110, 0x6A6496: 0xF7CC50, 0x6A64EC: 0xF7CD20,
    0xF7CC59: 0x13E9A60, 0xF7CDFE: 0x13E9FE0,
    0x13E9FED: 0x78B1C, 0x78B8E: 0x8E744, 0x78BD0: 0x9FD68,
}
BRANCHES = {
    0x78B7A: (0x74, 0x78B95),  # null-parent JE
    0x78B7F: (0x75, 0x78B95),  # nonzero-state JNE
    0x78B93: (0xEB, 0x78BD5),  # fast path skips descriptor fallback
}
MUTATIONS = (0x6A649B, 0x6A64BC, 0xF7CD57, 0xF7CD9C, 0x13E9A7E, 0x13E9FE9,
             0x78B2E, 0x78B71, 0x6A64ED, 0xF7CDFF, 0x13E9FEE,
             0x78B7A, 0x78B7B, 0x78B7F, 0x78B80, 0x78B93, 0x78B94,
             0x78BD1, 0x78B95, 0x78BBC)


def insist(value, message):
    if not value:
        raise ValueError(message)


def rva_bytes(windows, rva, length):
    for name, (start, size, _) in WINDOWS.items():
        if start <= rva and rva + length <= start + size:
            return windows[name][rva - start:rva - start + length]
    raise ValueError(f"outside source windows: {rva:#x}")


def semantic_check(windows):
    for rva, hx in ANCHORS.items():
        expect = bytes.fromhex(hx)
        insist(rva_bytes(windows, rva, len(expect)) == expect, f"bad anchor {rva:#x}")
    for site, expected in CALLS.items():
        insn = rva_bytes(windows, site, 5)
        insist(insn[0] == 0xE8 and site + 5 + struct.unpack_from("<i", insn, 1)[0] == expected,
               f"bad direct call {site:#x}")
    for site, (opcode, expected) in BRANCHES.items():
        insn = rva_bytes(windows, site, 2)
        insist(insn[0] == opcode and site + 2 + struct.unpack_from("<b", insn, 1)[0] == expected,
               f"bad conditional/fallback branch {site:#x}")


def read_windows(raw):
    insist(len(raw) == 60493640 and hashlib.sha256(raw).hexdigest() == SHA,
           "unexpected exact-build source")
    pe = struct.unpack_from("<I", raw, 0x3C)[0]
    insist(raw[pe:pe + 4] == bytes((80, 69, 0, 0)), "bad PE signature")
    insist(struct.unpack_from("<H", raw, pe + 4)[0] == 0x8664, "not x64")
    opt = pe + 24
    insist(struct.unpack_from("<H", raw, opt)[0] == 0x20B, "not PE32+")
    insist(struct.unpack_from("<Q", raw, opt + 24)[0] == 0x140000000, "image base changed")
    sections = []
    section_count = struct.unpack_from("<H", raw, pe + 6)[0]
    header_bytes = struct.unpack_from("<H", raw, pe + 20)[0]
    for i in range(section_count):
        sh = opt + header_bytes + i * 40
        _virtual_size, va, size, off = struct.unpack_from("<4I", raw, sh + 8)
        sections.append((va, size, off))
    found = {}
    for name, (rva, size, digest) in WINDOWS.items():
        locations = [off + rva - va for va, raw_size, off in sections
                     if va <= rva and rva + size <= va + raw_size]
        insist(len(locations) == 1, f"unmapped window: {name}")
        pos = locations[0]
        insist(pos + size <= len(raw), f"truncated window: {name}")
        window = raw[pos:pos + size]
        insist(hashlib.sha256(window).hexdigest() == digest, f"changed window: {name}")
        found[name] = window
    return found


def main():
    windows = read_windows(PE.read_bytes())
    semantic_check(windows)
    for rva in MUTATIONS:
        name = next((name for name, (start, size, _) in WINDOWS.items()
                     if start <= rva < start + size), None)
        insist(name is not None, f"unowned mutation: {rva:#x}")
        altered = dict(windows)
        bytes_copy = bytearray(windows[name])
        bytes_copy[rva - WINDOWS[name][0]] ^= 1
        altered[name] = bytes(bytes_copy)
        try:
            semantic_check(altered)
        except ValueError:
            continue
        raise ValueError(f"RAM-only mutation accepted: {rva:#x}")
    print(json.dumps({
        "task": "WA-006", "evidence": "static-wrapper-parent-route-only",
        "sourceSha256": SHA, "windows": len(WINDOWS),
        "opcodeAnchors": len(ANCHORS), "directCalls": len(CALLS),
        "checkedBranches": len(BRANCHES),
        "ramNegativeControls": len(MUTATIONS), "wa006Accepted": False,
        "unproven": ["nonzero wrapper+8 setter", "same runtime parent",
                     "WorldManager virtual dispatch", "physics/gameplay owner"]
    }, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
