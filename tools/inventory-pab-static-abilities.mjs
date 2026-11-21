// Static RIFT ability-candidate inventory from a DISABLED ProjectAbilityBook copy.
// No Lua execution, no live API calls, no addon writes, no castability assertions.
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import {fileURLToPath} from 'node:url';
import {parsePabSoulLiteral} from './parse-pab-soul-literal.mjs';
import {readStableOriginalWithMetadata} from './read-stable-original.mjs';

export const CALLINGS=Object.freeze(['Cleric','Mage','Primalist','Rogue','Warrior']);
const SOUL=/^[A-Za-z][A-Za-z0-9_]{0,60}$/;
const SOURCE_LIMIT=256*1024;
const sha=bytes=>crypto.createHash('sha256').update(bytes).digest('hex');
const fail=code=>{throw Error(code);};
function sortedEntries(dir){
  const stat=fs.lstatSync(dir);
  if(!stat.isDirectory()||stat.isSymbolicLink())fail('SOURCE_DIRECTORY_INVALID');
  const entries=fs.readdirSync(dir,{withFileTypes:true});
  if(entries.some(e=>e.isSymbolicLink()))fail('SOURCE_LINK_NOT_ALLOWED');
  return entries.filter(e=>e.name.endsWith('.lua')).sort((a,b)=>a.name.localeCompare(b.name,'en'));
}
export function inventoryStaticCandidates(addonRoot){
  if(path.basename(path.resolve(addonRoot)).toLowerCase()!=='projectabilitybook.disabled')
    fail('SOURCE_ROOT_DIRECTORY');
  const callingRoot=path.join(addonRoot,'Callings');
  const files=[],records=[],quarantined=[],duplicateNames=[],counts={};
  for(const calling of CALLINGS){
    const dir=path.join(callingRoot,calling);
    const entries=sortedEntries(dir);
    if(entries.length<1||entries.length>16)fail('SOURCE_SOUL_FILE_COUNT');
    counts[calling]={souls:entries.length,parsedSouls:0,entries:0,quarantinedSouls:0};
    for(const entry of entries){
      const stem=entry.name.slice(0,-4);
      if(!entry.isFile()||!SOUL.test(stem))fail('SOURCE_SOUL_FILENAME');
      const file=path.join(dir,entry.name);
      const st=fs.lstatSync(file);
      if(!st.isFile()||st.isSymbolicLink()||st.size<32||st.size>SOURCE_LIMIT)
        fail('SOURCE_SOUL_SIZE_OR_TYPE');
      const original=readStableOriginalWithMetadata(file).bytes;
      if(original.length<32||original.length>SOURCE_LIMIT)fail('SOURCE_SOUL_SIZE_CHANGED');
      const sourceSha=sha(original);
      const sourcePath='Callings/'+calling+'/'+entry.name;
      let parsed;
      try{
        parsed=parsePabSoulLiteral(original,stem);
      }catch(error){
        throw Error('SOURCE_PARSE_FAILED:'+sourcePath+':'+
          String(error?.message??'UNPARSABLE').slice(0,130));
      }
      for(const item of parsed.records){
        records.push({calling,soul:stem,...item,sourcePath});
      }
      for(const duplicate of parsed.duplicateNames){
        duplicateNames.push({calling,soul:stem,sourcePath,...duplicate});
      }
      files.push({path:sourcePath,sha256:sourceSha,status:'parsed',
        entries:parsed.records.length,duplicateNameGroups:parsed.duplicateNames.length});
      counts[calling].parsedSouls++;
      counts[calling].entries+=parsed.records.length;
    }
  }
  const byId=new Map();
  for(const row of records){
    const rows=byId.get(row.id)||[];
    rows.push({calling:row.calling,soul:row.soul,name:row.name,sourcePath:row.sourcePath});
    byId.set(row.id,rows);
  }
  const duplicateIds=[...byId].filter(([,rows])=>rows.length>1)
    .map(([id,occurrences])=>({id,occurrences})).sort((a,b)=>a.id.localeCompare(b.id,'en'));
  const manifestSha256=sha(Buffer.from(files.map(f=>f.path+'|'+f.sha256+'|'+f.status+'\n').join('')));
  return {schemaVersion:2,evidenceKind:'rre-static-candidates-from-disabled-addon/2',
    provenance:{sourceRootType:'disabled-third-party-ProjectAbilityBook',
      originalBytesHashed:true,originalSourceFilesModified:false,
      luaExecuted:false,losslessDuplicateAbilityNames:true,sourceLineRecorded:true,
      apiKnownVerified:false,currentBuildVerified:false,
      learnabilityVerified:false,castabilityVerified:false},
    sourceManifestSha256:manifestSha256,
    totals:{sourceFiles:files.length,parsedFiles:files.length-quarantined.length,
      quarantinedFiles:quarantined.length,abilityEntries:records.length,
      uniqueIds:byId.size,duplicateIds:duplicateIds.length,
      duplicateNameGroups:duplicateNames.length},
    callings:counts,files,quarantined,duplicateNames,duplicateIds,records};
}
if(process.argv[1]&&path.resolve(process.argv[1])===fileURLToPath(import.meta.url)){
  try{
    const args=process.argv.slice(2);
    if(args.length!==1&&!(args.length===3&&args[1]==='--output'))
      fail('USAGE_SOURCE_ROOT_OPTIONAL_OUTPUT');
    const result=inventoryStaticCandidates(args[0]);
    if(args.length===3){
      const output=path.resolve(args[2]);
      const docs=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'../docs');
      if(path.dirname(output)!==docs||!output.endsWith('.json'))
        fail('OUTPUT_MUST_BE_NEW_RRE_DOCS_JSON');
      const bytes=JSON.stringify(result,null,2)+'\n';
      if(Buffer.byteLength(bytes)>2*1024*1024)fail('OUTPUT_TOO_LARGE');
      fs.writeFileSync(output,bytes,{encoding:'utf8',flag:'wx'});
    }
    process.stdout.write(JSON.stringify({status:'verified-offline-static-only',
      manifestSha256:result.sourceManifestSha256,totals:result.totals,
      callings:result.callings,quarantined:result.quarantined,
      duplicateNames:result.duplicateNames,
      duplicateIds:result.duplicateIds})+'\n');
  }catch(error){
    process.stderr.write(JSON.stringify({status:'failed',
      reason:String(error?.message??'STATIC_INVENTORY_FAILED')})+'\n');
    process.exitCode=1;
  }
}
