// RC-29 / SC-103: source-qualified 353-ID reference enriched by prior API Detail evidence.
// The input SavedVariables is parsed as literal Lua only; no player/target/private stats are exported.
import fs from "node:fs";
import path from "node:path";
import crypto from "node:crypto";
import { fileURLToPath } from "node:url";
import { parseSavedLua, buildAbilityCrosswalk } from "./read-rrecollector-saved.mjs";

function assertRecords(value, label) {
  if (!value || !Array.isArray(value.records)) throw new Error(label + " records required");
}
function byExactId(records, label) {
  const result = new Map();
  for (const r of records) {
    if (typeof r?.id !== "string" || !/^A[0-9A-F]{16}$/i.test(r.id) || result.has(r.id)) {
      throw new Error(label + " has invalid/duplicate exact ID");
    }
    result.set(r.id, r);
  }
  return result;
}
function sha(bytes) { return crypto.createHash("sha256").update(bytes).digest("hex"); }
const SAFE_DETAIL_FIELDS = [
  "lookupId", "id", "idNew", "name", "description", "castingTime", "channeled",
  "cooldown", "cooldownSeconds", "currentCooldownBegin", "currentCooldownDuration",
  "currentCooldownRemaining", "currentCooldownExpired", "currentCooldownPaused",
  "unusable", "outOfRange", "rangeMin", "rangeMax", "costPower", "costMana",
  "costEnergy", "costCharge", "costSpirit", "costPlanarCharge", "positioned",
  "passive", "continuous", "autoattack", "weapon", "stealthRequired",
  "gainCharge", "racial", "icon", "focusMin", "focusMax"
];
function safeDetail(raw) {
  if (!raw || typeof raw !== "object") return null;
  const detail = {};
  for (const key of SAFE_DETAIL_FIELDS) {
    const value = raw[key];
    if (typeof value === "string" || typeof value === "boolean"
      || typeof value === "number" && Number.isFinite(value)) detail[key] = value;
  }
  return detail;
}
function safeLookup(raw) {
  if (!raw || typeof raw !== "object") return null;
  const result = {};
  for (const key of ["status","phase","listed","id","soul","category","name"]) {
    const value = raw[key];
    if (typeof value === "string" || typeof value === "boolean") result[key] = value;
  }
  if (raw.detail) result.detail = safeDetail(raw.detail);
  return result;
}

