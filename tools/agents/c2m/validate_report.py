"""Validate retained offline evidence against exact sources; no process or input APIs."""
import hashlib
import json
import struct
import sys
from pathlib import Path

sys.dont_write_bytecode = True

def main():
    import capstone
    import pefile
    report = Path(__file__).resolve().parents[3] / 'docs/agents/c2m.json'
    data = json.loads(report.read_text(encoding='utf-8'))
    binary = Path(data['build']['binary'])
    assert hashlib.sha256(binary.read_bytes()).hexdigest() == data['build']['sha256']
    for source in data['sources']:
        assert hashlib.sha256(Path(source['path']).read_bytes()).hexdigest() == source['sha256'], source['path']
    pe = pefile.PE(str(binary), fast_load=True)
    base = int(data['build']['preferredImageBase'], 0)
    assert pe.OPTIONAL_HEADER.ImageBase == base
    decoder = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_64)
    count = 0
    for region in data['regions']:
        start, end = int(region['beginRva'], 0), int(region['endRvaExclusive'], 0)
        body = pe.get_data(start, end-start)
        assert hashlib.sha256(body).hexdigest() == region['windowSha256'], region['beginRva']
        for row in region['instructions']:
            rva = int(row['rva'], 0)
            raw = bytes.fromhex(row['bytes'])
            assert start <= rva and rva+len(raw) <= end
            assert pe.get_data(rva, len(raw)) == raw, row['rva']
            decoded = list(decoder.disasm(raw, base+rva))
            assert len(decoded) == 1 and decoded[0].size == len(raw), row['rva']
            assert (decoded[0].mnemonic+' '+decoded[0].op_str).strip() == row['instruction'], row['rva']
            count += 1
    for item in data['constants']:
        raw = pe.get_data(int(item['rva'], 0), 4)
        assert raw.hex() == item['bytes']
        assert struct.unpack('<f', raw)[0] == item['float32']
    assert all(value is False for value in data['safety'].values())
    assert data['scan']['rootMovCandidateCount'] == len(data['scan']['rootMovSites'])
    assert data['scan']['rootMovAlignedCount'] == 319
    pe.close()
    print(json.dumps({'status':'passed', 'sources':len(data['sources']), 'regions':len(data['regions']),
                      'retainedInstructions':count, 'exactBuildSha256':data['build']['sha256']}))

if __name__ == '__main__':
    main()
