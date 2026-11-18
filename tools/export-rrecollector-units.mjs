// Strict, offline SavedVariables exporter for RRECollector manual bounded unit witnesses.
// No Lua execution, game IO, native identity assertion, or data rewriting.
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import {fileURLToPath} from 'node:url';
import {parseSavedLuaBytes} from './read-rrecollector-saved.mjs';
import {readStableOriginalWithMetadata} from './read-stable-original.mjs';

const VERSION = '0.4.23';
const UNIT_ID = /^u[0-9A-Fa-f]{16}$/;
const STATUSES = new Set(['complete', 'partial', 'capped', 'empty']);
const REASONS = new Set(['bounded-sample-complete', 'detail-sample-cap', 'invalid-list-entries',
  'detail-errors', 'detail-identity-unqualified', 'xyz-incomplete', 'list-cap-reached',
  'no-nonself-listed']);
const ATTEMPT_STATUSES = new Set([...STATUSES, 'unavailable', 'error']);
const ATTEMPT_REASONS = new Set([...REASONS, 'missing-unit-api', 'player-id-unavailable',
  'unit-list-error', 'unit-list-non-table', 'unit-capture-exception']);
const isObject = v => v !== null && typeof v === 'object' && !Array.isArray(v);
const integer = (v, max = 9007199254740991) => Number.isSafeInteger(v) && v >= 0 && v <= max;
const finite = v => typeof v === 'number' && Number.isFinite(v) && Math.abs(v) <= 1e12;
const fail = code => {throw Error(code);};
const requireValue = (value, code) => {if (!value) fail(code);};
const id = value => typeof value === 'string' && UNIT_ID.test(value);
const specifier = value => typeof value === 'string' && value.length > 0
  && Buffer.byteLength(value, 'utf8') <= 80 && !/[\x00-\x1f\x7f|]/.test(value);
