// Focused, dependency-free source/candidate/manifest guard for RRECollector v0.4.1.
import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import test from "node:test";
import { fileURLToPath } from "node:url";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const read = (relative) => fs.readFileSync(path.join(root, relative), "utf8");
const source = JSON.parse(read("docs/REA-RIFT-SPELLCASTING-SC103-WARRIOR-STATIC-ABILITIES-2026-11-02.json"));
const catalog = read("addons/RRECollector/candidate_catalog.lua");
const candidateLua = read("addons/RRECollector/candidates.lua");
const main = read("addons/RRECollector/main.lua");
const abilities = read("addons/RRECollector/abilities.lua");
const context = read("addons/RRECollector/context.lua");
const core = read("addons/RRECollector/core.lua");
const ui = read("addons/RRECollector/ui.lua");
const toc = read("addons/RRECollector/RiftAddon.toc");

test("96 unique source-hashed Warrior candidate IDs, six named screenshot canaries", () => {
  assert.equal(source.schemaVersion, 1);
  assert.equal(source.records.length, 96);
  assert.equal(new Set(source.records.map(x => x.id)).size, 96);
  assert.deepEqual(Object.fromEntries(["Paladin", "VoidKnight", "Paragon"]
    .map(soul => [soul, source.records.filter(r => r.soul === soul).length])),
    {Paladin:34, VoidKnight:33, Paragon:29});
  assert.equal(source.sourceFiles.length, 3);
  for (const file of source.sourceFiles) assert.match(file.sha256, /^[a-f0-9]{64}$/);
  assert.equal(source.counts.seenInAtankKnown69 + source.counts.absentFromAtankKnown69, 96);
  for (const [id, name] of [
    ["AFDD9D7E2A8F0E50B", "Light's Benediction"],
    ["A768CF3B63EE8D6ED", "Vengeful Decree"],
    ["AFA78C0D582C9F2E5", "Aegis of the Light"],
    ["A37397DC597DDAF03", "Sanctuary"],
    ["A0E2112FD6FE262EE", "Protector's Fury"],
    ["A411792DB5CF7E0E4", "Call of the Divine"],
  ]) assert.ok(source.records.some(x => x.id === id && x.name === name), name);
});

test("Lua catalog matches machine-readable provenance exactly", () => {
  assert.ok(catalog.includes(JSON.stringify(source.catalogVersion)));
  for (const f of source.sourceFiles) assert.ok(catalog.includes(f.sha256));
  const re = /^\s*\{ id = ("(?:\\.|[^"\\])*"), soul = ("(?:\\.|[^"\\])*"), category = ("(?:\\.|[^"\\])*"), name = ("(?:\\.|[^"\\])*") \},?$/gm;
  const observed = [...catalog.matchAll(re)].map((m) => ({
    id: JSON.parse(m[1]), soul: JSON.parse(m[2]),
    category: JSON.parse(m[3]), name: JSON.parse(m[4])
  }));
  assert.equal(observed.length, 96, "all Lua entries parse as quoted scalar IDs/names");
  assert.deepEqual(observed, source.records.map(({id,soul,category,name})=>({id,soul,category,name})));
});

test("RIFT TOC metadata and dependency order are complete", () => {
  for (const field of ["Identifier", "Name", "NameShort", "Description", "Author", "Email", "Version", "Environment"]) {
    assert.match(toc, new RegExp("^" + field + ' = "[^"]+"', "m"));
  }
  assert.match(toc, /^Version = "0\.4\.1"$/m);
  assert.match(toc, /RRECollectorData = "character"/);
  const scripts = [...toc.matchAll(/^\s+"([^"]+\.lua)",?$/gm)].map(m=>m[1]);
  assert.deepEqual(scripts, [
    "core.lua", "context.lua", "abilities.lua", "capabilities.lua",
    "candidate_catalog.lua", "candidates.lua", "ui.lua", "main.lua"
  ]);
  for (const s of scripts) assert.ok(fs.existsSync(path.join(root,"addons/RRECollector",s)));
});

