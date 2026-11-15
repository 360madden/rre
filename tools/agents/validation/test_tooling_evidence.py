"""Portable evidence/locator tests; no native process, model or network."""
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[3]

def module(name,path):
    spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
E=module('evidence_summary',ROOT/'tools/evidence-summary.py')
I=module('literal_index',ROOT/'tools/agents/collision/wa_backlink_literal_index.py')

def evidence():
    a={'schemaVersion':1,'sha256':'a'*64,'queueRemaining':0,'functions':[{'beginRva':'0x1000','endRvaExclusive':'0x1010','decodedThroughRvaExclusive':'0x1010','windowTruncated':False,'instructionDecodingCoversWindow':True,'instructions':[{'rva':hex(0x1000+i),'bytes':'90','instruction':'nop'} for i in range(16)]}],
       'unresolvedAnchors':[{'rva':'0x2000','reason':'No unwind entry'}]}
    raw=json.dumps(a).encode()
    m={'schemaVersion':2,'source':{'sha256':'a'*64,'unchangedDuringRun':True},'artifact':{'sha256':hashlib.sha256(raw).hexdigest()},'status':'completed','invocation':{'exitCode':0},'queries':{'kind':'static','rvas':['0x1000','0x2000']},'coverage':{'boundedCaptureComplete':True}}
    return a,m,raw

class EvidenceTests(unittest.TestCase):
    def test_recording_success_is_not_complete_disassembly(self):
        r=E.summarize(*evidence());self.assertTrue(r['recordingCompleted']);self.assertFalse(r['allRequestedAnchorsDecoded']);self.assertEqual(len(r['unresolvedRequestedAnchors']),1)
    def test_fully_decoded_requested_anchor(self):
        a,m,raw=evidence();m['queries']['rvas']=['0x1000'];r=E.summarize(a,m,raw);self.assertTrue(r['allRequestedAnchorsDecoded']);self.assertFalse(r['semanticOwnershipQualified'])
    def test_empty_instructions_cannot_prove_full_decode(self):
        a,m,_=evidence();m['queries']['rvas']=['0x1000']
        a['functions'][0]['instructions']=[]
        raw=json.dumps(a).encode();m['artifact']['sha256']=hashlib.sha256(raw).hexdigest()
        r=E.summarize(a,m,raw)
        self.assertFalse(r['recordingCompleted'])
        self.assertFalse(r['allRequestedAnchorsDecoded'])
        self.assertEqual(r['retainedInstructionRows'],0)
        self.assertEqual(len(r['partialRegions']),1)

    def test_invalid_instruction_coverage_stays_partial(self):
        for scenario in ('gap','overlap','bad-hex','odd-hex','missing-rva','short','out-of-order'):
            with self.subTest(scenario=scenario):
                a,m,_=evidence();m['queries']['rvas']=['0x1000']
                rows=a['functions'][0]['instructions']
                if scenario=='gap':rows[8]['rva']='0x1009'
                elif scenario=='overlap':rows[8]['rva']='0x1007'
                elif scenario=='bad-hex':rows[8]['bytes']='zz'
                elif scenario=='odd-hex':rows[8]['bytes']='9'
                elif scenario=='missing-rva':rows[8].pop('rva')
                elif scenario=='short':rows.pop()
                elif scenario=='out-of-order':rows[0],rows[1]=rows[1],rows[0]
                raw=json.dumps(a).encode();m['artifact']['sha256']=hashlib.sha256(raw).hexdigest()
                r=E.summarize(a,m,raw)
                self.assertFalse(r['allRequestedAnchorsDecoded'])
                self.assertEqual(len(r['partialRegions']),1)

    def test_hash_corruption_rejected(self):
        a,m,raw=evidence()
        with self.assertRaisesRegex(ValueError,'SHA'):E.summarize(a,m,raw+b' ')
    def test_source_mismatch_rejected(self):
        a,m,raw=evidence();m['source']['sha256']='b'*64
        with self.assertRaisesRegex(ValueError,'source'):E.summarize(a,m,raw)
    def test_unaccounted_anchor_prevents_completion(self):
        a,m,raw=evidence();m['queries']['rvas'].append('0x3000');r=E.summarize(a,m,raw);self.assertFalse(r['recordingCompleted']);self.assertEqual(r['unaccountedRequestedAnchors'],['0x3000'])
    def test_incomplete_window_not_promoted(self):
        a,m,raw=evidence();a['functions'][0]['windowTruncated']=True;raw=json.dumps(a).encode();m['artifact']['sha256']=hashlib.sha256(raw).hexdigest();r=E.summarize(a,m,raw);self.assertFalse(r['allRequestedAnchorsDecoded']);self.assertEqual(len(r['partialRegions']),1)
    def test_duplicate_requested_anchor_rejected(self):
        a,m,raw=evidence();m['queries']['rvas'].append('0x1000')
        with self.assertRaisesRegex(ValueError,'Duplicate'):E.summarize(a,m,raw)
    def test_failed_process_not_promoted(self):
        a,m,raw=evidence();m['invocation']['exitCode']=1;self.assertFalse(E.summarize(a,m,raw)['recordingCompleted'])
    def test_duplicate_json_keys_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'x.json';p.write_text('{"a":1,"a":2}')
            with self.assertRaisesRegex(ValueError,'Duplicate'):E.load(p)
    def test_boolean_schema_rejected(self):
        a,m,raw=evidence();a['schemaVersion']=True
        with self.assertRaisesRegex(ValueError,'schema'):E.summarize(a,m,raw)

class LiteralIndexTests(unittest.TestCase):
    def test_all_hits_retained_beyond_old_top24(self):
        code=I.PATTERN*40;r=I.raw_hits(code,0x1000,[(0x1000,0x1100)])
        self.assertEqual(r['rawMatchCount'],40);self.assertEqual(len(r['regions'][0]['hits']),40);self.assertTrue(r['allRawHitsRetained'])
    def test_missing_unwind_retained_not_disassembled(self):
        r=I.raw_hits(I.PATTERN,0x1000,[]);self.assertEqual(len(r['withoutContainingUnwind']),1);self.assertFalse(r['instructionBoundariesVerified'])
    def test_nearest_range_does_not_claim_semantic_owner(self):
        r=I.raw_hits(b'\x90'*4+I.PATTERN,0x1000,[(0x1000,0x1004),(0x1004,0x1010)])
        self.assertEqual(r['regions'][0]['beginRva'],'0x1004');self.assertFalse(r['entityOwnershipQualified'])
    def test_relevance_flags_are_raw_only(self):
        code=bytes.fromhex('baffff0000b0000000b8000000');r=I.raw_hits(code,0x1000,[(0x1000,0x1100)])['regions'][0]
        self.assertTrue(r['rawContainsB0Disp']);self.assertTrue(r['rawContainsB8Disp']);self.assertTrue(r['rawContainsKeyAsEdxImmediate']);self.assertFalse(r['instructionBoundariesVerified'])
    def test_byte_budget_enforced(self):
        with patch.object(I,'MAX_TEXT',8):
            with self.assertRaisesRegex(ValueError,'budget'):I.raw_hits(b'0'*9,0,[])
    def test_repeatable_index(self):
        self.assertEqual(I.raw_hits(I.PATTERN,0,[]),I.raw_hits(I.PATTERN,0,[]))

if __name__=='__main__':unittest.main()
