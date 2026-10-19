#!/usr/bin/env node
/** Manager-only M4A contract/fixture audit. Read-only; no game or process access. */
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const contract=JSON.parse(fs.readFileSync(path.join(root,'docs/m4a-offline-target-contract.json'),'utf8'));
const suite=JSON.parse(fs.readFileSync(path.join(root,'docs/m4a-offline-target-fixtures.json'),'utf8'));
const failures=[];
const check=(condition,description)=>{if(!condition)failures.push(description);};
const number=v=>typeof v==='number'&&Number.isFinite(v);
const ids=new Set(),seenCodes=new Set(),checked=[];
check(contract.schemaVersion===1 && suite.schemaVersion===1,'Expected schema version 1');
check(contract.taskId==='M4A-001' && suite.taskId==='M4A-001','Unexpected owner task');
check(contract.runMode==='offline-replay-only','Contract live mode prohibited');
check(contract.source.kind==='synthetic-fixture' && contract.source.replayOnly===true,'Contract must be synthetic replay');
check(suite.source.kind==='synthetic-fixture' && suite.source.replayOnly===true,'Fixture must be synthetic replay');
check(suite.gameInputAuthorized===false && suite.notRuntimeEvidence===true,'No gameplay claims or authority');
check(contract.outputContract.commandsIssued===0 && contract.outputContract.gameInputSent===false,'No actuation allowed');
check(contract.coordinateFrame.horizontalAxes.join(',')==='x,z' && contract.coordinateFrame.verticalAxis==='y','Coordinate frame mismatch');
for(const k of ['arrivalRadiusM','maximumVerticalDifferenceM','staleAfterGapMs','progressWindowMs','minimumProgressM','movingAwayToleranceM']){
  check(number(contract.policy[k])&&contract.policy[k]>0,'Invalid policy value: '+k);
}
const states=new Set(contract.stateVocabulary), terminal=new Set(contract.terminalStates);
check(states.has('approach-intent')&&!terminal.has('approach-intent'),'Approach must be nonterminal');
for(const code of terminal)check(states.has(code),'Unknown terminal state: '+code);
check(Array.isArray(suite.cases)&&suite.cases.length>=contract.acceptance.minimumCases,'Insufficient fixtures');
for(const item of suite.cases){
  check(typeof item.id==='string'&&item.id.length>0,'Missing scenario ID');
  check(!ids.has(item.id),'Duplicate scenario '+item.id);ids.add(item.id);
  check(typeof item.purpose==='string'&&item.purpose.length>0,'Missing purpose '+item.id);
  const samples=item.samples||[], expected=item.expectedStates||[];
  check(Array.isArray(samples)&&samples.length>0&&samples.length<=40,'Bad sample array '+item.id);
  check(Array.isArray(expected)&&samples.length===expected.length,'Need one decision per sample '+item.id);
  for(const decision of expected){
    check(states.has(decision),'Unknown state '+decision+' in '+item.id);
    seenCodes.add(decision);
  }
  check(terminal.has(item.expectedTerminal),'Unknown terminal state '+item.id);
  check(expected.includes(item.expectedTerminal),'Terminal not in expected trace '+item.id);
  for(let i=0;i<samples.length;i++){
    const row=samples[i],player=row?.player,target=row?.target;
    check(Number.isInteger(row?.tMs)&&row.tMs>=0,'Invalid timestamp '+item.id+'-'+i);
    check(typeof row?.sceneId==='string'&&row.sceneId.length>0,'Missing scene '+item.id+'-'+i);
    check(typeof row?.cancelRequested==='boolean','Bad cancellation flag '+item.id+'-'+i);
    check(player && typeof player==='object','Missing player '+item.id+'-'+i);
    if(player)for(const axis of ['x','y','z'])
      check(number(player[axis])||item.id==='invalid-coordinate','Bad player '+axis+' '+item.id+'-'+i);
    if(target!==null){
      check(target && typeof target==='object','Bad target '+item.id+'-'+i);
      if(target){
        check(typeof target.id==='string'&&target.id.length>0,'Missing target ID '+item.id+'-'+i);
        for(const axis of ['x','y','z'])check(number(target[axis]),'Bad target '+axis+' '+item.id+'-'+i);
      }
    }
    if(i>0&&row?.tMs<=samples[i-1]?.tMs)
      check(item.id==='nonmonotonic-time'&&item.expectedTerminal==='invalid-sample','Unexpected nonmonotonic timestamp '+item.id);
  }
  checked.push({caseId:item.id,samples:samples.length,expectedTerminal:item.expectedTerminal});
}
for(const code of contract.acceptance.requiredCodes||[])
  check(seenCodes.has(code),'Missing expected fixture state '+code);
const latched=suite.cases.find(x=>x.id==='terminal-latched');
check(Boolean(latched)&&latched.expectedStates.every(x=>x==='arrived')&&latched.assertions.secondSampleIgnored,'Need terminal latch fixture');
const output={ok:failures.length===0,taskId:'M4A-001',scope:'schema/fixture audit only, not a replay engine',
fixtureCount:checked.length,totalSamples:checked.reduce((n,x)=>n+x.samples,0),
statesCovered:[...seenCodes].sort(),noActuation:true,scenarios:checked,failures};
process.stdout.write(JSON.stringify(output,null,2)+'\n');
if(failures.length)process.exitCode=1;
