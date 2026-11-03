import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import test from "node:test";
import { fileURLToPath } from "node:url";
import { parseSavedLua, buildAbilityCrosswalk } from "./read-rrecollector-saved.mjs";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const staticCatalog = JSON.parse(fs.readFileSync(
  path.join(root,"docs/REA-RIFT-SPELLCASTING-SC103-WARRIOR-STATIC-ABILITIES-2026-11-02.json"),"utf8"));

test("SavedVariables literal parser retains 0/false and escaped physical newlines", () => {
  const id = staticCatalog.records[0].id;
  const lua = 'RRECollectorData = { latest = { captureComplete = true, abilities = {'
    + '{ lookupId = "' + id + '", name = "Aggressive Block", cooldown = 0, '
    + 'passive = false, description = "Line' + "\\" + "\n"
    + 'break" } } } }';
  const parsed = parseSavedLua(lua);
  assert.equal(parsed.latest.abilities.length, 1);
  assert.equal(parsed.latest.abilities[0].description, "Line\nbreak");
  assert.equal(parsed.latest.abilities[0].cooldown, 0);
  assert.equal(parsed.latest.abilities[0].passive, false);
  assert.equal(parsed.latest.captureComplete, true);
});

test("decoder refuses non-literal Lua and duplicate table keys", () => {
  assert.throws(()=>parseSavedLua('RRECollectorData = os.execute("bad")'),/only literal Lua values/);
  assert.throws(()=>parseSavedLua('RRECollectorData = { latest = {}, latest = {} }'),/duplicate Lua table key/);
  assert.throws(()=>parseSavedLua('OtherGlobal = {}'),/unexpected SavedVariables assignment/);
});

test("exact-ID merge keeps absent unknown, preserves role-variant names and source counts", () => {
  const first=staticCatalog.records[0];
  const saved={latest:{
    addonVersion:"0.1.0",captureComplete:true,
    abilities:[{lookupId:first.id,name:first.name,cooldown:0,passive:false,target:"uPRIVATE_LATEST"},
      {lookupId:"A0000000000000000",name:"Outside static",cooldown:8}]
  }};
  const result=buildAbilityCrosswalk(saved,staticCatalog,"f".repeat(64));
  assert.equal(result.counts.knownApi,2);
  assert.equal(result.counts.staticCandidates,96);
  assert.equal(result.counts.staticKnown,1);
  assert.equal(result.counts.staticUnlisted,95);
  assert.equal(result.counts.knownOutsideStatic,1);
  assert.equal(result.counts.knownStaticNameMismatches,0);
  assert.equal(result.knownOutsideStatic[0].id,"A0000000000000000");
  assert.equal(result.staticCandidates.find(x=>x.id===first.id).currentDetail.cooldown,0);
  assert.equal(result.staticCandidates.find(x=>x.id===first.id).currentDetail.passive,false);
  assert.equal(result.staticCandidates.find(x=>x.id===first.id).currentDetail.target,undefined);
  assert.equal(result.staticCandidates.filter(x=>x.name==="Building Fury").length,3);
  assert.equal(result.liveCandidateLookupSaved,false);
});

test("candidate lookup handles implicit and explicit numeric-keyed Lua entries", () => {
  const item = staticCatalog.records[0];
  for (const numbered of [false, true]) {
    const entry = '{ id = ' + JSON.stringify(item.id)
      + ', status = "returned", listed = false, detail = { '
      + 'name = ' + JSON.stringify(item.name)
      + ', cooldown = 0, unusable = false, target = "uPRIVATE_TARGET" } }';
    const entries = numbered ? '[1] = ' + entry : entry;
    const lua = 'RRECollectorData = { latest = { abilities = {} }, '
      + 'candidateLookup = { addonVersion = "0.4.4", entries = { '
      + entries + ' } } }';
    const saved = parseSavedLua(lua);
    const result = buildAbilityCrosswalk(saved, staticCatalog, "c".repeat(64));
    const row = result.staticCandidates.find(r=>r.id === item.id);
    assert.equal(result.liveCandidateLookupSaved, true);
    assert.equal(row.candidateLookup.status, "returned");
    assert.equal(row.candidateLookup.detail.name, item.name);
    assert.equal(row.candidateLookup.detail.cooldown, 0);
    assert.equal(row.candidateLookup.detail.unusable, false);
    assert.equal(row.candidateLookup.detail.target, undefined);
  }
});
