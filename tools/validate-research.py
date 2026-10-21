#!/usr/bin/env python3
"""One bounded RRE acceptance gate with explicit suite inventory and durable logs.

Run with the existing RRE .venv interpreter. No installs or active game control.
Existing exact-build tests only recheck original files/saved evidence.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
from datetime import datetime, timezone
ROOT=Path(__file__).resolve().parents[1]
TEST_SCRIPT="""import json,sys,unittest
suite=unittest.TestLoader().discover(sys.argv[1],pattern='*test*.py')
def ids(s):
 for t in s:
  if isinstance(t,unittest.TestSuite): yield from ids(t)
  else: yield t.id()
found=list(ids(suite));result=unittest.TextTestRunner(verbosity=1).run(suite)
print('RRE_TEST_RESULT '+json.dumps({'testsRun':result.testsRun,'failures':len(result.failures),'errors':len(result.errors),'skipped':len(result.skipped),'ids':found}))
sys.exit(0 if result.wasSuccessful() and not result.skipped else 1)
"""

def now():return datetime.now(timezone.utc).isoformat()
def sha(raw):return hashlib.sha256(raw).hexdigest()

def source_inventory():
    files=sorted(p for p in (ROOT/'tools').rglob('*') if p.is_file() and p.suffix in ('.py','.mjs'))
    return {str(p.relative_to(ROOT)).replace('\\','/'):sha(p.read_bytes()) for p in files}

def run(output:Path, image_python:Path | None = None):
    output.mkdir(parents=False,exist_ok=False)
    before=source_inventory()
    state={'schemaVersion':1,'startedAt':now(),'status':'running','sourceHashes':before,'groups':[],
           'scope':'RRE lane Python tests, navigation evidence tests, separate screenshot image-runtime tests, review-adapter Node tests and roadmap validator',
           'excludes':'Other repositories, model inference, live game observation and unrelated hardware/runtime acceptance'}
    def checkpoint():
        temp=output/'state.tmp';temp.write_text(json.dumps(state,indent=2)+'\n',encoding='utf-8');temp.replace(output/'validation.json')
    checkpoint()
    commands=[]
    for lane in ('validation','c2m','follow','collision','pathfinding'):
        commands.append((lane,[sys.executable,'-B','-c',TEST_SCRIPT,'tools/agents/'+lane],'python',150))
    commands.append(('navigation-evidence',[sys.executable,'-B','-c',TEST_SCRIPT,'tools/tests_navigation'],'python',60))
    # Reuse an existing image runtime without installing packages or altering environments.
    default_image = ROOT.parent/'riftreader2/artifacts/tools/control-python/Scripts/python.exe'
    image_executable = str(image_python or (default_image if default_image.is_file() else Path(sys.executable)))
    image_script = "import json,sys,PIL; print('RRE_IMAGE_RUNTIME '+json.dumps({'python':sys.version,'executable':sys.executable,'pillow':PIL.__version__}))\n" + TEST_SCRIPT
    commands.append(('visual-evidence',[image_executable,'-B','-c',image_script,'tools/tests_visual'],'python',150))
    commands.extend([('review-adapter',['node','--test','--test-reporter=tap','tools/agents/validation/test_agent_review_runner.mjs'],'node',60),
                     ('roadmap',['node','tools/validate-roadmap.mjs'],'roadmap',30)])
    ok=True;count=0;all_ids=[]
    for name,args,kind,timeout in commands:
        result={'group':name,'argv':args,'startedAt':now(),'timeoutSeconds':timeout,'testCount':0}
        try:
            completed=subprocess.run(args,cwd=ROOT,stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=timeout,check=False)
            stdout,stderr=completed.stdout,completed.stderr;result['exitCode']=completed.returncode
            result['timedOut']=False
        except subprocess.TimeoutExpired as exc:
            stdout,stderr=exc.stdout or b'',exc.stderr or b'';result.update(exitCode=None,timedOut=True)
        except OSError as exc:
            stdout,stderr=b'',str(exc).encode();result.update(exitCode=None,timedOut=False,launchError=str(exc))
        for stream,raw in (('stdout',stdout),('stderr',stderr)):
            (output/(name+'.'+stream+'.log')).write_bytes(raw);result[stream+'Sha256']=sha(raw)
        text=stdout.decode('utf-8',errors='replace');passed=result['exitCode']==0
        if kind=='python':
            summaries=[line[len('RRE_TEST_RESULT '):] for line in text.splitlines() if line.startswith('RRE_TEST_RESULT ')]
            try:
                if len(summaries)!=1:raise ValueError('missing or ambiguous test summary')
                summary=json.loads(summaries[0]);result['testCount']=summary['testsRun'];result['testSummary']=summary
                passed=passed and summary['testsRun']>0 and summary['failures']==0 and summary['errors']==0 and summary['skipped']==0
                all_ids.extend(name+':'+x for x in summary['ids'])
            except (ValueError,KeyError,TypeError) as exc:result['summaryError']=str(exc);passed=False
        elif kind=='node':
            matches=re.findall(r'^# tests (\d+)\s*$',text,re.M)
            passed=passed and len(matches)==1
            if matches:result['testCount']=int(matches[-1])
        else:
            try:passed=passed and json.loads(text).get('ok') is True
            except (ValueError,TypeError):passed=False
        result.update(status='passed' if passed else 'failed',endedAt=now());count+=result['testCount'];ok=ok and passed
        state['groups'].append(result);checkpoint()
        print(json.dumps({'group':name,'status':result['status'],'exitCode':result['exitCode'],'tests':result['testCount']}),flush=True)
    state['sourcesUnchanged']=source_inventory()==before
    state['duplicatePythonTestIds']=len(all_ids)-len(set(all_ids))
    ok=ok and state['sourcesUnchanged'] and not state['duplicatePythonTestIds']
    state.update(status='passed' if ok else 'failed',endedAt=now(),totalTests=count)
    checkpoint()
    return state

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output-dir',required=True,type=Path)
    p.add_argument('--image-python',type=Path,help='Existing interpreter with Pillow; missing runtime fails, never silently skips')
    args=p.parse_args()
    try:
        state=run(args.output_dir.resolve(),args.image_python);print(json.dumps({'status':state['status'],'totalTests':state['totalTests'],'sourcesUnchanged':state['sourcesUnchanged']}));return 0 if state['status']=='passed' else 1
    except (OSError,ValueError,TypeError) as exc:
        print(json.dumps({'status':'failed','error':str(exc)}),file=sys.stderr);return 2
if __name__=='__main__':raise SystemExit(main())
