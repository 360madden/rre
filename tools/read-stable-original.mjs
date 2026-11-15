// Shared, bounded original-file read for offline RRE SavedVariables and source catalogs.
// A changed path, file identity, size or timestamp fails closed; no source content is logged.
import fs from 'node:fs';

export const MAX_ORIGINAL_BYTES = 2_000_000;
export const MAX_CASTING_BYTES = 32_000_000;

export function readStableOriginalWithMetadata(file, maximumBytes = MAX_ORIGINAL_BYTES) {
  if (!Number.isSafeInteger(maximumBytes) || maximumBytes < 1 || maximumBytes > MAX_CASTING_BYTES)
    throw Error('saved-byte-limit-configuration');
  const pathBefore = fs.lstatSync(file);
  if (!pathBefore.isFile() || pathBefore.isSymbolicLink()) throw Error('saved-source-not-plain-file');
  const fd = fs.openSync(file, 'r');
  try {
    const before = fs.fstatSync(fd);
    const same = stat => stat.dev === before.dev && stat.ino === before.ino
      && stat.size === before.size && stat.mtimeMs === before.mtimeMs
      && stat.ctimeMs === before.ctimeMs;
    if (!same(pathBefore)) throw Error('saved-source-changed-before-read');
    if (before.size > maximumBytes) throw Error('saved-byte-limit');
    const buffer = Buffer.alloc(Math.min(maximumBytes + 1, before.size + 1));
    let length = 0, n;
    do { n = fs.readSync(fd, buffer, length, buffer.length - length, null); length += n; }
    while (n && length < buffer.length);
    const pathAfter = fs.lstatSync(file);
    if (length > maximumBytes) throw Error('saved-byte-limit');
    if (length !== before.size || !same(fs.fstatSync(fd))
      || !pathAfter.isFile() || pathAfter.isSymbolicLink() || !same(pathAfter))
      throw Error('saved-source-changed-during-read');
    return {bytes: buffer.subarray(0, length), modifiedAtUtc: before.mtime.toISOString()};
  } finally { fs.closeSync(fd); }
}

export const readStableOriginal = file => readStableOriginalWithMetadata(file).bytes;