const exact = (object, names, code) => {
  requireValue(isObject(object), code);
  requireValue(Object.keys(object).every(k => names.includes(k)), code);
};
function dense(value, maximum, code) {
  if (Array.isArray(value)) {
    requireValue(value.length <= maximum && Array.from({length:value.length},(_,i)=>i)
      .every(i=>Object.hasOwn(value,i)), code);
    return value;
  }
  requireValue(isObject(value) && Object.keys(value).length <= maximum,code);
  const keys = Object.keys(value);
  requireValue(keys.every((key,i)=>key===String(i+1)), code);
  return keys.map(key=>value[key]);
}
function snapshot(value, expectedVersion) {
  const fields = ['schemaVersion','addonVersion','scope','status','reason','limits','counts',
    'records','listEnumerationComplete','detailSampleComplete','coordinateFrameVerified',
    'nativeIdentityVerified','atomicSnapshot','frameStart','realStart','frameEnd',
    'realEnd','selfId','sequence'];
  exact(value, fields, 'UNIT_SNAPSHOT_SHAPE');
  requireValue(value.schemaVersion===1 && value.addonVersion===expectedVersion
    && value.scope==='manual-bounded-unit-api-witness'
    && STATUSES.has(value.status) && REASONS.has(value.reason)
    && integer(value.sequence) && value.sequence > 0, 'UNIT_SNAPSHOT_CONTRACT');
  exact(value.limits,['listEntries','detailCalls'],'UNIT_LIMIT_SHAPE');
  requireValue(value.limits.listEntries===128 && value.limits.detailCalls===8,'UNIT_LIMITS');
  const counterNames=['examined','invalidEntries','selfEntries','nonselfEligible',
    'detailsCalled','detailErrors','idMismatches','idMissing','qualifiedXYZ'];
  exact(value.counts,counterNames,'UNIT_COUNTS_SHAPE');
  requireValue(counterNames.every(k=>integer(value.counts[k],128))
    && value.counts.examined<=128 && value.counts.detailsCalled<=8
    && value.counts.examined===value.counts.invalidEntries
      +value.counts.selfEntries+value.counts.nonselfEligible, 'UNIT_COUNTS');
  for(const name of ['listEnumerationComplete','detailSampleComplete',
    'coordinateFrameVerified','nativeIdentityVerified','atomicSnapshot'])
    requireValue(typeof value[name]==='boolean','UNIT_QUALIFICATION_SHAPE');
  requireValue(value.coordinateFrameVerified===false && value.nativeIdentityVerified===false
    && value.atomicSnapshot===false,'UNIT_QUALIFICATION_FALSE');
  requireValue(value.listEnumerationComplete===(value.status!=='capped')
    && value.detailSampleComplete===(value.status!=='capped'
      && value.counts.nonselfEligible<=8), 'UNIT_COVERAGE');
  requireValue(id(value.selfId),'UNIT_SELF_ID');
  for(const name of ['frameStart','realStart','frameEnd','realEnd'])
    if(Object.hasOwn(value,name)) requireValue(finite(value[name]),'UNIT_CLOCK');
  const records = dense(value.records,8,'UNIT_RECORD_ARRAY');
  requireValue(records.length===value.counts.detailsCalled
    && records.length===Math.min(value.counts.nonselfEligible,8),'UNIT_RECORD_COUNT');
  const seen=new Set();
  let errors=0,mismatches=0,missing=0,qualified=0;
  const rows=records.map((record)=>{
    exact(record,['id','specifier','idBinding','detailStatus','xyzComplete',
      'coordX','coordY','coordZ'],'UNIT_RECORD_FIELDS');
    requireValue(id(record.id) && record.id!==value.selfId
      && !seen.has(record.id) && specifier(record.specifier),'UNIT_RECORD_ID');
    seen.add(record.id);
    requireValue(['matched','missing','mismatch'].includes(record.idBinding)
      && ['returned','missing','error'].includes(record.detailStatus)
      && typeof record.xyzComplete==='boolean','UNIT_RECORD_STATUS');
    requireValue(record.detailStatus==='returned' || record.idBinding==='missing',
      'UNIT_DETAIL_STATUS_BINDING');
    requireValue(record.idBinding!=='matched' || record.detailStatus==='returned',
      'UNIT_DETAIL_STATUS_BINDING');
    if(record.detailStatus==='error') errors++;
    if(record.idBinding==='mismatch') mismatches++;
    if(record.detailStatus==='returned' && record.idBinding==='missing') missing++;
    if(record.idBinding!=='matched')
      requireValue(!['coordX','coordY','coordZ'].some(k=>Object.hasOwn(record,k))
        && record.xyzComplete===false,'UNIT_UNBOUND_COORDINATE');
    const xyz=['coordX','coordY','coordZ'];
    for(const key of xyz) if(Object.hasOwn(record,key))
      requireValue(finite(record[key]),'UNIT_COORDINATE');
    const complete=xyz.every(key=>Object.hasOwn(record,key));
    requireValue(record.xyzComplete===complete && (!complete || record.idBinding==='matched'),
      'UNIT_XYZ_BINDING');
    if(complete) qualified++;
    return {id:record.id,specifier:record.specifier,idBinding:record.idBinding,
      detailStatus:record.detailStatus,xyzComplete:record.xyzComplete,
      ...(record.idBinding==='matched' ? Object.fromEntries(xyz.filter(k=>Object.hasOwn(record,k))
        .map(k=>[k,record[k]])) : {})};
  });
  requireValue(errors===value.counts.detailErrors
    && mismatches===value.counts.idMismatches
    && missing===value.counts.idMissing
    && qualified===value.counts.qualifiedXYZ,'UNIT_COUNT_COHERENCE');
  if(value.status==='complete')
    requireValue(value.reason==='bounded-sample-complete'
      && value.counts.nonselfEligible>0 && value.counts.nonselfEligible<=8
      && value.counts.invalidEntries===0 && errors===0 && missing===0
      && mismatches===0 && qualified===records.length,'UNIT_COMPLETE_CONTRADICTION');
  if(value.status==='empty')
    requireValue(value.reason==='no-nonself-listed' && value.counts.nonselfEligible===0
      && value.counts.invalidEntries===0,'UNIT_EMPTY_CONTRADICTION');
  if(value.status==='capped')requireValue(value.reason==='list-cap-reached'
    && value.counts.examined===128,'UNIT_CAP_CONTRADICTION');
  if(value.status==='partial') requireValue(value.reason!=='bounded-sample-complete'
    && value.reason!=='list-cap-reached' && value.reason!=='no-nonself-listed',
    'UNIT_PARTIAL_CONTRADICTION');
  return {sequence:value.sequence,status:value.status,reason:value.reason,
    selfId:value.selfId,counts:{...value.counts},
    coverage:{listEnumerationComplete:value.listEnumerationComplete,
      detailSampleComplete:value.detailSampleComplete},
    clocks:Object.fromEntries(['frameStart','realStart','frameEnd','realEnd']
      .filter(k=>Object.hasOwn(value,k)).map(k=>[k,value[k]])),records:rows};
}

