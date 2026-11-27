// Static all-calling source index tests. Inputs are literal-only Lua tables.
import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {spawnSync} from 'node:child_process';
import {CALLINGS,inventoryStaticCandidates} from './inventory-pab-static-abilities.mjs';
import {parsePabSoulLiteral} from './parse-pab-soul-literal.mjs';
import {parseSavedLua} from './read-rrecollector-saved.mjs';
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
    assert.equal(out.schemaVersion,2);
    assert.equal(out.provenance.losslessDuplicateAbilityNames,true);
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
    assert.throws(()=>inventoryStaticCandidates(f.addon),/PAB_ABILITY_ID_OR_ICON/);
    f.set('Rogue','Sample','Valid',id(2));
    fs.writeFileSync(file,'ProjectAbilityBook_Souls_OTHER={["Abilities"]={}}');
    assert.throws(()=>inventoryStaticCandidates(f.addon),/PAB_ROOT_IDENTITY/);
    fs.writeFileSync(file,'ProjectAbilityBook_Souls_Sample={["Abilities"]={}};print("must never run")');
    assert.throws(()=>inventoryStaticCandidates(f.addon),/SOURCE_PARSE_FAILED/);
  }finally{f.cleanup();}
});
test('duplicate ability names preserve both IDs and original source line numbers',()=>{
  const f=fixture();
  try{
    const file=path.join(f.addon,'Callings','Rogue','Sample.lua');
    const original=[
      'ProjectAbilityBook_Souls_Sample={',
      '  ["Abilities"]={',
      '    ["1Builder"]={',
      '      ["Twice"]={["ID"]='+JSON.stringify(id(1))+',["Icon"]="x"},',
      '      -- the comment does not choose which ID is current',
      '      ["Twice"]={["ID"]='+JSON.stringify(id(2))+',["Icon"]="y"}',
      '    }',
      '  }',
      '}'
    ].join('\n');
    fs.writeFileSync(file,original);
    const out=inventoryStaticCandidates(f.addon);
    assert.equal(out.totals.abilityEntries,6);
    assert.equal(out.totals.duplicateNameGroups,1);
    assert.equal(out.totals.quarantinedFiles,0);
    assert.deepEqual(out.duplicateNames[0].occurrences,[
      {id:id(1),sourceLine:4,nameOccurrence:1},
      {id:id(2),sourceLine:6,nameOccurrence:2}
    ]);
    const rows=out.records.filter(r=>r.calling==='Rogue');
    assert.equal(rows.every(r=>r.duplicateName===true),true);
    assert.deepEqual(rows.map(r=>r.sourceLine),[4,6]);
    assert.equal(fs.readFileSync(file,'utf8'),original);
  }finally{f.cleanup();}
});
test('same category or ID field duplication still fails closed',()=>{
  const root='ProjectAbilityBook_Souls_Sample=';
  const dupCat=root+'{["Abilities"]={["B"]={},["B"]={}}}';
  assert.throws(()=>parsePabSoulLiteral(Buffer.from(dupCat),'Sample'),
    /PAB_CATEGORY_SHAPE_OR_DUPLICATE/);
  const dupField=root+'{["Abilities"]={["B"]={["X"]={["ID"]='+
    JSON.stringify(id(1))+',["ID"]='+JSON.stringify(id(2))+',["Icon"]="x"}}}}';
  assert.throws(()=>parsePabSoulLiteral(Buffer.from(dupField),'Sample'),
    /PAB_ABILITY_FIELD_SHAPE_OR_DUPLICATE/);
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
const sourceMode=process.env.RRE_PAB_TEST_MODE??'auto';
assert.ok(['auto','fixtures-only','source-required'].includes(sourceMode),'invalid PAB test mode');
// CI must not read an installed addon; local-source mode must not silently skip.
const sourceSkip=sourceMode==='fixtures-only'?'portable fixtures only':
  sourceMode==='auto'&&!fs.existsSync(liveRoot)?'original local source unavailable':false;

test('actual disabled source counts and preserved Warrior 96/96 exact IDs',
  {skip:sourceSkip},()=>{
  const out=inventoryStaticCandidates(liveRoot);
  assert.deepEqual(out.totals,{sourceFiles:56,parsedFiles:56,quarantinedFiles:0,
    abilityEntries:1434,uniqueIds:1433,duplicateIds:1,duplicateNameGroups:1});
  assert.deepEqual(out.quarantined,[]);
  assert.equal(out.sourceManifestSha256,
    '898f651e8fd272dc220fe0c32aecbb3e937dac750d6d9b912b1f94ab561eb5bb');
  const purifier=out.files.find(x=>x.path==='Callings/Cleric/Purifier.lua');
  assert.equal(purifier.status,'parsed');
  assert.equal(purifier.entries,29);
  assert.equal(purifier.sha256,
    'fbcdf9383c93204c976dc526b126fe6b49c677aa169e87f25fc13b1aefa4835c');
  assert.deepEqual(out.duplicateNames,[{
    calling:'Cleric',soul:'Purifier',
    sourcePath:'Callings/Cleric/Purifier.lua',
    category:'2Damage',name:'Flame Lance',
    occurrences:[
      {id:'A060ED54D21F2B259',sourceLine:18,nameOccurrence:1},
      {id:'A1A35B21D4891044E',sourceLine:22,nameOccurrence:2}
    ]
  }]);
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
  // Independently compare all 55 previously accepted literal-table files
  // against the historical strict SavedVariables reader's exact field values.
  let compared=0;
  for(const f of out.files){
    if(f.path==='Callings/Cleric/Purifier.lua')continue;
    const original=fs.readFileSync(path.join(liveRoot,f.path),'utf8');
    const normalized=original.replace(/^ProjectAbilityBook_Souls_[A-Za-z0-9_]+\s*=/,
      'RRECollectorData =');
    assert.notEqual(normalized,original);
    const older=parseSavedLua(normalized);
    const expected=[];
    for(const [cat,group] of Object.entries(older.Abilities))
      for(const [name,v] of Object.entries(group))
        expected.push([cat,name,v.ID,v.Icon].join('|'));
    const actual=out.records.filter(r=>r.sourcePath===f.path)
      .map(r=>[r.category,r.name,r.id,r.icon].join('|'));
    assert.deepEqual(actual.sort(),expected.sort(),f.path);
    compared++;
  }
  assert.equal(compared,55);
});
test('generated v2 artifact exactly reproduces all original source rows and provenance',
  {skip:sourceSkip},()=>{
  const saved=JSON.parse(fs.readFileSync(path.join(root,
    'docs/RRECOLLECTOR-ALL-CALLINGS-STATIC-CANDIDATES-LOSSLESS-2026-11-21.json')));
  const live=inventoryStaticCandidates(liveRoot);
  assert.deepEqual(saved,live);
  assert.equal(saved.schemaVersion,2);
  assert.equal(saved.duplicateNames.length,1);
  assert.equal(saved.records.filter(r=>r.duplicateName===true).length,2);
  assert.equal(saved.records.filter(r=>r.sourcePath==='Callings/Cleric/Purifier.lua').length,29);
});
