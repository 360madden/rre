// Offline research packet only. Never sends queries or acts on a live game.
import crypto from 'node:crypto';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {readStableOriginalWithMetadata} from './read-stable-original.mjs';
import {CALLINGS} from './inventory-pab-static-abilities.mjs';

export const CATALOG = fileURLToPath(new URL('../docs/RRECOLLECTOR-ALL-CALLINGS-STATIC-CANDIDATES-LOSSLESS-2026-11-21.json', import.meta.url));
export const CATALOG_SHA = '5685fa02b82b9802739f85348dcf1d0514a8b1b3e39353cf80f96135cc36908c';
const MANIFEST_SHA = '898f651e8fd272dc220fe0c32aecbb3e937dac750d6d9b912b1f94ab561eb5bb';
const sha = bytes => crypto.createHash('sha256').update(bytes).digest('hex');
export const MAX_IDS = 8;
const fail = code => { throw new Error(code); };

export function planCandidates({calling, ids, bytes}) {
  // Require explicit IDs, not a sweep, and reject case ambiguity/duplicates.
  if (!CALLINGS.includes(calling)) fail('CALLING_REQUIRED');
  if (!Array.isArray(ids) || ids.length < 1 || ids.length > MAX_IDS)
    fail('ID_COUNT_OUT_OF_RANGE');
  if (ids.some(id => typeof id !== 'string' || !/^A[0-9A-F]{16}$/.test(id)))
    fail('INVALID_ID');
  if (new Set(ids).size !== ids.length) fail('DUPLICATE_REQUEST_ID');
  // Do not accept alternative or republished data under the original evidence pin.
  if (!Buffer.isBuffer(bytes) || bytes.length !== 449055 || sha(bytes) !== CATALOG_SHA)
    fail('CATALOG_SHA_MISMATCH');
  const data = JSON.parse(bytes.toString('utf8'));
  if (data.schemaVersion !== 2 || data.sourceManifestSha256 !== MANIFEST_SHA
      || data.records.length !== 1434 || data.files.length !== 56)
    fail('CATALOG_SCHEMA_MISMATCH');
  const sourceHashes = new Map(data.files.map(file => [file.path, file.sha256]));
  const occurrence = row => ({
    ...row, sourceSha256: sourceHashes.get(row.sourcePath),
  });
  const selected = ids.map(id => {
    const all = data.records.filter(row => row.id === id);
    const matches = all.filter(row => row.calling === calling);
    if (!matches.length) fail('ID_NOT_IN_CALLING:' + id);
    return {
      id,
      occurrences: matches.map(occurrence),
      // A shared ID is not evidence of exclusive calling membership.
      otherCallingOccurrences: all.filter(row => row.calling !== calling).map(occurrence),
      // Preserve ambiguity in duplicated name declarations; these are context, not
      // additional selected IDs or inferred current-game alternatives.
      duplicateNameContext: data.records.filter(row => row.id !== id &&
        matches.some(match => match.duplicateName && row.calling === match.calling &&
          row.soul === match.soul && row.category === match.category &&
          row.name === match.name)).map(occurrence),
    };
  });
  return {
    schemaVersion: 1,
    evidenceKind: 'rre-offline-static-candidate-plan/1',
    catalogSha256: CATALOG_SHA, sourceManifestSha256: MANIFEST_SHA,
    calling, requestedIds: [...ids], maxIds: MAX_IDS, selected,
    qualification: {
      staticSourceOnly: true, currentBuildVerified: false, apiKnownVerified: false,
      learnabilityVerified: false, castabilityVerified: false, liveExecution: false,
    },
  };
}

if (process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  try {
    const [calling, ...ids] = process.argv.slice(2);
    const bytes = readStableOriginalWithMetadata(CATALOG).bytes;
    process.stdout.write(JSON.stringify(planCandidates({calling, ids, bytes}), null, 2) + '\n');
  } catch (error) {
    process.stderr.write(JSON.stringify({status: 'failed', reason: error.message}) + '\n');
    process.exitCode = 1;
  }
}
