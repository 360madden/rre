import test from 'node:test';
import assert from 'node:assert/strict';
import crypto from 'node:crypto';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import {spawnSync} from 'node:child_process';
import {exportSavedSnapshot,summarizeSavedPins,readBoundedSaved,savedCliErrorReason,MAX_BYTES} from '../rre-reader-saved-snapshot.mjs';
import {parseSavedLua,parseSavedLuaBytes} from '../read-rrecollector-saved.mjs';
import {readStableOriginalWithMetadata} from '../read-stable-original.mjs';
import {buildLiveAtlas} from '../build-rift-ability-atlas-live.mjs';

const source='RRECollectorData = {addonVersion="0.4.11",sequence=1,latest={addonVersion="0.1.0",sequence=1,captureComplete=true,abilityList={apiAvailable=true,enumerationComplete=true,detailFailures=0,ignored=0,truncated=0,uniqueCount=1,detailCount=1,rawEntries=1},player={id="uFIXTURE",name="Fixture",combat=false,power=0},roleSlot=1,roleNames={"One","Two"},frameTime=10,realTime=20,abilities={{lookupId="A0000000100000000",name="Fixture",target="uTARGET",passive=false,cooldown=0}}}}';
const read=s=>exportSavedSnapshot(Buffer.from(s));
const withPins = value=>source.replace('sequence=1,latest=', 'sequence=1,toolbarSlots='+value+',latest=');
const pinAudit = s=>summarizeSavedPins(Buffer.from(s));

