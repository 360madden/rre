// WA-006 G2 cross-source preflight: synthetic memory-only negative controls, NO game.
import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {preflightG2Sources} from './verify_wa006_g2_cross_source_preflight.mjs';

const marker = 'WA006_G2_V1';
const self = 'u035400012FA2D207';
const idA = 'u80000001C0001EEC';
const idB = 'u8000000215000A32';
const luaSourceSha = '990c91a06cb0398cbc3e495c59169b43b11bd0c29d132319c30607d39f448b5e';
const startTicks = '639304372516074064';
const buildSha = '1935a05c9db6d468e34e0055014a4a99c1b5afceb1695884e24600f5c20a4be8';
const time = tail => '2026-11-16T21:00:' + tail + '+00:00';
const hash = buf => createHash('sha256').update(buf).digest('hex');
const decimal = id => BigInt('0x' + id.slice(1)).toString();
const selfXYZ = [100, 200, 300];
function f32bits(n) {
  const b = Buffer.alloc(4);
  b.writeFloatLE(n, 0);
  return b.readUInt32LE(0);
}
function row(id, xyz, t1, t2) {
  return {unitKey:decimal(id), unitIdCandidate:id, entityAddressDecimal:'2624201508368',
    positionCandidate:{x:xyz[0], y:xyz[1], z:xyz[2]},
    rawBits:xyz.map(f32bits), startedAtUtc:time(t1), completedAtUtc:time(t2),
    horizontalDistanceCandidate:Math.hypot(xyz[0] - selfXYZ[0], xyz[2] - selfXYZ[2])};
}
function fixture() {
  const packet = [
    marker + '|BEGIN|self=' + self + '|frame=12.500000|real=13.500000',
    marker + '|ROW|id=' + idA + '|specifier=other.one|x=100.125000|y=200.250000|z=300.500000|idBinding=matched',
    marker + '|ROW|id=' + idB + '|specifier=other.two|x=111.000000|y=222.000000|z=333.000000|idBinding=matched',
    marker + '|END|examined=3|details=2|validXYZ=2|errors=0|capped=false|frameEnd=13.500000|realEnd=14.500000|status=exploratory-only'
  ].join('\n') + '\n';
  const native = {schemaVersion:1, contractVersion:'native-current-unit-positions-candidate-sample/1',
    status:'complete', observation:{
      identity:{processId:77704,processStartUtcTicks:'TICKS_LITERAL',executableSha256:buildSha.toUpperCase()},
      startedAtUtc:time('01.0000000'),completedAtUtc:time('01.0300000'),
      selfKey:decimal(self),selfPositionCandidate:{x:100,y:200,z:300},
      selfPositionRawBits:selfXYZ.map(f32bits),
      worldIdentityStatus:'unavailable',
      unitLimit:8, examined:2, noPosition:0, unavailable:0, unavailableChains:0,
      bucketsExamined:4, startBucket:0, bucketCount:4, unitLimitReached:false, readBytes:512,
      opticalCameraCandidate:null, opticalCameraAfterCandidate:null, cameraStableCandidate:false,
      rows:[row(idA,[100.125,200.25,300.5],'01.0100001','01.0110001'),
        row(idB,[111,222,333],'01.0200001','01.0210001')]
    }};
  const receipt={schemaVersion:1,kind:'WA006_G2_REJECTION_ONLY_V1',hostName:'AMD-DESKTOP',
    ownerLeaseId:'UNVERIFIED-SYNTHETIC-OWNER',sceneWitnessSha256:'a'.repeat(64),
    process:{processId:77704,processStartUtcTicks:startTicks,executableSha256:buildSha},
    lua:{sourceSha256:luaSourceSha,transcriptSha256:'',
      startedAtUtc:time('00.5000000'),completedAtUtc:time('01.5000000')},
    nativeSourceSha256:'',
    window:{startedAtUtc:time('00.0000000'),completedAtUtc:time('02.0000000')}};
  return {packet,native,receipt,keepHashes:false,nativeRawRewrite:null};
}
function serializeNative(native) {
  const json = JSON.stringify(native);
  const marker = '"TICKS_LITERAL"';
  assert.equal(json.split(marker).length, 2, 'one lossless source integer slot');
  return Buffer.from(json.replace(marker, startTicks));
}
let tests = 0;
function check(name, modify, expectedConsistent, reason, forbiddenReason) {
  const x = fixture();
  modify?.(x);
  const luaRaw = Buffer.from(x.packet);
  const original = serializeNative(x.native);
  const nativeRaw = x.nativeRawRewrite ?
    Buffer.from(x.nativeRawRewrite(original.toString('utf8'))) : original;
  if (!x.keepHashes) {
    x.receipt.lua.transcriptSha256 = hash(luaRaw);
    x.receipt.nativeSourceSha256 = hash(nativeRaw);
  }
  const result = preflightG2Sources(luaRaw, nativeRaw, x.receipt);
  assert.equal(result.sourceFieldsConsistent, expectedConsistent,
    name + ': ' + result.reasons.join(','));
  assert.equal(result.wa006Accepted, false, name + ': never accept WA-006');
  assert.equal(result.nativeCorrelationDone, false, name + ': never qualify native match');
  assert.ok(result.limitations.includes('nonself-coordinate-tolerance-unqualified'),
    name + ': synthetic coordinates cannot calibrate');
  if (reason) assert.ok(result.reasons.includes(reason), name + ': expected ' + reason +
    ', got ' + result.reasons.join(','));
  if (forbiddenReason) assert.ok(!result.reasons.includes(forbiddenReason),
    name + ': unexpected ' + forbiddenReason + ', got ' + result.reasons.join(','));
  tests++;
}

