import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import crypto from 'node:crypto';
import {spawnSync} from 'node:child_process';
import {fileURLToPath} from 'node:url';
import {parseSavedLua} from './read-rrecollector-saved.mjs';
import {summarizeQuestReceipt, readQuestReceipt, compareQuestReceipts, serializeQuestReceipt} from './export-rrecollector-quests.mjs';

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
function pair() {
  const before = fixture(), after = fixture();
  after.questSnapshotSequence = after.questSnapshot.sequence = 4;
  after.questSnapshot.context.frameTime = 10; after.questSnapshot.context.realTime = 13;
  objective(after).countDone = 1;
  const receipt = x => {
    const bytes = Buffer.from(saved(x));
    return summarizeQuestReceipt(x, {sha256: crypto.createHash('sha256').update(bytes).digest('hex'), bytes: bytes.length});
  };
  return {before, after, compare: () => compareQuestReceipts(receipt(before), receipt(after))};
}
const preview = text => ({type: 'string', encoding: 'ascii', preview: text,
  sourceBytes: text.length, retainedBytes: text.length, truncated: false});
function diagnosticFixture() {
  const x = fixture(); x.addonVersion = x.questSnapshot.addonVersion = '0.4.21';
  x.questSnapshot.status = 'partial'; x.questSnapshot.complete = false;
  objective(x).indicators = [];
  Object.assign(x.questSnapshot.counts, {indicatorsRetained: 0, malformedIndicators: 1});
  x.questSnapshot.indicatorShapes = {schemaVersion: 1, scope: 'unsupported-indicator-diagnostics',
    coverage: 'bounded-sample', counts: {seen: 1, sampled: 1, dropped: 0, fieldsScanned: 2,
      stringsTruncated: 0, encodedBytesRetained: 23, fieldReadErrors: 0, mapReads: 1},
    histogram: {'string/table': 1}, samples: [{questId: 'qTEST', objectiveKey: 1,
      entryKind: 'entry', status: 'unsupported-shape', key: preview('mTEST'),
      value: {type: 'table', fieldsTruncated: false, fields: [
        {key: preview('zero'), value: {type: 'number', finite: true, value: 0}},
        {key: preview('flag'), value: {type: 'boolean', value: false}}]},
      candidateLookups: [{candidateSource: 'key', status: 'returned', cached: false,
        identityMatches: true, coordinateFrameVerified: false, questAssociationVerified: false,
        identifier: preview('mTEST'), returnedId: preview('mTEST'), coordX: 0, coordY: 2, coordZ: -3}]}]};
  return x;
}
test('v21 retains v20 journals with separate root/capture/attempt versions', () => {
  const x = fixture(); x.addonVersion = '0.4.21';
  x.questAttempt = {addonVersion: '0.4.21', status: 'error'};
  const result = summarizeQuestReceipt(x);
  assert.equal(result.savedAddonVersion, '0.4.21'); assert.equal(result.producerVersion, '0.4.20');
  assert.equal(result.indicatorDiagnostics, null); assert.equal(result.journalRetainedAfterFailure, true);
});
test('v21 source-bound candidate diagnostics preserve zero/false without producing destinations', () => {
  const result = summarizeQuestReceipt(diagnosticFixture());
  const sample = result.indicatorDiagnostics.samples[0], candidate = sample.candidateLookups[0];
  assert.equal(candidate.sourceBindingsVerified, true); assert.equal(candidate.coordX, 0);
  assert.equal(candidate.coordinateFrameVerified, false); assert.equal(candidate.questAssociationVerified, false);
  assert.equal(sample.value.fields[0].value.value, 0); assert.equal(sample.value.fields[1].value.value, false);
  assert.equal(result.status, 'partial'); assert.deepEqual(result.nextObjectives[0].locations, []);
});
test('diagnostic binary bytes remain exact hex and do not need UTF-8 decoding', () => {
  const x = diagnosticFixture(), d = x.questSnapshot.indicatorShapes;
  d.samples[0].value.fields.push({key: preview('bin'), value: {type: 'string', encoding: 'hex-bytes',
    preview: '00FF', sourceBytes: 2, retainedBytes: 2, truncated: false}});
  d.counts.fieldsScanned++; d.counts.encodedBytesRetained += 7;
  const result = summarizeQuestReceipt(x).indicatorDiagnostics.samples[0].value.fields[2].value;
  assert.equal(result.preview, '00FF'); assert.equal(result.encoding, 'hex-bytes');
});
test('clipped or different source/candidate/returned previews cannot bind an identifier', () => {
  for (const target of ['source', 'identifier', 'returnedId']) {
    const x = diagnosticFixture(), d = x.questSnapshot.indicatorShapes, sample = d.samples[0];
    const p = target === 'source' ? sample.key : sample.candidateLookups[0][target];
    p.preview = 'm'; p.retainedBytes = 1; p.truncated = true;
    d.counts.encodedBytesRetained -= 4; d.counts.stringsTruncated++;
    const result = summarizeQuestReceipt(x).indicatorDiagnostics.samples[0].candidateLookups[0];
    assert.equal(result.sourceBindingsVerified, false); assert.equal(result.coordX, null);
  }
  const x = diagnosticFixture(); x.questSnapshot.indicatorShapes.samples[0].key.preview = 'mFAKE';
  assert.equal(summarizeQuestReceipt(x).indicatorDiagnostics.samples[0].candidateLookups[0].sourceBindingsVerified, false);
});
test('wrong returned identity never exposes diagnostic coordinates', () => {
  const x = diagnosticFixture(), candidate = x.questSnapshot.indicatorShapes.samples[0].candidateLookups[0];
  candidate.status = 'id-mismatch'; candidate.identityMatches = false; candidate.returnedId.preview = 'mNOPE';
  const result = summarizeQuestReceipt(x).indicatorDiagnostics.samples[0].candidateLookups[0];
  assert.equal(result.sourceBindingsVerified, false); assert.equal(result.coordZ, null);
});
test('diagnostic schema, provenance, counters and qualifications fail closed', () => {
  for (const mutate of [x => delete x.questSnapshot.indicatorShapes,
    x => x.questSnapshot.indicatorShapes.samples[0].questId = 'qOTHER',
    x => x.questSnapshot.indicatorShapes.counts.mapReads = 2,
    x => x.questSnapshot.indicatorShapes.counts.encodedBytesRetained++,
    x => x.questSnapshot.indicatorShapes.histogram['string/table'] = 2,
    x => x.questSnapshot.indicatorShapes.samples[0].candidateLookups[0].questAssociationVerified = true,
    x => x.questSnapshot.indicatorShapes.samples[0].candidateLookups[0].coordX = '0',
    x => x.questSnapshot.indicatorShapes.samples[0].key.encoding = 'unknown']) {
    const x = diagnosticFixture(); mutate(x);
    assert.throws(() => summarizeQuestReceipt(x), /QUEST_SHAPE/);
  }
});
test('diagnostic sample, field, byte and lookup bounds cannot be widened by source metadata', () => {
  for (const mutate of [x => x.questSnapshot.indicatorShapes.counts.mapReads = 17,
    x => x.questSnapshot.indicatorShapes.counts.encodedBytesRetained = 8193,
    x => x.questSnapshot.indicatorShapes.samples = Array(9).fill(x.questSnapshot.indicatorShapes.samples[0]),
    x => x.questSnapshot.indicatorShapes.samples[0].value.fields = Array(17).fill({key: preview('x'), value: {type: 'nil'}}),
    x => x.questSnapshot.indicatorShapes.samples[0].candidateLookups.push(x.questSnapshot.indicatorShapes.samples[0].candidateLookups[0])]) {
    const x = diagnosticFixture(); mutate(x);
    assert.throws(() => summarizeQuestReceipt(x), /QUEST_SHAPE|QUEST_ARRAY_SHAPE/);
  }
});

