// Data-only adapter: reuse the existing literal Lua parser and Detail projection.
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import {fileURLToPath} from 'node:url';
import {parseSavedLua, assessSnapshotForComparison, buildAbilityCrosswalk} from './read-rrecollector-saved.mjs';

export const MAX_BYTES = 2_000_000;
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
  const crosswalk = buildAbilityCrosswalk(saved, {records:[], catalogVersion:'no-static-catalog'}, sha(bytes));
  // The historical research crosswalk deliberately redacts target IDs. The local
  // reader data contract retains the producer's scalar target without changing it.
  const rawById = new Map(Object.values(saved.latest.abilities).map(row=>[row.lookupId,row]));
  const abilities = crosswalk.knownOutsideStatic.map(row=>{
    const detail = {...row.currentDetail};
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
  return {adapterContract:'rre-saved-snapshot/1', sourceSha256:sha(bytes), sourceBytes:bytes.length,
    addonVersion:saved.latest.addonVersion, savedAddonVersion:typeof saved.addonVersion === 'string' ? saved.addonVersion : null,
    sequence:saved.latest.sequence,
    abilities, context,
    counts:boundedCopy(saved.latest.abilityList), structure};
}
export function readBoundedSaved(file) {
  const fd = fs.openSync(file,'r');
  try {
    const buffer = Buffer.alloc(MAX_BYTES + 1);
    let length = 0, n;
    do { n = fs.readSync(fd,buffer,length,buffer.length-length,null); length += n; }
    while (n && length < buffer.length);
    if (length > MAX_BYTES) throw Error('saved-byte-limit');
    return buffer.subarray(0,length);
  } finally { fs.closeSync(fd); }
}
if (process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  try {
    if (process.argv.length !== 3) throw Error('usage: node tools/rre-reader-saved-snapshot.mjs FILE');
    process.stdout.write(JSON.stringify(exportSavedSnapshot(readBoundedSaved(process.argv[2]))) + '\n');
  } catch (error) {
    process.stderr.write(JSON.stringify({error:String(error.message)}) + '\n');
    process.exitCode = 2;
  }
}