check('synthetic-exact-fields-candidate-only', null, true);
check('source-lossless-unquoted-ticks-candidate-only', null, true);
check('swapped-Lua-ID-unknown-native', x => {x.packet=x.packet.replace('id='+idB,'id=u8000000215000A33');},
  false,'missing-independent-nonself-key');
check('swapped-two-existing-Lua-IDs-preserve-XYZ', x => {
  x.packet=x.packet.replace('id='+idA,'id=TEMP').replace('id='+idB,'id='+idA)
    .replace('id=TEMP','id='+idB);
}, false,'uncalibrated-coordinate-mismatch');
check('large-coordinate-discrepancy', x => {
  x.native.observation.rows[0].positionCandidate.x=999999;
  x.native.observation.rows[0].rawBits[0]=f32bits(999999);
  x.native.observation.rows[0].horizontalDistanceCandidate=
    Math.hypot(999999-selfXYZ[0],300.5-selfXYZ[2]);
}, false,'uncalibrated-coordinate-mismatch');
check('native-epoch-decimal-not-rounded', x => {x.receipt.process.processStartUtcTicks =
  String(Number(startTicks));}, false,'process-epoch-or-build-mismatch');
check('lossless-token-decoy-not-identity', x => {
  x.native.observation.identity.processStartUtcTicks=startTicks;
  x.native.decoy={processStartUtcTicks:'TICKS_LITERAL'};
}, false,'invalid-or-lossy-native-JSON');
check('different-process', x => {x.receipt.process.processId=77705;},
  false,'process-epoch-or-build-mismatch');
check('different-executable', x => {x.receipt.process.executableSha256='b'.repeat(64);},
  false,'process-epoch-or-build-mismatch');
check('stale-native-source', x => {
  x.native.observation.startedAtUtc=time('03.0000000');
  x.native.observation.completedAtUtc=time('03.0300000');
  for(const r of x.native.observation.rows) {
    r.startedAtUtc=r.startedAtUtc.replace('21:00:01','21:00:03');
    r.completedAtUtc=r.completedAtUtc.replace('21:00:01','21:00:03');
  }
}, false,'stale-cross-source-window');
check('stale-Lua-receipt', x => {x.receipt.lua.startedAtUtc=time('03.0000000');
  x.receipt.lua.completedAtUtc=time('03.5000000');}, false,'stale-cross-source-window');
