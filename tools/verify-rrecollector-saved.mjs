import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import test from "node:test";
import { fileURLToPath } from "node:url";
import { parseSavedLua, buildAbilityCrosswalk, assessSnapshotForComparison } from "./read-rrecollector-saved.mjs";

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

function completeSnapshotFixture() {
  const item = staticCatalog.records[0];
  return {sequence:7,latest:{sequence:7,addonVersion:"0.4.10",
    captureComplete:true,frameTime:12.25,realTime:192.5,roleSlot:0,
    player:{id:"uSYNTHETIC",name:"Synthetic Player"},
    abilityList:{apiAvailable:true,enumerationComplete:true,detailFailures:0,
      ignored:0,truncated:0,uniqueCount:1,detailCount:1},
    abilities:[{lookupId:item.id,name:item.name}]}};
}

test("single saved snapshot may pass internal structure, never live freshness or event comparison", () => {
  const saved = completeSnapshotFixture();
  const q = assessSnapshotForComparison(saved);
  assert.equal(q.offlineStructureQualified, true);
  assert.deepEqual(q.reasons, []);
  for (const key of ["freshnessVerified","processBuildVerified","eventDeliveryVerified","eventComparisonReady"])
    assert.equal(q[key], false, key);
  const legacy = buildAbilityCrosswalk(saved,staticCatalog,"a".repeat(64));
  assert.equal(legacy.counts.knownApi,1);
  assert.deepEqual(legacy.knownSnapshotReadiness,q);
  assert.equal(JSON.stringify(q).includes("Synthetic Player"),false);
});

test("empty player table cannot qualify despite collector-level captureComplete=true", () => {
  const saved = completeSnapshotFixture();
  saved.latest.player = {};
  saved.latest.capabilities = {player:true};
  const q = assessSnapshotForComparison(saved);
  assert.equal(q.offlineStructureQualified,false);
  assert.ok(q.reasons.includes("PLAYER_IDENTITY_UNBOUND"));
  assert.equal(q.eventComparisonReady,false);
});

test("internally contradictory capability, clocks and List counts fail closed", () => {
  const cases = [
    ["explicit-player-unavailable", saved => {
      saved.latest.capabilities = {player:false};
    }, "PLAYER_CAPABILITY_CONTRADICTS_COMPLETE"],
    ["missing-player-capability", saved => {
      saved.latest.capabilities = {};
    }, "PLAYER_CAPABILITY_CONTRADICTS_COMPLETE"],
    ["negative-frame-clock", saved => {
      saved.latest.frameTime = -0.01;
    }, "CAPTURE_CLOCK_UNBOUND"],
    ["negative-real-clock", saved => {
      saved.latest.realTime = -0.01;
    }, "CAPTURE_CLOCK_UNBOUND"],
    ["impossible-raw-entry-count", saved => {
      saved.latest.abilityList.rawEntries = 0;
    }, "LIST_COUNT_CONTRADICTION"]
  ];
  for (const [name, mutate, reason] of cases) {
    const saved = completeSnapshotFixture();
    mutate(saved);
    const q = assessSnapshotForComparison(saved);
    assert.equal(q.offlineStructureQualified,false,name);
    assert.ok(q.reasons.includes(reason),name);
    assert.equal(q.eventComparisonReady,false,name);
  }
});

test("missing role and clock, stale sequence, partial List and counts fail closed", () => {
  const saved = completeSnapshotFixture();
  saved.latest.roleSlot = null;
  saved.latest.frameTime = undefined;
  saved.latest.sequence = 6;
  saved.latest.abilityList.enumerationComplete = false;
  saved.latest.abilityList.detailCount = 2;
  const q = assessSnapshotForComparison(saved);
  for (const reason of ["ROLE_UNBOUND","CAPTURE_CLOCK_UNBOUND","SEQUENCE_UNBOUND",
    "LIST_NOT_COMPLETE","RECORD_COUNT_MISMATCH"]) assert.ok(q.reasons.includes(reason),reason);
  assert.equal(q.offlineStructureQualified,false);
  assert.equal(q.freshnessVerified,false);
});

test("missing, zero-based, gapped and extra-key ability rows never qualify", () => {
  const cases = [
    ["missing", saved => {
      delete saved.latest.abilities;
      saved.latest.abilityList.uniqueCount = 0;
      saved.latest.abilityList.detailCount = 0;
    }],
    ["zero-based", saved => {
      saved.latest.abilities = {"0":saved.latest.abilities[0]};
    }],
    ["gapped", saved => {
      saved.latest.abilities = {"2":saved.latest.abilities[0]};
    }],
    ["extra-key", saved => {
      saved.latest.abilities = {"1":saved.latest.abilities[0],extra:"not-an-ability"};
    }]
  ];
  for (const [name, mutate] of cases) {
    const saved = completeSnapshotFixture();
    mutate(saved);
    const q = assessSnapshotForComparison(saved);
    assert.equal(q.offlineStructureQualified,false,name);
    assert.ok(q.reasons.includes("ABILITY_RECORDS_MALFORMED"),name);
    assert.equal(q.eventComparisonReady,false,name);
  }
});

test("zero or missing snapshot sequence remains unqualified", () => {
  for (const sequence of [0, null]) {
    const saved = completeSnapshotFixture();
    saved.sequence = saved.latest.sequence = sequence;
    assert.ok(assessSnapshotForComparison(saved).reasons.includes("SEQUENCE_UNBOUND"));
  }
});

test("explicit one-based Lua ability keys pass the offline structure gate", () => {
  const item = staticCatalog.records[0];
  const lua = 'RRECollectorData = { sequence = 7, latest = { sequence = 7, '
    + 'addonVersion = "0.4.10", captureComplete = true, frameTime = 12.25, '
    + 'realTime = 192.5, roleSlot = 0, player = { id = "uSYNTHETIC", name = "Fixture" }, '
    + 'abilityList = { apiAvailable = true, enumerationComplete = true, '
    + 'detailFailures = 0, ignored = 0, truncated = 0, uniqueCount = 1, detailCount = 1 }, '
    + 'abilities = { [1] = { lookupId = ' + JSON.stringify(item.id)
    + ', name = ' + JSON.stringify(item.name) + ' } } } }';
  const saved = parseSavedLua(lua);
  assert.equal(Array.isArray(saved.latest.abilities),false);
  const result = assessSnapshotForComparison(saved);
  assert.equal(result.offlineStructureQualified,true);
  assert.equal(result.eventComparisonReady,false);
});
