// Strict, bounded Lua 5.1 literal-table reader for historical ProjectAbilityBook
// soul catalogs. Preserves duplicate nested ability names and exact source lines.
// Never execute Lua or interpret comments as gameplay/API claims.
const ID=/^A[0-9A-F]{16}$/;
const STEM=/^[A-Za-z][A-Za-z0-9_]{0,60}$/;
const MAX_CHARS=256*1024;
const MAX_ENTRIES=4096;
const MAX_DEPTH=5;
const escapes={a:'\x07',b:'\b',f:'\f',n:'\n',r:'\r',t:'\t',v:'\v'};
const error=(kind,line)=>{throw Error('PAB_'+kind+'_LINE_'+line);};
const compare=(a,b)=>a<b?-1:a>b?1:0;

export function parsePabSoulLiteral(original,stem){
  if(!(original instanceof Uint8Array)||!STEM.test(stem))
    error('SOURCE_OR_STEM',1);
  if(original.byteLength<32||original.byteLength>MAX_CHARS)
    error('SOURCE_SIZE',1);
  const src=new TextDecoder('utf-8',{fatal:true}).decode(original);
  if(src.charCodeAt(0)===0xfeff)error('BOM',1);
  let pos=0,line=1,entriesSeen=0;
  function next(){
    if(pos>=src.length)error('UNEXPECTED_EOF',line);
    const ch=src[pos++];
    if(ch==='\n')line++;
    return ch;
  }
  function skip(){
    while(pos<src.length){
      const ch=src[pos];
      if(/\s/u.test(ch)){next();continue;}
      if(ch==='-'&&src[pos+1]==='-'){
        next();next();
        // Only ordinary Lua 5.1 single-line comments are supported.
        if(src[pos]==='['&&src[pos+1]==='[')error('LONG_COMMENT_UNSUPPORTED',line);
        while(pos<src.length&&src[pos]!=='\n')next();
        continue;
      }
      break;
    }
  }
  function expect(ch){
    skip();
    if(src[pos]!==ch)error('EXPECTED_'+ch.charCodeAt(0),line);
    next();
  }
  function quote(){
    skip();
    const boundary=next();
    if(boundary!=='"'&&boundary!=="'")error('STRING_EXPECTED',line);
    let value='';
    while(pos<src.length){
      let ch=next();
      if(ch===boundary)return value;
      if(ch==='\n'||ch==='\r')error('RAW_NEWLINE',line);
      if(ch!=='\\'){value+=ch;continue;}
      if(pos>=src.length)error('TRAILING_ESCAPE',line);
      const escaped=next();
      if(escaped===boundary||escaped==='\\'||escaped==='"'||escaped==="'"){
        value+=escaped;
      }else if(Object.hasOwn(escapes,escaped)){
        value+=escapes[escaped];
      }else if(escaped>='0'&&escaped<='9'){
        let digits=escaped;
        while(digits.length<3&&src[pos]>='0'&&src[pos]<='9')digits+=next();
        const code=Number(digits);
        if(code>255)error('DECIMAL_ESCAPE',line);
        value+=String.fromCharCode(code);
      }else if(escaped==='\n'){
        value+='\n';
      }else if(escaped==='\r'){
        if(src[pos]==='\n')next();
        value+='\n';
      }else error('UNSUPPORTED_ESCAPE',line);
      if(value.length>2048)error('STRING_TOO_LONG',line);
    }
    error('UNCLOSED_STRING',line);
  }
  function table(depth){
    if(depth>MAX_DEPTH)error('NESTING_LIMIT',line);
    expect('{');
    const result=[];
    for(;;){
      skip();
      if(src[pos]==='}'){next();return result;}
      if(++entriesSeen>MAX_ENTRIES)error('ENTRY_LIMIT',line);
      const sourceLine=line;
      expect('[');
      const key=quote();
      expect(']');
      expect('=');
      skip();
      const value=src[pos]==='{'?table(depth+1):quote();
      result.push({key,value,line:sourceLine});
      skip();
      if(src[pos]===','||src[pos]===';'){next();continue;}
      if(src[pos]!=='}')error('TABLE_SEPARATOR',line);
    }
  }
  skip();
  const root=/^[A-Za-z_][A-Za-z0-9_]*/.exec(src.slice(pos));
  if(!root||root[0]!=='ProjectAbilityBook_Souls_'+stem)error('ROOT_IDENTITY',line);
  for(let n=0;n<root[0].length;n++)next();
  expect('=');
  const rootTable=table(1);
  skip();
  if(src[pos]===';'){next();skip();}
  if(pos!==src.length)error('TRAILING_CODE',line);
  if(rootTable.length!==1||rootTable[0].key!=='Abilities'
    ||!Array.isArray(rootTable[0].value))
    error('ROOT_SHAPE',1);

  const categories=rootTable[0].value;
  const categoriesSeen=new Set(),records=[],duplicateNames=[];
  for(const group of categories){
    if(typeof group.key!=='string'||group.key.length<1||group.key.length>100
      ||!Array.isArray(group.value)||categoriesSeen.has(group.key))
      error('CATEGORY_SHAPE_OR_DUPLICATE',group.line);
    categoriesSeen.add(group.key);
    const nameOccurrences=new Map();
    for(const ability of group.value){
      if(typeof ability.key!=='string'||ability.key.length<1
        ||ability.key.length>200||!Array.isArray(ability.value))
        error('ABILITY_NAME_OR_SHAPE',ability.line);
      const fields=new Map();
      for(const property of ability.value){
        if(fields.has(property.key)||!['ID','Icon'].includes(property.key)
          ||typeof property.value!=='string')
          error('ABILITY_FIELD_SHAPE_OR_DUPLICATE',property.line);
        fields.set(property.key,property.value);
      }
      const id=fields.get('ID'),icon=fields.get('Icon');
      if(fields.size!==2||!ID.test(id??'')||typeof icon!=='string'||icon.length>512)
        error('ABILITY_ID_OR_ICON',ability.line);
      const row={category:group.key,name:ability.key,id,icon,sourceLine:ability.line};
      records.push(row);
      const matching=nameOccurrences.get(ability.key)||[];
      matching.push(row);
      nameOccurrences.set(ability.key,matching);
    }
    for(const [name,matches] of nameOccurrences){
      if(matches.length>1){
        matches.forEach((r,i)=>{r.duplicateName=true;r.nameOccurrence=i+1;});
        duplicateNames.push({category:group.key,name,
          occurrences:matches.map(r=>({id:r.id,sourceLine:r.sourceLine,
            nameOccurrence:r.nameOccurrence}))});
      }
    }
  }
  records.sort((a,b)=>compare(a.category,b.category)
    ||compare(a.name,b.name)||a.sourceLine-b.sourceLine);
  duplicateNames.sort((a,b)=>compare(a.category,b.category)||compare(a.name,b.name));
  return {records,duplicateNames};
}
