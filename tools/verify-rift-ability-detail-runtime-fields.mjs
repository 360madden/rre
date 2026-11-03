// SC-103: review sanitized, source-hashed current-client Detail documentation fields.
import assert from "node:assert/strict";
import crypto from "node:crypto";
import fs from "node:fs";
import path from "node:path";
import test from "node:test";
import { fileURLToPath } from "node:url";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const json = JSON.parse(fs.readFileSync(path.join(root,
  "docs/REA-RIFT-SPELLCASTING-SC103-RUNTIME-ABILITY-DETAIL-FIELDS-2026-11-03.json"), "utf8"));
const abilitySrc = fs.readFileSync(path.join(root, "addons/RRECollector/abilities.lua"));
const sha256 = bytes => crypto.createHash("sha256").update(bytes).digest("hex");
const fieldBody = abilitySrc.toString("utf8").match(/local FIELDS = \{([\s\S]*?)\n\}/);
assert.ok(fieldBody, "RRECollector field allowlist missing from source");
const exportedFields = [...fieldBody[1].matchAll(/"([A-Za-z][A-Za-z0-9]*)"/g)].map(m => m[1]);

test("saved-runtime source and field-list integrity", () => {
  assert.equal(json.schemaVersion, 1);
  assert.equal(json.sourceIndex.rrecollectorFieldSource.sha256, sha256(abilitySrc));
  assert.equal(json.sourceIndex.documentation.api, "Inspect.Ability.New.Detail");
  assert.equal(json.sourceIndex.documentation.lengthCharacters, 2711);
  assert.match(json.sourceIndex.documentation.sha256, /^[a-f0-9]{64}$/);
  assert.equal(json.sourceIndex.documentation.truncated, false);
  assert.equal(json.sourceIndex.characterSavedEvidence.containsPeOrClientBuildHash, false);
});

test("34 documented fields exactly match current RRECollector explicit whitelist", () => {
  const observed = json.documentedReturnedMembers;
  assert.equal(observed.length, 34);
  assert.equal(new Set(observed).size, 34);
  assert.deepEqual(observed, [...observed].sort(), "deterministic field order");
  assert.equal(exportedFields.length, 34);
  assert.deepEqual([...exportedFields].sort(), observed);
  assert.deepEqual(json.counts, {
    documentedReturnedMembers:34, rrecollectorExportWhitelistFields:34,
    undocumentedWhitelistFields:0, documentedUncapturedFields:0
  });
});

test("eligibility/variant fields are not documented; export contains no unit values", () => {
  for (const key of json.notDocumentedNames) assert.equal(
    json.documentedReturnedMembers.includes(key), false, key);
  assert.ok(json.documentedReturnedMembers.includes("target"),
    "field name is not a live target ID");
  const serialized = JSON.stringify(json);
  const privateIdPattern = /(?:[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}|u[0-9a-f]{16,})/i;
  assert.match("synthetic@example.invalid", privateIdPattern);
  assert.match("u0123456789abcdef", privateIdPattern);
  assert.doesNotMatch(serialized, privateIdPattern);
  assert.ok(json.limitations.some(x => x.includes("undocumented")),
    "no false claim of exhaustive runtime shape");
});
