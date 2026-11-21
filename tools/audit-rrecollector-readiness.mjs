// Read-only RRECollector release readiness check: source vs installed addon vs SavedVariables.
// This is not a proof of active Lua, current UI, executable mapping, or same-load publication.
import {createHash} from 'node:crypto';
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {parseSavedLuaBytes} from './read-rrecollector-saved.mjs';
import {readStableOriginalWithMetadata} from './read-stable-original.mjs';
import {summarizeUnitWitness} from './export-rrecollector-units.mjs';

const repo=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const sourceDir=path.join(repo,'addons','RRECollector');
const sourceModules=['core.lua','context.lua','abilities.lua','capabilities.lua',
  'candidate_catalog.lua','candidates.lua','wire.lua','units.lua','ui.lua','main.lua'];
const files=[...sourceModules,'README.md','RiftAddon.toc'];
const sha=file=>createHash('sha256').update(fs.readFileSync(file)).digest('hex');
function versionInToc(raw){
  const matches=[...raw.matchAll(/^Version\s*=\s*"([^"\r\n]+)"\s*$/gm)];
  if(matches.length!==1)throw Error('INVALID_TOC_VERSION');
  return matches[0][1];
}
function versionInCore(raw){
  const matches=[...raw.matchAll(/^RRECollectorRuntime\.VERSION\s*=\s*"([^"\r\n]+)"\s*$/gm)];
  if(matches.length!==1)throw Error('INVALID_CORE_VERSION');
  return matches[0][1];
}
function pkgVersion(dir){
  const toc=versionInToc(fs.readFileSync(path.join(dir,'RiftAddon.toc'),'utf8'));
  const core=versionInCore(fs.readFileSync(path.join(dir,'core.lua'),'utf8'));
  if(toc!==core)throw Error('TOC_CORE_VERSION_MISMATCH');
  return toc;
}
export function inspectCollectorReadiness(installedDir,savedFile){
  if(path.basename(installedDir).toLowerCase()!=='rrecollector'
    || path.basename(path.dirname(installedDir)).toLowerCase()!=='addons')
    throw Error('INSTALL_DIRECTORY_CONTRACT');
  if(path.basename(savedFile).toLowerCase()!=='rrecollector.lua')
    throw Error('SAVED_FILENAME_CONTRACT');
  const sourceVersion=pkgVersion(sourceDir), installedVersion=pkgVersion(installedDir);
  const matched=[],changed=[],missing=[];
  for(const file of files){
    const expected=path.join(sourceDir,file),existing=path.join(installedDir,file);
    if(!fs.existsSync(existing)){missing.push(file);continue;}
    if(!fs.statSync(existing).isFile())throw Error('INSTALL_NOT_FILE');
    (sha(expected)===sha(existing)?matched:changed).push(file);
  }
  const original=readStableOriginalWithMetadata(savedFile);
  const data=parseSavedLuaBytes(original.bytes);
  const latest=data.latest&&typeof data.latest==='object'?data.latest:null;
  const abilityCount=Array.isArray(latest?.abilities)?latest.abilities.length:null;
  const capture=data.captureAttempt&&typeof data.captureAttempt==='object'?data.captureAttempt:null;
  const units=data.unitAttempt&&typeof data.unitAttempt==='object'?data.unitAttempt:null;
  const hasUnitRecord=Object.hasOwn(data,'unitSnapshotSequence')
    || Object.hasOwn(data,'unitSnapshots') || Object.hasOwn(data,'unitAttempt');
  let unitValidation={status:'absent',reason:null,latestStatus:null,retainedCount:0};
  if(hasUnitRecord){
    try{
      const witness=summarizeUnitWitness(data);
      if(witness.snapshotState==='attempt-only'){
        unitValidation={status:'attempt-only',reason:witness.lastAttempt.reason,
          latestStatus:null,retainedCount:0,
          lastAttemptStatus:witness.lastAttempt.status};
      }else{
        unitValidation={status:'validated',reason:null,
          latestStatus:witness.snapshots[0].status,retainedCount:witness.snapshots.length};
      }
    }catch(error){
      const message=String(error?.message??'UNIT_INVALID');
      unitValidation={status:'rejected',reason:/^UNIT_[A-Z0-9_]+$/.test(message)
        ? message : 'UNIT_INVALID',latestStatus:null,retainedCount:0};
    }
  }
  const instParity=missing.length===0&&changed.length===0;
  return {
    schemaVersion:1,evidenceKind:'rrecollector-readiness-audit/1',
    sourceVersion,installedVersion,
    install:{status:instParity?'source-hash-parity':'not-current-source',
      filesExpected:files.length,matchedCount:matched.length,
      missing,changed},
    saved:{rootVersion:typeof data.addonVersion==='string'?data.addonVersion:null,
      acceptedAbilityVersion:latest?.addonVersion??null,
      acceptedAbilitySequence:latest?.sequence??null,
      acceptedAbilityComplete:latest?.captureComplete===true,
      acceptedAbilityCount:abilityCount,
      publicationStatus:data.memoryPublication?.status??null,
      lastCaptureAttemptVersion:capture?.addonVersion??null,
      lastCaptureAttemptStatus:capture?.status??null,
      lastUnitAttemptVersion:units?.addonVersion??null,
      lastUnitAttemptStatus:units?.status??null,
      acceptedUnitSequence:data.unitSnapshotSequence??null,
      unitValidation,
      sourceBytes:original.bytes.length,
      sourceSha256:createHash('sha256').update(original.bytes).digest('hex'),
      sourceModifiedAtUtc:original.modifiedAtUtc},
    checks:{sourceInstalledByteIdentical:instParity,
      installedVersionMatchesSource:installedVersion===sourceVersion,
      savedRootMatchesSource:data.addonVersion===sourceVersion,
      acceptedAbilityMatchesSource:latest?.addonVersion===sourceVersion,
      acceptedAbilityComplete:latest?.captureComplete===true,
      acceptedUnitsPresent:unitValidation.status==='validated',
      acceptedUnitsComplete:unitValidation.status==='validated'
        && unitValidation.latestStatus==='complete'},
    limits:{activeLuaLoadVerified:false,gameUiVerified:false,
      sameProcessEpochVerified:false,liveRrec2TransferVerified:false,
      nativeCorrelationDone:false,wa006Accepted:false}
  };
}
if(process.argv[1]&&path.resolve(process.argv[1])===fileURLToPath(import.meta.url)){
  try{
    if(process.argv.length!==4)throw Error('USAGE_INSTALLED_DIR_SAVED_FILE');
    process.stdout.write(JSON.stringify(inspectCollectorReadiness(process.argv[2],process.argv[3]))+'\n');
  }catch(error){
    const reason=String(error?.message??'AUDIT_FAILED');
    process.stderr.write(JSON.stringify({status:'failed',reason})+'\n');
    process.exitCode=2;
  }
}
