// RC-30 read-only persisted-state receipt. Never execute Lua or expose original IDs.
// Usage: node tools/rc30-saved-receipt.mjs <original RRECollector.lua> [--expected-sha <64 hex>] [--require-version 0.4.10]
// This proves saved bytes, not in-game Pin -> Undo or their process/session writer.
import fs from "node:fs";
import path from "node:path";
import crypto from "node:crypto";
import { fileURLToPath } from "node:url";
import { parseSavedLua, assessSnapshotForComparison } from "./read-rrecollector-saved.mjs";

const ID = /^A[0-9A-Fa-f]{16}$/;
const HEX64 = /^[0-9a-fA-F]{64}$/;
const VERSION = /^0\.[0-9]+\.[0-9]+$/;
const OUTPUT_VERSION = /^0\.[0-9]{1,3}\.[0-9]{1,3}$/;
const MAX_BYTES = 2_000_000;
const sha256 = (bytes) => crypto.createHash("sha256").update(bytes).digest("hex");

function numericKeys(value, label, maximum) {
  if (value == null) return [];
  if (Array.isArray(value)) {
    if (value.length > maximum) throw new Error(label + "_OVER_LIMIT");
    return Array.from(value, (v, i) => [i + 1, v]);
  }
  if (typeof value !== "object") throw new Error(label + "_INVALID_TYPE");
  const result = [];
  for (const [key, val] of Object.entries(value)) {
    if (!/^(?:[1-9][0-9]*)$/.test(key)) throw new Error(label + "_BAD_KEY");
    const n = Number(key);
    if (!Number.isSafeInteger(n) || n > maximum) throw new Error(label + "_OVER_LIMIT");
    result.push([n, val]);
  }
  return result.sort(([a], [b]) => a - b);
}

function buildSlotArray(storage) {
  const slots = Array(8).fill(null);
  for (const [index, value] of numericKeys(storage, "TOOLBAR", 8)) {
    // No 0-based fallback: an absent eighth slot must never duplicate slot 7.
    slots[index - 1] = value;
  }
  return slots;
}

export function buildReceipt(saved, source) {
  if (!saved || typeof saved !== "object" || Array.isArray(saved))
    throw new Error("INVALID_LUA_ROOT");
  const slots = buildSlotArray(saved.toolbarSlots);
  const knownRows = numericKeys(saved.latest?.abilities, "KNOWN_ABILITY", 10000);
  const candidateRows = numericKeys(saved.candidateLookup?.entries, "CANDIDATE", 10000);
  const known = new Set();
  for (const [, value] of knownRows) {
    const id = value?.lookupId;
    if (typeof id === "string" && ID.test(id)) known.add(id.toUpperCase());
  }
  const statuses = Object.create(null);
  for (const [, entry] of candidateRows) {
    const value = entry && typeof entry.status === "string" ? entry.status : "";
    // Only source-defined categories may be printed; never echo arbitrary saved text.
    const kind = ["returned","listed-not-queried","no-detail"].includes(value)
      ? value : value ? "other" : "not-recorded";
    if (Object.keys(statuses).length >= 24 && !Object.hasOwn(statuses, kind))
      throw new Error("TOO_MANY_CANDIDATE_STATUSES");
    statuses[kind] = (statuses[kind] || 0) + 1;
  }
  const canonical = [];
  const slotStates = [];
  const seen = new Set();
  let validPins = 0, duplicatePins = 0, validKnown = 0, unknownToKnown = 0;
  for (const v of slots) {
    if (v === null || v === undefined) {
      canonical.push(null);
      slotStates.push("empty");
      continue;
    }
    if (typeof v !== "string" || !ID.test(v)) {
      canonical.push({ kind: "invalid", type: typeof v });
      slotStates.push("invalid-stored-value");
      continue;
    }
    const id = v.toUpperCase();
    canonical.push(id);
    slotStates.push("ability-id");
    validPins++;
    if (seen.has(id)) duplicatePins++;
    seen.add(id);
    if (known.has(id)) validKnown++;
    else unknownToKnown++;
  }
  // An absent table or malformed value has no trustworthy comparable baseline.
  // Never hash the redacted type placeholder as if it identified original bytes.
  const slotFingerprintComplete = saved.toolbarSlots != null &&
    !slotStates.includes("invalid-stored-value");
  return {
    schemaVersion: 1,
    sourceKind: "single stable read of original RRECollector SavedVariables; G1 saved data only",
    sourceFilename: "RRECollector.lua",
    observedAtUtc: source.observedAtUtc,
    modifiedAtUtc: source.modifiedAtUtc,
    sourceSha256: source.sha256,
    sourceBytes: source.bytes,
    addonVersion: typeof saved.addonVersion === "string" && OUTPUT_VERSION.test(saved.addonVersion)
      ? saved.addonVersion : null,
    latestKnownCount: knownRows.length,
    latestCaptureComplete: saved.latest?.captureComplete === true,
    knownSnapshotReadiness: assessSnapshotForComparison(saved),
    candidateCount: candidateRows.length,
    candidateStatuses: statuses,
    candidateSequence: Number.isSafeInteger(saved.candidateLookup?.sequence)
      ? saved.candidateLookup.sequence : null,
    slotCount: slots.length,
    slotStorageForm: Array.isArray(saved.toolbarSlots) ? "implicit-lua-array"
      : saved.toolbarSlots ? "explicit-numeric-lua-table" : "absent",
    slotStates,
    validPinnedIds: validPins,
    distinctValidPinnedIds: seen.size,
    duplicateValidPinnedIds: duplicatePins,
    validIdPresentInKnown: validKnown,
    validIdAbsentFromKnown: unknownToKnown,
    eighthSlotEmpty: slots[7] == null,
    slotFingerprintComplete,
    slotArraySha256: slotFingerprintComplete ? sha256(JSON.stringify(canonical)) : null,
    roleFromLiveProcessVerified: false,
    sourceWriterPidVerified: false,
    pinUndoInGameVerified: false,
    rawAbilityIdsEmitted: false
  };
}

