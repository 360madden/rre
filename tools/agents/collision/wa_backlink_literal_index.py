#!/usr/bin/env python3
"""Reusable raw PE literal locator for WA-007; no instruction/ownership claims.

A prior one-off probe retained only 24 proximity-ranked regions. This replacement
retains every bounded raw hit and its nearest PE-unwind range for offline queries.
A hit may be unaligned data; neither proximity nor displacement proves an owner.
"""
from __future__ import annotations
import argparse
import bisect
import hashlib
import json
from pathlib import Path
import re
import sys

BUILD = '7c356c9dde9e12fcbff3c08d953b0630b48b1510a0ffb36e4ec164606e7b17bd'
EXE = Path(r'C:\Program Files (x86)\Glyph\Games\RIFT\Live\rift_x64.exe')
MAX_TEXT = 64 * 1024 * 1024
PATTERN = bytes.fromhex('ffff0000')


def raw_hits(code: bytes, base: int, ranges: list[tuple[int,int]]) -> dict:
    if len(code) > MAX_TEXT:
        raise ValueError('Text exceeds 64 MiB bounded locator budget')
    ordered = sorted(set(ranges)); starts = [a for a,_ in ordered]
    grouped = {}; unresolved = []
    for match in re.finditer(re.escape(PATTERN), code):
        offset = match.start(); rva = base + offset
        start = max(0, offset-12); end = min(len(code), offset+20)
        hit = {'literalRva':hex(rva),'contextRva':hex(base+start),'contextHex':code[start:end].hex()}
        i = bisect.bisect_right(starts,rva)-1
        if i < 0 or not (ordered[i][0] <= rva < ordered[i][1]):
            unresolved.append(hit); continue
        first,last = ordered[i]
        grouped.setdefault((first,last),[]).append(hit)
    rows = []
    for (first,last), hits in sorted(grouped.items()):
        # Source-byte relevance flags only; deliberately no disassembler here.
        lo,hi = max(0,first-base),min(len(code),last-base)
        blob=code[lo:hi]
        rows.append({'beginRva':hex(first),'endRvaExclusive':hex(last),'hits':hits,
                     'rawContainsB0Disp':bytes.fromhex('b0000000') in blob,
                     'rawContainsB8Disp':bytes.fromhex('b8000000') in blob,
                     'rawContainsKeyAsEdxImmediate':bytes.fromhex('baffff0000') in blob,
                     'instructionBoundariesVerified':False})
    return {'regions':rows,'withoutContainingUnwind':unresolved,
            'rawMatchCount':sum(len(r['hits']) for r in rows)+len(unresolved),
            'scannedTextBytes':len(code),'allRawHitsRetained':True,
            'instructionBoundariesVerified':False,'entityOwnershipQualified':False}


def scan(binary: Path = EXE) -> dict:
    import pefile
    raw=binary.read_bytes(); digest=hashlib.sha256(raw).hexdigest()
    if digest != BUILD:
        raise ValueError('Pinned native executable SHA mismatch')
    pe=pefile.PE(data=raw,fast_load=True)
    try:
        if pe.FILE_HEADER.Machine != 0x8664 or pe.OPTIONAL_HEADER.ImageBase != 0x140000000:
            raise ValueError('Unexpected native PE target')
        pe.parse_data_directories(directories=[pefile.DIRECTORY_ENTRY['IMAGE_DIRECTORY_ENTRY_EXCEPTION']])
        section=next(s for s in pe.sections if s.Name.rstrip(b'\0')==b'.text')
        ranges=[(int(e.struct.BeginAddress),int(e.struct.EndAddress)) for e in pe.DIRECTORY_ENTRY_EXCEPTION]
        result=raw_hits(section.get_data(),int(section.VirtualAddress),ranges)
        result.update(schemaVersion=1,taskId='WA-007',sourceSha256=digest,literalHex=PATTERN.hex(),
                      method='raw literal index; nearest PE metadata range; NOT disassembly or complete data flow',
                      generatorSha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                      parserWarnings=pe.get_warnings(),offlineOnly=True,gameInputSent=False)
        return result
    finally:
        pe.close()


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True)
    args=p.parse_args()
    try:
        if args.output.exists(): raise FileExistsError('Existing index is immutable')
        result=scan()
        with args.output.open('x',encoding='utf-8',newline='\n') as out: json.dump(result,out,indent=2);out.write('\n')
        candidates=[{'begin':r['beginRva'],'end':r['endRvaExclusive'],'hits':len(r['hits'])}
                    for r in result['regions'] if r['rawContainsB0Disp'] and r['rawContainsB8Disp']]
        print(json.dumps({'output':str(args.output),'rawMatches':result['rawMatchCount'],'regions':len(result['regions']),
                          'allHitsRetained':True,'rawB0B8Candidates':candidates,'entityOwnershipQualified':False},indent=2))
        return 0
    except (OSError,ValueError,KeyError,StopIteration) as exc:
        print(json.dumps({'status':'failed','error':str(exc)}),file=sys.stderr);return 1

if __name__=='__main__': raise SystemExit(main())
