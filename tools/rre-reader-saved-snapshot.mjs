// Data-only adapter: reuse the existing literal Lua parser and Detail projection.
import path from 'node:path';
import crypto from 'node:crypto';
import {fileURLToPath} from 'node:url';
import {parseSavedLua, assessSnapshotForComparison, buildAbilityCrosswalk} from './read-rrecollector-saved.mjs';
import {readStableOriginal, MAX_ORIGINAL_BYTES} from './read-stable-original.mjs';

export const MAX_BYTES = MAX_ORIGINAL_BYTES;
const sha = b => crypto.createHash('sha256').update(b).digest('hex');
function boundedCopy(value, depth = 0) {
  if (value == null || typeof value === 'boolean') return value;
  if (typeof value === 'string') {
    if (value.length > 4096) throw Error('context-string-limit');
    return value;
  }
  if (typeof value === 'number' && Number.isFinite(value)) return value;
  if (typeof value !== 'object' || depth >= 6) throw Error('context-value-limit');
  const entries = Object.entries(value);
  if (entries.length > 512) throw Error('context-entry-limit');
  const result = Array.isArray(value) ? [] : Object.create(null);
  for (const [key, item] of entries) {
    if (key.length > 128) throw Error('context-key-limit');
    result[key] = boundedCopy(item, depth + 1);
  }
  return result;
}
export function exportSavedSnapshot(bytes) {
  if (!Buffer.isBuffer(bytes) || bytes.length === 0 || bytes.length > MAX_BYTES) throw Error('saved-byte-limit');
  const text = new TextDecoder('utf-8', {fatal:true}).decode(bytes);
  const saved = parseSavedLua(text);
  const structure = assessSnapshotForComparison(saved);
  if (!structure.offlineStructureQualified) throw Error('saved-structure-unqualified:' + structure.reasons.join(','));
  // The historical crosswalk drops non-scalars; reject malformed raw fields first.
  const rawAbilities = Object.values(saved.latest.abilities);
  for (const row of rawAbilities) {
    if (!row || typeof row !== 'object' || Array.isArray(row)) throw Error('ability-record-shape');
    if (!Object.values(row).every(value => typeof value === 'string'
        || typeof value === 'boolean' || typeof value === 'number' && Number.isFinite(value)))
      throw Error('ability-field-not-scalar');
  }
  const crosswalk = buildAbilityCrosswalk(saved, {records:[], catalogVersion:'no-static-catalog'}, sha(bytes));
  // The historical research crosswalk deliberately redacts target IDs. The local
  // reader data contract retains the producer's scalar target without changing it.
  const rawById = new Map(rawAbilities.map(row=>[row.lookupId,row]));
  const abilities = crosswalk.knownOutsideStatic.map(row=>{
    const detail = {...row.currentDetail};
    if (detail.lookupId.length !== 17 || !/^A[0-9A-F]{16}$/.test(detail.lookupId)) throw Error('ability-id-unqualified');
    const original = rawById.get(detail.lookupId);
    if (Object.hasOwn(original,'target')) {
      const target = original.target;
      if (!['string','boolean','number'].includes(typeof target) || typeof target === 'number' && !Number.isFinite(target))
        throw Error('ability-target-not-scalar');
      detail.target = boundedCopy(target);
    }
    return detail;
  });
  const context = Object.create(null);
  for (const key of ['player','target','roleSlot','roleNames','clientVersion','frameTime','realTime','capabilities','scope','stats','statsTruncated']) {
    if (Object.hasOwn(saved.latest,key)) context[key] = boundedCopy(saved.latest[key]);
  }
  // Keep older producer contracts strict. The literal Lua parser represents {}
  // as []; Experience-capable v0.4.14+ may normalize that empty table only.
  const version = saved.latest.addonVersion;
  const capabilities = saved.latest.capabilities;
  const hasMap = Object.hasOwn(saved.latest,'experience');
  const hasFlag = capabilities != null && typeof capabilities === 'object'
    && Object.hasOwn(capabilities,'experience');
  if (version === '0.4.14' || version === '0.4.15' || version === '0.4.16' || version === '0.4.17' || version === '0.4.18' || version === '0.4.19') {
    if (!hasFlag || typeof capabilities.experience !== 'boolean') throw Error('experience-capability-unqualified');
    if (capabilities.experience !== hasMap) throw Error('experience-capability-map-contradiction');
    if (hasMap) {
      const input = saved.latest.experience;
      if (!input || typeof input !== 'object' || Array.isArray(input) && input.length !== 0)
        throw Error('experience-map-shape');
      const entries = Object.entries(input);
      if (entries.length > 3) throw Error('experience-map-limit');
      const result = Object.create(null);
      for (const [key,value] of entries) {
        if (!['accumulated','needed','rested'].includes(key) || typeof value !== 'number' || !Number.isFinite(value))
          throw Error('experience-field-unqualified');
        result[key] = value;
      }
      context.experience = result;
    }
  } else if (hasMap || hasFlag) {
    throw Error('experience-version-unqualified');
  }
  return {adapterContract:'rre-saved-snapshot/1', sourceSha256:sha(bytes), sourceBytes:bytes.length,
    addonVersion:saved.latest.addonVersion, savedAddonVersion:typeof saved.addonVersion === 'string' ? saved.addonVersion : null,
    sequence:saved.latest.sequence,
    abilities, context,
    counts:boundedCopy(saved.latest.abilityList), structure};
}
// Opt-in UI pin audit. Preserve rre-saved-snapshot/1's exact schema for C# consumers.
// Mirrors ui.lua loadSlots: a saved table (even empty) suppresses defaults.
export function summarizeSavedPins(bytes) {
  const snapshot = exportSavedSnapshot(bytes);
  const saved = parseSavedLua(new TextDecoder('utf-8', {fatal:true}).decode(bytes));
  const present = Object.hasOwn(saved,'toolbarSlots');
  const previous = saved.toolbarSlots;
  const persisted = previous !== null && typeof previous === 'object';
  const knownIds = new Set(snapshot.abilities.map(row=>row.lookupId));
  const states = Array(8).fill('empty');
  function labelSlot(slot, id) {
    if (typeof id !== 'string' || Buffer.byteLength(id,'utf8') > 128) {
      states[slot] = 'invalid';
    } else {
      states[slot] = knownIds.has(id) ? 'matched' : 'missing';
    }
  }
  if (persisted) {
    for (let slot=0;slot<8;slot++) {
      const value = Array.isArray(previous) ? previous[slot] : previous[String(slot+1)];
      if (value !== undefined) labelSlot(slot,value);
    }
  } else {
    let slot=0;
    for (const row of Object.values(saved.latest.abilities)) {
      if (slot === 8) break;
      if (row && typeof row.lookupId === 'string' && row.passive !== true) {
        labelSlot(slot,row.lookupId);
        slot++;
      }
    }
  }
  const count = status=>states.filter(value=>value === status).length;
  return {
    adapterContract:'rre-saved-pins/1', sourceSha256:snapshot.sourceSha256,
    captureVersion:snapshot.addonVersion, sequence:snapshot.sequence,
    mode:persisted ? 'persisted' : 'auto-defaults',
    savedField:!present ? 'absent' : persisted ? 'table' : 'non-table',
    pinCount:count('matched')+count('missing'),
    matchedCount:count('matched'), missingCount:count('missing'),
    invalidCount:count('invalid'), slotStates:states
  };
}
// Preserve the existing exported reader contract while sharing one guarded implementation.
export const readBoundedSaved = readStableOriginal;
// CLI diagnostics must not expose user account paths or untrusted Lua source.
const CLI_USAGE = 'usage: node tools/rre-reader-saved-snapshot.mjs FILE [--pins]';
const SAFE_REASONS = new Set([
  'saved-byte-limit', 'saved-source-not-plain-file',
  'saved-source-changed-before-read', 'saved-source-changed-during-read',
  'ability-record-shape', 'ability-field-not-scalar', 'ability-id-unqualified',
  'ability-target-not-scalar', 'context-string-limit', 'context-value-limit',
  'context-entry-limit', 'context-key-limit', 'experience-capability-unqualified',
  'experience-capability-map-contradiction', 'experience-map-shape',
  'experience-map-limit', 'experience-field-unqualified', 'experience-version-unqualified'
]);
export function savedCliErrorReason(error) {
  if (error?.code === 'ENOENT') return 'saved-file-not-found';
  if (error?.code === 'EPERM' || error?.code === 'EACCES') return 'saved-file-unreadable';
  const message = String(error?.message || '');
  if (message === CLI_USAGE || SAFE_REASONS.has(message)) return message;
  if (message.startsWith('saved-structure-unqualified:')) return 'saved-structure-unqualified';
  return 'saved-input-invalid';
}
if (process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  try {
    if (process.argv.length !== 3 && (process.argv.length !== 4 || process.argv[3] !== '--pins'))
      throw Error(CLI_USAGE);
    const bytes = readBoundedSaved(process.argv[2]);
    const result = process.argv.length === 4 ? summarizeSavedPins(bytes) : exportSavedSnapshot(bytes);
    process.stdout.write(JSON.stringify(result) + '\n');
  } catch (error) {
    process.stderr.write(JSON.stringify({error:savedCliErrorReason(error)}) + '\n');
    process.exitCode = 2;
  }
}