check('nonoverlapping-Lua-native-within-window', x => {
  x.receipt.lua.startedAtUtc=time('00.1000000');
  x.receipt.lua.completedAtUtc=time('00.5000000');
}, false,'disjoint-cross-source-UTC');
check('seventh-digit-UTC-row-order', x => {
  x.native.observation.rows[0].completedAtUtc=time('01.0200002');
  x.native.observation.rows[1].startedAtUtc=time('01.0200001');
}, false,'invalid-or-unordered-UTC-bracket');
check('misbound-self', x => {x.native.observation.selfKey=decimal(idA);},
  false,'self-native-key-mismatch');
check('native-key-derived-only-tamper', x => {
  x.native.observation.rows[0].unitIdCandidate='uFFFFFFFFFFFFFFFF';
}, false,'invalid-native-unit-key-or-position');
check('native-float32-tamper', x => {x.native.observation.rows[0].rawBits[0]++;},
  false,'invalid-native-unit-key-or-position');
check('native-self-float32-tamper', x => {x.native.observation.selfPositionRawBits[0]++;},
  false,'invalid-native-unit-positions-contract');
check('native-distance-from-float32-not-rounded-JSON', x => {
  const r=x.native.observation.rows[0];
  r.positionCandidate={x:6120.2207,y:942.88794,z:5222.583};
  r.rawBits=[1170162116,1147910356,1168323754];
  r.horizontalDistanceCandidate=Math.hypot(Math.fround(r.positionCandidate.x)-100,
    Math.fround(r.positionCandidate.z)-300);
}, false,'uncalibrated-coordinate-mismatch','invalid-native-unit-key-or-position');
check('native-float32-overflow-to-infinity', x => {
  x.native.observation.rows[0].positionCandidate.x=1e40;
  x.native.observation.rows[0].rawBits[0]=0x7f800000;
}, false,'invalid-native-unit-key-or-position');
check('duplicate-native-key', x => {x.native.observation.rows[1].unitKey=decimal(idA);
  x.native.observation.rows[1].unitIdCandidate=idA;},
  false,'invalid-native-unit-key-or-position');
check('native-row-invalid-entity-address', x => {
  x.native.observation.rows[0].entityAddressDecimal='1';
}, false,'invalid-native-unit-key-or-position');
check('native-row-negative-horizontal-distance', x => {
  x.native.observation.rows[0].horizontalDistanceCandidate=-1;
}, false,'invalid-native-unit-key-or-position');
check('native-examined-count-corrupt', x => {x.native.observation.examined=3;},
  false,'invalid-native-unit-positions-contract');
check('native-noPosition-count-corrupt', x => {x.native.observation.noPosition=1;},
  false,'invalid-native-unit-positions-contract');
check('native-unitLimit-zero', x => {x.native.observation.unitLimit=0;},
  false,'invalid-native-unit-positions-contract');
check('native-cameraStable-null', x => {x.native.observation.cameraStableCandidate=null;},
  false,'invalid-native-unit-positions-contract');
check('native-cameraStable-false-positive', x => {x.native.observation.cameraStableCandidate=true;},
  false,'invalid-native-unit-positions-contract');
check('duplicate-native-JSON-key', x => {x.nativeRawRewrite=s =>
  s.replace('"examined":2','"examined":2,"examined":2');},
  false,'invalid-or-lossy-native-JSON');
check('nonfinite-native-JSON-number', x => {x.nativeRawRewrite=s =>
  s.replace('"examined":2','"examined":1e999');},
  false,'invalid-or-lossy-native-JSON');
check('world-instance-claim-not-source-backed', x => {
  x.native.observation.worldIdentityStatus='verified';},
  false,'invalid-native-unit-positions-contract');
check('missing-owner-lease-receipt', x => {x.receipt.ownerLeaseId='';},
  false,'missing-external-receipt-fields');
check('missing-scene-witness', x => {x.receipt.sceneWitnessSha256=null;},
  false,'missing-external-receipt-fields');
