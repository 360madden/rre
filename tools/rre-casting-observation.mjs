// RC-84: file-only combat feedback from the existing casting observer.
// Parses literal Lua, never loads addon code or sends a gameplay command.
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import {fileURLToPath} from 'node:url';
import {parseSavedLuaBytes} from './read-rrecollector-saved.mjs';
import {readStableOriginalWithMetadata, MAX_CASTING_BYTES} from './read-stable-original.mjs';

const requireValue = (okay, code) => { if (!okay) throw Error(code); };
const object = x => x !== null && typeof x === 'object' && !Array.isArray(x);
const finite = x => typeof x === 'number' && Number.isFinite(x);
const clock = x => finite(x) && x >= 0;
const id = x => typeof x === 'string' && x.length > 0 && Buffer.byteLength(x) <= 128
  && !/[\x00-\x1f\x7f]/.test(x);
const text = x => typeof x === 'string' && Buffer.byteLength(x) <= 2048 ? x : null;
// The literal decoder represents explicit Lua nil as null. It is absent for
// producer precedence/optional-field rules, unlike false/zero/empty strings.
const own = (o, key) => Object.hasOwn(o, key) && o[key] !== null;
const EVENT_KINDS = new Set(['damage', 'heal', 'miss', 'immune', 'resist', 'dodge', 'parry']);
const SAMPLE_STATES = new Set(['ready', 'blocked', 'waiting']);
const MAP_SOURCES = new Set(['Inspect.Ability.New.Detail', 'Inspect.Ability.Detail']);
const REASONS = new Set(['unavailable', 'player-unavailable', 'no-target', 'select-ability',
  'identity-changed', 'player-not-alive', 'target-not-alive', 'unsupported-ability-type',
  'ability-target-mismatch', 'out-of-range', 'cast-state-unavailable', 'invalid-cooldown',
  'cooldown-paused', 'cooldown-ability-or-gcd', 'cast-or-channel-active', 'ability-unusable',
  'observed-ready', 'invalid-ability-cost', 'clock-invalid', 'target-or-player-changed',
  'readout-update-failed', 'intended-hit-confirmed', 'intended-heal-confirmed',
  'intended-overheal-observed', 'no-matching-outcome-observed',
  ...['power', 'mana', 'energy', 'charge', 'spirit', 'planar'].map(x => 'insufficient-or-unknown-' + x)]);
const reason = x => REASONS.has(x) ? x : null;
const BOOLEAN_FIELDS = new Set(['combat', 'player', 'unusable', 'outOfRange', 'currentCooldownPaused']);

function dense(value, max) {
  requireValue(value !== null && typeof value === 'object', 'CASTING_ARRAY_SHAPE');
  const keys = Object.keys(value);
  requireValue(keys.length <= max && (Array.isArray(value)
    ? keys.length === value.length && keys.every((key, i) => key === String(i))
    : keys.every((key, i) => key === String(i + 1))), 'CASTING_ARRAY_LIMIT_OR_HOLE');
  return Array.isArray(value) ? value : keys.map(key => value[key]);
}
function scalarProjection(value, fields) {
  const result = {};
  if (!object(value)) return result;
  for (const key of fields) {
    const x = value[key];
    if (BOOLEAN_FIELDS.has(key) ? typeof x === 'boolean'
      : key === 'target' ? id(x)
      : key === 'relation' ? ['friendly', 'hostile', 'neutral'].includes(x)
      : finite(x)) result[key] = x;
  }
  return result;
}
function sampleSummary(sample) {
  if (!object(sample)) return null;
  requireValue(Number.isSafeInteger(sample.sequence) && sample.sequence > 0
    && clock(sample.clock) && SAMPLE_STATES.has(sample.status), 'CASTING_SAMPLE_SHAPE');
  return {sequence: sample.sequence, clock: sample.clock,
    playerId: id(sample.playerId) ? sample.playerId : null,
    targetId: id(sample.targetId) ? sample.targetId : null,
    abilityId: id(sample.abilityId) ? sample.abilityId : null,
    reportedStatus: sample.status, reportedReason: reason(sample.reason),
    player: scalarProjection(sample.player, ['health', 'healthMax', 'power', 'mana', 'energy',
      'charge', 'spirit', 'planar', 'combo', 'combat']),
    target: scalarProjection(sample.target, ['health', 'healthMax', 'relation', 'player', 'combat']),
    ability: scalarProjection(sample.ability, ['target', 'unusable', 'outOfRange',
      'currentCooldownRemaining', 'currentCooldownPaused', 'costPower', 'costMana',
      'costEnergy', 'costCharge', 'costSpirit', 'costPlanarCharge']),
    facingAndLineOfSight: 'unverified'};
}

