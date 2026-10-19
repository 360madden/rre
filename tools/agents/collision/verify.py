"""Read-only exact-build collision evidence verification. Never executes target.

Reuses pefile and the existing RiftReader name matcher; instruction decoding
remains in tools/inspect-navigation-static.py and inspect-navigation-names.py.
"""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import struct
import sys

sys.dont_write_bytecode = True
EXPECTED = '7c356c9dde9e12fcbff3c08d953b0630b48b1510a0ffb36e4ec164606e7b17bd'
BINARY = Path(r'C:\Program Files (x86)\Glyph\Games\RIFT\Live\rift_x64.exe')
SCANNER = Path(r'C:\rift modding\RiftReader\scripts\anti-re\rtti_class_scanner.py')
SCANNER_HASH = '3636e5ca9c39318c27a7c5fdbccfd01e3258ef079139a0d9df64f49961448331'
NAMES = ('hkpCharacterProxy', 'hkpWorldRayCaster', 'hkpWorldLinearCaster',
         'hkpKdTreeWorldLinearCaster', 'hkpGroupCollisionFilter')


def require(condition, message):
    if not condition:
        raise ValueError(message)


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def rtti_links(pe):
    """Bounded MSVC x64 RTTI-shaped records, not verified class layouts.

    Test name-16, signature=1, self-RVA and stored locator pointers. Retain
    at most eight executable-pointer slots; stop before adjacent data.
    This is metadata parsing, not a new instruction decoder.
    """
    require(digest(SCANNER) == SCANNER_HASH, 'RTTI scanner changed')
    spec = importlib.util.spec_from_file_location('collision_existing_rtti', SCANNER)
    scanner = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(scanner)
    names = scanner.scan_for_rtti(pe)
    base = int(pe.OPTIONAL_HEADER.ImageBase)
    sections = [(int(s.VirtualAddress), s.get_data(), int(s.Characteristics)) for s in pe.sections]
    def executable(rva):
        return any(flags & 0x20000000 and start <= rva < start + len(body)
                   for start, body, flags in sections)
    result = []
    for name in NAMES:
        matches = [n for n in names if n['name'] == '?AV' + name + '@@']
        require(len(matches) == 1, 'Missing/ambiguous name: ' + name)
        nrva = matches[0]['rva']
        td = nrva - 16
        locators = []
        for start, body, flags in sections:
            if flags & 0x20000000:
                continue
            needle = struct.pack('<I', td)
            offset = body.find(needle)
            while offset >= 0:
                col = start + offset - 12
                if offset >= 12 and offset + 12 <= len(body):
                    fields = struct.unpack_from('<6I', body, offset - 12)
                    if fields[0] == 1 and fields[5] == col:
                        tables = []
                        for start2, body2, flags2 in sections:
                            if flags2 & 0x20000000:
                                continue
                            pointer = struct.pack('<Q', base + col)
                            at = body2.find(pointer)
                            while at >= 0:
                                vrva = start2 + at + 8
                                slots = []
                                for index in range(8):
                                    target = struct.unpack('<Q', pe.get_data(vrva + index * 8, 8))[0] - base
                                    if not executable(target):
                                        break
                                    slots.append(hex(target))
                                tables.append({'vtableRva': hex(vrva), 'codePointerPrefixRvas': slots,
                                               'prefixCap': 8, 'stoppedAtNonExecutablePointer': len(slots) < 8})
                                at = body2.find(pointer, at + 1)
                        locators.append({'rva': hex(col), 'rawBytes': pe.get_data(col, 24).hex(),
                                         'signature': fields[0], 'subobjectOffset': hex(fields[1]),
                                         'constructorDisplacement': fields[2], 'typeDescriptorRva': hex(fields[3]),
                                         'hierarchyRva': hex(fields[4]), 'selfRva': hex(fields[5]), 'tables': tables})
                offset = body.find(needle, offset + 1)
        result.append({'name': name, 'nameRva': hex(nrva), 'typeDescriptorCandidateRva': hex(td),
                       'descriptorPrefixBytes': pe.get_data(td, 16).hex(), 'locators': locators})
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--rtti', action='store_true')
    parser.add_argument('--verify', type=Path)
    args = parser.parse_args()
    require(args.rtti != bool(args.verify), 'Choose exactly one mode')
    binary_bytes = BINARY.read_bytes()
    require(hashlib.sha256(binary_bytes).hexdigest() == EXPECTED, 'Executable hash mismatch')
    import pefile
    pe = pefile.PE(data=binary_bytes, fast_load=True)
    try:
        require(pe.FILE_HEADER.Machine == 0x8664, 'Expected x64 PE')
        require(pe.OPTIONAL_HEADER.ImageBase == 0x140000000, 'Image base mismatch')
        links = rtti_links(pe)
        if args.rtti:
            print(json.dumps(links, indent=2))
            return
        report = json.loads(args.verify.read_text(encoding='utf-8'))
        require(report['build']['sha256'] == EXPECTED, 'Report build mismatch')
        for source in report['sources']:
            require(digest(source['path']) == source['sha256'], 'Source hash mismatch: ' + source['path'])
        require(report['evidence']['rttiLinks'] == links, 'RTTI links differ')
        rows = 0
        regions = report['evidence']['nativeRegions']
        for region in regions:
            start, end = int(region['beginRva'], 0), int(region['endRvaExclusive'], 0)
            require(region['instructionDecodingCoversWindow'] and not region['windowTruncated'], 'Incomplete window')
            body = pe.get_data(start, end - start)
            require(hashlib.sha256(body).hexdigest() == region['windowSha256'], 'Region hash mismatch')
            cursor = start
            for row in region['instructions']:
                rva, data = int(row['rva'], 0), bytes.fromhex(row['bytes'])
                require(rva == cursor, 'Non-contiguous instructions')
                require(pe.get_data(rva, len(data)) == data, 'Instruction bytes differ')
                cursor += len(data)
                rows += 1
            require(cursor == end, 'Instructions do not cover region')
        for ref in report['evidence']['references']:
            if 'bytes' in ref:
                data = bytes.fromhex(ref['bytes'])
                require(pe.get_data(int(ref['siteRva'], 0), len(data)) == data, 'Reference bytes differ')
        for string in report['evidence']['strings']:
            data = string['text'].encode('ascii') + b'\0'
            require(pe.get_data(int(string['rva'], 0), len(data)) == data, 'String bytes differ')
        print(json.dumps({'verified': True, 'binarySha256': EXPECTED, 'sources': len(report['sources']),
                          'rttiClasses': len(links), 'regions': len(regions), 'instructionRows': rows,
                          'strings': len(report['evidence']['strings']),
                          'scope': 'Offline byte/provenance verification; no runtime or semantic proof'}))
    finally:
        pe.close()


if __name__ == '__main__':
    main()
