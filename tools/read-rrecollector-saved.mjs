// Read-only RRECollector SavedVariables decoder. Lua values are parsed, never executed.
import fs from "node:fs";
import path from "node:path";
import crypto from "node:crypto";
import { fileURLToPath } from "node:url";

const MAX_CHARS = 2_000_000;
const MAX_DEPTH = 48;
const MAX_VALUES = 100_000;
const ID = /^A[0-9A-F]{16}$/;
const DETAILS = [
  "lookupId", "id", "idNew", "name", "description", "castingTime",
  "channeled", "cooldown", "currentCooldownBegin", "currentCooldownDuration",
  "currentCooldownRemaining", "currentCooldownExpired", "currentCooldownPaused",
  "unusable", "outOfRange", "rangeMin", "rangeMax", "costPower", "costMana",
  "costEnergy", "costCharge", "costSpirit", "costPlanarCharge", "positioned",
  "passive", "continuous", "autoattack", "weapon", "stealthRequired",
  "gainCharge", "racial", "icon", "focusMin", "focusMax"
];

export function parseSavedLuaBytes(bytes) {
  if (!(bytes instanceof Uint8Array)) throw new Error("SavedVariables input must be bytes");
  return parseSavedLua(new TextDecoder("utf-8", { fatal: true }).decode(bytes));
}

