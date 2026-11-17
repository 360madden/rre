// WA-006 G2: bounded OFFLINE rejection-only Lua/native preflight.
// A supplied receipt is a claim, NOT independent proof of execution, owner, UTC or scene.
// No positive native-correlation or WA-006 acceptance path exists in this module.
import {createHash} from 'node:crypto';
import {openSync, fstatSync, readSync, closeSync} from 'node:fs';
import {resolve} from 'node:path';
import {fileURLToPath} from 'node:url';
import {validatePacket} from './verify_wa006_g2_packet.mjs';

const SOURCE_SHA = '990c91a06cb0398cbc3e495c59169b43b11bd0c29d132319c30607d39f448b5e';
const HEX_SHA = /^[0-9a-f]{64}$/i;
const U64 = (1n << 64n) - 1n;
const UTC = /^(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2})(?:\.(\d{1,7}))?(?:Z|\+00:00)$/;
const AXES = ['x', 'y', 'z'];
const INTEGER_NATIVE_FIELDS = new Set(['schemaVersion','processId','moduleBaseAddress',
  'moduleSize','unitLimit','examined','noPosition','unavailable','unavailableChains',
  'bucketsExamined','startBucket','bucketCount','readBytes']);
const BIT_FIELDS = new Set(['rawBits','selfPositionRawBits','projectionRawBits']);

