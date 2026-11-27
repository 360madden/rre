import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import crypto from 'node:crypto';
import {resolveRoundtripRuntime} from './lua51-roundtrip-runtime.mjs';

const root=path.resolve('.');
const profile='compat-5.1.5';
test('compatibility runtime requires an explicit profile and absolute path/hash',()=>{
  assert.throws(()=>resolveRoundtripRuntime(root,{RRE_LUA51_COMPAT_EXE:'anything'}),
    /ROUNDTRIP_COMPAT_PROFILE_REQUIRED/);
  assert.throws(()=>resolveRoundtripRuntime(root,{RRE_LUA51_ROUNDTRIP_PROFILE:profile}),
    /ROUNDTRIP_COMPAT_EXECUTABLE_AND_SHA_REQUIRED/);
  assert.throws(()=>resolveRoundtripRuntime(root,{RRE_LUA51_ROUNDTRIP_PROFILE:profile,
    RRE_LUA51_COMPAT_EXE:'relative',RRE_LUA51_COMPAT_SHA256:'0'.repeat(64)}),
    /ROUNDTRIP_COMPAT_EXECUTABLE_AND_SHA_REQUIRED/);
});
test('unknown or conflicting runtime profiles fail closed',()=>{
  assert.throws(()=>resolveRoundtripRuntime(root,{RRE_LUA51_ROUNDTRIP_PROFILE:'auto'}),
    /ROUNDTRIP_UNKNOWN_PROFILE/);
  assert.throws(()=>resolveRoundtripRuntime(root,{RRE_LUA51_ROUNDTRIP_PROFILE:profile,
    RRE_LUA51_DIR:root}),/ROUNDTRIP_CONFLICTING_PROFILE/);
});
test('compatibility resolution checks bytes without executing fixture files',()=>{
  const dir=fs.mkdtempSync(path.join(os.tmpdir(),'rre-lua-profile-'));
  try{
    const file=path.join(dir,'fixture');
    const data=Buffer.from('not an executable');
    fs.writeFileSync(file,data);
    const pin=crypto.createHash('sha256').update(data).digest('hex');
    const env={RRE_LUA51_ROUNDTRIP_PROFILE:profile,RRE_LUA51_COMPAT_EXE:file,
      RRE_LUA51_COMPAT_SHA256:pin};
    const runtime=resolveRoundtripRuntime(root,env);
    assert.equal(runtime.profile,profile);
    assert.equal(runtime.exeSha256,pin);
    assert.equal(runtime.dllSha256,null);
    fs.appendFileSync(file,'changed');
    assert.throws(()=>resolveRoundtripRuntime(root,env),/LUA51_ARTIFACT_SHA_MISMATCH/);
  }finally{fs.rmSync(dir,{recursive:true,force:true});}
});
