#!/usr/bin/env python3
"""Compact V7 saved-evidence summary: recording success is not resolved code coverage.

Reads only existing JSON and verifies artifact/manifest identities. Does not open
RIFT, execute native code, validate semantic labels, or rerun any binary scan.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import sys

MAX_BYTES=16*1024*1024


def require(ok, message):
    if not ok: raise ValueError(message)


def load(path):
    with Path(path).open('rb') as stream: raw=stream.read(MAX_BYTES+1)
    require(0<len(raw)<=MAX_BYTES,'Evidence outside 16 MiB limit')
    def pairs(items):
        result={}
        for key,value in items:
            require(key not in result,'Duplicate evidence JSON key: '+key);result[key]=value
        return result
    obj=json.loads(raw.decode('utf-8'),object_pairs_hook=pairs)
    require(isinstance(obj,dict),'Evidence must be an object')
    return obj,raw


def rows_cover_window(rows, first, last):
    """Check that retained instruction byte spans exactly cover the claimed window."""
    if not rows: return False
    cursor=first
    for row in rows:
        if not isinstance(row,dict): return False
        rva,encoded=row.get('rva'),row.get('bytes')
        if not isinstance(rva,str) or not isinstance(encoded,str) or not encoded or len(encoded)%2:
            return False
        if not all(char in '0123456789abcdefABCDEF' for char in encoded): return False
        try:
            if int(rva,0)!=cursor: return False
        except ValueError:
            return False
        cursor+=len(encoded)//2
        if cursor>last: return False
    return cursor==last


def summarize(artifact, manifest, artifact_bytes):
    require(type(artifact.get('schemaVersion')) is int and artifact['schemaVersion']==1 and
            type(manifest.get('schemaVersion')) is int and manifest['schemaVersion']==2,'Unsupported V7 schemas')
    expected=manifest.get('artifact',{}).get('sha256')
    require(expected==hashlib.sha256(artifact_bytes).hexdigest(),'Artifact SHA does not match immutable manifest')
    source=artifact.get('sha256'); ms=manifest.get('source',{})
    require(isinstance(source,str) and len(source)==64 and source==ms.get('sha256'),'Native source identity mismatch')
    queries=manifest.get('queries',{})
    require(queries.get('kind')=='static','Only static V7 captures supported')
    requested=queries.get('rvas')
    require(isinstance(requested,list) and requested,'Missing requested anchors')
    anchors=[int(v,0) for v in requested]
    require(len(set(anchors))==len(anchors),'Duplicate requested anchors')
    functions=artifact.get('functions'); unresolved=artifact.get('unresolvedAnchors')
    require(isinstance(functions,list) and isinstance(unresolved,list),'Missing coverage records')
    decoded=[]; partial=[]; ranges=[]; total=0
    for region in functions:
        first=int(region['beginRva'],0);last=int(region['endRvaExclusive'],0)
        require(first<last,'Invalid region bounds')
        rows=region.get('instructions',[])
        require(isinstance(rows,list),'Invalid instruction collection')
        complete=(region.get('windowTruncated') is False and region.get('instructionDecodingCoversWindow') is True
                  and int(region.get('decodedThroughRvaExclusive','0'),0)==last
                  and rows_cover_window(rows,first,last))
        total+=len(rows)
        ranges.append((first,last,complete))
        (decoded if complete else partial).append({'beginRva':hex(first),'endRvaExclusive':hex(last),'retainedInstructionRows':len(rows)})
    unresolved_by_rva={int(row['rva'],0):row.get('reason','unspecified') for row in unresolved}
    covered=[]; missing=[]; unresolved_requested=[]
    for rva in anchors:
        if any(a<=rva<b and complete for a,b,complete in ranges): covered.append(hex(rva))
        elif rva in unresolved_by_rva: unresolved_requested.append({'rva':hex(rva),'reason':unresolved_by_rva[rva]})
        else: missing.append(hex(rva))
    exit_code=manifest.get('invocation',{}).get('exitCode')
    process_ok=manifest.get('status')=='completed' and type(exit_code) is int and exit_code==0
    process_ok=process_ok and ms.get('unchangedDuringRun') is True
    recorded_complete=(process_ok and manifest.get('coverage',{}).get('boundedCaptureComplete') is True
                       and not missing and artifact.get('queueRemaining')==0)
    code_complete=recorded_complete and not unresolved_requested and not partial and len(covered)==len(anchors)
    return {'schemaVersion':1,'scope':'saved-static-evidence-summary; no native execution or fresh source read',
            'artifactSha256':expected,'sourceSha256':source,
            'recordingCompleted':recorded_complete,'allRequestedAnchorsDecoded':code_complete,
            'coverageState':'all-requested-anchors-decoded' if code_complete else 'unresolved-or-partial-code-coverage',
            'requestedAnchorCount':len(anchors),'decodedRequestedAnchors':covered,
            'unresolvedRequestedAnchors':unresolved_requested,'unaccountedRequestedAnchors':missing,
            'fullyDecodedRegions':decoded,'partialRegions':partial,'retainedInstructionRows':total,
            'recordedParserWarningCount':manifest.get('parserDiagnostics',{}).get('count'),
            'sourceUnchangedDuringOriginalRun':ms.get('unchangedDuringRun'),
            'nativeBytesReverifiedNow':False,'semanticOwnershipQualified':False,'liveBehaviorQualified':False}


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--artifact',type=Path,required=True);p.add_argument('--manifest',type=Path,required=True)
    p.add_argument('--output',type=Path)
    args=p.parse_args()
    try:
        art,raw=load(args.artifact);man,mraw=load(args.manifest)
        result=summarize(art,man,raw);result['manifestSha256']=hashlib.sha256(mraw).hexdigest()
        result['summaryToolSha256']=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
        encoded=json.dumps(result,indent=2,sort_keys=True)+'\n'
        if args.output:
            with args.output.open('x',encoding='utf-8',newline='\n') as out:out.write(encoded)
        print(encoded)
        return 0 if result['recordingCompleted'] else 1
    except (OSError,ValueError,KeyError,TypeError) as exc:
        print(json.dumps({'status':'failed','error':str(exc)}),file=sys.stderr);return 2

if __name__=='__main__':raise SystemExit(main())
