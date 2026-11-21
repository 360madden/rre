// Static all-calling source index tests. Inputs are literal-only Lua tables.
import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {spawnSync} from 'node:child_process';
import {CALLINGS,inventoryStaticCandidates} from './inventory-pab-static-abilities.mjs';
const here=path.dirname(fileURLToPath(import.meta.url));
const root=path.resolve(here,'..');
const id=n=>'A'+n.toString(16).toUpperCase().padStart(16,'0');
function fixture(){
  const tmp=fs.mkdtempSync(path.join(os.tmpdir(),'rre-pab-static-'));
  const addon=path.join(tmp,'projectabilitybook.disabled');
  for(const calling of CALLINGS)fs.mkdirSync(path.join(addon,'Callings',calling),{recursive:true});
  const set=(calling,soul,name,abilityId=id(2))=>{
    const text='ProjectAbilityBook_Souls_'+soul+' = {["Abilities"]={["1Builder"]={'+
      '['+JSON.stringify(name)+']={["Icon"]="Data/icons/x.dds",["ID"]='+JSON.stringify(abilityId)+'}}}}';
    const file=path.join(addon,'Callings',calling,soul+'.lua');
    fs.writeFileSync(file,text,'utf8');
    return file;
  };
  CALLINGS.forEach((calling,i)=>set(calling,'Sample','Spell '+calling,id(i+1)));
  return {tmp,addon,set,cleanup:()=>fs.rmSync(tmp,{recursive:true,force:true})};
}
test('all five callings indexed without executing source Lua',()=>{
  const f=fixture();
  try{
    const out=inventoryStaticCandidates(f.addon);
    assert.equal(out.totals.sourceFiles,5);
    assert.equal(out.totals.parsedFiles,5);
    assert.equal(out.totals.abilityEntries,5);
    assert.equal(out.totals.uniqueIds,5);
    assert.equal(out.totals.quarantinedFiles,0);
    assert.equal(out.provenance.luaExecuted,false);
    assert.equal(out.provenance.castabilityVerified,false);
    assert.ok(out.sourceManifestSha256.match(/^[a-f0-9]{64}$/));
    assert.equal(out.files.every(f=>/^[a-f0-9]{64}$/.test(f.sha256)),true);
  }finally{f.cleanup();}
});
test('cross-calling repeated exact ID retains both source owners',()=>{
  const f=fixture();
  try{
    f.set('Rogue','Sample','Shared Spell',id(1));
    const out=inventoryStaticCandidates(f.addon);
    assert.equal(out.totals.abilityEntries,5);
    assert.equal(out.totals.uniqueIds,4);
    assert.equal(out.totals.duplicateIds,1);
    assert.equal(out.duplicateIds[0].occurrences.length,2);
    assert.deepEqual(out.duplicateIds[0].occurrences.map(r=>r.calling),['Cleric','Rogue']);
  }finally{f.cleanup();}
});
test('source ID, root, and any executable expression are rejected',()=>{
  const f=fixture();
  try{
    const file=f.set('Rogue','Sample','Bad Spell','A_NOTANID');
    assert.throws(()=>inventoryStaticCandidates(f.addon),/SOURCE_ABILITY_ENTRY/);
    f.set('Rogue','Sample','Valid',id(2));
    fs.writeFileSync(file,'ProjectAbilityBook_Souls_OTHER={["Abilities"]={}}');
    assert.throws(()=>inventoryStaticCandidates(f.addon),/SOURCE_ROOT_IDENTITY/);
    fs.writeFileSync(file,'ProjectAbilityBook_Souls_Sample={["Abilities"]={}};print("must never run")');
    assert.throws(()=>inventoryStaticCandidates(f.addon),/SOURCE_PARSE_FAILED/);
  }finally{f.cleanup();}
});
test('unrecognized duplicate table key does not silently overwrite',()=>{
  const f=fixture();
  try{
    const file=path.join(f.addon,'Callings','Rogue','Sample.lua');
    const prefix='ProjectAbilityBook_Souls_Sample={["Abilities"]={["1Builder"]={';
    fs.writeFileSync(file,prefix+'["Twice"]={["ID"]='+JSON.stringify(id(1))+
      ',["Icon"]="x"},["Twice"]={["ID"]='+JSON.stringify(id(2))+
      ',["Icon"]="y"}}}}');
    assert.throws(()=>inventoryStaticCandidates(f.addon),/duplicate Lua table key/);
  }finally{f.cleanup();}
});
test('incorrect install root and missing directories are rejected',()=>{
  const f=fixture();
  try{
    assert.throws(()=>inventoryStaticCandidates(f.tmp),/SOURCE_ROOT_DIRECTORY/);
    fs.rmSync(path.join(f.addon,'Callings','Mage'),{recursive:true});
    assert.throws(()=>inventoryStaticCandidates(f.addon),/ENOENT/);
  }finally{f.cleanup();}
});
test('CLI usage fails without printing an invented partial catalog',()=>{
  const cli=path.join(here,'inventory-pab-static-abilities.mjs');
  const result=spawnSync(process.execPath,[cli],{encoding:'utf8',timeout:5000});
  assert.equal(result.status,1);
  assert.match(result.stderr,/USAGE_SOURCE_ROOT_OPTIONAL_OUTPUT/);
  assert.equal(result.stdout,'');
});
const liveRoot=process.env.RRE_PAB_ROOT||path.join(process.env.USERPROFILE||'',
  'OneDrive','Documents','RIFT','Interface','AddOns','projectabilitybook.disabled');
test('actual disabled source counts and preserved Warrior 96/96 exact IDs',
  {skip:!fs.existsSync(liveRoot)},()=>{
  const out=inventoryStaticCandidates(liveRoot);
  assert.deepEqual(out.totals,{sourceFiles:56,parsedFiles:55,quarantinedFiles:1,
    abilityEntries:1405,uniqueIds:1404,duplicateIds:1});
  assert.equal(out.quarantined[0].path,'Callings/Cleric/Purifier.lua');
  assert.equal(out.quarantined[0].sha256,
    'fbcdf9383c93204c976dc526b126fe6b49c677aa169e87f25fc13b1aefa4835c');
  assert.equal(out.duplicateIds[0].id,'A40C51A65DBA71310');
  assert.deepEqual(out.duplicateIds[0].occurrences.map(r=>r.calling),['Cleric','Rogue']);
  const historic=JSON.parse(fs.readFileSync(path.join(root,
    'docs/REA-RIFT-SPELLCASTING-SC103-WARRIOR-STATIC-ABILITIES-2026-11-02.json')));
  const selected=new Set(['Paladin','VoidKnight','Paragon']);
  const current=out.records.filter(r=>r.calling==='Warrior'&&selected.has(r.soul));
  assert.equal(current.length,96);
  const keys=rows=>rows.map(r=>[r.id,r.name,r.category,r.soul].join('|')).sort();
  assert.deepEqual(keys(current),keys(historic.records));
  for(const src of historic.sourceFiles){
    const matching=out.files.find(x=>x.path.endsWith('/'+src.soul+'.lua')
      && x.path.startsWith('Callings/Warrior/'));
    assert.equal(matching.sha256,src.sha256);
  }
});
