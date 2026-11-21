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
    const value='RRECollectorData = {addonVersion='+JSON.stringify(rootVersion)+
      ',latest={addonVersion='+JSON.stringify(latest)+
      ',sequence=3,captureComplete=true,abilities={{lookupId="A0000000000000001"}}},'+
      'memoryPublication={status="complete"},captureAttempt={addonVersion="0.4.23",status="accepted"},'+
      (units?'unitSnapshotSequence=1,unitAttempt={addonVersion="0.4.23",status="complete"},':'')+
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
