import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import crypto from 'node:crypto';
import {classify,buildLaunch,validateRequest,runReview} from '../../agent-review-runner.mjs';
const request={schemaVersion:1,taskId:'WA-TEST',sourceSha256:'a'.repeat(64),requiredCoverage:['strict_load'],model:'openrouter/test:free'};
const review=()=>({schemaVersion:1,taskId:request.taskId,sourceSha256:request.sourceSha256,complete:true,coverage:['strict_load'],findings:[],summary:'The supplied parser rejects duplicate JSON keys and never treats saved data as current. Missing observations remain explicitly unavailable.',checks:['strict_load rejects duplicate keys before the observation is returned.','strict_load reports invalid UTF-8 instead of replacing damaged characters.','strict_load enforces a bounded input file size before parsing.'],limitations:['Static source review only.'],testExecution:'not-run'});
const events=(answer=review(),extra=[])=>[
  {type:'step_start',sessionID:'ses-test',part:{}},...extra,
  {type:'text',sessionID:'ses-test',part:{text:typeof answer==='string'?answer:JSON.stringify(answer)}},
  {type:'step_finish',sessionID:'ses-test',part:{reason:'stop'}}
].map(x=>JSON.stringify(x)).join('\n');
test('completed model response is not automatically manager accepted',()=>{
 const r=classify(events(),' ',0,request);assert.equal(r.semanticComplete,true);assert.equal(r.managerAccepted,false);
});
test('schema example echo is not an accepted review',()=>{const r=review();r.summary='assessment; empty findings array when no actual defect';delete r.checks;assert.equal(classify(events(r),'',0,request).semanticComplete,false);});
test('inline path uses bounded literal source and builtin plan',()=>{const r=buildLaunch({...request,delivery:'inline'},'unused','source code');assert.equal(r.args[r.args.indexOf('--agent')+1],'plan');assert(!r.args.includes('--file'));assert.equal(r.config.permission.edit,'deny');assert.throws(()=>buildLaunch({...request,delivery:'inline'},'x','a'.repeat(18001)),/18000/);});
test('exit zero without answer is incomplete',()=>assert.equal(classify('','',0,request).semanticComplete,false));
test('step-limit summary is not a review',()=>assert.equal(classify(events('Maximum steps for this agent have been reached.'),'',0,request).semanticComplete,false));
test('permission failure exit zero is incomplete',()=>assert.equal(classify(events(),'permission requested: read; auto-rejecting',0,request).semanticComplete,false));
test('source hash mismatch rejected',()=>{const r=review();r.sourceSha256='b'.repeat(64);assert.equal(classify(events(r),'',0,request).semanticComplete,false);});
test('missing coverage rejected',()=>{const r=review();r.coverage=[];assert.equal(classify(events(r),'',0,request).semanticComplete,false);});
test('provider error or tool event prevents success',()=>{for(const type of ['error','tool_use'])assert.equal(classify(events(review(),[{type,sessionID:'ses-test'}]),'',0,request).semanticComplete,false);});
test('bad primitive review is rejected',()=>{for(const answer of ['null','false','0','[]','"hello"'])assert.equal(classify(events(answer),'',0,request).semanticComplete,false,answer);});
test('timeout truncated output and changed source never complete',()=>{for(const flag of ['timedOut','outputTruncated','sourceChanged'])assert.equal(classify(events(),'',0,request,{[flag]:true}).semanticComplete,false);});
test('nonzero process exit does not pass on valid text',()=>assert.equal(classify(events(),'',1,request).semanticComplete,false));
test('different session IDs are rejected',()=>assert.equal(classify(events(review(),[{type:'step_start',sessionID:'other'}]),'',0,request).semanticComplete,false));
test('malformed findings rejected',()=>{const r=review();r.findings=[{severity:'critical'}];assert.equal(classify(events(r),'',0,request).semanticComplete,false);});
test('false completion or claimed test execution rejected',()=>{for(const [k,v] of [['complete',false],['testExecution','passed']]){const r=review();r[k]=v;assert.equal(classify(events(r),'',0,request).semanticComplete,false);}});
test('argv is literal; message precedes file list; no max-step trap',()=>{
 const r=buildLaunch(request,'space folder/packet.txt');assert.equal(r.args[0],'run');assert.equal(r.args.at(-2),'--file');assert.equal(r.args.at(-1),'space folder/packet.txt');assert(!r.args.includes('--auto'));assert(!('steps' in r.config.agent['rre-review']));assert.equal(r.config.permission['*'],'deny');
});
test('request pins, no-clobber and free model enforcement',()=>{
 const dir=fs.mkdtempSync(path.join(os.tmpdir(),'rre-review-test-'));
 try {const packet=path.join(dir,'packet.txt'),source=path.join(dir,'source.py');fs.writeFileSync(packet,'review this');fs.writeFileSync(source,'x = 1');
 const sha=p=>crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
 const r={...request,cwd:dir,packetPath:packet,sourcePath:source,packetSha256:sha(packet),sourceSha256:sha(source),executable:process.execPath,timeoutSeconds:30,outputDirectory:path.join(dir,'output')};
 assert.equal(validateRequest(r).packetBytes,11);assert.throws(()=>validateRequest({...r,model:'paid/model'}),/free/);assert.throws(()=>validateRequest({...r,sourceSha256:'b'.repeat(64)}),/Source SHA/);
 fs.mkdirSync(r.outputDirectory);assert.throws(()=>validateRequest(r),/already exists/);
 } finally {fs.rmSync(dir,{recursive:true,force:true});}
});
