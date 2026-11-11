// RC-33: Calling-neutral RRECollector source contract; no game, VM or external packages.
import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import test from "node:test";
import {fileURLToPath} from "node:url";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const read = relative => fs.readFileSync(path.join(root, relative), "utf8").replace(/\r\n/g, "\n");
const ui = read("addons/RRECollector/ui.lua");
const core = read("addons/RRECollector/core.lua");
const main = read("addons/RRECollector/main.lua");
const candidates = read("addons/RRECollector/candidates.lua");
const abilities = read("addons/RRECollector/abilities.lua");
const context = read("addons/RRECollector/context.lua");
const capabilities = read("addons/RRECollector/capabilities.lua");
const source = JSON.parse(read("docs/REA-RIFT-LAB2-CATALOG-2026-11-07.json"));
const realRogue = source.catalog;

test("original Rogue Bolinao capture has 54/54 valid current ability records", () => {
  assert.equal(realRogue.player.calling, "rogue");
  assert.equal(realRogue.roleSlot, 1);
  assert.equal(realRogue.counts.uniqueCount, 54);
  assert.equal(realRogue.counts.detailCount, 54);
  assert.equal(realRogue.counts.detailFailures, 0);
  assert.equal(realRogue.catalog.length, 54);
  assert.equal(new Set(realRogue.catalog.map(a => a.lookupId)).size, 54);
  for (const a of realRogue.catalog) {
    assert.match(a.lookupId, /^A[0-9A-F]{16}$/);
    assert.ok(typeof a.name === "string" && a.name.length > 0);
  }
});