test('SavedSource accepts RIFT shared player tables while preserving raw SHA and false/zero', () => {
  const header = 'local ref = {}\nfor k=1,1 do ref[k] = {} end\n'
    + 'ref[1].id="uFIXTURE"\nref[1].name="Fixture"\nref[1].combat=false\nref[1].power=0\n';
  const shared = header + source.replace('RRECollectorData = {', 'RRECollectorData = {alias=ref[1],')
    .replace('player={id="uFIXTURE",name="Fixture",combat=false,power=0}', 'player=ref[1]');
  const result = read(shared);
  assert.equal(result.sourceSha256, crypto.createHash('sha256').update(Buffer.from(shared)).digest('hex'));
  assert.equal(result.context.player.combat, false); assert.equal(result.context.player.power, 0);
  assert.equal(result.abilities[0].target, 'uTARGET');
  assert.equal(result.structure.offlineStructureQualified, true);
});
test('saved-file CLI hides path details on errors and preserves --pins success',()=>{
  const script=path.resolve('tools/rre-reader-saved-snapshot.mjs');
  const dir=fs.mkdtempSync(path.join(os.tmpdir(),'rre-rc46-cli-'));
  const marker='private@example.invalid';
  const missing=path.join(dir,marker,'RRECollector.lua');
  const run=file=>spawnSync(process.execPath,[script,file,'--pins'],{encoding:'utf8'});
  try {
    const absent=run(missing);
    assert.equal(absent.error,undefined);
    assert.equal(absent.status,2);
    assert.equal(absent.stdout,'');
    assert.deepEqual(JSON.parse(absent.stderr),{error:'saved-file-not-found'});
    assert.equal(absent.stderr.includes(marker),false);
    assert.equal(absent.stderr.includes(missing),false);
    const file=path.join(dir,'RRECollector.lua');
    fs.writeFileSync(file,'RRECollectorData = { private = "'+marker+'", -- invalid Lua source\n');
    const malformed=run(file);
    assert.equal(malformed.status,2);
    assert.equal(malformed.stdout,'');
    assert.equal(JSON.parse(malformed.stderr).error,'saved-input-invalid');
    assert.equal(malformed.stderr.includes(marker),false);
    fs.writeFileSync(file,source);
    const valid=run(file);
    assert.equal(valid.status,0);
    assert.equal(valid.stderr,'');
    assert.deepEqual(JSON.parse(valid.stdout),pinAudit(source));
    assert.equal(savedCliErrorReason(new Error('saved-source-changed-during-read')),'saved-source-changed-during-read');
    assert.equal(savedCliErrorReason(new Error('sensitive: '+missing)),'saved-input-invalid');
  } finally { fs.rmSync(dir,{recursive:true,force:true}); }
});
test('legacy saved crosswalk CLI redacts path and parser failures',()=>{
  const script=path.resolve('tools/read-rrecollector-saved.mjs');
  const dir=fs.mkdtempSync(path.join(os.tmpdir(),'rre-rc48-cli-'));
  const marker='private@example.invalid';
  const missing=path.join(dir,marker,'RRECollector.lua');
  const staticFile=path.join(dir,'static.json');
  const run=file=>spawnSync(process.execPath,[script,file,staticFile],{encoding:'utf8'});
  try {
    fs.writeFileSync(staticFile,JSON.stringify({catalogVersion:'test-only',records:[]}));
    const absent=run(missing);
    assert.equal(absent.error,undefined);
    assert.equal(absent.status,2);
    assert.equal(absent.stdout,'');
    assert.deepEqual(JSON.parse(absent.stderr),{error:'saved-file-not-found'});
    assert.equal(absent.stderr.includes(marker),false);
    assert.equal(absent.stderr.includes(missing),false);
    const file=path.join(dir,'RRECollector.lua');
    fs.writeFileSync(file,'RRECollectorData = { leaked = "'+marker+'", -- invalid Lua source\n');
    const invalid=run(file);
    assert.equal(invalid.status,2);
    assert.equal(invalid.stdout,'');
    assert.deepEqual(JSON.parse(invalid.stderr),{error:'saved-input-invalid'});
    assert.equal(invalid.stderr.includes(marker),false);
    fs.writeFileSync(file,source);
    const valid=run(file);
    assert.equal(valid.status,0);
    assert.equal(valid.stderr,'');
    const parsed=JSON.parse(valid.stdout);
    assert.equal(parsed.savedSha256,crypto.createHash('sha256').update(source).digest('hex'));
    assert.equal(parsed.counts.knownApi,1);
    assert.equal(parsed.counts.staticCandidates,0);
  } finally { fs.rmSync(dir,{recursive:true,force:true}); }
});
test('shared original reader returns stable bytes and timestamp and rejects races/oversize',()=>{
  const dir=fs.mkdtempSync(path.join(os.tmpdir(),'rre-rc49-stable-'));
  const file=path.join(dir,'RRECollector.lua');
  try {
    fs.writeFileSync(file,source);
    const stable=readStableOriginalWithMetadata(file);
    assert.deepEqual(stable.bytes,Buffer.from(source));
    assert.equal(stable.modifiedAtUtc,fs.statSync(file).mtime.toISOString());
    const originalRead=fs.readSync;
    let changed=false;
    try {
      fs.readSync=function(...args) {
        const count=originalRead.apply(this,args);
        if (!changed) {
          changed=true;
          fs.appendFileSync(file,'-- concurrent modification');
        }
        return count;
      };
      assert.throws(()=>readStableOriginalWithMetadata(file),/saved-source-changed-during-read/);
    } finally { fs.readSync=originalRead; }
    assert.equal(changed,true);
    fs.writeFileSync(file,Buffer.alloc(MAX_BYTES+1));
    assert.throws(()=>readStableOriginalWithMetadata(file),/saved-byte-limit/);
  } finally { fs.rmSync(dir,{recursive:true,force:true}); }
});
test('shared original reader detects same-size mutation while reading',()=>{
  const dir=fs.mkdtempSync(path.join(os.tmpdir(),'rre-rc50-same-size-'));
  const file=path.join(dir,'RRECollector.lua');
  const originalRead=fs.readSync;
  let changed=false;
  try {
    fs.writeFileSync(file,source);
    fs.readSync=function(...args) {
      const count=originalRead.apply(this,args);
      if (!changed) {
        changed=true;
        fs.writeFileSync(file,Buffer.alloc(Buffer.byteLength(source),0x58));
        const future=new Date(Date.now()+60_000);
        fs.utimesSync(file,future,future);
      }
      return count;
    };
    assert.throws(()=>readStableOriginalWithMetadata(file),/saved-source-changed-during-read/);
    assert.equal(changed,true);
  } finally {
    fs.readSync=originalRead;
    fs.rmSync(dir,{recursive:true,force:true});
  }
});
test('live atlas refuses lowercase and case-colliding exact ability IDs',()=>{
  const saved=parseSavedLuaBytes(Buffer.from(source));
  const base={saved,savedSha256:crypto.createHash('sha256').update(source).digest('hex'),
    originalThree:{catalogVersion:'fixture',records:[]},allWarrior:{records:[]}};
  const record=id=>({id,name:'Case fixture',priorKnownApiList:'listed-in-preserved-69'});
  const upper='A0123456789ABCDEF', lower='a0123456789abcdef';
  assert.throws(()=>buildLiveAtlas({...base,priorAtlas:{records:[record(lower)]}}),
    /prior atlas has invalid\/duplicate exact ID/);
  assert.throws(()=>buildLiveAtlas({...base,priorAtlas:{records:[record(upper),record(lower)]}}),
    /prior atlas has invalid\/duplicate exact ID/);
});
test('atlas CLI rejects private paths and preserves exclusive successful output',()=>{
  const script=path.resolve('tools/build-rift-ability-atlas-live.mjs');
  const dir=fs.mkdtempSync(path.join(os.tmpdir(),'rre-rc49-atlas-'));
  const output=path.join(dir,'atlas.json');
  const marker='private@example.invalid';
  const missing=path.join(dir,marker,'RRECollector.lua');
  const run=file=>spawnSync(process.execPath,[script,file,output],{encoding:'utf8'});
  try {
    const absent=run(missing);
    assert.equal(absent.error,undefined);
    assert.equal(absent.status,2);
    assert.equal(absent.stdout,'');
    assert.deepEqual(JSON.parse(absent.stderr),{error:'saved-file-not-found'});
    assert.equal(absent.stderr.includes(marker),false);
    assert.equal(fs.existsSync(output),false);
    const file=path.join(dir,'RRECollector.lua');
    fs.writeFileSync(file,source);
    const valid=run(file);
    assert.equal(valid.status,0);
    assert.equal(valid.stderr,'');
    const receipt=JSON.parse(valid.stdout), atlas=JSON.parse(fs.readFileSync(output,'utf8'));
    assert.equal(receipt.savedSha256,crypto.createHash('sha256').update(source).digest('hex'));
    assert.equal(atlas.schemaVersion,1);
    assert.equal(atlas.savedFileModifiedUtc,fs.statSync(file).mtime.toISOString());
    assert.equal(receipt.counts.exactIds,atlas.counts.exactIds);
    const previouslyWritten=fs.readFileSync(output);
    const duplicate=run(file);
    assert.equal(duplicate.status,2);
    assert.deepEqual(JSON.parse(duplicate.stderr),{error:'saved-input-invalid'});
    assert.deepEqual(fs.readFileSync(output),previouslyWritten);
  } finally { fs.rmSync(dir,{recursive:true,force:true}); }
});
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
test('v0.4.19 saved Experience preserves existing contract and rejects missing capability',()=>{
  const base=source.replace('addonVersion="0.1.0"','addonVersion="0.4.19"');
  const input=base.replace('roleSlot=1,','capabilities={player=true,experience=true},experience={accumulated=0,needed=78},roleSlot=1,');
  const output=read(input);
  assert.equal(output.addonVersion,'0.4.19');
  assert.deepEqual({...output.context.experience},{accumulated:0,needed:78});
  assert.throws(()=>read(base),/experience-capability/);
});
test('v0.4.20 saved Experience retains prior contracts and rejects missing capability',()=>{
  const base=source.replace('addonVersion="0.1.0"','addonVersion="0.4.20"');
  const input=base.replace('roleSlot=1,','capabilities={player=true,experience=true},experience={accumulated=0,needed=78},roleSlot=1,');
  const output=read(input);
  assert.equal(output.addonVersion,'0.4.20');
  assert.deepEqual({...output.context.experience},{accumulated:0,needed:78});
  assert.throws(()=>read(base),/experience-capability/);
});
test('v0.4.21 diagnostics release preserves Experience and retained producer provenance',()=>{
  const base=source.replace('addonVersion="0.4.11"','addonVersion="0.4.21"')
    .replace('addonVersion="0.1.0"','addonVersion="0.4.21"');
  const input=base.replace('roleSlot=1,','capabilities={player=true,experience=true},experience={accumulated=0,needed=78},roleSlot=1,');
  assert.equal(read(input).addonVersion,'0.4.21');
  assert.deepEqual({...read(input).context.experience},{accumulated:0,needed:78});
  const retained=read(input.replace('latest={addonVersion="0.4.21"','latest={addonVersion="0.4.20"'));
  assert.equal(retained.savedAddonVersion,'0.4.21'); assert.equal(retained.addonVersion,'0.4.20');
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
