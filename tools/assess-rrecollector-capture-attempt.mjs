// Validate the current-schema saved ability attempt against its retained result.
// This is offline structural consistency, not evidence of a new capture or live execution.
import {assessSnapshotForComparison} from './read-rrecollector-saved.mjs';

const own=(v,k)=>Object.hasOwn(v,k);
const obj=v=>v!==null&&typeof v==='object'&&!Array.isArray(v);
const integer=(v,max=Number.MAX_SAFE_INTEGER)=>Number.isSafeInteger(v)&&v>=0&&v<=max;
const clock=v=>typeof v==='number'&&Number.isFinite(v)&&v>=0&&v<=1e12;
const fields=['schemaVersion','addonVersion','attemptSequence','status','reason','preservedPrior',
  'priorSequence','resultSequence','frameTime','realTime','counts','publicationStatus','publicationReason'];
const countKeys=['uniqueCount','detailCount','detailFailures'];
const outcomes={complete:'none',partial:'none',failed:'api-capture-error',
  'incomplete-preserved':'capture-incomplete'};

export function assessCaptureAttempt(saved,expectedVersion){
  const result={status:'absent',outcome:null,attemptSequence:null,resultSequence:null,
    resultBound:false,completeResultBound:false,reasons:[]};
  if(!obj(saved)||!own(saved,'captureAttempt'))return result;
  const a=saved.captureAttempt;
  const fail=reason=>({...result,status:'rejected',reasons:[reason]});
  if(!obj(a)||Object.keys(a).some(k=>!fields.includes(k)))
    return fail('CAPTURE_ATTEMPT_SHAPE');
  if(a.schemaVersion!==1||a.addonVersion!==expectedVersion||saved.addonVersion!==expectedVersion)
    return fail('CAPTURE_ATTEMPT_VERSION');
  if(!integer(a.attemptSequence)||a.attemptSequence===0)
    return fail('CAPTURE_ATTEMPT_SEQUENCE');
  if(typeof a.status!=='string'||!own(outcomes,a.status)||a.reason!==outcomes[a.status])
    return fail('CAPTURE_ATTEMPT_OUTCOME');
  const accepted=a.status==='complete'||a.status==='partial';
  if(a.preservedPrior!==!accepted||own(a,'resultSequence')!==accepted)
    return fail('CAPTURE_ATTEMPT_PRESERVATION');
  if(own(a,'priorSequence')&&!integer(a.priorSequence))
    return fail('CAPTURE_ATTEMPT_PRIOR_SEQUENCE');
  for(const key of ['frameTime','realTime']){
    if(own(a,key)&&!clock(a[key]))return fail('CAPTURE_ATTEMPT_CLOCK');
  }
  if(own(a,'counts')&&(!obj(a.counts)||Object.keys(a.counts).length===0||
    Object.keys(a.counts).some(k=>!countKeys.includes(k)||!integer(a.counts[k],1048576))))
    return fail('CAPTURE_ATTEMPT_COUNTS');
  // Wire publication is independent of the saved ability result. If recorded,
  // its receipt must agree, but a non-published capture can still be complete.
  for(const [key,rootKey,max] of [['publicationStatus','status',40],['publicationReason','reason',80]]){
    if(own(a,key)&&(typeof a[key]!=='string'||a[key].length>max||
      !/^[A-Za-z0-9-]+$/.test(a[key])||a[key]!==saved.memoryPublication?.[rootKey]))
      return fail('CAPTURE_ATTEMPT_PUBLICATION');
  }
  if(!accepted){
    if(integer(saved.sequence)&&(!own(a,'priorSequence')||a.priorSequence!==saved.sequence))
      return fail('CAPTURE_ATTEMPT_PRIOR_BINDING');
    if(a.status==='incomplete-preserved'&&!assessSnapshotForComparison(saved).offlineStructureQualified)
      return fail('CAPTURE_ATTEMPT_PRESERVED_RESULT');
    return {...result,status:'validated',outcome:a.status,attemptSequence:a.attemptSequence};
  }
  const latest=saved.latest;
  if(!obj(latest)||latest.addonVersion!==a.addonVersion||
    !integer(a.resultSequence)||a.resultSequence===0||
    a.resultSequence!==saved.sequence||a.resultSequence!==latest.sequence)
    return fail('CAPTURE_ATTEMPT_RESULT_BINDING');
  // Counter reset/wrap is not an advancing result under this conservative gate.
  const prior=own(a,'priorSequence')?a.priorSequence:0;
  if(prior>=Number.MAX_SAFE_INTEGER||a.resultSequence!==prior+1)
    return fail('CAPTURE_ATTEMPT_PRIOR_BINDING');
  const complete=a.status==='complete';
  if(latest.captureComplete!==complete)
    return fail('CAPTURE_ATTEMPT_COMPLETION_BINDING');
  for(const key of ['frameTime','realTime']){
    if((complete||own(a,key))&&(!clock(a[key])||a[key]!==latest[key]))
      return fail('CAPTURE_ATTEMPT_CLOCK_BINDING');
  }
  if(!obj(latest.abilityList)||latest.abilityList.apiAvailable!==true)
    return fail('CAPTURE_ATTEMPT_RESULT_LIST');
  for(const key of countKeys){
    if((complete||own(a.counts??{},key))&&
      (!integer(a.counts?.[key],1048576)||a.counts[key]!==latest.abilityList[key]))
      return fail('CAPTURE_ATTEMPT_COUNT_BINDING');
  }
  if(complete&&!assessSnapshotForComparison(saved).offlineStructureQualified)
    return fail('CAPTURE_ATTEMPT_RESULT_STRUCTURE');
  return {...result,status:'validated',outcome:a.status,attemptSequence:a.attemptSequence,
    resultSequence:a.resultSequence,resultBound:true,completeResultBound:complete};
}
