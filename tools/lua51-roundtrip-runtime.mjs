// Explicit runtime profiles for offline unit-producer round-trip tests.
// Compatibility mode never qualifies the original Windows interpreter artifacts.
import path from 'node:path';
import {spawnSync} from 'node:child_process';
import {resolvePinnedLua51,runPinnedLua51,verifyPinnedFile} from './pinned-lua51.mjs';

const HISTORICAL='historical-windows-5.1.4';
const COMPAT='compat-5.1.5';
export function resolveRoundtripRuntime(root,env=process.env){
  if(typeof root!=='string'||!path.isAbsolute(root))throw Error('ROUNDTRIP_ROOT_MUST_BE_ABSOLUTE');
  const profile=env.RRE_LUA51_ROUNDTRIP_PROFILE??HISTORICAL;
  if(profile===HISTORICAL){
    if(env.RRE_LUA51_COMPAT_EXE!==undefined||env.RRE_LUA51_COMPAT_SHA256!==undefined)
      throw Error('ROUNDTRIP_COMPAT_PROFILE_REQUIRED');
    return {profile,...resolvePinnedLua51(root,env)};
  }
  if(profile!==COMPAT)throw Error('ROUNDTRIP_UNKNOWN_PROFILE');
  if(env.RRE_LUA51_DIR!==undefined)throw Error('ROUNDTRIP_CONFLICTING_PROFILE');
  const exe=env.RRE_LUA51_COMPAT_EXE,pin=env.RRE_LUA51_COMPAT_SHA256;
  if(typeof exe!=='string'||!path.isAbsolute(exe)||!/^[a-f0-9]{64}$/.test(pin??''))
    throw Error('ROUNDTRIP_COMPAT_EXECUTABLE_AND_SHA_REQUIRED');
  return {profile,exe,exeSha256:verifyPinnedFile(exe,pin),dllSha256:null};
}

export function runRoundtripLua51(args,{root,env=process.env}){
  const runtime=resolveRoundtripRuntime(root,env);
  if(runtime.profile===HISTORICAL)return runPinnedLua51(args,{root,env});
  const childEnv={};
  for(const [key,value] of Object.entries(env)){
    if(['LUA_INIT','LUA_PATH','LUA_CPATH','LD_PRELOAD','LD_LIBRARY_PATH',
      'DYLD_INSERT_LIBRARIES','DYLD_LIBRARY_PATH'].includes(key.toUpperCase()))continue;
    childEnv[key]=value;
  }
  return spawnSync(runtime.exe,args,{cwd:root,env:childEnv,encoding:'utf8',
    windowsHide:true,shell:false,timeout:5000,maxBuffer:65536});
}

export function validateRoundtripRuntime(root,env=process.env){
  const runtime=resolveRoundtripRuntime(root,env);
  if(runtime.profile===COMPAT){
    const probe=runRoundtripLua51(['-v'],{root,env});
    if(probe.error||probe.status!==0||
      !/^Lua 5\.1\.5(?:\s|$)/m.test((probe.stdout??'')+(probe.stderr??'')))
      throw Error('ROUNDTRIP_COMPAT_VERSION_MISMATCH');
  }
  return runtime;
}
