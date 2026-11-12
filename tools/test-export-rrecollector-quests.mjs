import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import crypto from 'node:crypto';
import {spawnSync} from 'node:child_process';
import {fileURLToPath} from 'node:url';
import {parseSavedLua} from './read-rrecollector-saved.mjs';
import {summarizeQuestReceipt, readQuestReceipt} from './export-rrecollector-quests.mjs';

function fixture() {
  return {addonVersion: '0.4.20', questSnapshotSequence: 3, questSnapshot: {
    schemaVersion: 1, addonVersion: '0.4.20', scope: 'quest-journal-snapshot', sequence: 3,
    status: 'recorded', complete: true, context: {capabilities: {player: true}, frameTime: 9, realTime: 12,
      player: {id: 'uTEST', zone: 'zTEST'}},
    counts: {questsRetained: 1, objectivesRetained: 1, indicatorsRetained: 1},
    quests: [{id: 'qTEST', sourceId: 'qTEST', status: 'returned', name: 'Collect flowers',
      track: true, complete: false, failed: false,
      objectives: [{key: 1, description: 'Pick flowers', count: 3, countDone: 0, complete: false,
        indicators: [{id: 'mTEST', status: 'returned', location: {sourceId: 'mTEST',
          coordX: 0, coordY: 2, coordZ: -3, title: 'Flower patch'}}]}]}]}};
}
const quest = x => x.questSnapshot.quests[0];
const objective = x => quest(x).objectives[0];
function lua(x) {
  if (x === null) return 'nil';
  if (Array.isArray(x)) return '{' + x.map(lua).join(',') + '}';
  if (typeof x === 'object') return '{' + Object.entries(x)
    .map(([key, value]) => '[' + JSON.stringify(key) + ']=' + lua(value)).join(',') + '}';
  return JSON.stringify(x);
}
const saved = x => 'RRECollectorData=' + lua(x);

