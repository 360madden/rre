import test from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import crypto from "node:crypto";
import {parseSavedLua} from "./read-rrecollector-saved.mjs";
import {summarizeProfessionReceipt, readProfessionReceipt} from "./verify-rrecollector-profession-receipt.mjs";

const STEMS = ["Craft","Crafting","Profession","Tradeskill","TradeSkill","Recipe","Fishing","Survival","Skill"];
const PATH_TYPES = STEMS.flatMap(stem => ["List","Detail"].map(suffix =>
  `["Inspect.${stem}.${suffix}"]="nil"`)).join(",");
const DOC_DEFAULT = STEMS.flatMap(stem => ["List","Detail"].map(suffix =>
  `["Inspect.${stem}.${suffix}"]={status="other",returnType="nil"}`)).join(",");

function savedReceipt({rootVersion = "0.4.17", probeVersion = "0.4.17",
  rootSequence = 3, sequence = 3, scanned = 2, matched = 1, retained = 1,
  ignored = 1, truncated = 0, capped = false, schemaVersion = 1,
  docsStatus = "index-available", names = `{"Inspect.Craft.List"}`,
  paths = PATH_TYPES, documents = null, documentErrors = 0} = {}) {
  const emittedDocuments = documents ?? (docsStatus === "missing" ? "{}" : `{${DOC_DEFAULT}}`);
  const schemaField = schemaVersion === null ? "" : `schemaVersion=${schemaVersion},`;
  return parseSavedLua(`RRECollectorData = {
    addonVersion="${rootVersion}", professionProbeSequence=${rootSequence},
    professionProbe={${schemaField}addonVersion="${probeVersion}", sequence=${sequence},
      documentationStatus="${docsStatus}", documentErrors=${documentErrors},
      index={scanned=${scanned}, matched=${matched}, retained=${retained},
        ignored=${ignored}, truncated=${truncated}, scanLimitReached=${capped},
        names=${names}},
      pathTypes={${paths}}, documents=${emittedDocuments}
    }
  }`);
}

test("old saved file has no profession receipt, never claims discovery", () => {
  const saved = parseSavedLua(`RRECollectorData={addonVersion="0.4.14",latest={}}`);
  const result = summarizeProfessionReceipt(saved, {sha256: "a".repeat(64), bytes: 40});
  assert.equal(result.status, "not-captured");
  assert.equal(result.scanCompleteness, "unknown");
  assert.equal(result.actualProfessionDataVerified, false);
  assert.equal(result.inGameLoadVerified, false);
});

test("bounded index returns only safe counts and candidate exact paths", () => {
  const saved = savedReceipt({paths: PATH_TYPES.replace(`["Inspect.Craft.List"]="nil"`,
    `["Inspect.Craft.List"]="function"`)});
  const result = summarizeProfessionReceipt(saved, {sha256: "b".repeat(64), bytes: 900});
  assert.equal(result.status, "observed-bounded");
  assert.equal(result.scanCompleteness, "bounded-index-observed");
  assert.deepEqual(result.callablePaths, ["Inspect.Craft.List"]);
  assert.equal(result.candidatePathTypes["Inspect.Craft.List"], "function");
  assert.equal(Object.keys(result.candidatePathTypes).length, 18);
  assert.equal(result.candidatePathsChecked, 18);
  assert.equal(result.scan.retained, 1);
  assert.equal(result.versionBound, true);
  assert.equal(result.sequenceBound, true);
  assert.equal(result.actualProfessionDataVerified, false);
  assert.equal(Object.hasOwn(result, "player"), false);
  assert.equal(Object.hasOwn(result, "names"), false);
});

test("exact documentation statuses are summarized without exposing text", () => {
  const documents = `{${DOC_DEFAULT.replace(`["Inspect.Craft.List"]={status="other",returnType="nil"}`,
    `["Inspect.Craft.List"]={status="returned",text="API detail",textTruncated=false}`)
    .replace(`["Inspect.Craft.Detail"]={status="other",returnType="nil"}`,
      `["Inspect.Craft.Detail"]={status="error"}`)}}`;
  const result = summarizeProfessionReceipt(savedReceipt({documents, documentErrors:1}));
  assert.deepEqual(result.documentedPaths, ["Inspect.Craft.List"]);
  assert.equal(result.documentsReturned, 1);
  assert.equal(result.documentErrors, 1);
  assert.equal(JSON.stringify(result).includes("API detail"), false);
  assert.throws(() => summarizeProfessionReceipt(savedReceipt({documents, documentErrors:0})),
    /DOCUMENT_ERRORS_CONTRADICTION/);
});

