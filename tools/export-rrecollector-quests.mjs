// Offline quest goals from a source-hashed RRECollector journal; no game actions.
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import {fileURLToPath} from 'node:url';
import {parseSavedLuaBytes} from './read-rrecollector-saved.mjs';
import {readStableOriginalWithMetadata} from './read-stable-original.mjs';

const VERSION = '0.4.20';
const object = x => x !== null && typeof x === 'object' && !Array.isArray(x);
const integer = x => Number.isSafeInteger(x) && x >= 0;
const id = x => typeof x === 'string'
  ? x.length > 0 && Buffer.byteLength(x) <= 256 && !/[\x00-\x1f\x7f]/.test(x)
  : integer(x);
const requireValue = (okay, code) => { if (!okay) throw Error(code); };
const token = x => typeof x + ':' + x;
const optionalText = x => {
  if (typeof x !== 'string') return null;
  requireValue(Buffer.byteLength(x) <= 2048, 'QUEST_TEXT_LIMIT');
  return x;
};
const scalar = x => typeof x === 'string' ? optionalText(x)
  : typeof x === 'boolean' || Number.isFinite(x) ? x : null;
function dense(value, max) {
  requireValue(value !== null && typeof value === 'object', 'QUEST_ARRAY_SHAPE');
  const keys = Object.keys(value);
  requireValue(keys.length <= max && (Array.isArray(value)
    ? keys.length === value.length && keys.every((key, i) => key === String(i))
    : keys.every((key, i) => key === String(i + 1))), 'QUEST_ARRAY_SHAPE');
  return Array.isArray(value) ? value : keys.map(key => value[key]);
}

