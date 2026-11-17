#!/usr/bin/env node
// WA-006 evidence matrix verifier: offline, read-only, fail closed.
import { createHash } from 'node:crypto';
import { execFileSync } from 'node:child_process';
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
    // Historical RR2 prose can evolve in its working tree. Recover only the
    // explicitly pinned Git revision, then reconstitute its original Windows
    // checkout bytes before verifying the *unchanged* evidence SHA256.
    let originalBytes;
    if (item.archivedGit) {
      const a = item.archivedGit;
      requireTrue(item.id === 'rr2-physical-workflow'
        && a.repoPath === 'C:/work/riftreader2'
        && a.gitPath === 'docs/workflows/physical-world-screen.md'
        && a.commit === '3c5287aa4c75500728207083dd0c33d8c0e8f536'
        && a.checkoutEol === 'crlf'
        && path.resolve(a.repoPath, a.gitPath).toLowerCase()
          === path.resolve(item.path).toLowerCase(),
      'invalid archived source locator: ' + item.id);
      const blob = execFileSync('git', ['-C', a.repoPath, 'show', a.commit + ':' + a.gitPath],
        {timeout: 5000, maxBuffer: 1000000, windowsHide: true});
      requireTrue(!blob.includes(0x0d), 'archived Git source is not LF-only: ' + item.id);
      originalBytes = Buffer.from(blob.toString('utf8').replace(/\n/g, '\r\n'), 'utf8');
    } else {
      originalBytes = readFileSync(item.path);
    }
    requireTrue(sha(originalBytes) === item.sha256, 'source changed: ' + item.id);
    sourceBytes.set(item.id, originalBytes);
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
  const utc = compare.captureOrder?.observedUtc;
  requireTrue(utc
    && scans[0].startedAtUtc === utc.firstScanStarted
    && scans[0].completedAtUtc === utc.firstScanCompleted
    && scans[1].startedAtUtc === utc.secondScanStarted
    && scans[1].completedAtUtc === utc.secondScanCompleted
    && Date.parse(scans[0].startedAtUtc) < Date.parse(scans[0].completedAtUtc)
    && Date.parse(scans[0].completedAtUtc) < Date.parse(scans[1].startedAtUtc)
    && Date.parse(scans[1].startedAtUtc) < Date.parse(scans[1].completedAtUtc),
    'original Lua scan timestamps are not source-coherent or ordered');
  requireTrue(bracket.scanSnapshots.length === 2 &&
    bracket.scanSnapshots.every((n, i) => n === self.luaFramesPerScan[i]) &&
    compare.frameCounts.every((n, i) => n === self.luaFramesPerScan[i]),
    'Lua frame counts not original-source bound');
  // The original SHA-pinned scan indexes transitively pin their *actual* Lua
  // snapshot files. Decode those 4-KiB captured pages, not just RR2's summary.
  // RR2's separate strict raw replay remains the independent second implementation.
  const replayLua = (scan, sourceId) => {
    const pin = matrix.sources.find(x => x.id === sourceId);
    requireTrue(pin && Array.isArray(scan.candidates), 'missing original Lua scan index');
    const accepted = scan.candidates.filter(x => x.status === 'complete');
    requireTrue(accepted.length === scan.publishedSnapshots && accepted.length >= 2,
      'original Lua snapshot count mismatches index');
    const frames = [];
    for (const item of accepted) {
      requireTrue(/^capture-\d{2}\.snapshot\.json$/.test(item.snapshotFile),
        'unsafe Lua snapshot filename');
      const raw = readFileSync(path.join(path.dirname(pin.path), item.snapshotFile));
      requireTrue(sha(raw) === String(item.snapshotSha256).toLowerCase(),
        'original Lua snapshot SHA mismatch');
      const snapshotText = raw.toString('utf8');
      const snapshot = JSON.parse(snapshotText);
      const ticks = snapshotText.match(/"processStartUtcTicks"\s*:\s*(\d+)/);
      requireTrue(snapshot.evidenceKind === 'native-memory-snapshot/1'
        && snapshot.status === 'complete'
        && snapshot.identity.processId === self.pid
        && ciEqual(snapshot.identity.executableSha256, self.executableSha256)
        && ticks && ticks[1] === self.processStartUtcTicks
        && Array.isArray(snapshot.chunks) && snapshot.chunks.length > 0,
        'Lua snapshot provenance mismatch');
      let firstAddress = null;
      let expectedAddress = null;
      const pages = [];
      for (const page of snapshot.chunks) {
        const address = BigInt(page.address);
        requireTrue(page.status === 'success' && page.requestedByteLength === 4096
          && page.bytesRead === 4096
          && (expectedAddress === null || address === expectedAddress),
          'Lua page missing or noncontiguous');
        const data = Buffer.from(page.bytesBase64, 'base64');
        requireTrue(data.length === 4096
          && data.toString('base64') === page.bytesBase64
          && sha(data) === String(page.bytesSha256).toLowerCase(),
          'Lua captured page corrupt');
        if (firstAddress === null) firstAddress = address;
        expectedAddress = address + 4096n;
        pages.push(data);
      }
      const data = Buffer.concat(pages);
      const relative = BigInt(item.markerAddress) - firstAddress;
      requireTrue(relative >= 0n && relative < BigInt(data.length),
        'Lua marker outside captured pages');
      const offset = Number(relative);
      const prefix = Buffer.from('RR2A1|');
      const suffix = Buffer.from('|ENDRR2A1');
      const end = data.indexOf(suffix, offset + prefix.length);
      requireTrue(data.subarray(offset, offset + prefix.length).equals(prefix)
        && end >= 0 && end + suffix.length - offset <= 4096,
        'Lua frame marker or terminator missing');
      const observed = JSON.parse(data.subarray(offset + prefix.length, end).toString('utf8'));
      requireTrue(observed.schemaVersion === 1 && observed.addonVersion === '0.1.0'
        && observed.player?.status === 'ok'
        && observed.player.value === self.independentLuaPlayerId
        && Number.isSafeInteger(observed.sequence) && observed.sequence > 0
        && Number.isSafeInteger(observed.epoch) && observed.epoch > 0
        && observed.clock?.status === 'ok'
        && Number.isFinite(observed.clock.value)
        && ['coordX', 'coordY', 'coordZ'].every(axis =>
          observed.fields?.[axis]?.status === 'ok'
          && Number.isFinite(observed.fields[axis].value)),
        'actual original Lua player frame does not match matrix self identity');
      frames.push({sequence: observed.sequence, epoch: observed.epoch,
        clock: observed.clock.value});
    }
    frames.sort((a, b) => a.sequence - b.sequence);
    requireTrue(frames.every((f, i) => i === 0 ||
      (f.sequence > frames[i - 1].sequence && f.clock > frames[i - 1].clock)),
      'Lua original frame sequence or time did not advance');
    return frames;
  };
  const originalLuaFrames = scans.map((scan, i) => replayLua(scan,
    i === 0 ? 'rr2-self-scan-index-first' : 'rr2-self-scan-index-second'));
  requireTrue(originalLuaFrames[0].at(-1).sequence < originalLuaFrames[1][0].sequence
    && originalLuaFrames[0].at(-1).clock < originalLuaFrames[1][0].clock
    && originalLuaFrames[0][0].epoch === compare.luaEpochCandidate
    && originalLuaFrames[0][0].epoch === originalLuaFrames[1][0].epoch
    && originalLuaFrames.every((frames, i) =>
      frames.length === self.luaFramesPerScan[i]
      && frames.every(f => f.epoch === originalLuaFrames[0][0].epoch)
      && frames[0].sequence === compare.sequenceWindows[i][0]
      && frames.at(-1).sequence === compare.sequenceWindows[i][1]),
    'Lua original scan frames disagree with source comparison');
  const hex = BigInt(self.nativeSelfKeyDecimal).toString(16).toUpperCase().padStart(16, '0');
  requireTrue(hex === self.nativeSelfKeyHex && 'u' + hex === self.independentLuaPlayerId,
    'native self key is not equal to separately recorded Lua player ID');
  requireTrue(self.status === 'candidate-only-unbound' && self.sameEpochSelfCorrelation === true
    && self.sameEpochNonselfCorrelation === false && self.nonceAuthenticated === false
    && self.originalRawLuaSnapshotsTransitivelyHashVerified === 7
    && self.changedPositionQualified === false
    && self.cannotCombineWithLaterPid51524Scene === true, 'self proof overpromoted');
  requireTrue(other.displayedNonselfCandidates === 18, 'nonself candidate count changed');
  const query = matrix.currentBuildStaticQuery;
  requireTrue(query.exitCode === 0 && query.sourceWindows === 9
    && query.decodedInstructions === 1036 && query.opcodeAnchors === 19
    && query.directCallEdges === 5 && query.inMemoryNegativeControls === 2,
    'current-build static verification receipt changed');
  requireTrue(query.candidateSelectorVtableRva === '0x278C980'
    && query.candidateSelectorRva === '0xA2514'
    && query.candidateBooleanReaderRva === '0xA24F4'
    && query.candidateScratchFieldOffset === '0x50'
    && query.candidateObjectVirtualResultProducerQualified === false,
    'candidate selector/result ownership promoted or corrupted');
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
    originalLuaSnapshotsReplayed: originalLuaFrames.reduce((n, f) => n + f.length, 0),
    originalLuaPassFrameCounts: originalLuaFrames.map(f => f.length),
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
  // Three separate synthetic failures must not bypass the immutable Git
  // document anchor, even when all historical Lua/native artifacts are valid.
  const source = (m, id) => m.sources.find(item => item.id === id);
  const archiveCases = [
    ['wrong-commit', m => { source(m, 'rr2-physical-workflow').archivedGit.commit = '0'.repeat(40); }],
    ['wrong-EOL', m => { source(m, 'rr2-physical-workflow').archivedGit.checkoutEol = 'lf'; }],
    ['unapproved-archive', m => {
      source(m, 'rre-contract').archivedGit =
        structuredClone(source(m, 'rr2-physical-workflow').archivedGit);
    }],
  ];
  for (const [name, mutate] of archiveCases) {
    const mutated = structuredClone(original);
    mutate(mutated);
    let refused = false;
    try { verify(mutated); } catch { refused = true; }
    requireTrue(refused, 'archive negative control failed: ' + name);
  }
  receipt.inMemoryArchivedSourceNegativeControls = archiveCases.map(([name]) => name);
  process.stdout.write(JSON.stringify(receipt, null, 2) + '\n');
} catch (error) {
  process.stderr.write(String(error) + '\n');
  process.exitCode = 1;
}