export function readReceipt(originalPath, expectedSha, requiredVersion) {
  if (path.basename(originalPath) !== "RRECollector.lua")
    throw new Error("ONLY_RRECOLLECTOR_SAVED_FILE");
  if (expectedSha !== undefined && !HEX64.test(expectedSha))
    throw new Error("EXPECTED_SHA_INVALID");
  if (requiredVersion !== undefined && !VERSION.test(requiredVersion))
    throw new Error("REQUIRED_VERSION_INVALID");
  const linkStat = fs.lstatSync(originalPath);
  if (!linkStat.isFile() || linkStat.isSymbolicLink())
    throw new Error("SOURCE_NOT_PLAIN_FILE");
  let fd;
  try {
    fd = fs.openSync(originalPath, "r");
    const before = fs.fstatSync(fd);
    // Fail closed if the pathname was replaced between initial lstat and open.
    if (linkStat.dev !== before.dev || linkStat.ino !== before.ino ||
        linkStat.size !== before.size || linkStat.mtimeMs !== before.mtimeMs ||
        linkStat.ctimeMs !== before.ctimeMs)
      throw new Error("SOURCE_CHANGED_BETWEEN_LOOKUP_AND_OPEN");
    if (!before.isFile() || before.size > MAX_BYTES) throw new Error("SOURCE_TOO_LARGE");
    const bytes = fs.readFileSync(fd);
    const after = fs.fstatSync(fd);
    const current = fs.statSync(originalPath);
    for (const item of [after, current]) {
      if (item.dev !== before.dev || item.ino !== before.ino ||
          item.size !== before.size || item.mtimeMs !== before.mtimeMs ||
          item.ctimeMs !== before.ctimeMs)
        throw new Error("SOURCE_CHANGED_DURING_READ");
    }
    if (bytes.length !== before.size) throw new Error("INCOMPLETE_READ");
    const digest = sha256(bytes);
    if (expectedSha && digest !== expectedSha.toLowerCase())
      throw new Error("SOURCE_SHA_MISMATCH");
    const text = new TextDecoder("utf-8", { fatal: true }).decode(bytes);
    const saved = parseSavedLua(text);
    if (requiredVersion !== undefined && saved?.addonVersion !== requiredVersion)
      throw new Error("SOURCE_VERSION_MISMATCH");
    return buildReceipt(saved, {
      observedAtUtc: new Date().toISOString(),
      modifiedAtUtc: new Date(after.mtimeMs).toISOString(),
      bytes: bytes.length, sha256: digest
    });
  } finally {
    if (fd !== undefined) fs.closeSync(fd);
  }
}

const invoked = process.argv[1] &&
  path.resolve(process.argv[1]) === fileURLToPath(import.meta.url);
if (invoked) {
  try {
    const args = process.argv.slice(2);
    if (args.length < 1 || args.length > 5 || args.length % 2 !== 1)
      throw new Error("INVALID_CLI_ARGUMENTS");
    let expectedSha, requiredVersion;
    for (let i = 1; i < args.length; i += 2) {
      if (args[i] === "--expected-sha" && expectedSha === undefined) expectedSha = args[i + 1];
      else if (args[i] === "--require-version" && requiredVersion === undefined) requiredVersion = args[i + 1];
      else throw new Error("INVALID_CLI_ARGUMENTS");
    }
    const receipt = readReceipt(args[0], expectedSha, requiredVersion);
    process.stdout.write(JSON.stringify(receipt) + "\n");
  } catch (error) {
    // No raw paths, values, file snippets or partial snapshots on failure.
    const message = String(error?.message || "SOURCE_READ_OR_PARSE_FAILED");
    const reason = /^[A-Z][A-Z0-9_]*$/.test(message) ? message : "SOURCE_READ_OR_PARSE_FAILED";
    process.stderr.write(JSON.stringify({ status: "failed", reason }) + "\n");
    process.exitCode = 1;
  }
}
