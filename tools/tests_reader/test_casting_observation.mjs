import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import crypto from 'node:crypto';
import {spawnSync} from 'node:child_process';
import {parseSavedLua, parseSavedLuaBytes} from '../read-rrecollector-saved.mjs';
import {readStableOriginalWithMetadata, MAX_CASTING_BYTES} from '../read-stable-original.mjs';
import {assessCastingTrial, summarizeCastingEvidence, readCastingEvidence}
  from '../rre-casting-observation.mjs';

const ABILITY = 'A1111111111111111', MODERN = 'A2222222222222222';
function sample(sequence = 1, at = 100) {
  return {sequence, clock: at, playerId: 'uPLAYER', targetId: 'uTARGET', abilityId: ABILITY,
    player: {id: 'uPLAYER', health: 100, power: 30, combat: false},
    target: {id: 'uTARGET', health: 100, relation: 'hostile'},
    ability: {idNew: MODERN, name: 'Fixture', target: 'uTARGET', costPower: 0,
      currentCooldownRemaining: 0, unusable: false, outOfRange: false},
    status: sequence === 1 ? 'ready' : 'waiting', reason: 'observed-ready'};
}
function event() {
  return {kind: 'damage', clock: 105, caster: 'uPLAYER', target: 'uTARGET',
    ability: ABILITY, abilityNew: MODERN, normalizedAbilityId: MODERN,
    abilityMappingSource: 'Event.Combat.abilityNew', damage: 10,
    matchesAbility: true, matchesTarget: true};
}
function trial() {
  return {status: 'finished', started: 100, deadline: 160, playerId: 'uPLAYER',
    targetId: 'uTARGET', abilityId: ABILITY, abilityNewId: MODERN, abilityName: 'Fixture',
    samples: [sample()], events: [event()], cooldowns: [], hit: true,
    healingConfirmed: false, overhealObserved: false, reason: 'intended-hit-confirmed'};
}
function root(t = trial()) {
  return {schemaVersion: 1, addonVersion: '0.4.0', source: 'RIFT Lua API',
    trials: [t], previousTrials: [], last: sample(), trial: t};
}
const damage = t => assessCastingTrial(t).outcome === 'exact-target-damage';
function lua(value) {
  if (value === null) return 'nil';
  if (Array.isArray(value)) return '{' + value.map(lua).join(',') + '}';
  if (value !== null && typeof value === 'object') return '{' + Object.entries(value)
    .map(([key, x]) => '[' + JSON.stringify(key) + ']=' + lua(x)).join(',') + '}';
  return JSON.stringify(value);
}
const saved = value => 'RiftReader2CastingEvidence=' + lua(value);
function temporary(t) {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'rre-casting-'));
  assert.equal(path.dirname(path.resolve(dir)), path.resolve(os.tmpdir()));
  assert.ok(path.basename(dir).startsWith('rre-casting-'));
  t.after(() => fs.rmSync(dir, {recursive: true, force: true}));
  return dir;
}

