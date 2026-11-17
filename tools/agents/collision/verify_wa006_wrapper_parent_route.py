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
    "projection_a": (0x13EA010, 67, "795ed0774017d43101c5145c6466a60a0d1b6c8b0fdc13f26b73ac937a037b9c"),
    "projection_b": (0x13EA060, 67, "f61ff24636763b2d41a08acfaa395f9cd58b8abfaa0cf9dc93fa59dd66eaeaab"),
    "projection_helper": (0x13EA0B0, 527, "305ca293f882dc55390d552579b2b6ba7c003d5e3904994e7202ce6bfe5640cb"),
    "adapter_table": (0x2793F58, 160, "2dfc91e5709f35b7cca3ec7afa86a18b117f342286a2c620b091f5c1c4ff85a2"),
    "global_cleanup": (0x49CC60, 72, "c6ab4e5de7b5e91f3c1f29fb2a91268d77e0db388754f40ac4ec5ca915171d2b"),
    "global_init": (0x4A207C, 940, "426b0340c3960c12a2d20451adf0e24ee77cd02f0c61bf3dd78154d29bb67385"),
    "global_compare": (0x13E7E70, 68, "ca7400d01c3681b0d5cdef92cc7e6505f716ff56c972fd176bea3abe9351c912"),
    "manager_unlink": (0x787C8, 288, "94ddc4726d58bf3315f73b76653bb75b6c46e0dd658e27828fd47df685da0c1f"),
    "manager_link": (0x78D78, 282, "62b8d075618a4b20d33bd0844e7b231c1054364f023a3f157449b3f33284d9f0"),
    "global_guard": (0x60CE30, 20, "fbe884911f0fe0a4a869cdda2ccdc21b0c8488a456d7f97fe88aee109f819c57"),
    "global_guard_epilogue": (0x60CF13, 5, "3297a0e4175e5d032a2be5212c1a1980cd3df21251db492413a47fcb4b6187ac"),
    "global_publish": (0x60CEE5, 46, "6755d8bcdb5baf2404af68c1df88db27251f682d77a292177563ad5b42ac68bf"),
    "global_third_constructor": (0x731D16, 3073, "70d0bfa0443e5f4651f0bf7108f80a550d66ee81ef89b5ff60fafc0e0bda6ef9"),
    "global_collection_consumer": (0x13EA650, 85, "cac00f71819c315841e7262aeb4c10f6013495f9db9f47d99531636b58b5a508"),
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
    0x13E9A82: "48 8b d9",     # preserve actual wrapper RCX in RBX for adapters
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
    0x13E9AB2: "48 89 58 08", # first adapter stores wrapper backreference
    0x13E9AB6: "48 89 08", # first adapter vptr
    0x13E9AC3: "48 89 43 50", # wrapper keeps first adapter at +0x50
    0x13E9AD8: "48 89 58 08", # second adapter stores wrapper backreference
    0x13E9ADC: "48 89 08", # second adapter vptr
    0x13E9AE4: "48 89 43 58", # wrapper keeps second adapter at +0x58
    0x13EA025: "48 8b 49 08", # adapter A reads its wrapper pointer
    0x13EA075: "48 8b 49 08", # adapter B reads its wrapper pointer
    0x13EA0D0: "4c 8b f1",    # preserve wrapper helper RCX in R14
    0x13EA16E: "49 8b 4e 08", # shared helper consumes wrapper+0x08
    0x13EA1BA: "4c 8b 81 c0 00 00 00", # dereferences subobject +0xC0
    0x4A233D: "48 8b d3",          # global wrapper pointer -> helper RDX
    0x4A2340: "48 8d 4d c0",       # separate local manager context -> RCX
    0x13E7E7A: "48 8b 7a 08",     # READ (not write) wrapper+8
    0x7324B2: "48 8b cb",         # constructed wrapper RBX -> helper RCX
    0x13EA666: "48 8b f9",       # helper keeps wrapper RCX in RDI
    0x13EA67A: "ff 4f 60",       # decrement dword at wrapper+0x60
    0x13EA682: "48 8b 4f 08",   # READ wrapper+8, not an assignment
    0x60CE3B: "48 85 c0",       # test existing global pointer
    0x60CF13: "48 83 c4 28 c3", # return epilogue after global guard
}
CALLS = {
    0x6A6489: 0x78E110, 0x6A6496: 0xF7CC50, 0x6A64EC: 0xF7CD20,
    0xF7CC59: 0x13E9A60, 0xF7CDFE: 0x13E9FE0,
    0x13E9FED: 0x78B1C, 0x78B8E: 0x8E744, 0x78BD0: 0x9FD68,
    0x13EA037: 0x13EA0B0, 0x13EA087: 0x13EA0B0,
    0x13EA1C1: 0x7D3E4,
    0x4A231A: 0xF7CC50, 0x4A2344: 0x13E7E70,
    0x13E7E98: 0x787C8, 0x13E7EA4: 0x78D78,
    0x60CEE8: 0xF7CC50, 0x60CEFA: 0x3C320,
    0x73247F: 0x78E110, 0x73248C: 0xF7CC50,
    0x7324B5: 0x13EA650, 0x13EA686: 0x786CC,
}
# Selected RIP-relative loads/stores of the wrapper-publication global.
# This is NOT a whole-PE exhaustive cross-reference census.
# (site RVA, opcode prefix, instruction length); target is recomputed.
GLOBAL_RIP_REFS = (
    (0x49CC76, "48 8b 0d", 7), # read in cleanup
    (0x49CC82, "48 c7 05", 11), # clear global, imm32 zero
    (0x4A2288, "48 8b 1d", 7), # read in alternate constructor
    (0x4A2327, "48 89 1d", 7), # publish alternate construction
    (0x4A2336, "48 89 1d", 7), # republish after LeaveCriticalSection
    (0x60CE34, "48 8b 05", 7), # separate global-present guard
    (0x60CEF0, "48 89 1d", 7), # second constructor publication
    (0x60CF07, "48 89 1d", 7), # second constructor republish
    (0x732498, "48 89 1d", 7), # third constructor publication
    (0x7324A7, "48 89 1d", 7), # third constructor republish
    (0x6A6413, "48 8b 3d", 7), # read in original callback
    (0x6A6433, "48 8b 3d", 7), # repeat read in callback
    (0x6A64A2, "48 89 3d", 7), # first published pointer
    (0x6A64B1, "48 89 3d", 7), # second published pointer
)
GLOBAL_RVA = 0x3362498
BRANCHES = {
    0x78B7A: (0x74, 0x78B95),  # null-parent JE
    0x78B7F: (0x75, 0x78B95),  # nonzero-state JNE
    0x78B93: (0xEB, 0x78BD5),  # fast path skips descriptor fallback
}
LONG_BRANCHES = {
    0x60CE3E: (bytes.fromhex("0f 85"), 0x60CF13),  # nonnull global -> ret
}
MUTATIONS = (0x6A649B, 0x6A64BC, 0xF7CD57, 0xF7CD9C, 0x13E9A7E, 0x13E9FE9,
             0x78B2E, 0x78B71, 0x6A64ED, 0xF7CDFF, 0x13E9FEE,
             0x78B7A, 0x78B7B, 0x78B7F, 0x78B80, 0x78B93, 0x78B94,
             0x78BD1, 0x78B95, 0x78BBC,
    0x13E9A84, 0x13E9AB5, 0x13E9AC6, 0x13E9ADB, 0x13E9AE7,
    0x13EA028, 0x13EA078, 0x13EA0D2, 0x13EA16F, 0x13EA1BD,
    0x13EA038, 0x13EA088, 0x13EA1C2,
    0x2793FE8, 0x2793FF0,
    0x49CC79, 0x49CC85, 0x4A228B, 0x4A232A, 0x4A2339,
    0x6A6416, 0x6A6436, 0x6A64A5, 0x6A64B4, 0x4A233F, 0x4A2345,
    0x13E7E7D, 0x13E7E99, 0x13E7EA5,
    0x60CE37, 0x60CEF3, 0x60CF0A, 0x73249B, 0x7324AA,
    0x60CEE9, 0x732480, 0x73248D, 0x7324B6, 0x13EA687,
    0x13EA668, 0x13EA67C, 0x13EA684,
    0x60CE3C, 0x60CE3F, 0x60CE40, 0x60CF14)


