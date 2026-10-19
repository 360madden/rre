"""Verify M2-001 saved bytes/provenance offline, without adding research regions."""
import hashlib
import json
import sys
from pathlib import Path

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[3]
EXPECTED = '7c356c9dde9e12fcbff3c08d953b0630b48b1510a0ffb36e4ec164606e7b17bd'


def main():
    import capstone
    import pefile
    follow = json.loads((ROOT / 'docs/agents/c2m.json').read_text(encoding='utf-8'))['followUps'][-1]
    assert follow['taskId'] == 'M2-001'
    assert follow['build']['sha256'] == EXPECTED
    binary = Path(follow['build']['binary'])
    body = binary.read_bytes()
    assert hashlib.sha256(body).hexdigest() == EXPECTED
    for item in follow['sources'] + follow['artifacts']:
        path = Path(item['path'])
        if not path.is_absolute():
            path = ROOT / path
        assert hashlib.sha256(path.read_bytes()).hexdigest() == item['sha256'], str(path)
    pe = pefile.PE(data=body, fast_load=True)
    base = pe.OPTIONAL_HEADER.ImageBase
    assert base == 0x140000000 and pe.FILE_HEADER.Machine == 0x8664
    decoder = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_64)
    regions = set()
    rows = {}
    instruction_count = 0
    for artifact in follow['artifacts']:
        if artifact['kind'] != 'static-region-query':
            continue
        query = json.loads((ROOT / artifact['path']).read_text(encoding='utf-8'))
        assert query['sha256'] == EXPECTED and query['imageBase'] == hex(base)
        assert not query['queueRemaining'] and not query['unresolvedAnchors']
        assert query['dependencies'] == {'pefile': pefile.__version__, 'capstone': capstone.__version__}
        assert all(query[key] is False for key in ('reaDecompilation', 'gameInputSent', 'gameProcessAttached', 'targetExecuted'))
        for region in query['functions']:
            start, end = int(region['beginRva'], 0), int(region['endRvaExclusive'], 0)
            assert (start, end) not in regions
            regions.add((start, end))
            assert not region['windowTruncated'] and region['instructionDecodingCoversWindow']
            assert int(region['decodedThroughRvaExclusive'], 0) == end
            assert hashlib.sha256(pe.get_data(start, end-start)).hexdigest() == region['windowSha256']
            position = start
            for row in region['instructions']:
                rva, raw = int(row['rva'], 0), bytes.fromhex(row['bytes'])
                assert rva == position and pe.get_data(rva, len(raw)) == raw
                decoded = list(decoder.disasm(raw, base+rva))
                assert len(decoded) == 1 and decoded[0].size == len(raw)
                assert (decoded[0].mnemonic + ' ' + decoded[0].op_str).strip() == row['instruction']
                rows[row['rva']] = row
                position += len(raw)
                instruction_count += 1
            assert position == end
    assert len(regions) == follow['coverage']['freshUniqueRegions'] == 25
    for match in follow['matchedAssembly']:
        assert rows[match['rva']] == match, match['rva']
    ref = json.loads((ROOT / 'tools/agents/c2m/m2-001-references.json').read_text(encoding='utf-8'))
    assert ref['sha256'] == EXPECTED and ref['referenceTargets'] == ['0x6942a0']
    assert ref['references'] == []
    assert all(value is False for value in follow['safety'].values())
    pe.close()
    print(json.dumps({'status': 'passed', 'taskId': 'M2-001', 'regions': len(regions),
                      'instructions': instruction_count, 'sources': len(follow['sources']),
                      'artifacts': len(follow['artifacts']), 'matchedAssembly': len(follow['matchedAssembly']),
                      'exactBuildSha256': EXPECTED}))


if __name__ == '__main__':
    main()