export function summarizeUnitWitness(saved, source={}) {
  requireValue(isObject(saved) && saved.addonVersion===VERSION,'UNIT_ROOT_VERSION');
  requireValue(integer(saved.unitSnapshotSequence) && saved.unitSnapshotSequence>0,
    'UNIT_SEQUENCE');
  const items=dense(saved.unitSnapshots,2,'UNIT_SNAPSHOT_ARRAY');
  requireValue(items.length>0 && items.length<=2,'UNIT_SNAPSHOT_COUNT');
  const snapshots=items.map(row=>snapshot(row,VERSION));
  requireValue(snapshots[0].sequence===saved.unitSnapshotSequence
    && (snapshots.length===1 || snapshots[1].sequence<snapshots[0].sequence),
    'UNIT_SEQUENCE_COHERENCE');
  let lastAttempt=null;
  if(Object.hasOwn(saved,'unitAttempt')) {
    const a=saved.unitAttempt;
    exact(a,['schemaVersion','addonVersion','attemptSequence','status','reason',
      'resultSequence'],'UNIT_ATTEMPT_SHAPE');
    requireValue(a.schemaVersion===1 && a.addonVersion===VERSION
      && integer(a.attemptSequence) && a.attemptSequence>0
      && ATTEMPT_STATUSES.has(a.status) && ATTEMPT_REASONS.has(a.reason)
      && (!Object.hasOwn(a,'resultSequence')
        || integer(a.resultSequence) && a.resultSequence===snapshots[0].sequence),
      'UNIT_ATTEMPT_CONTRACT');
    requireValue((a.status==='error'||a.status==='unavailable')
      ===!Object.hasOwn(a,'resultSequence'),'UNIT_ATTEMPT_PRESERVATION');
    if(a.status==='error') requireValue(['unit-list-error','unit-capture-exception']
      .includes(a.reason),'UNIT_ATTEMPT_REASON');
    else if(a.status==='unavailable') requireValue(['missing-unit-api',
      'player-id-unavailable','unit-list-non-table'].includes(a.reason),
      'UNIT_ATTEMPT_REASON');
    else requireValue(a.status===snapshots[0].status
      && a.reason===snapshots[0].reason,'UNIT_ATTEMPT_RESULT_BINDING');
    lastAttempt={attemptSequence:a.attemptSequence,status:a.status,reason:a.reason,
      resultSequence:a.resultSequence??null};
  }
  return {schemaVersion:1,evidenceKind:'rre-unit-witness/1',producerVersion:VERSION,
    savedAddonVersion:saved.addonVersion,sourceSha256:source.sha256??null,
    sourceBytes:source.bytes??null,sourceModifiedAtUtc:source.modifiedAtUtc??null,
    lastAttempt,qualification:{live:false,sourceAuthenticityVerified:false,
      processEpochVerified:false,atomicSnapshot:false,coordinateFrameVerified:false,
      nativeIdentityVerified:false,worldCoverageVerified:false},
    snapshots};
}
export function readUnitWitness(file) {
  requireValue(path.basename(file)==='RRECollector.lua','UNIT_INPUT_NAME');
  const original=readStableOriginalWithMetadata(file);
  const receipt=summarizeUnitWitness(parseSavedLuaBytes(original.bytes), {
    sha256:crypto.createHash('sha256').update(original.bytes).digest('hex'),
    bytes:original.bytes.length,modifiedAtUtc:original.modifiedAtUtc});
  return receipt;
}
if(process.argv[1]&&path.resolve(process.argv[1])===fileURLToPath(import.meta.url)) {
  try {
    const args=process.argv.slice(2);
    requireValue(args.length===1 || args.length===3 && args[1]==='--output',
      'UNIT_USAGE');
    const receipt=readUnitWitness(args[0]);
    const output=JSON.stringify(receipt,null,2)+'\n';
    if(args.length===3)fs.writeFileSync(args[2],output,{encoding:'utf8',flag:'wx'});
    else process.stdout.write(output);
  } catch(error) {
    const code=String(error?.message||'UNIT_EXPORT_FAILED');
    process.stderr.write(JSON.stringify({status:'failed',
      reason:/^[A-Z][A-Z0-9_]*$/.test(code)?code:'UNIT_EXPORT_FAILED'})+'\n');
    process.exitCode=1;
  }
}