function digest(raw) { return createHash('sha256').update(raw).digest('hex'); }
function decimal64(value) {
  if (typeof value !== 'string' || !/^[1-9][0-9]*$/.test(value)) throw Error('invalid-decimal-u64');
  const n = BigInt(value);
  if (n > U64) throw Error('out-of-range-u64');
  return n;
}
function utc100ns(value) {
  if (typeof value !== 'string') throw Error('invalid-utc');
  const m = UTC.exec(value);
  if (!m) throw Error('invalid-utc');
  const millisecond = Date.parse(m[1] + 'Z');
  if (!Number.isFinite(millisecond) ||
      new Date(millisecond).toISOString().slice(0, 19) !== m[1]) throw Error('invalid-utc');
  return BigInt(millisecond) * 10000n + BigInt((m[2] || '').padEnd(7, '0'));
}
function sha(value) { return typeof value === 'string' && HEX_SHA.test(value); }
function bytes(input, limit) {
  const raw = Buffer.isBuffer(input) ? input : Buffer.from(input);
  if (raw.length === 0 || raw.length > limit) throw Error('source-size-invalid');
  return raw;
}
// Read at most the declared regular-file size. Check again after reading, so
// even a concurrent growth cannot be silently interpreted as a complete source.
function boundedFile(path, limit) {
  const fd = openSync(path, 'r');
  try {
    const st = fstatSync(fd);
    if (!st.isFile() || !Number.isSafeInteger(st.size) || st.size < 1 ||
        st.size > limit) throw Error('source-size-invalid');
    const raw = Buffer.alloc(st.size);
    let offset = 0;
    while (offset < raw.length) {
      const count = readSync(fd, raw, offset, raw.length - offset, offset);
      if (count <= 0) throw Error('source-short-read');
      offset += count;
    }
    const probe = Buffer.alloc(1);
    if (readSync(fd, probe, 0, 1, offset) !== 0) throw Error('source-size-changed');
    return raw;
  } finally {
    closeSync(fd);
  }
}
function noDuplicateObjectKeys(source) {
  // A string-aware lexical pass over the JSON itself; arrays may repeat row key names,
  // but a *single object* may not contain duplicate property names, even with \u escapes.
  const stack = [];
  for (let i = 0; i < source.length; i++) {
    const ch = source[i];
    if (ch === '{') stack.push({type:'object', keys:new Set()});
    else if (ch === '[') stack.push({type:'array'});
    else if (ch === '}' || ch === ']') {
      const popped = stack.pop();
      if (!popped || popped.type !== (ch === '}' ? 'object' : 'array'))
        throw Error('invalid-JSON-scope');
    } else if (ch === '"') {
      let j = i + 1;
      for (; j < source.length; j++) {
        if (source[j] === '\\') { j++; continue; }
        if (source[j] === '"') break;
      }
      if (j >= source.length) throw Error('unterminated-JSON-string');
      let k = j + 1;
      while (k < source.length && /\s/.test(source[k])) k++;
      if (source[k] === ':') {
        const scope = stack.at(-1);
        if (!scope || scope.type !== 'object') throw Error('invalid-JSON-key-context');
        const key = JSON.parse(source.slice(i, j + 1));
        if (scope.keys.has(key)) throw Error('duplicate-native-JSON-key');
        scope.keys.add(key);
        let valueStart = k + 1;
        while (valueStart < source.length && /\s/.test(source[valueStart])) valueStart++;
        if (INTEGER_NATIVE_FIELDS.has(key) &&
            !/^(?:0|[1-9][0-9]*)(?=\s*[,}])/.test(source.slice(valueStart)))
          throw Error('noninteger-native-number-token');
        if (BIT_FIELDS.has(key) && source[valueStart] === '[') {
          const end = source.indexOf(']', valueStart + 1);
          if (end < 0) throw Error('unterminated-native-bit-array');
          const tokens = source.slice(valueStart + 1, end).trim();
          if (tokens && tokens.split(',').some(v => !/^(?:0|[1-9][0-9]*)$/.test(v.trim())))
            throw Error('noninteger-native-bit-token');
        }
      }
      i = j;
    }
  }
  if (stack.length) throw Error('unclosed-JSON-scope');
}
function parseExternalReceipt(raw) {
  const source = new TextDecoder('utf-8', {fatal:true}).decode(raw);
  noDuplicateObjectKeys(source);
  return JSON.parse(source, (_key, value) => {
    if (typeof value === 'number' && !Number.isFinite(value))
      throw Error('nonfinite-receipt-number');
    return value;
  });
}
function nativeWithLosslessStart(raw) {
  const source = new TextDecoder('utf-8', {fatal:true}).decode(raw);
  noDuplicateObjectKeys(source);
  // Node 26 JSON.parse reviver source is the ORIGINAL numeric literal, before
  // JS Number precision is lost; reject older runtimes lacking the source context.
  let seen = 0, exact = null;
  const report = JSON.parse(source, (key, value, context) => {
    if (key === 'processStartUtcTicks') {
      if (typeof value !== 'number' || !context ||
          typeof context.source !== 'string' || !/^[1-9][0-9]*$/.test(context.source))
        throw Error('native-start-must-be-unquoted-decimal');
      decimal64(context.source);
      seen++;
      exact = context.source;
      return exact;
    }
    if (typeof value === 'number' && !Number.isFinite(value))
      throw Error('nonfinite-native-JSON-number');
    return value;
  });
  if (seen !== 1 || report?.observation?.identity?.processStartUtcTicks !== exact)
    throw Error('native-start-ticks-ambiguous-or-wrong-path');
  return report;
}
function arrayBitsMatch(values, rawBits, length) {
  if (!Array.isArray(values) || values.length !== length ||
      !Array.isArray(rawBits) || rawBits.length !== length) return false;
  return values.every((number, i) => {
    const bit = rawBits[i], encoded = Math.fround(number);
    if (typeof number !== 'number' || !Number.isFinite(number) ||
        !Number.isFinite(encoded) || !Number.isInteger(bit) ||
        bit < 0 || bit > 0xffffffff) return false;
    const buf = Buffer.allocUnsafe(4);
    buf.writeUInt32LE(bit, 0);
    const decoded = buf.readFloatLE(0);
    return Number.isFinite(decoded) && (encoded === decoded ||
      (encoded === 0 && decoded === 0));
  });
}
function floatBitsMatch(pos, bits) {
  return pos && typeof pos === 'object' &&
    arrayBitsMatch(AXES.map(axis => pos[axis]), bits, 3);
}
// Match Windows Lua 5.1 string.format("%.6f") on exact native binary32 bits.
// Convert IEEE-754 significand to integer micro-units with nearest-even ties;
// JS toFixed rounds halfway values differently and loses large fixed digits.
function luaFixed6FromFloat32Bits(bits) {
  if (!Number.isInteger(bits) || bits < 0 || bits > 0xffffffff)
    throw Error('invalid-native-float32-bits');
  const sign = bits >= 0x80000000 ? '-' : '';
  const exponent = (bits >>> 23) & 0xff;
  if (exponent === 0xff) throw Error('nonfinite-native-float32-bits');
  const significand = BigInt((exponent ? 0x800000 : 0) + (bits & 0x7fffff));
  const power = exponent === 0 ? -149 : exponent - 150;
  let micros = significand * 1000000n;
  if (power >= 0) micros <<= BigInt(power);
  else {
    const divisor = 1n << BigInt(-power);
    const whole = micros / divisor, remainder = micros % divisor;
    micros = whole + (2n * remainder > divisor ||
      (2n * remainder === divisor && (whole & 1n) === 1n) ? 1n : 0n);
  }
  return sign + (micros / 1000000n).toString() + '.' +
    (micros % 1000000n).toString().padStart(6, '0');
}
function cameraValid(camera) {
  if (camera === null) return true;
  if (!camera || typeof camera !== 'object' || camera.cameraYawQualified !== false ||
      camera.sourceRootRva !== '0x3362848' ||
      camera.selectedModeCameraGetterRva !== '0xF88580') return false;
  if (camera.status === 'unavailable')
    return typeof camera.unavailableReason === 'string' && !!camera.unavailableReason &&
      camera.rawBits == null && camera.bearingDegreesCandidate == null &&
      camera.pitchDegreesCandidate == null && camera.worldEyeXYZ == null;
  if (camera.status !== 'available-candidate') return false;
  const transform = [...(camera.rotationRowMajor || []),
    ...(camera.rendererEyeXYZ || []), ...(camera.renderOriginXYZ || [])];
  if (!Array.isArray(camera.rotationRowMajor) || camera.rotationRowMajor.length !== 9 ||
      !Array.isArray(camera.rendererEyeXYZ) || camera.rendererEyeXYZ.length !== 3 ||
      !Array.isArray(camera.renderOriginXYZ) || camera.renderOriginXYZ.length !== 3 ||
      !arrayBitsMatch(transform, camera.rawBits, 15)) return false;
  // RR2 physical_rift.py _optical_camera_values: source-bound row-orthonormal
  // rotation, yaw/pitch and world-eye consistency before trusting camera equality.
  const raw = transform.map(Math.fround);
  for (let row = 0; row < 3; row++) {
    for (let other = 0; other < 3; other++) {
      const dot = [0,1,2].reduce((sum, i) => sum + raw[row*3+i]*raw[other*3+i], 0);
      if (Math.abs(dot - (row === other ? 1 : 0)) > 0.001) return false;
    }
  }
  const horizontal = Math.hypot(raw[0],raw[6]);
  const yaw = horizontal >= 1e-8 ? Math.atan2(raw[0],raw[6])*180/Math.PI : null;
  const pitch = Math.atan2(raw[3],horizontal)*180/Math.PI;
  const angleMatch = (actual, expected) =>
    expected === null ? actual === null :
      typeof actual === 'number' && Number.isFinite(actual) &&
      Math.abs(actual-expected) <= 0.00001;
  if (!angleMatch(camera.bearingDegreesCandidate,yaw) ||
      !angleMatch(camera.pitchDegreesCandidate,pitch) ||
      !Array.isArray(camera.worldEyeXYZ) || camera.worldEyeXYZ.length !== 3 ||
      camera.worldEyeXYZ.some((v,i) => typeof v !== 'number' || !Number.isFinite(v) ||
        Math.abs(v - raw[9+i] - raw[12+i]) > 0.00001)) return false;
  if (camera.projectionRawBits == null)
    return camera.projectionRowMajor == null && camera.viewportLeftRightTopBottom == null;
  const projection = [...(camera.projectionRowMajor || []),
    ...(camera.viewportLeftRightTopBottom || [])];
  if (!Array.isArray(camera.projectionRowMajor) || camera.projectionRowMajor.length !== 16 ||
      !Array.isArray(camera.viewportLeftRightTopBottom) ||
      camera.viewportLeftRightTopBottom.length !== 4 ||
      !arrayBitsMatch(projection, camera.projectionRawBits, 20)) return false;
  const bits = projection.map(Math.fround);
  const [left,right,top,bottom] = bits.slice(16);
  if (!(0 <= left && left < right && right <= 1 &&
        0 <= bottom && bottom < top && top <= 1)) return false;
  for(let i=0;i<3;i++) if(Math.abs(bits[12+i]-raw[i*3])>0.001) return false;
  const originDot = [0,1,2].reduce((sum,i)=>sum+raw[i*3]*raw[9+i],0);
  return Math.abs(bits[15]+originDot)<=0.001;
}
function cameraSameCandidate(a, b) {
  if (!a || !b || !cameraValid(a) || !cameraValid(b) ||
      a.status !== 'available-candidate' || b.status !== 'available-candidate' ||
      !Array.isArray(a.projectionRawBits) || !Array.isArray(b.projectionRawBits)) return false;
  let address;
  try { address = decimal64(a.cameraAddressDecimal); } catch { return false; }
  return address > 0n && a.cameraAddressDecimal === b.cameraAddressDecimal &&
    JSON.stringify(a.rawBits) === JSON.stringify(b.rawBits) &&
    JSON.stringify(a.projectionRawBits) === JSON.stringify(b.projectionRawBits);
}
function nativeShapeValid(report) {
  const o = report?.observation;
  if (report?.schemaVersion !== 1 || report?.status !== 'complete' ||
      report?.contractVersion !== 'native-current-unit-positions-candidate-sample/1' ||
      !o || !o.identity || !Array.isArray(o.rows) ||
      o.worldIdentityStatus !== 'unavailable') return false;
  const names = ['unitLimit','examined','noPosition','unavailable','unavailableChains',
    'bucketsExamined','startBucket','bucketCount','readBytes'];
  const [limit, examined, absent, unavailable, chains, visited, start, buckets, readBytes] =
    names.map(name => o[name]);
  if (names.some(name => !Number.isSafeInteger(o[name])) ||
      !(limit >= 1 && limit <= 512 && examined >= 0 && examined <= limit &&
        buckets >= 1 && buckets <= 4096 && start >= 0 && start < buckets &&
        visited >= 1 && visited <= buckets && chains >= 0 && chains <= visited &&
        absent >= 0 && unavailable >= 0 && readBytes > 0 && readBytes <= 2 * 1024 * 1024 &&
        o.rows.length + absent + unavailable === examined) ||
      typeof o.unitLimitReached !== 'boolean' ||
      (o.unitLimitReached ? examined !== limit : visited !== buckets) ||
      !floatBitsMatch(o.selfPositionCandidate, o.selfPositionRawBits) ||
      typeof o.cameraStableCandidate !== 'boolean' ||
      !cameraValid(o.opticalCameraCandidate) || !cameraValid(o.opticalCameraAfterCandidate) ||
      o.cameraStableCandidate !== cameraSameCandidate(o.opticalCameraCandidate,
        o.opticalCameraAfterCandidate)) return false;
  try { decimal64(o.selfKey); } catch { return false; }
  try {
    const dotnetStart = decimal64(o.identity.processStartUtcTicks);
    const observedStart = utc100ns(o.startedAtUtc), observedEnd = utc100ns(o.completedAtUtc);
    // DateTime.MaxValue.Ticks, not merely an arbitrary unsigned native key.
    if (observedStart >= observedEnd || dotnetStart > 3155378975999999999n ||
        dotnetStart > 621355968000000000n + observedStart) return false;
  } catch { return false; }
  return true;
}
function nativeRowsValid(observation) {
  const keys = new Map();
  const self = observation.selfPositionCandidate;
  for (const row of observation.rows) {
    let key, address;
    try { key = decimal64(row.unitKey); address = decimal64(row.entityAddressDecimal); }
    catch { throw Error('invalid-native-unit-identity'); }
    if (keys.has(key) ||
        row.unitIdCandidate !== 'u' + key.toString(16).toUpperCase().padStart(16, '0') ||
        address < 0x10000n || address > 0x7fffffffffffn - 0x110n || address % 8n ||
        !floatBitsMatch(row.positionCandidate, row.rawBits)) throw Error('invalid-native-unit-row');
    const distance = Math.hypot(Math.fround(row.positionCandidate.x) - Math.fround(self.x),
      Math.fround(row.positionCandidate.z) - Math.fround(self.z));
    if (typeof row.horizontalDistanceCandidate !== 'number' ||
        !Number.isFinite(row.horizontalDistanceCandidate) ||
        Math.abs(row.horizontalDistanceCandidate - distance) > 1e-6)
      throw Error('invalid-native-unit-distance');
    keys.set(key, row);
  }
  return keys;
}
function luaRows(raw) {
  const lines = raw.toString('utf8').replace(/\r\n/g, '\n').trimEnd().split('\n');
  const self = /^WA006_G2_V1\|BEGIN\|self=(u[0-9a-fA-F]{16})\|/.exec(lines[0]);
  if (!self) throw Error('lua-self-id-missing');
  const rows = [];
  for (const line of lines.slice(1, -1)) {
    const m = /^WA006_G2_V1\|ROW\|id=(u[0-9a-fA-F]{16})\|specifier=[^|]+\|x=(-?[0-9]+\.[0-9]{6})\|y=(-?[0-9]+\.[0-9]{6})\|z=(-?[0-9]+\.[0-9]{6})\|idBinding=matched$/.exec(line);
    if (m) {
      const xyzText = m.slice(2, 5);
      rows.push({id:m[1], key:BigInt('0x' + m[1].slice(1)),
        xyz:xyzText.map(Number), xyzText});
    }
  }
  return {selfKey:BigInt('0x' + self[1].slice(1)), rows};
}
function inRange(begin, end, outerBegin, outerEnd) {
  return outerBegin <= begin && begin <= end && end <= outerEnd;
}

