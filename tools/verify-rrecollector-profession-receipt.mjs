// Read-only, bounded RRECollector profession API discovery receipt.
// Usage: node tools/verify-rrecollector-profession-receipt.mjs <RRECollector.lua> [--require-version 0.4.17]
// Parsed data never executes as Lua. A receipt does not establish live freshness or usable crafting APIs.
import fs from "node:fs";
import path from "node:path";
import crypto from "node:crypto";
import {fileURLToPath} from "node:url";
import {parseSavedLuaBytes} from "./read-rrecollector-saved.mjs";

const STEMS = ["Craft","Crafting","Profession","Tradeskill","TradeSkill","Recipe","Fishing","Survival","Skill"];
const PATHS = STEMS.flatMap(stem => [`Inspect.${stem}.List`, `Inspect.${stem}.Detail`]);
const TYPES = new Set(["nil","error","function","table","number","string","boolean","thread","userdata"]);
const STATUSES = new Set(["missing","index-error","index-non-table","index-available"]);
const PROFESSION_TERMS = ["craft","profession","tradeskill","recipe","fishing","survival"];
const PROFESSION_PREFIXES = ["Inspect.","Command.","Event."];
const UTF8_LENGTH = value => Buffer.byteLength(value, "utf8");
const SHA = bytes => crypto.createHash("sha256").update(bytes).digest("hex");
const validVersion = v => typeof v === "string" && /^0\.[0-9]{1,3}\.[0-9]{1,3}$/.test(v);
const integer = (n, max) => Number.isSafeInteger(n) && n >= 0 && n <= max;
const object = v => v !== null && typeof v === "object" && !Array.isArray(v);
const check = (condition, label) => { if (!condition) throw new Error(label); };

function luaArray(value) {
  if (Array.isArray(value)) return value;
  check(object(value), "NAMES_MALFORMED");
  const keys = Object.keys(value);
  check(keys.every((key, i) => key === String(i + 1)), "NAMES_MALFORMED");
  return keys.map(key => value[key]);
}

export function summarizeProfessionReceipt(saved, source = {}) {
  check(object(saved), "SAVED_ROOT_MALFORMED");
  const base = {
    schemaVersion: 1, sourceKind: "single stable SavedVariables file; offline API-discovery evidence only",
    sourceSha256: source.sha256 ?? null, sourceBytes: source.bytes ?? null,
    savedAddonVersion: validVersion(saved.addonVersion) ? saved.addonVersion : null,
    inGameLoadVerified: false, freshCaptureVerified: false, actualProfessionDataVerified: false,
    evidenceLimit: "Names and types do not prove usable crafting APIs or character profession coverage.",
  };
  if (saved.professionProbe === undefined || saved.professionProbe === null)
    return {...base, status: "not-captured", probeVersion: null,
      sequenceBound: false, scanCompleteness: "unknown", callablePaths: []};

  const probe = saved.professionProbe;
  // Empty Lua '{}' decodes to [] in the existing literal-only reader.
  check(object(probe) && object(probe.index) && object(probe.pathTypes)
    && (object(probe.documents) || Array.isArray(probe.documents)
      && probe.documents.length === 0), "PROFESSION_PROBE_MALFORMED");
  check(probe.schemaVersion === 1, "PROFESSION_SCHEMA_MALFORMED");
  check(validVersion(probe.addonVersion), "PROFESSION_VERSION_MALFORMED");
  check(STATUSES.has(probe.documentationStatus), "DOCUMENTATION_STATUS_MALFORMED");
  check(integer(probe.sequence, Number.MAX_SAFE_INTEGER) && probe.sequence > 0,
    "PROFESSION_SEQUENCE_MALFORMED");
  const idx = probe.index;
  for (const [key, maximum] of Object.entries({scanned: 2048, matched: 2048,
    retained: 96, ignored: 2048, truncated: 2048}))
    check(integer(idx[key], maximum), "INDEX_COUNTER_MALFORMED");
  check(typeof idx.scanLimitReached === "boolean" && idx.matched + idx.ignored === idx.scanned
    && idx.retained + idx.truncated === idx.matched
    && (idx.truncated === 0 || idx.retained === 96)
    && (!idx.scanLimitReached || idx.scanned === 2048), "INDEX_COUNTER_CONTRADICTION");
  const names = luaArray(idx.names);
  check(names.length === idx.retained
    && names.every(name => typeof name === "string" && UTF8_LENGTH(name) > 0
      && UTF8_LENGTH(name) <= 160 && PROFESSION_PREFIXES.some(prefix => name.startsWith(prefix))
      && PROFESSION_TERMS.some(term => name.toLowerCase().includes(term)))
    && names.every((name, i) => i === 0
      || Buffer.compare(Buffer.from(names[i - 1], "utf8"), Buffer.from(name, "utf8")) < 0),
    "INDEX_NAMES_MALFORMED");
  if (probe.documentationStatus !== "index-available")
    check(idx.scanned === 0 && idx.matched === 0 && idx.retained === 0
      && idx.ignored === 0 && idx.truncated === 0 && !idx.scanLimitReached,
      "INDEX_UNAVAILABLE_CONTRADICTION");
  check(Object.keys(probe.pathTypes).length === PATHS.length, "PATH_TYPES_COUNT_MISMATCH");
  const callablePaths = [], candidatePathTypes = {}, pathTypeCounts = {function: 0, nil: 0, other: 0};
  for (const key of PATHS) {
    const kind = probe.pathTypes[key];
    check(TYPES.has(kind), "PATH_TYPE_MALFORMED");
    candidatePathTypes[key] = kind;
    if (kind === "function") { callablePaths.push(key); pathTypeCounts.function++; }
    else if (kind === "nil") pathTypeCounts.nil++;
    else pathTypeCounts.other++;
  }
  const docKeys = Object.keys(probe.documents);
  const expectedDocuments = probe.documentationStatus === "missing" ? 0 : PATHS.length;
  check(docKeys.length === expectedDocuments && docKeys.every(key => PATHS.includes(key)),
    "DOCUMENTS_MALFORMED");
  let errors = 0, returned = 0;
  const documentedPaths = [];
  for (const key of docKeys) {
    const item = probe.documents[key];
    check(object(item) && ["error","other","returned"].includes(item.status),
      "DOCUMENT_ENTRY_MALFORMED");
    if (item.status === "error") errors++;
    if (item.status === "other")
      check(TYPES.has(item.returnType) && item.returnType !== "error",
        "DOCUMENT_ENTRY_MALFORMED");
    if (item.status === "returned") {
      check(typeof item.text === "string" && UTF8_LENGTH(item.text) <= 512
        && typeof item.textTruncated === "boolean", "DOCUMENT_ENTRY_MALFORMED");
      returned++; documentedPaths.push(key);
    }
  }
  check(integer(probe.documentErrors, PATHS.length) && probe.documentErrors === errors,
    "DOCUMENT_ERRORS_CONTRADICTION");
  const sequenceBound = saved.professionProbeSequence === probe.sequence;
  const versionBound = saved.addonVersion === probe.addonVersion;
  const scanCompleteness = idx.scanLimitReached || idx.truncated > 0
    ? "partial-capped" : probe.documentationStatus === "index-available"
      ? "bounded-index-observed" : "documentation-unavailable";
  const status = !sequenceBound || !versionBound ? "stale-or-unbound"
    : scanCompleteness === "partial-capped" ? "observed-partial"
      : scanCompleteness === "bounded-index-observed" ? "observed-bounded"
        : "observed-without-index";
  return {...base, status, probeVersion: probe.addonVersion, probeSequence: probe.sequence,
    sequenceBound, versionBound, documentationStatus: probe.documentationStatus,
    scanCompleteness, scan: {scanned: idx.scanned, matched: idx.matched,
      retained: idx.retained, ignored: idx.ignored, truncated: idx.truncated,
      scanLimitReached: idx.scanLimitReached},
    candidatePathsChecked: PATHS.length, candidatePathTypes, callablePaths, pathTypeCounts,
    documentedPaths, documentsReturned: returned, documentErrors: errors};
}

