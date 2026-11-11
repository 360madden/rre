// RC-54: Strict, offline exporter for the current-client RRECollector navigation probe.
// No Lua execution, game access, network calls, invented API data, or overwrite.
import fs from "node:fs";
import path from "node:path";
import crypto from "node:crypto";
import {fileURLToPath} from "node:url";
import {parseSavedLuaBytes} from "./read-rrecollector-saved.mjs";
import {readStableOriginalWithMetadata} from "./read-stable-original.mjs";

const VERSION = "0.4.19";
const MAX_DOCS = 18, MAX_NAMES = 96;
const PREFIXES = ["Inspect.Unit.","Inspect.Map.","Inspect.Target.","Inspect.Player.",
  "Inspect.Location.","Inspect.World.","Inspect.Waypoint.","Inspect.Path.",
  "Inspect.NPC.","Inspect.Camera.","Inspect.Follow.","Event.Unit.","Event.Map.",
  "Event.Target.","Event.NPC.","Event.Follow.","Command.Map.","Command.Target.",
  "Command.Follow."];
const TERMS = ["position","coordinate","location","movement","velocity","heading",
  "waypoint","target","distance","navigate","path","npc","follow","camera",
  "facing","orientation","rotation"];
const PATHS = ["Inspect.Documentation","Inspect.Unit.Detail","Inspect.Unit.Lookup",
  "Inspect.Unit.List","Inspect.Map.Detail","Inspect.Map.List","Inspect.Unit.Castbar",
  "Inspect.Unit.Availability"];
const LUA_TYPES = new Set(["nil","error","function","table","number","string",
  "boolean","thread","userdata"]);
