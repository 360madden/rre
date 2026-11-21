// Real source + disposable copied package: no physical RIFT writes, calls or reload.
import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {spawnSync} from 'node:child_process';
import {inspectCollectorReadiness} from './audit-rrecollector-readiness.mjs';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const source=path.join(root,'addons','RRECollector');
const allFiles=['core.lua','context.lua','abilities.lua','capabilities.lua',
  'candidate_catalog.lua','candidates.lua','wire.lua','units.lua','ui.lua','main.lua',
  'README.md','RiftAddon.toc'];
function fixture() {
  const tmp=fs.mkdtempSync(path.join(os.tmpdir(),'rre-readiness-'));
  const installed=path.join(tmp,'AddOns','RRECollector');
  const saved=path.join(tmp,'SavedVariables','RRECollector.lua');
  fs.mkdirSync(installed,{recursive:true});
  fs.mkdirSync(path.dirname(saved),{recursive:true});
  for(const name of allFiles)fs.copyFileSync(path.join(source,name),path.join(installed,name));
  function setSaved(rootVersion='0.4.23',latest='0.4.23',units=true){
    const witness=units ? 'unitSnapshotSequence=1,unitSnapshots={{schemaVersion=1,'+
      'addonVersion="0.4.23",scope="manual-bounded-unit-api-witness",'+
      'status="empty",reason="no-nonself-listed",sequence=1,'+
      'limits={listEntries=128,detailCalls=8},'+
      'counts={examined=0,invalidEntries=0,selfEntries=0,nonselfEligible=0,'+
      'detailsCalled=0,detailErrors=0,idMismatches=0,idMissing=0,qualifiedXYZ=0},'+
      'records={},listEnumerationComplete=true,detailSampleComplete=true,'+
      'coordinateFrameVerified=false,nativeIdentityVerified=false,atomicSnapshot=false,'+
      'selfId="u0000000000000001"}},'+
      'unitAttempt={schemaVersion=1,addonVersion="0.4.23",attemptSequence=1,'+
      'status="empty",reason="no-nonself-listed",resultSequence=1},' : '';
    const value='RRECollectorData = {addonVersion='+JSON.stringify(rootVersion)+
      ',latest={addonVersion='+JSON.stringify(latest)+
      ',sequence=3,captureComplete=true,abilities={{lookupId="A0000000000000001"}}},'+
      'memoryPublication={status="complete"},captureAttempt={addonVersion="0.4.23",status="accepted"},'+
      witness+
      'sequence=3}';
    fs.writeFileSync(saved,value);
  }
  setSaved();
  return {tmp,installed,saved,setSaved,cleanup:()=>fs.rmSync(tmp,{recursive:true,force:true})};
}
test('same source/install bytes and persisted producer version are not runtime load proof',()=>{
  const f=fixture();
  try{
    const result=inspectCollectorReadiness(f.installed,f.saved);
    assert.equal(result.sourceVersion,'0.4.23');
    assert.equal(result.install.matchedCount,12);
    assert.deepEqual(result.install.changed,[]);
    assert.deepEqual(result.install.missing,[]);
    assert.equal(result.checks.sourceInstalledByteIdentical,true);
    assert.equal(result.checks.acceptedUnitsPresent,true);
    assert.equal(result.checks.acceptedUnitsComplete,false);
    assert.equal(result.saved.unitValidation.latestStatus,'empty');
    assert.equal(result.saved.unitValidation.status,'validated');
    assert.equal(result.limits.activeLuaLoadVerified,false);
    assert.equal(result.limits.liveRrec2TransferVerified,false);
    assert.equal(result.limits.wa006Accepted,false);
  }finally{f.cleanup();}
});
test('older installed package and older accepted capture remain distinct',()=>{
  const f=fixture();
  try{
    for(const name of ['RiftAddon.toc','core.lua']){
      const filename=path.join(f.installed,name);
      fs.writeFileSync(filename,fs.readFileSync(filename,'utf8').replaceAll('0.4.23','0.4.21'));
    }
    fs.unlinkSync(path.join(f.installed,'units.lua'));
    f.setSaved('0.4.21','0.4.20',false);
    const result=inspectCollectorReadiness(f.installed,f.saved);
    assert.equal(result.sourceVersion,'0.4.23');
    assert.equal(result.installedVersion,'0.4.21');
    assert.equal(result.saved.rootVersion,'0.4.21');
    assert.equal(result.saved.acceptedAbilityVersion,'0.4.20');
    assert.equal(result.checks.sourceInstalledByteIdentical,false);
    assert.equal(result.checks.acceptedAbilityMatchesSource,false);
    assert.ok(result.install.missing.includes('units.lua'));
    assert.ok(result.install.changed.includes('RiftAddon.toc'));
    assert.equal(result.checks.acceptedUnitsPresent,false);
  }finally{f.cleanup();}
});
test('new root version with older good ability capture is not a fresh capture',()=>{
  const f=fixture();
  try{
    f.setSaved('0.4.23','0.4.20',false);
    const result=inspectCollectorReadiness(f.installed,f.saved);
    assert.equal(result.checks.sourceInstalledByteIdentical,true);
    assert.equal(result.checks.savedRootMatchesSource,true);
    assert.equal(result.checks.acceptedAbilityMatchesSource,false);
    assert.equal(result.checks.acceptedUnitsPresent,false);
    assert.equal(result.saved.unitValidation.status,'absent');
    assert.equal(result.limits.activeLuaLoadVerified,false);
  }finally{f.cleanup();}
});
test('first unavailable unit attempt is a valid failure, not a corrupt snapshot',()=>{
  const f=fixture();
  try{
    f.setSaved('0.4.23','0.4.20',false);
    const original=fs.readFileSync(f.saved,'utf8');
    fs.writeFileSync(f.saved,original.replace('sequence=3}',
      'unitAttempt={schemaVersion=1,addonVersion="0.4.23",attemptSequence=1,'+
      'status="unavailable",reason="missing-unit-api"},sequence=3}'));
    const result=inspectCollectorReadiness(f.installed,f.saved);
    assert.equal(result.saved.unitValidation.status,'attempt-only');
    assert.equal(result.saved.unitValidation.lastAttemptStatus,'unavailable');
    assert.equal(result.saved.unitValidation.reason,'missing-unit-api');
    assert.equal(result.saved.unitValidation.retainedCount,0);
    assert.equal(result.checks.acceptedUnitsPresent,false);
    assert.equal(result.checks.acceptedUnitsComplete,false);
    assert.equal(result.checks.savedRootMatchesSource,true);
  }finally{f.cleanup();}
});
test('first exception attempt is retained, but forged positive attempt is rejected',()=>{
  const f=fixture();
  try{
    f.setSaved('0.4.23','0.4.20',false);
    const original=fs.readFileSync(f.saved,'utf8');
    const error=original.replace('sequence=3}',
      'unitAttempt={schemaVersion=1,addonVersion="0.4.23",attemptSequence=3,'+
      'status="error",reason="unit-capture-exception"},sequence=3}');
    fs.writeFileSync(f.saved,error);
    const accepted=inspectCollectorReadiness(f.installed,f.saved);
    assert.equal(accepted.saved.unitValidation.status,'attempt-only');
    assert.equal(accepted.saved.unitValidation.lastAttemptStatus,'error');
    assert.equal(accepted.checks.acceptedUnitsPresent,false);
    fs.writeFileSync(f.saved,error.replace('status="error"','status="complete"'));
    const forged=inspectCollectorReadiness(f.installed,f.saved);
    assert.equal(forged.saved.unitValidation.status,'rejected');
    assert.equal(forged.checks.acceptedUnitsPresent,false);
  }finally{f.cleanup();}
});
test('positive unit sequence alone is not a validated snapshot',()=>{
  const f=fixture();
  try{
    f.setSaved('0.4.23','0.4.20',false);
    fs.writeFileSync(f.saved,fs.readFileSync(f.saved,'utf8')
      .replace(/}$/,',unitSnapshotSequence=7}'));
    const result=inspectCollectorReadiness(f.installed,f.saved);
    assert.equal(result.saved.acceptedUnitSequence,7);
    assert.equal(result.saved.unitValidation.status,'rejected');
    assert.equal(result.saved.unitValidation.reason,'UNIT_SEQUENCE_FIELDS');
    assert.equal(result.checks.acceptedUnitsPresent,false);
    assert.equal(result.checks.acceptedUnitsComplete,false);
  }finally{f.cleanup();}
});
test('TOC and core version contradiction fails closed',()=>{
  const f=fixture();
  try{
    const file=path.join(f.installed,'RiftAddon.toc');
    fs.writeFileSync(file,fs.readFileSync(file,'utf8').replace('0.4.23','0.4.22'));
    assert.throws(()=>inspectCollectorReadiness(f.installed,f.saved),/TOC_CORE_VERSION_MISMATCH/);
  }finally{f.cleanup();}
});
test('paths cannot silently point to another installed addon or saved-data name',()=>{
  const f=fixture();
  try{
    assert.throws(()=>inspectCollectorReadiness(f.tmp,f.saved),/INSTALL_DIRECTORY_CONTRACT/);
    assert.throws(()=>inspectCollectorReadiness(f.installed,path.join(f.tmp,'other.lua')),
      /SAVED_FILENAME_CONTRACT/);
  }finally{f.cleanup();}
});
test('CLI reports usage failure without reading game or modifying files',()=>{
  const file=fileURLToPath(new URL('./audit-rrecollector-readiness.mjs',import.meta.url));
  const p=spawnSync(process.execPath,[file],{encoding:'utf8',timeout:5000});
  assert.equal(p.status,2);
  assert.match(p.stderr,/USAGE_INSTALLED_DIR_SAVED_FILE/);
});
