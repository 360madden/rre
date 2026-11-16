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
  requireTrue(Array.isArray(matrix.sources) && matrix.sources.length >= 22,
    'expected at least 22 original source hashes');
  const seen = new Set();
  for (const item of matrix.sources) {
    requireTrue(item.id && !seen.has(item.id), 'unique source ID');
    seen.add(item.id);
    requireTrue(/^C:\/work\//i.test(item.path), 'source path outside C:/work');
    requireTrue(/^[a-f0-9]{64}$/.test(item.sha256), 'malformed SHA for ' + item.id);
    const onDisk = readFileSync(item.path);
    requireTrue(sha(onDisk) === item.sha256, 'source changed: ' + item.id);
  }
  const self = matrix.recordedSelfCorrelation;
  const other = matrix.recordedObservation;
  requireTrue(self.host === 'AMD-DESKTOP' && other.host === self.host,
    'source-host mismatch');
  requireTrue(self.pid !== other.pid && self.processStartUtcTicks !== other.processStartUtcTicks,
    'self and nonself candidate captures must remain distinct epochs');
  requireTrue(self.executableSha256 === other.executableSha256, 'build mismatch');
  const hex = BigInt(self.nativeSelfKeyDecimal).toString(16).toUpperCase().padStart(16, '0');
  requireTrue(hex === self.nativeSelfKeyHex && 'u' + hex === self.independentLuaPlayerId,
    'native self key is not equal to separately recorded Lua player ID');
  requireTrue(self.status === 'candidate-only-unbound' && self.sameEpochSelfCorrelation === true
    && self.sameEpochNonselfCorrelation === false && self.nonceAuthenticated === false
    && self.changedPositionQualified === false
    && self.cannotCombineWithLaterPid51524Scene === true, 'self proof overpromoted');
  requireTrue(other.displayedNonselfCandidates === 18, 'nonself candidate count changed');
  const query = matrix.currentBuildStaticQuery;
  requireTrue(query.exitCode === 0 && query.sourceWindows === 4
    && query.decodedInstructions === 360 && query.opcodeAnchors === 15
    && query.directCallEdges === 4 && query.inMemoryNegativeControls === 2,
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
  process.stdout.write(JSON.stringify(receipt, null, 2) + '\n');
} catch (error) {
  process.stderr.write(String(error) + '\n');
  process.exitCode = 1;
}
