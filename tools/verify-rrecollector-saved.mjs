import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import test from "node:test";
import { fileURLToPath } from "node:url";
import { parseSavedLua, buildAbilityCrosswalk, assessSnapshotForComparison } from "./read-rrecollector-saved.mjs";
import { exportSavedSnapshot } from "./rre-reader-saved-snapshot.mjs";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const staticCatalog = JSON.parse(fs.readFileSync(
  path.join(root,"docs/REA-RIFT-SPELLCASTING-SC103-WARRIOR-STATIC-ABILITIES-2026-11-02.json"),"utf8"));

const refSource = (assignments, body = '{counts=ref[1],attempt={counts=ref[1]}}', count = 1,
  assignment = 'RRECollectorData') => `local ref = {}\nfor k=1,${count} do ref[k] = {} end\n${assignments}\n${assignment}=${body}`;
test('RIFT shared-counter prologue decodes as bounded data without executing Lua', () => {
  const parsed = parseSavedLua(refSource('ref[1].mapFailures=0\nref[1].available=false'));
  assert.equal(parsed.counts.mapFailures, 0); assert.equal(parsed.counts.available, false);
  assert.deepEqual(parsed.counts, parsed.attempt.counts);
  assert.notEqual(parsed.counts, parsed.attempt.counts);
  assert.equal(Object.getPrototypeOf(parsed.counts), null);
});
test('reference fields resolve after all writes and preserve keyed and empty shapes', () => {
  const parsed = parseSavedLua(refSource('ref[1].later=ref[2]\nref[2].name="late"\nref[2][1]=false',
    '{data=ref[1],empty=ref[3],literal={ref=1}}', 3));
  assert.equal(parsed.data.later.name, 'late'); assert.equal(parsed.data.later['1'], false);
  assert.ok(Array.isArray(parsed.empty)); assert.equal(parsed.empty.length, 0);
  assert.equal(parsed.literal.ref, 1);
});
test('reference objects do not mutate JavaScript prototypes', () => {
  const parsed = parseSavedLua(refSource('ref[1]["__proto__"]={polluted=true}\nref[1].constructor=0'));
  assert.equal(Object.getPrototypeOf(parsed.counts), null);
  assert.equal(parsed.counts.__proto__.polluted, true);
  assert.equal({}.polluted, undefined);
  assert.equal(parsed.counts.constructor, 0);
});
test('reference allocator recognizes only its fixed declaration and loop grammar', () => {
  const valid = refSource('ref[1].n=0');
  for (const changed of [valid.replace('local ref', 'local other'),
    valid.replace('k=1,1', 'k=0,1'), valid.replace('k=1,1', 'k=1,0'),
    valid.replace('k=1,1', 'k=1,01'), valid.replace('k=1,1', 'k=1,16385'),
    valid.replace('ref[k] = {}', 'ref[k] = run_game()'),
    valid.replace('do ref[k]', 'do notify(); ref[k]'),
    valid.replace('end\n', 'end; run_game()\n')])
    assert.throws(() => parseSavedLua(changed), /Unsupported SavedVariables/);
});
test('references require declared positive integer slots and unique field assignments', () => {
  for (const body of ['{x=ref[0]}', '{x=ref[-1]}', '{x=ref[2]}', '{x=ref[1.0]}',
    '{x=ref[1+0]}', '{x=ref[1].n}'])
    assert.throws(() => parseSavedLua(refSource('ref[1].n=0', body)), /Unsupported SavedVariables/);
  assert.throws(() => parseSavedLua('RRECollectorData={x=ref[1]}'), /undeclared/);
  for (const writes of ['ref[1].n=0\nref[1]["n"]=1', 'ref[1]={n=0}',
    'ref[1].n=os.execute("anything")', 'ref[1].n=function() end'])
    assert.throws(() => parseSavedLua(refSource(writes)), /Unsupported SavedVariables/);
});
test('self and mutual reference cycles are rejected including unused tables', () => {
  for (const source of [refSource('ref[1].self=ref[1]'),
    refSource('ref[1].other=ref[2]\nref[2].other=ref[1]', '{unused=true}', 2)])
    assert.throws(() => parseSavedLua(source), /cyclic table reference/);
});
test('reference expansion enforces depth and expanded node count', () => {
  const chain = Array.from({length: 49}, (_, i) => `ref[${i + 1}].next=ref[${i + 2}]`).join('\n');
  assert.throws(() => parseSavedLua(refSource(chain, '{x=ref[1]}', 50)), /expanded table nesting/);
  const tree = Array.from({length: 16}, (_, i) => `ref[${i + 1}].a=ref[${i + 2}]\nref[${i + 1}].b=ref[${i + 2}]`).join('\n');
  assert.throws(() => parseSavedLua(refSource(tree + '\nref[17].n=0', '{x=ref[1]}', 17)), /expanded value limit/);
});
test('reference expansion bounds repeated large string values and keys per occurrence', () => {
  const body = '{a=ref[1],b=ref[1],c=ref[1],d=ref[1],e=ref[1]}';
  assert.throws(() => parseSavedLua(refSource('ref[1].name="' + 'x'.repeat(500_000) + '"', body)), /expanded string and key byte limit/);
  assert.throws(() => parseSavedLua(refSource('ref[1]["' + 'k'.repeat(500_000) + '"]=0', body)), /expanded string and key byte limit/);
});
test('reference encoding keeps exact root contracts and rejects trailing executable code', () => {
  const source = refSource('ref[1].n=0');
  assert.throws(() => parseSavedLua(source + '\nRRECollectorData={}'), /trailing code/);
  assert.throws(() => parseSavedLua(source + '\nrun_game()'), /trailing code/);
  const casting = refSource('ref[1].n=0', '{sample=ref[1]}', 1, 'RiftReader2CastingEvidence');
  assert.equal(parseSavedLua(casting, 'RiftReader2CastingEvidence').sample.n, 0);
  assert.throws(() => parseSavedLua(casting), /unexpected SavedVariables assignment/);
  assert.throws(() => parseSavedLua(source, 'OtherGlobal'), /assignment contract/);
});

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

