-- RC-32 pre-gate RED fixture for real abilities.collect(), with fake RIFT API.
-- --expect-red documents four frozen v0.4.10 defects. Later use --require-fixed.
local calls = {batch=0, scalar=0, batchArg=nil, scalarIds={}}
local currentList
local function detail(arg)
  if type(arg) == "table" then
    calls.batch = calls.batch + 1
    calls.batchArg = arg
    local records = {}
    for key, value in pairs(arg) do
      local id = type(key) == "string" and key
        or (type(value) == "string" and value or nil)
      if id then records[id] = {idNew=id, name="Mock"} end
    end
    return records
  end
  calls.scalar = calls.scalar + 1
  calls.scalarIds[#calls.scalarIds + 1] = arg
  return {idNew=arg, name="Mock"}
end
Inspect = {Ability={New={
  List=function() return currentList end,
  Detail=detail
}}}
RRECollectorData = {sequence=1}
RRECollectorRuntime = {
  SCHEMA=1, VERSION="0.4.10",
  core={
    call=function(fn, ...) return pcall(fn, ...) end,
    fieldCopy=function(source, fields)
      local result={}
      for _, name in ipairs(fields) do if source[name]~=nil then result[name]=source[name] end end
      return result
    end
  },
  context={snapshot=function()
    return {capabilities={player=true}, frameTime=1, realTime=2,
      player={calling="warrior"}, target={}, roleNames={}, stats={}}
  end}
}
assert(loadfile("addons/RRECollector/abilities.lua"))()
local function id(i) return string.format("A%016X", i) end
local function map(n)
  local t={}
  for i=1,n do t[id(i)]=true end
  return t
end
local function array(n)
  local t={}
  for i=1,n do t[i]=id(i) end
  return t
end
local failures, checks, failedNames=0,0,{}
local function check(label, predicate)
  checks=checks+1
  if predicate then print("PASS "..label)
  else failures=failures+1; failedNames[label]=true; print("RED "..label) end
end
local function scalarExactlyMatches(record, used, list, count)
  if used.scalar~=count or #used.scalarIds~=count
    or #record.abilities~=count or record.abilityList.detailCount~=count then
    return false
  end
  local allowed, observed, captured={},{},{}
  for key, value in pairs(list) do
    local v=type(key)=="string" and key or
      (type(key)=="number" and type(value)=="string" and value or nil)
    if v then allowed[v]=true end
  end
  for i, item in ipairs(record.abilities) do
    if type(item.lookupId)~="string" or item.idNew~=item.lookupId
      or captured[item.lookupId] or used.scalarIds[i]~=item.lookupId
      or (i>1 and record.abilities[i-1].lookupId>item.lookupId)
      then return false end
    captured[item.lookupId]=true
  end
  for _, v in ipairs(used.scalarIds) do
    if type(v)~="string" or not allowed[v] or not captured[v]
      or observed[v] then return false end
    observed[v]=true
  end
  return true
end
local function batchExactlyMatches(record,used,list,count)
  if used.batch~=1 or used.batchArg~=list or used.scalar~=0
    or record.abilityList.uniqueCount~=count or record.abilityList.detailCount~=count
    or #record.abilities~=count then return false end
  local input, seen, inputCount={}, {}, 0
  for key,value in pairs(list) do
    local v=type(key)=="string" and key or
      (type(key)=="number" and type(value)=="string" and value or nil)
    if v and not input[v] then input[v]=true; inputCount=inputCount+1 end
  end
  if inputCount~=count then return false end
  for _,item in ipairs(record.abilities) do
    local v=item.lookupId
    if type(v)~="string" or not input[v] or seen[v]
      or item.idNew~=v then return false end
    seen[v]=true
  end
  return true
end
local function capture(list)
  currentList=list
  calls={batch=0, scalar=0, batchArg=nil, scalarIds={}}
  local result=RRECollectorRuntime.abilities.collect()
  return result,calls
end
local clean69=map(69)
local record, used = capture(clean69)
check("clean 69-ID batch preserved", batchExactlyMatches(record,used,clean69,69)
  and record.captureComplete==true)
local clean512=map(512)
record, used=capture(clean512)
check("clean 512-ID boundary retains batch", batchExactlyMatches(record,used,clean512,512)
  and record.captureComplete==true)
local duplicate={id(1),id(1),id(2)}
record, used=capture(duplicate)
check("duplicate list skips raw batch", used.batch==0 and used.batchArg==nil
  and scalarExactlyMatches(record,used,duplicate,2)
  and used.scalarIds[1]==id(1) and used.scalarIds[2]==id(2)
  and record.abilityList.uniqueCount==2 and record.abilityList.duplicates==1
  and record.captureComplete==true)
local invalid=map(2)
invalid[true]="not-an-ID"
record, used=capture(invalid)
check("invalid entry skips raw batch", used.batch==0 and used.batchArg==nil
  and scalarExactlyMatches(record,used,invalid,2)
  and used.scalarIds[1]==id(1) and used.scalarIds[2]==id(2)
  and record.abilityList.ignored==1 and record.captureComplete==false)
local oversized513=map(513)
record, used=capture(oversized513)
check("513 IDs capped before Detail", used.batch==0 and used.batchArg==nil
  and scalarExactlyMatches(record,used,oversized513,512)
  and record.abilityList.uniqueCount==512 and record.abilityList.truncated==1
  and record.captureComplete==false)
local oversized1025=array(1025)
record, used=capture(oversized1025)
check("1025 raw entries capped before Detail", used.batch==0 and used.batchArg==nil
  and scalarExactlyMatches(record,used,oversized1025,512)
  and record.abilityList.rawEntries==1025
  and record.abilityList.uniqueCount==512 and record.captureComplete==false)
local mixed={id(1),id(2)}
mixed[id(3)]=true
record, used=capture(mixed)
check("clean mixed numeric/map keys retain data", batchExactlyMatches(record,used,mixed,3)
  and record.captureComplete==true)
local expectRed=type(arg)=="table" and arg[1]=="--expect-red"
if expectRed then
  local wanted={
    ["duplicate list skips raw batch"]=true,
    ["invalid entry skips raw batch"]=true,
    ["513 IDs capped before Detail"]=true,
    ["1025 raw entries capped before Detail"]=true
  }
  assert(checks==7 and failures==4,
    "expected exactly four of seven frozen-source defects; observed "..failures)
  for name in pairs(wanted) do assert(failedNames[name], "missing expected red: "..name) end
  for name in pairs(failedNames) do assert(wanted[name], "unexpected red: "..name) end
  print("EXPECTED_RED_RC32_BATCH "..failures.."/"..checks.." named scenarios; no addon changes")
else
  assert(failures==0, "RC32 batch cap not yet implemented ("..failures.." defects)")
  print("PASS_RC32_BATCH "..checks.." scenarios")
end