export function readProfessionReceipt(originalPath, requiredVersion) {
  check(path.basename(originalPath) === "RRECollector.lua", "ONLY_RRECOLLECTOR_SAVED_FILE");
  if (requiredVersion !== undefined) check(validVersion(requiredVersion), "REQUIRED_VERSION_INVALID");
  const beforeName = fs.lstatSync(originalPath);
  check(beforeName.isFile() && !beforeName.isSymbolicLink(), "SOURCE_NOT_PLAIN_FILE");
  const fd = fs.openSync(originalPath, "r");
  try {
    const before = fs.fstatSync(fd);
    const same = item => item.dev === before.dev && item.ino === before.ino
      && item.size === before.size && item.mtimeMs === before.mtimeMs
      && item.ctimeMs === before.ctimeMs;
    check(same(beforeName), "SOURCE_CHANGED_BEFORE_READ");
    check(before.size <= 2_000_000, "SOURCE_TOO_LARGE");
    const bytes = fs.readFileSync(fd);
    check(bytes.length === before.size && same(fs.fstatSync(fd))
      && same(fs.statSync(originalPath)), "SOURCE_CHANGED_DURING_READ");
    const saved = parseSavedLuaBytes(bytes);
    if (requiredVersion !== undefined)
      check(saved.addonVersion === requiredVersion, "SOURCE_VERSION_MISMATCH");
    return summarizeProfessionReceipt(saved, {sha256: SHA(bytes), bytes: bytes.length});
  } finally { fs.closeSync(fd); }
}

if (process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  try {
    const args = process.argv.slice(2);
    check(args.length === 1 || args.length === 3 && args[1] === "--require-version",
      "INVALID_CLI_ARGUMENTS");
    const result = readProfessionReceipt(args[0], args[2]);
    process.stdout.write(JSON.stringify(result) + "\n");
  } catch (error) {
    const message = String(error?.message || "SOURCE_READ_OR_PARSE_FAILED");
    const reason = /^[A-Z][A-Z0-9_]*$/.test(message) ? message : "SOURCE_READ_OR_PARSE_FAILED";
    process.stderr.write(JSON.stringify({status: "failed", reason}) + "\n");
    process.exitCode = 1;
  }
}
