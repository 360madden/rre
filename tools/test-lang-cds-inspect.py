"""Synthetic fail-closed checks for inspect-lang-cds.py; no physical RIFT access."""
import hashlib
import importlib.util
import struct
import tempfile
import unittest
import zlib
from pathlib import Path

SCRIPT = Path(__file__).with_name("inspect-lang-cds.py")
SPEC = importlib.util.spec_from_file_location("inspect_lang_cds", SCRIPT)
MOD = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MOD)


def leb(value):
    if value < 0:
        raise ValueError("negative fixture")
    result = bytearray()
    while True:
        digit = value & 127
        value >>= 7
        result.append(digit | (128 if value else 0))
        if not value:
            return bytes(result)


def cds(records, offsets_override=None):
    frames = bytearray()
    offsets = []
    for _key, payload, unpacked in records:
        offsets.append(len(frames))
        frames.extend(leb(len(payload)))
        frames.extend(leb(unpacked))
        frames.extend(payload)
    key_table = bytearray()
    for i, (key, _payload, _unpacked) in enumerate(records):
        key_table.extend(struct.pack("<i", key))
        key_table.extend(leb(offsets[i] if offsets_override is None else offsets_override[i]))
    return (struct.pack("<i", len(records))
            + struct.pack("<256I", *([1] * 256))
            + key_table + frames)


def fixture_archive(cds_bytes, extra=b"", first_link=1):
    packed = zlib.compress(cds_bytes) + extra
    id8 = hashlib.sha1(cds_bytes).digest()[:8]
    sha = hashlib.sha1(packed).digest()
    head = struct.pack("<4sIIII", b"TWAD", 1, 20, 1, first_link)
    row = struct.pack("<8sIIIHH20s", id8, 64, len(packed), 0, 0, 1, sha)
    return head + row + packed, hashlib.sha256(head + row).hexdigest(), id8.hex()


class InspectLanguageTests(unittest.TestCase):
    def setUp(self):
        self.samples = [(100, b"abc", 5), (200, b"\x00\x01", 2)]
        self.good = cds(self.samples)

    def test_inventory_complete(self):
        info = MOD.inventory_cds(self.good)
        self.assertEqual((info["entryCount"], info["offsetsMatchingFrames"]), (2, 2))
        self.assertEqual((info["firstKey"], info["lastKey"]), (100, 200))
        self.assertEqual(info["framedRecordBytes"], 9)

    def test_uleb_truncated_and_overflow(self):
        with self.assertRaises(ValueError):
            MOD.read_uleb32(b"\x80", 0)
        with self.assertRaises(ValueError):
            MOD.read_uleb32(b"\x80\x80\x80\x80\x10", 0)

    def test_bad_offset(self):
        with self.assertRaisesRegex(ValueError, "offset"):
            MOD.inventory_cds(cds(self.samples, offsets_override=[0, 0]))

    def test_duplicate_key(self):
        with self.assertRaisesRegex(ValueError, "duplicate"):
            MOD.inventory_cds(cds([(100, b"x", 1), (100, b"y", 1)]))

    def test_truncated_record(self):
        with self.assertRaises(ValueError):
            MOD.inventory_cds(self.good[:-1])

    def test_extra_record_bytes(self):
        with self.assertRaisesRegex(ValueError, "unexpected bytes"):
            MOD.inventory_cds(self.good + b"\x00")

    def test_reject_huge_count(self):
        with self.assertRaisesRegex(ValueError, "count"):
            MOD.inventory_cds(struct.pack("<i", 500000) + self.good[4:])

    def check_archive(self, data, metadata_sha, id8):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "sample.002"
            path.write_bytes(data)
            return MOD.archive_entry(path, 0, metadata_sha, id8)

    def test_archive_full_integrity(self):
        b, digest, id8 = fixture_archive(self.good)
        info = self.check_archive(b, digest, id8)
        self.assertEqual((info["entryCount"], info["linkedRows"]), (2, 1))
        self.assertEqual(info["packedBytes"], len(b) - 64)
        self.assertFalse(info["contentTextDecoded"])

    def test_reject_metadata_drift(self):
        b, digest, id8 = fixture_archive(self.good)
        with self.assertRaisesRegex(ValueError, "metadata SHA256"):
            self.check_archive(b, "0" * 64, id8)

    def test_reject_wrong_content_id(self):
        b, digest, id8 = fixture_archive(self.good)
        with self.assertRaisesRegex(ValueError, "content ID"):
            self.check_archive(b, digest, "0" * 16)

    def test_reject_unlinked_entry(self):
        b, digest, id8 = fixture_archive(self.good, first_link=0)
        with self.assertRaisesRegex(ValueError, "not linked"):
            self.check_archive(b, digest, id8)

    def test_reject_trailing_packed_data(self):
        b, digest, id8 = fixture_archive(self.good, extra=b"garbage")
        with self.assertRaisesRegex(ValueError, "trailing"):
            self.check_archive(b, digest, id8)

    def test_reject_corrupt_payload_hash(self):
        b, digest, id8 = fixture_archive(self.good)
        bad = b[:-1] + bytes([b[-1] ^ 1])
        with self.assertRaises((ValueError, zlib.error)):
            self.check_archive(bad, digest, id8)


    def test_reject_stored_sha_even_if_zlib_valid(self):
        data, _digest, id8 = fixture_archive(self.good)
        bad = bytearray(data)
        bad[44] ^= 1  # SHA1 field starts at header 20 + row byte 24
        new_digest = hashlib.sha256(bad[:64]).hexdigest()
        with self.assertRaisesRegex(ValueError, "compressed SHA1"):
            self.check_archive(bytes(bad), new_digest, id8)

    def test_reject_decompressed_id_prefix(self):
        data, _digest, _id8 = fixture_archive(self.good)
        bad = bytearray(data)
        bad[20] ^= 1  # content-ID field, deliberately consistent with caller
        new_digest = hashlib.sha256(bad[:64]).hexdigest()
        with self.assertRaisesRegex(ValueError, "decompressed SHA1 prefix"):
            self.check_archive(bytes(bad), new_digest, bad[20:28].hex())

    def test_reject_link_cycle(self):
        data, _digest, id8 = fixture_archive(self.good)
        bad = bytearray(data)
        struct.pack_into("<H", bad, 40, 1)  # row next points to itself
        new_digest = hashlib.sha256(bad[:64]).hexdigest()
        with self.assertRaisesRegex(ValueError, "linked chain"):
            self.check_archive(bytes(bad), new_digest, id8)

    def test_reject_truncated_framed_entry(self):
        bad = bytearray(self.good)
        bad[1038] = 127  # first frame advertises more bytes than remain
        with self.assertRaisesRegex(ValueError, "truncated"):
            MOD.inventory_cds(bytes(bad))


if __name__ == "__main__":
    unittest.main(verbosity=2)
