import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import test from "node:test";
import { fileURLToPath } from "node:url";
import { buildLiveAtlas } from "./build-rift-ability-atlas-live.mjs";

const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),"..");
const load=p=>JSON.parse(fs.readFileSync(path.join(root,p),"utf8"));
const originalThree=load("docs/REA-RIFT-SPELLCASTING-SC103-WARRIOR-STATIC-ABILITIES-2026-11-02.json");
const allWarrior=load("docs/REA-RIFT-SPELLCASTING-SC103-WARRIOR-ALL-SOULS-STATIC-2026-11-02.json");
const priorAtlas=load("docs/REA-RIFT-SPELLCASTING-SC103-ABILITY-ATLAS-2026-11-02.json");
const listed=priorAtlas.records.filter(r=>r.priorKnownApiList==="listed-in-preserved-69");
const unlisted=originalThree.records.find(r=>!listed.some(k=>k.id===r.id));
const fakeSaved={
  player:{privateString:"SECRET-SENSITIVE"},
  latest:{addonVersion:"0.1.0",captureComplete:true,
    player:{name:"SECRET-SENSITIVE"},
    abilities:listed.map(r=>({lookupId:r.id,name:r.name}))},
  candidateLookup:{addonVersion:"0.4.4",entries:[
    {id:unlisted.id,status:"returned",listed:false,
      detail:{id:unlisted.id,name:unlisted.name,cooldown:0,unusable:false,
         target:"uPRIVATE_RUNTIME_TARGET_127",ownerUnit:"uPRIVATE_OWNER_127"}}
  ]}
};
const run=(other={})=>buildLiveAtlas({saved:fakeSaved,savedSha256:"a".repeat(64),
  originalThree,allWarrior,priorAtlas,...other});

test("353-ID union retains 69 API listed and 323 static without merges by name",()=>{
  assert.equal(listed.length,69);
  const atlas=run();
  assert.equal(atlas.counts.exactIds,353);
  assert.equal(atlas.counts.historicalStaticIds,323);
  assert.equal(atlas.counts.priorApiListed,69);
  assert.equal(atlas.counts.originalThreeSoulCandidates,96);
  assert.equal(atlas.records.filter(r=>!r.historicalStaticSource).length,30);
  assert.equal(new Set(atlas.records.map(r=>r.id)).size,353);
  assert.ok(atlas.duplicateNames.some(g=>g.name==="Building Fury"));
});
test("explicit-ID metadata preserves zero/false without inventing eligibility or leaking player",()=>{
  const atlas=run();
  const row=atlas.records.find(r=>r.id===unlisted.id);
  assert.equal(row.explicitIdDetail.status,"returned");
  assert.equal(row.explicitIdDetail.detail.cooldown,0);
  assert.equal(row.explicitIdDetail.detail.unusable,false);
  assert.equal(row.priorKnownApiList,"not-listed-in-preserved-69");
  assert.equal(row.unlockState,"unknown");
  assert.equal(row.learnableNow,"unknown");
  assert.equal(row.currentlyCastable,"unknown");
  assert.equal(atlas.counts.candidateDetailReturned,1);
  assert.equal(atlas.counts.additionalUnlistedDetailReturned,1);
  assert.doesNotMatch(JSON.stringify(atlas),/SECRET-SENSITIVE|uPRIVATE_/);
  assert.equal(row.explicitIdDetail.detail.target,undefined);
  assert.equal(row.explicitIdDetail.detail.ownerUnit,undefined);
});
test("export boundary strips target from prior Detail and leaves absent passive flags absent",()=>{
  const tainted={...priorAtlas,records:priorAtlas.records.map(r=>({...r}))};
  const targetRow=tainted.records.find(r=>r.priorApiDetail);
  assert.ok(targetRow);
  targetRow.priorApiDetail={...targetRow.priorApiDetail,target:"uPRIVATE_PRIOR_TARGET_127"};
  const passiveSaved={...fakeSaved,candidateLookup:{...fakeSaved.candidateLookup,entries:[
    {id:unlisted.id,status:"returned",listed:false,detail:{id:unlisted.id,passive:true}}
  ]}};
  const atlas=run({priorAtlas:tainted,saved:passiveSaved});
  const row=atlas.records.find(r=>r.id===unlisted.id);
  assert.equal(row.explicitIdDetail.detail.passive,true);
  assert.equal(Object.hasOwn(row.explicitIdDetail.detail,"unusable"),false);
  assert.equal(Object.hasOwn(row.explicitIdDetail.detail,"cooldown"),false);
  assert.equal(row.currentlyCastable,"unknown");
  assert.doesNotMatch(JSON.stringify(atlas),/uPRIVATE_/);
});
test("mismatched static identity and duplicate IDs refuse unqualified joins",()=>{
  const changed={...allWarrior,records:allWarrior.records.map(r=>({...r}))};
  const shared=changed.records.find(r=>priorAtlas.records.some(k=>k.id===r.id));
  shared.name="MISLABELED ABILITY";
  assert.throws(()=>run({allWarrior:changed}),/name mismatch/);
  const duplicate={...allWarrior,records:[...allWarrior.records,allWarrior.records[0]]};
  assert.throws(()=>run({allWarrior:duplicate}),/invalid\/duplicate exact ID/);
});
