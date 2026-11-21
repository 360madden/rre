// Static RIFT ability-candidate inventory from a DISABLED ProjectAbilityBook copy.
// No Lua execution, no live API calls, no addon writes, no castability assertions.
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import {fileURLToPath} from 'node:url';
import {parseSavedLua} from './read-rrecollector-saved.mjs';
import {readStableOriginalWithMetadata} from './read-stable-original.mjs';

export const CALLINGS=Object.freeze(['Cleric','Mage','Primalist','Rogue','Warrior']);
const ID=/^A[0-9A-F]{16}$/;
const SOUL=/^[A-Za-z][A-Za-z0-9_]{0,60}$/;
const PINNED_PURIFIER='fbcdf9383c93204c976dc526b126fe6b49c677aa169e87f25fc13b1aefa4835c';
const SOURCE_LIMIT=256*1024;
const sha=bytes=>crypto.createHash('sha256').update(bytes).digest('hex');
const fail=code=>{throw Error(code);};
const obj=x=>x!==null&&typeof x==='object'&&!Array.isArray(x);
function sortedEntries(dir){
  const stat=fs.lstatSync(dir);
  if(!stat.isDirectory()||stat.isSymbolicLink())fail('SOURCE_DIRECTORY_INVALID');
  const entries=fs.readdirSync(dir,{withFileTypes:true});
  if(entries.some(e=>e.isSymbolicLink()))fail('SOURCE_LINK_NOT_ALLOWED');
  return entries.filter(e=>e.name.endsWith('.lua')).sort((a,b)=>a.name.localeCompare(b.name,'en'));
}
function parseLiteralSoul(original,stem){
  const text=new TextDecoder('utf-8',{fatal:true}).decode(original);
  if(text.charCodeAt(0)===0xfeff)fail('SOURCE_BOM_NOT_ALLOWED');
  const prefix='ProjectAbilityBook_Souls_'+stem;
  // First token only. Never execute the Lua and never rewrite original source.
  const pattern=new RegExp('^\\s*'+prefix+'\\s*=');
  const m=pattern.exec(text);
  if(!m)fail('SOURCE_ROOT_IDENTITY');
  const normalized='RRECollectorData='+text.slice(m[0].length);
  return parseSavedLua(normalized);
}
export function inventoryStaticCandidates(addonRoot){
  if(path.basename(path.resolve(addonRoot)).toLowerCase()!=='projectabilitybook.disabled')
    fail('SOURCE_ROOT_DIRECTORY');
  const callingRoot=path.join(addonRoot,'Callings');
  const files=[],records=[],quarantined=[],counts={};
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
        parsed=parseLiteralSoul(original,stem);
      }catch(error){
        const detail=String(error?.message??'UNPARSABLE');
        if(calling==='Cleric'&&stem==='Purifier'&&sourceSha===PINNED_PURIFIER
          && detail.includes('duplicate Lua table key')){
          files.push({path:sourcePath,sha256:sourceSha,status:'quarantined'});
          quarantined.push({path:sourcePath,sha256:sourceSha,
            reason:'DUPLICATE_NESTED_ABILITY_NAME',
            interpretation:'source not indexed; preserve all original bytes'});
          counts[calling].quarantinedSouls++;
          continue;
        }
        throw Error('SOURCE_PARSE_FAILED:'+sourcePath+':'+detail.slice(0,130));
      }
      if(!obj(parsed)||Object.keys(parsed).length!==1||!obj(parsed.Abilities))
        fail('SOURCE_ABILITY_SHAPE:'+sourcePath);
      let inFile=0;
      const categories=Object.keys(parsed.Abilities).sort();
      for(const category of categories){
        const group=parsed.Abilities[category];
        if(!obj(group)||category.length<1||category.length>100)
          fail('SOURCE_CATEGORY_SHAPE:'+sourcePath);
        for(const name of Object.keys(group).sort()){
          const ability=group[name];
          if(!obj(ability)||typeof ability.ID!=='string'||!ID.test(ability.ID)
            ||typeof ability.Icon!=='string'||ability.Icon.length>512
            ||name.length<1||name.length>200)
            fail('SOURCE_ABILITY_ENTRY:'+sourcePath);
          if(Object.keys(ability).some(key=>!['ID','Icon'].includes(key)))
            fail('SOURCE_ABILITY_EXTRA_FIELDS:'+sourcePath);
          records.push({calling,soul:stem,category,name,
            id:ability.ID,icon:ability.Icon,sourcePath});
          inFile++;
        }
      }
      files.push({path:sourcePath,sha256:sourceSha,status:'parsed',entries:inFile});
      counts[calling].parsedSouls++;
      counts[calling].entries+=inFile;
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
  return {schemaVersion:1,evidenceKind:'rre-static-candidates-from-disabled-addon/1',
    provenance:{sourceRootType:'disabled-third-party-ProjectAbilityBook',
      originalBytesHashed:true,originalSourceFilesModified:false,
      luaExecuted:false,apiKnownVerified:false,
      currentBuildVerified:false,learnabilityVerified:false,castabilityVerified:false},
    sourceManifestSha256:manifestSha256,
    totals:{sourceFiles:files.length,parsedFiles:files.length-quarantined.length,
      quarantinedFiles:quarantined.length,abilityEntries:records.length,
      uniqueIds:byId.size,duplicateIds:duplicateIds.length},
    callings:counts,files,quarantined,duplicateIds,records};
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
      duplicateIds:result.duplicateIds})+'\n');
  }catch(error){
    process.stderr.write(JSON.stringify({status:'failed',
      reason:String(error?.message??'STATIC_INVENTORY_FAILED')})+'\n');
    process.exitCode=1;
  }
}