test('literal producer-shaped quest receipt keeps zero, false and opaque coordinates', () => {
  const result = summarizeQuestReceipt(parseSavedLua(saved(fixture())));
  assert.equal(result.coverageComplete, true);
  assert.equal(result.nextObjectives[0].countDone, 0);
  assert.equal(result.nextObjectives[0].remaining, 3);
  assert.equal(result.nextObjectives[0].locations[0].coordX, 0);
  assert.equal(result.journal[0].complete, false);
  assert.equal(result.qualification.live, false);
  assert.equal(result.qualification.coordinateFrameVerified, false);
  assert.equal(Object.hasOwn(result.nextObjectives[0], 'distance'), false);
});
test('missing capture, wrong version, scope and unbound sequence are rejected', () => {
  assert.throws(() => summarizeQuestReceipt({}), /QUEST_NOT_CAPTURED/);
  for (const mutate of [x => x.addonVersion = '0.4.19',
    x => x.questSnapshot.addonVersion = '0.4.19']) {
    const x = fixture(); mutate(x);
    assert.throws(() => summarizeQuestReceipt(x), /QUEST_VERSION_MISMATCH/);
  }
  const x = fixture(); x.questSnapshotSequence = 4;
  assert.throws(() => summarizeQuestReceipt(x), /QUEST_SEQUENCE_UNBOUND/);
  x.questSnapshotSequence = 3; x.questSnapshot.scope = 'different';
  assert.throws(() => summarizeQuestReceipt(x), /QUEST_SCHEMA_SCOPE/);
});
test('completed or failed quests and completed objectives never become next goals', () => {
  for (const change of [x => quest(x).complete = true, x => quest(x).failed = true,
    x => objective(x).complete = true]) {
    const x = fixture(); change(x);
    assert.equal(summarizeQuestReceipt(x).nextObjectives.length, 0);
  }
});
test('a preserved journal exposes the last recorded API failure without claiming freshness', () => {
  const x = fixture(); x.questAttempt = {addonVersion: '0.4.20', status: 'unavailable'};
  const result = summarizeQuestReceipt(x);
  assert.equal(result.status, 'recorded');
  assert.equal(result.statusScope, 'retained-snapshot');
  assert.equal(result.lastRecordedAttempt.status, 'unavailable');
  assert.equal(result.journalRetainedAfterFailure, true);
  assert.equal(result.qualification.freshnessVerified, false);
  x.questAttempt.addonVersion = 'old';
  assert.equal(summarizeQuestReceipt(x).lastRecordedAttempt, null);
});
test('producer text byte bounds prevent goal-name amplification and keep UTF-8 boundaries', () => {
  const x = fixture(); quest(x).name = '🌼'.repeat(512);
  assert.equal(summarizeQuestReceipt(x).nextObjectives[0].questName, quest(x).name);
  quest(x).name += 'a';
  assert.throws(() => summarizeQuestReceipt(x), /QUEST_TEXT_LIMIT/);
  quest(x).name = 'x'.repeat(150_000);
  assert.throws(() => summarizeQuestReceipt(x), /QUEST_TEXT_LIMIT/);
  const y = fixture(); objective(y).description = 'x'.repeat(2049);
  assert.throws(() => summarizeQuestReceipt(y), /QUEST_TEXT_LIMIT/);
  const z = fixture(); objective(z).indicators[0].location.title = 'x'.repeat(2049);
  assert.throws(() => summarizeQuestReceipt(z), /QUEST_TEXT_LIMIT/);
});
test('projected content text respects the producer global budget before duplicate goals', () => {
  const x = fixture(); const base = quest(x); delete base.name;
  base.objectives = Array.from({length: 32}, (_, i) => ({key: i + 1,
    description: 'x'.repeat(2048), count: 1, countDone: 0, indicators: []}));
  x.questSnapshot.quests.push({...structuredClone(base), id: 'qOTHER', sourceId: 'qOTHER'});
  Object.assign(x.questSnapshot.counts, {questsRetained: 2, objectivesRetained: 64, indicatorsRetained: 0});
  assert.equal(summarizeQuestReceipt(x).nextObjectives.length, 64);
  base.name = 'x';
  assert.throws(() => summarizeQuestReceipt(x), /QUEST_TEXT_BUDGET/);
});
test('unexpected status and context objects are not echoed as quest metadata', () => {
  const x = fixture(); quest(x).status = {private: 'unexpected'};
  x.questSnapshot.context.player.zone = {private: 'unexpected'};
  const result = summarizeQuestReceipt(x);
  assert.equal(result.journal[0].status, null);
  assert.equal(result.context.zone, null);
  assert.equal(result.nextObjectives.length, 0);
  x.questSnapshot.context.player.zone = false;
  assert.equal(summarizeQuestReceipt(x).context.zone, false);
  x.questSnapshot.context.player.zone = 0;
  assert.equal(summarizeQuestReceipt(x).context.zone, 0);
});
test('unavailable rows, incomplete context and nonzero error counters cannot become goals', () => {
  const x = fixture(); x.questSnapshot.counts.detailFailures = 1;
  assert.throws(() => summarizeQuestReceipt(x), /QUEST_COMPLETENESS_CONTRADICTION/);
  x.questSnapshot.complete = false; x.questSnapshot.status = 'unavailable';
  assert.throws(() => summarizeQuestReceipt(x), /QUEST_UNAVAILABLE_HAS_ROWS/);
  x.questSnapshot.status = 'partial'; delete x.questSnapshot.context.capabilities;
  assert.throws(() => summarizeQuestReceipt(x), /QUEST_CONTEXT_UNBOUND/);
});
test('missing completion facts remain unknown; counts alone can establish remaining work', () => {
  const x = fixture(); delete objective(x).complete;
  assert.equal(summarizeQuestReceipt(x).nextObjectives.length, 1);
  delete objective(x).count;
  assert.equal(summarizeQuestReceipt(x).nextObjectives.length, 0);
  assert.equal(summarizeQuestReceipt(x).journal[0].objectives[0].state, 'completion-unknown');
});
test('map and quest lookup identity mismatches cannot produce destinations', () => {
  const x = fixture(); objective(x).indicators[0].location.sourceId = 'mOTHER';
  assert.deepEqual(summarizeQuestReceipt(x).nextObjectives[0].locations, []);
  quest(x).sourceId = 'qOTHER';
  assert.deepEqual(summarizeQuestReceipt(x).nextObjectives, []);
});
test('failed map calls and incomplete coordinates retain objectives without invented locations', () => {
  const x = fixture(); delete objective(x).indicators[0].location.coordZ;
  assert.deepEqual(summarizeQuestReceipt(x).nextObjectives[0].locations, []);
  objective(x).indicators[0].status = 'error';
  assert.deepEqual(summarizeQuestReceipt(x).nextObjectives[0].locations, []);
});
test('partial and unavailable journal results stay distinct from an empty journal', () => {
  const x = fixture(); x.questSnapshot.complete = false; x.questSnapshot.status = 'partial';
  assert.equal(summarizeQuestReceipt(x).coverageComplete, false);
  for (const status of ['empty', 'unavailable', 'error']) {
    const x = fixture(); x.questSnapshot.status = status; x.questSnapshot.complete = status === 'empty';
    x.questSnapshot.quests = []; x.questSnapshot.counts = {questsRetained: 0,
      objectivesRetained: 0, indicatorsRetained: 0};
    assert.equal(summarizeQuestReceipt(x).status, status);
  }
  x.questSnapshot.complete = true;
  assert.throws(() => summarizeQuestReceipt(x), /QUEST_COMPLETENESS_CONTRADICTION/);
});
test('malformed counters, duplicate identities, sparse arrays and invalid quantities fail', () => {
  for (const value of [-1, 0.5, Infinity, 4]) {
    const x = fixture(); objective(x).countDone = value;
    assert.throws(() => summarizeQuestReceipt(x), /QUEST_OBJECTIVE_COUNT/);
  }
  const x = fixture(); x.questSnapshot.counts.questsRetained = 2;
  assert.throws(() => summarizeQuestReceipt(x), /QUEST_COUNT_MISMATCH/);
  x.questSnapshot.quests.push(structuredClone(quest(x)));
  assert.throws(() => summarizeQuestReceipt(x), /QUEST_ID_SHAPE/);
  x.questSnapshot.quests = {2: quest(x)};
  assert.throws(() => summarizeQuestReceipt(x), /QUEST_ARRAY_SHAPE/);
});
test('tracked goals sort before watched and other goals without unqualified distance sorting', () => {
  const x = fixture(); const other = structuredClone(quest(x));
  other.id = other.sourceId = 'qOTHER'; other.track = false; other.watch = true;
  x.questSnapshot.quests.unshift(other);
  x.questSnapshot.counts = {questsRetained: 2, objectivesRetained: 2, indicatorsRetained: 2};
  assert.deepEqual(summarizeQuestReceipt(x).nextObjectives.map(x => x.questId), ['qTEST', 'qOTHER']);
});
test('global objective limit rejects many individually bounded rows', () => {
  const x = fixture(); const template = structuredClone(quest(x));
  x.questSnapshot.quests = Array.from({length: 17}, (_, q) => ({...structuredClone(template),
    id: 'q' + q, sourceId: 'q' + q, objectives: Array.from({length: 32}, (_, k) => ({
      ...structuredClone(template.objectives[0]), key: k + 1, indicators: []}))}));
  x.questSnapshot.counts = {questsRetained: 17, objectivesRetained: 544, indicatorsRetained: 0};
  assert.throws(() => summarizeQuestReceipt(x), /QUEST_GLOBAL_LIMIT/);
});
test('original-file provenance and CLI exclusive output creation', t => {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'rre-quest-'));
  assert.equal(path.dirname(path.resolve(dir)), path.resolve(os.tmpdir()));
  assert.ok(path.basename(dir).startsWith('rre-quest-'));
  t.after(() => fs.rmSync(dir, {recursive: true, force: true}));
  const input = path.join(dir, 'RRECollector.lua'), output = path.join(dir, 'goals.json');
  const bytes = Buffer.from(saved(fixture())); fs.writeFileSync(input, bytes);
  assert.equal(readQuestReceipt(input).sourceSha256,
    crypto.createHash('sha256').update(bytes).digest('hex'));
  const cli = fileURLToPath(new URL('./export-rrecollector-quests.mjs', import.meta.url));
  const args = [cli, input, '--output', output];
  assert.equal(spawnSync(process.execPath, args).status, 0);
  const original = fs.readFileSync(output);
  assert.equal(JSON.parse(original).nextObjectives.length, 1);
  assert.equal(spawnSync(process.execPath, args).status, 2);
  assert.deepEqual(fs.readFileSync(output), original);
});
