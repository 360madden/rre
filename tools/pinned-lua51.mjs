// Host-local, pinned Lua 5.1.4 test runtime. No download, discovery or PATH fallback.
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import {spawnSync} from 'node:child_process';
import {readStableOriginalWithMetadata} from './read-stable-original.mjs';

const EXE_SHA = '6675a1c46671d8bbdfea2b94704c495a2cb9e7accaffbb309f85c025752c2c67';
const DLL_SHA = '9224c9f2929cff5a0a10ce1d795a9d83112eead52b93ce625e31a24fa6f31096';
const DEFAULT_DIR = 'artifacts/sc103-lua51-msvc-20261104-1925-v1';

export function verifyPinnedFile(file, expectedSha) {
  let original;
  try {
    original = readStableOriginalWithMetadata(file);
  } catch (err) {
    throw new Error('LUA51_ARTIFACT_UNREADABLE: ' + path.basename(file) + ' (' + err.message + ')', {cause:err});
  }
  const actual = crypto.createHash('sha256').update(original.bytes).digest('hex');
  if (actual !== expectedSha) throw new Error('LUA51_ARTIFACT_SHA_MISMATCH: ' + path.basename(file));
  return actual;
}

export function resolvePinnedLua51(root, env=process.env) {
  if (typeof root !== 'string' || !path.isAbsolute(root))
    throw new Error('LUA51_ROOT_MUST_BE_ABSOLUTE');
  const override = env.RRE_LUA51_DIR;
  if (override !== undefined && (typeof override !== 'string' || !path.isAbsolute(override)))
    throw new Error('LUA51_OVERRIDE_MUST_BE_ABSOLUTE');
  const dir = path.resolve(override ?? path.join(root, DEFAULT_DIR));
  let stat;
  try { stat = fs.lstatSync(dir); }
  catch (err) { throw new Error('LUA51_PINNED_RUNTIME_MISSING: ' + dir, {cause:err}); }
  if (!stat.isDirectory() || stat.isSymbolicLink())
    throw new Error('LUA51_RUNTIME_DIRECTORY_INVALID');
  const exe = path.join(dir, 'lua.exe');
  const dll = path.join(dir, 'lua51.dll');
  return {dir, exe, dll, exeSha256:verifyPinnedFile(exe, EXE_SHA),
    dllSha256:verifyPinnedFile(dll, DLL_SHA)};
}

// Verify both files immediately before each launch: an independent failed test
// must not leave the subsequent test free to execute an unqualified binary.
export function runPinnedLua51(args, {root, env=process.env}) {
  const runtime = resolvePinnedLua51(root, env);
  // Suppress inherited Lua initialization and module paths. Preserve other
  // environment variables; on Windows PATH spelling is case-insensitive.
  const childEnv = {};
  let inheritedPath = '';
  for (const [key, value] of Object.entries(env)) {
    const upper = key.toUpperCase();
    if (upper === 'PATH') { inheritedPath = value || ''; continue; }
    if (['LUA_INIT','LUA_PATH','LUA_CPATH'].includes(upper)) continue;
    childEnv[key] = value;
  }
  childEnv.PATH = runtime.dir + path.delimiter + inheritedPath;
  return spawnSync(runtime.exe, args, {cwd:root, env:childEnv, encoding:'utf8',
    windowsHide:true, shell:false, timeout:5000, maxBuffer:65536});
}
