// SC-103 continuation: source-pinned crosswalk of six UI tooltip candidates to RC-29 Detail.
import assert from "node:assert/strict";
import crypto from "node:crypto";
import fs from "node:fs";
import path from "node:path";
import test from "node:test";
import { fileURLToPath } from "node:url";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
function pinnedJson(relative, expectedHash) {
  const bytes = fs.readFileSync(path.join(root, relative));
  const actual = crypto.createHash("sha256").update(bytes).digest("hex");
  assert.equal(actual, expectedHash, relative + " source changed; review the crosswalk");
  return JSON.parse(bytes.toString("utf8"));
}
const atlas = pinnedJson(
  "docs/REA-RIFT-SPELLCASTING-SC103-353-ID-DETAIL-ATLAS-2026-11-03.json",
  "5da0b32bc6fd67e86b883d44155c86fb5ff05cab1655b216ebed2fb4e5cd5fb7"
);
const tooltips = pinnedJson(
  "docs/REA-RIFT-SPELLCASTING-SC103-PALADIN-TOOLTIP-METADATA-2026-11-02.json",
  "d9008e8d64860858299ea975817263c8cd2373d81f703c448b7ea2c7c8a65c43"
);
const index = new Map(atlas.records.map(r => [r.id, r]));
const joined = tooltips.abilities.map(ui => ({ui, api:index.get(ui.id)}));

test("six static tooltip IDs join exactly, remain absent from prior API List", () => {
  assert.equal(joined.length, 6);
  assert.equal(new Set(joined.map(x => x.ui.id)).size, 6);
  for (const {ui, api} of joined) {
    assert.ok(api, ui.name + " has exact-ID record");
    assert.equal(api.id, ui.id);
    assert.equal(api.name, ui.name);
    assert.equal(api.sourceSoul, "Paladin");
    assert.equal(api.historicalStaticSource, true);
    assert.equal(api.priorKnownApiList, "not-listed-in-preserved-69");
    assert.equal(api.unlockState, "unknown");
    assert.equal(api.learnableNow, "unknown");
    assert.equal(api.currentlyCastable, "unknown");
  }
});

test("five returned unusable=true; Protector's Fury no Detail does not imply locked", () => {
  const positive = joined.filter(x => x.api.explicitIdDetail?.status === "returned");
  const absent = joined.filter(x => x.api.explicitIdDetail?.status === "no-detail");
  assert.equal(positive.length, 5);
  assert.deepEqual(absent.map(x => x.ui.name), ["Protector's Fury"]);
  for (const {api} of positive) assert.equal(api.explicitIdDetail.detail?.unusable, true);
  assert.equal(absent[0].api.explicitIdDetail.detail, undefined);
});

test("four visible tooltip cooldowns match positive current-client Detail within float tolerance", () => {
  const matched = joined.filter(x => typeof x.ui.cooldownSeconds === "number");
  assert.equal(matched.length, 4);
  for (const {ui, api} of matched) {
    assert.equal(api.explicitIdDetail.status, "returned", ui.name);
    const value = api.explicitIdDetail.detail?.cooldown;
    assert.equal(typeof value, "number", ui.name);
    assert.ok(Math.abs(value - ui.cooldownSeconds) < 0.001, ui.name);
  }
  const noDisplay = joined.filter(x => x.ui.cooldownSeconds === null);
  assert.equal(noDisplay.length, 2);
});