test("Known mode never restricts API abilities using Warrior historical IDs", () => {
  const records = ui.match(/local function records\(\)([\s\S]*?)\nlocal function loadSlots\(/)?.[1];
  assert.ok(records, "source-extracted record browser");
  assert.match(records, /mode == "static" and soul or "All"/);
  assert.match(records, /type\(a\) == "table" and type\(a\.lookupId\) == "string"/);
  assert.match(records, /local src = warrior and sourceById\[a\.lookupId\] or nil/);
  assert.doesNotMatch(records, /filter == "All" or \(src and src\.soul == filter\)/);
  assert.match(records, /kind = "known", id = a\.lookupId/);
  assert.match(records, /if filter == "All" or src\.soul == filter/);
  assert.match(ui, /soulButton\.setEnabled\(mode == "static"\)/);
  assert.match(ui, /mode, soul, page, selectedId = "known", "All", 1, nil/);
  assert.match(ui, /"Saved " \.\. short\(savedName, 9\)/);
  assert.match(ui, /short\(savedCalling, 9\).*short\(savedCaptureLabel\(\), 27\)/s);
  assert.match(ui, /" #" \.\. tostring\(savedSeq or "\?"\)/);
});

test("Mage, Cleric, Primalist, Rogue and unknown callings use the same API list", () => {
  for (const calling of ["mage", "cleric", "primalist", "rogue", "warrior", "unknown"]) {
    assert.ok(calling.length > 0);
    assert.match(abilities, /local ids, enumeration = abilityIds\(rawList\)/);
    assert.doesNotMatch(abilities, /calling\s*==\s*"warrior"/);
  }
  assert.match(context, /"id", "name", "calling", "level", "role"/);
});

test("Warrior static research is isolated and non-Warrior status is not a retry failure", () => {
  assert.match(candidates, /return nil, "warrior-catalog-not-applicable"/);
  assert.match(candidates, /return nil, "warrior-player-context-not-ready"/);
  assert.match(main, /notApplicable = code == "warrior-catalog-not-applicable"/);
  assert.match(main, /status = notApplicable and "not-applicable" or "deferred"/);
  assert.match(main, /Static candidate research is Warrior-only/);
  assert.match(ui, /"Warrior-only static candidates \| " \.+ soul/);
  assert.match(ui, /"Warrior IDs"/);
  assert.match(ui, /elseif snapshotCalling\(\) == nil or snapshotCalling\(\):lower\(\):find\("warrior"/);
  assert.match(ui, /Warrior-only historical candidates do not apply to saved/);
});

test("SavedVariables damage and first-capture empty slots do not break browsing", () => {
  assert.match(ui, /type\(a\) == "table" and type\(a\.lookupId\) == "string"/);
  assert.match(ui, /type\(entry\) == "table" and type\(entry\.id\) == "string"/);
  assert.match(ui, /type\(counts\) == "table" and counts\.queried/);
  assert.match(ui, /if ready and type\(slots\) == "table" and next\(slots\) == nil/);
  assert.match(ui, /and type\(saved\(\)\.toolbarSlots\) ~= "table"/);
  assert.match(ui, /loadSlots\(\)/);
});

test("Empty API lists, malformed saved counters and bogus prior catalogs are not complete", () => {
  assert.match(abilities, /captureComplete = enumeration.apiAvailable and #ids > 0/);
  assert.match(abilities, /and nonempty\(context\.player\.calling, 128\)/);
  assert.match(abilities, /and shared\.finite\(context\.player\.level\) and context\.player\.level > 0/);
  assert.match(abilities, /if not substantive\(item\) then/);
  assert.match(abilities, /if substantive\(item\) then/);
  assert.match(abilities, /and shared\.finite\(context\.frameTime\) and context\.frameTime >= 0/);
  assert.match(main, /savedSnapshotComplete\(prior\) and record\.captureComplete ~= true/);
  assert.ok(abilities.includes("priorSequence ~= math.floor(priorSequence)"));
  assert.match(abilities, /priorSequence >= 9007199254740991/);
  assert.match(main, /if count < 1 or count > 512 or list.uniqueCount ~= count/);
  assert.match(main, /or type\(latest\.player\.id\) ~= "string" or #latest\.player\.id == 0/);
  assert.match(main, /or not finite\(latest\.player\.level\) or latest\.player\.level <= 0/);
  assert.match(main, /list.detailCount ~= count or list.detailFailures ~= 0/);
  assert.match(main, /list.apiAvailable ~= true or list.enumerationComplete ~= true/);
  assert.match(main, /list.ignored ~= 0 or list.truncated ~= 0/);
  assert.match(main, /not id:match\("\^A\[0-9A-F\]\+\$"\) or seen\[id\]/);
});

test("visible-row action guards block hidden Pin/Check and reset navigation selection", () => {
  assert.match(ui, /local function visibleKnownSelection\(\)/);
  assert.match(ui, /if mode ~= "known" or selectedKind ~= "known"/);
  assert.match(ui, /for i = first, math.min\(first \+ MAX_ROWS - 1, #items\)/);
  assert.match(ui, /if not visibleKnownSelection\(\) or not knownMap\(\)\[selectedId\]/);
  assert.match(ui, /pinControls.pin.setEnabled\(visibleKnownSelection\(\) ~= nil\)/);
  assert.match(ui, /pinControls.check.setEnabled\(visibleKnownSelection\(\) ~= nil\)/);
  assert.match(ui, /pinControls.check = button\("RRECheckSelected"/);
  assert.match(ui, /if visibleKnownSelection\(\) then\s+checked\[selectedId\] = apiCheck\(selectedId\)/);
  assert.match(ui, /selectedId, selectedKind = nil, nil/);
});

test("same-name row IDs and toolbar labels distinguish abilities", () => {
  assert.match(ui, /row.label:SetText\(tag \.\. item.id \.\. "  "/);
  assert.match(ui, /short\(safe\(item.name, item.id\), 30\)/);
  assert.match(ui, /local function fitTileTail\(frame, value\)/);
  assert.match(ui, /second:SetText\(remaining ~= "" and fitTileTail\(second, remaining\) or ""\)/);
});

test("bounded capability index and live wire receipt are not overstated", () => {
  assert.match(capabilities, /if result.index.scanned >= MAX_INDEX_SCAN then/);
  assert.match(main, /wire.receipt\(\) or nil/);
  assert.match(main, /saved API capture and wire publication are separate/);
});

test("Profession discovery is bounded, read-only and keeps snapshots independent", () => {
  assert.match(capabilities, /local function collectProfessions\(\)/);
  assert.match(capabilities, /for _, stem in ipairs\(PROFESSION_STEMS\) do/);
  assert.match(capabilities, /if report\.index\.scanned >= MAX_INDEX_SCAN then/);
  assert.match(capabilities, /if #report\.index\.names < MAX_MATCHES then/);
  assert.match(capabilities, /local docOk, description = pcall\(doc, name\)/);
  assert.doesNotMatch(capabilities, /pcall\(current\s*[,\)]/);
  assert.match(main, /elseif action == "professions" then/);
  assert.match(main, /RRECollectorData\.professionProbe = report/);
  assert.match(main, /RRECollectorData\.professionProbeSequence = sequence/);
  assert.match(main, /nextSequence\(RRECollectorData\.candidateSequence\)/);
  assert.match(main, /nextSequence\(RRECollectorData\.probeSequence\)/);
  assert.match(main, /nextSequence\(RRECollectorData\.professionProbeSequence\)/);
  assert.match(ui, /if length <= 3 then return v:sub\(1, length\) end/);
});

test("saved Rogue browser and toolbar reveal old or incomplete capture provenance", () => {
  assert.match(ui, /local function savedCaptureLabel\(compact\)/);
  assert.match(ui, /version == "\?" and "UNKNOWN "/);
  assert.match(ui, /version ~= runtime\.VERSION and "OLD " or ""/);
  assert.match(ui, /latest\.captureComplete == true\s+and \(compact and "flag:full" or "marked complete"\) or "INCOMPLETE"/);
  assert.match(ui, /short\(savedCaptureLabel\(true\), 22\)/);
  assert.match(ui, /short\(savedCaptureLabel\(true\), 24\)/);
  assert.match(ui, /short\(savedCaptureLabel\(\), 27\)/);
  assert.doesNotMatch(ui, /\| " \.\. soul \.\. " \| " \.\. #list/);
});

test("Navigation discovery ranks sampled names before clipping and keeps receipts isolated", () => {
  assert.match(capabilities, /local function collectNavigation\(\)/);
  assert.match(capabilities, /if report\.index\.scanned >= MAX_INDEX_SCAN then/);
  assert.match(capabilities, /table\.sort\(matched, function\(a, b\)/);
  assert.match(capabilities, /report\.index\.retained = math\.min\(#matched, MAX_MATCHES\)/);
  assert.match(capabilities, /for i = 1, math\.min\(report\.index\.retained, MAX_NAVIGATION_DOCS\) do/);
  assert.match(capabilities, /local docOk, description = pcall\(doc, name\)/);
  assert.match(capabilities, /navigation = collectNavigation/);
  assert.match(main, /elseif action == "navigation" then/);
  assert.match(main, /RRECollectorData\.navigationProbe = report/);
  assert.match(main, /RRECollectorData\.navigationProbeSequence = sequence/);
  assert.match(main, /nextSequence\(RRECollectorData\.navigationProbeSequence\)/);
  const nav = capabilities.split("local function collectNavigation()")[1]?.split("\nRRECollectorRuntime.capabilities =")[0];
  assert.ok(nav, "navigation-specific source body");
  assert.ok(nav.indexOf("table.sort(matched,") < nav.indexOf("report.index.retained ="));
  assert.doesNotMatch(nav, /Command\.[A-Za-z]+\s*\(/);
  assert.doesNotMatch(nav, /Inspect\.Unit\.[A-Za-z]+\s*\(/);
});

test("all bounded documentation receipts preserve UTF-8 character boundaries", () => {
  assert.equal((capabilities.match(/RRECollectorRuntime\.core\.scalar\(description, MAX_DOC\)/g) || []).length, 3);
  assert.doesNotMatch(capabilities, /description:sub\(1, MAX_DOC\)/);
  assert.match(core, /local following = value:byte\(endAt \+ 1\)/);
  assert.match(core, /return value:sub\(1, endAt\)/);
});

test("One version drives toolbar title and startup chat", () => {
  assert.match(ui, /title:SetText\("RRE v" \.\. runtime\.VERSION \.\. " research"\)/);
  assert.match(main, /say\("v" \.\. VERSION \.\. " ready\. \/rre status"\)/);
});
