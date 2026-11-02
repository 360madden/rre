#!/usr/bin/env node
// RC-14: source-hash-guarded, read-only inventory of the disabled PAB Warrior files.
// This does not enumerate live game abilities, change addons, or infer eligibility.
import fs from "node:fs";
import path from "node:path";
import crypto from "node:crypto";
import {fileURLToPath} from "node:url";
import {parseSavedLua} from "./read-rrecollector-saved.mjs";

const ROOT=path.resolve(path.dirname(fileURLToPath(import.meta.url)),"..");
export const SOURCES=Object.freeze([
  {soul:"Beastmaster",file:"Beastmaster.lua",sha256:"209def510f0d7b4dccd7613e592bed0c65a68fd5e3f7be68d76b80198eea6fcb"},
  {soul:"Champion",file:"Champion.lua",sha256:"87151f611e3057a6a28b21892e954ba13025cbdbe6709872f3a0abe7d535bc5f"},
  {soul:"Liberator",file:"Liberator.lua",sha256:"6c9c080ad8e94b8edde6696f6bb0db4006ee0464124ee49cd2bf0fdbb3accda5"},
  {soul:"Paladin",file:"Paladin.lua",sha256:"e4af04464201adbc5cbae9d07cab0e36a9da616b5b30abd466f8ca44c8f92f28"},
  {soul:"Paragon",file:"Paragon.lua",sha256:"6798169325e337613a5ff28c4a0c1f2830f67d8ac0da9dc584cde1e8a1421a9b"},
  {soul:"Reaver",file:"Reaver.lua",sha256:"7a1b57558c3357137514fe3b9f2f8047d31ea15e632ca55b62ab43cc351fb2a9"},
  {soul:"Riftblade",file:"Riftblade.lua",sha256:"db59f3b44d11b62056f5e8b73276dd8f889299e8010a0551a98fb10cc70f7027"},
  {soul:"Tempest",file:"Tempest.lua",sha256:"05237d5d41293c93a58517b9eba36ccd064b3ba6e9c5a1221b2fc8821004123c"},
  {soul:"VoidKnight",file:"VoidKnight.lua",sha256:"b8dd0a75359fac18515a346d1492ce2885eb1a0fdd01ca459dffbdb236a94439"},
  {soul:"Warchanter",file:"Warchanter.lua",sha256:"a94355ee9fc733468dc8f124dca54a5ba4238dc4a50037e114cf77b6dce0432e"},
  {soul:"Warlord",file:"Warlord.lua",sha256:"2ac0c3cef2691cb940985987a5646f727609ecd3f1fcc401ec4c5a0c09b26ad4"}
]);
const BASE={
 path:"docs/REA-RIFT-SPELLCASTING-SC103-WARRIOR-STATIC-ABILITIES-2026-11-02.json",
 sha256:"c48797e3cde754bbc8ce6812eb9dbfbe2549c1d271efde6468bfae10fbe6a3ae"
};
const ATLAS={
 path:"docs/REA-RIFT-SPELLCASTING-SC103-ABILITY-ATLAS-2026-11-02.json",
 sha256:"70a3e0fc7db4f2419c47011f4676b421835b2627ed23ce6d3bcf2a862689632e"
};
const ID=/^A[0-9A-F]{16}$/;
function check(ok,why){if(!ok)throw new Error(why);}
function sha256(data){return crypto.createHash("sha256").update(data).digest("hex");}
function checkedJson(ref){
 const bytes=fs.readFileSync(path.join(ROOT,ref.path));
 check(sha256(bytes)===ref.sha256,"Previously accepted input changed: "+ref.path);
 return JSON.parse(bytes.toString("utf8"));
}
function parseStaticFile(content,ref){
 check(typeof content==="string","Missing source text: "+ref.file);
 check(sha256(Buffer.from(content,"utf8"))===ref.sha256,"Source hash changed: "+ref.file);
 // Reuse the bounded literal-only Lua parser; never evaluate third-party Lua.
 const lead=/^(\uFEFF?)ProjectAbilityBook_Souls_([A-Za-z]+)(?=\s*=)/;
 const match=lead.exec(content);
 check(match&&match[2]===ref.soul,"Unexpected source assignment: "+ref.file);
 const parsed=parseSavedLua(content.replace(lead,"RRECollectorData"));
 check(parsed&&parsed.Abilities&&typeof parsed.Abilities==="object"&&!Array.isArray(parsed.Abilities),
   "Missing Abilities table: "+ref.file);
 const records=[];
 for(const [category,abilities] of Object.entries(parsed.Abilities)){
  check(abilities&&typeof abilities==="object"&&!Array.isArray(abilities),
    "Non-object source category: "+ref.file+"/"+category);
  for(const [name,item] of Object.entries(abilities)){
   check(item&&typeof item==="object"&&!Array.isArray(item)&&
    ID.test(item.ID)&&typeof item.Icon==="string"&&item.Icon.length>0 &&
    typeof name==="string"&&name.length>0,
    "Invalid static name/icon/ID: "+ref.file+"/"+name);
   records.push({id:item.ID,name,soul:ref.soul,category,icon:item.Icon});
  }
 }
 return records;
}
export function buildStaticReference(contents,priorAtlas,baseline){
 check(priorAtlas.schemaVersion===1&&priorAtlas.counts?.exactIds===126&&
   priorAtlas.counts?.priorApiListed===69&&priorAtlas.counts?.staticWarriorCandidates===96,
   "Unexpected accepted RC-13 atlas");
 check(baseline.schemaVersion===1&&baseline.counts?.total===96&&
   baseline.records?.length===96,"Unexpected accepted three-soul source catalog");
 const old=new Map(baseline.records.map(r=>[r.id,r]));
 check(old.size===96,"Duplicate original three-soul IDs");
 const known=new Map(priorAtlas.records
   .filter(r=>r.priorKnownApiList==="listed-in-preserved-69").map(r=>[r.id,r]));
 check(known.size===69,"Prior current-known ID count changed");
 const priorAll=new Map(priorAtlas.records.map(r=>[r.id,r]));
 check(priorAll.size===126,"Prior atlas identity collision");
 const all=new Map(),bySoul={},byName=new Map(),sourceIndex=[];
 for(const ref of SOURCES){
  const found=parseStaticFile(contents[ref.file],ref);
  check(found.length>0,"No static candidates: "+ref.file);
  let listed=0;
  for(const value of found){
   check(!all.has(value.id),"Duplicate static exact ID across Warrior sources: "+value.id);
   const inBase=old.get(value.id);
   if(inBase)check(inBase.name===value.name&&inBase.soul===value.soul&&
    inBase.category===value.category&&inBase.icon.replaceAll(String.fromCharCode(92,92),String.fromCharCode(92))===value.icon,
    "Original three-soul catalog disagrees: "+value.id);
   else check(!["Paladin","VoidKnight","Paragon"].includes(value.soul),
    "Original three-soul catalog unexpectedly missing static source ID: "+value.id);
   const fromAtlas=priorAll.get(value.id);
   if(fromAtlas){
    check(fromAtlas.name===value.name&&
      (fromAtlas.sourceSoul===null||fromAtlas.sourceSoul===value.soul),
      "Existing RC-13 atlas disagrees on exact ID/name/soul: "+value.id);
   }
   const currentKnown=known.get(value.id);
   if(currentKnown)listed++;
   const r={
     ...value,
     includedInOriginalThreeSoulCatalog:!!inBase,
     priorKnownApiList:currentKnown?"listed-in-preserved-69":"not-listed-in-preserved-69",
     priorKnownUiSection:currentKnown?.knownUiSection??null,
     roleSlot:null,unlockState:"unknown",currentUsability:"unknown"
   };
   all.set(r.id,r);
   if(!byName.has(r.name))byName.set(r.name,[]);
   byName.get(r.name).push(r.id);
  }
  bySoul[ref.soul]={staticIds:found.length,priorApiListed:listed,
    notListedInPrior69:found.length-listed};
  sourceIndex.push({relative:"projectabilitybook.disabled/Callings/Warrior/"+ref.file,
    sha256:ref.sha256,staticIds:found.length});
 }
 check(all.size===323&&sourceIndex.length===11,"Expected pinned 323 IDs in 11 source files");
 check([...old].every(([id])=>all.has(id)),"Original three-soul catalog not a subset");
 const priorKnownCount=[...all.values()]
   .filter(r=>r.priorKnownApiList==="listed-in-preserved-69").length;
 const oldSubset=[...all.values()].filter(r=>r.includedInOriginalThreeSoulCatalog).length;
 const originalKnown=[...all.values()].filter(r=>r.includedInOriginalThreeSoulCatalog&&
   r.priorKnownApiList==="listed-in-preserved-69").length;
 check(priorKnownCount===39&&oldSubset===96&&originalKnown===39,
  "Unexpected static/current-known overlap");
 const homonyms=[...byName].filter(([,ids])=>ids.length>1)
   .map(([name,ids])=>({name,ids:ids.sort()})).sort((a,b)=>a.name.localeCompare(b.name));
 check(homonyms.length===1&&homonyms[0].name==="Building Fury"&&
  homonyms[0].ids.length===9,"Source duplicate-name identities changed");
 const records=[...all.values()].sort((a,b)=>a.id.localeCompare(b.id));
 const result={
  schemaVersion:1,taskId:"RC-14 / SC-103",
  sourceKind:"exact-ID and icon reference from 11 disabled ProjectAbilityBook Warrior Lua files",
  evidenceScope:"historical disabled static source; no newly discovered live known/learnable/castable abilities",
  sourceIndex:{
    originalWarriorFiles:sourceIndex,
    acceptedThreeSoulCatalog:BASE,
    acceptedPriorKnownApiAtlas:ATLAS
  },
  counts:{
    sourceSoulFiles:11,uniqueStaticIds:323,
    alreadyInOriginalThreeSoulCatalog:96,additionalStaticIds:227,
    listedInPreserved69:39,notListedInPreserved69:284,
    priorApiKnownOutsideAllStatic:30,
    mergedDistinctStaticAndPriorKnown:353,
    duplicateNameGroups:homonyms.length
  },
  bySoul,duplicateNames:homonyms,records,
  limitations:[
   "Eleven files means the source-installed Warrior directory snapshot; it does not prove a complete current RIFT Warrior spellbook.",
   "No source ID absent from the preserved Atank 69-known API List is classified as locked, learnable, eligible, castable or current-role-owned.",
   "Historical static names, IDs and icon paths have source-file provenance, not runtime Detail, cooldown, skill rank or prerequisite proof.",
   "The original three-soul 96-ID catalog and the RC-13 126-ID atlas remain unchanged; this is an additive reference, not a new addon deployment.",
   "No game input, current-client lookup receipt or native timing/queue measurement occurred."
  ]
 };
 const text=JSON.stringify(result);
 check(!/"(?:target|stats|currentCooldownBegin)"\s*:/.test(text)&&
   !/u[0-9A-F]{16}/.test(text),"Private or live-unit data entered static reference");
 return result;
}
export function defaultWarriorSourceDir(){
 const base=process.env.USERPROFILE;
 check(typeof base==="string"&&base.length>0,
  "Pass a Warrior source directory argument; USERPROFILE unavailable");
 return path.join(base,"OneDrive","Documents","RIFT","Interface","AddOns",
  "projectabilitybook.disabled","Callings","Warrior");
}
export function buildFromPinned(sourceDir=defaultWarriorSourceDir()){
 const available=fs.readdirSync(sourceDir).filter(f=>f.endsWith(".lua")).sort();
 check(JSON.stringify(available)===JSON.stringify(SOURCES.map(s=>s.file).sort()),
  "Unexpected Warrior Lua source file set");
 const contents={};
 for(const ref of SOURCES)contents[ref.file]=fs.readFileSync(path.join(sourceDir,ref.file),"utf8");
 return buildStaticReference(contents,checkedJson(ATLAS),checkedJson(BASE));
}
const direct=process.argv[1]&&path.resolve(process.argv[1])===fileURLToPath(import.meta.url);
if(direct){
 try{process.stdout.write(JSON.stringify(buildFromPinned(process.argv[2]||defaultWarriorSourceDir()),null,2)+"\n");}
 catch(error){process.stderr.write("RC-14 static reference failed: "+error.message+"\n");process.exitCode=1;}
}
