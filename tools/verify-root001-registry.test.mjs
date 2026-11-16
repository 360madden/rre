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
  assert.equal(result.sourceWindowsVerified, 111);
  assert.equal(result.opcodeAnchorsVerified, 333);
  assert.equal(result.directCallsVerified, 75);
  assert.equal(result.directJumpsVerified, 3);
  assert.equal(result.ripTargetsVerified, 42);
  assert.equal(result.vectorUpstreamDirectCallersVerified, 9);
  assert.equal(result.c2mConsecutiveCodePointersVerified, 40);
  assert.equal(result.vectorAppendPathsVerified, 2);
  assert.equal(result.appendOwnerVirtualMethodsVerified, 2);
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
  assert.equal(result.staticC2mInteriorVptrAssignmentsQualified, true);
  assert.equal(result.staticC2mFirstKeyReferencePairUpdateQualified, true);
  assert.equal(result.staticC2mTransientReferenceCleanupQualified, true);
  assert.equal(result.staticVectorProcessorCallersQualified, true);
  assert.equal(result.c2mKeyMismatchBranchesVerified, 1);
  assert.equal(result.c2mFirstKeyEqualityBranchesVerified, 1);
  assert.equal(result.c2mVtableDeleteBranchesVerified, 1);
  assert.equal(result.objectLocalVectorElementWritersProven, true);
  assert.equal(result.staticAppendOwnerVptrConstructionQualified, true);
  assert.equal(result.staticAppendOwnerVectorLifecycleQualified, true);
  assert.equal(result.staticInitializerOwnerField6a8StoreQualified, true);
  assert.equal(result.staticAppendOwnerConditionalPublicationQualified, true);
  assert.equal(result.staticPublishedOwnerRefcountRetainSourcePathQualified, true);
  assert.equal(result.staticThreadEntrypointForwardsUnprovenRdiReceiverQualified, true);
  assert.equal(result.staticSpawnerRdiPreservedToCrtR9Qualified, true);
  assert.equal(result.staticThreadCreatorCrtImportNameQualified, true);
  assert.equal(result.staticCrtThreadHandleStoredAndStatusByteQualified, true);
  assert.equal(result.staticThreadReceiverViaHost6a8SlotQualified, true);
  assert.equal(result.staticProcessorOwnerField6a8ReadQualified, true);
  assert.equal(result.staticProducerProcessorFieldLayoutBridgeQualified, true);
  assert.equal(result.staticInitializerSameReceiverCallbackRegistrationQualified, true);
  assert.equal(result.staticRegisteredProcessorAdapterVptrQualified, true);
  assert.equal(result.staticSecondaryProcessorAdapterSameHostRegistrationQualified, true);
  assert.equal(result.staticHostRegistryLookupToStagedCallbackQualified, true);
  assert.equal(result.staticHostSelectedCallbackSameReceiverRdxDispatchQualified, true);
  assert.equal(result.staticAdapterAllocationConditionalQualified, true);
  assert.equal(result.staticCallbackSecondConsumerQualified, true);
  assert.equal(result.staticDistinctRegisteredEventKeysQualified, true);
  assert.equal(result.staticLoginFailedKeySetterPathQualified, true);
  assert.equal(result.staticInGameLiteralReachesSetterProven, true);
  assert.equal(result.staticInGameSetterUsesPublishedHostGlobalQualified, true);
  assert.equal(result.staticHostTransientStringSetterQualified, true);
  assert.equal(result.staticHostSelectorDefaultEmptyQualified, true);
  assert.equal(result.staticHostSelectorEmptyGuardQualified, true);
  assert.equal(result.staticHostSelectorPostlookupEmptyAssignmentQualified, true);
  assert.equal(result.staticHostSelectorExistingCallbackPrelookupMethodQualified, true);
  assert.equal(result.staticHostLookupMissBypassesCallbackStageQualified, true);
  assert.equal(result.staticHostRegistryFNV1a64Qualified, true);
  assert.equal(result.staticHostRegistryCollisionLengthAndByteEqualityQualified, true);
  assert.equal(result.staticHostRegistryMemcmpImportThunkQualified, true);
  assert.equal(result.specificRegisteredEventKeyMatchObserved, false);
  assert.equal(result.staticHostOwnerConditionalVectorResetQualified, true);
  assert.equal(result.specificFba020AdapterSelectedProven, false);
  // Generic callback dispatch preserves its own host; particular adapter
  // selection and equality with a previous initializer instance stay unproven.
  assert.equal(result.callbackProcessorArgumentMatchesRegisteredHostProven, false);
  assert.equal(result.producerProcessorReceiverTypeMatchProven, false);
  assert.equal(result.dispatchVectorElementProducerProven, false);
  assert.equal(result.dispatchVectorProducerOwnerIdentityProven, false);
  assert.equal(result.threadReceiverAppendOwnerVptrIdentityProven, false);
  assert.equal(result.threadStartedAtRuntimeProven, false);
  assert.equal(result.liveExecutionProven, false);
  assert.equal(result.playerIdentityProven, false);
  assert.equal(result.dispatchBranchesVerified, 2);
  assert.equal(result.negativeMutationRejected, true);
});

test('fails closed on a truncated source image', () => {
  assert.throws(() => verifyRoot001Bytes(original.subarray(0, original.length - 1)), /size mismatch/);
});

