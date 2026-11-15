#!/usr/bin/env node
// Deterministic read-only replay of already accepted SC-604/SC-103/SC-502 evidence.
// Output is sanitized: no raw player IDs, target IDs, stats or gameplay controls.
import fs from "node:fs";
import path from "node:path";
import crypto from "node:crypto";
import {fileURLToPath} from "node:url";
import {canonicalRepositoryTextBytes} from "./repository-text-eol.mjs";
const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const inputs = Object.freeze({
 "docs/REA-RIFT-SPELLCASTING-SC604-INTERIM-MECHANISM-2026-11-01.json":"963774ae669970767b4267a10b75a835d4d24e90954a814494f3c504e695c824",
 "docs/REA-RIFT-SPELLCASTING-SC103-WARRIOR-STATIC-ABILITIES-2026-11-02.json":"c48797e3cde754bbc8ce6812eb9dbfbe2549c1d271efde6468bfae10fbe6a3ae",
 "docs/REA-RIFT-SPELLCASTING-SC103-EXACT-ID-CROSSWALK-2026-11-02.json":"00c1cc8896591bd2c7dfedf0a831f689179fbfb0ac5369dcc63cfcf8b5ec79f5",
 "docs/REA-RIFT-SPELLCASTING-SC502-EVENT-ATTRIBUTION-2026-11-01.json":"73bfe67b4a79f3c6c983113d439ef503ba622235f362a2cb16e39e803714ea16"
});
const hex=/^[a-f0-9]{64}$/, id=/^A[0-9A-F]{16}$/;
function check(ok,why){if(!ok)throw Error(why);}
function sha(bytes){return crypto.createHash("sha256").update(bytes).digest("hex");}
function safeDocPath(p){
 return typeof p==="string"&&/^docs\/[A-Za-z0-9_./-]+$/.test(p)
  &&p.split("/").every(part=>part!==""&&part!=="."&&part!=="..");
}
function raw(p){
 check(safeDocPath(p),"Unsafe evidence path");
 return fs.readFileSync(path.resolve(root,p));
}
export function buildReplay(model, catalog, crosswalk, outcomes){
 check([model,catalog,crosswalk,outcomes].every(x=>x.schemaVersion===1),"Unexpected evidence schema");
 const current=model.latestOriginalLocalExecutableSha256, old=model.historicalRiftRecordSha256;
 check(typeof current==="string"&&typeof old==="string"&&hex.test(current)&&hex.test(old)&&current!==old,"Build identity conflict");
 check(outcomes.sourceBuildSha256===old&&outcomes.hostCurrentBuildSha256===current,"Historical/current build mixed");
 const indexed=Object.values(model.sourceIndex||{});
 check(indexed.length===14,"Source index is not 14 reports");
 const seenIndexed=new Set();
 for(const s of indexed){
  check(s&&typeof s==="object"&&safeDocPath(s.path)&&typeof s.sha256==="string"&&hex.test(s.sha256)&&!seenIndexed.has(s.path),"Unsafe source-index entry");
  seenIndexed.add(s.path);
 }
 const staticMap=new Map();
 for(const s of catalog.records||[]){
  check(id.test(s.id)&&!staticMap.has(s.id)&&["Paladin","VoidKnight","Paragon"].includes(s.soul),"Invalid static ID/soul");
  staticMap.set(s.id,s);
 }
 check(staticMap.size===96,"Static candidate count changed");
 check(Array.isArray(catalog.sourceFiles)&&catalog.sourceFiles.length===3,"Missing original static Lua hashes");
 const seenSources=new Set();
 for(const s of catalog.sourceFiles){
  check(s&&["Paladin","VoidKnight","Paragon"].includes(s.soul)
   &&s.path===`projectabilitybook.disabled/Callings/Warrior/${s.soul}.lua`
   &&typeof s.sha256==="string"&&hex.test(s.sha256)
   &&!seenSources.has(s.soul),"Unsafe original Warrior source manifest");
  seenSources.add(s.soul);
 }
 check(typeof crosswalk.savedSha256==="string"&&hex.test(crosswalk.savedSha256),"Invalid saved evidence digest");
 const rows=crosswalk.staticCandidates||[], seen=new Set();
 check(rows.length===staticMap.size,"Crosswalk size mismatch");
 for(const r of rows){
  const s=staticMap.get(r.id);
  check(s&&!seen.has(r.id)&&r.name===s.name&&r.soul===s.soul&&r.category===s.category,"Static/crosswalk mismatch: "+r.id);
  seen.add(r.id);
  check(typeof r.listedInSavedCurrent==="boolean","Missing List membership");
  check(r.exactNameAgreement===(r.listedInSavedCurrent?true:null),"Unqualified exact-name agreement");
  if(r.listedInSavedCurrent)check(r.currentDetail?.lookupId===r.id&&r.currentDetail?.name===r.name,"Known Detail mismatch");
 }
 const outside=crosswalk.knownOutsideStatic||[], extra=new Set();
 for(const r of outside){
  check(id.test(r.id)&&!staticMap.has(r.id)&&!extra.has(r.id)&&r.currentDetail?.lookupId===r.id,"Outside-known ID mismatch");
  extra.add(r.id);
 }
 const known=rows.filter(r=>r.listedInSavedCurrent).length;
 const totals={knownApi:known+outside.length,staticCandidates:rows.length,staticKnown:known,
  staticUnlisted:rows.length-known,knownOutsideStatic:outside.length,knownStaticNameMismatches:0};
 for(const [k,v] of Object.entries(totals))check(crosswalk.counts?.[k]===v,"Changed crosswalk count: "+k);
 check(crosswalk.knownCaptureComplete===true&&known===39&&outside.length===30,"Not the accepted 69/96 capture");
 const bySoul={};
 for(const soul of ["Paladin","VoidKnight","Paragon"]){
  const sub=rows.filter(r=>r.soul===soul), n=sub.filter(r=>r.listedInSavedCurrent).length;
  check(crosswalk.bySoul?.[soul]?.candidates===sub.length&&crosswalk.bySoul?.[soul]?.known===n,"Soul count mismatch: "+soul);
  bySoul[soul]={candidates:sub.length,known:n};
 }
 const fury=rows.filter(r=>r.name==="Building Fury");
 check(fury.length===3&&new Set(fury.map(r=>r.id)).size===3&&new Set(fury.map(r=>r.soul)).size===3,"Building Fury ID collision");
 const names=new Map([...rows.map(r=>[r.id,r.name]),...outside.map(r=>[r.id,r.currentDetail.name||null])]);
 const trials=[];
 for(const t of outcomes.rangedTrials||[]){
  check(id.test(t.selectedAbilityId)&&names.has(t.selectedAbilityId),"Historical ID has no exact current catalog match");
  check(t.events?.length===t.rawEventCount,"Historical event count mismatch");
  const c={selectedTargetDamage:0,selectedTargetDodges:0,selfDodges:0,otherTargetAbilityDamage:0,
   otherTargetAbilityDamageEvents:0,differentAbilityDamageToSelected:0,differentAbilityDamageEvents:0,
   differentAbilityMissesToSelected:0};
  for(const e of t.events){
   const own=e.abilityNew===t.selectedAbilityId&&e.caster===t.playerId, sel=e.target===t.selectedTargetId, self=e.target===t.playerId;
   if(own&&sel&&e.kind==="damage")c.selectedTargetDamage+=e.damage;
   else if(own&&sel&&e.kind==="dodge")c.selectedTargetDodges++;
   else if(own&&self&&e.kind==="dodge")c.selfDodges++;
   else if(own&&!sel&&!self&&e.kind==="damage"){c.otherTargetAbilityDamage+=e.damage;c.otherTargetAbilityDamageEvents++;}
   else if(!own&&sel&&e.kind==="damage"){c.differentAbilityDamageToSelected+=e.damage;c.differentAbilityDamageEvents++;}
   else if(!own&&sel&&e.kind==="miss")c.differentAbilityMissesToSelected++;
   else throw Error("Unclassified event in trial "+t.trial);
  }
  for(const [k,v] of Object.entries(c))check(t.classification?.[k]===v,"Attribution mismatch: "+t.trial+" "+k);
  trials.push({trial:t.trial,abilityId:t.selectedAbilityId,matchedCurrentName:names.get(t.selectedAbilityId),
   ...c,evidenceBuild:"historical only"});
 }
 check(trials.length===2&&outcomes.melee?.originalRawMatchFlag===false&&
  outcomes.melee?.originalRawHitFlag===false,"Historical raw melee negative match lost");
 return {
  schemaVersion:1,taskId:"RC-10",scope:"SC-602 interim groundwork; final SC-601/602 still blocked",
  builds:{physicalClient:current,historicalEvents:old},
  sourceManifest:{
   pinned:Object.entries(inputs).map(([relative,sha256])=>({relative,sha256})),
   indexed:indexed.map(s=>({relative:s.path,sha256:s.sha256})),
   disabledWarriorLua:catalog.sourceFiles.map(s=>({soul:s.soul,relative:s.path,sha256:s.sha256,
    note:"catalog-attested; original Lua outside RRE repo"})),
   savedVariablesSha256:crosswalk.savedSha256
  },
  abilityIndex:{...totals,bySoul,static:rows.map(r=>({id:r.id,name:r.name,soul:r.soul,category:r.category,
   listedInSavedCurrent:r.listedInSavedCurrent})),
   knownOutsideStatic:outside.map(r=>({id:r.id,name:r.currentDetail.name||null}))},
  outcomes:{historicalRangedTrials:trials,rawMeleeExactIdMatched:false,
   laterReplayCannotReplaceRawMatch:true},
  unknowns:["Unlisted does not imply locked/learnable/castable","No persisted v0.3 candidateLookup",
   "No qualified current GCD or queue-mode label","No native cast submission or server acknowledgement",
   "Historical exact-ID match does not prove current-build outcome parity"]
 };
}
export function replay(){
 const [m,c,x,e]=Object.entries(inputs).map(([p,d])=>{
  const b=canonicalRepositoryTextBytes(raw(p));check(sha(b)===d,"Pinned input SHA mismatch: "+p);return JSON.parse(b.toString("utf8"));
 });
 for(const s of Object.values(m.sourceIndex)){
  check(hex.test(s.sha256)&&sha(canonicalRepositoryTextBytes(raw(s.path)))===s.sha256,"Indexed source SHA mismatch: "+s.path);
 }
 return buildReplay(m,c,x,e);
}
const invoked=process.argv[1]&&path.resolve(process.argv[1])===fileURLToPath(import.meta.url);
if(invoked){try{process.stdout.write(JSON.stringify(replay(),null,2)+"\n");}
catch(e){process.stderr.write("Interim replay failed: "+e.message+"\n");process.exitCode=1;}}