export function eventMatchesAbility(event, trial) {
  // The marker preserves modern-ID presence even if an unsupported raw value
  // disappeared during the producer's scalar projection. Never rescue it.
  const modern = own(event, 'abilityNew') || event.abilityMappingSource === 'Event.Combat.abilityNew';
  if (modern) return id(event.abilityNew) && id(trial.abilityNewId)
    && event.abilityNew === trial.abilityNewId
    && (!own(event, 'normalizedAbilityId') || event.normalizedAbilityId === event.abilityNew);
  if (!id(event.ability)) return false;
  if (event.ability === trial.abilityId || id(trial.abilityNewId) && event.ability === trial.abilityNewId)
    return true;
  return MAP_SOURCES.has(event.abilityMappingSource) && id(trial.abilityNewId)
    && event.normalizedAbilityId === trial.abilityNewId;
}

export function assessCastingTrial(trial, origin = 'current-load', index = 0) {
  requireValue(object(trial), 'CASTING_TRIAL_SHAPE');
  requireValue(['recording', 'finished', 'aborted'].includes(trial.status), 'CASTING_TRIAL_STATUS');
  requireValue(id(trial.playerId) && id(trial.targetId) && id(trial.abilityId)
    && (!own(trial, 'abilityNewId') || id(trial.abilityNewId)), 'CASTING_TRIAL_IDENTITY');
  requireValue(clock(trial.started) && clock(trial.deadline) && trial.deadline > trial.started
    && Math.abs(trial.deadline - trial.started - 60) <= 0.001, 'CASTING_TRIAL_WINDOW');
  const samples = dense(trial.samples, 630), events = dense(trial.events, 64);
  const cooldowns = dense(trial.cooldowns, 64);
  const issues = [], ignored = {outsideWindow: 0, otherCaster: 0, otherTarget: 0,
    otherAbility: 0, unsupportedKind: 0, contradictoryMatchFlag: 0};
  if (samples.length === 0) issues.push('initial-sample-missing');
  let lastClock = trial.started, lastSequence = 0;
  for (const sample of samples) {
    const summary = sampleSummary(sample);
    requireValue(summary !== null, 'CASTING_SAMPLE_SHAPE');
    if (summary.playerId !== trial.playerId || summary.targetId !== trial.targetId
      || summary.abilityId !== trial.abilityId) issues.push('sample-identity-unbound');
    if (summary.clock < trial.started || summary.clock > trial.deadline
      || summary.clock < lastClock || summary.sequence <= lastSequence) issues.push('sample-clock-or-sequence-unbound');
    lastClock = summary.clock; lastSequence = summary.sequence;
  }
  if (samples.length && (samples[0].status !== 'ready' || samples[0].clock !== trial.started))
    issues.push('initial-readiness-unbound');
  if (samples.length) {
    const ability = object(samples[0].ability) ? samples[0].ability : {};
    // Lua's `or` treats only nil/false as absent. Bind the frozen modern ID to
    // the exact Detail record selected at Begin, not merely later event labels.
    const initialNewId = own(ability, 'idNew') && ability.idNew !== false ? ability.idNew : ability.id;
    if ((initialNewId ?? null) !== (trial.abilityNewId ?? null) || ability.target !== trial.targetId)
      issues.push('initial-ability-or-target-unbound');
  }
  let previousEventClock = trial.started;
  for (const event of events) {
    requireValue(object(event), 'CASTING_EVENT_SHAPE');
    if (clock(event.clock) && event.clock < previousEventClock) issues.push('event-clock-regression');
    if (clock(event.clock)) previousEventClock = event.clock;
  }
  for (const row of cooldowns) {
    requireValue(object(row) && clock(row.clock) && finite(row.remaining)
      && ['Begin', 'End'].includes(row.kind) && id(row.abilityId), 'CASTING_COOLDOWN_SHAPE');
    if (row.clock < trial.started || row.clock > trial.deadline
      || row.abilityId !== trial.abilityId) issues.push('cooldown-binding-unqualified');
  }
  if (own(trial, 'eventsTruncated')) requireValue(typeof trial.eventsTruncated === 'boolean', 'CASTING_TRUNCATION_SHAPE');
  for (const key of ['hit', 'healingConfirmed', 'overhealObserved'])
    if (own(trial, key)) requireValue(typeof trial[key] === 'boolean', 'CASTING_OUTCOME_FLAG_SHAPE');
  const candidates = events.map(event => ({event, source: 'events'}));
  for (const key of ['lastHit', 'lastHeal']) if (own(trial, key)) {
    requireValue(object(trial[key]), 'CASTING_LAST_EVENT_SHAPE');
    if (key === 'lastHit'
      ? trial[key].kind !== 'damage' || !finite(trial[key].damage) || trial[key].damage <= 0
      : trial[key].kind !== 'heal' || !((finite(trial[key].heal) && trial[key].heal > 0)
        || (finite(trial[key].overheal) && trial[key].overheal > 0))) {
      issues.push('last-event-slot-contradiction'); continue;
    }
    candidates.push({event: trial[key], source: key});
  }
  const examples = {}, failures = new Set();
  for (const {event, source} of candidates) {
    for (const key of ['matchesTarget', 'matchesAbility'])
      if (own(event, key)) requireValue(typeof event[key] === 'boolean', 'CASTING_MATCH_FLAG_SHAPE');
    if (!clock(event.clock) || event.clock < trial.started || event.clock > trial.deadline) {
      ignored.outsideWindow++; continue;
    }
    if (!EVENT_KINDS.has(event.kind)) { ignored.unsupportedKind++; continue; }
    if (event.caster !== trial.playerId) { ignored.otherCaster++; continue; }
    if (event.target !== trial.targetId) { ignored.otherTarget++; continue; }
    if (!eventMatchesAbility(event, trial)) { ignored.otherAbility++; continue; }
    if (event.matchesTarget === false || event.matchesAbility === false) {
      ignored.contradictoryMatchFlag++; continue;
    }
    const example = {source, clock: event.clock, caster: event.caster, target: event.target,
      ability: id(event.ability) ? event.ability : null,
      abilityNew: id(event.abilityNew) ? event.abilityNew : null,
      normalizedAbilityId: id(event.normalizedAbilityId) ? event.normalizedAbilityId : null,
      abilityMappingSource: MAP_SOURCES.has(event.abilityMappingSource)
        || event.abilityMappingSource === 'Event.Combat.abilityNew' ? event.abilityMappingSource : null};
    if (event.kind === 'damage' && finite(event.damage) && event.damage > 0)
      examples.damage = {...example, kind: 'damage', amount: event.damage};
    else if (event.kind === 'heal') {
      if (finite(event.heal) && event.heal > 0) examples.heal = {...example, kind: 'heal', amount: event.heal};
      if (finite(event.overheal) && event.overheal > 0)
        examples.overheal = {...example, kind: 'overheal', amount: event.overheal};
    } else if (event.kind !== 'damage') failures.add(event.kind);
  }
  for (const [key, example] of [['hit', 'damage'], ['healingConfirmed', 'heal'], ['overhealObserved', 'overheal']])
    if (trial[key] === false && examples[example]) issues.push('producer-flag-event-contradiction');
  const structureQualified = issues.length === 0;
  // A positive event may precede a later abort. Preserve that observation and
  // report observation completion separately, without granting action authority.
  let outcome = !structureQualified ? 'inconclusive'
    : examples.damage ? 'exact-target-damage'
    : examples.heal ? 'exact-target-heal'
    : examples.overheal ? 'overheal-only'
    : failures.size ? 'matched-combat-failure'
    : trial.eventsTruncated === true || events.length === 64 ? 'inconclusive'
    : trial.status === 'finished' ? 'no-matching-outcome-observed' : 'incomplete-observation';
  const uncorroborated = [];
  if (trial.hit === true && !examples.damage) uncorroborated.push('hit');
  if (trial.healingConfirmed === true && !examples.heal) uncorroborated.push('healingConfirmed');
  if (trial.overhealObserved === true && !examples.overheal) uncorroborated.push('overhealObserved');
  for (const [reported, example] of [['intended-hit-confirmed', 'damage'],
    ['intended-heal-confirmed', 'heal'], ['intended-overheal-observed', 'overheal']])
    if (trial.reason === reported && !examples[example]) uncorroborated.push('reportedReason');
  if (uncorroborated.length) outcome = 'inconclusive';
  return {origin, index, playerId: trial.playerId, targetId: trial.targetId,
    abilityId: trial.abilityId, abilityNewId: trial.abilityNewId ?? null,
    abilityName: text(trial.abilityName), started: trial.started, deadline: trial.deadline,
    status: trial.status, reportedReason: reason(trial.reason), structureQualified,
    observationFinished: structureQualified && trial.status === 'finished',
    outcome, issues: [...new Set(issues)], uncorroboratedProducerFlags: uncorroborated,
    positiveExamples: structureQualified ? examples : {}, matchedFailureKinds: [...failures].sort(),
    retained: {samples: samples.length, events: events.length, cooldowns: cooldowns.length},
    limitsReached: {samples: samples.length === 630, events: events.length === 64,
      cooldowns: cooldowns.length === 64, declaredEventsTruncated: trial.eventsTruncated === true},
    ignoredEvents: ignored, firstSample: samples.length ? sampleSummary(samples[0]) : null,
    lastSample: samples.length ? sampleSummary(samples.at(-1)) : null,
    producerVersionAtTrial: origin === 'current-load' ? '0.4.0' : 'unknown'};
}

