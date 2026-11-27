// Portable RRE regression gate; never requires a game instance or installs dependencies.
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {spawnSync} from 'node:child_process';

const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const args=process.argv.slice(2);
const mode=args[0]??'--portable';
if(args.length>1||!['--portable','--local-source'].includes(mode)){
  console.error('Usage: node tools/run-offline-regression-gate.mjs [--portable|--local-source]');
  process.exit(2);
}
const env={...process.env,RRE_PAB_TEST_MODE:mode==='--portable'?'fixtures-only':'source-required'};
const cases=[
  'tools/test-pinned-lua51.mjs',
  'tools/test-export-rrecollector-units.mjs',
  'tools/test-audit-rrecollector-readiness.mjs',
  'tools/test-compare-rrecollector-captures.mjs',
  'tools/verify-rrecollector-saved.mjs',
  'tools/test-plan-pab-static-candidates.mjs',
  'tools/test-inventory-pab-static-abilities.mjs',
  'tools/agents/collision/test_verify_wa006_g2_packet.mjs',
  'tools/agents/collision/test_verify_wa006_g2_cross_source_preflight.mjs',
];
function run(name,argv){
  console.log('RRE_GATE_START '+name);
  const r=spawnSync(process.execPath,argv,{cwd:root,env,stdio:'inherit',shell:false,
    timeout:120000,windowsHide:true});
  if(r.error||r.status!==0){
    console.error('RRE_GATE_FAILED '+name+' '+(r.error?.message??String(r.status)));
    process.exit(r.status&&r.status>0?r.status:1);
  }
  console.log('RRE_GATE_PASSED '+name);
}
run('roadmap',['tools/validate-roadmap.mjs']);
run('package-source',['tools/verify-rrecollector-package.mjs']);
run('offline-regression',['--test',...cases]);
console.log(JSON.stringify({gate:'rre-offline',mode,passed:true,
  localSourceReplayRequired:mode==='--local-source',
  pinnedLuaRoundTrip:'separate-required-environment',
  liveRiftAcceptance:false}));
