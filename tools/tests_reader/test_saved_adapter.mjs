import test from 'node:test';
import assert from 'node:assert/strict';
import crypto from 'node:crypto';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import {exportSavedSnapshot,summarizeSavedPins,readBoundedSaved,MAX_BYTES} from '../rre-reader-saved-snapshot.mjs';
import {parseSavedLua,parseSavedLuaBytes} from '../read-rrecollector-saved.mjs';

const source='RRECollectorData = {addonVersion="0.4.11",sequence=1,latest={addonVersion="0.1.0",sequence=1,captureComplete=true,abilityList={apiAvailable=true,enumerationComplete=true,detailFailures=0,ignored=0,truncated=0,uniqueCount=1,detailCount=1,rawEntries=1},player={id="uFIXTURE",name="Fixture",combat=false,power=0},roleSlot=1,roleNames={"One","Two"},frameTime=10,realTime=20,abilities={{lookupId="A0000000100000000",name="Fixture",target="uTARGET",passive=false,cooldown=0}}}}';
const read=s=>exportSavedSnapshot(Buffer.from(s));
const withPins = value=>source.replace('sequence=1,latest=', 'sequence=1,toolbarSlots='+value+',latest=');
const pinAudit = s=>summarizeSavedPins(Buffer.from(s));
test('pin audit treats absent slots as auto-defaults without changing the C# snapshot schema',()=>{
  const p=pinAudit(source), original=read(source);
  assert.equal(p.adapterContract,'rre-saved-pins/1');
  assert.equal(p.mode,'auto-defaults');assert.equal(p.savedField,'absent');
  assert.equal(p.pinCount,1);assert.equal(p.matchedCount,1);assert.equal(p.missingCount,0);
  assert.deepEqual(p.slotStates,['matched','empty','empty','empty','empty','empty','empty','empty']);
  assert.equal(p.captureVersion,'0.1.0');
  assert.equal(p.sourceSha256,original.sourceSha256);
  assert.equal(Object.hasOwn(original,'pinCount'),false);
  assert.equal(Object.hasOwn(original,'slotStates'),false);
});
test('explicit empty saved toolbar table does not activate default pins',()=>{
  const p=pinAudit(withPins('{}'));
  assert.equal(p.mode,'persisted');assert.equal(p.savedField,'table');
  assert.equal(p.pinCount,0);assert.equal(p.invalidCount,0);
  assert.deepEqual(p.slotStates,Array(8).fill('empty'));
});
test('sparse and dense toolbar slots distinguish matching and stale saved IDs',()=>{
  const good='A0000000100000000', stale='AFFFFFFFFFFFFFFFF';
  const sparse=pinAudit(withPins('{[1]="'+good+'",[3]="'+stale+'"}'));
  assert.equal(sparse.mode,'persisted');assert.equal(sparse.matchedCount,1);
  assert.equal(sparse.missingCount,1);assert.equal(sparse.invalidCount,0);
  assert.deepEqual(sparse.slotStates.slice(0,4),['matched','empty','missing','empty']);
  const dense=pinAudit(withPins('{"'+good+'","'+stale+'"}'));
  assert.deepEqual(dense.slotStates.slice(0,3),['matched','missing','empty']);
});
test('invalid persisted pin values are reported without discarding a qualified snapshot',()=>{
  const value=pinAudit(withPins('{[1]=false,[2]="'+('x'.repeat(129))+'",[3]="AFFFFFFFFFFFFFFFF"}'));
  assert.equal(value.invalidCount,2);assert.equal(value.missingCount,1);
  assert.deepEqual(value.slotStates.slice(0,4),['invalid','invalid','missing','empty']);
  const badRoot=pinAudit(withPins('"invalid"'));
  assert.equal(badRoot.mode,'auto-defaults');assert.equal(badRoot.savedField,'non-table');
  assert.equal(badRoot.matchedCount,1);
});
test('original saved-file read detects a concurrent change and bounds the input',()=>{
  const dir=fs.mkdtempSync(path.join(os.tmpdir(),'rre-rc44-saved-'));
  const file=path.join(dir,'RRECollector.lua');
  try {
    fs.writeFileSync(file,source);
    assert.deepEqual(readBoundedSaved(file),Buffer.from(source));
    const originalRead=fs.readSync;
    let changed=false;
    try {
      fs.readSync=function(...args) {
        const length=originalRead.apply(this,args);
        if (!changed) {
          changed=true;
          fs.appendFileSync(file,'-- changed during read');
        }
        return length;
      };
      assert.throws(()=>readBoundedSaved(file),/saved-source-changed-during-read/);
    } finally { fs.readSync=originalRead; }
    assert.equal(changed,true);
    fs.writeFileSync(file,Buffer.alloc(MAX_BYTES+1));
    assert.throws(()=>readBoundedSaved(file),/saved-byte-limit/);
  } finally { fs.rmSync(dir,{recursive:true,force:true}); }
});
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
  assert.throws(()=>read(source.replace('target="uTARGET"','target={}')),/ability-field-not-scalar/);
});
test('strict SavedVariables byte decoder rejects corrupt UTF-8',()=>{
  assert.equal(parseSavedLuaBytes(Buffer.from(source)).latest.abilities[0].target,'uTARGET');
  for (const bytes of [Buffer.from([0xff,0xfe]),Buffer.from([0xc3,0x28])]) {
    assert.throws(()=>parseSavedLuaBytes(bytes),/valid for encoding utf-8/i);
  }
});
test('bounds exact byte size and rejects invalid UTF8',()=>{
  assert.throws(()=>exportSavedSnapshot(Buffer.alloc(MAX_BYTES+1)),/byte-limit/);
  assert.throws(()=>exportSavedSnapshot(Buffer.from([0xff,0xfe])));
});
test('v0.4.14 Experience preserves partial finite values, zeros and explicit empty map',()=>{
  const base=source.replace('addonVersion="0.1.0"', 'addonVersion="0.4.14"');
  const make=(fields)=>base.replace('roleSlot=1,','capabilities={player=true,experience=true},experience={'+fields+'},roleSlot=1,');
  const received=read(make('accumulated=0,needed=1000'));
  assert.deepEqual({...received.context.experience},{accumulated:0,needed:1000});
  assert.equal(Object.hasOwn(received.context.experience,'rested'),false);
  assert.equal(received.context.capabilities.experience,true);
  assert.deepEqual({...read(make('')).context.experience},{});
  const unavailable=read(base.replace('roleSlot=1,','capabilities={player=true,experience=false},roleSlot=1,'));
  assert.equal(unavailable.context.capabilities.experience,false);
  assert.equal(Object.hasOwn(unavailable.context,'experience'),false);
});
test('v0.4.14 rejects Experience binding contradictions and incorrect scalar types',()=>{
  const base=source.replace('addonVersion="0.1.0"', 'addonVersion="0.4.14"');
  assert.throws(()=>read(base),/experience-capability/);
  assert.throws(()=>read(base.replace('roleSlot=1,','capabilities={player=true,experience=true},roleSlot=1,')),/experience-capability-map/);
  assert.throws(()=>read(base.replace('roleSlot=1,','capabilities={player=true,experience=false},experience={needed=10},roleSlot=1,')),/experience-capability-map/);
  for(const x of ['rested="1"','foo=5','rested=true','rested={}','accumulated=0/0']) {
    assert.throws(()=>read(base.replace('roleSlot=1,','capabilities={player=true,experience=true},experience={'+x+'},roleSlot=1,')));
  }
  assert.throws(()=>read(base.replace('roleSlot=1,','capabilities={player=true,experience=true},experience={1},roleSlot=1,')),/experience-map-shape/);
  assert.throws(()=>read(base.replace('roleSlot=1,','capabilities={player=true,experience=true},experience={accumulated=1,needed=2,rested=3,extra=4},roleSlot=1,')),/experience-map-limit/);
});
test('v0.4.15 Rogue Experience is retained with explicit capability binding',()=>{
  const base=source.replace('addonVersion="0.1.0"', 'addonVersion="0.4.15"');
  const complete=base.replace('roleSlot=1,','capabilities={player=true,experience=true},experience={accumulated=0,needed=42,rested=0},roleSlot=1,');
  const received=read(complete);
  assert.equal(received.addonVersion,'0.4.15');
  assert.deepEqual({...received.context.experience},{accumulated:0,needed:42,rested:0});
  assert.equal(received.context.capabilities.experience,true);
  assert.equal(received.abilities[0].lookupId,'A0000000100000000');
  assert.throws(()=>read(base),/experience-capability/);
});
test('v0.4.16 saved Experience supports Rogue and rejects missing capability',()=>{
  const base=source.replace('addonVersion="0.1.0"','addonVersion="0.4.16"');
  const input=base.replace('roleSlot=1,','capabilities={player=true,experience=true},experience={rested=0},roleSlot=1,');
  const output=read(input);
  assert.equal(output.addonVersion,'0.4.16');
  assert.deepEqual({...output.context.experience},{rested:0});
  assert.throws(()=>read(base),/experience-capability/);
});
test('v0.4.17 saved Experience preserves all-callings context and schema',()=>{
  const base=source.replace('addonVersion="0.1.0"','addonVersion="0.4.17"');
  const input=base.replace('roleSlot=1,','capabilities={player=true,experience=true},experience={accumulated=0,needed=42},roleSlot=1,');
  const output=read(input);
  assert.equal(output.addonVersion,'0.4.17');
  assert.deepEqual({...output.context.experience},{accumulated:0,needed:42});
  assert.throws(()=>read(base),/experience-capability/);
});
test('v0.4.18 saved Experience preserves Rogue context and rejects absent capability',()=>{
  const base=source.replace('addonVersion="0.1.0"','addonVersion="0.4.18"');
  const input=base.replace('roleSlot=1,','capabilities={player=true,experience=true},experience={needed=0,rested=42},roleSlot=1,');
  const output=read(input);
  assert.equal(output.addonVersion,'0.4.18');
  assert.deepEqual({...output.context.experience},{needed:0,rested:42});
  assert.equal(output.context.capabilities.experience,true);
  assert.throws(()=>read(base),/experience-capability/);
});
test('earlier versions reject Experience fields while retaining original parser behavior',()=>{
  assert.throws(()=>read(source.replace('roleSlot=1,','capabilities={player=true,experience=false},roleSlot=1,')),/experience-version-unqualified/);
  assert.throws(()=>read(source.replace('roleSlot=1,','experience={rested=0},roleSlot=1,')),/experience-version-unqualified/);
  assert.equal(read(source).addonVersion,'0.1.0');
});
test('rejects newline-suffixed IDs consistently at the data boundary',()=>{
  const malformed=source.replace('A0000000100000000','A0000000100000000\\n');
  assert.equal(Object.values(parseSavedLua(malformed).latest.abilities)[0].lookupId,'A0000000100000000\n');
  assert.throws(()=>read(malformed),/ability-id-unqualified|ABILITY_IDS_UNQUALIFIED/);
});