const DOC_STATUS = new Set(["missing","index-error","index-non-table","index-available"]);
const fail = code => { throw Error(code); };
const requireValue = (okay, code) => { if (!okay) fail(code); };
const object = x => x !== null && typeof x === "object" && !Array.isArray(x);
const count = (x, max) => Number.isSafeInteger(x) && x >= 0 && x <= max;
const byteLen = x => Buffer.byteLength(x,"utf8");
const sha = x => crypto.createHash("sha256").update(x).digest("hex");
const cell = x => String(x ?? "").replaceAll("&","&amp;")
  .replaceAll("<","&lt;").replaceAll(">","&gt;")
  .replace(/[\\|`!*_\[\]()~]/g, mark => "\\" + mark)
  .replace(/[\r\n\t]+/g," ");

function dense(value) {
  if (Array.isArray(value)) return value;
  requireValue(object(value),"NAV_NAMES_SHAPE");
  const keys=Object.keys(value);
  requireValue(keys.every((key,i)=>key===String(i+1)),"NAV_NAMES_SHAPE");
  return keys.map(key=>value[key]);
}
function acceptedName(name) {
  return typeof name==="string" && byteLen(name)>0 && byteLen(name)<=160
    && (name.startsWith("Inspect.") || name.startsWith("Event.")
      || name.startsWith("Command."))
    && (PREFIXES.some(prefix=>name.startsWith(prefix))
      || TERMS.some(term=>name.toLowerCase().includes(term)));
}
function priority(name) {
  if (["Inspect.Unit.Detail","Inspect.Map.Detail","Inspect.Unit.Lookup"].includes(name)) return 0;
  const lower=name.toLowerCase();
  if (TERMS.some(term=>term!=="target" && term!=="npc" && lower.includes(term))) return 1;
  if (lower.includes("target") || lower.includes("npc")) return 2;
  if (name.startsWith("Inspect.Map.")) return 3;
  if (name.startsWith("Inspect.Unit.")) return 4;
  return 5;
}
const compare=(a,b)=>priority(a)-priority(b)||Buffer.compare(Buffer.from(a),Buffer.from(b));

export function summarizeNavigationReceipt(saved, source={}) {
  requireValue(object(saved),"SAVED_ROOT_SHAPE");
  const probe=saved.navigationProbe;
  requireValue(object(probe) && object(probe.index) && object(probe.pathTypes),
    "NAV_NOT_CAPTURED_OR_MALFORMED");
  requireValue(saved.addonVersion===VERSION && probe.addonVersion===VERSION,
    "NAV_VERSION_MISMATCH");
  requireValue(probe.schemaVersion===1 && probe.scope===
    "navigation-api-name-discovery-only-no-gameplay-or-api-execution",
    "NAV_SCHEMA_SCOPE_MISMATCH");
  requireValue(count(probe.sequence,Number.MAX_SAFE_INTEGER) && probe.sequence>0
    && saved.navigationProbeSequence===probe.sequence,"NAV_SEQUENCE_UNBOUND");
  requireValue(DOC_STATUS.has(probe.documentationStatus),"NAV_DOC_STATUS");
  const idx=probe.index;
  for(const [field,max] of Object.entries({scanned:2048,matched:2048,retained:96,
    ignored:2048,truncated:2048}))
    requireValue(count(idx[field],max),"NAV_COUNTER_SHAPE");
  requireValue(idx.matched+idx.ignored===idx.scanned
    && idx.retained+idx.truncated===idx.matched
    && (idx.truncated===0||idx.retained===MAX_NAMES)
    && typeof idx.scanLimitReached==="boolean"
    && (!idx.scanLimitReached||idx.scanned===2048),"NAV_COUNTER_CONTRADICTION");
  if(probe.documentationStatus!=="index-available")
    requireValue(idx.scanned===0 && !idx.scanLimitReached,"NAV_INDEX_UNAVAILABLE");
  const names=dense(idx.names);
  requireValue(names.length===idx.retained && names.every(acceptedName)
    && names.every((name,i)=>i===0||compare(names[i-1],name)<0),
    "NAV_NAMES_INVALID_OR_UNSORTED");
  const types={};
  requireValue(Object.keys(probe.pathTypes).length===PATHS.length,"NAV_PATH_COUNT");
  for(const p of PATHS) {
    requireValue(LUA_TYPES.has(probe.pathTypes[p]),"NAV_PATH_TYPE");
    types[p]=probe.pathTypes[p];
  }
  const docs=probe.documents;
  requireValue(object(docs)||(Array.isArray(docs)&&docs.length===0),"NAV_DOC_SHAPE");
  const docNames=Object.keys(docs);
  const expected=probe.documentationStatus==="index-available"
    ? names.slice(0,MAX_DOCS):[];
  requireValue(docNames.length===expected.length
    && docNames.every(name=>expected.includes(name)),"NAV_DOC_NAMES");
  let errors=0;
  const descriptions={};
  for(const name of expected) {
    const d=docs[name];
    requireValue(object(d)&&["returned","other","error"].includes(d.status),
      "NAV_DOC_ENTRY");
    if(d.status==="returned") {
      requireValue(typeof d.text==="string" && byteLen(d.text)<=512
        && typeof d.textTruncated==="boolean","NAV_DOC_TEXT");
      descriptions[name]={status:d.status,text:d.text,textTruncated:d.textTruncated};
    } else if(d.status==="other") {
      requireValue(LUA_TYPES.has(d.returnType)&&d.returnType!=="error",
        "NAV_DOC_RETURN_TYPE");
      descriptions[name]={status:d.status,returnType:d.returnType};
    } else { errors++; descriptions[name]={status:"error"}; }
  }
  requireValue(count(probe.documentErrors,MAX_DOCS)
    && probe.documentErrors===errors,"NAV_DOC_ERRORS");
  const partial=idx.truncated>0||idx.scanLimitReached;
  return {schemaVersion:1,probeVersion:VERSION,sequence:probe.sequence,
    sourceSha256:source.sha256??null,sourceBytes:source.bytes??null,
    sourceModifiedAtUtc:source.modifiedAtUtc??null,
    dataClaim:"Names and documentation reported by an offline SavedVariables file; no verified current load, live freshness, physical movement or actionable API.",
    status:probe.documentationStatus!=="index-available"?"observed-without-index"
      : partial?"observed-partial":"bounded-index-observed",
    documentationStatus:probe.documentationStatus,
    scan:{scanned:idx.scanned,matched:idx.matched,retained:idx.retained,
      ignored:idx.ignored,truncated:idx.truncated,scanLimitReached:idx.scanLimitReached},
    pathTypes:types,names,descriptions};
}

export function renderNavigationMarkdown(receipt) {
  requireValue(object(receipt)&&Array.isArray(receipt.names),"NAV_RENDER_INPUT");
  const s=receipt.scan;
  const lines=["# RIFT movement and navigation API — bounded observed index","",
    "> **Evidence qualification:** This document is derived from a single original RRECollector SavedVariables file. It does not establish current in-game load, live freshness, available gameplay actions, or movement control. API names are leads for investigation, not verified controls.","",
    "## Provenance","",
    "- Addon version: `"+receipt.probeVersion+"`",
    "- Probe sequence: `"+receipt.sequence+"`",
    "- Original source SHA-256: `"+(receipt.sourceSha256??"unavailable")+"`",
    "- Original source bytes: "+(receipt.sourceBytes??"unknown"),
    "- Original file modified (UTC): "+(receipt.sourceModifiedAtUtc??"unknown"),
    "- Documentation status: `"+receipt.documentationStatus+"`",
    "- Scan: "+s.scanned+" inspected / "+s.matched+" matching / "+s.retained+
      " retained / "+s.truncated+" omitted by retained-name limit",
    "- Scope: "+(receipt.documentationStatus!=="index-available"
      ? "**DOCUMENTATION UNAVAILABLE** — no API index names observed"
      : s.scanLimitReached||s.truncated>0
        ? "**PARTIAL** — at least one scan/retention limit reached"
        : "Bounded index only; no completeness claim beyond observed index"),"",
    "## Guarded exact Inspect path types","",
    "| Candidate path | Observed Lua type |","|---|---|"];
  for(const [key,value] of Object.entries(receipt.pathTypes))
    lines.push("| `"+cell(key)+"` | "+cell(value)+" |");
  lines.push("","## API-name leads (not verified action capabilities)","",
    "| # | API name | Documentation excerpt (up to 512 bytes) |","|---:|---|---|");
  receipt.names.forEach((name,i)=>{
    const d=receipt.descriptions[name];
    let summary="Not requested (18-document cap)";
    if(d?.status==="returned")
      summary=cell(d.text)+(d.textTruncated?" … [truncated]":"");
    else if(d?.status==="error") summary="Documentation query errored";
    else if(d?.status==="other") summary="Documentation returned "+cell(d.returnType);
    lines.push("| "+(i+1)+" | `"+cell(name)+"` | "+summary+" |");
  });
  if(receipt.names.length===0)
    lines.push("| — | No retained names | Documentation index unavailable or no matching names |");
  lines.push("","## Machine-readable index receipt","",
    "```json",JSON.stringify({schemaVersion:receipt.schemaVersion,
      probeVersion:receipt.probeVersion,sequence:receipt.sequence,
      sourceSha256:receipt.sourceSha256,status:receipt.status,
      scan:receipt.scan,names:receipt.names},null,2),"```","");
  return lines.join("\n");
}

