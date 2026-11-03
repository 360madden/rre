import test from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import os from "node:os";
import crypto from "node:crypto";
import { spawnSync } from "node:child_process";
import { parseSavedLua } from "./read-rrecollector-saved.mjs";
import { buildReceipt, readReceipt } from "./rc30-saved-receipt.mjs";

const A = "A1111111111111111", B = "A2222222222222222";
const C = "A3333333333333333", D = "A4444444444444444";
const E = "A5555555555555555", F = "A6666666666666666";
const G = "A7777777777777777";
const sha = bytes => crypto.createHash("sha256").update(bytes).digest("hex");
const meta = {
  sha256: "f".repeat(64), bytes: 1378,
  observedAtUtc: "2026-11-03T18:30:00.000Z",
  modifiedAtUtc: "2026-11-03T18:11:04.712Z"
};
const saved = {
  addonVersion: "0.4.10",
  latest: { captureComplete: true, abilities: [{lookupId:A}, {lookupId:B}] },
  candidateLookup: { sequence:5, entries:[
    {status:"returned"}, {status:"listed-not-queried"}, {status:"no-detail"}
  ]},
  toolbarSlots: {1:A,2:B,3:C,4:D,5:E,6:F,7:G}
};

test("seven exact numeric keys cannot duplicate the seventh into missing eighth",()=>{
  const r=buildReceipt(saved,meta);
  assert.equal(r.slotCount,8);
  assert.equal(r.validPinnedIds,7);
  assert.equal(r.distinctValidPinnedIds,7);
  assert.equal(r.duplicateValidPinnedIds,0);
  assert.equal(r.eighthSlotEmpty,true);
  assert.equal(r.slotStates[7],"empty");
  assert.equal(r.validIdPresentInKnown,2);
  assert.equal(r.validIdAbsentFromKnown,5);
  assert.equal(r.candidateCount,3);
  assert.deepEqual(Object.fromEntries(Object.entries(r.candidateStatuses)),{
    returned:1,"listed-not-queried":1,"no-detail":1
  });
  assert.equal(r.pinUndoInGameVerified,false);
  assert.equal(r.rawAbilityIdsEmitted,false);
  const output=JSON.stringify(r);
  for(const id of [A,B,C,D,E,F,G]) assert.equal(output.includes(id),false);
});

test("canonical fingerprint changes when slot eight becomes genuinely populated",()=>{
  const x=buildReceipt(saved,meta);
  const y=buildReceipt({...saved,toolbarSlots:{...saved.toolbarSlots,8:A}},meta);
  assert.equal(y.validPinnedIds,8);
  assert.equal(y.duplicateValidPinnedIds,1);
  assert.equal(y.distinctValidPinnedIds,7);
  assert.equal(y.eighthSlotEmpty,false);
  assert.notEqual(x.slotArraySha256,y.slotArraySha256);
});

test("malformed values are reported but not falsely counted as valid",()=>{
  const r=buildReceipt({...saved,toolbarSlots:{1:"not-an-id",2:7,3:null,7:A}},meta);
  assert.deepEqual(r.slotStates.slice(0,3),
    ["invalid-stored-value","invalid-stored-value","empty"]);
  assert.equal(r.validPinnedIds,1);
  assert.equal(r.slotStates[6],"ability-id");
  assert.equal(r.eighthSlotEmpty,true);
});

test("fail-closed unexpected numeric slots and ambiguous keys",()=>{
  for(const toolbarSlots of [{"0":A},{"9":B},{foo:A},A,{"01":A}])
    assert.throws(()=>buildReceipt({...saved,toolbarSlots},meta),/TOOLBAR_/);
  assert.throws(()=>buildReceipt({...saved,latest:{abilities:"oops"}},meta),/KNOWN_ABILITY_/);
});

test("pure parser handles literal Lua saves without executing source",()=>{
  const lua='RRECollectorData = { addonVersion = "0.4.10", ' +
    'latest = { captureComplete = true, abilities = { { lookupId = "'+A+'" } } }, ' +
    'candidateLookup = {sequence=5, entries = { {status="returned"} } }, ' +
    'toolbarSlots = { [1]="'+A+'", [7]="'+G+'" } }';
  const parsed=parseSavedLua(lua),r=buildReceipt(parsed,meta);
  assert.equal(r.validPinnedIds,2);
  assert.equal(r.eighthSlotEmpty,true);
  assert.equal(r.slotArraySha256.length,64);
  assert.equal(r.candidateStatuses.returned,1);
});

