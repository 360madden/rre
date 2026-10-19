"""Offline bounded settings-root references; reuse RiftReader section reader + Capstone.

Print JSON to stdout. No target execution, process access, input, or source writes.
Usage: C:/work/rre/.venv/Scripts/python.exe -B tools/agents/c2m/inspect_settings.py
"""
import bisect
import hashlib
import importlib
import json
import re
import struct
import sys
from pathlib import Path

sys.dont_write_bytecode = True
BINARY = Path('C:/Program Files (x86)/Glyph/Games/RIFT/Live/rift_x64.exe')
HELPER = Path('C:/rift modding/RiftReader/scripts/postupdate_static_access_chain.py')
EXPECTED = '7c356c9dde9e12fcbff3c08d953b0630b48b1510a0ffb36e4ec164606e7b17bd'


def inspect():
    assert hashlib.sha256(BINARY.read_bytes()).hexdigest() == EXPECTED
    assert hashlib.sha256(HELPER.read_bytes()).hexdigest() == 'c62d729ea027c271c8b4113c927ab039ae760d6db20f479166e7769dd4891319'
    sys.path.insert(0, str(HELPER.parent))
    helper = importlib.import_module(HELPER.stem)
    assert Path(helper.__file__).resolve() == HELPER.resolve()
    import capstone
    import pefile
    from capstone.x86_const import X86_OP_MEM, X86_REG_RIP
    base, sections, errors = helper.executable_sections(BINARY)
    assert not errors
    pe = pefile.PE(str(BINARY), fast_load=True)
    pe.parse_data_directories(directories=[pefile.DIRECTORY_ENTRY['IMAGE_DIRECTORY_ENTRY_EXCEPTION']])
    ranges = sorted((int(x.struct.BeginAddress), int(x.struct.EndAddress)) for x in pe.DIRECTORY_ENTRY_EXCEPTION)
    starts = [x[0] for x in ranges]
    decoder = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_64)
    decoder.detail = True
    references = []
    for section in sections:
        # Only common REX.W MOV r64,[RIP+disp32], not an exhaustive xref engine.
        for match in re.finditer(rb'[\x48\x4c]\x8b[\x05\x0d\x15\x1d\x25\x2d\x35\x3d]', section.data):
            off = match.start()
            if off + 7 > len(section.data):
                continue
            site = section.rva + off
            if site + 7 + struct.unpack_from('<i', section.data, off + 3)[0] != 0x33136f0:
                continue
            index = bisect.bisect_right(starts, site) - 1
            bounds = ranges[index] if index >= 0 and site < ranges[index][1] else None
            aligned = False
            if bounds and site - bounds[0] <= 65536:
                prefix = helper.read_section_bytes(sections, bounds[0], site - bounds[0] + 7)
                aligned = any(i.address == base + site and i.mnemonic == 'mov' for i in decoder.disasm(prefix, base + bounds[0]))
            stop = min(site + 512, bounds[1]) if bounds else site + 128
            instructions = list(decoder.disasm(helper.read_section_bytes(sections, site, stop-site), base+site))[:96]
            fields = [hex(i.address-base) for i in instructions if any(o.type == X86_OP_MEM and o.mem.base != X86_REG_RIP and o.mem.disp == 0x146 for o in i.operands)]
            references.append({'siteRva':hex(site), 'peRange':[hex(x) for x in bounds] if bounds else None,
                               'aligned':aligned, 'field146SitesInWindow':fields,
                               'window':[{'rva':hex(i.address-base), 'bytes':bytes(i.bytes).hex(), 'instruction':i.mnemonic+' '+i.op_str} for i in instructions] if fields else []})
    field_references = []
    for section in sections:
      for field_offset in (0x146, 0x1a8):
        for match in re.finditer(re.escape(struct.pack('<i', field_offset)), section.data):
            site = section.rva + match.start()
            index = bisect.bisect_right(starts, site) - 1
            bounds = ranges[index] if index >= 0 and site < ranges[index][1] else None
            if not bounds or site - bounds[0] > 65536:
                continue
            data = helper.read_section_bytes(sections, bounds[0], min(bounds[1]-bounds[0], site-bounds[0]+160))
            instructions = list(decoder.disasm(data, base+bounds[0]))
            for n, insn in enumerate(instructions):
                if insn.address-base <= site < insn.address-base+insn.size and any(o.type == X86_OP_MEM and o.mem.disp == field_offset and o.size == 1 for o in insn.operands):
                    field_references.append({'fieldOffset':hex(field_offset), 'siteRva':hex(insn.address-base), 'peRange':[hex(x) for x in bounds],
                                             'window':[{'rva':hex(i.address-base), 'bytes':bytes(i.bytes).hex(), 'instruction':i.mnemonic+' '+i.op_str} for i in instructions[max(0,n-18):n+20]]})
    assert hashlib.sha256(BINARY.read_bytes()).hexdigest() == EXPECTED
    pe.close()
    return {'sha256':EXPECTED, 'imageBase':hex(base), 'method':'Common RIP MOV references, PE-range prefix alignment, bounded 512-byte/96-instruction lookahead; field displacement is a lead, not alias proof',
            'references':references, 'byteFieldReferences':field_references}


if __name__ == '__main__':
    print(json.dumps(inspect(), indent=2))
