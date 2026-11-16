#!/usr/bin/env node
// WA-006 evidence matrix verifier: offline, read-only, fail closed.
import { createHash } from 'node:crypto';
import { readFileSync } from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..', '..', '..');
const matrixPath = path.join(root, 'docs', 'RRE-WA006-EVIDENCE-MATRIX-2026-11-16.json');
const sha = (value) => createHash('sha256').update(value).digest('hex');
const requireTrue = (value, msg) => { if (!value) throw new Error('WA-006 source gate: ' + msg); };

function verify(matrix) {
  requireTrue(matrix.taskId === 'WA-006' && matrix.taskStatus === 'blocked'
    && matrix.qualifiedRealScene === false, 'do not promote scene acceptance');
  requireTrue(Array.isArray(matrix.sources) && matrix.sources.length >= 24,
    'expected at least 24 original source hashes');
  const seen = new Set();
  const sourceBytes = new Map();
  for (const item of matrix.sources) {
    requireTrue(item.id && !seen.has(item.id), 'unique source ID');
    seen.add(item.id);
    requireTrue(/^C:\/work\//i.test(item.path), 'source path outside C:/work');
    requireTrue(/^[a-f0-9]{64}$/.test(item.sha256), 'malformed SHA for ' + item.id);
    const onDisk = readFileSync(item.path);
    requireTrue(sha(onDisk) === item.sha256, 'source changed: ' + item.id);
    sourceBytes.set(item.id, onDisk);
  }
  const self = matrix.recordedSelfCorrelation;
  const other = matrix.recordedObservation;
  requireTrue(self.host === 'AMD-DESKTOP' && other.host === self.host,
    'source-host mismatch');
  requireTrue(self.pid !== other.pid && self.processStartUtcTicks !== other.processStartUtcTicks,
    'self and nonself candidate captures must remain distinct epochs');
  requireTrue(self.executableSha256 === other.executableSha256, 'build mismatch');
  // Bind the self crosswalk to independently HASHED ORIGINAL receipts, not
  // only three mutually consistent values repeated inside this matrix.
  const source = (id) => {
    requireTrue(sourceBytes.has(id), 'missing pinned source ' + id);
    return JSON.parse(sourceBytes.get(id).toString('utf8'));
  };
  const bracket = source('rr2-self-temporal-bracket');
  const nativeBefore = source('rr2-self-native-before');
  const nativeRawBytes = sourceBytes.get('rr2-self-native-raw').toString('utf8');
  const nativeRaw = JSON.parse(nativeRawBytes);
  const nativeAfter = source('rr2-self-native-after');
  const scanFirst = source('rr2-self-scan-index-first');
  const scanSecond = source('rr2-self-scan-index-second');
  const originalSelfKey = nativeBefore.selfKeyCandidate;
  const ciEqual = (a, b) => String(a).toLowerCase() === String(b).toLowerCase();
  requireTrue(bracket.status === 'candidate-only' && bracket.ownerHost === self.host
    && bracket.target.hostName === self.host && bracket.target.processId === self.pid
    && bracket.target.processStartUtcTicks === self.processStartUtcTicks
    && bracket.target.hwnd === self.hwnd
    && ciEqual(bracket.target.executableSha256, self.executableSha256),
    'bracket source epoch differs from matrix');
  requireTrue(ciEqual(bracket.nativeBracketSha256.before,
                sha(sourceBytes.get('rr2-self-native-before')))
    && ciEqual(bracket.nativeBracketSha256.after,
                sha(sourceBytes.get('rr2-self-native-after'))),
    'bracket source hashes do not refer to originals');
  for (const native of [nativeBefore, nativeAfter]) {
    requireTrue(native.status === 'candidate-only'
      && native.identity.host === self.host
      && native.identity.processId === self.pid
      && native.identity.processStartUtcTicks === self.processStartUtcTicks
      && ciEqual(native.identity.executableSha256, self.executableSha256)
      && native.selfKeyCandidate === originalSelfKey
      && native.sampleCount === 3, 'native original bracket mismatch');
  }
  requireTrue(nativeBefore.sourceSha256.position.toLowerCase() ===
    sha(sourceBytes.get('rr2-self-native-raw')), 'raw native source hash mismatch');
  requireTrue(nativeRaw.identity.processId === self.pid
    && ciEqual(nativeRaw.sourceBuildSha256, self.executableSha256)
    && nativeRaw.completedSamples === 3
    && nativeRaw.observations.length === 3
    && nativeRaw.observations.every(x => x.unitKey === originalSelfKey),
    'raw original native unit-key observations disagree');
  // C# serialized ticks as an unsafe JS integer: read its original decimal
  // token without parsing as Number, preserving the exact 64-bit epoch.
  const rawTicks = nativeRawBytes.match(/"processStartUtcTicks"\s*:\s*(\d+)/);
  requireTrue(rawTicks && rawTicks[1] === self.processStartUtcTicks,
    'raw original process start ticks differ');
  requireTrue(self.nativeSelfKeyDecimal === originalSelfKey,
    'matrix self value does not match original native observations');
  const compare = bracket.comparison;
  requireTrue(compare.status === 'candidate-only' &&
    compare.luaProtocol === 'RR2A1-unbound' &&
    compare.identity.host === self.host &&
    compare.identity.processId === self.pid &&
    compare.identity.processStartUtcTicks === self.processStartUtcTicks &&
    ciEqual(compare.identity.executableSha256, self.executableSha256) &&
    compare.luaPlayerIdCandidate === self.independentLuaPlayerId,
    'matrix Lua player ID does not match original RR2A1 comparison');
  requireTrue(compare.captureOrder.status === 'source-verified-order' &&
    compare.coordinateAgreementScreen.withinTolerance === true,
    'original cross-source comparison order/screen not qualified');
  const gaps = compare.maxAbsLuaNativeCoordinateDifferenceCandidate;
  for (const axis of ['x', 'y', 'z']) {
    requireTrue(Number.isFinite(gaps[axis]) && gaps[axis] <= 0.05 &&
      Math.abs(gaps[axis] - self.maxAbsoluteNativeLuaAxisDifference[axis]) < 0.000001,
      'matrix coordinate discrepancy is not source bound: ' + axis);
  }
  const scans = [scanFirst, scanSecond];
  for (let i = 0; i < scans.length; i++) {
    const scan = scans[i];
    requireTrue(scan.status === 'partial' && scan.reason === 'byte-budget-exceeded'
      && scan.copyLimited === false
      && scan.publishedSnapshots === self.luaFramesPerScan[i]
      && scan.request.target.processId === self.pid
      && ciEqual(scan.request.target.executableSha256, self.executableSha256),
      'original partial scan receipt mismatch');
    const indexId = i === 0 ? 'rr2-self-scan-index-first' : 'rr2-self-scan-index-second';
    const expected = i === 0 ? bracket.scanIndexSha256.first : bracket.scanIndexSha256.second;
    requireTrue(ciEqual(expected, sha(sourceBytes.get(indexId))),
      'bracket scan-index SHA mismatch');
  }
  requireTrue(bracket.scanSnapshots.length === 2 &&
    bracket.scanSnapshots.every((n, i) => n === self.luaFramesPerScan[i]) &&
    compare.frameCounts.every((n, i) => n === self.luaFramesPerScan[i]),
    'Lua frame counts not original-source bound');
  const hex = BigInt(self.nativeSelfKeyDecimal).toString(16).toUpperCase().padStart(16, '0');
  requireTrue(hex === self.nativeSelfKeyHex && 'u' + hex === self.independentLuaPlayerId,
    'native self key is not equal to separately recorded Lua player ID');
  requireTrue(self.status === 'candidate-only-unbound' && self.sameEpochSelfCorrelation === true
    && self.sameEpochNonselfCorrelation === false && self.nonceAuthenticated === false
    && self.changedPositionQualified === false
    && self.cannotCombineWithLaterPid51524Scene === true, 'self proof overpromoted');
  requireTrue(other.displayedNonselfCandidates === 18, 'nonself candidate count changed');
  const query = matrix.currentBuildStaticQuery;
  requireTrue(query.exitCode === 0 && query.sourceWindows === 7
    && query.decodedInstructions === 911 && query.opcodeAnchors === 15
    && query.directCallEdges === 5 && query.inMemoryNegativeControls === 2,
    'current-build static verification receipt changed');
  requireTrue(query.successWithoutOwnerWrite === true
    && query.actualRaycastHitMissVerified === false
    && query.physicalShapeOrOwnerVerified === false
    && query.logicalGameplayOwnerVerified === false, 'collision owner overpromoted');
  requireTrue(matrix.acceptanceGates.length === 5
    && matrix.acceptanceGates.every(g => g.status !== 'accepted'), 'scene gates overpromoted');
  for (const gate of matrix.acceptanceGates) {
    for (const id of gate.evidenceIds ?? []) requireTrue(seen.has(id), 'unresolved source ID ' + id);
  }
  return { status: 'passed', task: 'WA-006', originalHashesVerified: seen.size,
    selfNativeLuaIdMatch: true, selfAndNonselfEpochsSeparate: true,
    staticQueryOnly: true, qualifiedRealScene: false,
    gates: matrix.acceptanceGates.map(g => ({id: g.id, status: g.status})) };
}

try {
  const original = JSON.parse(readFileSync(matrixPath, 'utf8'));
  const receipt = verify(original);
  // Negative decision control: in-memory promotion is rejected, never saved.
  const rejected = structuredClone(original);
  rejected.currentBuildStaticQuery.logicalGameplayOwnerVerified = true;
  let failedClosed = false;
  try { verify(rejected); } catch { failedClosed = true; }
  requireTrue(failedClosed, 'ownership-promotion negative control failed');
  receipt.inMemoryPromotionNegativeControl = 'passed';
  // QA reproduced a real false positive in the first version: change all
  // three self ID fields together while keeping every source hash intact.
  const wrongSelf = structuredClone(original);
  wrongSelf.recordedSelfCorrelation.nativeSelfKeyDecimal = '1';
  wrongSelf.recordedSelfCorrelation.nativeSelfKeyHex = '0000000000000001';
  wrongSelf.recordedSelfCorrelation.independentLuaPlayerId = 'u0000000000000001';
  let rejectedFalseSelf = false;
  try { verify(wrongSelf); } catch { rejectedFalseSelf = true; }
  requireTrue(rejectedFalseSelf, 'original-source-binding negative control failed');
  receipt.inMemoryCoordinatedSelfIdCorruptionNegativeControl = 'passed';
  process.stdout.write(JSON.stringify(receipt, null, 2) + '\n');
} catch (error) {
  process.stderr.write(String(error) + '\n');
  process.exitCode = 1;
}
