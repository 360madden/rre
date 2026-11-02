import test from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import {buildFromPinned,buildSectionMap} from "./build-spellbook-section-map.mjs";
const readJson = p => JSON.parse(fs.readFileSync(new URL("../docs/"+p,import.meta.url),"utf8"));
const crosswalkName="REA-RIFT-SPELLCASTING-SC103-EXACT-ID-CROSSWALK-2026-11-02.json";
test("fixed exported snapshot matches source-hashed 69-ID section replay",()=>{
 const got=buildFromPinned();
 const saved=readJson("REA-RIFT-SPELLCASTING-SC103-KNOWN-UI-SECTIONS-2026-11-02.json");
 assert.deepEqual(got,saved);
 assert.deepEqual(got.counts.bySection,{Paladin:28,VoidKnight:7,Paragon:4,General:7,Role:4,
  "Ascended Powers":5,"Patron Abilities":14});
 assert.equal(new Set(got.knownSections.map(r=>r.id)).size,69);
 assert.equal(got.origin.screenshotFiles.length,6);
});
test("four Changing Role identities remain distinct and unassigned to slots",()=>{
 const rows=buildFromPinned().knownSections.filter(r=>r.section==="Role");
 assert.equal(rows.length,4);
 assert.equal(new Set(rows.map(r=>r.id)).size,4);
 assert.ok(rows.every(r=>r.name==="Changing Role"&&r.roleSlot===null));
});
test("future unfamiliar non-static ability and corrupted static identity fail closed",()=>{
 const unknown=readJson(crosswalkName);unknown.knownOutsideStatic[0].currentDetail.name="Unobserved Ability";
 assert.throws(()=>buildSectionMap(unknown),/Unclassified outside ID/);
 const wrong=readJson(crosswalkName);wrong.staticCandidates[0].currentDetail.lookupId="A0000000000000000";
 assert.throws(()=>buildSectionMap(wrong),/Invalid static known ID/);
});