export function buildLiveAtlas({ saved, savedSha256, originalThree, allWarrior, priorAtlas, sourceIndex = {}, savedFileModifiedUtc = null }) {
  assertRecords(originalThree, "three-soul catalog");
  assertRecords(allWarrior, "all-soul static catalog");
  assertRecords(priorAtlas, "prior ability atlas");
  const cross = buildAbilityCrosswalk(saved, originalThree, savedSha256);
  const staticIds = byExactId(allWarrior.records, "all-soul");
  const priorIds = byExactId(priorAtlas.records, "prior atlas");
  const queryIds = byExactId(cross.staticCandidates, "candidate crosswalk");
  for (const id of queryIds.keys()) {
    if (!staticIds.has(id)) throw new Error("three-soul candidate missing from all-soul catalog");
  }
  const records = [];
  for (const [id, source] of staticIds) {
    const prior = priorIds.get(id);
    if (prior && prior.name !== source.name) throw new Error("static/prior exact-ID name mismatch");
    const query = queryIds.get(id)?.candidateLookup || null;
    records.push({
      id, name: source.name, sourceSoul: source.soul, sourceCategory: source.category,
      sourceIcon: source.icon, historicalStaticSource: true,
      priorKnownApiList: source.priorKnownApiList,
      priorApiDetail: safeDetail(prior?.priorApiDetail),
      knownUiSection: prior?.knownUiSection ?? source.priorKnownUiSection ?? null,
      uiSoulTreeTooltip: prior?.uiSoulTreeTooltip ?? null,
      explicitIdDetail: safeLookup(query),
      unlockState: "unknown", learnableNow: "unknown", currentlyCastable: "unknown"
    });
  }
  for (const [id, prior] of priorIds) {
    if (staticIds.has(id)) continue;
    if (prior.priorKnownApiList !== "listed-in-preserved-69") {
      throw new Error("nonstatic record lacks positive prior API listing");
    }
    records.push({
      id, name: prior.name, sourceSoul: prior.sourceSoul ?? null,
      sourceCategory: prior.sourceCategory ?? null, sourceIcon: prior.sourceIcon ?? null,
      historicalStaticSource: false, priorKnownApiList: prior.priorKnownApiList,
      priorApiDetail: safeDetail(prior.priorApiDetail), knownUiSection: prior.knownUiSection ?? null,
      uiSoulTreeTooltip: prior.uiSoulTreeTooltip ?? null, explicitIdDetail: null,
      unlockState: "unknown", learnableNow: "unknown", currentlyCastable: "unknown"
    });
  }
  records.sort((a,b) => a.id.localeCompare(b.id));
  if (new Set(records.map(r=>r.id)).size !== records.length) throw new Error("merged IDs duplicated");
  const observed = records.filter(r=>r.explicitIdDetail);
  const qStatus = Object.fromEntries([...new Set(observed.map(r=>r.explicitIdDetail.status))]
    .sort().map(status=>[status,observed.filter(r=>r.explicitIdDetail.status===status).length]));
  const returned = observed.filter(r=>r.explicitIdDetail.detail);
  const priorListed = records.filter(r=>r.priorKnownApiList==="listed-in-preserved-69");
  const duplicates = Object.entries(Object.groupBy(records, r=>r.name))
    .filter(([,list])=>list.length>1)
    .map(([name,list])=>({name,ids:list.map(r=>r.id),souls:list.map(r=>r.sourceSoul)}));
  return {
    schemaVersion:1, taskId:"SC-103/RC-29",
    sourceScope:"physical RIFT prior 69-ID List snapshot + historical 11-soul static IDs + explicit candidate Detail results",
    sourceIndex:{...sourceIndex, characterSavedVariablesSha256:savedSha256},
    savedFileModifiedUtc, sourceKnownCaptureVersion:cross.knownCaptureVersion,
    sourceCandidateLookupVersion:cross.candidateLookupVersion,
    counts:{
      exactIds:records.length, historicalStaticIds:staticIds.size,
      priorApiListed:priorListed.length, originalThreeSoulCandidates:queryIds.size,
      candidateLookupEntries:observed.length, candidateLookupByStatus:qStatus,
      candidateDetailReturned:returned.length,
      additionalUnlistedDetailReturned:returned.filter(r=>r.priorKnownApiList!=="listed-in-preserved-69").length,
      eligibilityResolved:0, castingSuccessVerified:0, duplicateNameGroups:duplicates.length
    },
    duplicateNames:duplicates, records,
    limitations:[
      "An arbitrary-ID Detail response does not establish learned, learnable, unlocked, bound, or castable state.",
      "Missing/false/zero metadata are distinct; no missing cooldown or readiness value is inferred.",
      "Saved file filesystem modified time is not necessarily the API capture time.",
      "No native ability resolver, cooldown timing, queue enum, or cast-success path is established here."
    ]
  };
}

const invoked = process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url);
if (invoked) {
  const savedFile = process.argv[2], output = process.argv[3];
  if (!savedFile || !output) {
    process.stderr.write("Usage: node tools/build-rift-ability-atlas-live.mjs <RRECollector.lua> <output.json>\n");
    process.exitCode = 2;
  } else {
    const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
    const paths = {
      originalThree: "docs/REA-RIFT-SPELLCASTING-SC103-WARRIOR-STATIC-ABILITIES-2026-11-02.json",
      allWarrior: "docs/REA-RIFT-SPELLCASTING-SC103-WARRIOR-ALL-SOULS-STATIC-2026-11-02.json",
      priorAtlas: "docs/REA-RIFT-SPELLCASTING-SC103-ABILITY-ATLAS-2026-11-02.json"
    };
    const inputs = Object.fromEntries(Object.entries(paths).map(([key,p])=>{
      const bytes = fs.readFileSync(path.join(root,p));
      return [key,{value:JSON.parse(bytes.toString("utf8")),path:p,sha256:sha(bytes)}];
    }));
    const savedBytes = fs.readFileSync(savedFile);
    const atlas = buildLiveAtlas({
      saved:parseSavedLua(savedBytes.toString("utf8")),savedSha256:sha(savedBytes),
      originalThree:inputs.originalThree.value,allWarrior:inputs.allWarrior.value,
      priorAtlas:inputs.priorAtlas.value,
      sourceIndex:{...Object.fromEntries(Object.entries(inputs).map(([key,v])=>[key,{path:v.path,sha256:v.sha256}])),
        generatorSha256:sha(fs.readFileSync(fileURLToPath(import.meta.url))),
        decoderSha256:sha(fs.readFileSync(path.join(root,"tools/read-rrecollector-saved.mjs")))},
      savedFileModifiedUtc:fs.statSync(savedFile).mtime.toISOString()
    });
    fs.writeFileSync(output,JSON.stringify(atlas,null,2)+"\n",{encoding:"utf8",flag:"wx"});
    process.stdout.write(JSON.stringify({output,counts:atlas.counts,savedSha256:atlas.sourceIndex.characterSavedVariablesSha256})+"\n");
  }
}
