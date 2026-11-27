// Read-only RRECollector release readiness check: source vs installed addon vs SavedVariables.
// This is not a proof of active Lua, current UI, executable mapping, or same-load publication.
import {createHash} from 'node:crypto';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {parseSavedLuaBytes, assessSnapshotForComparison} from './read-rrecollector-saved.mjs';
import {readStableOriginalWithMetadata} from './read-stable-original.mjs';
import {summarizeUnitWitness} from './export-rrecollector-units.mjs';
import {assessCaptureAttempt} from './assess-rrecollector-capture-attempt.mjs';
import {COLLECTOR_FILES,readCollectorPackage,requireExactPackage,packageText} from './read-rrecollector-package.mjs';

const repo=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const sourceDir=path.join(repo,'addons','RRECollector');
const files=COLLECTOR_FILES;
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
function pkgVersion(pkg){
  const toc=versionInToc(packageText(pkg,'RiftAddon.toc'));
  const core=versionInCore(packageText(pkg,'core.lua'));
  if(toc!==core)throw Error('TOC_CORE_VERSION_MISMATCH');
  return toc;
}
export function inspectCollectorReadiness(installedDir,savedFile){
  if(path.basename(installedDir).toLowerCase()!=='rrecollector'
    || path.basename(path.dirname(installedDir)).toLowerCase()!=='addons')
    throw Error('INSTALL_DIRECTORY_CONTRACT');
  if(path.basename(savedFile).toLowerCase()!=='rrecollector.lua')
    throw Error('SAVED_FILENAME_CONTRACT');
  const source=readCollectorPackage(sourceDir);
  requireExactPackage(source);
  const installed=readCollectorPackage(installedDir);
  const sourceVersion=pkgVersion(source), installedVersion=pkgVersion(installed);
  const matched=[],changed=[];
  const {missing,unexpected}=installed;
  for(const file of files){
    const existing=installed.records.get(file);
    if(!existing)continue;
    (source.records.get(file).sha256===existing.sha256?matched:changed).push(file);
  }
  const original=readStableOriginalWithMetadata(savedFile);
  const data=parseSavedLuaBytes(original.bytes);
  const latest=data.latest&&typeof data.latest==='object'?data.latest:null;
  // A producer's complete flag is descriptive, not proof of a coherent snapshot.
  // Reuse the saved-reader's existing structure gate; never infer freshness from it.
  const abilityStructure=assessSnapshotForComparison(data);
  const abilityQualified=abilityStructure.offlineStructureQualified===true;
  // The gate binds uniqueCount to the actual rows, including explicit Lua
  // one-based table keys. Rejected snapshots must not report accepted counts.
  const abilityCount=abilityQualified?latest.abilityList.uniqueCount:null;
  const abilityValidation={
    status:latest===null?'absent':abilityQualified?'validated':'rejected',
    reportedComplete:latest?.captureComplete===true,
    reasons:latest===null?[]:abilityStructure.reasons,
  };
  const abilityVersionMatches=latest?.addonVersion===sourceVersion;
  const capture=data.captureAttempt&&typeof data.captureAttempt==='object'?data.captureAttempt:null;
  const captureAttemptValidation=assessCaptureAttempt(data,sourceVersion);
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
          lastAttemptStatus:witness.lastAttempt.status,
          lastAttemptSequence:witness.lastAttempt.attemptSequence,lastAttemptResultSequence:null};
      }else{
        unitValidation={status:'validated',reason:null,
          latestStatus:witness.snapshots[0].status,retainedCount:witness.snapshots.length,
          lastAttemptStatus:witness.lastAttempt?.status??null,
          lastAttemptSequence:witness.lastAttempt?.attemptSequence??null,
          lastAttemptResultSequence:witness.lastAttempt?.resultSequence??null};
      }
    }catch(error){
      const message=String(error?.message??'UNIT_INVALID');
      unitValidation={status:'rejected',reason:/^UNIT_[A-Z0-9_]+$/.test(message)
        ? message : 'UNIT_INVALID',latestStatus:null,retainedCount:0};
    }
  }
  const instParity=missing.length===0&&changed.length===0&&unexpected.length===0;
  return {
    schemaVersion:1,evidenceKind:'rrecollector-readiness-audit/1',
    sourceVersion,installedVersion,
    install:{status:instParity?'source-hash-parity':'not-current-source',
      filesExpected:files.length,matchedCount:matched.length,
      missing,changed,unexpected,
      stableReadRetries:{source:source.retried,installed:installed.retried}},
    saved:{rootVersion:typeof data.addonVersion==='string'?data.addonVersion:null,
      acceptedAbilityVersion:latest?.addonVersion??null,
      acceptedAbilitySequence:latest?.sequence??null,
      acceptedAbilityComplete:abilityQualified,
      abilityValidation,
      acceptedAbilityCount:abilityCount,
      publicationStatus:data.memoryPublication?.status??null,
      lastCaptureAttemptVersion:capture?.addonVersion??null,
      lastCaptureAttemptStatus:capture?.status??null,
      captureAttemptValidation,
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
      abilityProducerVersionMatchesSource:abilityVersionMatches,
      acceptedAbilityMatchesSource:abilityQualified&&abilityVersionMatches,
      acceptedAbilityComplete:abilityQualified,
      completeAbilityAttemptBound:captureAttemptValidation.completeResultBound,
      acceptedUnitsPresent:unitValidation.status==='validated',
      acceptedUnitsComplete:unitValidation.status==='validated'
        && unitValidation.latestStatus==='complete',
      completeUnitAttemptBound:unitValidation.status==='validated'
        && data.addonVersion===sourceVersion && unitValidation.lastAttemptStatus==='complete'
        && unitValidation.lastAttemptResultSequence===data.unitSnapshotSequence},
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