test("decoder rejects unescaped line breaks in Lua short strings", () => {
  for (const raw of ["line\nbreak", "line\r\nbreak", "line\rbreak"]) {
    assert.throws(
      () => parseSavedLua('RRECollectorData = { description = "' + raw + '" }'),
      /unescaped newline/
    );
  }
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

test("saved reader rejects malformed raw ability fields before the crosswalk drops them", () => {
  const bad = 'RRECollectorData = {addonVersion="0.4.14", sequence=7, latest={addonVersion="0.4.14", sequence=7, captureComplete=true, abilityList={apiAvailable=true, enumerationComplete=true, detailFailures=0, ignored=0, truncated=0, uniqueCount=1, detailCount=1, rawEntries=1}, player={id="uFIXTURE", name="Fixture"}, roleSlot=1, frameTime=10, realTime=20, capabilities={player=true, experience=false}, abilities={{lookupId="A0000000100000000", name="Fixture", passive={}}}}}';
  assert.throws(() => exportSavedSnapshot(Buffer.from(bad)), /ability-field-not-scalar/);
  const corrected = Buffer.from(bad.replace("passive={}", "passive=false, cooldown=0"));
  const result = exportSavedSnapshot(corrected);
  assert.equal(result.structure.offlineStructureQualified, true);
  assert.equal(result.abilities[0].passive, false);
  assert.equal(result.abilities[0].cooldown, 0);
});

const decodeDecimal = body => parseSavedLua('RRECollectorData={name="' + body + '"}').name;
test("Lua decimal escapes reconstruct UTF-8 bytes without mojibake", () => {
  assert.equal(decodeDecimal(String.raw`Caf\195\169`), "Café");
  assert.equal(decodeDecimal(String.raw`São \240\159\152\128`), "São 😀");
  assert.equal(decodeDecimal(String.raw`one\n\t\r\\\"`), "one\n\t\r\\\"");
});
test("invalid decimal-escaped UTF-8 rejects instead of inventing characters", () => {
  assert.throws(() => decodeDecimal(String.raw`bad\256`), /decimal escape out of range/);
  assert.throws(() => decodeDecimal(String.raw`bad\195`), /invalid UTF-8 in quoted string/);
});
test("SavedSource export preserves escaped UTF-8 names plus false and zero", () => {
  const capture = Buffer.from(String.raw`RRECollectorData = {addonVersion="0.4.14", sequence=7, latest={addonVersion="0.4.14", sequence=7, captureComplete=true, abilityList={apiAvailable=true, enumerationComplete=true, detailFailures=0, ignored=0, truncated=0, uniqueCount=1, detailCount=1, rawEntries=1}, player={id="uFIXTURE", name="Caf\195\169"}, roleSlot=1, frameTime=10, realTime=20, capabilities={player=true, experience=false}, abilities={{lookupId="A0000000100000000", name="São \240\159\152\128", passive=false, cooldown=0}}}}`);
  const snapshot = exportSavedSnapshot(capture);
  assert.equal(snapshot.context.player.name, "Café");
  assert.equal(snapshot.abilities[0].name, "São 😀");
  assert.equal(snapshot.abilities[0].passive, false);
  assert.equal(snapshot.abilities[0].cooldown, 0);
});
