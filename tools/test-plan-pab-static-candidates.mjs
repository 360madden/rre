import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import {CATALOG, CATALOG_SHA, MAX_IDS, planCandidates} from './plan-pab-static-candidates.mjs';

const bytes = fs.readFileSync(CATALOG);
const plan = (calling, ids, original = bytes) => planCandidates({calling, ids, bytes: original});
const flame1 = 'A060ED54D21F2B259';
const flame2 = 'A1A35B21D4891044E';
const pet = 'A40C51A65DBA71310';

test('both Flame Lance declarations retain distinct IDs, lines and source hash', () => {
  const packet = plan('Cleric', [flame1, flame2]);
  assert.equal(packet.catalogSha256, CATALOG_SHA);
  assert.deepEqual(packet.selected.map(item => item.occurrences[0].sourceLine), [18, 22]);
  for (const item of packet.selected) {
    assert.equal(item.occurrences[0].sourceSha256, 'fbcdf9383c93204c976dc526b126fe6b49c677aa169e87f25fc13b1aefa4835c');
    assert.equal(item.duplicateNameContext.length, 1);
    assert.notEqual(item.duplicateNameContext[0].id, item.id);
  }
});
test('shared ID preserves other calling provenance without selecting it', () => {
  const p = plan('Cleric', [pet]).selected[0];
  assert.equal(p.occurrences[0].soul, 'Druid');
  assert.equal(p.otherCallingOccurrences[0].soul, 'Ranger');
  assert.equal(p.otherCallingOccurrences[0].calling, 'Rogue');
  assert.equal(plan('Rogue', [pet]).selected[0].otherCallingOccurrences[0].calling, 'Cleric');
});
test('wrong calling and unknown ID fail closed', () => {
  assert.throws(() => plan('Warrior', [pet]), /ID_NOT_IN_CALLING/);
  assert.throws(() => plan('Cleric', ['A0000000000000000']), /ID_NOT_IN_CALLING/);
});
test('explicit bounded unique canonical IDs required', () => {
  assert.throws(() => plan('cleric', [pet]), /CALLING_REQUIRED/);
  assert.throws(() => plan('Cleric', []), /ID_COUNT_OUT_OF_RANGE/);
  assert.throws(() => plan('Cleric', Array(MAX_IDS + 1).fill(pet)), /ID_COUNT_OUT_OF_RANGE/);
  assert.throws(() => plan('Cleric', [pet, pet]), /DUPLICATE_REQUEST_ID/);
  assert.throws(() => plan('Cleric', [pet.toLowerCase()]), /INVALID_ID/);
});
test('single-byte mutation or truncation is rejected', () => {
  const mutated = Buffer.from(bytes);
  mutated[10] ^= 1;
  assert.throws(() => plan('Cleric', [pet], mutated), /CATALOG_SHA_MISMATCH/);
  assert.throws(() => plan('Cleric', [pet], bytes.subarray(0, -1)), /CATALOG_SHA_MISMATCH/);
});
test('deterministic packet never claims live qualification', () => {
  const p = plan('Cleric', [flame2, pet]);
  assert.deepEqual(p, plan('Cleric', [flame2, pet]));
  assert.deepEqual(p.requestedIds, [flame2, pet]);
  assert.deepEqual(p.qualification, {
    staticSourceOnly: true, currentBuildVerified: false, apiKnownVerified: false,
    learnabilityVerified: false, castabilityVerified: false, liveExecution: false,
  });
});
