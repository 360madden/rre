// Synthetic-only failure controls for the archived exact-build ROOT-001 verifier.
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import path from 'node:path';
import test from 'node:test';
import { fileURLToPath } from 'node:url';
import { verifyRoot001Bytes } from './verify-root001-registry.mjs';

const repoRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const original = readFileSync(path.join(repoRoot, 'artifacts', 'lab2-live-20261107-0922', 'guest-rift_x64.exe'));

test('qualifies only the pinned static dispatch path, never live player identity', () => {
  const result = verifyRoot001Bytes(original);
  assert.equal(result.ok, true);
  assert.equal(result.registrationRecordsVerified, 850);
  assert.equal(result.rootRecordIndex, 575);
  assert.equal(result.sourceWindowsVerified, 34);
  assert.equal(result.opcodeAnchorsVerified, 82);
  assert.equal(result.directCallsVerified, 22);
  assert.equal(result.ripTargetsVerified, 18);
  assert.equal(result.rootInternalTagHex, '0xdd3c');
  assert.equal(result.rootTagNameRegistrationConditional, true);
  assert.equal(result.namedSingletonRva, '0x35199f0');
  assert.equal(result.separateNameBufferRva, '0x35159f8');
  assert.equal(result.staticCallbackArgumentReferenceFlowQualified, true);
  assert.equal(result.staticC2mRootPointerIdentityQualified, true);
  assert.equal(result.staticHandlerDispatchPathQualified, true);
  assert.equal(result.staticDispatchVectorSlotLoopQualified, true);
  assert.equal(result.staticDispatchVectorTripleSwapQualified, true);
  assert.equal(result.staticVectorCriticalSectionGuardQualified, true);
  assert.equal(result.staticC2mPositiveEligibilityWriterQualified, true);
  assert.equal(result.staticC2mRootKeyEqualityGateQualified, true);
  assert.equal(result.staticC2mMethodPointerAvailabilityQualified, true);
  assert.equal(result.c2mKeyMismatchBranchesVerified, 1);
  assert.equal(result.liveExecutionProven, false);
  assert.equal(result.playerIdentityProven, false);
  assert.equal(result.dispatchBranchesVerified, 2);
  assert.equal(result.negativeMutationRejected, true);
});

test('fails closed on a truncated source image', () => {
  assert.throws(() => verifyRoot001Bytes(original.subarray(0, original.length - 1)), /size mismatch/);
});

// Resolve exact file offsets so each negative case mutates the stated source field.
function rawOffsetForRva(rva) {
  const pe = original.readUInt32LE(0x3c);
  const count = original.readUInt16LE(pe + 6);
  const start = pe + 24 + original.readUInt16LE(pe + 20);
  for (let i = 0; i < count; i++) {
    const at = start + i * 40;
    const virtualRva = original.readUInt32LE(at + 12);
    const rawSize = original.readUInt32LE(at + 16);
    if (rva >= virtualRva && rva < virtualRva + rawSize) {
      return original.readUInt32LE(at + 20) + rva - virtualRva;
    }
  }
  throw new Error('No original raw bytes at RVA 0x' + rva.toString(16));
}

for (const [name, rva] of [
  ['ROOT descriptor 575', 0x2f5d618],
  ['dispatch-function table slot', 0x26c5a48],
  ['native handler trampoline', 0x7068c0],
  ['keyed handler-store instruction', 0x81765b],
  ['named singleton ID vtable method', 0x1edda64],
  ['separate formatted-name vtable method', 0x1ede6f0],
  ['C2M callback-state root pointer store', 0x6a3e97],
  ['C2M root eligibility byte guard', 0x6a5e3b],
  ['dispatch vector QWORD slot caller A', 0x7875b6],
  ['dispatch vector QWORD slot caller B', 0x788713],
  ['dispatch vector triple swap', 0x74b922],
  ['C2M positive eligibility byte writer', 0x580a1c],
  ['C2M key equality conditional branch', 0x5f6732],
  ['C2M conditional writer method pointer', 0x26afc00],
]) {
  test('exact-build SHA rejects a mutation at source RVA: ' + name, () => {
    const modified = Buffer.from(original);
    modified[rawOffsetForRva(rva)] ^= 1;
    assert.throws(() => verifyRoot001Bytes(modified), /SHA-256 mismatch/);
  });
}

test('rejects non-Buffer inputs', () => {
  assert.throws(() => verifyRoot001Bytes('not an executable'), /expected a Buffer/);
});
