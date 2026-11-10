#!/usr/bin/env node
// Bounded, offline REA investigation using the already installed MCP SDK.
// Never attaches to Rift, sends game input, invokes game code, or changes REA config.
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import os from 'node:os';
import { createRequire } from 'node:module';
import { pathToFileURL } from 'node:url';

const optionsPath = process.argv[2];
const preflightOnly = process.argv.length === 4 && process.argv[3] === '--preflight';
if (!optionsPath || (process.argv.length !== 3 && !preflightOnly)) {
  console.error('Usage: node tools/rea-session.mjs <absolute-session-options.json> [--preflight]');
  process.exit(2);
}
const cfg = JSON.parse(fs.readFileSync(optionsPath, 'utf8'));
const host = os.hostname();
if (cfg.expectedHost && host.toUpperCase() !== String(cfg.expectedHost).toUpperCase()) {
  throw new Error('Session host mismatch: expected ' + cfg.expectedHost + ', observed ' + host);
}
const sourceFormat = cfg.format ?? 'pe';
// REA open_binary may auto-import an entire PE before any focused query executes.
// Only an explicit, config-owned opt-in can allow that expensive operation.
if (!preflightOnly && sourceFormat === 'pe' && cfg.allowFullPeImport !== true) {
  throw new Error('Full PE import blocked; allowFullPeImport must be explicitly true.');
}
const expected = String(cfg.expectedSha256 || '').toLowerCase();
if (!/^[0-9a-f]{64}$/.test(expected)) throw new Error('Expected SHA-256 must be a 64-digit hex digest.');
const out = path.resolve(cfg.outputDirectory);
function ensureOutputAdmissible(directory) {
  if (!fs.existsSync(directory)) return;
  // Requests may be pre-staged; any prior response or receipt makes the session immutable.
  const unexpected = fs.readdirSync(directory).filter(name =>
    name !== 'requests' && name !== 'responses');
  const repliesDir = path.join(directory, 'responses');
  if (unexpected.length ||
      (fs.existsSync(repliesDir) && fs.readdirSync(repliesDir).length)) {
    throw new Error('Session output contains prior evidence; choose a new outputDirectory.');
  }
}
function inspectSourceFormat(bytes, format, options) {
  if (format === 'pe') {
    if (bytes.length < 128) throw new Error('PE file too small.');
    const pe = bytes.readUInt32LE(0x3c);
    if (pe + 56 > bytes.length ||
        bytes.toString('ascii',0,2) !== 'MZ' ||
        bytes.readUInt32LE(pe) !== 0x4550 ||
        bytes.readUInt16LE(pe+4) !== 0x8664) throw new Error('Expected x64 PE.');
    return bytes.readBigUInt64LE(pe+24+24);
  }
  if (format === 'raw-binary') {
    if (options.architecture !== 'x86_64' ||
        typeof options.entryPoint !== 'string' ||
        !/^0x[0-9a-fA-F]{1,16}$/.test(options.entryPoint) ||
        bytes.length < 1 || bytes.length > 65536) {
      throw new Error('Raw probe requires x86_64, valid entryPoint and 1..65536 bytes.');
    }
    const base = BigInt(options.entryPoint);
    if (base + BigInt(bytes.length) > (1n << 64n)) {
      throw new Error('Raw probe address range exceeds 64-bit space.');
    }
    return base;
  }
  throw new Error('Unsupported analysis input format.');
}
if (preflightOnly) {
  const source = fs.readFileSync(cfg.binary);
  const actual = crypto.createHash('sha256').update(source).digest('hex');
  if (actual !== expected) throw new Error('Preflight target SHA-256 mismatch.');
  const imageBase = inspectSourceFormat(source, sourceFormat, cfg);
  ensureOutputAdmissible(out);
  const reaMetadata = JSON.parse(fs.readFileSync(path.join(cfg.reaHome, 'node_modules', 'rea-agents', 'package.json'), 'utf8'));
  if (reaMetadata.version !== cfg.expectedReaVersion) throw new Error('Preflight REA version mismatch.');
  const headless = path.join(cfg.ghidraHome, 'support', process.platform === 'win32' ? 'analyzeHeadless.bat' : 'analyzeHeadless');
  const java = path.join(cfg.javaHome, 'bin', process.platform === 'win32' ? 'java.exe' : 'java');
  if (!fs.existsSync(headless) || !fs.existsSync(java)) throw new Error('Preflight Ghidra or Java executable missing.');
  console.log(JSON.stringify({mode:'preflight', host, source:cfg.binary,
    size:source.length, sha256:actual, format:sourceFormat,
    imageBase:'0x'+imageBase.toString(16), reaVersion:reaMetadata.version,
    ghidraHeadless:headless, java, fullPeImportAllowed:cfg.allowFullPeImport === true,
    analysisStarted:false, sessionFilesCreated:false}));
  process.exit(0);
}
const queue = path.join(out, 'requests');
const replies = path.join(out, 'responses');
ensureOutputAdmissible(out);
const started = Date.now();
const deadline = started + Math.min(550, cfg.durationSeconds ?? 550) * 1000;
const allowed = new Set([
  'binary_session', 'binary_overview', 'list_segments',
  'search_strings', 'search_procedures', 'xrefs',
  'resolve_containing_procedure', 'procedure_info', 'procedure_pseudo_code',
  'procedure_assembly', 'procedure_callers', 'procedure_callees',
  'procedure_references', 'read_function_instructions',
  'inspect_native_instruction', 'resolve_native_call_targets',
  'read_bytes', 'search_bytes', 'address_to_file_offset',
  'get_evidence_bundle', 'inspect_analysis_view'
]);
fs.mkdirSync(queue, {recursive:true});
fs.mkdirSync(replies, {recursive:true});
const status = {
  schemaVersion:1, state:'starting', startedAt:new Date(started).toISOString(),
  target:cfg.binary, expectedSha256:expected, completed:[], failures:[],
  current:null, phase:'identity', offlineOnly:true,
  gameInputSent:false, gameProcessAttached:false, targetExecuted:false
};
function save(file, value) {
  // Status is mutable progress; all other evidence/receipts are write-once.
  fs.writeFileSync(path.join(out, file), JSON.stringify(value, null, 2) + '\n',
    {encoding:'utf8',flag:file === 'status.json' ? 'w' : 'wx'});
}
function progress(phase, detail = {}) {
  status.phase = phase;
  status.updatedAt = new Date().toISOString();
  Object.assign(status, detail);
  save('status.json', status);
  console.log(JSON.stringify({time:status.updatedAt, phase, current:status.current,
    completed:status.completed.length, ...detail}));
}
const sleep = ms => new Promise(resolve => setTimeout(resolve, ms));
let client, transport, opened = false, stopped = false, timer;
let stderr = '';
const doneFiles = new Set();
try {
  const originalBytes = fs.readFileSync(cfg.binary);
  const digest = crypto.createHash('sha256').update(originalBytes).digest('hex');
  if (digest !== expected) throw new Error('Target SHA256 does not match qualified build.');
  const loadFormat = sourceFormat;
  const imageBase = inspectSourceFormat(originalBytes, loadFormat, cfg);
  status.identity = {sha256:digest, size:originalBytes.length,
    format:loadFormat, imageBase:'0x'+imageBase.toString(16), sourcePath:cfg.binary};
  save('identity.json', status.identity);
  const reaRequire = createRequire(path.join(cfg.reaHome, 'package.json'));
  const {Client} = await import(pathToFileURL(reaRequire.resolve('@modelcontextprotocol/client')).href);
  const {StdioClientTransport} = await import(pathToFileURL(reaRequire.resolve('@modelcontextprotocol/client/stdio')).href);
  const reaPackage = JSON.parse(fs.readFileSync(path.join(cfg.reaHome,'node_modules','rea-agents','package.json'),'utf8'));
  if (reaPackage.version !== cfg.expectedReaVersion) throw new Error('REA version changed; review contracts.');
  const childEnv = {
    ...process.env,
    GHIDRA_INSTALL_DIR:cfg.ghidraHome,
    JAVA_HOME:cfg.javaHome,
    REA_ANALYSIS_PROVIDER:'ghidra',
    REA_GHIDRA_STARTUP_TIMEOUT_MS:String(cfg.startupTimeoutMs ?? 450000)
  };
  delete childEnv.REA_GHIDRA_DISABLED_ANALYZERS;
  delete childEnv.REA_GHIDRA_SEED_FILE;
  if (cfg.disabledAnalyzers?.length)
    childEnv.REA_GHIDRA_DISABLED_ANALYZERS = cfg.disabledAnalyzers.join(',');
  if (cfg.seedFile) childEnv.REA_GHIDRA_SEED_FILE = cfg.seedFile;
  save('analysis-profile.json', {reaVersion:reaPackage.version, ghidraHome:cfg.ghidraHome,
    javaHome:cfg.javaHome, startupTimeoutMs:Number(childEnv.REA_GHIDRA_STARTUP_TIMEOUT_MS),
    disabledAnalyzers:cfg.disabledAnalyzers ?? [], seedFile:cfg.seedFile ?? null,
    limitations:['Static analysis only; configured analyzer omissions reduce coverage.',
      'No route or collision semantics are established merely by names or addresses.']});
  client = new Client({name:'rre-navigation-research', version:'0.1.0'});
  transport = new StdioClientTransport({
    command:process.execPath,
    args:[path.join(cfg.reaHome,'node_modules','rea-agents','scripts','rea.mjs'),'mcp'],
    cwd:cfg.reaHome, env:childEnv, stderr:'pipe'
  });
  transport.stderr?.on('data', chunk => {
    stderr = (stderr + chunk.toString()).slice(-120000);
    fs.writeFileSync(path.join(out,'rea-stderr.log'),stderr,'utf8');
  });
  progress('connect');
  await client.connect(transport,{timeout:30000});
  status.server = client.getServerVersion();
  const catalog = [];
  let cursor;
  do {
    const page = await client.listTools(cursor ? {cursor} : undefined);
    catalog.push(...page.tools);
    cursor = page.nextCursor;
  } while (cursor);
  save('tool-contracts.json',catalog.filter(t=>allowed.has(t.name) ||
    ['open_binary','close_binary','export_evidence_bundle'].includes(t.name)));
  const names = new Set(catalog.map(t=>t.name));
  async function call(name, args, timeoutMs) {
    if (!names.has(name)) throw new Error('Operation absent from installed catalog: '+name);
    return client.callTool({name,arguments:args},{timeout:timeoutMs,
      onprogress:p=>{ status.providerProgress=p; save('status.json',status); }});
  }
  progress('open-binary');
  const openTimeout = Math.min((cfg.startupTimeoutMs ?? 450000) + 20000, deadline-Date.now()-60000);
  const openArgs = loadFormat === 'raw-binary'
    ? {path:cfg.binary,format:'raw-binary',architecture:'x86_64',
       entry_point:cfg.entryPoint,provider_id:'ghidra'}
    : {path:cfg.binary,provider_id:'ghidra'};
  const open = await call('open_binary',openArgs,openTimeout);
  save('open-binary.json',open);
  if (open.isError) throw new Error('REA rejected open_binary; inspect open-binary.json.');
  opened = true; // Still close provider resources if admission identity is wrong.
  const admitted = open.structuredContent?.result;
  if (!admitted || typeof admitted.sha256 !== 'string' ||
      admitted.sha256.toLowerCase() !== expected ||
      admitted.architecture !== 'x86_64' || admitted.format !== loadFormat ||
      typeof admitted.path !== 'string' ||
      path.win32.normalize(admitted.path).toLowerCase() !==
        path.win32.normalize(cfg.binary).toLowerCase()) {
    throw new Error('REA provider target identity mismatch; no analysis queries allowed.');
  }
  status.state = 'running';
  progress('ready');
  timer = setInterval(()=>progress(status.phase),15000);
  timer.unref();
  while (Date.now() < deadline - 45000 && !stopped) {
    const pending = fs.readdirSync(queue).filter(f=>/^[a-zA-Z0-9_.-]+\.json$/.test(f)
      && !doneFiles.has(f)).sort();
    if (!pending.length) { await sleep(500); continue; }
    const filename = pending[0];
    const request = JSON.parse(fs.readFileSync(path.join(queue,filename),'utf8'));
    if (request.finish === true) { doneFiles.add(filename); stopped=true; break; }
    if (!allowed.has(request.tool)) throw new Error('Unapproved offline operation: '+request.tool);
    const args = request.arguments ?? {};
    const timeoutMs = Math.min(request.timeoutMs ?? 480000, deadline-Date.now()-40000);
    if (timeoutMs < 1000) break;
    const requestStart = Date.now();
    progress('query',{current:filename,tool:request.tool});
    let result;
    try {
      result = await call(request.tool,args,timeoutMs);
    } catch (error) {
      const failure = {request,startedAt:new Date(requestStart).toISOString(),
        endedAt:new Date().toISOString(),error:String(error)};
      save(path.join('responses',filename),failure);
      throw error;
    }
    save(path.join('responses',filename),{
      request,startedAt:new Date(requestStart).toISOString(),endedAt:new Date().toISOString(),
      elapsedMs:Date.now()-requestStart,result
    });
    doneFiles.add(filename);
    status.completed.push({file:filename,tool:request.tool,isError:!!result.isError,
      elapsedMs:Date.now()-requestStart});
    if (result.isError) {
      status.failures.push({file:filename,reason:'REA tool error; inspect saved response.'});
      // A cancelled/failed import must not silently trigger another full import.
      status.state='blocked';
      break;
    }
    progress('ready',{current:null,tool:null});
  }
  if (status.state === 'running') status.state = stopped ? 'completed' : 'time-budget-reached';
} catch (error) {
  status.state='failed';
  status.failures.push({error:String(error)});
  progress('error',{error:String(error)});
} finally {
  if (timer) clearInterval(timer);
  if (client && opened) {
    progress('export-evidence',{current:null});
    try {
      const exported = await client.callTool({name:'export_evidence_bundle',
        arguments:{path:path.join(out,'evidence.json'),overwrite:false}},{timeout:20000});
      save('export-receipt.json',exported);
      if (exported.isError) status.failures.push({stage:'export',reason:'REA export error'});
    } catch(error) { status.failures.push({stage:'export',error:String(error)}); }
    progress('close-binary');
    try {
      const closed = await client.callTool({name:'close_binary',
        arguments:{snapshot_path:path.join(out,'analysis-snapshot.json'),overwrite:false}},
        {timeout:20000});
      save('close-receipt.json',closed);
      if (closed.isError) status.failures.push({stage:'close',reason:'REA close error'});
    } catch(error) { status.failures.push({stage:'close',error:String(error)}); }
  }
  if (client) { try { await client.close(); } catch(error) {
    status.failures.push({stage:'client-close',error:String(error)});
  }}
  status.endedAt = new Date().toISOString();
  status.elapsedMs = Date.now()-started;
  progress('finished',{current:null});
  process.exitCode = status.failures.length || status.state !== 'completed' ? 1 : 0;
}
