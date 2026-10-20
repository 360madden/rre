#!/usr/bin/env node
// RRE single-review adapter. Direct argv, pinned packet, durable logs, semantic completion.
// No dependencies or global config changes. Does not execute the reviewed source.
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import { spawn, spawnSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';

export const MAX_PACKET_BYTES = 128 * 1024;
export const MAX_OUTPUT_BYTES = 2 * 1024 * 1024;
const hash = (b) => crypto.createHash('sha256').update(b).digest('hex');
const check = (v, message) => { if (!v) throw new Error(message); };
const nonempty = (v) => typeof v === 'string' && v.trim().length > 0;
const hexSha = (s) => typeof s === 'string' && /^[a-f0-9]{64}$/.test(s);
const resolve = (p) => path.resolve(p);

export function validateRequest(r) {
  check(r && typeof r === 'object' && !Array.isArray(r) && r.schemaVersion === 1, 'Unsupported review request');
  check(/^[A-Za-z0-9_-]{1,100}$/.test(r.taskId || ''), 'Invalid taskId');
  for (const k of ['cwd','executable','packetPath','sourcePath','outputDirectory'])
    check(nonempty(r[k]) && path.isAbsolute(r[k]), `Absolute ${k} required`);
  check(hexSha(r.sourceSha256) && hexSha(r.packetSha256), 'Pinned source/packet SHA256 required');
  check(r.delivery === undefined || r.delivery === 'inline' || r.delivery === 'file', 'Unsupported packet delivery');
  check(nonempty(r.model) && r.model.endsWith(':free') && r.model.startsWith('openrouter/'),
        'Only explicitly selected OpenRouter :free models supported by this adapter');
  check(Number.isInteger(r.timeoutSeconds) && r.timeoutSeconds >= 15 && r.timeoutSeconds <= 300, 'Deadline must be 15..300 seconds');
  check(Array.isArray(r.requiredCoverage) && r.requiredCoverage.length > 0 && r.requiredCoverage.length <= 60 &&
        r.requiredCoverage.every(nonempty) && new Set(r.requiredCoverage).size === r.requiredCoverage.length,
        'Nonempty unique requiredCoverage required');
  check(fs.statSync(r.cwd).isDirectory() && fs.statSync(r.executable).isFile(), 'Missing cwd or executable');
  const relative = path.relative(resolve(r.cwd), resolve(r.packetPath));
  check(relative !== '' && !relative.startsWith('..' + path.sep) && relative !== '..' && !path.isAbsolute(relative),
        'Packet must be inside the review worktree');
  check(!fs.existsSync(r.outputDirectory), 'Output directory already exists; choose a new run ID');
  const packet = fs.readFileSync(r.packetPath);
  check(packet.length > 0 && packet.length <= MAX_PACKET_BYTES, 'Packet is empty or exceeds 128 KiB');
  check(hash(packet) === r.packetSha256, 'Packet SHA mismatch');
  check(hash(fs.readFileSync(r.sourcePath)) === r.sourceSha256, 'Source SHA mismatch');
  return { packetBytes: packet.length, relativePacket: relative };
}

export function buildLaunch(r, relativePacket, packetText = null) {
  // Deliberately OMIT steps:1: OpenCode injects a max-step summary before the review.
  const config = {
    autoupdate: false,
    permission: { '*': 'deny' },
    agent: { 'rre-review': { description: 'Bounded independent source review; attached evidence only',
      mode: 'primary', permission: { '*': 'deny' },
      prompt: 'All source is included in the attached packet. Review it without tools. Do not request tools, execute commands, ask questions, or output a plan. Return the requested completed JSON assessment only. Do not claim tests ran.' } },
  };
  const prompt = `Perform an independent source review NOW, not a plan. Task ${r.taskId}. ` +
    `Output only one JSON object with schemaVersion=1, taskId=${JSON.stringify(r.taskId)}, sourceSha256=${JSON.stringify(r.sourceSha256)}, complete=true, testExecution="not-run". ` +
    `Required coverage array: ${JSON.stringify(r.requiredCoverage)}. Read every listed function. ` +
    'Include findings: an array (empty is allowed); each finding must contain severity (low/medium/high/critical), location, description and a concrete counterexample. ' +
    'Include summary: TWO ORIGINAL SOURCE-SPECIFIC SENTENCES; checks: at least THREE original strings identifying a function, its actual behavior and an edge case you checked; limitations: an array of strings. ' +
    'Do not copy schema descriptions as your answer. Do not claim tests ran. Use supplied code only; do not call tools.';
  if (r.delivery === 'inline') {
    check(typeof packetText === 'string' && packetText.length <= 18000, 'Inline packet exceeds 18000 characters');
    const inlineConfig = {autoupdate:false,permission:{edit:'deny',bash:'deny',task:'deny',
      external_directory:'deny',webfetch:'deny',websearch:'deny',question:'deny'}};
    return {args:['run',prompt+'\n\nSUPPLIED SOURCE PACKET:\n'+packetText,'--pure','--agent','plan',
      '--model',r.model,'--format','json'],config:inlineConfig};
  }
  return {args:['run',prompt,'--pure','--agent','rre-review','--model',r.model,'--format','json','--file',relativePacket],config};
}

export function classify(stdout, stderr, exitCode, request, flags = {}) {
  const sessions = new Set(), texts = [], reasons = [], coverage = [];
  let stopped = false, tools = 0, errors = 0;
  if (exitCode !== 0) reasons.push('process-nonzero-or-no-exit');
  if (flags.timedOut) reasons.push('deadline-exhausted');
  if (flags.outputTruncated) reasons.push('output-limit-exceeded');
  if (flags.sourceChanged) reasons.push('source-or-packet-changed-during-review');
  for (const line of stdout.split(/\r?\n/).filter(s => s.trim())) {
    let e;
    try { e = JSON.parse(line); } catch { reasons.push('non-json-event-output'); continue; }
    if (typeof e.sessionID === 'string') sessions.add(e.sessionID);
    if (e.type === 'text' && typeof e.part?.text === 'string') texts.push(e.part.text);
    if (e.type === 'step_finish' && e.part?.reason === 'stop') stopped = true;
    if (e.type === 'tool_use' || e.part?.type === 'tool') tools++;
    if (e.type === 'error') errors++;
  }
  if (sessions.size !== 1) reasons.push('missing-or-ambiguous-independent-session');
  if (!stopped) reasons.push('no-terminal-model-stop');
  if (tools) reasons.push('reviewer-attempted-tools');
  if (errors) reasons.push('provider-error-event');
  const answer = texts.join('\n').trim();
  let review = null;
  try { review = JSON.parse(answer.replace(/^```(?:json)?\s*/, '').replace(/\s*```$/, '')); }
  catch { reasons.push('missing-structured-review'); }
  if (review === null || typeof review !== 'object' || Array.isArray(review)) {
    reasons.push('review-must-be-json-object');
    review = null;
  }
  if (review) {
    if (review.schemaVersion !== 1 || review.taskId !== request.taskId ||
        review.sourceSha256 !== request.sourceSha256 || review.complete !== true || review.testExecution !== 'not-run')
      reasons.push('review-identity-or-completion-mismatch');
    if (!Array.isArray(review.coverage) || !request.requiredCoverage.every(k => review.coverage.includes(k)))
      reasons.push('review-coverage-incomplete');
    else coverage.push(...review.coverage);
    if (!nonempty(review.summary) || review.summary.length < 60 ||
        /assessment; empty findings|your own summary|source-specific sentences/i.test(review.summary) ||
        !Array.isArray(review.limitations) || !review.limitations.every(nonempty))
      reasons.push('review-summary-or-limitations-invalid');
    if (!Array.isArray(review.checks) || review.checks.length < 3 ||
        !review.checks.every(s => nonempty(s) && s.length >= 30))
      reasons.push('missing-source-specific-review-checks');
    if (!Array.isArray(review.findings) || review.findings.length > 20 || !review.findings.every(f => f &&
        ['low','medium','high','critical'].includes(f.severity) && nonempty(f.location) && nonempty(f.description) && nonempty(f.counterexample)))
      reasons.push('review-findings-invalid');
  }
  if (/maximum steps .* reached|no .*review .*performed|no concrete findings .*produced|permission .*reject/i.test(answer))
    reasons.push('model-declared-noncompletion');
  if (/permission .*reject|file not found|invalid config|api error|provider.*error/i.test(stderr))
    reasons.push('launcher-or-provider-diagnostic');
  return {status: reasons.length ? 'incomplete' : 'review-produced', processExitCode:exitCode,
    semanticComplete:reasons.length === 0, managerAccepted:false, reasons:[...new Set(reasons)],
    sessionIds:[...sessions], coverage, toolEvents:tools, review, answer};
}

function writeJson(target, value) {
  fs.writeFileSync(target, JSON.stringify(value,null,2)+'\n', {flag:'wx'});
}

export async function runReview(requestPath) {
  const requestRaw = fs.readFileSync(requestPath);
  check(requestRaw.length <= 65536, 'Request exceeds 64 KiB');
  const r = JSON.parse(requestRaw.toString('utf8'));
  const pin = validateRequest(r);
  const launch = buildLaunch(r, pin.relativePacket, fs.readFileSync(r.packetPath,'utf8'));
  fs.mkdirSync(r.outputDirectory); // Existing parent required; no overwrite.
  writeJson(path.join(r.outputDirectory,'request.json'),r);
  writeJson(path.join(r.outputDirectory,'started.json'), {schemaVersion:1,taskId:r.taskId,
    startedAt:new Date().toISOString(),requestSha256:hash(requestRaw),sourceSha256:r.sourceSha256,
    packetSha256:r.packetSha256,argv:launch.args,agentConfig:launch.config,semanticComplete:false});
  const stdoutFd = fs.openSync(path.join(r.outputDirectory,'stdout.jsonl'),'wx');
  const stderrFd = fs.openSync(path.join(r.outputDirectory,'stderr.log'),'wx');
  let stdout = '', stderr = '', kept = 0, timedOut = false, outputTruncated = false, spawnFailure = null;
  const env = {...process.env, OPENCODE_CONFIG_CONTENT:JSON.stringify(launch.config)};
  const child = spawn(r.executable, launch.args, {cwd:r.cwd,env,windowsHide:true,shell:false,
    detached:process.platform !== 'win32',stdio:['ignore','pipe','pipe']});
  const kill = () => {
    if (!child.pid || child.exitCode !== null || child.signalCode !== null) return;
    if (process.platform === 'win32') spawnSync('taskkill.exe',['/PID',String(child.pid),'/T','/F'],{windowsHide:true,stdio:'ignore'});
    else { try { process.kill(-child.pid,'SIGKILL'); } catch {} }
  };
  const append = (buf, stream) => {
    const room = MAX_OUTPUT_BYTES-kept, part = buf.subarray(0,Math.max(0,room));
    fs.writeSync(stream === 'stdout' ? stdoutFd : stderrFd,part); kept += part.length;
    if (stream === 'stdout') stdout += part.toString('utf8'); else stderr += part.toString('utf8');
    if (buf.length > room) { outputTruncated = true; kill(); }
  };
  child.stdout.on('data', b => append(b,'stdout')); child.stderr.on('data', b => append(b,'stderr'));
  const timer = setTimeout(() => {timedOut=true;kill();},r.timeoutSeconds*1000);
  const exitCode = await new Promise(resolveExit => {
    child.once('error',e => {spawnFailure=e.code || 'spawn-error';});
    child.once('close',code => resolveExit(code));
  });
  clearTimeout(timer); fs.closeSync(stdoutFd);fs.closeSync(stderrFd);
  // Decode from complete retained bytes, not independently decoded stream chunks.
  stdout = fs.readFileSync(path.join(r.outputDirectory,'stdout.jsonl'),'utf8');
  stderr = fs.readFileSync(path.join(r.outputDirectory,'stderr.log'),'utf8');
  let sourceChanged = true;
  try { sourceChanged = hash(fs.readFileSync(r.sourcePath)) !== r.sourceSha256 || hash(fs.readFileSync(r.packetPath)) !== r.packetSha256; } catch {}
  const result = {schemaVersion:1,taskId:r.taskId,modelRequested:r.model,reasoningLevel:'',
    sourceSha256:r.sourceSha256,packetSha256:r.packetSha256,endedAt:new Date().toISOString(),
    timedOut,outputTruncated,spawnFailure,stdoutSha256:hash(fs.readFileSync(path.join(r.outputDirectory,'stdout.jsonl'))),
    stderrSha256:hash(fs.readFileSync(path.join(r.outputDirectory,'stderr.log'))),
    ...classify(stdout,stderr,exitCode,r,{timedOut,outputTruncated,sourceChanged})};
  if (spawnFailure) {result.semanticComplete=false;result.status='incomplete';result.reasons.push(spawnFailure);}
  writeJson(path.join(r.outputDirectory,'result.json'),result);
  return result;
}

if (process.argv[1] && resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  try {
    check(process.argv.length === 4 && process.argv[2] === '--request', 'Usage: node tools/agent-review-runner.mjs --request PATH');
    const r = await runReview(resolve(process.argv[3]));
    console.log(JSON.stringify({taskId:r.taskId,status:r.status,semanticComplete:r.semanticComplete,
      managerAccepted:false,sessionIds:r.sessionIds,reasons:r.reasons}));
    process.exitCode = r.semanticComplete ? 0 : 2;
  } catch(e) {console.error(JSON.stringify({status:'failed',error:e.message,semanticComplete:false}));process.exitCode=2;}
}