export function summarizeQuestReceipt(saved, source = {}) {
  const snap = saved?.questSnapshot;
  requireValue(object(saved) && object(snap), 'QUEST_NOT_CAPTURED');
  requireValue(saved.addonVersion === VERSION && snap.addonVersion === VERSION,
    'QUEST_VERSION_MISMATCH');
  requireValue(snap.schemaVersion === 1 && snap.scope === 'quest-journal-snapshot',
    'QUEST_SCHEMA_SCOPE');
  requireValue(integer(snap.sequence) && snap.sequence > 0
    && saved.questSnapshotSequence === snap.sequence, 'QUEST_SEQUENCE_UNBOUND');
  requireValue(typeof snap.complete === 'boolean'
    && ['recorded', 'partial', 'empty', 'unavailable', 'error'].includes(snap.status),
    'QUEST_STATUS_SHAPE');
  requireValue(snap.complete === ['recorded', 'empty'].includes(snap.status),
    'QUEST_COMPLETENESS_CONTRADICTION');
  requireValue(object(snap.counts), 'QUEST_COUNTS_SHAPE');
  for (const n of Object.values(snap.counts))
    requireValue(integer(n) && n <= 131072, 'QUEST_COUNTER_RANGE');
  const quests = dense(snap.quests, 128);
  if (snap.status === 'unavailable' || snap.status === 'error')
    requireValue(quests.length === 0, 'QUEST_UNAVAILABLE_HAS_ROWS');
  else requireValue(snap.context?.capabilities?.player === true
    && id(snap.context?.player?.id)
    && Number.isFinite(snap.context.frameTime) && snap.context.frameTime >= 0
    && Number.isFinite(snap.context.realTime) && snap.context.realTime >= 0,
    'QUEST_CONTEXT_UNBOUND');
  const observationalCounters = new Set(['questEntriesScanned', 'questsRetained',
    'objectiveEntriesScanned', 'objectivesRetained', 'indicatorEntriesScanned',
    'indicatorsRetained', 'mapReads', 'textBytesRetained']);
  if (snap.complete) requireValue(Object.entries(snap.counts).every(([key, value]) =>
    observationalCounters.has(key) || value === 0), 'QUEST_COMPLETENESS_CONTRADICTION');
  requireValue(snap.counts.questsRetained === quests.length, 'QUEST_COUNT_MISMATCH');
  const seen = new Set(), journal = [], nextObjectives = [];
  let objectiveCount = 0, indicatorCount = 0, textBytes = 0;
  const text = value => {
    const result = optionalText(value);
    textBytes += result === null ? 0 : Buffer.byteLength(result);
    requireValue(textBytes <= 131072, 'QUEST_TEXT_BUDGET');
    return result;
  };
  for (const quest of quests) {
    requireValue(object(quest) && id(quest.id) && !seen.has(token(quest.id)), 'QUEST_ID_SHAPE');
    seen.add(token(quest.id));
    const objectives = dense(quest.objectives, 32);
    objectiveCount += objectives.length;
    const identityMatches = quest.status === 'returned' && quest.sourceId === quest.id;
    const row = {id: quest.id, name: text(quest.name),
      status: ['returned', 'missing-api', 'error', 'no-detail', 'invalid-detail',
        'missing-identity', 'id-mismatch'].includes(quest.status) ? quest.status : null,
      complete: typeof quest.complete === 'boolean' ? quest.complete : null,
      failed: typeof quest.failed === 'boolean' ? quest.failed : null,
      tracked: quest.track === true, watched: quest.watch === true,
      objectives: []};
    const objectiveKeys = new Set();
    for (const objective of objectives) {
      requireValue(object(objective) && id(objective.key)
        && !objectiveKeys.has(token(objective.key)), 'QUEST_OBJECTIVE_SHAPE');
      objectiveKeys.add(token(objective.key));
      for (const field of ['count', 'countDone']) if (Object.hasOwn(objective, field))
        requireValue(integer(objective[field]), 'QUEST_OBJECTIVE_COUNT');
      if (Object.hasOwn(objective, 'complete'))
        requireValue(typeof objective.complete === 'boolean', 'QUEST_OBJECTIVE_COMPLETE');
      const countsKnown = integer(objective.count) && integer(objective.countDone);
      requireValue(!countsKnown || objective.countDone <= objective.count, 'QUEST_OBJECTIVE_COUNT');
      const remaining = countsKnown ? objective.count - objective.countDone : null;
      const state = objective.complete === true ? 'complete'
        : objective.complete === false || countsKnown && remaining > 0 ? 'incomplete'
        : 'completion-unknown';
      const entry = {key: objective.key, description: text(objective.description),
        count: objective.count ?? null, countDone: objective.countDone ?? null,
        remaining, state, locations: []};
      const indicators = dense(objective.indicators, 16);
      indicatorCount += indicators.length;
      const indicatorIds = new Set();
      for (const indicator of indicators) {
        requireValue(object(indicator) && id(indicator.id)
          && !indicatorIds.has(token(indicator.id)), 'QUEST_INDICATOR_SHAPE');
        indicatorIds.add(token(indicator.id));
        const location = indicator.location;
        if (identityMatches && indicator.status === 'returned' && object(location)
          && location.sourceId === indicator.id
          && ['coordX', 'coordY', 'coordZ'].every(k => Number.isFinite(location[k]))) {
          entry.locations.push({id: indicator.id, coordX: location.coordX,
            coordY: location.coordY, coordZ: location.coordZ,
            title: text(location.title), description: text(location.description)});
        }
      }
      row.objectives.push(entry);
      if (identityMatches && row.complete !== true && row.failed !== true && state === 'incomplete')
        nextObjectives.push({questId: row.id, questName: row.name, tracked: row.tracked,
          watched: row.watched, ...entry});
    }
    journal.push(row);
  }
  requireValue(objectiveCount <= 512 && indicatorCount <= 512, 'QUEST_GLOBAL_LIMIT');
  requireValue(snap.counts.objectivesRetained === objectiveCount
    && snap.counts.indicatorsRetained === indicatorCount, 'QUEST_COUNT_MISMATCH');
  requireValue(!(snap.status === 'empty' && quests.length !== 0), 'QUEST_EMPTY_CONTRADICTION');
  nextObjectives.sort((a, b) => Number(b.tracked) - Number(a.tracked)
    || Number(b.watched) - Number(a.watched)
    || token(a.questId).localeCompare(token(b.questId), 'en')
    || token(a.key).localeCompare(token(b.key), 'en'));
  const attempt = saved.questAttempt;
  const lastRecordedAttempt = object(attempt) && attempt.addonVersion === VERSION
    && ['recorded', 'partial', 'empty', 'unavailable', 'error'].includes(attempt.status)
    ? {producerVersion: attempt.addonVersion, status: attempt.status} : null;
  return {schemaVersion: 1, producerVersion: snap.addonVersion, sequence: snap.sequence,
    sourceSha256: source.sha256 ?? null, sourceBytes: source.bytes ?? null,
    sourceModifiedAtUtc: source.modifiedAtUtc ?? null,
    status: snap.status, statusScope: 'retained-snapshot', coverageComplete: snap.complete,
    lastRecordedAttempt, journalRetainedAfterFailure: lastRecordedAttempt
      ? ['unavailable', 'error'].includes(lastRecordedAttempt.status) : null,
    qualification: {live: false, freshnessVerified: false, coordinateFrameVerified: false,
      travelFeasibilityVerified: false, completionActionsVerified: false},
    context: {frameTime: Number.isFinite(snap.context?.frameTime) && snap.context.frameTime >= 0
      ? snap.context.frameTime : null,
      realTime: Number.isFinite(snap.context?.realTime) && snap.context.realTime >= 0
        ? snap.context.realTime : null,
      playerId: id(snap.context?.player?.id) ? snap.context.player.id : null,
      zone: scalar(snap.context?.player?.zone)},
    counts: {...snap.counts}, journal, nextObjectives};
}

export function readQuestReceipt(file) {
  requireValue(path.basename(file) === 'RRECollector.lua', 'ONLY_RRECOLLECTOR_SAVED_FILE');
  const original = readStableOriginalWithMetadata(file);
  return summarizeQuestReceipt(parseSavedLuaBytes(original.bytes), {
    sha256: crypto.createHash('sha256').update(original.bytes).digest('hex'),
    bytes: original.bytes.length, modifiedAtUtc: original.modifiedAtUtc});
}

if (process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  try {
    const args = process.argv.slice(2);
    requireValue(args.length === 1 || args.length === 3 && args[1] === '--output', 'QUEST_USAGE');
    const result = readQuestReceipt(args[0]);
    const json = JSON.stringify(result, null, 2) + '\n';
    if (args.length === 3) {
      fs.writeFileSync(args[2], json, {encoding: 'utf8', flag: 'wx'});
      process.stdout.write(JSON.stringify({status: 'written', sourceSha256: result.sourceSha256,
        quests: result.journal.length, nextObjectives: result.nextObjectives.length}) + '\n');
    } else process.stdout.write(json);
  } catch (error) {
    const reason = /^[A-Z][A-Z0-9_]*$/.test(error?.message) ? error.message : 'QUEST_EXPORT_FAILED';
    process.stderr.write(reason + '\n'); process.exitCode = 2;
  }
}