test('exact caster/ability/target damage is distinguished from execution authority', () => {
  const result = summarizeCastingEvidence(root());
  assert.equal(result.trials[0].outcome, 'exact-target-damage');
  assert.equal(result.trials[0].positiveExamples.damage.amount, 10);
  assert.equal(result.trials[0].observationFinished, true);
  for (const flag of ['live', 'freshnessVerified', 'castDeliveryVerified', 'currentActionAuthorized'])
    assert.equal(result.qualification[flag], false);
});
test('wrong, absent or invalid modern ID cannot fall back to the correct raw ID', () => {
  for (const modern of ['A3333333333333333', true, 1, '']) {
    const t = trial(); t.events[0].abilityNew = modern;
    assert.equal(damage(t), false);
  }
  const t = trial(); delete t.events[0].abilityNew;
  assert.equal(damage(t), false, 'modern marker preserves omitted raw value');
});
test('legacy exact IDs and observation-time mappings work, current reconciliation does not', () => {
  const t = trial(); delete t.events[0].abilityNew;
  t.events[0].abilityMappingSource = 'Inspect.Ability.New.Detail';
  assert.equal(damage(t), true);
  t.events[0].ability = 'rawOTHER';
  assert.equal(damage(t), true, 'captured normalized ID binds the legacy event');
  delete t.events[0].normalizedAbilityId;
  const r = root(t); r.abilityMappings = {rawOTHER: {New: {idNew: MODERN}}};
  assert.notEqual(summarizeCastingEvidence(r).trials[0].outcome, 'exact-target-damage');
});
test('wrong caster, wrong target and same-name/different-ID events never confirm', () => {
  for (const key of ['caster', 'target']) {
    const t = trial(); t.events[0][key] = 'uOTHER'; assert.equal(damage(t), false);
  }
  const t = trial(); t.events[0].abilityNew = 'other'; t.events[0].abilityName = 'Fixture';
  assert.equal(damage(t), false);
});
test('trial modern identity must be frozen from the initially selected ability Detail', () => {
  const t = trial(); t.abilityNewId = 'A3333333333333333';
  t.events[0].abilityNew = t.events[0].normalizedAbilityId = t.abilityNewId;
  const result = assessCastingTrial(t);
  assert.equal(result.outcome, 'inconclusive');
  assert.ok(result.issues.includes('initial-ability-or-target-unbound'));
});
test('initial ability target must bind the exact selected trial target', () => {
  const t = trial(); t.samples[0].ability.target = 'uOTHER';
  assert.equal(assessCastingTrial(t).structureQualified, false);
});
test('Lua nil is absence and idNew false falls back to id without defeating modern markers', () => {
  for (const value of [null, false]) {
    const t = trial(); t.samples[0].ability.idNew = value; t.samples[0].ability.id = MODERN;
    assert.equal(assessCastingTrial(t).outcome, 'exact-target-damage');
    const decoded = parseSavedLua(saved(root(t)), 'RiftReader2CastingEvidence');
    assert.equal(summarizeCastingEvidence(decoded).trials[0].outcome, 'exact-target-damage');
  }
  const t = trial(); t.events[0].abilityNew = null;
  delete t.events[0].abilityMappingSource;
  assert.equal(assessCastingTrial(t).outcome, 'exact-target-damage');
  t.events[0].abilityMappingSource = 'Event.Combat.abilityNew';
  assert.equal(assessCastingTrial(t).outcome, 'inconclusive');
});
test('zero, negative, string, nonfinite and absorbed-only damage are not hits', () => {
  for (const value of [0, -1, '10', NaN, Infinity]) {
    const t = trial(); t.events[0].damage = value; t.events[0].damageAbsorbed = 10;
    assert.equal(damage(t), false);
  }
});
test('overheal-only does not become effective healing', () => {
  const t = trial(); t.hit = false; t.overhealObserved = true;
  t.reason = 'intended-overheal-observed'; t.events[0] = {...event(), kind: 'heal', heal: 0, overheal: 15};
  const r = assessCastingTrial(t);
  assert.equal(r.outcome, 'overheal-only'); assert.equal(r.positiveExamples.heal, undefined);
});
test('matched combat failures and cooldown/castbar do not become positive damage', () => {
  for (const kind of ['miss', 'dodge', 'parry', 'resist', 'immune']) {
    const t = trial(); t.hit = false; t.reason = 'no-matching-outcome-observed';
    t.events[0].kind = kind; t.samples[0].cast = {ability: ABILITY};
    t.cooldowns = [{kind: 'Begin', clock: 104, remaining: 1.5, abilityId: ABILITY}];
    const r = assessCastingTrial(t); assert.equal(r.outcome, 'matched-combat-failure');
    assert.deepEqual(r.matchedFailureKinds, [kind]);
  }
});
test('event-window boundaries are inclusive and events outside cannot confirm', () => {
  for (const clock of [100, 160]) {
    const t = trial(); t.events[0].clock = clock; assert.equal(damage(t), true);
  }
  for (const clock of [99.99, 160.01]) {
    const t = trial(); t.events[0].clock = clock; assert.equal(damage(t), false);
  }
});
test('abort/recording status does not hide prior positive evidence or imply a finished observation', () => {
  for (const status of ['aborted', 'recording']) {
    const t = trial(); t.status = status; t.reason = 'target-or-player-changed';
    const r = assessCastingTrial(t);
    assert.equal(r.outcome, 'exact-target-damage'); assert.equal(r.observationFinished, false);
  }
});
test('uncorroborated producer flags or positive reasons are inconclusive', () => {
  const t = trial(); t.events = [];
  assert.equal(assessCastingTrial(t).outcome, 'inconclusive');
  assert.ok(assessCastingTrial(t).uncorroboratedProducerFlags.includes('hit'));
  delete t.hit;
  assert.equal(assessCastingTrial(t).outcome, 'inconclusive', 'positive reason alone cannot confirm');
});
test('valid lastHit survives capped unrelated events but wrong-slot events are unqualified', () => {
  const t = trial(); t.events = Array.from({length: 64}, (_, i) => ({...event(),
    clock: 100 + i * 0.5, abilityNew: 'other'}));
  t.eventsTruncated = true; t.lastHit = {...event(), clock: 159};
  const r = assessCastingTrial(t);
  assert.equal(r.outcome, 'exact-target-damage'); assert.equal(r.positiveExamples.damage.source, 'lastHit');
  t.lastHit = {...event(), kind: 'heal', heal: 5};
  assert.equal(assessCastingTrial(t).outcome, 'inconclusive');
  assert.equal(assessCastingTrial(t).structureQualified, false);
});
test('no matching event in a capped list stays inconclusive', () => {
  const t = trial(); t.hit = false; t.reason = 'no-matching-outcome-observed';
  t.events = []; t.eventsTruncated = true;
  assert.equal(assessCastingTrial(t).outcome, 'inconclusive');
});
test('root latest-trial alias is not counted twice; archived provenance stays unknown', () => {
  const r = root(); r.previousTrials = [trial()];
  const result = summarizeCastingEvidence(r);
  assert.equal(result.trials.length, 1); assert.equal(result.previousTrials.length, 1);
  assert.equal(result.latestTrialAliasIgnored, true);
  assert.equal(result.previousTrials[0].producerVersionAtTrial, 'unknown');
});
test('readout failure retains reviewable completed trials', () => {
  const r = root(); r.last = {status: 'unavailable', reason: 'readout-update-failed'};
  const result = summarizeCastingEvidence(r);
  assert.equal(result.latestSample, null);
  assert.equal(result.latestSampleStatus, 'readout-update-failed');
  assert.equal(result.trials[0].outcome, 'exact-target-damage');
});
test('unknown older archive shapes cannot erase current-load observations', () => {
  const r = root(); r.previousTrials = [{status: 'finished', started: 10, deadline: 40}];
  const result = summarizeCastingEvidence(r);
  assert.equal(result.trials[0].outcome, 'exact-target-damage');
  assert.equal(result.previousTrials[0].outcome, 'inconclusive');
  assert.equal(result.previousTrials[0].producerVersionAtTrial, 'unknown');
  assert.deepEqual(result.previousTrials[0].issues, ['unsupported-historical-shape']);
});
test('numeric/bool fields and controlled reason enums cannot emit arbitrary text', () => {
  const r = root(); const marker = 'PRIVATE_NUMERIC_FIELD_MARKER';
  r.last.player.health = marker; r.last.player.combat = marker;
  r.last.ability.currentCooldownRemaining = marker; r.last.reason = marker;
  r.trials[0].events[0].abilityMappingSource = marker;
  assert.equal(JSON.stringify(summarizeCastingEvidence(r)).includes(marker), false);
});
test('clock/sequence regression, changed sample identity and cooldown binding stay unqualified', () => {
  for (const mutate of [t => t.samples.push(sample(1, 101)),
    t => { const s = sample(2, 101); s.targetId = 'uOTHER'; t.samples.push(s); },
    t => t.cooldowns.push({kind: 'Begin', clock: 161, remaining: 1, abilityId: ABILITY}),
    t => t.events.push({...event(), clock: 104})]) {
    const t = trial(); mutate(t);
    assert.equal(assessCastingTrial(t).structureQualified, false);
    assert.equal(assessCastingTrial(t).outcome, 'inconclusive');
  }
});
test('empty observer remains no-trials and malformed dense arrays/contracts are rejected', () => {
  const r = root(); r.trials = []; delete r.trial;
  assert.equal(summarizeCastingEvidence(r).status, 'no-trials');
  r.trials = {2: trial()};
  assert.throws(() => summarizeCastingEvidence(r), /ARRAY_LIMIT_OR_HOLE/);
  r.trials = []; r.addonVersion = '0.3.0';
  assert.throws(() => summarizeCastingEvidence(r), /PRODUCER_CONTRACT/);
});
test('literal parser defaults stay strict and no executable Lua or duplicate key is accepted', () => {
  assert.throws(() => parseSavedLua(saved(root())), /unexpected SavedVariables assignment/);
  assert.throws(() => parseSavedLua('RRECollectorData={}', 'arbitrary'), /Unsupported/);
  assert.equal(parseSavedLua(saved(root()), 'RiftReader2CastingEvidence').trials.length, 1);
  for (const code of ['RiftReader2CastingEvidence=(function() return {} end)()',
    'RiftReader2CastingEvidence={schemaVersion=1,schemaVersion=1}'])
    assert.throws(() => parseSavedLua(code, 'RiftReader2CastingEvidence'));
  assert.throws(() => parseSavedLuaBytes(Buffer.from([0xff]), 'RiftReader2CastingEvidence'));
});
test('full 16-trial recordings exceed old limits and remain bounded casting inputs', t => {
  const r = root(); r.trials = []; r.previousTrials = []; delete r.trial;
  for (let i = 0; i < 16; i++) {
    const v = trial(); v.samples = Array.from({length: 630}, (_, j) => sample(j + 1, 100 + j * 0.09));
    (i < 8 ? r.trials : r.previousTrials).push(v);
  }
  const file = path.join(temporary(t), 'RiftReader2Casting.lua');
  const bytes = Buffer.from(saved(r)); assert.ok(bytes.length > 2_000_000 && bytes.length < MAX_CASTING_BYTES);
  fs.writeFileSync(file, bytes);
  assert.throws(() => readStableOriginalWithMetadata(file), /saved-byte-limit/);
  const result = readCastingEvidence(file);
  assert.equal(result.trials.length, 8); assert.equal(result.previousTrials.length, 8);
  assert.equal(result.trials[0].limitsReached.samples, true);
  assert.equal(result.sourceSha256, crypto.createHash('sha256').update(bytes).digest('hex'));
});
test('CLI hashes original bytes, refuses overwrite and hides unavailable private paths', t => {
  const dir = temporary(t), file = path.join(dir, 'RiftReader2Casting.lua'), out = path.join(dir, 'combat.json');
  fs.writeFileSync(file, saved(root()));
  const cli = path.resolve('tools/rre-casting-observation.mjs');
  const run = args => spawnSync(process.execPath, [cli, ...args], {encoding: 'utf8'});
  assert.equal(run([file, '--output', out]).status, 0);
  const original = fs.readFileSync(out);
  assert.equal(run([file, '--output', out]).status, 2); assert.deepEqual(fs.readFileSync(out), original);
  const missing = run([path.join(dir, 'private@example.invalid', 'RiftReader2Casting.lua')]);
  assert.equal(missing.status, 2); assert.equal(missing.stdout, '');
  assert.equal(missing.stderr.includes('private@example.invalid'), false);
});