test("candidate probe remains bounded, guarded and separate from known/probe data", () => {
  assert.match(candidateLua, /MAX_CATALOG, MAX_LIST_ENTRIES, MAX_UNLISTED_CANARIES = 128, 1024, 8/);
  assert.match(candidateLua, /pcall\(newApi\.Detail, item\.id\)/);
  assert.match(candidateLua, /counts\.unlistedReturned > 0/);
  assert.match(candidateLua, /not-attempted-canary-stop/);
  assert.doesNotMatch(candidateLua, /RRECollectorData\.(?:latest|probe)\s*=/);
  assert.match(abilities, /copyDetail = function\(detail\)/);
  assert.match(context, /call, finite, scalar = shared\.call, shared\.finite, shared\.scalar/);
  assert.equal([...main.matchAll(/RRECollectorData\.latest = record/g)].length,1);
  assert.equal([...main.matchAll(/RRECollectorData\.probe = report/g)].length,1);
  assert.equal([...main.matchAll(/RRECollectorData\.candidateLookup = report/g)].length,1);
  assert.match(main, /elseif action == "candidates"/);
  assert.match(main, /runCandidateLookup\("startup"\)/);
  assert.match(main, /prior\.catalogVersion == candidateVersion/);
  assert.doesNotMatch(candidateLua, /Command\.(?:Ability|Unit|Input|System|Focus)/);
});

test("read-only toolbar is optional, bound to existing commands and honest about readiness", () => {
  assert.match(core, /VERSION = "0\.4\.1"/);
  assert.match(ui, /UI\.CreateContext\("RRECollectorToolbar"\)/);
  assert.match(ui, /UI\.CreateFrame\("Texture"/);
  assert.match(ui, /UI\.CreateFrame\("RiftButton", name, parent\)/);
  assert.match(ui, /modeButtons\.known\.frame:SetEnabled\(mode ~= "known"\)/);
  assert.match(ui, /pageButtons\.next\.frame:SetEnabled\(page < total\)/);
  assert.match(ui, /row\.setSelected\(/);
  assert.match(ui, /cursor\.In/);
  assert.match(ui, /leftMouse\.Down/);
  assert.match(ui, /RRESlotAccent/);
  assert.match(ui, /Event\.UI\.Input\.Mouse\.Left\.Click/);
  assert.match(ui, /function apiCheck\(id\)/);
  assert.match(ui, /pcall\(fn, id\)/);
  assert.match(ui, /READINESS UNKNOWN/);
  assert.match(ui, /No auto-cast \/ no continuous readiness polling/);
  assert.doesNotMatch(ui, /EventMacroSet|Command\.(?:Ability|Unit|Input|System|Focus)/);
  assert.match(main, /RRECollectorRuntime\.command = function\(raw\) onSlash\(nil, raw\) end/);
  assert.match(main, /RRECollectorData\.candidateAttempt =/);
  assert.match(main, /elseif action == "ui"/);
  assert.match(main, /pcall\(ui\.start\)/);
  assert.match(main, /refreshUI\(true\)/);
});

test("startup context retry is event-driven, bounded, and preserves manual command", () => {
  assert.match(main, /MAX_AUTOMATIC_CANDIDATE_RETRIES = 2/);
  assert.match(main, /trigger == "startup"/);
  assert.match(main, /code == "warrior-player-context-not-ready"/);
  assert.match(main, /Event\.Addon\.Startup\.End/);
  assert.match(main, /Event\.Unit\.Availability\.Full/);
  assert.match(main, /specifier == "player"/);
  assert.match(main, /automaticRetries = automaticCandidateRetries/);
  assert.match(main, /runCandidateLookup\("manual"\)/);
  assert.doesNotMatch(main, /Event\.System\.Update\./);
});
