// WA-006: compare two Lua API unit witnesses without treating either as native proof.
// The Collector chooses sorted IDs; the historical G2 probe chooses early unordered IDs.
// No process, scene or time attestation is available from these files alone.
import {createHash} from 'node:crypto';
import {openSync, fstatSync, readSync, closeSync} from 'node:fs';
import {resolve} from 'node:path';
import {fileURLToPath} from 'node:url';
import {readUnitWitness} from '../../export-rrecollector-units.mjs';
import {validatePacket} from './verify_wa006_g2_packet.mjs';

const UID=/^u[0-9a-fA-F]{16}$/;
const hash=raw=>createHash('sha256').update(raw).digest('hex');
const canonical=id=>typeof id==='string'&&UID.test(id)?id.toLowerCase():null;
function boundedG2File(file){
  const fd=openSync(file,'r');
  try{
    const stat=fstatSync(fd);
    if(!stat.isFile()||!Number.isSafeInteger(stat.size)
      ||stat.size===0||stat.size>=12000)throw Error('G2_SOURCE_SIZE');
    const bytes=Buffer.alloc(stat.size);
    let offset=0;
    while(offset<bytes.length){
      const count=readSync(fd,bytes,offset,bytes.length-offset,offset);
      if(count<=0)throw Error('G2_SOURCE_SHORT_READ');
      offset+=count;
    }
    if(readSync(fd,Buffer.alloc(1),0,1,offset)!==0)throw Error('G2_SOURCE_CHANGED');
    return bytes;
  }finally{closeSync(fd);}
}
function parsePacket(raw) {
  const text=Buffer.from(raw).toString('utf8').replace(/\r\n/g,'\n').trimEnd();
  const lines=text.split('\n');
  const start=/^WA006_G2_V1\|BEGIN\|self=(u[0-9a-fA-F]{16})\|/.exec(lines[0]??'');
  if(!start)throw Error('G2_SELF_MISSING');
  const rows=new Map();
  for(const line of lines.slice(1,-1)){
    const m=/^WA006_G2_V1\|ROW\|id=(u[0-9a-fA-F]{16})\|specifier=[^|]+\|x=([^|]+)\|y=([^|]+)\|z=([^|]+)\|idBinding=matched$/.exec(line);
    if(m && [m[2],m[3],m[4]].every(x=>x!=='unknown')) {
      const id=canonical(m[1]);
      rows.set(id,{id,xyz:[Number(m[2]),Number(m[3]),Number(m[4])]});
    }
  }
  return {selfId:canonical(start[1]),rows};
}
export function triageCollectorG2(collector, g2Raw) {
  const reasons=[], limitations=[
    'both-sources-use-Lua-Inspect-Unit-API-not-independent-native-proof',
    'collector-sorts-eligible-IDs-G2-selects-during-unordered-enumeration',
    'independent-host-UTC-and-process-epoch-unavailable',
    'same-scene-and-coordinate-time-calibration-unavailable'
  ];
  const packet=validatePacket(g2Raw);
  const snapshot=collector?.snapshots?.[0];
  if(!snapshot || collector?.evidenceKind!=='rre-unit-witness/1'
    || collector?.producerVersion!=='0.4.23') reasons.push('invalid-collector-receipt');
  if(!packet.packetStructurallyReady)reasons.push('invalid-G2-packet');
  let shared=[],collectorIds=0,g2Ids=0,selfMatch=false,maxAxisDelta=null;
  if(reasons.length===0){
    const parsed=parsePacket(g2Raw);
    selfMatch=canonical(snapshot.selfId)===parsed.selfId;
    if(!selfMatch)reasons.push('self-unit-ID-mismatch');
    if(snapshot.status!=='complete'||!snapshot.coverage?.listEnumerationComplete
      ||!snapshot.coverage?.detailSampleComplete) reasons.push('collector-sample-incomplete');
    const c=new Map();
    for(const row of snapshot.records??[])if(row.idBinding==='matched'&&row.xyzComplete===true){
      const k=canonical(row.id);
      if(k&&k!==canonical(snapshot.selfId)) c.set(k,[row.coordX,row.coordY,row.coordZ]);
    }
    collectorIds=c.size;g2Ids=parsed.rows.size;
    shared=[...c.keys()].filter(k=>parsed.rows.has(k)).sort();
    if(shared.length<2)reasons.push('fewer-than-two-shared-Lua-API-IDs');
    // Numerical differences are observations, not failure or positive proof:
    // the two serial captures have no authenticated shared UTC bracket.
    if(shared.length){
      maxAxisDelta=Math.max(...shared.flatMap(k=>c.get(k).map((v,i)=>
        Math.abs(v-parsed.rows.get(k).xyz[i]))));
      if(maxAxisDelta!==0)limitations.push('serial-coordinate-values-differ-without-time-alignment');
    }
  }
  return {schemaVersion:1,evidenceKind:'collector-g2-Lua-API-triage/1',
    status:reasons.length?'rejected':'API-ID-overlap-unqualified',
    reasons,limitations,collectorSnapshotSequence:snapshot?.sequence??null,
    collectorSourceSha256:collector?.sourceSha256??null,
    g2TranscriptSha256:hash(Buffer.from(g2Raw)),
    collectorQualifiedNonself:collectorIds,g2QualifiedNonself:g2Ids,
    sharedNonselfCount:shared.length,sharedNonselfIds:shared,
    selfIdAgrees:selfMatch,maxAxisDeltaObserved:maxAxisDelta,
    sameSceneVerified:false,sameEpochVerified:false,
    nativeCorrelationDone:false,wa006Accepted:false};
}
if(process.argv[1] && resolve(process.argv[1])===fileURLToPath(import.meta.url)){
  try{
    if(process.argv.length!==4)throw Error('TRIAGE_USAGE');
    const collector=readUnitWitness(process.argv[2]);
    const raw=boundedG2File(process.argv[3]);
    const result=triageCollectorG2(collector,raw);
    process.stdout.write(JSON.stringify(result)+'\n');
    if(result.status==='rejected')process.exitCode=1;
  }catch(error){
    process.stderr.write(JSON.stringify({status:'failed',reason:String(error?.message||'TRIAGE_FAILED')})+'\n');
    process.exitCode=2;
  }
}
