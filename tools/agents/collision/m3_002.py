"""M3-002 offline evidence verification, reusing the original decoder helper.

Leaf entries lack PE unwind records: retain fixed windows and helper summaries,
never assign guessed function boundaries. No process or network APIs.
"""
import argparse
import hashlib
import importlib
import json
from pathlib import Path
import struct
import sys

sys.dont_write_bytecode = True
EXPECTED = '7c356c9dde9e12fcbff3c08d953b0630b48b1510a0ffb36e4ec164606e7b17bd'
BINARY = Path(r'C:\Program Files (x86)\Glyph\Games\RIFT\Live\rift_x64.exe')
HELPER = Path(r'C:\rift modding\RiftReader\scripts\postupdate_static_access_chain.py')
HELPER_HASH = 'c62d729ea027c271c8b4113c927ab039ae760d6db20f479166e7769dd4891319'
LEAVES = (0x105cb4, 0x13d2910)


def require(condition, message):
    if not condition:
        raise ValueError(message)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def acquire():
    data = BINARY.read_bytes()
    require(sha(data) == EXPECTED, 'Build mismatch')
    require(sha(HELPER.read_bytes()) == HELPER_HASH, 'Original helper changed')
    import pefile
    pe = pefile.PE(data=data, fast_load=True)
    require(pe.FILE_HEADER.Machine == 0x8664, 'Not x64')
    require(pe.OPTIONAL_HEADER.ImageBase == 0x140000000, 'Wrong preferred base')
    sys.path.insert(0, str(HELPER.parent))
    helper = importlib.import_module(HELPER.stem)
    require(Path(helper.__file__).resolve() == HELPER.resolve(), 'Wrong import')
    base, sections, errors = helper.executable_sections(BINARY)
    require(not errors and base == 0x140000000, 'Section acquisition failed')
    require(sha(BINARY.read_bytes()) == EXPECTED, 'Binary changed during acquisition')
    return pe, helper, sections


def supplemental(pe, helper, sections):
    leaves = []
    for rva in LEAVES:
        body = helper.read_section_bytes(sections, rva, 96)
        leaves.append({
            'beginRva': hex(rva), 'windowBytes': 96, 'rawBytes': body.hex(),
            'windowSha256': sha(body),
            'boundarySource': 'Fixed 96-byte window at stored vtable entry; no unwind record',
            'summary': helper.summarize_function_window(
                image_base=0x140000000, sections=sections, function_rva=rva,
                function_bytes=96, max_rows=64),
            'limitation': 'Original helper stops at first INT3, not RET. No complete function/CFG claim. Raw window includes bytes beyond the summarized prefix.'})
    records = []
    def read(rva, size, role):
        body = pe.get_data(rva, size)
        records.append({'rva': hex(rva), 'size': size, 'role': role,
                        'rawBytes': body.hex(), 'sha256': sha(body)})
        return body
    for table in (0x272b808, 0x2d609a0):
        col = struct.unpack('<Q', read(table - 8, 8, 'Stored locator VA'))[0] - 0x140000000
        fields = struct.unpack('<6I', read(col, 24, 'MSVC COL-shaped record'))
        require(fields[0] == 1 and fields[5] == col, 'Invalid locator candidate')
        name = pe.get_string_at_rva(fields[3] + 16)
        read(fields[3] + 16, len(name) + 1, 'RTTI name: ' + name.decode('ascii'))
        read(table, 24, 'Three code VAs; full table extent unproven')
    read(0x2659570, 16, 'SIMD absolute-value mask')
    read(0x272bb90, 16, 'Four float32 0.1 threshold values')
    return {'leafWindows': leaves, 'dataReads': records}


def verify(report):
    document = json.loads(report.read_text(encoding='utf-8'))
    followup = next(x for x in document['followUps'] if x['taskId'] == 'M3-002')
    evidence = followup['evidence']
    pe, helper, sections = acquire()
    try:
        require(evidence['sha256'] == EXPECTED, 'Evidence build mismatch')
        for source in evidence['sources']:
            require(sha(Path(source['path']).read_bytes()) == source['sha256'],
                    'Source changed: ' + source['path'])
        pe.parse_data_directories(directories=[3])
        bounds = {(int(e.struct.BeginAddress), int(e.struct.EndAddress))
                  for e in pe.DIRECTORY_ENTRY_EXCEPTION}
        regions = [r for q in evidence['staticQueries'] for r in q['functions']]
        require(len(regions) == len({r['beginRva'] for r in regions}) == 10, 'Wrong region count')
        require(all(q['queueRemaining'] == 0 for q in evidence['staticQueries']), 'Pending regions')
        require(len(regions) + len(LEAVES) == evidence['codeRegionBudget']['totalUniqueCodeRegions'] <= 25,
                'Budget mismatch')
        rows = 0
        for region in regions:
            begin, end = int(region['beginRva'], 0), int(region['endRvaExclusive'], 0)
            require((begin, end) in bounds, 'Invalid unwind boundary')
            require(not region['windowTruncated'] and region['instructionDecodingCoversWindow'], 'Incomplete decode')
            require(sha(pe.get_data(begin, end - begin)) == region['windowSha256'], 'Region mismatch')
            cursor = begin
            for row in region['instructions']:
                body = bytes.fromhex(row['bytes'])
                require(int(row['rva'], 0) == cursor and pe.get_data(cursor, len(body)) == body,
                        'Noncontiguous or mismatched instruction bytes')
                cursor += len(body)
                rows += 1
            require(cursor == end, 'Incomplete region')
        current = supplemental(pe, helper, sections)
        for key in current:
            require(evidence[key] == current[key], key + ' mismatch')
        require(all(value is False for value in evidence['safety'].values()), 'Unexpected action')
        print(json.dumps({'verified': True, 'taskId': 'M3-002', 'codeRegions': 12,
                          'unwindInstructionRows': rows, 'leafWindows': 2,
                          'dataReads': len(current['dataReads']),
                          'scope': 'Offline bytes, boundaries, helper summaries and provenance; no semantic/runtime proof'}))
    finally:
        pe.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--verify', type=Path)
    group.add_argument('--supplemental', action='store_true')
    args = parser.parse_args()
    if args.verify:
        verify(args.verify)
    else:
        pe, helper, sections = acquire()
        try:
            print(json.dumps(supplemental(pe, helper, sections), indent=2))
        finally:
            pe.close()