export function readNavigationReceipt(file,requiredVersion=VERSION) {
  requireValue(path.basename(file)==="RRECollector.lua","ONLY_RRECOLLECTOR_SAVED_FILE");
  requireValue(requiredVersion===VERSION,"NAV_REQUIRED_VERSION");
  const original=readStableOriginalWithMetadata(file);
  const saved=parseSavedLuaBytes(original.bytes);
  return summarizeNavigationReceipt(saved,{sha256:sha(original.bytes),bytes:original.bytes.length,
    modifiedAtUtc:original.modifiedAtUtc});
}

if(process.argv[1]&&path.resolve(process.argv[1])===fileURLToPath(import.meta.url)) {
  try {
    const args=process.argv.slice(2);
    requireValue(args.length===5&&args[1]==="--require-version"
      && args[3]==="--output"&&typeof args[4]==="string"
      && args[4].toLowerCase().endsWith(".md"),"NAV_USAGE");
    const receipt=readNavigationReceipt(args[0],args[2]);
    const markdown=renderNavigationMarkdown(receipt);
    fs.writeFileSync(args[4],markdown,{encoding:"utf8",flag:"wx"});
    process.stdout.write(JSON.stringify({status:"written",sourceSha256:receipt.sourceSha256,
      output:path.basename(args[4]),names:receipt.names.length,partial:receipt.status==="observed-partial"})+"\n");
  } catch(error) {
    const code=String(error?.message||"NAV_EXPORT_FAILED");
    const reason=/^[A-Z][A-Z0-9_]*$/.test(code)?code:"NAV_EXPORT_FAILED";
    process.stderr.write(JSON.stringify({status:"failed",reason})+"\n");
    process.exitCode=1;
  }
}