export function summarizeCastingEvidence(saved, source = {}) {
  requireValue(object(saved) && saved.schemaVersion === 1 && saved.source === 'RIFT Lua API'
    && saved.addonVersion === '0.4.0', 'CASTING_PRODUCER_CONTRACT');
  const current = dense(saved.trials, 8);
  const archived = own(saved, 'previousTrials') ? dense(saved.previousTrials, 8) : [];
  const trials = current.map((trial, index) => assessCastingTrial(trial, 'current-load', index));
  const previousTrials = archived.map((trial, index) => {
    try { return assessCastingTrial(trial, 'archived', index); }
    catch (error) {
      if (!/^CASTING_[A-Z_]+$/.test(error?.message)) throw error;
      // The root version belongs to this load; old archives were copied as-is.
      // An older trial shape must not erase valid current-load observations.
      return {origin: 'archived', index, producerVersionAtTrial: 'unknown',
        structureQualified: false, observationFinished: false, outcome: 'inconclusive',
        issues: ['unsupported-historical-shape'], validationReason: error.message};
    }
  });
  const unavailableLast = object(saved.last) && saved.last.status === 'unavailable'
    && saved.last.reason === 'readout-update-failed';
  return {adapterContract: 'rre-casting-evidence/1', producer: 'RiftReader2Casting',
    producerVersion: saved.addonVersion, sourceSha256: source.sha256 ?? null,
    sourceBytes: source.bytes ?? null, sourceModifiedAtUtc: source.modifiedAtUtc ?? null,
    status: current.length || archived.length ? 'observations-available' : 'no-trials',
    trials, previousTrials, latestSample: own(saved, 'last') && !unavailableLast ? sampleSummary(saved.last) : null,
    latestSampleStatus: unavailableLast ? 'readout-update-failed'
      : own(saved, 'last') ? 'reported-sample' : 'missing',
    latestTrialAliasIgnored: own(saved, 'trial'),
    qualification: {offlineStructureVerified: true, live: false, freshnessVerified: false,
      processBuildVerified: false, sourceAuthenticityVerified: false,
      castDeliveryVerified: false, eventHistoryComplete: false,
      currentActionAuthorized: false},
    interpretation: 'Outcomes describe identity-matched records in a persisted file. They do not prove current readiness, cast-command delivery, or a complete event timeline.'};
}

export function readCastingEvidence(file) {
  requireValue(path.basename(file) === 'RiftReader2Casting.lua', 'CASTING_SAVED_FILENAME');
  const original = readStableOriginalWithMetadata(file, MAX_CASTING_BYTES);
  return summarizeCastingEvidence(parseSavedLuaBytes(original.bytes, 'RiftReader2CastingEvidence'), {
    sha256: crypto.createHash('sha256').update(original.bytes).digest('hex'),
    bytes: original.bytes.length, modifiedAtUtc: original.modifiedAtUtc});
}
if (process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  try {
    const args = process.argv.slice(2);
    requireValue(args.length === 1 || args.length === 3 && args[1] === '--output', 'CASTING_USAGE');
    const json = JSON.stringify(readCastingEvidence(args[0])) + '\n';
    if (args.length === 3) fs.writeFileSync(args[2], json, {encoding: 'utf8', flag: 'wx'});
    else process.stdout.write(json);
  } catch (error) {
    const reason = /^[A-Z][A-Z0-9_]*$/.test(error?.message) ? error.message : 'CASTING_SOURCE_UNAVAILABLE';
    process.stderr.write(JSON.stringify({error: reason}) + '\n'); process.exitCode = 2;
  }
}
