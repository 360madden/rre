// Offline fail-closed tests for source-hashed RRECollector unit receipts.
import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import crypto from 'node:crypto';
import {spawnSync} from 'node:child_process';
import {fileURLToPath} from 'node:url';
import {summarizeUnitWitness, readUnitWitness} from './export-rrecollector-units.mjs';

const uid = n => 'u' + n.toString(16).toUpperCase().padStart(16, '0');
function fixture() {
  const snap = {
    schemaVersion:1, addonVersion:'0.4.23', scope:'manual-bounded-unit-api-witness',
    status:'complete', reason:'bounded-sample-complete', sequence:2,
    limits:{listEntries:128, detailCalls:8},
    counts:{examined:2, invalidEntries:0, selfEntries:1, nonselfEligible:1,
      detailsCalled:1, detailErrors:0, idMismatches:0, idMissing:0, qualifiedXYZ:1},
    records:[{id:uid(2),specifier:'group01',idBinding:'matched',
      detailStatus:'returned',xyzComplete:true,coordX:0,coordY:-2,coordZ:3}],
    listEnumerationComplete:true,detailSampleComplete:true,
    coordinateFrameVerified:false,nativeIdentityVerified:false,atomicSnapshot:false,
    selfId:uid(1),frameStart:1,frameEnd:1.5,realStart:1795030000,realEnd:1795030001
  };
  return {addonVersion:'0.4.23',unitSnapshotSequence:2,
    unitSnapshots:[snap,{...structuredClone(snap),sequence:1}],
    unitAttempt:{schemaVersion:1,addonVersion:'0.4.23',attemptSequence:2,
      status:'complete',reason:'bounded-sample-complete',resultSequence:2}};
}
function reject(change, code) {
  const x=fixture();change(x);
  assert.throws(()=>summarizeUnitWitness(x),new RegExp(code));
}
test('two retained sequences, zero and negative XYZ, source and false qualification',()=>{
  const out=summarizeUnitWitness(fixture(),{sha256:'a'.repeat(64),bytes:4096});
  assert.equal(out.evidenceKind,'rre-unit-witness/1');
  assert.deepEqual(out.snapshots.map(x=>x.sequence),[2,1]);
  assert.equal(out.snapshots[0].records[0].coordX,0);
  assert.equal(out.snapshots[0].records[0].coordY,-2);
  assert.equal(out.qualification.nativeIdentityVerified,false);
  assert.equal(out.sourceSha256,'a'.repeat(64));
});
test('first manual unit API failure is a valid attempt-only receipt',()=>{
  const x={addonVersion:'0.4.23',unitAttempt:{schemaVersion:1,
    addonVersion:'0.4.23',attemptSequence:1,status:'unavailable',
    reason:'missing-unit-api'}};
  const result=summarizeUnitWitness(x,{sha256:'b'.repeat(64),bytes:128});
  assert.equal(result.snapshotState,'attempt-only');
  assert.equal(result.snapshots.length,0);
  assert.equal(result.lastAttempt.status,'unavailable');
  assert.equal(result.lastAttempt.resultSequence,null);
  assert.equal(result.qualification.nativeIdentityVerified,false);
  assert.equal(result.sourceSha256,'b'.repeat(64));
});
test('attempt-only errors keep diagnostics but never create accepted snapshots',()=>{
  const x={addonVersion:'0.4.23',unitAttempt:{schemaVersion:1,
    addonVersion:'0.4.23',attemptSequence:2,status:'error',
    reason:'unit-capture-exception'}};
  const result=summarizeUnitWitness(x);
  assert.equal(result.snapshotState,'attempt-only');
  assert.equal(result.lastAttempt.reason,'unit-capture-exception');
  assert.deepEqual(result.snapshots,[]);
});
test('attempt-only success, result sequence, or missing attempt fail closed',()=>{
  const x={addonVersion:'0.4.23',unitAttempt:{schemaVersion:1,
    addonVersion:'0.4.23',attemptSequence:1,status:'error',
    reason:'unit-list-error'}};
  const rejectOnly=(modify,code)=>{
    const attempt=structuredClone(x); modify(attempt);
    assert.throws(()=>summarizeUnitWitness(attempt),new RegExp(code));
  };
  rejectOnly(v=>{v.unitAttempt.status='complete'},'UNIT_ATTEMPT');
  rejectOnly(v=>{v.unitAttempt.resultSequence=1},'UNIT_ATTEMPT');
  rejectOnly(v=>{v.unitSnapshotSequence=1},'UNIT_SEQUENCE');
  rejectOnly(v=>{v.unitSnapshots=[]},'UNIT_SEQUENCE');
  rejectOnly(v=>{delete v.unitAttempt},'UNIT_ATTEMPT');
});
test('failed later witness preserves previous accepted report',()=>{
  const x=fixture();
  x.unitAttempt={schemaVersion:1,addonVersion:'0.4.23',attemptSequence:3,
    status:'error',reason:'unit-list-error'};
  assert.equal(summarizeUnitWitness(x).lastAttempt.resultSequence,null);
});
test('producer version and retained sequences cannot be retagged',()=>{
  reject(x=>{x.addonVersion='0.4.22'},'UNIT_ROOT_VERSION');
  reject(x=>{x.unitSnapshots[0].addonVersion='0.4.22'},'UNIT_SNAPSHOT_CONTRACT');
  reject(x=>{x.unitSnapshots[1].sequence=2},'UNIT_SEQUENCE_COHERENCE');
  reject(x=>{x.unitSnapshotSequence=3},'UNIT_SEQUENCE_COHERENCE');
  reject(x=>{x.unitSnapshots.push(x.unitSnapshots[0])},'UNIT_SNAPSHOT_ARRAY');
});
test('attempt outcome distinguishes persistent failure from successful capture',()=>{
  reject(x=>{delete x.unitAttempt.resultSequence},'UNIT_ATTEMPT_PRESERVATION');
  reject(x=>{x.unitAttempt.status='error'},'UNIT_ATTEMPT_PRESERVATION');
  reject(x=>{x.unitAttempt.resultSequence=1},'UNIT_ATTEMPT_CONTRACT');
});
test('attempt status and reason must bind to actual outcome',()=>{
  reject(x=>{x.unitAttempt.reason='unit-list-error'},'UNIT_ATTEMPT_RESULT_BINDING');
  reject(x=>{x.unitAttempt.status='partial'},'UNIT_ATTEMPT_RESULT_BINDING');
  reject(x=>{x.unitAttempt.status='error';delete x.unitAttempt.resultSequence;
    x.unitAttempt.reason='bounded-sample-complete'},'UNIT_ATTEMPT_REASON');
});
test('Detail status cannot invent matched identity after an error',()=>{
  reject(x=>{x.unitSnapshots[0].records[0].detailStatus='error'},
    'UNIT_DETAIL_STATUS_BINDING');
});
test('forged qualification rejected, zero coordinates valid',()=>{
  reject(x=>{x.unitSnapshots[0].nativeIdentityVerified=true},'UNIT_QUALIFICATION_FALSE');
  reject(x=>{x.unitSnapshots[0].atomicSnapshot=true},'UNIT_QUALIFICATION_FALSE');
  reject(x=>{x.unitSnapshots[0].coordinateFrameVerified=true},'UNIT_QUALIFICATION_FALSE');
});
test('missing/mismatched identity never authorizes XYZ',()=>{
  reject(x=>{x.unitSnapshots[0].records[0].idBinding='mismatch'},'UNIT_UNBOUND_COORDINATE');
  reject(x=>{delete x.unitSnapshots[0].records[0].coordZ},'UNIT_XYZ_BINDING');
  reject(x=>{x.unitSnapshots[0].records[0].coordY=Infinity},'UNIT_COORDINATE');
  reject(x=>{x.unitSnapshots[0].records[0].coordY=NaN},'UNIT_COORDINATE');
});
test('counter, cap, and exact-ID contradictions rejected',()=>{
  reject(x=>{x.unitSnapshots[0].counts.qualifiedXYZ=0},'UNIT_COUNT_COHERENCE');
  reject(x=>{x.unitSnapshots[0].counts.examined=129},'UNIT_COUNTS');
  reject(x=>{x.unitSnapshots[0].records[0].id=uid(1)},'UNIT_RECORD_ID');
  reject(x=>{x.unitSnapshots[0].records[0].specifier='\n'},'UNIT_RECORD_ID');
  reject(x=>{x.unitSnapshots[0].status='capped'},'UNIT_COVERAGE');
  reject(x=>{x.unitSnapshots[0].status='empty'},'UNIT_STATUS_REASON_BINDING');
});
test('producer-specific partial reasons cannot be fabricated',()=>{
  reject(x=>{x.unitSnapshots[0].status='partial';
    x.unitSnapshots[0].reason='xyz-incomplete'},'UNIT_STATUS_REASON_BINDING');
  reject(x=>{x.unitSnapshots[0].status='partial';
    x.unitSnapshots[0].reason='detail-sample-cap'},'UNIT_STATUS_REASON_BINDING');
  reject(x=>{x.unitSnapshots[0].reason='detail-errors'},'UNIT_STATUS_REASON_BINDING');
  reject(x=>{x.unitSnapshots[0].reason='invalid-list-entries'},'UNIT_STATUS_REASON_BINDING');
});
test('per-capture clock regressions and duplicate self entries fail',()=>{
  reject(x=>{x.unitSnapshots[0].frameEnd=0.5},'UNIT_CLOCK_ORDER');
  reject(x=>{x.unitSnapshots[0].realEnd=1795029999},'UNIT_CLOCK_ORDER');
  reject(x=>{const c=x.unitSnapshots[0].counts;
    c.examined=3;c.selfEntries=2},'UNIT_SELF_COUNT');
});
test('row order and case-folded duplicate native keys are rejected',()=>{
  const two=x=>{
    const s=x.unitSnapshots[0];
    s.counts.examined=3;s.counts.nonselfEligible=2;
    s.counts.detailsCalled=2;s.counts.qualifiedXYZ=2;
    s.records.push({...structuredClone(s.records[0]),id:uid(3)});
  };
  reject(x=>{two(x);x.unitSnapshots[0].records.reverse()},'UNIT_RECORD_ORDER');
  reject(x=>{two(x);x.unitSnapshots[0].records[0].id=uid(10);
    x.unitSnapshots[0].records[1].id=uid(10).toLowerCase()},'UNIT_RECORD_ID');
  reject(x=>{x.unitSnapshots[0].selfId=uid(10);
    x.unitSnapshots[0].records[0].id=uid(10).toLowerCase()},'UNIT_RECORD_ID');
});
test('unrecognized source fields rejected',()=>{
  reject(x=>{x.unitSnapshots[0].spell='cast'},'UNIT_SNAPSHOT_SHAPE');
  reject(x=>{x.unitSnapshots[0].records[0].spell='cast'},'UNIT_RECORD_FIELDS');
});
test('original attempt-only SavedVariables file is source-hashed without false capture',()=>{
  const source='RRECollectorData={addonVersion="0.4.23",'+
    'unitAttempt={schemaVersion=1,addonVersion="0.4.23",'+
    'attemptSequence=1,status="unavailable",reason="missing-unit-api"}}';
  const dir=fs.mkdtempSync(path.join(os.tmpdir(),'rre-attempt-only-'));
  const file=path.join(dir,'RRECollector.lua');
  try {
    fs.writeFileSync(file,source,'utf8');
    const receipt=readUnitWitness(file);
    assert.equal(receipt.snapshotState,'attempt-only');
    assert.equal(receipt.lastAttempt.reason,'missing-unit-api');
    assert.deepEqual(receipt.snapshots,[]);
    assert.equal(receipt.sourceSha256,crypto.createHash('sha256').update(source).digest('hex'));
    assert.equal(receipt.qualification.live,false);
    const cli=fileURLToPath(new URL('./export-rrecollector-units.mjs',import.meta.url));
    const run=spawnSync(process.execPath,[cli,file],
      {encoding:'utf8',timeout:5000});
    assert.equal(run.status,0,run.stderr);
    const json=JSON.parse(run.stdout);
    assert.equal(json.snapshotState,'attempt-only');
    assert.deepEqual(json.snapshots,[]);
    assert.equal(json.lastAttempt.status,'unavailable');
  }finally{
    fs.unlinkSync(file);fs.rmdirSync(dir);
  }
});
test('original Lua file parsed read-only and SHA-bound',()=>{
  const content='RRECollectorData={addonVersion="0.4.23",unitSnapshotSequence=1,'
    +'unitSnapshots={{schemaVersion=1,addonVersion="0.4.23",'
    +'scope="manual-bounded-unit-api-witness",status="empty",'
    +'reason="no-nonself-listed",sequence=1,limits={listEntries=128,detailCalls=8},'
    +'counts={examined=0,invalidEntries=0,selfEntries=0,nonselfEligible=0,'
    +'detailsCalled=0,detailErrors=0,idMismatches=0,idMissing=0,qualifiedXYZ=0},'
    +'records={},listEnumerationComplete=true,detailSampleComplete=true,'
    +'coordinateFrameVerified=false,nativeIdentityVerified=false,atomicSnapshot=false,'
    +'selfId="u0000000000000001"}}}';
  const root=fs.mkdtempSync(path.join(os.tmpdir(),'rre-unit-export-'));
  const file=path.join(root,'RRECollector.lua');
  try {
    fs.writeFileSync(file,content,'utf8');
    const out=readUnitWitness(file);
    assert.equal(out.sourceSha256,crypto.createHash('sha256').update(content).digest('hex'));
    assert.equal(out.snapshots[0].status,'empty');
  } finally {
    fs.unlinkSync(file);fs.rmdirSync(root);
  }
});