def insist(value, message):
    if not value:
        raise ValueError(message)


def rva_bytes(windows, rva, length):
    for name, (start, size, _) in WINDOWS.items():
        if start <= rva and rva + length <= start + size:
            return windows[name][rva - start:rva - start + length]
    raise ValueError(f"outside source windows: {rva:#x}")


def semantic_check(windows):
    for site, hx, size in GLOBAL_RIP_REFS:
        op = bytes.fromhex(hx)
        insn = rva_bytes(windows, site, size)
        insist(insn[:3] == op and site + size + struct.unpack_from("<i", insn, 3)[0] == GLOBAL_RVA,
               f"bad wrapper global reference {site:#x}")
        if site == 0x49CC82:
            insist(insn[7:] == bytes(4), "global clear must store zero")
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
    for site, (opcode, expected) in LONG_BRANCHES.items():
        insn = rva_bytes(windows, site, 6)
        insist(insn[:2] == opcode and site + 6 + struct.unpack_from("<i", insn, 2)[0] == expected,
               f"bad long conditional branch {site:#x}")
    for site, opcode, target in (
        (0x13E9A74, bytes.fromhex("48 8d 05"), 0x2793F58),
        (0x13E9AAB, bytes.fromhex("48 8d 0d"), 0x2793FE8),
        (0x13E9AD1, bytes.fromhex("48 8d 0d"), 0x2793FF0),
    ):
        insn = rva_bytes(windows, site, 7)
        insist(insn[:3] == opcode and site + 7 + struct.unpack_from("<i", insn, 3)[0] == target,
               f"bad adapter vptr LEA {site:#x}")
    for site, target in ((0x2793FE8, 0x13EA010), (0x2793FF0, 0x13EA060)):
        insist(struct.unpack("<Q", rva_bytes(windows, site, 8))[0] == 0x140000000 + target,
               f"bad adapter callback pointer {site:#x}")


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
        "task": "WA-006", "evidence": "static-wrapper-parent-global-lifecycle-and-adapter-only",
        "sourceSha256": SHA, "windows": len(WINDOWS),
        "opcodeAnchors": len(ANCHORS), "selectedGlobalRipReferences": len(GLOBAL_RIP_REFS),
        "directCalls": len(CALLS),
        "checkedBranches": len(BRANCHES) + len(LONG_BRANCHES),
        "ramNegativeControls": len(MUTATIONS), "wa006Accepted": False,
        "unproven": ["nonzero wrapper+8 setter", "same runtime parent",
                     "adapter invocation", "WorldManager virtual dispatch",
                     "physics/gameplay owner"]
    }, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
