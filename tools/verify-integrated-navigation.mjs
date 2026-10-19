#!/usr/bin/env node
/**
 * Verify the merged navigation follow-ups against immutable Git snapshots.
 * No runtime Rift access, process attach, input, or writes.
 *
 * Worker provenance is intentionally pinned to its historical source version.
 * Git for Windows can change working-tree CRLF without changing Git blob content.
 * Both facts are validated explicitly; hashes are never redefined.
 */
import crypto from 'node:crypto';
import fs from 'node:fs';
import path from 'node:path';
import { execFileSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';

const ROOT=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const GIT='C:\\Program Files\\Git\\cmd\\git.exe';
const BUILD='7c356c9dde9e12fcbff3c08d953b0630b48b1510a0ffb36e4ec164606e7b17bd';
const FIRST_WAVE='ca52df618921ac0cdc18c71592b46ec63ed6a25b';
const ROADMAP_WAVE='54bd35be6730158351a1805e39f19f4b8cac9137';
const SUCCESS=[
 {lane:'validation',worker:'d1668fd72ece9a571cf1922ed39056c1c24b1f97',main:'a4fac10'},
 {lane:'c2m',worker:'40554843379ea937321c13f115554ec950fbd759',main:'a7d2c4e'},
 {lane:'follow',worker:'2042ebc592a533b5bdf463e5e8e0ff49270481d6',main:'37a244a'},
 {lane:'collision',worker:'21a1d204dc7560adcba2276d381caf9767779097',main:'b023d66'}
];
const sha=b=>crypto.createHash('sha256').update(b).digest('hex');
const LF=b=>Buffer.from(b.toString('utf8').replace(/\r\n/g,'\n'),'utf8');
const CRLF=b=>Buffer.from(LF(b).toString('utf8').replace(/\n/g,'\r\n'),'utf8');
const fail=(ok,msg)=>{if(!ok)throw Error(msg)};
const git=(...a)=>execFileSync(GIT,a,{cwd:ROOT,encoding:null,maxBuffer:16_000_000});
const gitBlob=(ref,p)=>git('show',ref+':'+p);
const readRel=p=>fs.readFileSync(path.join(ROOT,p));
const matchesHash=(b,expected)=>[sha(b),sha(LF(b)),sha(CRLF(b))].includes(expected);
const records=[];
for (const item of SUCCESS) {
  const names=git('diff-tree','--no-commit-id','--name-only','-r',item.worker).toString('utf8').trim().split(/\r?\n/).filter(Boolean);
  fail(names.length>=3 && names.every(p=>p.startsWith('docs/agents/'+item.lane+'.') || p.startsWith('tools/agents/'+item.lane+'/')),
       'Out-of-lane worker files in '+item.lane);
  const paths=[];
  for (const p of names) {
    const historical=gitBlob(item.worker,p);
    const integrated=gitBlob(item.main,p);
    const local=readRel(p);
    fail(LF(historical).equals(LF(integrated)),item.lane+' changed during cherry-pick: '+p);
    fail(LF(integrated).equals(LF(local)),item.lane+' worktree data differs from merged Git blob: '+p);
    paths.push({path:p,workerBlobSha256:sha(historical),mainBlobSha256:sha(integrated),
      currentRawSha256:sha(local),eolOnlyTransformed:!historical.equals(local)&&LF(historical).equals(LF(local))});
  }
  records.push({lane:item.lane,originalWorkerCommit:item.worker,integratedCommit:item.main,
    validatedPaths:paths.length,paths});
}
fail(sha(fs.readFileSync('C:\\Program Files (x86)\\Glyph\\Games\\RIFT\\Live\\rift_x64.exe'))===BUILD,
  'Exact Rift research build changed');
const cj=JSON.parse(readRel('docs/agents/c2m.json'));
const f=cj.followUps.at(-1);
fail(f.taskId==='M2-001' && f.build.sha256===BUILD,'C2M follow-up/identity mismatch');
const sources=[];
for (const entry of f.sources) {
  const p=entry.path;
  let raw,sourceRef;
  const underMain=path.win32.isAbsolute(p) && p.toLowerCase().startsWith('c:\\work\\rre\\');
  const external=path.win32.isAbsolute(p) && !underMain;
  if (external) {
    raw=fs.readFileSync(p);
    sourceRef='external exact source';
    fail(sha(raw)===entry.sha256,'External C2M source changed: '+p);
  } else {
    const relative=underMain?p.slice('C:\\work\\rre\\'.length).replace(/\\/g,'/'):p.replace(/\\/g,'/');
    sourceRef=relative==='tools/agents/c2m/verify_m2_001.py'
      ? SUCCESS.find(x=>x.lane==='c2m').worker
      : underMain?ROADMAP_WAVE:FIRST_WAVE;
    raw=gitBlob(sourceRef,relative);
    fail(matchesHash(raw,entry.sha256),'Pinned C2M source hash cannot be reproduced from '+sourceRef+':'+relative);
  }
  sources.push({path:p,sourceRef,recordedSha256:entry.sha256,
    verification:'historical version / exact current external source',lineEndingVariant:sha(raw)!==entry.sha256});
}
for(const artifact of f.artifacts) {
  const p=artifact.path.replace(/\\/g,'/');
  fail(!path.win32.isAbsolute(p)&&p.startsWith('tools/agents/c2m/'),
       'Untrusted C2M artifact path: '+p);
  const committed=gitBlob(SUCCESS.find(x=>x.lane==='c2m').worker,p);
  const local=readRel(p);
  fail(matchesHash(committed,artifact.sha256),'Original C2M artifact hash mismatch: '+p);
  fail(LF(committed).equals(LF(local)),'Integrated C2M artifact semantic bytes differ: '+p);
}
const follow=JSON.parse(readRel('docs/agents/follow.json')).followUps.at(-1);
fail(follow.taskId==='M2-002','Missing M2-002 report');
const prev=follow.preservation;
const all=LF(readRel('docs/agents/follow.json'));
const reconstructed=Buffer.concat([all.subarray(0,prev.jsonPrefixBytes),Buffer.from('}'),Buffer.from(prev.jsonSuffixHex,'hex')]);
fail(sha(reconstructed)===prev.jsonSha256,'Historic follow JSON prefix mismatch even after CRLF normalization');
const md=readRel('docs/agents/follow.md');
fail(sha(md.subarray(0,prev.markdownBytes))===prev.markdownSha256,
     'Historic follow Markdown prefix mismatch');
const output={result:'passed',scope:'historical Git provenance and cherry-pick payload integrity, not live semantic validation',
  exactBuildSha256:BUILD,lanes:records.map(r=>({lane:r.lane,originalWorkerCommit:r.originalWorkerCommit,
    integratedCommit:r.integratedCommit,ownedPaths:r.validatedPaths,eolOnlyPaths:r.paths.filter(p=>p.eolOnlyTransformed).length})),
  c2mHistoricalSources:sources.length,c2mArtifacts:f.artifacts.length,
  followPrefixIntegrity:true,
  warnings:['Versioned historical source hashes are intentionally different from newer main; recovered from pinned Git blobs.',
    'Git EOL conversion is normalized for content equivalence without redefining original raw SHA256.',
    'Instruction decoding/semantic evidence independently checked by lane-specific Python verifiers in source worktrees.']
};
process.stdout.write(JSON.stringify(output,null,2)+'\n');
