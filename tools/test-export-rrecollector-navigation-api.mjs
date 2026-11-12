import test from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import crypto from "node:crypto";
import {spawnSync} from "node:child_process";
import {fileURLToPath} from "node:url";
import {parseSavedLua} from "./read-rrecollector-saved.mjs";
import {summarizeNavigationReceipt,renderNavigationMarkdown,readNavigationReceipt}
  from "./export-rrecollector-navigation-api.mjs";

const PATHS=["Inspect.Documentation","Inspect.Unit.Detail","Inspect.Unit.Lookup",
  "Inspect.Unit.List","Inspect.Map.Detail","Inspect.Map.List","Inspect.Unit.Castbar",
  "Inspect.Unit.Availability"];
const types=PATHS.map((p,i)=>`["${p}"]="${i<2?"function":"nil"}"`).join(",");
const DEFAULT_NAMES=["Inspect.Map.Detail","Inspect.Unit.Detail","Inspect.Unit.Position"];
const literalName=n=>JSON.stringify(n);
const other=name=>`["${name}"]={status="other",returnType="nil"}`;
const documentation=(names)=>names.slice(0,18).map(other).join(",");
function fixture({rootVersion="0.4.19",probeVersion="0.4.19",
  sequence=3,rootSequence=3,names=DEFAULT_NAMES,scanned=4,
  matched=3,ignored=1,truncated=0,capped=false,docStatus="index-available",
  docEntries,docErrors=0,pathTypes=types}={}) {
  const docs=docEntries===undefined?documentation(names):docEntries;
  return `RRECollectorData={addonVersion="${rootVersion}",navigationProbeSequence=${rootSequence},
    navigationProbe={schemaVersion=1,addonVersion="${probeVersion}",sequence=${sequence},
      scope="navigation-api-name-discovery-only-no-gameplay-or-api-execution",
      documentationStatus="${docStatus}",documentErrors=${docErrors},
      index={scanned=${scanned},matched=${matched},retained=${names.length},
        ignored=${ignored},truncated=${truncated},scanLimitReached=${capped},
        names={${names.map(literalName).join(",")}}},
      pathTypes={${pathTypes}},documents={${docs}}}}`;
}
const summarize = opts=>summarizeNavigationReceipt(parseSavedLua(fixture(opts)),
  {sha256:"a".repeat(64),bytes:723,modifiedAtUtc:"2026-11-11T00:00:00Z"});

test("v0.4.20 navigation retains version identity and rejects older retained probes",()=>{
  assert.equal(summarize({rootVersion:"0.4.20",probeVersion:"0.4.20"}).probeVersion,"0.4.20");
  assert.throws(()=>summarize({rootVersion:"0.4.20"}),/NAV_VERSION_MISMATCH/);
});
test("v0.4.21 navigation retains its producer version and rejects older retained probes",()=>{
  assert.equal(summarize({rootVersion:"0.4.21",probeVersion:"0.4.21"}).probeVersion,"0.4.21");
  assert.throws(()=>summarize({rootVersion:"0.4.21"}),/NAV_VERSION_MISMATCH/);
});

