import test from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import {fileURLToPath} from "node:url";
import {
 SOURCES,defaultWarriorSourceDir,buildStaticReference,buildFromPinned
} from "./build-warrior-static-reference.mjs";

const ROOT=path.resolve(path.dirname(fileURLToPath(import.meta.url)),"..");
const OUT="docs/REA-RIFT-SPELLCASTING-SC103-WARRIOR-ALL-SOULS-STATIC-2026-11-02.json";
const BASE="docs/REA-RIFT-SPELLCASTING-SC103-WARRIOR-STATIC-ABILITIES-2026-11-02.json";
const ATLAS="docs/REA-RIFT-SPELLCASTING-SC103-ABILITY-ATLAS-2026-11-02.json";
const read=p=>JSON.parse(fs.readFileSync(path.join(ROOT,p),"utf8"));
const sources=()=>Object.fromEntries(SOURCES.map(s=>
 [s.file,fs.readFileSync(path.join(defaultWarriorSourceDir(),s.file),"utf8")]));

test("11 source SHA hashes reproduce the committed 323-ID reference exactly",()=>{
 const built=buildFromPinned();
 assert.equal(fs.readFileSync(path.join(ROOT,OUT),"utf8"),
  JSON.stringify(built,null,2)+"\n");
 assert.deepEqual(built.counts,{
  sourceSoulFiles:11,uniqueStaticIds:323,
  alreadyInOriginalThreeSoulCatalog:96,additionalStaticIds:227,
  listedInPreserved69:39,notListedInPreserved69:284,
  priorApiKnownOutsideAllStatic:30,mergedDistinctStaticAndPriorKnown:353,
  duplicateNameGroups:1
 });
 assert.equal(built.sourceIndex.originalWarriorFiles.length,11);
 assert.equal(new Set(built.records.map(r=>r.id)).size,323);
 assert.deepEqual(built.records.map(r=>r.id),
  built.records.map(r=>r.id).sort());
 assert.deepEqual(built.duplicateNames.map(r=>[r.name,r.ids.length]),
  [["Building Fury",9]]);
});

test("source byte or old-catalog/atlas identity mutations fail closed",()=>{
 const bytes=sources(),atlas=read(ATLAS),baseline=read(BASE);
 const badBytes={...bytes};
 badBytes["Champion.lua"]=badBytes["Champion.lua"]+" ";
 assert.throws(()=>buildStaticReference(badBytes,atlas,baseline),/Source hash changed/);
 const badBaseline=structuredClone(baseline);
 badBaseline.records[0].name="Different identity";
 assert.throws(()=>buildStaticReference(bytes,atlas,badBaseline),
  /Original three-soul catalog disagrees/);
 const badAtlas=structuredClone(atlas);
 badAtlas.records.find(r=>r.id==="A6663BAE96C8E85E6").name="Different identity";
 assert.throws(()=>buildStaticReference(bytes,badAtlas,baseline),
  /Existing RC-13 atlas disagrees/);
});

test("additional static candidates stay source-only, with unknown eligibility and no private state",()=>{
 const d=buildFromPinned();
 assert.equal(d.records.filter(r=>r.includedInOriginalThreeSoulCatalog).length,96);
 assert.equal(d.records.filter(r=>!r.includedInOriginalThreeSoulCatalog).length,227);
 assert.equal(d.records.filter(r=>r.priorKnownApiList==="listed-in-preserved-69").length,39);
 assert.ok(d.records.every(r=>r.roleSlot===null&&r.unlockState==="unknown"&&
  r.currentUsability==="unknown"));
 assert.ok(d.records.every(r=>r.includedInOriginalThreeSoulCatalog||
  r.priorKnownApiList==="not-listed-in-preserved-69"));
 assert.equal(d.bySoul["Warchanter"].staticIds,26);
 assert.equal(d.bySoul["Beastmaster"].staticIds,36);
 assert.doesNotMatch(JSON.stringify(d),/"(?:target|stats|currentCooldownBegin)"\s*:/);
 assert.doesNotMatch(JSON.stringify(d),/u[0-9A-F]{16}/);
});
