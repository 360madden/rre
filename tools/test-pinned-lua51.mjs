import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import crypto from 'node:crypto';
import {resolvePinnedLua51, runPinnedLua51, verifyPinnedFile} from './pinned-lua51.mjs';

function fixture(fn) {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(),'rre-lua51-preflight-'));
  try { fn(dir); } finally { fs.rmSync(dir,{recursive:true,force:true}); }
}
test('missing historical runtime fails explicitly without fallback',()=>fixture(root=>{
  assert.throws(()=>resolvePinnedLua51(root,{}),/LUA51_PINNED_RUNTIME_MISSING/);
  assert.throws(()=>runPinnedLua51(['-v'],{root,env:{}}),/LUA51_PINNED_RUNTIME_MISSING/);
}));
test('relative and empty overrides are rejected',()=>fixture(root=>{
  for(const override of ['', 'relative/path'])
    assert.throws(()=>resolvePinnedLua51(root,{RRE_LUA51_DIR:override}),/LUA51_OVERRIDE_MUST_BE_ABSOLUTE/);
}));
test('missing executable and malformed executable fail before launch',()=>fixture(root=>{
  const env={RRE_LUA51_DIR:root};
  assert.throws(()=>runPinnedLua51(['-v'],{root,env}),/LUA51_ARTIFACT_UNREADABLE: lua.exe/);
  fs.writeFileSync(path.join(root,'lua.exe'),'not a trusted interpreter');
  assert.throws(()=>runPinnedLua51(['-v'],{root,env}),/LUA51_ARTIFACT_SHA_MISMATCH: lua.exe/);
}));
test('stable-file digest validation detects mutation and missing input',()=>fixture(root=>{
  const file=path.join(root,'fixture.bin');
  const bytes=Buffer.from('fixture bytes');
  const sha=crypto.createHash('sha256').update(bytes).digest('hex');
  fs.writeFileSync(file,bytes);
  assert.equal(verifyPinnedFile(file,sha),sha);
  fs.appendFileSync(file,'changed');
  assert.throws(()=>verifyPinnedFile(file,sha),/LUA51_ARTIFACT_SHA_MISMATCH/);
  fs.unlinkSync(file);
  assert.throws(()=>verifyPinnedFile(file,sha),/LUA51_ARTIFACT_UNREADABLE/);
}));
test('explicit override is not treated as a file or searched on PATH',()=>fixture(root=>{
  const file=path.join(root,'file');
  fs.writeFileSync(file,'x');
  assert.throws(()=>resolvePinnedLua51(root,{RRE_LUA51_DIR:file}),/LUA51_RUNTIME_DIRECTORY_INVALID/);
}));
