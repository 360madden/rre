#!/usr/bin/env node
// RC-13: reproducible, source-hash-pinned ability atlas. Read-only; no game calls.
import fs from "node:fs";
import path from "node:path";
import crypto from "node:crypto";
import {fileURLToPath} from "node:url";

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
export const SOURCES = Object.freeze([
  {kind:"prior-api/static exact-ID crosswalk",path:"docs/REA-RIFT-SPELLCASTING-SC103-EXACT-ID-CROSSWALK-2026-11-02.json",sha256:"00c1cc8896591bd2c7dfedf0a831f689179fbfb0ac5369dcc63cfcf8b5ec79f5"},
  {kind:"disabled static Warrior candidate IDs",path:"docs/REA-RIFT-SPELLCASTING-SC103-WARRIOR-STATIC-ABILITIES-2026-11-02.json",sha256:"c48797e3cde754bbc8ce6812eb9dbfbe2549c1d271efde6468bfae10fbe6a3ae"},
  {kind:"previously-known spellbook UI section classification",path:"docs/REA-RIFT-SPELLCASTING-SC103-KNOWN-UI-SECTIONS-2026-11-02.json",sha256:"a68baa63c35a312e906025f796dd783bc2082661c445d1ba5678f8726eac65f3"},
  {kind:"source-hashed Soul Tree UI tooltip transcriptions",path:"docs/REA-RIFT-SPELLCASTING-SC103-PALADIN-TOOLTIP-METADATA-2026-11-02.json",sha256:"d9008e8d64860858299ea975817263c8cd2373d81f703c448b7ea2c7c8a65c43"}
]);
const ID = /^A[0-9A-F]{16}$/;
const OWN = (obj,key)=>Object.prototype.hasOwnProperty.call(obj,key);
function check(ok,why){if(!ok)throw new Error(why);}
function sha256(data){return crypto.createHash("sha256").update(data).digest("hex");}
function pick(obj,keys){
  const result={};
  for(const k of keys)if(OWN(obj,k))result[k]=obj[k];
  return result;
}
const API_FIELDS=[
  "description","rangeMin","rangeMax","costPower","costPlanarCharge",
  "weapon","castingTime","channeled","passive","racial","autoattack",
  "continuous","positioned"
];
const UI_FIELDS=[
  "tooltipType","powerCost","castPresentation","range","cooldownSeconds",
  "requiresMeleeWeapon","noGlobalCooldownStatement","durationSeconds",
  "targetCap","attackPointDamageExamples","mitigationPercent",
  "mitigationDurationSeconds","allyHeal","excludedStackingWith",
  "buffDurationSeconds","normalVersion","legendaryVersionExtra",
  "requiresBuffStack","effect","visibilityNote"
];
function apiMetadata(detail){
  if(detail===null)return null;
  const meta=pick(detail,API_FIELDS);
  // Missing/unknown does not mean a zero-second cooldown.
  check(!OWN(detail,"cooldown")||
    (typeof detail.cooldown==="number"&&Number.isFinite(detail.cooldown)&&detail.cooldown>=0),
    "Invalid saved API cooldown");
  meta.cooldownSeconds=OWN(detail,"cooldown")?detail.cooldown:null;
  return meta;
}
function uiTooltip(t){
  return {
    ...pick(t,UI_FIELDS),
    screenshot:{filename:t.screenshot.filename,sha256:t.screenshot.sha256},
    idAssociation:"static-ID and exact name, not a UI-visible ID"
  };
}
export function buildAtlas(crosswalk,staticSource,uiSource,tooltipSource){
  check(crosswalk.schemaVersion===1 && crosswalk.knownCaptureComplete===true &&
    crosswalk.liveCandidateLookupSaved===false &&
    crosswalk.counts?.knownApi===69 && crosswalk.counts?.staticCandidates===96 &&
    crosswalk.counts?.staticKnown===39 && crosswalk.counts?.staticUnlisted===57 &&
    crosswalk.counts?.knownOutsideStatic===30,
    "Prior accepted exact-ID crosswalk scope changed");
  check(staticSource.schemaVersion===1 &&
    staticSource.catalogVersion===crosswalk.staticCatalogVersion &&
    staticSource.records?.length===96 && crosswalk.staticCandidates?.length===96 &&
    crosswalk.knownOutsideStatic?.length===30,
    "Static candidate source scope changed");
  check(uiSource.schemaVersion===1 && uiSource.knownSections?.length===69 &&
    uiSource.counts?.knownApi===69 &&
    tooltipSource.schemaVersion===1 && tooltipSource.abilities?.length===6,
    "Known UI evidence scope changed");

  const staticRecords=new Map();
  for(const row of staticSource.records){
    check(ID.test(row.id)&&!staticRecords.has(row.id),"Duplicate/invalid static ID: "+row.id);
    staticRecords.set(row.id,row);
  }
  const uiIds=new Map();
  for(const row of uiSource.knownSections){
    check(ID.test(row.id)&&!uiIds.has(row.id)&&row.roleSlot===null,
      "Invalid/duplicate known UI section or inferred role slot: "+row.id);
    uiIds.set(row.id,row);
  }
  const records=new Map();
  const knownIds=new Set();
  for(const row of crosswalk.staticCandidates){
    const s=staticRecords.get(row.id);
    check(s&&s.name===row.name&&s.soul===row.soul&&s.category===row.category&&
      s.icon===row.icon&&row.exactNameAgreement!==false,
      "Crosswalk vs source static identity mismatch: "+row.id);
    const isKnown=row.listedInSavedCurrent===true;
    const detail=row.currentDetail;
    check(isKnown===Boolean(detail),
      "Current-known listing/detail mismatch: "+row.id);
    if(isKnown){
      check(detail.lookupId===row.id&&detail.id===row.id&&
        detail.idNew===row.id&&detail.name===row.name,
        "Current-known static Detail ID/name mismatch: "+row.id);
      knownIds.add(row.id);
    }
    check(!records.has(row.id),"Duplicate atlas ID: "+row.id);
    records.set(row.id,{
      id:row.id,name:row.name,
      stableIdBasis:"disabled ProjectAbilityBook Warrior static ID",
      sourceSoul:row.soul,sourceCategory:row.category,sourceIcon:row.icon,
      priorKnownApiList:isKnown?"listed-in-preserved-69":"not-listed-in-preserved-69",
      priorApiDetail:apiMetadata(isKnown?detail:null),
      knownUiSection:null,knownUiSectionAssociation:null,
      uiSoulTreeTooltip:null,
      roleSlot:null,unlockState:"unknown",currentUsability:"unknown"
    });
  }
  for(const row of crosswalk.knownOutsideStatic){
    const detail=row.currentDetail;
    check(ID.test(row.id)&&detail&&detail.lookupId===row.id&&detail.id===row.id&&
      detail.idNew===row.id&&typeof detail.name==="string"&&
      !records.has(row.id),
      "Known outside-static API Detail identity mismatch: "+row.id);
    knownIds.add(row.id);
    records.set(row.id,{
      id:row.id,name:detail.name,
      stableIdBasis:"preserved Inspect.Ability.List/Detail ID",
      sourceSoul:null,sourceCategory:null,sourceIcon:detail.icon??null,
      priorKnownApiList:"listed-in-preserved-69",
      priorApiDetail:apiMetadata(detail),
      knownUiSection:null,knownUiSectionAssociation:null,
      uiSoulTreeTooltip:null,
      roleSlot:null,unlockState:"unknown",currentUsability:"unknown"
    });
  }
  check(records.size===126&&knownIds.size===69&&
    [...records.values()].filter(r=>r.sourceSoul!==null).length===96,
    "Expected 126 union IDs / 69 listed / 96 static");

  for(const [id,section] of uiIds){
    const row=records.get(id);
    check(row&&knownIds.has(id)&&row.name===section.name &&
      (row.sourceSoul===null||row.sourceSoul===section.section),
      "UI known-section ID/name/soul mismatch: "+id);
    row.knownUiSection=section.section;
    row.knownUiSectionAssociation=section.association;
  }
  check([...knownIds].every(id=>uiIds.has(id)),"Known API ID absent from UI section index");

  const tooltipIds=new Set();
  for(const t of tooltipSource.abilities){
    const row=records.get(t.id);
    check(ID.test(t.id)&&!tooltipIds.has(t.id)&&row&&row.name===t.name&&
      row.sourceSoul==="Paladin"&&row.sourceCategory===t.staticCategory&&
      row.priorKnownApiList==="not-listed-in-preserved-69"&&
      t.currentKnownApiList==="absent-from-preserved-69"&&
      t.stableIdSource==="static-exact-name" &&
      /^[a-f0-9]{64}$/.test(t.screenshot?.sha256??""),
      "Tooltip ID must match unlisted static Paladin identity: "+t.id);
    tooltipIds.add(t.id);
    row.uiSoulTreeTooltip=uiTooltip(t);
  }
  check(tooltipIds.size===6&&
    [...records.values()].filter(r=>r.uiSoulTreeTooltip!==null).length===6,
    "Unexpected UI-only tooltip count");

  const byName=new Map();
  for(const r of records.values()){
    if(!byName.has(r.name))byName.set(r.name,[]);
    byName.get(r.name).push(r.id);
  }
  const homonyms=[...byName].filter(([,ids])=>ids.length>1)
    .map(([name,ids])=>({name,ids:ids.sort()}))
    .sort((a,b)=>a.name.localeCompare(b.name));
  check(homonyms.some(g=>g.name==="Building Fury"&&g.ids.length===3)&&
    homonyms.some(g=>g.name==="Changing Role"&&g.ids.length===4),
    "Required same-name distinct IDs not preserved");
  const all=[...records.values()].sort((a,b)=>a.id.localeCompare(b.id));
  const counts={
    exactIds:126,priorApiListed:69,staticWarriorCandidates:96,
    staticAndPriorApiListed:39,staticNotPriorApiListed:57,
    priorApiListedOutsideStatic:30,uiSectionAssignedKnown:69,
    uiOnlyTooltipRecords:6,duplicateNameGroups:homonyms.length
  };
  const atlas={
    schemaVersion:1,taskId:"RC-13 / SC-103",
    scope:"Read-only exact-ID union; no live v0.3 candidateLookup receipt or eligibility inference",
    sourceIndex:SOURCES,
    priorSavedVariablesSha256:crosswalk.savedSha256,
    counts,
    duplicateNames:homonyms,
    records:all,
    limitations:[
      "Not-listed means absent only from the preserved 69-ability current-known API snapshot; it is not a locked, learnable, eligible or unusable finding.",
      "Prior API cooldown is a saved Detail field, not a measured current remaining cooldown or global-cooldown result. Missing cooldown is null, never zero.",
      "UI section for non-static known spells is exact-name association; UI screenshots do not expose modern IDs or Changing Role slot mapping.",
      "The six Soul Tree tooltip IDs come from separate disabled static-source exact-name matches; UI tooltip mechanics are not a current runtime Detail response.",
      "Aegis of the Light has an explicit UI No Global Cooldown tooltip label, not an independently measured timing trace.",
      "Raw unit/target identifiers, character stats, live state and usability are deliberately not exported.",
      "RRECollector v0.3 source/host installation is accepted but a saved candidateLookup v0.3 receipt has not yet been observed."
    ]
  };
  const serialized=JSON.stringify(atlas);
  check(!/"(?:target|stats|currentCooldownBegin)"\s*:/.test(serialized)&&
    !/u[0-9A-F]{16}/.test(serialized),
    "Forbidden private/volatile unit state in atlas");
  return atlas;
}
export function buildFromPinned(){
  const data=SOURCES.map(source=>{
    const bytes=fs.readFileSync(path.join(ROOT,source.path));
    check(sha256(bytes)===source.sha256,"Pinned source changed: "+source.path);
    return JSON.parse(bytes.toString("utf8"));
  });
  return buildAtlas(...data);
}
const direct=process.argv[1]&&path.resolve(process.argv[1])===fileURLToPath(import.meta.url);
if(direct){
  try{process.stdout.write(JSON.stringify(buildFromPinned(),null,2)+"\n");}
  catch(error){process.stderr.write("RC-13 atlas generation failed: "+error.message+"\n");process.exitCode=1;}
}