export function parseSavedLua(input) {
  if (typeof input !== "string" || input.length > MAX_CHARS) {
    throw new Error("SavedVariables input missing or too large");
  }
  const src = input.charCodeAt(0) === 0xfeff ? input.slice(1) : input;
  let i = 0, depth = 0, values = 0;
  const fail = what => { throw new Error("Unsupported SavedVariables Lua at offset " + i + ": " + what); };
  function skip() {
    for (;;) {
      while (i < src.length && /\s/.test(src[i])) i++;
      if (src.slice(i, i + 2) !== "--") return;
      while (i < src.length && src[i] !== "\n") i++;
    }
  }
  function identifier() {
    const m = /^[A-Za-z_][A-Za-z0-9_]*/.exec(src.slice(i));
    if (!m) fail("identifier expected");
    i += m[0].length;
    return m[0];
  }
  function expect(c) {
    skip();
    if (src[i] !== c) fail("expected " + c);
    i++;
  }
  function quoted() {
    const delim = src[i++];
    const bytes = [];
    const encoder = new TextEncoder();
    const decoder = new TextDecoder("utf-8", {fatal:true});
    let rawStart = i;
    function appendRaw(end) {
      for (const byte of encoder.encode(src.slice(rawStart, end))) bytes.push(byte);
    }
    const special = {n:10,r:13,t:9,a:7,b:8,f:12,v:11};
    while (i < src.length) {
      const c = src[i++];
      if (c === delim) {
        appendRaw(i - 1);
        try { return decoder.decode(Uint8Array.from(bytes)); }
        catch { fail("invalid UTF-8 in quoted string"); }
      }
      if (c === "\n" || c === "\r") fail("unescaped newline in quoted string");
      if (c !== "\\") continue;
      appendRaw(i - 1);
      if (i >= src.length) fail("unterminated escape");
      let e = src[i++];
      if (/[0-9]/.test(e)) {
        while (i < src.length && e.length < 3 && /[0-9]/.test(src[i])) e += src[i++];
        const n = Number(e);
        if (n > 255) fail("decimal escape out of range");
        bytes.push(n);
      } else if (e === delim || e === "\\") bytes.push(e.charCodeAt(0));
      else if (e === "\n") bytes.push(10);
      else if (e === "\r") { if (src[i] === "\n") i++; bytes.push(10); }
      else if (Object.hasOwn(special, e)) bytes.push(special[e]);
      else fail("unsupported escape");
      rawStart = i;
    }
    fail("unterminated quoted string");
  }
  function number() {
    const m = /^[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?/.exec(src.slice(i));
    if (!m) fail("number expected");
    i += m[0].length;
    const n = Number(m[0]);
    if (!Number.isFinite(n)) fail("non-finite number");
    return n;
  }
  function value() {
    skip();
    if (++values > MAX_VALUES) fail("value limit exceeded");
    if (src[i] === "{") return table();
    if (src[i] === '"' || src[i] === "'") return quoted();
    if (/[0-9+.\-]/.test(src[i] || "")) return number();
    const v = identifier();
    if (v === "true") return true;
    if (v === "false") return false;
    if (v === "nil") return null;
    fail("only literal Lua values allowed");
  }
  function table() {
    if (++depth > MAX_DEPTH) fail("table nesting limit exceeded");
    i++;
    const sequence = [], keyed = Object.create(null);
    let explicit = false;
    for (;;) {
      skip();
      if (src[i] === "}") { i++; break; }
      let key = null, hasKey = false;
      if (src[i] === "[") {
        i++;
        key = value();
        if (typeof key !== "string" && typeof key !== "number") fail("invalid bracket key");
        expect("]");
        expect("=");
        hasKey = true;
      } else if (/^[A-Za-z_]/.test(src[i] || "")) {
        const rewind = i;
        key = identifier();
        skip();
        if (src[i] === "=") { i++; hasKey = true; }
        else i = rewind;
      }
      const next = value();
      if (hasKey) {
        explicit = true;
        const k = String(key);
        if (Object.hasOwn(keyed, k)) fail("duplicate Lua table key");
        keyed[k] = next;
      } else sequence.push(next);
      skip();
      if (src[i] === "," || src[i] === ";") i++;
      else if (src[i] !== "}") fail("table delimiter expected");
    }
    depth--;
    if (!explicit) return sequence;
    for (let n = 0; n < sequence.length; n++) {
      const k = String(n + 1);
      if (Object.hasOwn(keyed, k)) fail("duplicate implicit array key");
      keyed[k] = sequence[n];
    }
    return keyed;
  }
  skip();
  if (identifier() !== "RRECollectorData") fail("unexpected SavedVariables assignment");
  expect("=");
  const data = value();
  skip();
  if (src[i] === ";") { i++; skip(); }
  if (i !== src.length || !data || Array.isArray(data) || typeof data !== "object") {
    fail("trailing code or invalid root");
  }
  return data;
}

function scalars(source, names) {
  const out = {};
  if (!source || typeof source !== "object") return out;
  for (const field of names) {
    const v = source[field];
    if (typeof v === "string" || typeof v === "boolean"
      || typeof v === "number" && Number.isFinite(v)) out[field] = v;
  }
  return out;
}
function asArray(value) {
  if (Array.isArray(value)) return value;
  if (!value || typeof value !== "object") return [];
  return Object.entries(value).filter(([k])=>/^\d+$/.test(k))
    .sort(([a],[b])=>Number(a)-Number(b)).map(([,v])=>v);
}

// Offline structure gate only: one SavedVariables file cannot prove a fresh live capture.
export function assessSnapshotForComparison(saved) {
  const latest = saved?.latest && typeof saved.latest === "object" ? saved.latest : {};
  const list = latest.abilityList && typeof latest.abilityList === "object" ? latest.abilityList : {};
  const player = latest.player && typeof latest.player === "object" ? latest.player : {};
  const rawRecords = latest.abilities;
  const keys = rawRecords && typeof rawRecords === "object" ? Object.keys(rawRecords) : [];
  // Keep the historical crosswalk's permissive asArray(); strict evidence is a separate gate.
  const recordShapeValid = Array.isArray(rawRecords)
    ? keys.length === rawRecords.length && keys.every((key, i) => key === String(i))
    : rawRecords && typeof rawRecords === "object" && keys.length > 0
      && keys.every((key, i) => key === String(i + 1));
  const records = asArray(rawRecords);
  const reasons = [];
  const require = (valid, reason) => { if (!valid) reasons.push(reason); };
  const named = value => typeof value === "string" && value.trim().length > 0;
  const role = latest.roleSlot;
  require(recordShapeValid, "ABILITY_RECORDS_MALFORMED");
  require(latest.captureComplete === true, "CAPTURE_NOT_COMPLETE");
  require(list.apiAvailable === true && list.enumerationComplete === true, "LIST_NOT_COMPLETE");
  require(list.detailFailures === 0 && list.ignored === 0 && list.truncated === 0, "LIST_HAS_GAPS");
  require(list.uniqueCount === records.length && list.detailCount === records.length, "RECORD_COUNT_MISMATCH");
  if (Object.hasOwn(list,"rawEntries"))
    require(Number.isSafeInteger(list.rawEntries) && list.rawEntries >= records.length,
      "LIST_COUNT_CONTRADICTION");
  const ids = records.map(record => record?.lookupId);
  require(ids.every(id => named(id) && ID.test(id)) && new Set(ids).size === ids.length,
    "ABILITY_IDS_UNQUALIFIED");
  require(Number.isSafeInteger(latest.sequence) && latest.sequence > 0
    && saved?.sequence === latest.sequence, "SEQUENCE_UNBOUND");
  require(named(player.id) && named(player.name), "PLAYER_IDENTITY_UNBOUND");
  if (latest.capabilities != null)
    require(typeof latest.capabilities === "object" && latest.capabilities.player === true,
      "PLAYER_CAPABILITY_CONTRADICTS_COMPLETE");
  require(named(role) || typeof role === "number" && Number.isFinite(role), "ROLE_UNBOUND");
  require(Number.isFinite(latest.frameTime) && latest.frameTime >= 0
    && Number.isFinite(latest.realTime) && latest.realTime >= 0,
    "CAPTURE_CLOCK_UNBOUND");
  require(named(latest.addonVersion), "SNAPSHOT_VERSION_UNBOUND");
  return {
    schemaVersion:1, offlineStructureQualified:reasons.length === 0, reasons,
    freshnessVerified:false, processBuildVerified:false, eventDeliveryVerified:false,
    eventComparisonReady:false,
    evidenceLimit:"Single saved latest cannot prove a newly flushed capture, process/build, or events."
  };
}

export function buildAbilityCrosswalk(saved, staticCatalog, savedSha256) {
  const latest = saved?.latest;
  if (!latest || !staticCatalog || !Array.isArray(staticCatalog.records)) {
    throw new Error("latest ability snapshot and static candidate catalog required");
  }
  const current = new Map();
  for (const raw of asArray(latest.abilities)) {
    const detail = scalars(raw, DETAILS);
    if (!ID.test(detail.lookupId || "") || current.has(detail.lookupId)) {
      throw new Error("invalid or duplicate current-known ID");
    }
    current.set(detail.lookupId, detail);
  }
  const queried = new Map();
  for (const q of asArray(saved?.candidateLookup?.entries)) {
    if (q && typeof q === "object" && ID.test(q.id || "") && !queried.has(q.id)) {
      queried.set(q.id, q);
    }
  }
  const seen = new Set(), rows = [];
  for (const s of staticCatalog.records) {
    if (!ID.test(s.id || "") || seen.has(s.id)) throw new Error("invalid or duplicate static ID");
    seen.add(s.id);
    const detail = current.get(s.id);
    const query = queried.get(s.id);
    const row = {
      id:s.id, name:s.name, soul:s.soul, category:s.category,
      icon:s.icon, listedInSavedCurrent:!!detail,
      exactNameAgreement:detail ? detail.name === s.name : null
    };
    if (detail) row.currentDetail = detail;
    if (query) {
      row.candidateLookup = scalars(query, ["status","phase","listed","id","soul","category","name"]);
      if (query.detail) row.candidateLookup.detail = scalars(query.detail, DETAILS);
    }
    rows.push(row);
  }
  const onlyKnown = [...current.entries()].filter(([id])=>!seen.has(id))
    .map(([id,detail])=>({id, currentDetail:detail}));
  const duplicateNames = Object.entries(Object.groupBy(rows, r=>r.name))
    .filter(([,group])=>group.length>1)
    .map(([name,group])=>({name,ids:group.map(r=>r.id),souls:group.map(r=>r.soul)}));
  const listed = rows.filter(r=>r.listedInSavedCurrent);
  const candidate = saved.candidateLookup;
  return {
    schemaVersion:1,
    sourceKind:"character-scoped prior current-known API capture plus disabled static Warrior source, exact-ID join",
    evidenceLimit:"Absence from List or a negative arbitrary-ID Detail response is not proof of locked, learnable or unavailable state",
    savedSha256,
    knownCaptureVersion:latest.addonVersion || null,
    knownCaptureComplete:latest.captureComplete === true,
    knownSnapshotReadiness:assessSnapshotForComparison(saved),
    staticCatalogVersion:staticCatalog.catalogVersion,
    liveCandidateLookupSaved:!!candidate,
    candidateLookupVersion:candidate?.addonVersion || null,
    candidateLookupPolicy:candidate?.policy || null,
    counts:{
      knownApi:current.size, staticCandidates:rows.length,
      staticKnown:listed.length, staticUnlisted:rows.length-listed.length,
      knownOutsideStatic:onlyKnown.length,
      knownStaticNameMismatches:listed.filter(r=>r.exactNameAgreement===false).length,
      duplicateStaticNames:duplicateNames.length
    },
    bySoul:Object.fromEntries(["Paladin","VoidKnight","Paragon"].map(soul=>{
      const slice=rows.filter(r=>r.soul===soul);
      return [soul,{candidates:slice.length,known:slice.filter(r=>r.listedInSavedCurrent).length}];
    })),
    duplicateNames, staticCandidates:rows, knownOutsideStatic:onlyKnown
  };
}

const invoked = process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url);
if (invoked) {
  const savedFile = process.argv[2];
  const staticFile = process.argv[3] || path.resolve(path.dirname(fileURLToPath(import.meta.url)),
    "../docs/REA-RIFT-SPELLCASTING-SC103-WARRIOR-STATIC-ABILITIES-2026-11-02.json");
  if (!savedFile) {
    process.stderr.write("Usage: node tools/read-rrecollector-saved.mjs <RRECollector.lua> [static catalog JSON]\n");
    process.exitCode = 2;
  } else {
    const bytes = fs.readFileSync(savedFile);
    const saved = parseSavedLuaBytes(bytes);
    const staticCatalog = JSON.parse(fs.readFileSync(staticFile,"utf8"));
    const digest = crypto.createHash("sha256").update(bytes).digest("hex");
    process.stdout.write(JSON.stringify(buildAbilityCrosswalk(saved,staticCatalog,digest)) + "\n");
  }
}
