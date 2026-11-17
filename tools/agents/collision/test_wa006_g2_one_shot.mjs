// WA-006 offline mock tests using pinned Windows Lua 5.3 (default) or 5.1 (--lua51).
// No dependency installation, RIFT process, input, game addon, or external writes.
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import assert from 'node:assert/strict';
import {spawnSync} from 'node:child_process';

const root = process.cwd();
const probePath = path.join(root, 'tools/agents/collision/wa006_g2_one_shot.lua');
const sha = file => crypto.createHash('sha256').update(fs.readFileSync(file)).digest('hex');
const mode = process.argv[2] || '--lua53';
assert.ok(process.argv.length <= 3 && (mode === '--lua53' || mode === '--lua51'),
  'Usage: node test_wa006_g2_one_shot.mjs [--lua53|--lua51]');
const lua51Root = path.join(root, 'artifacts/sc103-lua51-msvc-20261104-1925-v1');
const runtime = mode === '--lua51' ? {
  label: 'Windows Lua 5.1.4/hash-pinned',
  exe: path.join(lua51Root, 'lua.exe'),
  dll: path.join(lua51Root, 'lua51.dll'),
  exeSha256: '6675a1c46671d8bbdfea2b94704c495a2cb9e7accaffbb309f85c025752c2c67',
  dllSha256: '9224c9f2929cff5a0a10ce1d795a9d83112eead52b93ce625e31a24fa6f31096',
} : {
  label: 'Windows Lua 5.3.0/hash-pinned',
  exe: 'C:\\work\\tools\\cheat-engine-master\\Cheat Engine\\bin\\lua_extra\\lua.exe',
  dll: 'C:\\work\\tools\\cheat-engine-master\\Cheat Engine\\bin\\lua53-32.dll',
  exeSha256: '702502820320538d06409d7818754ce529087ef8ff608a723f49b1ccffdc2d6f',
  dllSha256: '58b206ab9a3d84fdafb537b419f721ecdeade489707dbab227b043d5343db369',
};
assert.equal(sha(runtime.exe), runtime.exeSha256, 'interpreter source integrity mismatch');
assert.equal(sha(runtime.dll), runtime.dllSha256, 'runtime DLL integrity mismatch');
const beforeSource = sha(probePath);
const scenarios = [];
function scenario(name, mock, verify) {
  const code = [
    'print = function() end',
    mock,
    "local report = dofile('tools/agents/collision/wa006_g2_one_shot.lua')",
    "io.write(report, '\\n')",
  ].join('\n');
  const env = {...process.env,
    PATH:path.dirname(runtime.dll) + path.delimiter + (process.env.PATH || '')};
  const r = spawnSync(runtime.exe, ['-e', code], {cwd:root, env, timeout:5000, encoding:'utf8',
    windowsHide:true, shell:false, maxBuffer:8192});
  if (r.error) throw r.error;
  assert.equal(r.status, 0, name + ': Lua failed: ' + (r.stderr || ''));
  assert.equal(r.stderr, '', name + ': unexpected Lua stderr');
  assert.ok(r.stdout.length <= 4096, name + ': oversized output');
  verify(r.stdout);
  scenarios.push(name);
}
const coreMock = String.raw`
Inspect = {
 Time = {Frame = function() return 12.5 end, Real = function() return 13.5 end},
 Unit = {
   Lookup = function(s) assert(s == 'player'); return 'u035400012FA2D207' end,
   List = function()
     return {['u035400012FA2D207']='player',
       ['u035400012FA2D208']='target.one',
       ['u035400012FA2D209']='target.two'}
   end,
   Detail = function(id)
     if id == 'u035400012FA2D208' then
       return {id=id, coordX=100.125, coordY=200.25, coordZ=300.5}
     end
     return {id=id, coordX=111, coordY=222, coordZ=333}
   end
 }
}`;
scenario('missing-api', '', report => {
  assert.match(report, /WA006_G2_V1\|ERROR\|missing-unit-api/);
});
scenario('two-independent-nonself', coreMock, report => {
  assert.match(report, /BEGIN\|self=u035400012FA2D207\|frame=12.500000\|real=13.500000/);
  assert.match(report, /ROW\|id=u035400012FA2D208\|specifier=target.one\|x=100.125000/);
  assert.match(report, /ROW\|id=u035400012FA2D209\|specifier=target.two\|x=111.000000/);
  assert.doesNotMatch(report, /ROW\|id=u035400012FA2D207/);
  assert.match(report, /END\|examined=3\|details=2\|validXYZ=2\|errors=0\|capped=false/);
});
scenario('list-error', String.raw`
Inspect = {Unit = {
  Lookup = function() return 'u035400012FA2D207' end,
  List = function() error('unavailable') end,
  Detail = function() return {} end
}}`, report => {
  assert.match(report, /ERROR\|unit-list-unavailable/);
  assert.doesNotMatch(report, /ROW\|/);
});
scenario('missing-self', String.raw`
Inspect = {Unit = {
  Lookup = function() return nil end,
  List = function() error('must-not-call') end,
  Detail = function() return {} end
}}`, report => {
  assert.match(report, /ERROR\|player-id-unavailable/);
  assert.doesNotMatch(report, /BEGIN\|/);
});
scenario('invalid-specifier-and-unknown-coordinates', String.raw`
Inspect = {Unit = {
  Lookup = function() return 'u035400012FA2D207' end,
  List = function() return {
    ['u035400012FA2D208']='unsafe|specifier',
    ['u035400012FA2D209']='safe.specifier'
  } end,
  Detail = function() return {coordX=0/0, coordY=22, coordZ=33} end
}}`, report => {
  assert.doesNotMatch(report, /unsafe\|specifier/);
  assert.match(report, /ROW\|id=u035400012FA2D209\|specifier=safe.specifier\|x=unknown/);
  assert.match(report, /details=1\|validXYZ=0/);
});
scenario('strict-output-caps', String.raw`
Inspect = {Unit = {
  Lookup = function() return 'u035400012FA2D207' end,
  List = function()
    local t = {}
    for i=1,130 do t[string.format('u%016X',i)]='visible'..i end
    return t
  end,
  Detail = function(id) return {id=id,coordX=1,coordY=2,coordZ=3} end
}}`, report => {
  assert.match(report, /END\|examined=128\|details=8\|validXYZ=8\|errors=0\|capped=true/);
  assert.equal((report.match(/ROW\|/g) || []).length, 8);
});
scenario('malformed-self-id', String.raw`
Inspect = {Unit = {
  Lookup = function() return 'not-a-rift-id' end,
  List = function() error('must-not-call') end,
  Detail = function() return {} end
}}`, report => {
  assert.match(report, /ERROR\|player-id-unavailable/);
  assert.doesNotMatch(report, /BEGIN\|/);
});
scenario('malformed-list-id', String.raw`
Inspect = {Unit = {
  Lookup = function() return 'u035400012FA2D207' end,
  List = function() return {
    ['not-a-unit-id']='bad',
    ['u035400012FA2D208']='good.specifier'
  } end,
  Detail = function(id) return {id=id,coordX=4, coordY=5, coordZ=6} end
}}`, report => {
  assert.doesNotMatch(report, /ROW\|id=not-a-unit-id/);
  assert.match(report, /ROW\|id=u035400012FA2D208\|specifier=good.specifier/);
  assert.match(report, /END\|examined=2\|details=1\|validXYZ=1/);
});
scenario('detail-id-absent-unverified', String.raw`
Inspect = {Unit = {
   Lookup = function() return 'u035400012FA2D207' end,
   List = function() return {['u035400012FA2D208']='candidate'} end,
   Detail = function() return {coordX=123, coordY=456, coordZ=789} end
}}`, report => {
  assert.match(report, /ROW\|id=u035400012FA2D208\|specifier=candidate\|x=123.000000/);
  assert.match(report, /idBinding=missing/);
  assert.match(report, /validXYZ=0\|errors=0/);
});
scenario('detail-id-mismatch-rejected', String.raw`
Inspect = {Unit = {
  Lookup = function() return 'u035400012FA2D207' end,
  List = function() return {['u035400012FA2D208']='candidate'} end,
  Detail = function() return {
    id='u035400012FA2D209', coordX=123, coordY=456, coordZ=789
  } end
}}`, report => {
  assert.match(report, /ERROR\|detail-id-mismatch\|id=u035400012FA2D208/);
  assert.doesNotMatch(report, /ROW\|/);
  assert.match(report, /validXYZ=0\|errors=1/);
});
assert.equal(sha(probePath), beforeSource, 'probe file changed during test');
assert.ok(fs.statSync(probePath).size < 8192, 'probe source too large');
process.stdout.write(JSON.stringify({task:'WA-006',runtime:runtime.label,
  scope:'mocked-offline-only',tests:scenarios.length,scenarios,sourceSha256:beforeSource,
  liveQualified:false})+'\n');