test("genuine nav probe required: prior v0.4.18 saved data never invents names",()=>{
  assert.throws(()=>summarizeNavigationReceipt(parseSavedLua(
    'RRECollectorData={addonVersion="0.4.18"}')),/NAV_NOT_CAPTURED_OR_MALFORMED/);
});
test("valid synthetic receipt renders provenance, names, types and explicit limits",()=>{
  const s=summarize();
  assert.equal(s.status,"bounded-index-observed");
  assert.deepEqual(s.names,DEFAULT_NAMES);
  assert.equal(s.pathTypes["Inspect.Unit.Detail"],"function");
  const md=renderNavigationMarkdown(s);
  assert.match(md,/Original source SHA-256/);
  assert.match(md,/Inspect.Unit.Position/);
  assert.match(md,/Names are leads|API names are leads/);
  assert.match(md,/Not requested|Documentation returned/);
  assert.match(md,/does not establish current in-game load/);
  assert.doesNotMatch(md,/actualMovementVerified":true/);
});
test("priority order is required: exact Map/Unit first, then spatial names",()=>{
  assert.throws(()=>summarize({names:["Inspect.Unit.Position","Inspect.Map.Detail","Inspect.Unit.Detail"]}),
    /NAV_NAMES_INVALID_OR_UNSORTED/);
  assert.throws(()=>summarize({names:["Inspect.Map.Detail","Inspect.Map.Detail","Inspect.Unit.Position"]}),
    /duplicate Lua table key|NAV_NAMES_INVALID_OR_UNSORTED/);
});
test("root version and sequence must bind to this v0.4.19 receipt",()=>{
  assert.throws(()=>summarize({rootVersion:"0.4.18"}),/NAV_VERSION_MISMATCH/);
  assert.throws(()=>summarize({probeVersion:"0.4.18"}),/NAV_VERSION_MISMATCH/);
  assert.throws(()=>summarize({rootSequence:2}),/NAV_SEQUENCE_UNBOUND/);
});
test("counter arithmetic and index availability are strict",()=>{
  assert.throws(()=>summarize({matched:4}),/NAV_COUNTER_CONTRADICTION/);
  assert.throws(()=>summarize({docStatus:"missing"}),/NAV_INDEX_UNAVAILABLE/);
  assert.throws(()=>summarize({scanned:9,capped:true,ignored:6}),
    /NAV_COUNTER_CONTRADICTION/);
  const missing=summarize({names:[],scanned:0,matched:0,ignored:0,
    docStatus:"missing"});
  assert.equal(missing.status,"observed-without-index");
  assert.match(renderNavigationMarkdown(missing),/DOCUMENTATION UNAVAILABLE/);
});
test("producer-permitted non-ASCII and punctuation names are not falsely rejected",()=>{
  const names=["Inspect.Unit.Detail","Inspect.Unit.Position-É"];
  const result=summarize({names,scanned:3,matched:2,ignored:1});
  assert.deepEqual(result.names,names);
  assert.match(renderNavigationMarkdown(result),/Position-É/);
});
test("producer-permitted backticks in API names cannot break Markdown table cells",()=>{
  const name="Inspect.Unit.Name`Odd";
  const md=renderNavigationMarkdown(summarize({names:["Inspect.Unit.Detail",name],
    scanned:3,matched:2,ignored:1}));
  const row=md.split("\n").find(line=>line.startsWith("| 2 | "));
  assert.ok(row);
  assert.equal(row.split(" | ")[1],"Inspect.Unit.Name\\`Odd");
  assert.doesNotMatch(row,/\| 2 \| `/);
});
test("96-name retention and 2048-name scan flags are qualified partial",()=>{
  const names=Array.from({length:96},(_,i)=>`Inspect.Map.Item${String(i).padStart(3,"0")}`);
  const result=summarize({names,scanned:97,matched:97,ignored:0,truncated:1});
  assert.equal(result.status,"observed-partial");
  assert.equal(result.names.length,96);
  assert.match(renderNavigationMarkdown(result),/\*\*PARTIAL\*\*/);
  const capped=summarize({names:[],scanned:2048,matched:0,ignored:2048,capped:true});
  assert.equal(capped.status,"observed-partial");
  assert.equal(capped.scan.scanLimitReached,true);
});
test("exact documentation key membership and errors are enforced",()=>{
  const extra=documentation(DEFAULT_NAMES)+',["Inspect.Unit.Fake"]={status="error"}';
  assert.throws(()=>summarize({docEntries:extra}),/NAV_DOC_NAMES/);
  const errors=other(DEFAULT_NAMES[0])+','+
    `["${DEFAULT_NAMES[1]}"]={status="error"}`+','+other(DEFAULT_NAMES[2]);
  assert.throws(()=>summarize({docEntries:errors}),/NAV_DOC_ERRORS/);
  assert.equal(summarize({docEntries:errors,docErrors:1}).descriptions[DEFAULT_NAMES[1]].status,
    "error");
});
test("documentation UTF-8 bytes are bounded and Markdown metacharacters escaped",()=>{
  const bad=`["${DEFAULT_NAMES[0]}"]={status="returned",text="${"界".repeat(171)}",textTruncated=true}`+
    ','+documentation(DEFAULT_NAMES.slice(1));
  assert.throws(()=>summarize({docEntries:bad}),/NAV_DOC_TEXT/);
  const good=`["${DEFAULT_NAMES[0]}"]={status="returned",text="Map | <docs> ![x](https://example.invalid/x)",textTruncated=false}`+
    ','+documentation(DEFAULT_NAMES.slice(1));
  const md=renderNavigationMarkdown(summarize({docEntries:good}));
  assert.match(md,/Map \\\| &lt;docs&gt;/);
  assert.doesNotMatch(md,/!\[x\]\(https:/);
  assert.match(md,/\\!\\\[x\\\]\\\(https:/);
});
test("original single-file bytes are hashed and output creation refuses overwrite",t=>{
  const dir=fs.mkdtempSync(path.join(os.tmpdir(),"rre-nav-export-"));
  t.after(()=>fs.rmSync(dir,{recursive:true,force:true}));
  const input=path.join(dir,"RRECollector.lua");
  const output=path.join(dir,"navigation.md");
  const src=fixture();
  fs.writeFileSync(input,src);
  const receipt=readNavigationReceipt(input);
  assert.equal(receipt.sourceSha256,crypto.createHash("sha256").update(src).digest("hex"));
  const script=fileURLToPath(new URL("./export-rrecollector-navigation-api.mjs",import.meta.url));
  const args=[script,input,"--require-version","0.4.19","--output",output];
  const first=spawnSync(process.execPath,args,{encoding:"utf8"});
  assert.equal(first.status,0,first.stderr);
  assert.match(fs.readFileSync(output,"utf8"),/Inspect.Map.Detail/);
  const second=spawnSync(process.execPath,args,{encoding:"utf8"});
  assert.equal(second.status,1);
  assert.match(second.stderr,/NAV_EXPORT_FAILED/);
  assert.equal(fs.readFileSync(output,"utf8"),renderNavigationMarkdown(receipt));
});
