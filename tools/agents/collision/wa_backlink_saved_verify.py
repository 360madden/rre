#!/usr/bin/env python3
"""Verify already acquired WA-007 artifacts only; no new native reads or capture.

The next capture was tool-blocked. This verifier does not attempt that capture
or expand its targets. It checks retained byte records/receipts, not live identity.
"""
import hashlib
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[3]
BUILD='7c356c9dde9e12fcbff3c08d953b0630b48b1510a0ffb36e4ec164606e7b17bd'
CAPTURES={
 'wa2-keyed-owner-20261020-01':('d59d739b1d5d7f45abb1c9c110d02b52f63f739e830d4475fc58d45478c7b6d6','a4e39415698c5e8bb53c84c3d90b5d1ceb2f9e9e3bd236b52dad408b2b88b8e2'),
 'wa2-backlink-neighborhood-20261020-01':('f7c946197666f8b69360c76fb0ee8dbc2d4f959cfd39e73d3af4133ea9d5f6bd','6b034bedffea16059c966057909484c390565c114ac490e2abe9a57d8f3bd583'),
 'wa2-backlink-lookup-20261020-01':('35a2cbdd5e4f2adc3dbe4d19daf8b967d2c4472b68aa9d80036694573f1de4e1','8f64e57896ba9f4d99935b628cee85788037d29e5137f4a0fe9e5783fd44737e')}
PINS={'0xf674ea':'33db','0xf674ef':'48891a','0xf674f2':'486381b8000000','0xf674fd':'4c8b89b0000000',
      '0xf67510':'8138ffff0000','0xf6755e':'498b5cc108','0xf67563':'e8b89d52ff','0xf6756b':'4533c0',
      '0xf6756e':'488bd3','0xf67571':'e8da6b72ff','0xf67579':'488907',
      '0x68e15f':'4c8bc2','0x68e16b':'488b4cc150','0x68e170':'e8cbc9eeff','0x68e1af':'488b4210',
      '0x491324':'488b059defe402','0x49132e':'0f85cf000000','0x13d1a31':'6644018fcc070000'}

def check(ok,message):
    if not ok:raise ValueError(message)
def sha(b):return hashlib.sha256(b).hexdigest()

def verify(root=ROOT):
    rows={};regions=[]
    for tag,(ah,mh) in CAPTURES.items():
        ar=(root/'artifacts'/(tag+'.json')).read_bytes();mr=(root/'artifacts'/(tag+'-manifest.json')).read_bytes()
        check(sha(ar)==ah and sha(mr)==mh,'Saved artifact/manifest SHA mismatch: '+tag)
        a=json.loads(ar);m=json.loads(mr)
        check(a['sha256']==BUILD and m['source']['sha256']==BUILD,'Original source identity mismatch')
        check(m['status']=='completed' and m['invocation']['exitCode']==0 and m['source']['unchangedDuringRun'] is True,'Original recording not completed/stable')
        check(m['artifact']['sha256']==ah,'Receipt artifact hash mismatch')
        for f in a['functions']:
            check(f['instructionDecodingCoversWindow'] is True and f['windowTruncated'] is False,'Partial retained window')
            regions.append({'begin':f['beginRva'],'endExclusive':f['endRvaExclusive'],'rows':len(f['instructions'])})
            for row in f['instructions']:
                if row['rva'] in rows:check(rows[row['rva']]['bytes']==row['bytes'],'Conflicting byte records')
                rows[row['rva']]=row
    for rva,expected in PINS.items():check(rva in rows and rows[rva]['bytes']==expected,'Saved instruction pin mismatch: '+rva)
    return {'schemaVersion':1,'taskId':'WA-007','status':'saved-evidence-verified','sourceSha256':BUILD,
            'regions':regions,'retainedInstructionRows':sum(x['rows'] for x in regions),'pins':{r:rows[r] for r in PINS},
            'chain':['0xf674e0 reads 16-byte property records at receiver+0xb0/count+0xb8',
                     '0xf6755e loads the 0xffff record value',
                     '0xf67563 calls 0x491320; only its initial global-read region was captured',
                     '0xf67571 passes property value to 0x68e150 with index 0',
                     '0x68e16b selects receiver+0x50 container; 0x68e170 calls unexpanded 0x57ab40',
                     '0x68e1af can return node+0x10; exact key/owner classes remain unresolved'],
            'normalOutputBehavior':'0xf674ef initializes output to zero before search; this differs from earlier optional output in 0xf671c0',
            'rejectedLead':'0x13d1a31 uses 0xffff as a 16-bit decrement value, not a demonstrated property-key insertion',
            'unresolved':['Property-record writer/insertion path','Type and meaning of lookup key/value','Complete 0x491320 return/control flow','0x57ab40 internals','Logical unit/scene identity and live correspondence'],
            'nativeBytesReverifiedNow':False,'gameEntityIdentityQualified':False,'liveBehaviorQualified':False,
            'nextCaptureToolBlocked':True,'blockedCaptureRetried':False,
            'scope':'Retained original-build evidence only; no new PE scan, process read, game input or native call'}

if __name__=='__main__':
    try:print(json.dumps(verify(),indent=2,sort_keys=True))
    except (OSError,ValueError,KeyError,TypeError) as exc:print(json.dumps({'status':'failed','error':str(exc)}),file=sys.stderr);raise SystemExit(1)
