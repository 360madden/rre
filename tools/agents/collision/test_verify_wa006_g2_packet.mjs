// Bounded offline packet-transcript validation; no game, file writes or dependencies.
import assert from 'node:assert/strict';
import {validatePacket} from './verify_wa006_g2_packet.mjs';

const marker = 'WA006_G2_V1';
const self = 'u035400012FA2D207';
const a = 'u035400012FA2D208';
const b = 'u035400012FA2D209';
const begin = marker + '|BEGIN|self=' + self + '|frame=12.500000|real=13.500000';
const row1 = marker + '|ROW|id=' + a + '|specifier=target.one|x=100.125000|y=200.250000|z=300.500000|idBinding=matched';
const row2 = marker + '|ROW|id=' + b + '|specifier=target.two|x=111.000000|y=222.000000|z=333.000000|idBinding=matched';
const end = marker + '|END|examined=3|details=2|validXYZ=2|errors=0|capped=false|frameEnd=13.500000|realEnd=14.500000|status=exploratory-only';
const original = [begin, row1, row2, end].join('\n') + '\n';
let count = 0;
function test(name, text, ready, reason) {
  const result = validatePacket(text);
  assert.equal(result.packetStructurallyReady, ready, name + ' outcome: ' + result.reasons.join(','));
  assert.equal(result.wa006Accepted, false, name + ' may never qualify native/WA-006');
  assert.equal(result.nativeCorrelationDone, false, name + ' may never claim native');
  if (reason) assert.ok(result.reasons.includes(reason), name + ' expected ' + reason);
  count++;
}
test('complete-two-matched-IDs', original, true);
test('missing-BEGIN', original.replace(begin + '\n', ''), false, 'missing-or-malformed-BEGIN');
test('missing-END', original.replace(end + '\n', ''), false, 'missing-or-malformed-END');
test('duplicate-BEGIN', original.replace(begin + '\n', begin + '\n' + begin + '\n'), false,
  'malformed-or-duplicate-record');
test('duplicate-unit-ID', original.replace('id=' + b, 'id=' + a), false, 'duplicate-unit-ID');
test('self-row-not-nonself', original.replace('id=' + b, 'id=' + self), false, 'self-listed-as-nonself');
test('detail-count-mismatch', original.replace('details=2', 'details=3'), false, 'row-detail-counter-mismatch');
test('partial-capped', original.replace('capped=false', 'capped=true'), false, 'partial-enumeration');
test('regressing-clock', original.replace('frameEnd=13.500000', 'frameEnd=11.500000'), false, 'regressing-clock');
test('missing-detail-ID', original.replace('idBinding=matched', 'idBinding=missing'), false,
  'validXYZ-counter-mismatch');
test('unknown-coordinate', original.replace('x=100.125000', 'x=unknown'), false,
  'validXYZ-counter-mismatch');
test('embedded-source-error', original.replace(row2 + '\n',
  row2 + '\n' + marker + '|ERROR|detail-id-mismatch|id=' + b + '\n'), false, 'ERROR-record');
test('LuaPad-tail-limit', original + 'X'.repeat(12000), false, 'size-at-or-over-LuaPad-tail-limit');
test('non-UTF8-clipboard', Buffer.from([0xff, 0xfe, 0x00]), false, 'non-UTF8-copy');
test('UTF8-BOM-prefix-not-from-Lua',
  Buffer.concat([Buffer.from([0xef, 0xbb, 0xbf]), Buffer.from(original)]),
  false, 'UTF8-BOM-prefix');
test('unrelated-prefix', 'output:\n' + original, false, 'missing-or-malformed-BEGIN');
test('case-folded-duplicate-unit', original.replace('id=' + b, 'id=' + a.toLowerCase()), false,
  'duplicate-unit-ID');
test('case-folded-self-row', original.replace('id=' + b, 'id=' + self.toLowerCase()), false,
  'self-listed-as-nonself');
test('duplicate-END', original + end + '\n', false, 'malformed-or-duplicate-record');
test('malformed-ROW', original.replace('specifier=target.one', 'specifier=bad|extra'), false,
  'malformed-or-duplicate-record');
test('invalid-coordinate', original.replace('x=100.125000', 'x=NaN'), false,
  'invalid-coordinate-token');
test('changed-end-status', original.replace('status=exploratory-only', 'status=accepted'), false,
  'missing-or-malformed-END');
test('unknown-end-clock', original.replace('frameEnd=13.500000', 'frameEnd=unknown'), false,
  'missing-or-malformed-END');
test('detail-exceeds-examined', original.replace('examined=3', 'examined=1'), false,
  'examined-less-than-details');
test('explicit-error-counter', original.replace('errors=0', 'errors=1'), false,
  'row-detail-counter-mismatch');
test('negative-infinite-BEGIN-frame', original.replace('frame=12.500000',
  'frame=-' + '9'.repeat(400) + '.000000'), false, 'invalid-begin-clock');
test('negative-infinite-BEGIN-real', original.replace('real=13.500000',
  'real=-' + '9'.repeat(400) + '.000000'), false, 'invalid-begin-clock');
test('specifier-78-UTF8-byte-boundary', original.replace('target.one', '界'.repeat(26)), true);
test('specifier-81-UTF8-byte-overflow', original.replace('target.one', '界'.repeat(27)),
  false, 'oversize-specifier');
const thirdRow = row2.replace('id=' + b, 'id=u035400012FA2D20A')
  .replace('specifier=target.two', 'specifier=target.three')
  .replace('x=111.000000', 'x=unknown');
const threeRows = [begin, row1, row2, thirdRow,
  end.replace('examined=3', 'examined=4').replace('details=2', 'details=3')]
  .join('\n') + '\n';
test('third-unknown-coordinate-valid', threeRows, true);
test('third-nonfinite-coordinate-rejected', threeRows.replace('x=unknown',
  'x=' + '9'.repeat(400) + '.000000'), false, 'invalid-coordinate-token');
test('noncanonical-leading-zero-examined', original.replace('examined=3', 'examined=03'),
  false, 'missing-or-malformed-END');
test('noncanonical-leading-zero-details', original.replace('details=2', 'details=02'),
  false, 'missing-or-malformed-END');
test('noncanonical-leading-zero-validXYZ', original.replace('validXYZ=2', 'validXYZ=02'),
  false, 'missing-or-malformed-END');
test('noncanonical-leading-zero-errors', original.replace('errors=0', 'errors=00'),
  false, 'missing-or-malformed-END');
test('noncanonical-leading-zero-BEGIN-clock',
  original.replace('frame=12.500000', 'frame=012.500000'),
  false, 'missing-or-malformed-BEGIN');
test('noncanonical-leading-zero-END-clock',
  original.replace('frameEnd=13.500000', 'frameEnd=013.500000'),
  false, 'missing-or-malformed-END');
test('noncanonical-leading-zero-ROW-coordinate',
  original.replace('x=100.125000', 'x=0100.125000'),
  false, 'invalid-coordinate-token');
test('canonical-zero-ROW-coordinate', original.replace('x=100.125000', 'x=0.000000'),
  true);
test('canonical-negative-rounded-zero', original.replace('y=200.250000', 'y=-0.000000'),
  true);
process.stdout.write(JSON.stringify({task:'WA-006',tests:count,passed:count,
  scope:'offline-LuaPad-transcript-structure-only',nativeCorrelationDone:false,wa006Accepted:false}) + '\n');

