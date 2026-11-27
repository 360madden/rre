// Shared read-only package inventory. The same bytes drive manifest checks and SHA parity.
// Per-file stability is checked; this is not an atomic filesystem snapshot or live-load proof.
import fs from 'node:fs';
import path from 'node:path';
import {createHash} from 'node:crypto';
import {readStableOriginalWithMetadata} from './read-stable-original.mjs';

export const COLLECTOR_MODULES=Object.freeze([
  'core.lua','context.lua','abilities.lua','capabilities.lua',
  'candidate_catalog.lua','candidates.lua','wire.lua','units.lua','ui.lua','main.lua',
]);
export const COLLECTOR_FILES=Object.freeze([...COLLECTOR_MODULES,'README.md','RiftAddon.toc']);

function plainDirectory(dir){
  const stat=fs.lstatSync(dir);
  if(!stat.isDirectory()||stat.isSymbolicLink())throw Error('PACKAGE_DIRECTORY_NOT_PLAIN');
  return stat;
}
// A cloud-backed file can change metadata as it hydrates. Discard that
// invalid read and allow exactly one independently stable new read.
// Never retry missing, linked, oversized or otherwise invalid inputs.
export function readPackageMember(file,read=readStableOriginalWithMetadata){
  try{
    return {bytes:read(file).bytes,retried:false};
  }catch(error){
    if(!['saved-source-changed-before-read','saved-source-changed-during-read'].includes(error?.message))
      throw error;
    return {bytes:read(file).bytes,retried:true};
  }
}

export function readCollectorPackage(dir){
  const before=plainDirectory(dir);
  const names=fs.readdirSync(dir).sort();
  const present=new Set(names);
  const records=new Map(), missing=[],retried=[];
  const unexpected=names.filter(name=>!COLLECTOR_FILES.includes(name));
  for(const name of COLLECTOR_FILES){
    if(!present.has(name)){missing.push(name);continue;}
    try{
      const member=readPackageMember(path.join(dir,name));
      const {bytes}=member; if(member.retried)retried.push(name);
      records.set(name,{bytes,sha256:createHash('sha256').update(bytes).digest('hex')});
    }catch(error){
      throw Error('PACKAGE_FILE_UNREADABLE:'+name+':'+(error?.code??error?.message??'UNKNOWN'),{cause:error});
    }
  }
  const after=plainDirectory(dir);
  const finalNames=fs.readdirSync(dir).sort();
  if(before.dev!==after.dev||before.ino!==after.ino
      || JSON.stringify(names)!==JSON.stringify(finalNames))
    throw Error('PACKAGE_DIRECTORY_CHANGED_DURING_READ');
  return {records,missing,unexpected,retried};
}

export function requireExactPackage(pkg){
  if(pkg.missing.length||pkg.unexpected.length)
    throw Error('PACKAGE_FILE_SET_MISMATCH: missing='+pkg.missing.length+' unexpected='+pkg.unexpected.length);
}

export function packageText(pkg,name){
  const record=pkg.records.get(name);
  if(!record)throw Error('PACKAGE_REQUIRED_FILE_MISSING:'+name);
  return record.bytes.toString('utf8');
}
