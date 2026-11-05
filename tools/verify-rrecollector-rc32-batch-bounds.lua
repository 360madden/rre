-- RC-32 pre-gate RED fixture for real abilities.collect(), with fake RIFT API.
-- --expect-red documents four frozen v0.4.10 defects. Later use --require-fixed.
local calls = {batch=0, scalar=0}
local currentList
local function detail(arg)
  if type(arg) == "table" then
    calls.batch = calls.batch + 1
    local records = {}
    for key, value in pairs(arg) do
      local id = type(key) == "string" and key
        or (type(value) == "string" and value or nil)
      if id then records[id] = {idNew=id, name="Mock"} end
    end
    return records
  end
  calls.scalar = calls.scalar + 1
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
local failures, checks=0,0
local function check(label, predicate)
  checks=checks+1
  if predicate then print("PASS "..label)
  else failures=failures+1; print("RED "..label) end
end
local function capture(list)
  currentList=list
  calls={batch=0, scalar=0}
  local result=RRECollectorRuntime.abilities.collect()
  return result,calls
end
local record, used = capture(map(69))
check("clean 69-ID batch preserved", used.batch==1 and used.scalar==0
  and record.abilityList.uniqueCount==69 and record.abilityList.detailCount==69
  and record.captureComplete==true)
local duplicate={id(1),id(1),id(2)}
record, used=capture(duplicate)
check("duplicate list skips raw batch", used.batch==0 and used.scalar==2
  and record.abilityList.uniqueCount==2 and record.captureComplete==true)
local invalid=map(2)
invalid[true]="not-an-ID"
record, used=capture(invalid)
check("invalid entry skips raw batch", used.batch==0 and used.scalar==2
  and record.abilityList.ignored==1 and record.captureComplete==false)
record, used=capture(map(513))
check("513 IDs capped before Detail", used.batch==0 and used.scalar<=512
  and record.abilityList.uniqueCount==512 and record.captureComplete==false)
record, used=capture(array(1025))
check("1025 raw entries capped before Detail", used.batch==0 and used.scalar<=512
  and record.abilityList.rawEntries==1025 and record.captureComplete==false)
local mixed={id(1),id(2)}
mixed[id(3)]=true
record, used=capture(mixed)
check("clean mixed numeric/map keys retain data", record.abilityList.uniqueCount==3
  and record.abilityList.detailCount==3 and record.captureComplete==true)
local expectRed=type(arg)=="table" and arg[1]=="--expect-red"
if expectRed then
  assert(failures==4, "expected exactly four frozen-source defects; observed "..failures)
  print("EXPECTED_RED_RC32_BATCH "..failures.."/"..checks.." scenarios; no addon changes")
else
  assert(failures==0, "RC32 batch cap not yet implemented ("..failures.." defects)")
  print("PASS_RC32_BATCH "..checks.." scenarios")
end