// Mutations target stated source fields; the whole-image SHA must reject first.
// Original-image window/opcode/call/RIP checks independently pin the named source relationships.
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
  // Newly source-qualified callers, not producers of vector elements.
  ['vector processor first direct parent call', 0xfba02c],
  ['vector processor midstream parent call', 0xfc8abd],
  ['vector processor second-path parent call', 0xfca4b0],
  // The contiguous code-pointer run has multiple interior vptr starts; no slot is established.
  ['C2M one object-vptr assignment', 0x5dc530],
  ['C2M interior vptr at +0x100', 0x5da7df],
  ['C2M interior vptr +0x190', 0x5da88e],
  ['C2M distinct vptr at +0x198', 0x5da89c],
  ['C2M interior vptr at object start', 0x5db354],
  // The following writers append into an object-local +0x80 vector.
  // Ownership identity with the registered-handler swapper is still unresolved.
  ['append writer A owner parameter', 0x74bc1f],
  ['append writer A capacity guard', 0x74bd92],
  ['append writer A element pointer store', 0x74bdc5],
  ['append writer A lock release', 0x74be07],
  ['append writer B owner parameter', 0x74bf1f],
  ['append writer B capacity guard', 0x74c085],
  ['append writer B element pointer store', 0x74c0b8],
  ['append writer B lock release', 0x74c0fa],
  // New source-qualified owner class/vector lifecycle and receiver-relative field link.
  ['append owner virtual method A pointer', 0x26be3a8],
  ['append owner virtual method B pointer', 0x26be3b0],
  ['append owner constructor installs vptr', 0x74aaa9],
  ['append owner constructor initializes vector', 0x74aae3],
  ['append owner destructor resets vptr', 0x74ac0a],
  ['append initializer saves incoming receiver', 0x76f015],
  ['initializer calls RAX-preserving stack probe', 0x76f01f],
  ['stack probe preserves the RAX allocation size', 0x24e1160],
  ['append owner constructor callsite', 0x7724d9],
  ['append initializer host field +0x6A8', 0x7724fc],
  ['append initializer restores field address after cleanup', 0x772545],
  ['append initializer stores owner pointer', 0x772555],
  // Same initializer receiver registers a separate callback adapter under +0x240.
  // Whether delivered callback RDX points back to that host remains UNPROVEN.
  ['host singleton object allocation', 0x761f14],
  ['host constructor installs primary vptr', 0x75ba04],
  ['host initialized global reference', 0x761f4a],
  ['host virtual initializer pointer', 0x26be9f8],
  ['host callback lookup method', 0x766050],
  ['same initializer receiver calls callback builder', 0x771f36],
  ['callback builder saves incoming host receiver', 0x777ce0],
  ['adapter installs its distinct vptr', 0x7781bf],
  ['adapter vptr links processor forwarding wrapper', 0x26beb40],
  ['adapter callback registered under host collection', 0x778210],
  ['callback wrapper preserves incoming RDX as processor receiver', 0xfba026],
  ['adapter reference committed to host collection slot', 0x77822e],
  ['A adapter allocation can be null', 0x7781a0],
  ['B adapter allocation can be null', 0x7786f4],
  ['B adapter reads same original host', 0x77872d],
  ['B adapter constructed vptr', 0xfc91ba],
  ['B adapter vptr processor slot', 0x2712f20],
  ['host selector virtual registry lookup', 0x776230],
  ['selected registry result into host+0x218', 0x77628a],
  ['host virtual callback invocation', 0x779c72],
  ['callback invocation original host RDX', 0x779c6d],
  ['A callback literal LoginFailed registration key', 0x26bf9b0],
  ['A callback second consumer', 0xfba034],
  ['host callback registration slot accessor', 0x75d9f4],
  // The new source-only key/setter/cleanup proof must fail closed on edits.
  ['host string initial empty state', 0x75b2e9],
  ['host transient string key setter', 0x77d761],
  ['host non-reentrant key guard', 0x77d775],
  ['host empty key selector skip', 0x776199],
  ['host existing callback virtual cleanup', 0x7761da],
  ['null registry result skips staging', 0x776275],
  ['host FNV key hash', 0x783aa0],
  ['host lookup calls collision checker', 0x783afc],
  ['collision length comparison', 0x4ef4bf],
  ['collision byte comparator call', 0x4ef4d5],
  ['collision chain mismatch advance', 0x4ef4e8],
  ['collision memcmp IAT thunk', 0x25047c7],
  ['registered InGame literal', 0x26a79d0],
  ['LoginFailed key to setter', 0x765edc],
  ['InGame literal to setter caller', 0xfcf553],
  ['InGame getter to setter tail', 0xfcf5ff],
  ['published host getter', 0x766014],
  ['host owner reset receiver', 0x7639ce],
  ['conditional owner vector reset', 0x74b756],
  // Static host owner publication and CRT thread-argument flow (NOT runtime execution).
  ['append owner constructed vptr', 0x74aab0],
  ['constructed owner written into host slot', 0x772555],
  ['thread entry callback pointer', 0x74c875],
  ['thread receiver passed in R9', 0x74c87c],
  ['indirect CRT thread-start call', 0x74c888],
  ['thread callback saves incoming receiver', 0x74d5f2],
  ['thread parameter forwarded to virtual receiver', 0x74d6d7],
  ['virtual receiver retains incoming argument', 0x74d730],
  // These source mutations are rejected by the whole-image SHA gate first.
  ['host owner slot passed to native accessor', 0x77258c],
  ['host slot value forwarded to spawner', 0x772594],
  ['spawner receives same pointer in RDI', 0x74c6c9],
  ['thread spawner chained pdata record', 0x36465f4],
  ['thread spawner chained unwind header', 0x2e31fc4],
  ['post-publication owner retain call', 0x772578],
  ['owner refcount retain helper', 0x75eaf0],
  ['owner vector end reset', 0x74b827],
  // Only the first QWORD is compared before the reference pair is replaced.
  ['C2M reference pair first-key comparison', 0x5807f1],
  ['C2M reference pair first-key match branch', 0x5807f8],
  ['C2M reference pair retain/release transition', 0x580821],
  ['C2M transient reference-pair cleanup', 0x49ac00],
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
