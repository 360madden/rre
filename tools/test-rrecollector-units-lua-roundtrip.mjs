// Real pinned Lua 5.1 producer -> literal SavedVariables -> strict Node exporter.
// Offline only. No RIFT instance, installed addon, gameplay inputs, or new dependencies.
import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import crypto from 'node:crypto';
import {fileURLToPath} from 'node:url';
import {readUnitWitness} from './export-rrecollector-units.mjs';
import {validateRoundtripRuntime,runRoundtripLua51} from './lua51-roundtrip-runtime.mjs';

const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
// Fail the suite once, before registering any runtime-dependent cases.
const runtime=validateRoundtripRuntime(root);

const SELF='u0000000000000001';
const id=n=>'u'+n.toString(16).toUpperCase().padStart(16,'0');

function runLua(mode){
  const code=String.raw`
local mode = "${mode}"
dofile("addons/RRECollector/core.lua")
dofile("addons/RRECollector/units.lua")
local function id(n) return "u"..string.format("%016X",n) end
local selfId = id(1)
Inspect = {Time = {Frame=function() return 12.5 end, Real=function() return 17.25 end},
  Unit = {Lookup=function(spec) assert(spec=="player"); return selfId end,
    List=function()
      if mode=="list-error" then error("synthetic first List exception") end
      local values={[selfId]="player"}
      local maximum=(mode=="cap129" and 130) or (mode=="cap9" and 10) or
        (mode=="empty" and 1) or 3
      for n=2,maximum do values[id(n)]="group"..tostring(n) end
      return values
    end,
    Detail=function(key)
      if mode=="error" and key==id(2) then error("synthetic Detail exception") end
      if mode=="identity" and key==id(2) then return {id=id(9),coordX=0,coordY=-2,coordZ=3} end
      return {id=key,coordX=0,coordY=-2,coordZ=3}
    end}}
if mode=="no-api" then Inspect.Unit.List=nil end
local report=RRECollectorRuntime.units.capture()
assert(type(report)=="table")
assert(report.addonVersion=="0.4.23")
assert(report.counts.detailsCalled<=8 and report.counts.examined<=128)
local saved
if report.status=="error" or report.status=="unavailable" then
  -- main.lua records this attempt but leaves all successful snapshot keys absent.
  saved={addonVersion="0.4.23",
    unitAttempt={schemaVersion=1,addonVersion="0.4.23",attemptSequence=1,
      status=report.status,reason=report.reason}}
else
  report.sequence=1
  saved={addonVersion="0.4.23",unitSnapshotSequence=1,unitSnapshots={report},
    unitAttempt={schemaVersion=1,addonVersion="0.4.23",attemptSequence=1,
      status=report.status,reason=report.reason,resultSequence=1}}
end
local function encode(value)
  local kind=type(value)
  if kind=="string" then return string.format("%q",value) end
  if kind=="number" then assert(value==value and value~=math.huge and value~=-math.huge)
    return string.format("%.17g",value) end
  if kind=="boolean" then return tostring(value) end
  assert(kind=="table", "unexpected value type")
  local num,txt={},{}
  for key in pairs(value) do
    if type(key)=="number" then num[#num+1]=key
    elseif type(key)=="string" then txt[#txt+1]=key
    else error("invalid fixture table key") end
  end
  table.sort(num); table.sort(txt)
  local pairsOut={}
  for _,key in ipairs(num) do
    pairsOut[#pairsOut+1]="["..tostring(key).."]="..encode(value[key])
  end
  for _,key in ipairs(txt) do
    pairsOut[#pairsOut+1]="["..string.format("%q",key).."]="..encode(value[key])
  end
  return "{"..table.concat(pairsOut,",").."}"
end
io.write("RRECollectorData=",encode(saved),"\n")
`;
  const proc=runRoundtripLua51(['-e',code],{root});
  if(proc.error)throw proc.error;
  assert.equal(proc.status,0,mode+': '+proc.stderr);
  assert.equal(proc.stderr,'',mode+': Lua unexpectedly wrote stderr');
  assert.ok(proc.stdout.startsWith('RRECollectorData='),mode+': missing assignment');
  assert.ok(Buffer.byteLength(proc.stdout)<30000,mode+': output exceeded fixture bound');
  const dir=fs.mkdtempSync(path.join(os.tmpdir(),'rre-unit-roundtrip-'));
  const file=path.join(dir,'RRECollector.lua');
  try {
    fs.writeFileSync(file,proc.stdout,'utf8');
    const report=readUnitWitness(file);
    assert.equal(report.sourceSha256,
      crypto.createHash('sha256').update(Buffer.from(proc.stdout)).digest('hex'));
    assert.equal(report.savedAddonVersion,'0.4.23');
    if(mode==='no-api'||mode==='list-error'){
      assert.equal(report.snapshotState,'attempt-only');
      assert.equal(report.snapshots.length,0);
      assert.equal(report.lastAttempt.resultSequence,null);
    }else{
      assert.equal(report.snapshotState,'retained-snapshots');
      assert.equal(report.snapshots[0].sequence,1);
      assert.equal(report.lastAttempt.resultSequence,1);
    }
    assert.equal(report.qualification.nativeIdentityVerified,false);
    assert.equal(report.qualification.live,false);
    return report;
  } finally {
    fs.unlinkSync(file);fs.rmdirSync(dir);
  }
}
test('explicit Lua runtime profile satisfies its own qualification contract',()=>{
  if(runtime.profile==='historical-windows-5.1.4'){
    assert.equal(runtime.exeSha256,'6675a1c46671d8bbdfea2b94704c495a2cb9e7accaffbb309f85c025752c2c67');
    assert.equal(runtime.dllSha256,'9224c9f2929cff5a0a10ce1d795a9d83112eead52b93ce625e31a24fa6f31096');
  }else{
    assert.equal(runtime.profile,'compat-5.1.5');
    assert.equal(runtime.exeSha256,process.env.RRE_LUA51_COMPAT_SHA256);
    assert.equal(runtime.dllSha256,null);
  }
});
test('real Lua missing API yields only a retained unavailable attempt',()=>{
  const out=runLua('no-api');
  assert.equal(out.snapshotState,'attempt-only');
  assert.equal(out.lastAttempt.status,'unavailable');
  assert.equal(out.lastAttempt.reason,'missing-unit-api');
  assert.equal(out.snapshots.length,0);
});
test('real Lua first List exception yields only an error attempt',()=>{
  const out=runLua('list-error');
  assert.equal(out.snapshotState,'attempt-only');
  assert.equal(out.lastAttempt.status,'error');
  assert.equal(out.lastAttempt.reason,'unit-list-error');
  assert.equal(out.snapshots.length,0);
});
test('real Lua complete witness survives SavedVariables parsing and strict exporter',()=>{
  const out=runLua('complete');
  assert.equal(out.snapshots[0].status,'complete');
  assert.equal(out.snapshots[0].reason,'bounded-sample-complete');
  assert.equal(out.snapshots[0].counts.qualifiedXYZ,2);
  assert.deepEqual(out.snapshots[0].records.map(r=>r.id),[id(2),id(3)]);
  assert.equal(out.snapshots[0].records[0].coordX,0);
  assert.equal(out.snapshots[0].records[0].coordY,-2);
});
test('real Lua empty witness remains distinct from API unavailability',()=>{
  const out=runLua('empty');
  assert.equal(out.snapshots[0].status,'empty');
  assert.equal(out.snapshots[0].reason,'no-nonself-listed');
  assert.equal(out.snapshots[0].records.length,0);
});
test('real Lua missing/mismatched identity never retains unbound XYZ',()=>{
  const out=runLua('identity');
  assert.equal(out.snapshots[0].status,'partial');
  assert.equal(out.snapshots[0].reason,'detail-identity-unqualified');
  assert.equal(out.snapshots[0].counts.idMismatches,1);
  const row=out.snapshots[0].records[0];
  assert.equal(row.idBinding,'mismatch');
  assert.equal(row.xyzComplete,false);
  assert.equal(Object.hasOwn(row,'coordX'),false);
});
test('real Lua partial Detail error is preserved as partial error receipt',()=>{
  const out=runLua('error');
  assert.equal(out.snapshots[0].status,'partial');
  assert.equal(out.snapshots[0].reason,'detail-errors');
  assert.equal(out.snapshots[0].counts.detailErrors,1);
  assert.equal(out.snapshots[0].records[0].detailStatus,'error');
});
test('real Lua 9-to-8 detail limit remains an incomplete sample',()=>{
  const out=runLua('cap9');
  assert.equal(out.snapshots[0].status,'partial');
  assert.equal(out.snapshots[0].reason,'detail-sample-cap');
  assert.equal(out.snapshots[0].counts.detailsCalled,8);
  assert.equal(out.snapshots[0].records.length,8);
  assert.equal(out.snapshots[0].coverage.detailSampleComplete,false);
});
test('real Lua 129+ list entries cannot claim complete enumeration',()=>{
  const out=runLua('cap129');
  assert.equal(out.snapshots[0].status,'capped');
  assert.equal(out.snapshots[0].reason,'list-cap-reached');
  assert.equal(out.snapshots[0].counts.examined,128);
  assert.equal(out.snapshots[0].coverage.listEnumerationComplete,false);
  assert.equal(out.snapshots[0].counts.detailsCalled,8);
});