test('two advancing complete retained captures report exact recorded count differences', () => {
  const p = pair(), result = p.compare();
  assert.equal(result.status, 'comparable');
  assert.equal(result.summary.countAdvanced, 1);
  assert.equal(result.quests[0].objectives[0].countDoneDelta, 1);
  assert.equal(result.quests[0].objectives[0].before.countDone, 0);
  assert.equal(result.quests[0].objectives[0].after.countDone, 1);
  for (const value of Object.values(result.qualification)) assert.equal(value, false);
  assert.notEqual(result.previous.sourceSha256, result.current.sourceSha256);
});
test('quest comparison rejects identical bytes, stale sequence and each nonadvancing clock', () => {
  const p = pair(); Object.assign(p.after, structuredClone(p.before));
  assert.ok(p.compare().reasons.includes('same-source-bytes'));
  for (const mutate of [p => p.after.questSnapshotSequence = p.after.questSnapshot.sequence = 3,
    p => p.after.questSnapshot.context.frameTime = 9,
    p => p.after.questSnapshot.context.realTime = 12,
    p => p.after.questSnapshot.context.frameTime = 8]) {
    const p = pair(); mutate(p);
    assert.equal(p.compare().status, 'incomparable');
    assert.equal(p.compare().quests.length, 0);
  }
});
test('comparison player IDs are typed and do not match by display name', () => {
  const p = pair(); p.before.questSnapshot.context.player.id = 123;
  p.after.questSnapshot.context.player.id = '123';
  assert.ok(p.compare().reasons.includes('player-mismatch-or-unbound'));
  p.after.questSnapshot.context.player.id = 'uOTHER';
  assert.equal(p.compare().summary.countAdvanced, 0);
});
test('partial retained journals cannot qualify objective matching', () => {
  const p = pair(); p.before.questSnapshot.complete = false; p.before.questSnapshot.status = 'partial';
  assert.ok(p.compare().reasons.includes('incomplete-coverage'));
  assert.equal(p.compare().summary.countAdvanced, 0);
});
test('quest source identity is retained and required for count deltas', () => {
  const p = pair(); quest(p.before).sourceId = 'qMISMATCH';
  assert.equal(summarizeQuestReceipt(p.before).journal[0].identityQualified, false);
  assert.equal(p.compare().quests[0].objectives[0].classification, 'quest-identity-unqualified');
  assert.equal(p.compare().summary.countAdvanced, 0);
});
test('changed descriptions and required quantities remain diagnostic', () => {
  for (const mutate of [x => objective(x).description = 'Different step',
    x => objective(x).description = '', x => objective(x).count = 4,
    x => delete objective(x).count, x => delete objective(x).countDone]) {
    const p = pair(); mutate(p.after);
    assert.equal(p.compare().quests[0].objectives[0].countDoneDelta, null);
    assert.equal(p.compare().summary.countAdvanced, 0);
  }
});
test('duplicate descriptions and reordered objective keys cannot manufacture progress', () => {
  const p = pair();
  for (const x of [p.before, p.after]) {
    quest(x).objectives.push({...structuredClone(objective(x)), key: 2});
    x.questSnapshot.counts.objectivesRetained = x.questSnapshot.counts.indicatorsRetained = 2;
  }
  assert.equal(p.compare().summary.objectivesUnqualified, 2);
  assert.ok(p.compare().quests[0].objectives.every(x => x.classification === 'description-ambiguous'));
  quest(p.before).objectives[1].description = 'Second step';
  quest(p.after).objectives[0].description = 'Second step';
  assert.equal(p.compare().summary.countAdvanced, 0);
});
test('typed objective keys are not silently equated', () => {
  const p = pair(); objective(p.after).key = '1';
  assert.equal(p.compare().summary.objectivesUnqualified, 2);
  assert.equal(p.compare().summary.countAdvanced, 0);
});
test('decreased counters describe a reset without inventing quest failure', () => {
  const p = pair(); objective(p.before).countDone = 2;
  const result = p.compare();
  assert.equal(result.summary.countRegressed, 1);
  assert.equal(result.quests[0].objectives[0].countDoneDelta, -1);
  assert.equal(result.quests[0].reportedFailedAfter, false);
});
test('counts at the required total do not manufacture explicit completion', () => {
  const p = pair(); objective(p.after).countDone = 3;
  assert.equal(p.compare().quests[0].objectives[0].after.reportedComplete, false);
  assert.equal(p.compare().quests[0].reportedCompleteAfter, false);
  objective(p.after).complete = true; quest(p.after).complete = true; quest(p.after).failed = true;
  assert.equal(p.compare().quests[0].objectives[0].after.reportedComplete, true);
  assert.equal(p.compare().quests[0].reportedFailedAfter, true);
});
test('quest disappearance and newly observed quests never imply completion', () => {
  const p = pair(); p.after.questSnapshot.quests = []; p.after.questSnapshot.status = 'empty';
  p.after.questSnapshot.counts = {questsRetained: 0, objectivesRetained: 0, indicatorsRetained: 0};
  const result = p.compare();
  assert.equal(result.summary.questsAbsent, 1);
  assert.equal(result.quests[0].reportedCompleteAfter, null);
  assert.equal(result.summary.countAdvanced, 0);
  quest(p.before).id = quest(p.before).sourceId = 'qDIFFERENT';
  p.after.questSnapshot.quests = fixture().questSnapshot.quests;
  p.after.questSnapshot.status = 'recorded'; p.after.questSnapshot.counts = fixture().questSnapshot.counts;
  assert.equal(p.compare().summary.questsAdded, 1);
  assert.equal(p.compare().summary.questsAbsent, 1);
});
test('unrecognized counter names cannot echo arbitrary large metadata', () => {
  const x = fixture(); x.questSnapshot.counts['x'.repeat(200_000)] = 0;
  assert.throws(() => summarizeQuestReceipt(x), /QUEST_COUNTER_FIELD/);
});
test('comparison CLI validates both originals and rejects duplicate options before output', t => {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'rre-quest-compare-'));
  assert.equal(path.dirname(path.resolve(dir)), path.resolve(os.tmpdir()));
  assert.ok(path.basename(dir).startsWith('rre-quest-compare-'));
  t.after(() => fs.rmSync(dir, {recursive: true, force: true}));
  fs.mkdirSync(path.join(dir, 'previous'));
  const input = path.join(dir, 'RRECollector.lua');
  const previous = path.join(dir, 'previous', 'RRECollector.lua');
  const output = path.join(dir, 'comparison.json'), p = pair();
  fs.writeFileSync(input, saved(p.after)); fs.writeFileSync(previous, saved(p.before));
  const cli = fileURLToPath(new URL('./export-rrecollector-quests.mjs', import.meta.url));
  const args = [cli, input, '--previous', previous, '--output', output];
  assert.equal(spawnSync(process.execPath, args).status, 0);
  const report = JSON.parse(fs.readFileSync(output, 'utf8'));
  assert.equal(report.comparison.summary.countAdvanced, 1);
  assert.equal(report.comparison.previous.sourceSha256,
    crypto.createHash('sha256').update(fs.readFileSync(previous)).digest('hex'));
  const invalidOutput = path.join(dir, 'invalid.json');
  assert.equal(spawnSync(process.execPath, [cli, input, '--previous', previous,
    '--previous', previous]).status, 2);
  fs.writeFileSync(previous, 'RRECollectorData=run_game()');
  assert.equal(spawnSync(process.execPath, [cli, input, '--output', invalidOutput,
    '--previous', previous]).status, 2);
  assert.equal(fs.existsSync(invalidOutput), false);
  const retained = fs.readFileSync(output);
  assert.equal(spawnSync(process.execPath, args).status, 2);
  assert.deepEqual(fs.readFileSync(output), retained);
});
test('bounded512-objective comparison fits the existing helper output limit', () => {
  const p = pair();
  for (const [savedRoot, done] of [[p.before, 0], [p.after, 1]]) {
    savedRoot.questSnapshot.quests = Array.from({length: 16}, (_, q) => {
      const id = ('q' + q).padEnd(256, 'q');
      return {id, sourceId: id, status: 'returned', name: 'n'.repeat(2048),
        complete: false, failed: false,
        objectives: Array.from({length: 32}, (_, o) => {
          const mapId = ('m' + ((q * 32 + o) % 128)).padEnd(256, 'm');
          return {key: ('o' + o).padEnd(256, 'o'), description: ('step' + o).padEnd(128, 'd'),
            count: 3, countDone: done, complete: false,
            indicators: [{id: mapId, status: 'returned', location: {sourceId: mapId,
              coordX: 0, coordY: 1, coordZ: 2, title: 't'.repeat(64)}}]};
        })};
    });
    savedRoot.questSnapshot.counts = {questsRetained: 16, objectivesRetained: 512,
      indicatorsRetained: 512, mapReads: 128, textBytesRetained: 131072};
    assert.ok(Buffer.byteLength(saved(savedRoot)) < 2_000_000);
  }
  const report = summarizeQuestReceipt(p.after); report.comparison = p.compare();
  assert.equal(report.comparison.summary.countAdvanced, 512);
  assert.ok(Buffer.byteLength(JSON.stringify(report, null, 2)) < 4_000_000);
});
test('escape-heavy text reports a transport limit before stdout or output publication', t => {
  const x = fixture();
  x.questSnapshot.quests = Array.from({length: 16}, (_, q) => ({
    id: 'q' + q, sourceId: 'q' + q, status: 'returned', name: '\u0001'.repeat(2048),
    objectives: Array.from({length: 32}, (_, k) => ({key: k + 1,
      description: 'step' + k, count: 3, countDone: 0, indicators: []}))}));
  x.questSnapshot.counts = {questsRetained: 16, objectivesRetained: 512, indicatorsRetained: 0};
  assert.throws(() => serializeQuestReceipt(summarizeQuestReceipt(x)), /QUEST_OUTPUT_LIMIT/);
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'rre-quest-limit-'));
  assert.equal(path.dirname(path.resolve(dir)), path.resolve(os.tmpdir()));
  assert.ok(path.basename(dir).startsWith('rre-quest-limit-'));
  t.after(() => fs.rmSync(dir, {recursive: true, force: true}));
  const input = path.join(dir, 'RRECollector.lua'), output = path.join(dir, 'goals.json');
  const bytes = Buffer.from(saved(x).replaceAll('\\u0001', '\\001'));
  assert.ok(bytes.length < 2_000_000); fs.writeFileSync(input, bytes);
  assert.equal(readQuestReceipt(input).nextObjectives.length, 512);
  const cli = fileURLToPath(new URL('./export-rrecollector-quests.mjs', import.meta.url));
  const result = spawnSync(process.execPath, [cli, input, '--output', output], {encoding: 'utf8'});
  assert.equal(result.status, 2); assert.equal(result.stderr.trim(), 'QUEST_OUTPUT_LIMIT');
  assert.equal(result.stdout, ''); assert.equal(fs.existsSync(output), false);
});

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
