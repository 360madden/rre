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
const counterNames = new Set(['questEntriesScanned', 'questsRetained', 'duplicateQuestIds',
  'malformedQuestEntries', 'droppedQuests', 'questScanTruncated', 'objectiveEntriesScanned',
  'objectivesRetained', 'malformedObjectives', 'droppedObjectives', 'objectiveScanTruncated',
  'objectiveBudgetExceeded', 'missingObjectiveTables', 'indicatorEntriesScanned',
  'indicatorsRetained', 'duplicateIndicators', 'malformedIndicators', 'droppedIndicators',
  'indicatorScanTruncated', 'indicatorBudgetExceeded', 'textBytesRetained', 'textBudgetExceeded',
  'mapReads', 'mapLimitReached', 'detailFailures', 'mapFailures', 'fieldErrors',
  'malformedFields', 'truncatedFields', 'contextErrors']);
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
  requireValue(Object.keys(snap.counts).every(key => counterNames.has(key)), 'QUEST_COUNTER_FIELD');
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
    const row = {id: quest.id, name: text(quest.name), identityQualified: identityMatches,
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
        reportedComplete: typeof objective.complete === 'boolean' ? objective.complete : null,
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

// Differences between validated retained records; never action/session proof.
export function compareQuestReceipts(previous, current) {
  const reference = value => ({sourceSha256: value.sourceSha256, sourceBytes: value.sourceBytes,
    sequence: value.sequence, frameTime: value.context.frameTime, realTime: value.context.realTime});
  const reasons = [];
  if (![previous, current].every(value => typeof value.sourceSha256 === 'string'
    && /^[0-9a-f]{64}$/.test(value.sourceSha256) && integer(value.sourceBytes)))
    reasons.push('source-provenance-unavailable');
  else if (previous.sourceSha256 === current.sourceSha256) reasons.push('same-source-bytes');
  if (!previous.coverageComplete || !current.coverageComplete) reasons.push('incomplete-coverage');
  if (!id(previous.context.playerId) || !id(current.context.playerId)
    || previous.context.playerId !== current.context.playerId) reasons.push('player-mismatch-or-unbound');
  if (!(current.sequence > previous.sequence)) reasons.push('sequence-not-advancing');
  for (const clock of ['frameTime', 'realTime'])
    if (!Number.isFinite(previous.context[clock]) || !Number.isFinite(current.context[clock])
      || !(current.context[clock] > previous.context[clock])) reasons.push(clock + '-not-advancing');
  const result = {scope: 'retained-quest-record-changes',
    status: reasons.length ? 'incomparable' : 'comparable', reasons,
    previous: reference(previous), current: reference(current),
    qualification: {live: false, sourceAuthenticityVerified: false, processEpochVerified: false,
      questInstanceContinuityVerified: false, objectiveIdentityVerified: false,
      actionExecutionVerified: false, causedByActionVerified: false},
    summary: {questsAdded: 0, questsAbsent: 0, countAdvanced: 0, countRegressed: 0,
      objectivesUnqualified: 0}, quests: []};
  if (reasons.length) return result;
  const before = new Map(previous.journal.map(quest => [token(quest.id), quest]));
  const after = new Map(current.journal.map(quest => [token(quest.id), quest]));
  const keys = [...new Set([...before.keys(), ...after.keys()])].sort();
  const descriptionCounts = quest => {
    const counts = new Map();
    for (const objective of quest?.objectives ?? [])
      counts.set(objective.description, (counts.get(objective.description) ?? 0) + 1);
    return counts;
  };
  const state = objective => objective ? {count: objective.count, countDone: objective.countDone,
    reportedComplete: objective.reportedComplete} : null;
  for (const key of keys) {
    const old = before.get(key), now = after.get(key);
    const row = {questId: (now ?? old).id,
      presence: !old ? 'current-only' : !now ? 'previous-only' : 'both',
      reportedCompleteBefore: old?.complete ?? null, reportedCompleteAfter: now?.complete ?? null,
      reportedFailedBefore: old?.failed ?? null, reportedFailedAfter: now?.failed ?? null,
      objectives: []};
    if (!old) result.summary.questsAdded++;
    if (!now) result.summary.questsAbsent++;
    const oldObjectives = new Map((old?.objectives ?? []).map(o => [token(o.key), o]));
    const newObjectives = new Map((now?.objectives ?? []).map(o => [token(o.key), o]));
    const oldDescriptions = descriptionCounts(old), newDescriptions = descriptionCounts(now);
    for (const objectiveKey of [...new Set([...oldObjectives.keys(), ...newObjectives.keys()])].sort()) {
      const a = oldObjectives.get(objectiveKey), b = newObjectives.get(objectiveKey);
      let reason = null;
      if (!a || !b) reason = !a ? 'current-only' : 'previous-only';
      else if (!old.identityQualified || !now.identityQualified) reason = 'quest-identity-unqualified';
      else if (typeof a.description !== 'string' || !a.description.trim()
        || a.description !== b.description) reason = 'description-changed-or-unknown';
      else if (oldDescriptions.get(a.description) !== 1 || newDescriptions.get(b.description) !== 1)
        reason = 'description-ambiguous';
      else if (!integer(a.count) || a.count !== b.count) reason = 'required-count-changed-or-unknown';
      else if (!integer(a.countDone) || !integer(b.countDone)) reason = 'quantity-unknown';
      const delta = reason ? null : b.countDone - a.countDone;
      const change = {key: (b ?? a).key, description: (b ?? a).description,
        before: state(a), after: state(b), countDoneDelta: delta,
        classification: reason ?? (delta > 0 ? 'count-advanced' : delta < 0 ? 'counter-decreased' : 'unchanged')};
      if (reason) result.summary.objectivesUnqualified++;
      else if (delta > 0) result.summary.countAdvanced++;
      else if (delta < 0) result.summary.countRegressed++;
      row.objectives.push(change);
    }
    result.quests.push(row);
  }
  return result;
}

export function readQuestReceipt(file, previousFile = null) {
  requireValue(path.basename(file) === 'RRECollector.lua', 'ONLY_RRECOLLECTOR_SAVED_FILE');
  const original = readStableOriginalWithMetadata(file);
  const result = summarizeQuestReceipt(parseSavedLuaBytes(original.bytes), {
    sha256: crypto.createHash('sha256').update(original.bytes).digest('hex'),
    bytes: original.bytes.length, modifiedAtUtc: original.modifiedAtUtc});
  if (previousFile !== null) result.comparison = compareQuestReceipts(readQuestReceipt(previousFile), result);
  return result;
}

export function serializeQuestReceipt(result) {
  const json = JSON.stringify(result, null, 2) + '\n';
  requireValue(Buffer.byteLength(json) <= 4_000_000, 'QUEST_OUTPUT_LIMIT');
  return json;
}

if (process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  try {
    const args = process.argv.slice(2);
    requireValue(args.length >= 1 && args.length <= 5 && args.length % 2 === 1, 'QUEST_USAGE');
    const options = new Map();
    for (let i = 1; i < args.length; i += 2) {
      requireValue(['--output', '--previous'].includes(args[i]) && !options.has(args[i]), 'QUEST_USAGE');
      options.set(args[i], args[i + 1]);
    }
    const result = readQuestReceipt(args[0], options.get('--previous') ?? null);
    const json = serializeQuestReceipt(result);
    if (options.has('--output')) {
      fs.writeFileSync(options.get('--output'), json, {encoding: 'utf8', flag: 'wx'});
      process.stdout.write(JSON.stringify({status: 'written', sourceSha256: result.sourceSha256,
        quests: result.journal.length, nextObjectives: result.nextObjectives.length}) + '\n');
    } else process.stdout.write(json);
  } catch (error) {
    const reason = /^[A-Z][A-Z0-9_]*$/.test(error?.message) ? error.message : 'QUEST_EXPORT_FAILED';
    process.stderr.write(reason + '\n'); process.exitCode = 2;
  }
}