export function preflightG2Sources(luaInput, nativeInput, receipt) {
  const reasons = [];
  const fail = reason => { if (!reasons.includes(reason)) reasons.push(reason); };
  const limitations = ['external-owner-scene-and-UTC-receipt-not-authenticated',
    'nonself-coordinate-tolerance-unqualified', 'serial-Lua-observations-not-simultaneous',
    'full-RR2-camera-geometry-not-independently-revalidated',
    'native-candidate-identity-not-runtime-qualified'];
  let candidateKeyJoins = 0, maxAxisDeltaCandidate = null, luaHash = null, nativeHash = null;
  let luaRaw, nativeRaw, report, rows;
  try {
    luaRaw = bytes(luaInput, 12000);
    nativeRaw = bytes(nativeInput, 4 * 1024 * 1024);
    luaHash = digest(luaRaw);
    nativeHash = digest(nativeRaw);
  } catch { fail('source-unavailable-or-oversize'); }
  if (luaRaw) {
    const result = validatePacket(luaRaw);
    if (!result.packetStructurallyReady) fail('invalid-LuaPad-transcript');
    else {
      try { rows = luaRows(luaRaw); } catch { fail('invalid-LuaPad-rows'); }
    }
  }
  if (nativeRaw) {
    try { report = nativeWithLosslessStart(nativeRaw); }
    catch { fail('invalid-or-lossy-native-JSON'); }
  }
  const observation = report?.observation, identity = observation?.identity;
  if (report && !nativeShapeValid(report)) fail('invalid-native-unit-positions-contract');

  let nativeKeys;
  if (observation?.rows && Array.isArray(observation.rows)) {
    try { nativeKeys = nativeRowsValid(observation); }
    catch { fail('invalid-native-unit-key-or-position'); }
  }

  const proc = receipt?.process, lua = receipt?.lua, window = receipt?.window;
  if (!receipt || receipt.schemaVersion !== 1 || receipt.kind !== 'WA006_G2_REJECTION_ONLY_V1' ||
      receipt.hostName !== 'AMD-DESKTOP' || typeof receipt.ownerLeaseId !== 'string' ||
      !receipt.ownerLeaseId.trim() || !sha(receipt.sceneWitnessSha256) ||
      !proc || !lua || !window) fail('missing-external-receipt-fields');
  if (!sha(lua?.sourceSha256) || lua.sourceSha256.toLowerCase() !== SOURCE_SHA ||
      !sha(lua?.transcriptSha256) || !sha(receipt?.nativeSourceSha256) ||
      lua.transcriptSha256.toLowerCase() !== luaHash ||
      receipt.nativeSourceSha256.toLowerCase() !== nativeHash) fail('source-hash-or-Lua-version-mismatch');
  try {
    if (!Number.isSafeInteger(proc?.processId) || proc.processId <= 0 ||
        decimal64(proc.processStartUtcTicks) !== decimal64(identity?.processStartUtcTicks) ||
        proc.processId !== identity.processId || !sha(proc.executableSha256) ||
        !sha(identity.executableSha256) ||
        proc.executableSha256.toLowerCase() !== identity.executableSha256.toLowerCase())
      fail('process-epoch-or-build-mismatch');
  } catch { fail('process-epoch-or-build-mismatch'); }
  try {
    const start = utc100ns(window.startedAtUtc), end = utc100ns(window.completedAtUtc);
    const ls = utc100ns(lua.startedAtUtc), le = utc100ns(lua.completedAtUtc);
    const ns = utc100ns(observation.startedAtUtc), ne = utc100ns(observation.completedAtUtc);
    // .NET DateTime ticks are exact 100-ns intervals since year 0001; UTC is Unix 100-ns.
    // A Lua execution cannot have begun before its claimed physical RIFT process existed.
    const processStart = decimal64(proc.processStartUtcTicks) - 621355968000000000n;
    if (ls < processStart) fail('lua-before-process-epoch');
    if (!inRange(ls, le, start, end) || !inRange(ns, ne, start, end))
      fail('stale-cross-source-window');
    // Without calibrated skew, distinct serial intervals cannot be labeled coherent.
    // Endpoint contact has zero overlap; require a positive time interval.
    if (le <= ns || ne <= ls) fail('disjoint-cross-source-UTC');
    if (!Array.isArray(observation.rows)) throw Error('missing-rows');
    let previous = ns;
    for (const row of observation.rows) {
      const rs = utc100ns(row.startedAtUtc), re = utc100ns(row.completedAtUtc);
      if (!inRange(rs, re, previous, ne)) throw Error('bad-row-window');
      previous = re;
    }
  } catch { fail('invalid-or-unordered-UTC-bracket'); }

  if (rows && nativeKeys && !reasons.includes('invalid-native-unit-key-or-position')) {
    try {
      if (rows.selfKey !== decimal64(observation.selfKey)) fail('self-native-key-mismatch');
      const luaStart = utc100ns(lua.startedAtUtc), luaEnd = utc100ns(lua.completedAtUtc);
      for (const row of rows.rows) {
        const native = nativeKeys.get(row.key);
        if (!native || row.key === rows.selfKey) {
          fail('missing-independent-nonself-key');
          continue;
        }
        candidateKeyJoins++;
        // Overall observation overlap cannot substitute for each matched native row.
        if (luaEnd <= utc100ns(native.startedAtUtc) ||
            utc100ns(native.completedAtUtc) <= luaStart)
          fail('disjoint-nonself-row-UTC');
        const delta = Math.max(...AXES.map((axis, i) =>
          Math.abs(row.xyz[i] - native.positionCandidate[axis])));
        maxAxisDeltaCandidate = Math.max(maxAxisDeltaCandidate ?? 0, delta);
        // Strict source-format coherence only, not a spatial tolerance or live match.
        // Compare actual Lua text with exact native float32 fixed-decimal text,
        // including the sign of rounded zero; do not use JS toFixed/Number here.
        // A separately calibrated time/skew policy is still needed for live correlation.
        if (AXES.some((axis, i) =>
          row.xyzText[i] !== luaFixed6FromFloat32Bits(native.rawBits[i])))
          fail('uncalibrated-coordinate-mismatch');
      }
      if (candidateKeyJoins < 2) fail('fewer-than-two-cross-source-ID-candidates');
    } catch { fail('invalid-native-self-key'); }
  }
  return {status:reasons.length ? 'rejected' : 'selected-fields-consistent-unqualified',
    sourceFieldsConsistent:reasons.length === 0, candidateKeyJoins, maxAxisDeltaCandidate,
    luaSha256:luaHash, nativeSha256:nativeHash, reasons, limitations,
    nativeCorrelationDone:false, wa006Accepted:false};
}

if (process.argv[1] && resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  if (process.argv.length !== 5) {
    process.stderr.write('Usage: node verify_wa006_g2_cross_source_preflight.mjs <LuaPad-copy.txt> <units-native.json> <independent-receipt.json>\n');
    process.exitCode = 2;
  } else {
    try {
      const result = preflightG2Sources(boundedFile(process.argv[2], 12000),
        boundedFile(process.argv[3], 4 * 1024 * 1024),
        parseExternalReceipt(boundedFile(process.argv[4], 32 * 1024)));
      process.stdout.write(JSON.stringify(result) + '\n');
      if (!result.sourceFieldsConsistent) process.exitCode = 1;
    } catch (error) {
      process.stderr.write(String(error.message || error) + '\n');
      process.exitCode = 2;
    }
  }
}
