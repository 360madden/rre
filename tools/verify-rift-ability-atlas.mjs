import test from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import {fileURLToPath} from "node:url";
import {buildAtlas,buildFromPinned,SOURCES} from "./build-rift-ability-atlas.mjs";

const ROOT=path.resolve(path.dirname(fileURLToPath(import.meta.url)),"..");
const ARTIFACT="docs/REA-RIFT-SPELLCASTING-SC103-ABILITY-ATLAS-2026-11-02.json";
const read=p=>JSON.parse(fs.readFileSync(path.join(ROOT,p),"utf8"));
const sourceData=()=>SOURCES.map(s=>read(s.path));

test("pinned atlas reproduces committed JSON, all 126 exact IDs, and no inferred states",()=>{
  const built=buildFromPinned();
  const committed=fs.readFileSync(path.join(ROOT,ARTIFACT),"utf8");
  assert.equal(committed,JSON.stringify(built,null,2)+"\n");
  assert.deepEqual(built.counts,{
    exactIds:126,priorApiListed:69,staticWarriorCandidates:96,
    staticAndPriorApiListed:39,staticNotPriorApiListed:57,
    priorApiListedOutsideStatic:30,uiSectionAssignedKnown:69,
    uiOnlyTooltipRecords:6,duplicateNameGroups:2
  });
  assert.equal(new Set(built.records.map(r=>r.id)).size,126);
  assert.deepEqual(built.records.map(r=>r.id),built.records.map(r=>r.id).sort());
  assert.ok(built.records.every(r=>r.roleSlot===null &&
    r.unlockState==="unknown" && r.currentUsability==="unknown"));
  assert.equal(built.records.filter(r=>r.knownUiSection!==null).length,69);
  assert.equal(built.records.filter(r=>r.uiSoulTreeTooltip!==null).length,6);
  assert.deepEqual(built.duplicateNames.map(r=>[r.name,r.ids.length]),
    [["Building Fury",3],["Changing Role",4]]);
});

test("mutated ID/name/section/tooltip input cannot silently alter a source-qualified join",()=>{
  const sources=sourceData();
  const staticTamper=structuredClone(sources);
  staticTamper[1].records[0].name="Unrelated";
  assert.throws(()=>buildAtlas(...staticTamper),/identity mismatch/);
  const uiTamper=structuredClone(sources);
  uiTamper[2].knownSections[0].name="Not a spell";
  assert.throws(()=>buildAtlas(...uiTamper),/UI known-section ID\/name\/soul mismatch/);
  const tooltipTamper=structuredClone(sources);
  tooltipTamper[3].abilities[0].id="A0000000000000000";
  assert.throws(()=>buildAtlas(...tooltipTamper),/Tooltip ID/);
});

test("only whitelisted static/API/UI metadata exported; null cooldown and No GCD proof tier preserved",()=>{
  const a=buildFromPinned();
  const serialized=JSON.stringify(a);
  assert.doesNotMatch(serialized,/"(?:target|stats|currentCooldownBegin)"\s*:/);
  assert.doesNotMatch(serialized,/u[0-9A-F]{16}/);
  assert.ok(a.records.some(r=>r.priorApiDetail&&r.priorApiDetail.cooldownSeconds===null));
  assert.ok(a.records.some(r=>r.priorApiDetail&&r.priorApiDetail.cooldownSeconds!==null));
  const unlisted=a.records.filter(r=>r.priorKnownApiList==="not-listed-in-preserved-69");
  assert.equal(unlisted.length,57);
  assert.ok(unlisted.every(r=>r.priorApiDetail===null));
  const aegis=a.records.find(r=>r.name==="Aegis of the Light");
  assert.equal(aegis.priorApiDetail,null);
  assert.equal(aegis.uiSoulTreeTooltip.noGlobalCooldownStatement,"No Global Cooldown");
  assert.equal(aegis.uiSoulTreeTooltip.cooldownSeconds,30);
  assert.equal(a.records.filter(r=>r.uiSoulTreeTooltip?.noGlobalCooldownStatement==="No Global Cooldown").length,1);
  assert.ok(a.records.some(r=>r.name==="Light's Benediction"&&r.uiSoulTreeTooltip.cooldownSeconds===null));
});
