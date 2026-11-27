import test from 'node:test';
import assert from 'node:assert/strict';
import crypto from 'node:crypto';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {spawnSync} from 'node:child_process';
import {compareCaptureBytes} from './compare-rrecollector-captures.mjs';

const V='0.4.23',ID='u0000000000000001',OTHER='u0000000000000002';
const hash=b=>crypto.createHash('sha256').update(b).digest('hex');
// Fixture-only serializer for controlled literal values, never a production Lua evaluator.
function lua(v){
  if(Array.isArray(v))return '{'+v.map(lua).join(',')+'}';
  if(v!==null&&typeof v==='object')return '{'+Object.entries(v).map(([k,x])=>'['+JSON.stringify(k)+']='+lua(x)).join(',')+'}';
  return JSON.stringify(v);
}
const bytes=v=>Buffer.from('RRECollectorData='+lua(v));
function snapshot(sequence,version){
  return {sequence,addonVersion:version,captureComplete:true,frameTime:10,realTime:20,
    roleSlot:1,player:{id:ID,name:'Fixture'},abilityList:{apiAvailable:true,
      enumerationComplete:true,detailFailures:0,ignored:0,truncated:0,
      uniqueCount:1,detailCount:1,rawEntries:1},abilities:[{lookupId:'A0000000000000001'}]};
}
function baseline(){
  return {addonVersion:V,sequence:2,latest:snapshot(2,'0.4.20')};
}
function candidate(sequence=3,attempt=1,unit=1,unitAttempt=1){
  return {addonVersion:V,sequence,latest:snapshot(sequence,V),
    captureAttempt:{schemaVersion:1,addonVersion:V,attemptSequence:attempt,
      status:'complete',reason:'none',preservedPrior:false,priorSequence:sequence-1,resultSequence:sequence,
      frameTime:10,realTime:20,counts:{uniqueCount:1,detailCount:1,detailFailures:0}},
    unitSnapshotSequence:unit,unitSnapshots:[{schemaVersion:1,addonVersion:V,
      scope:'manual-bounded-unit-api-witness',status:'complete',reason:'bounded-sample-complete',sequence:unit,
      selfId:ID,limits:{listEntries:128,detailCalls:8},counts:{examined:2,invalidEntries:0,
        selfEntries:1,nonselfEligible:1,detailsCalled:1,detailErrors:0,idMismatches:0,idMissing:0,qualifiedXYZ:1},
      records:[{id:OTHER,specifier:'group01',idBinding:'matched',detailStatus:'returned',
        xyzComplete:true,coordX:0,coordY:-2,coordZ:3}],
      listEnumerationComplete:true,detailSampleComplete:true,coordinateFrameVerified:false,
      nativeIdentityVerified:false,atomicSnapshot:false}],
    unitAttempt:{schemaVersion:1,addonVersion:V,attemptSequence:unitAttempt,
      status:'complete',reason:'bounded-sample-complete',resultSequence:unit}};
}
function compare(a,b){
  const original=bytes(a);
  return compareCaptureBytes(original,bytes(b),hash(original));
}
test('a prior-version ability baseline and two bound advancing attempts qualify offline only',()=>{
  const result=compare(baseline(),candidate());
  assert.equal(result.offlineProgressionQualified,true);
  assert.deepEqual(result.reasons,[]);
  assert.equal(result.baseline.abilitySequence,2);
  assert.equal(result.candidate.abilitySequence,3);
  assert.ok(Object.values(result.limits).every(v=>v===false));
  assert.equal(JSON.stringify(result).includes(ID),false);
});
test('wrong baseline hash is rejected before comparing',()=>{
  assert.throws(()=>compareCaptureBytes(bytes(baseline()),bytes(candidate()),'0'.repeat(64)),/BASELINE_SHA_MISMATCH/);
});
test('byte replay and metadata-only or counter-only changes cannot advance both receipts',()=>{
  const before=candidate();
  const replay=compare(before,before);
  assert.equal(replay.offlineProgressionQualified,false);
  assert.ok(replay.reasons.includes('distinctBytes'));
  const modified=structuredClone(before);modified.unrelated='changed';
  const stale=compare(before,modified);
  assert.equal(stale.checks.distinctBytes,true);
  assert.ok(stale.reasons.includes('advancingAbilitySequence'));
  assert.ok(stale.reasons.includes('advancingUnitAttempt'));
  assert.equal(stale.offlineProgressionQualified,false);
});
test('different character or mismatched unit self cannot qualify',()=>{
  const after=candidate();after.latest.player.id='u0000000000000003';
  assert.ok(compare(baseline(),after).reasons.includes('samePlayerId'));
  after.latest.player.id=ID;after.unitSnapshots[0].selfId='u0000000000000003';
  assert.ok(compare(baseline(),after).reasons.includes('unitSelfMatchesAbilityPlayer'));
});
test('failed attempts retaining old successes do not qualify',()=>{
  const after=candidate();
  after.captureAttempt={schemaVersion:1,addonVersion:V,attemptSequence:2,status:'failed',
    reason:'api-capture-error',preservedPrior:true,priorSequence:3};
  after.unitAttempt={schemaVersion:1,addonVersion:V,attemptSequence:2,status:'error',reason:'unit-list-error'};
  const r=compare(baseline(),after);
  assert.equal(r.offlineProgressionQualified,false);
  assert.ok(r.reasons.includes('completeAbilityAttemptBound'));
  assert.ok(r.reasons.includes('completeUnitAttemptBound'));
});
test('a second coherent capture advances all four counters; regressions fail closed',()=>{
  const before=candidate(),after=candidate(4,2,2,2);
  assert.equal(compare(before,after).offlineProgressionQualified,true);
  after.unitAttempt.attemptSequence=1;
  assert.ok(compare(before,after).reasons.includes('advancingUnitAttempt'));
  after.captureAttempt.attemptSequence=1;
  assert.ok(compare(before,after).reasons.includes('advancingAbilityAttempt'));
});
test('malformed baseline counter evidence cannot be silently replaced with zero',()=>{
  const before=baseline();before.captureAttempt={attemptSequence:9,status:'fake'};
  assert.ok(compare(before,candidate()).reasons.includes('baselineAttemptValid'));
  delete before.captureAttempt;before.unitSnapshotSequence=1;
  assert.ok(compare(before,candidate()).reasons.includes('baselineUnitStateValid'));
});
test('CLI exits distinctly for coherent progression, replay and invalid baseline pin',()=>{
  const tmp=fs.mkdtempSync(path.join(os.tmpdir(),'rre-capture-progression-'));
  try{
    const file=fileURLToPath(new URL('./compare-rrecollector-captures.mjs',import.meta.url));
    const before=path.join(tmp,'before','RRECollector.lua'),after=path.join(tmp,'after','RRECollector.lua');
    for(const p of [before,after])fs.mkdirSync(path.dirname(p));
    const b=bytes(baseline());fs.writeFileSync(before,b);fs.writeFileSync(after,bytes(candidate()));
    const run=(a,pin)=>spawnSync(process.execPath,[file,before,a,pin],{encoding:'utf8',timeout:5000});
    const passed=run(after,hash(b));assert.equal(passed.status,0,passed.stderr);
    assert.equal(JSON.parse(passed.stdout).offlineProgressionQualified,true);
    const replay=run(before,hash(b));assert.equal(replay.status,1);
    assert.equal(JSON.parse(replay.stdout).offlineProgressionQualified,false);
    assert.equal(run(after,'0'.repeat(64)).status,2);
  }finally{fs.rmSync(tmp,{recursive:true,force:true});}
});