check('wrong-host-claim', x => {x.receipt.hostName='LEGION';},
  false,'missing-external-receipt-fields');
check('wrong-canonical-Lua-source', x => {x.receipt.lua.sourceSha256='f'.repeat(64);},
  false,'source-hash-or-Lua-version-mismatch');
check('wrong-copied-transcript-sha', x => {x.keepHashes=true;
  x.receipt.lua.transcriptSha256='0'.repeat(64);
  x.receipt.nativeSourceSha256='0'.repeat(64);},
  false,'source-hash-or-Lua-version-mismatch');
check('partial-Lua-packet', x => {x.packet=x.packet.replace('|capped=false','|capped=true');},
  false,'invalid-LuaPad-transcript');
check('not-two-independently-listed-Lua-IDs', x => {x.native.observation.rows.pop();
  x.native.observation.examined=1;},
  false,'missing-independent-nonself-key');
check('native-row-after-completed', x => {
  x.native.observation.rows[1].completedAtUtc=time('01.0400000');},
  false,'invalid-or-unordered-UTC-bracket');
check('malformed-host-clock', x => {x.receipt.window.startedAtUtc='not UTC';},
  false,'invalid-or-unordered-UTC-bracket');
check('unbounded-uint64-native-key', x => {
  x.native.observation.rows[0].unitKey='18446744073709551616';},
  false,'invalid-native-unit-key-or-position');

check('native-integer-counter-written-as-float', x => {x.nativeRawRewrite=s =>
  s.replace('"unitLimit":8','"unitLimit":8.0');},
  false,'invalid-or-lossy-native-JSON');
check('native-integer-counter-written-as-exponent', x => {x.nativeRawRewrite=s =>
  s.replace('"startBucket":0','"startBucket":0e0');},
  false,'invalid-or-lossy-native-JSON');
check('native-rawBits-written-as-float', x => {x.nativeRawRewrite=s =>
  s.replace(/("rawBits":\[)([0-9]+)/,'$1$2.0');},
  false,'invalid-or-lossy-native-JSON');
check('impossible-future-process-start-ticks', x => {
  x.receipt.process.processStartUtcTicks='9999999999999999999';
  x.nativeRawRewrite=s => s.replace(startTicks,'9999999999999999999');
}, false,'invalid-native-unit-positions-contract');
check('zero-duration-native-observation', x => {
  x.native.observation.completedAtUtc=x.native.observation.startedAtUtc;
  for(const r of x.native.observation.rows) {
    r.startedAtUtc=x.native.observation.startedAtUtc;
    r.completedAtUtc=x.native.observation.startedAtUtc;
  }
}, false,'invalid-native-unit-positions-contract');
check('nonorthonormal-available-camera', x => {
  const projection=Array(16).fill(0).concat([0,1,1,0]);
  const camera={status:'available-candidate',cameraYawQualified:false,
    sourceRootRva:'0x3362848',selectedModeCameraGetterRva:'0xF88580',
    cameraAddressDecimal:'65536',rotationRowMajor:Array(9).fill(0),
    rendererEyeXYZ:[0,0,0],renderOriginXYZ:[0,0,0],rawBits:Array(15).fill(0),
    bearingDegreesCandidate:0,pitchDegreesCandidate:0,worldEyeXYZ:[0,0,0],
    projectionRowMajor:projection.slice(0,16),viewportLeftRightTopBottom:projection.slice(16),
    projectionRawBits:projection.map(f32bits)};
  x.native.observation.opticalCameraCandidate=camera;
  x.native.observation.opticalCameraAfterCandidate=structuredClone(camera);
  x.native.observation.cameraStableCandidate=true;
},false,'invalid-native-unit-positions-contract');

process.stdout.write(JSON.stringify({task:'WA-006',tests,passed:tests,
  scope:'synthetic-rejection-only-offline-cross-source-preflight',nativeCorrelationDone:false,
  wa006Accepted:false}) + '\n');
