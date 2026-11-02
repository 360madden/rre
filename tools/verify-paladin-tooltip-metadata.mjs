import test from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import crypto from "node:crypto";
import path from "node:path";
import {fileURLToPath} from "node:url";
const ROOT=path.resolve(path.dirname(fileURLToPath(import.meta.url)),"..");
const DATA="docs/REA-RIFT-SPELLCASTING-SC103-PALADIN-TOOLTIP-METADATA-2026-11-02.json";
const SHA=/^[a-f0-9]{64}$/;
const digest=p=>crypto.createHash("sha256").update(fs.readFileSync(path.join(ROOT,p))).digest("hex");
const read=p=>JSON.parse(fs.readFileSync(path.join(ROOT,p),"utf8"));
const known=read("docs/REA-RIFT-SPELLCASTING-SC103-EXACT-ID-CROSSWALK-2026-11-02.json");
const data=read(DATA);
function validate(d){
 assert.equal(d.schemaVersion,1);assert.equal(d.count,6);
 assert.equal(d.source.exactIdCrosswalk.sha256,
  digest(d.source.exactIdCrosswalk.path));
 assert.equal(d.source.screenshotReport.sha256,
  digest(d.source.screenshotReport.path));
 assert.equal(d.source.staticPaladinSource.sha256,
  "e4af04464201adbc5cbae9d07cab0e36a9da616b5b30abd466f8ca44c8f92f28");
 const report=fs.readFileSync(path.join(ROOT,d.source.screenshotReport.path),"utf8");
 const ids=new Set(),names=new Set();
 for(const v of d.abilities){
  assert.match(v.id,/^A[0-9A-F]{16}$/);
  assert.ok(!ids.has(v.id)&&!names.has(v.name),"duplicate static identity");
  ids.add(v.id);names.add(v.name);
  const row=known.staticCandidates.find(r=>r.id===v.id);
  assert.ok(row&&row.name===v.name&&row.soul==="Paladin"&&
   row.category===v.staticCategory&&!row.listedInSavedCurrent,
   "must be an unlisted exact-ID Paladin static candidate");
  assert.equal(v.currentKnownApiList,"absent-from-preserved-69");
  assert.equal(v.stableIdSource,"static-exact-name");
  assert.match(v.screenshot.filename,/^2026-11-01_210[67]\d\d\.jpg$/);
  assert.match(v.screenshot.sha256,SHA);
  assert.ok(report.includes(v.screenshot.filename)&&
    report.includes(v.screenshot.sha256),"screenshot not source-audited");
  assert.equal(v.castPresentation,"Instant");
  assert.ok(Number.isInteger(v.powerCost)&&v.powerCost>0);
  assert.ok(v.cooldownSeconds===null||
   (Number.isFinite(v.cooldownSeconds)&&v.cooldownSeconds>0));
  assert.equal(v.range.meters===null||v.range.meters>0,true);
  assert.equal(v.noGlobalCooldownStatement===null||
   v.noGlobalCooldownStatement==="No Global Cooldown",true);
 }
 assert.deepEqual(d.tooltipNoGcdNames,["Aegis of the Light"]);
 assert.deepEqual(d.abilities.filter(x=>x.noGlobalCooldownStatement!==null).map(x=>x.name),
  ["Aegis of the Light"]);
 assert.equal(d.abilities.filter(x=>x.cooldownSeconds!==null).length,4);
 assert.equal(d.abilities.find(x=>x.name==="Protector's Fury").legendaryVersionExtra.procAbility,
  "Light's Balm");
 return true;
}
test("6 exact static candidates are absent from known List and source-hash tied to originals",()=>validate(data));
test("unknown new candidate or invented live-known state fails closed",()=>{
 const x=structuredClone(data);x.abilities[0].id="A0000000000000000";
 assert.throws(()=>validate(x),/unlisted exact-ID/);
 const y=structuredClone(data);y.abilities[0].currentKnownApiList="currently-known";
 assert.throws(()=>validate(y),/absent-from-preserved-69/);
});
test("No Global Cooldown is a single explicit tooltip statement, never defaulted",()=>{
 const x=structuredClone(data);x.abilities[1].noGlobalCooldownStatement="No Global Cooldown";
 assert.throws(()=>validate(x));
 const y=structuredClone(data);y.abilities[0].cooldownSeconds=0;
 assert.throws(()=>validate(y));
});
