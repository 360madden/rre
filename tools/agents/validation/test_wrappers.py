"""Synthetic PE-only regression checks for the navigation wrappers.

Run with C:/work/rre/.venv/Scripts/python.exe -B this_file.py -v.
No target execution, attach, REA/Ghidra invocation, or external-tree writes.
"""
import hashlib
import json
from pathlib import Path
import struct
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
STATIC_HELPER = Path(r"C:\rift modding\RiftReader\scripts\postupdate_static_access_chain.py")
NAMES_HELPER = Path(r"C:\rift modding\RiftReader\scripts\anti-re\rtti_class_scanner.py")
HELPER_HASHES = {
    STATIC_HELPER: "c62d729ea027c271c8b4113c927ab039ae760d6db20f479166e7769dd4891319",
    NAMES_HELPER: "3636e5ca9c39318c27a7c5fdbccfd01e3258ef079139a0d9df64f49961448331",
}
BASE = 0x140000000


def synthetic_pe(text=b"\xc3", rdata=b"", ranges=((0x1000, 0x1001, 0x3100),), chain=False):
    """Minimal x64 PE carrier, parsed by actual pefile and actual Capstone."""
    text = text.ljust((len(text) + 511) // 512 * 512, b"\xcc")
    ro = bytearray(rdata.ljust(512, b"\0"))
    ro[0x100:0x104] = b"\x01\0\0\0"
    if chain:
        ro[0x110:0x120] = b"\x21\0\0\0" + struct.pack("<III", *ranges[0])
    pdata = b"".join(struct.pack("<III", *r) for r in ranges).ljust(512, b"\0")
    header = bytearray(512)
    header[:2] = b"MZ"
    struct.pack_into("<I", header, 0x3c, 0x80)
    header[0x80:0x84] = b"PE\0\0"
    struct.pack_into("<HHIIIHH", header, 0x84, 0x8664, 3, 0, 0, 0, 240, 0x22)
    opt = 0x98
    struct.pack_into("<H", header, opt, 0x20b)
    struct.pack_into("<I", header, opt + 16, 0x1000)
    struct.pack_into("<Q", header, opt + 24, BASE)
    struct.pack_into("<II", header, opt + 32, 0x1000, 0x200)
    struct.pack_into("<II", header, opt + 56, 0x5000, 0x200)
    struct.pack_into("<H", header, opt + 68, 3)
    struct.pack_into("<I", header, opt + 108, 16)
    struct.pack_into("<II", header, opt + 112 + 3 * 8, 0x4000, 12 * len(ranges))
    raw = 512
    for index, (name, va, content, flags) in enumerate([
        (b".text", 0x1000, text, 0x60000020),
        (b".rdata", 0x3000, bytes(ro), 0x40000040),
        (b".pdata", 0x4000, pdata, 0x40000040),
    ]):
        struct.pack_into("<8sIIIIIIHHI", header, opt + 240 + index * 40,
                         name, len(content), va, len(content), raw, 0, 0, 0, 0, flags)
        raw += len(content)
    return bytes(header) + text + ro + pdata


class WrapperChecks(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="synthetic-", dir=HERE)
        self.addCleanup(self.temp.cleanup)
        self.folder = Path(self.temp.name)

    def run_wrapper(self, kind, binary, *extra, binary_hash=None, helper_hash=None, output=None):
        source = self.folder / "synthetic.exe"
        source.write_bytes(binary)
        helper = STATIC_HELPER if kind == "static" else NAMES_HELPER
        self.assertEqual(hashlib.sha256(helper.read_bytes()).hexdigest(), HELPER_HASHES[helper])
        out = output or self.folder / "output.json"
        args = [sys.executable, "-B", str(ROOT / "tools" / f"inspect-navigation-{kind}.py"),
                "--binary", str(source), "--helper", str(helper), "--output", str(out),
                "--expected-sha256", binary_hash or hashlib.sha256(binary).hexdigest(),
                "--expected-helper-sha256", helper_hash or HELPER_HASHES[helper]]
        result = subprocess.run(args + list(extra), capture_output=True, text=True, timeout=25)
        return result, json.loads(out.read_text()) if out.exists() else None

    def test_static_signed_address_math_and_unwind_chain(self):
        text = bytearray(b"\x90" * 0x30)
        text[:5] = b"\xe8" + struct.pack("<i", 0x1020 - 0x1005)
        text[5:12] = b"\x48\x8d\x0d" + struct.pack("<i", 0x3000 - 0x100c)
        text[0x20:0x25] = b"\xe8" + struct.pack("<i", 0x1000 - 0x1025)
        binary = synthetic_pe(bytes(text), ranges=((0x1000, 0x1010, 0x3100), (0x1020, 0x1030, 0x3110)), chain=True)
        run, data = self.run_wrapper("static", binary, "--rva", "0x1020", "--depth", "0", "--follow-unwind-chains")
        self.assertEqual(run.returncode, 0, run.stderr)
        self.assertEqual(data["imageBase"], hex(BASE))
        functions = {f["beginRva"]: f for f in data["functions"]}
        self.assertEqual(set(functions), {"0x1000", "0x1020"})
        self.assertTrue(all(f["unwindChainRootRva"] == "0x1000" for f in functions.values()))
        self.assertEqual(functions["0x1020"]["directAndIndirectCalls"][0]["targetRva"], "0x1000")
        self.assertEqual(functions["0x1000"]["ripRelativeReferences"][0]["targetRva"], "0x3000")
        self.assertEqual(json.loads(run.stdout)["functions"], 2)

    def test_names_nonexecuting_strings_offsets_and_references(self):
        text = b"\x48\x8d\x0d" + struct.pack("<i", 0x3000 - 0x1007) + b"\xc3pathfind-in-code\0"
        ro = bytearray(256)
        ro[:9] = b"pathfind\0"
        wide = "navmesh".encode("utf-16-le") + b"\0\0"
        ro[0x20:0x20+len(wide)] = wide
        struct.pack_into("<Q", ro, 0x60, BASE + 0x3000)
        run, data = self.run_wrapper("names", synthetic_pe(text, bytes(ro), ((0x1000, 0x1008, 0x3100),)), "--reference-rva", "0x3000")
        self.assertEqual(run.returncode, 0, run.stderr)
        self.assertEqual(data["termCounts"]["pathfind"], 1)
        self.assertEqual(data["termCounts"]["navmesh"], 1)
        self.assertTrue(all(s["section"] != ".text" for s in data["stringMatches"]))
        wide_hit = next(s for s in data["stringMatches"] if s["encoding"] == "utf-16-le")
        self.assertEqual(wide_hit["rva"], "0x3020")
        self.assertEqual(wide_hit["fileOffset"], "0x420")
        self.assertTrue(data["references"][0]["instructionBoundaryVerifiedFromPeRange"])
        self.assertIn("stored absolute pointer", {r["kind"] for r in data["references"]})
        json.loads(run.stdout)

    def test_binary_and_helper_hash_mismatch_fail_closed(self):
        for kind in ("static", "names"):
            for hashes in ({"binary_hash": "0" * 64}, {"helper_hash": "0" * 64}):
                with self.subTest(kind=kind, hashes=hashes):
                    run, data = self.run_wrapper(kind, synthetic_pe(), *(["--rva", "0x1000"] if kind == "static" else []), **hashes)
                    self.assertNotEqual(run.returncode, 0)
                    self.assertIsNone(data)
                    self.assertEqual(run.stdout, "")

    def test_existing_output_is_preserved(self):
        out = self.folder / "sentinel.json"
        out.write_text('{"sentinel":true}')
        for kind in ("static", "names"):
            run, data = self.run_wrapper(kind, synthetic_pe(), *(["--rva", "0x1000"] if kind == "static" else []), output=out)
            self.assertNotEqual(run.returncode, 0)
            self.assertEqual(data, {"sentinel": True})

    def test_leaf_anchor_unresolved_and_decoder_stop_reported(self):
        run, data = self.run_wrapper("static", synthetic_pe(b"\x0f", ranges=((0x1000, 0x1001, 0x3100),)), "--rva", "0x1000", "--rva", "0x2000", "--depth", "0")
        self.assertEqual(run.returncode, 0, run.stderr)
        self.assertFalse(data["functions"][0]["instructionDecodingCoversWindow"])
        self.assertEqual(data["unresolvedAnchors"][0]["rva"], "0x2000")

    def test_bug_v1_valid_caller_after_64_unaligned_candidates_is_reported(self):
        target = 0x1800
        text = bytearray()
        for _ in range(64):
            site = 0x1000 + len(text) + 2
            text += b"\x48\xb8\xe8" + struct.pack("<i", target - (site + 5)) + b"\0\0\0"
        valid_site = 0x1000 + len(text)
        text += b"\xe8" + struct.pack("<i", target - (valid_site + 5)) + b"\xc3"
        end = 0x1000 + len(text)
        text = text.ljust(0x801, b"\x90")
        text[0x800] = 0xc3
        binary = synthetic_pe(bytes(text), ranges=((0x1000, end, 0x3100), (target, target+1, 0x3100)))
        run, data = self.run_wrapper("static", binary, "--rva", hex(target), "--caller-rva", hex(target), "--depth", "0")
        self.assertEqual(run.returncode, 0, run.stderr)
        self.assertEqual(len(data["callerReferences"]), 64)
        self.assertTrue(any(r["siteRva"] == hex(valid_site) and r["instructionBoundaryVerifiedFromPeRange"] for r in data["callerReferences"]))

    def test_bug_v2_empty_unmapped_window_is_not_complete(self):
        run, data = self.run_wrapper("static", synthetic_pe(ranges=((0x2000, 0x2010, 0x3100),)), "--rva", "0x2000", "--depth", "0")
        self.assertEqual(run.returncode, 0, run.stderr)
        self.assertFalse(data["functions"][0]["instructionDecodingCoversWindow"])


if __name__ == "__main__":
    if "--strict" in sys.argv:
        sys.argv.remove("--strict")
        for method in WrapperChecks.__dict__.values():
            if getattr(method, "__unittest_expecting_failure__", False):
                method.__unittest_expecting_failure__ = False
    unittest.main()
