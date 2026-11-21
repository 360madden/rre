// Offline-only Collector/G2 Lua unit sampling triage, never native qualification.
import test from 'node:test';
import assert from 'node:assert/strict';
import {spawnSync} from 'node:child_process';
import {mkdtempSync,writeFileSync,unlinkSync,rmdirSync} from 'node:fs';
import {tmpdir} from 'node:os';
import {join} from 'node:path';
import {fileURLToPath} from 'node:url';
import {summarizeUnitWitness} from '../../export-rrecollector-units.mjs';
import {triageCollectorG2} from './triage_collector_g2_units.mjs';
const id=n=>'u'+n.toString(16).toUpperCase().padStart(16,'0');
function collector(){
  const records=[2,3].map((n)=>({id:id(n),specifier:'other.'+n,
    idBinding:'matched',detailStatus:'returned',xyzComplete:true,
    coordX:100+n,coordY:200+n,coordZ:300+n}));
  const snap={schemaVersion:1,addonVersion:'0.4.23',
    scope:'manual-bounded-unit-api-witness',status:'complete',
    reason:'bounded-sample-complete',sequence:1,
    limits:{listEntries:128,detailCalls:8},
    counts:{examined:3,invalidEntries:0,selfEntries:1,nonselfEligible:2,
      detailsCalled:2,detailErrors:0,idMismatches:0,idMissing:0,qualifiedXYZ:2},
    records,listEnumerationComplete:true,detailSampleComplete:true,
    coordinateFrameVerified:false,nativeIdentityVerified:false,atomicSnapshot:false,
    selfId:id(1),frameStart:1,frameEnd:2,realStart:3,realEnd:4};
  return {addonVersion:'0.4.23',unitSnapshotSequence:1,unitSnapshots:[snap],
    unitAttempt:{schemaVersion:1,addonVersion:'0.4.23',attemptSequence:1,
      status:'complete',reason:'bounded-sample-complete',resultSequence:1}};
}
function packet(b=id(3),self=id(1),coord=103){
  return Buffer.from([
    `WA006_G2_V1|BEGIN|self=${self}|frame=10.000000|real=11.000000`,
    `WA006_G2_V1|ROW|id=${id(2)}|specifier=other.two|x=102.000000|y=202.000000|z=302.000000|idBinding=matched`,
    `WA006_G2_V1|ROW|id=${b}|specifier=other.three|x=${coord.toFixed(6)}|y=203.000000|z=303.000000|idBinding=matched`,
    'WA006_G2_V1|END|examined=3|details=2|validXYZ=2|errors=0|capped=false|frameEnd=12.000000|realEnd=13.000000|status=exploratory-only'
  ].join('\n')+'\n');
}
const compare=(data=collector(),raw=packet())=>triageCollectorG2(summarizeUnitWitness(data),raw);
test('two shared API IDs are only overlap leads, never native or WA006 acceptance',()=>{
  const out=compare();
  assert.equal(out.status,'API-ID-overlap-unqualified');
  assert.deepEqual(out.sharedNonselfIds,[id(2).toLowerCase(),id(3).toLowerCase()]);
  assert.equal(out.sharedNonselfCount,2);
  assert.equal(out.maxAxisDeltaObserved,0);
  for(const key of ['nativeCorrelationDone','wa006Accepted','sameSceneVerified','sameEpochVerified'])
    assert.equal(out[key],false);
  assert.ok(out.limitations.includes('collector-sorts-eligible-IDs-G2-selects-during-unordered-enumeration'));
});
test('G2 swapped ID with identical XYZ reduces overlap and is rejected',()=>{
  const out=compare(collector(),packet(id(4)));
  assert.equal(out.status,'rejected');
  assert.ok(out.reasons.includes('fewer-than-two-shared-Lua-API-IDs'));
  assert.equal(out.wa006Accepted,false);
});
test('self ID mismatch rejects even with two apparent other-unit joins',()=>{
  const out=compare(collector(),packet(id(3),id(9)));
  assert.ok(out.reasons.includes('self-unit-ID-mismatch'));
  assert.equal(out.status,'rejected');
});
test('coordinate drift is reported, never treated as same-time proof',()=>{
  const out=compare(collector(),packet(id(3),id(1),104));
  assert.equal(out.status,'API-ID-overlap-unqualified');
  assert.equal(out.maxAxisDeltaObserved,1);
  assert.ok(out.limitations.includes('serial-coordinate-values-differ-without-time-alignment'));
  assert.equal(out.nativeCorrelationDone,false);
});
test('partially sampled Collector is never treated as a complete witness',()=>{
  const x=collector(),s=x.unitSnapshots[0];
  delete s.records[1].coordZ;s.records[1].xyzComplete=false;
  s.counts.qualifiedXYZ=1;s.status='partial';s.reason='xyz-incomplete';
  x.unitAttempt.status='partial';x.unitAttempt.reason='xyz-incomplete';
  const out=compare(x);
  assert.equal(out.status,'rejected');
  assert.ok(out.reasons.includes('collector-sample-incomplete'));
  assert.equal(out.wa006Accepted,false);
});
test('invalid G2 packet fails existing canonical packet gate',()=>{
  const raw=Buffer.from(packet().toString().replace('details=2','details=9'));
  const out=compare(collector(),raw);
  assert.equal(out.status,'rejected');
  assert.ok(out.reasons.includes('invalid-G2-packet'));
  assert.equal(out.sharedNonselfCount,0);
});
test('CLI rejects missing source arguments without attempting a game action',()=>{
  const cli=fileURLToPath(new URL('./triage_collector_g2_units.mjs',import.meta.url));
  const out=spawnSync(process.execPath,[cli],{encoding:'utf8',timeout:5000});
  assert.equal(out.status,2);
  assert.match(out.stderr,/TRIAGE_USAGE/);
});
test('CLI accepts original Lua bytes and bounds original G2 text before reading it',()=>{
  const literal=value=>Array.isArray(value)
    ? '{'+value.map(literal).join(',')+'}'
    : value!==null && typeof value==='object'
      ? '{'+Object.entries(value).map(([key,v])=>key+'='+literal(v)).join(',')+'}'
      : typeof value==='string' ? JSON.stringify(value) : String(value);
  const dir=mkdtempSync(join(tmpdir(),'rre-g2-triage-'));
  const saved=join(dir,'RRECollector.lua'),g2=join(dir,'g2.txt');
  const cli=fileURLToPath(new URL('./triage_collector_g2_units.mjs',import.meta.url));
  try{
    writeFileSync(saved,'RRECollectorData='+literal(collector()),'utf8');
    writeFileSync(g2,packet());
    const good=spawnSync(process.execPath,[cli,saved,g2],
      {encoding:'utf8',timeout:5000});
    assert.equal(good.status,0,good.stderr);
    const receipt=JSON.parse(good.stdout);
    assert.equal(receipt.status,'API-ID-overlap-unqualified');
    assert.equal(receipt.nativeCorrelationDone,false);
    writeFileSync(g2,'x'.repeat(12000),'utf8');
    const large=spawnSync(process.execPath,[cli,saved,g2],
      {encoding:'utf8',timeout:5000});
    assert.equal(large.status,2);
    assert.match(large.stderr,/G2_SOURCE_SIZE/);
  }finally{
    unlinkSync(saved);unlinkSync(g2);rmdirSync(dir);
  }
});
test('wrong Collector schema and version never return source-overlap success',()=>{
  const invalid={evidenceKind:'something-else',producerVersion:'0.4.22',snapshots:[]};
  const out=triageCollectorG2(invalid,packet());
  assert.equal(out.status,'rejected');
  assert.ok(out.reasons.includes('invalid-collector-receipt'));
  assert.equal(out.nativeCorrelationDone,false);
});
