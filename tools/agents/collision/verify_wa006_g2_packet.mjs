// WA-006 G2 LuaPad packet preflight. This verifies transcript structure only.
// A valid packet is NOT independent RIFT/native correlation or WA-006 acceptance.
import {createHash} from 'node:crypto';
import {readFileSync} from 'node:fs';
import {resolve} from 'node:path';
import {fileURLToPath} from 'node:url';

const MARK = 'WA006_G2_V1';
const UNIT_ID = 'u[0-9a-fA-F]{16}';
const NUM = '-?(?:0|[1-9][0-9]*)\\.[0-9]{6}';
const startPattern = new RegExp('^' + MARK + '\\|BEGIN\\|self=(' + UNIT_ID +
  ')\\|frame=(' + NUM + ')\\|real=(' + NUM + ')$');
const endPattern = new RegExp('^' + MARK +
  '\\|END\\|examined=((?:0|[1-9][0-9]*))\\|details=((?:0|[1-9][0-9]*))\\|validXYZ=((?:0|[1-9][0-9]*))' +
  '\\|errors=((?:0|[1-9][0-9]*))\\|capped=(true|false)' +
  '\\|frameEnd=(' + NUM + ')\\|realEnd=(' + NUM + ')' +
  '\\|status=exploratory-only$');
const rowPattern = new RegExp('^' + MARK + '\\|ROW\\|id=(' + UNIT_ID +
  ')\\|specifier=([^|\\r\\n]{1,80})\\|x=([^|]+)\\|y=([^|]+)' +
  '\\|z=([^|]+)\\|idBinding=(matched|missing)$');
const numericPattern = new RegExp('^' + NUM + '$');

export function validatePacket(input) {
  const raw = Buffer.isBuffer(input) ? input : Buffer.from(input);
  const reasons = [];
  const fail = msg => { if (!reasons.includes(msg)) reasons.push(msg); };
  // LuaPad's canonical report starts with WA006_G2_V1, never a UTF-8 BOM.
  // TextDecoder would otherwise silently strip EF BB BF and falsely qualify the copy.
  if (raw[0] === 0xef && raw[1] === 0xbb && raw[2] === 0xbf)
    fail('UTF8-BOM-prefix');
  const sha256 = createHash('sha256').update(raw).digest('hex');
  if (raw.length >= 12000) fail('size-at-or-over-LuaPad-tail-limit');
  let transcript;
  try {
    transcript = new TextDecoder('utf-8', {fatal:true}).decode(raw);
  } catch {
    transcript = '';
    fail('non-UTF8-copy');
  }
  if (transcript.includes('\0')) fail('embedded-NUL');
  const normalized = transcript.replace(/\r\n/g, '\n').replace(/\n$/, '');
  const lines = normalized.split('\n');
  if (lines.length < 2 || lines.some(x => !x)) fail('missing-or-empty-record');
  const begin = startPattern.exec(lines[0] || '');
  const end = endPattern.exec(lines[lines.length - 1] || '');
  if (!begin) fail('missing-or-malformed-BEGIN');
  if (!end) fail('missing-or-malformed-END');
  const self = begin?.[1] || null;
  const seen = new Set();
  let qualified = 0;
  let rows = 0;
  for (const line of lines.slice(1, -1)) {
    if (line.startsWith(MARK + '|ERROR|')) {
      fail('ERROR-record');
      continue;
    }
    const m = rowPattern.exec(line);
    if (!m) { fail('malformed-or-duplicate-record'); continue; }
    const [ , id, spec, x, y, z, binding ] = m;
    if (/[\x00-\x1f\x7f]/.test(spec)) fail('invalid-specifier');
    if (Buffer.byteLength(spec, 'utf8') > 80) fail('oversize-specifier');
    // Hexadecimal unit IDs identify the same key regardless of letter case.
    const canonicalId = id.toLowerCase();
    if (self && canonicalId === self.toLowerCase()) fail('self-listed-as-nonself');
    if (seen.has(canonicalId)) fail('duplicate-unit-ID');
    seen.add(canonicalId);
    rows++;
    const xyz = [x, y, z];
    const completeXYZ = xyz.every(v => numericPattern.test(v) && Number.isFinite(Number(v)));
    if (xyz.some(v => v !== 'unknown' &&
        (!numericPattern.test(v) || !Number.isFinite(Number(v)))))
      fail('invalid-coordinate-token');
    if (binding === 'matched' && completeXYZ) qualified++;
  }
  if (rows > 8) fail('row-cap-exceeded');
  let counters = null;
  if (end) {
    const [examined, details, validXYZ, errors] = end.slice(1, 5).map(Number);
    counters = {examined, details, validXYZ, errors, capped:end[5] === 'true'};
    if (examined > 128 || details > 8) fail('source-cap-exceeded');
    if (details !== rows + errors) fail('row-detail-counter-mismatch');
    if (examined < details) fail('examined-less-than-details');
    if (validXYZ !== qualified) fail('validXYZ-counter-mismatch');
    if (errors !== 0) fail('source-errors');
    if (counters.capped) fail('partial-enumeration');
    if (!Number.isFinite(Number(end[6])) || !Number.isFinite(Number(end[7])))
      fail('invalid-end-clock');
  }
  if (begin && (!Number.isFinite(Number(begin[2])) ||
                !Number.isFinite(Number(begin[3]))))
    fail('invalid-begin-clock');
  if (begin && end) {
    if (Number(end[6]) < Number(begin[2]) || Number(end[7]) < Number(begin[3]))
      fail('regressing-clock');
  }
  if (qualified < 2) fail('fewer-than-two-ID-bound-XYZ');
  return {packetStructurallyReady:reasons.length === 0, nativeCorrelationDone:false,
    wa006Accepted:false, bytes:raw.length, sha256, rows, qualified, counters, reasons};
}

if (process.argv[1] && resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  if (process.argv.length !== 3) {
    process.stderr.write('Usage: node tools/agents/collision/verify_wa006_g2_packet.mjs <copied-report.txt>\n');
    process.exitCode = 2;
  } else {
    try {
      const result = validatePacket(readFileSync(process.argv[2]));
      process.stdout.write(JSON.stringify(result) + '\n');
      if (!result.packetStructurallyReady) process.exitCode = 1;
    } catch (error) {
      process.stderr.write(String(error.message || error) + '\n');
      process.exitCode = 2;
    }
  }
}

