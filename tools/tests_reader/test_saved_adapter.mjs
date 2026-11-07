import test from 'node:test';
import assert from 'node:assert/strict';
import crypto from 'node:crypto';
import {exportSavedSnapshot,MAX_BYTES} from '../rre-reader-saved-snapshot.mjs';
import {parseSavedLua} from '../read-rrecollector-saved.mjs';

const source='RRECollectorData = {addonVersion="0.4.11",sequence=1,latest={addonVersion="0.1.0",sequence=1,captureComplete=true,abilityList={apiAvailable=true,enumerationComplete=true,detailFailures=0,ignored=0,truncated=0,uniqueCount=1,detailCount=1,rawEntries=1},player={id="uFIXTURE",name="Fixture",combat=false,power=0},roleSlot=1,roleNames={"One","Two"},frameTime=10,realTime=20,abilities={{lookupId="A0000000100000000",name="Fixture",target="uTARGET",passive=false,cooldown=0}}}}';
const read=s=>exportSavedSnapshot(Buffer.from(s));
test('preserves separate saved-root and capture versions',()=>{
  const x=read(source);assert.equal(x.addonVersion,'0.1.0');assert.equal(x.savedAddonVersion,'0.4.11');
});
test('preserves producer target, zero and false without changing legacy crosswalk',()=>{
  const x=read(source);assert.equal(x.abilities[0].target,'uTARGET');assert.equal(x.abilities[0].passive,false);assert.equal(x.abilities[0].cooldown,0);
});
test('preserves context arrays, nested false/zero and missing unknowns',()=>{
  const x=read(source);assert.deepEqual(x.context.roleNames,['One','Two']);assert.equal(x.context.player.combat,false);assert.equal(x.context.player.power,0);assert.equal(Object.hasOwn(x.context.player,'zone'),false);
});
test('binds exact input bytes and never upgrades single-file evidence',()=>{
  const bytes=Buffer.from(source);const x=exportSavedSnapshot(bytes);assert.equal(x.sourceBytes,bytes.length);assert.equal(x.sourceSha256,crypto.createHash('sha256').update(bytes).digest('hex'));
  for(const key of ['freshnessVerified','processBuildVerified','eventDeliveryVerified','eventComparisonReady'])assert.equal(x.structure[key],false);
});
test('rejects expression, duplicate keys and wrong assignment',()=>{
  for(const s of ['RRECollectorData=os.execute("never")','RRECollectorData={latest={},latest={}}','Other={}'])assert.throws(()=>read(s));
});
test('rejects incomplete and count-contradictory catalog',()=>{
  assert.throws(()=>read(source.replace('captureComplete=true','captureComplete=false')));
  assert.throws(()=>read(source.replace('detailCount=1','detailCount=2')));
});
test('rejects unsupported target shape rather than losing data silently',()=>{
  assert.throws(()=>read(source.replace('target="uTARGET"','target={}')),/target-not-scalar/);
});
test('bounds exact byte size and rejects invalid UTF8',()=>{
  assert.throws(()=>exportSavedSnapshot(Buffer.alloc(MAX_BYTES+1)),/byte-limit/);
  assert.throws(()=>exportSavedSnapshot(Buffer.from([0xff,0xfe])));
});
test('rejects newline-suffixed IDs consistently at the data boundary',()=>{
  const malformed=source.replace('A0000000100000000','A0000000100000000\\n');
  assert.equal(Object.values(parseSavedLua(malformed).latest.abilities)[0].lookupId,'A0000000100000000\n');
  assert.throws(()=>read(malformed),/ability-id-unqualified|ABILITY_IDS_UNQUALIFIED/);
});
