"""Explicit offline integration against retained evidence; never connects to a VM."""
import argparse,hashlib,json,subprocess,sys
from pathlib import Path

def main():
 p=argparse.ArgumentParser(description=__doc__)
 for name in ('repo','saved','scan1','scan2','output'):p.add_argument('--'+name,required=True,type=Path)
 p.add_argument('--reader',type=Path,help='Existing built/published Rre.Reader.dll; default is the local Debug build')
 p.add_argument('--native-snapshot',type=Path);p.add_argument('--native-request',type=Path);p.add_argument('--native-session')
 args=p.parse_args();repo=args.repo.resolve();out=args.output.resolve();out.mkdir(parents=False,exist_ok=False)
 dll=(args.reader or repo/'reader/Rre.Reader/bin/Debug/net10.0/Rre.Reader.dll').resolve()
 assert dll.is_file(),'Build reader first'
 scan=json.loads(args.scan1.read_text(encoding='utf-8-sig'));session=scan['SearchText'].split('|')[1]
 sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
 runs=[];observations=[]
 cases=[('saved','saved',args.saved,['--repo',str(repo)]),('memory1','memory-scan',args.scan1,['--session',session,'--sequence','1']),('memory2','memory-scan',args.scan2,['--session',session,'--sequence','2'])]
 if any([args.native_snapshot,args.native_request,args.native_session]):
  assert all([args.native_snapshot,args.native_request,args.native_session]),'native snapshot/request/session must be supplied together'
  cases.append(('native','native-snapshot',args.native_snapshot,['--request',str(args.native_request.resolve()),'--session',args.native_session,'--sequence','1']))
 for name,source,file,extra in cases:
  destination=out/(name+'.json')
  run=subprocess.run(['dotnet',str(dll),'capture','--source',source,'--input',str(file.resolve()),*extra,'--output',str(destination)],cwd=repo,capture_output=True,text=True,timeout=20)
  assert run.returncode==0,(name,run.stderr)
  value=json.loads(destination.read_text(encoding='utf-8'));observations.append(value)
  assert value['source']['sha256']==sha(file)
  q=value['qualification'];assert all(q[k] is False for k in ['live','freshnessVerified','processBuildVerified','atomicSnapshotVerified','restartQualified'])
  assert value['modules']['abilities']['complete'] is True
  assert q['fixture'] is (source!='saved')
  assert q['complete'] is (source=='saved') # all modules requested, fixture has no context
  runs.append({'name':name,'exitCode':run.returncode,'inputSha256':sha(file),'outputSha256':sha(destination),'abilityCount':value['modules']['abilities']['count']})
 catalogs=[{r['lookupId']:r for r in o['modules']['abilities']['records']} for o in observations]
 assert all(len(c)==54 for c in catalogs),'Expected the explicit SC614/61854-ID trial'
 assert all(catalogs[0].keys()==c.keys() for c in catalogs[1:])
 assert all(catalogs[1]==c for c in catalogs[2:])
 # SC618 used the old research crosswalk projection, which deliberately omitted targets.
 # Compare every fixture field; the new saved adapter must retain additional targets.
 for id,row in catalogs[1].items():
  for key,value in row.items():
   assert catalogs[0][id][key]==value,(id,key)
   assert type(catalogs[0][id][key]) is type(value) or isinstance(value,(int,float)) and not isinstance(value,bool) and isinstance(catalogs[0][id][key],(int,float)) and not isinstance(catalogs[0][id][key],bool)
 target_count=sum('target' in row for row in catalogs[0].values())
 assert target_count>0,'Actual producer targets must survive the new adapter'
 assert all('target' not in row for row in catalogs[1].values()),'Historical fixture boundary changed'
 assert observations[0]['modules']['context']['status']=='available'
 assert observations[1]['modules']['context']['status']=='unavailable'
 assert observations[0]['sequence']==4 and [o['sequence'] for o in observations[1:]]==([1,2,1] if args.native_snapshot else [1,2])
 # Exercise CLI rejection and evidence no-overwrite using these actual input paths.
 bad=subprocess.run(['dotnet',str(dll),'validate','--source','memory-scan','--input',str(args.scan1.resolve()),'--session',session,'--sequence','2'],cwd=repo,capture_output=True,text=True,timeout=10)
 assert bad.returncode==2 and 'frame-session-sequence' in bad.stderr
 before=sha(out/'saved.json')
 overwrite=subprocess.run(['dotnet',str(dll),'capture','--source','saved','--input',str(args.saved.resolve()),'--repo',str(repo),'--output',str(out/'saved.json')],cwd=repo,capture_output=True,text=True,timeout=20)
 assert overwrite.returncode==2 and sha(out/'saved.json')==before
 result={'status':'passed','scope':'offline SC614saved / SC618memory and optional SC620native snapshot','runs':runs,'exactIds':54,'allFixtureFieldsCompared':True,'savedTargetFieldsPreserved':target_count,'historicalMemoryFixtureHasNoTargetFields':True,'allLiveQualificationsFalse':True,'staleSequenceRejected':True,'existingOutputPreserved':True,'nativeSnapshotIncluded':bool(args.native_snapshot),'liveVMAccess':False,'readerDllSha256':sha(dll)}
 (out/'integration.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8');print(json.dumps(result));return 0
if __name__=='__main__':sys.exit(main())