test("over 2048 unordered API index entries is explicitly inconclusive", () => {
  const result = summarizeProfessionReceipt(savedReceipt({scanned: 2048, matched: 0,
    retained: 0, ignored: 2048, capped: true, names: "{}"}));
  assert.equal(result.status, "observed-partial");
  assert.equal(result.scanCompleteness, "partial-capped");
  assert.equal(result.scan.scanLimitReached, true);
  assert.deepEqual(result.callablePaths, []);
  assert.equal(result.actualProfessionDataVerified, false);
});

test("matching names truncated at 96 are reported as partial too", () => {
  const names = "{" + Array.from({length:96}, (_, i) =>
    `Inspect.Craft.Item${i}`).sort().map(JSON.stringify).join(",") + "}";
  const result = summarizeProfessionReceipt(savedReceipt({scanned: 97, matched:97,
    retained:96, ignored:0, truncated:1, names}));
  assert.equal(result.status, "observed-partial");
  assert.equal(result.scan.truncated, 1);
});

test("version and sequence mismatches are not accepted as current", () => {
  assert.equal(summarizeProfessionReceipt(savedReceipt({rootVersion:"0.4.16"})).status,
    "stale-or-unbound");
  assert.equal(summarizeProfessionReceipt(savedReceipt({rootSequence:2})).status,
    "stale-or-unbound");
});

test("unavailable documentation is not mistaken for absent profession APIs", () => {
  const result = summarizeProfessionReceipt(savedReceipt({scanned:0, matched:0,
    retained:0, ignored:0, names:"{}", docsStatus:"missing"}));
  assert.equal(result.status, "observed-without-index");
  assert.equal(result.scanCompleteness, "documentation-unavailable");
});

test("malformed counts, paths and unsafe Lua expressions are rejected", () => {
  assert.throws(() => summarizeProfessionReceipt(savedReceipt({ignored:2})),
    /INDEX_COUNTER_CONTRADICTION/);
  assert.throws(() => summarizeProfessionReceipt(savedReceipt({scanned:2047,
    matched:0, retained:0, ignored:2047, capped:true, names:"{}"})),
    /INDEX_COUNTER_CONTRADICTION/);
  assert.throws(() => summarizeProfessionReceipt(savedReceipt({scanned:2, matched:2,
    retained:1, ignored:0, truncated:1, names:`{"Inspect.Craft.List"}`})),
    /INDEX_COUNTER_CONTRADICTION/);
  assert.throws(() => summarizeProfessionReceipt(savedReceipt({paths:`["Inspect.Craft.List"]="function"`})),
    /PATH_TYPES_COUNT_MISMATCH/);
  assert.throws(() => parseSavedLua(`RRECollectorData=os.execute("invalid")`),
    /only literal Lua values/);
});

test("profession receipt requires its actual schema and matching index status", () => {
  assert.throws(() => summarizeProfessionReceipt(savedReceipt({schemaVersion:null})),
    /PROFESSION_SCHEMA_MALFORMED/);
  assert.throws(() => summarizeProfessionReceipt(savedReceipt({schemaVersion:2})),
    /PROFESSION_SCHEMA_MALFORMED/);
  assert.throws(() => summarizeProfessionReceipt(savedReceipt({docsStatus:"missing"})),
    /INDEX_UNAVAILABLE_CONTRADICTION/);
  assert.throws(() => summarizeProfessionReceipt(savedReceipt({docsStatus:"index-error"})),
    /INDEX_UNAVAILABLE_CONTRADICTION/);
  assert.equal(summarizeProfessionReceipt(savedReceipt({scanned:0, matched:0,
    retained:0, ignored:0, names:"{}", docsStatus:"index-non-table"})).status,
    "observed-without-index");
});

