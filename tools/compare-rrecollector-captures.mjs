// Offline, source-hash-bound comparison of two original SavedVariables byte sets.
// A passing comparison demonstrates coherent persisted progression, not live freshness.
import path from 'node:path';
import crypto from 'node:crypto';
import {fileURLToPath} from 'node:url';
import {readStableOriginalWithMetadata,MAX_ORIGINAL_BYTES} from './read-stable-original.mjs';
import {parseSavedLuaBytes,assessSnapshotForComparison} from './read-rrecollector-saved.mjs';
import {assessCaptureAttempt} from './assess-rrecollector-capture-attempt.mjs';
import {summarizeUnitWitness} from './export-rrecollector-units.mjs';

const VERSION='0.4.23'; // Current unit exporter schema, not a claim about active Lua.
const sha=b=>crypto.createHash('sha256').update(b).digest('hex');
const own=(v,k)=>Object.hasOwn(v,k);
const seq=v=>Number.isSafeInteger(v)&&v>0?v:null;
const player=v=>typeof v==='string'&&/^u[0-9A-Fa-f]{16}$/.test(v)?v.toUpperCase():null;
function readUnits(saved){
  if(!['unitAttempt','unitSnapshotSequence','unitSnapshots'].some(k=>own(saved,k)))
    return {valid:true,sequence:0,attempt:0,completeBound:false,self:null};
  try{
    const report=summarizeUnitWitness(saved);
    const latest=report.snapshots[0],last=report.lastAttempt;
    // Retained snapshots without an attempt cannot establish the previous attempt counter.
    if(!last)return {valid:false,sequence:null,attempt:null,completeBound:false,self:null};
    return {valid:true,sequence:latest?.sequence??0,attempt:last.attemptSequence,
      completeBound:latest?.status==='complete'&&last.status==='complete'
        && last.resultSequence===latest.sequence,self:player(latest?.selfId)};
  }catch{
    return {valid:false,sequence:null,attempt:null,completeBound:false,self:null};
  }
}
export function compareCaptureBytes(beforeBytes,afterBytes,expectedBeforeSha){
  if(!/^[0-9a-f]{64}$/.test(expectedBeforeSha??'')||
    ![beforeBytes,afterBytes].every(b=>Buffer.isBuffer(b)&&b.length>0&&b.length<=MAX_ORIGINAL_BYTES))
    throw Error('COMPARISON_INPUT_CONTRACT');
  const beforeSha=sha(beforeBytes),afterSha=sha(afterBytes);
  if(beforeSha!==expectedBeforeSha)throw Error('BASELINE_SHA_MISMATCH');
  const before=parseSavedLuaBytes(beforeBytes),after=parseSavedLuaBytes(afterBytes);
  const beforeStructure=assessSnapshotForComparison(before).offlineStructureQualified;
  const afterStructure=assessSnapshotForComparison(after).offlineStructureQualified;
  const oldAttempt=assessCaptureAttempt(before,before.addonVersion);
  const newAttempt=assessCaptureAttempt(after,VERSION);
  const oldUnits=readUnits(before),newUnits=readUnits(after);
  const priorPlayer=player(before.latest?.player?.id),newPlayer=player(after.latest?.player?.id);
  const beforeSequence=seq(before.sequence),afterSequence=seq(after.sequence);
  const oldAttemptSequence=oldAttempt.status==='absent'?0:oldAttempt.attemptSequence;
  const newAttemptSequence=newAttempt.attemptSequence;
  const advances=(a,b)=>Number.isSafeInteger(a)&&Number.isSafeInteger(b)&&b>a;
  const checks={
    distinctBytes:beforeSha!==afterSha,
    baselineAbilityStructure:beforeStructure,
    baselineAttemptValid:oldAttempt.status!=='rejected',
    baselineUnitStateValid:oldUnits.valid,
    currentVersion:after.addonVersion===VERSION&&after.latest?.addonVersion===VERSION,
    currentAbilityStructure:afterStructure,
    samePlayerId:priorPlayer!==null&&priorPlayer===newPlayer,
    completeAbilityAttemptBound:newAttempt.completeResultBound,
    advancingAbilitySequence:advances(beforeSequence,afterSequence),
    advancingAbilityAttempt:advances(oldAttemptSequence,newAttemptSequence),
    completeUnitAttemptBound:newUnits.completeBound,
    advancingUnitSequence:advances(oldUnits.sequence,newUnits.sequence),
    advancingUnitAttempt:advances(oldUnits.attempt,newUnits.attempt),
    unitSelfMatchesAbilityPlayer:newPlayer!==null&&newPlayer===newUnits.self,
  };
  const reasons=Object.keys(checks).filter(k=>!checks[k]);
  return {schemaVersion:1,evidenceKind:'rre-persisted-capture-progression/1',
    expectedVersion:VERSION,offlineProgressionQualified:reasons.length===0,
    checks,reasons,baseline:{sha256:beforeSha,bytes:beforeBytes.length,
      abilitySequence:beforeSequence,abilityAttemptSequence:oldAttemptSequence,
      unitSequence:oldUnits.sequence,unitAttemptSequence:oldUnits.attempt},
    candidate:{sha256:afterSha,bytes:afterBytes.length,
      abilitySequence:afterSequence,abilityAttemptSequence:newAttemptSequence,
      unitSequence:newUnits.sequence,unitAttemptSequence:newUnits.attempt},
    limits:{liveFreshnessVerified:false,sourceAuthenticityVerified:false,
      sameProcessEpochVerified:false,gameUiVerified:false,
      atomicSnapshotVerified:false,nativeIdentityVerified:false,p0Accepted:false}};
}
if(process.argv[1]&&path.resolve(process.argv[1])===fileURLToPath(import.meta.url)){
  try{
    const [before,after,pin,...rest]=process.argv.slice(2);
    if(!before||!after||!pin||rest.length||
      ![before,after].every(f=>path.basename(f).toLowerCase()==='rrecollector.lua'))
      throw Error('USAGE_BEFORE_AFTER_BASELINE_SHA');
    const result=compareCaptureBytes(readStableOriginalWithMetadata(before).bytes,
      readStableOriginalWithMetadata(after).bytes,pin);
    process.stdout.write(JSON.stringify(result)+'\n');
    process.exitCode=result.offlineProgressionQualified?0:1;
  }catch(error){
    const reason=String(error?.message??'COMPARISON_FAILED');
    process.stderr.write(JSON.stringify({status:'failed',reason:
      /^[A-Z][A-Z0-9_]*$/.test(reason)?reason:'COMPARISON_READ_OR_PARSE_FAILED'})+'\n');
    process.exitCode=2;
  }
}