test("one read of temporary saved file returns source-bound, redacted receipt",()=>{
  const dir=fs.mkdtempSync(path.join(os.tmpdir(),"rre-rc30-receipt-test-"));
  try {
    const file=path.join(dir,"RRECollector.lua");
    const b=Buffer.from('RRECollectorData = { addonVersion="0.4.10", ' +
      'latest={captureComplete=true,abilities={{lookupId="'+A+'"}}}, ' +
      'candidateLookup={sequence=5,entries={{status="returned"}}}, ' +
      'toolbarSlots={[1]="'+A+'",[7]="'+G+'"} }', "utf8");
    fs.writeFileSync(file,b);
    const r=readReceipt(file,sha(b));
    assert.equal(r.sourceSha256,sha(b));
    assert.equal(r.sourceBytes,b.length);
    assert.equal(r.validPinnedIds,2);
    assert.equal(r.eighthSlotEmpty,true);
    assert.equal(JSON.stringify(r).includes(A),false);
    assert.throws(()=>readReceipt(file,"0".repeat(64)),/SOURCE_SHA_MISMATCH/);
    assert.throws(()=>readReceipt(file,"not-hash"),/EXPECTED_SHA_INVALID/);
    assert.throws(()=>readReceipt(path.join(dir,"wrong.lua")),/ONLY_RRECOLLECTOR_SAVED_FILE/);
  } finally {
    fs.rmSync(dir,{recursive:true,force:true});
  }
});

test("implicit eight-entry Lua table and explicit [1]..[8] normalize identically",()=>{
  const entries=[A,B,C,D,E,F,G,A];
  const implicit='RRECollectorData = { addonVersion="0.4.10", toolbarSlots={' +
    entries.map(v=>'"'+v+'"').join(',') + '} }';
  const explicit='RRECollectorData = { addonVersion="0.4.10", toolbarSlots={' +
    entries.map((v,i)=>'['+(i+1)+']="'+v+'"').join(',') + '} }';
  const a=buildReceipt(parseSavedLua(implicit),meta);
  const b=buildReceipt(parseSavedLua(explicit),meta);
  assert.equal(a.slotStorageForm,"implicit-lua-array");
  assert.equal(b.slotStorageForm,"explicit-numeric-lua-table");
  assert.equal(a.validPinnedIds,8);
  assert.equal(b.validPinnedIds,8);
  assert.equal(a.distinctValidPinnedIds,7);
  assert.equal(a.eighthSlotEmpty,false);
  assert.equal(a.slotArraySha256,b.slotArraySha256);
  assert.ok(a.slotStates.every(v=>v==="ability-id"));
});

test("sparse JavaScript array does not create a false ability ID",()=>{
  const storage=Array(8);
  storage[0]=A;
  storage[6]=G;
  const r=buildReceipt({...saved,toolbarSlots:storage},meta);
  assert.equal(r.validPinnedIds,2);
  assert.equal(r.eighthSlotEmpty,true);
  assert.equal(r.slotStates[7],"empty");
});

test("pathname replacement before open is rejected, not analyzed",()=>{
  const dir=fs.mkdtempSync(path.join(os.tmpdir(),"rre-rc30-race-test-"));
  const file=path.join(dir,"RRECollector.lua");
  const replacement=path.join(dir,"replacement.lua");
  const source='RRECollectorData = { addonVersion="0.4.10",toolbarSlots={} }';
  try {
    fs.writeFileSync(file,source);
    fs.writeFileSync(replacement,source+" ");
    const prior=fs.openSync;
    fs.openSync=(name,...rest)=>{
      if(name===file){fs.rmSync(file);fs.renameSync(replacement,file);}
      return prior(name,...rest);
    };
    try{
      assert.throws(()=>readReceipt(file),/SOURCE_CHANGED_BETWEEN_LOOKUP_AND_OPEN/);
    }finally{fs.openSync=prior;}
  }finally{fs.rmSync(dir,{recursive:true,force:true});}
});

test("unexpected candidate statuses and filesystem failures never print source data",()=>{
  const malicious="uPRIVATE_NOT_A_STATUS";
  const r=buildReceipt({
    ...saved,candidateLookup:{entries:[{status:malicious}],sequence:5}
  },meta);
  assert.equal(r.candidateStatuses.other,1);
  assert.equal(JSON.stringify(r).includes(malicious),false);
  const missing=path.join(os.tmpdir(),"rre-a-private-directory","RRECollector.lua");
  const actual=spawnSync(process.execPath,[
    "tools/rc30-saved-receipt.mjs",missing
  ],{cwd:process.cwd(),encoding:"utf8",timeout:4000});
  assert.equal(actual.status,1);
  assert.ok(actual.stderr.includes("SOURCE_READ_OR_PARSE_FAILED"));
  assert.equal(actual.stderr.includes(missing),false);
});

test("no sample or role claim is inferred from saved bytes",()=>{
  const r=buildReceipt(saved,meta);
  for(const field of ["roleFromLiveProcessVerified","sourceWriterPidVerified","pinUndoInGameVerified"])
    assert.equal(r[field],false);
  assert.equal(r.sourceKind.includes("G1"),true);
  assert.equal(r.sourceFilename,"RRECollector.lua");
});