test("names must be unique, ordered, bounded UTF-8 and profession-filtered", () => {
  assert.throws(() => summarizeProfessionReceipt(savedReceipt({names:`{"Unrelated.Call"}`})),
    /INDEX_NAMES_MALFORMED/);
  assert.throws(() => summarizeProfessionReceipt(savedReceipt({names:`{"Inspect.Other.List"}`})),
    /INDEX_NAMES_MALFORMED/);
  assert.throws(() => summarizeProfessionReceipt(savedReceipt({names:`{"Inspect.Craft.${"é".repeat(80)}"}`})),
    /INDEX_NAMES_MALFORMED/);
  const duplicate = `{"Inspect.Craft.List","Inspect.Craft.List"}`;
  assert.throws(() => summarizeProfessionReceipt(savedReceipt({scanned:2, matched:2,
    ignored:0, retained:2, names:duplicate})), /INDEX_NAMES_MALFORMED/);
  const outOfOrder = `{"Inspect.Fishing.List","Inspect.Craft.List"}`;
  assert.throws(() => summarizeProfessionReceipt(savedReceipt({scanned:2, matched:2,
    ignored:0, retained:2, names:outOfOrder})), /INDEX_NAMES_MALFORMED/);
  const valid = `{"Command.Craft.List","Event.Fishing.List"}`;
  assert.equal(summarizeProfessionReceipt(savedReceipt({scanned:2, matched:2,
    ignored:0, retained:2, names:valid})).status, "observed-bounded");
});

test("documentation entries are complete and exactly cover candidate paths", () => {
  assert.throws(() => summarizeProfessionReceipt(savedReceipt({documents:"{}"})),
    /DOCUMENTS_MALFORMED/);
  assert.throws(() => summarizeProfessionReceipt(savedReceipt({docsStatus:"missing",
    scanned:0, matched:0, retained:0, ignored:0, names:"{}",
    documents:`{${DOC_DEFAULT}}`})), /DOCUMENTS_MALFORMED/);
  const returned = DOC_DEFAULT.replace(`["Inspect.Craft.List"]={status="other",returnType="nil"}`,
    `["Inspect.Craft.List"]={status="returned",text="ok",textTruncated=false}`);
  assert.equal(summarizeProfessionReceipt(savedReceipt({documents:`{${returned}}`})).documentsReturned, 1);
  assert.throws(() => summarizeProfessionReceipt(savedReceipt({documents:`{${returned.replace("textTruncated=false", "badFlag=false")}}`})),
    /DOCUMENT_ENTRY_MALFORMED/);
  assert.throws(() => summarizeProfessionReceipt(savedReceipt({documents:`{${returned.replace('text="ok"', `text="${"é".repeat(257)}"`)}}`})),
    /DOCUMENT_ENTRY_MALFORMED/);
  assert.throws(() => summarizeProfessionReceipt(savedReceipt({documents:`{${DOC_DEFAULT.replace("returnType=\"nil\"", "returnType=\"unknown\"")}}`})),
    /DOCUMENT_ENTRY_MALFORMED/);
});

test("original-file reader verifies bytes, expected version and bounded parsing", () => {
  const scratch = fs.mkdtempSync(path.join(os.tmpdir(), "rre-profession-fixture-"));
  const filename = path.join(scratch, "RRECollector.lua");
  try {
    const bytes = Buffer.from(`RRECollectorData={addonVersion="0.4.14",latest={}}`, "utf8");
    fs.writeFileSync(filename, bytes);
    const receipt = readProfessionReceipt(filename, "0.4.14");
    assert.equal(receipt.status, "not-captured");
    assert.equal(receipt.sourceBytes, bytes.length);
    assert.equal(receipt.sourceSha256, crypto.createHash("sha256").update(bytes).digest("hex"));
    assert.throws(() => readProfessionReceipt(filename, "0.4.17"), /SOURCE_VERSION_MISMATCH/);
    assert.throws(() => readProfessionReceipt(filename, "invalid"), /REQUIRED_VERSION_INVALID/);
    fs.writeFileSync(filename, Buffer.from([0xff,0xfe]));
    assert.throws(() => readProfessionReceipt(filename, "0.4.14"), /valid for encoding utf-8/i);
  } finally {
    fs.rmSync(scratch, {recursive:true});
  }
});
