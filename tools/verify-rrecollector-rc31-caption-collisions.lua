-- RC-31 offline caption collision regression using the real candidate catalog.
-- Captures the frozen RC25 layout function; does not edit UI or contact RIFT.
-- Run from the repository root using Lua 5.1 or later.
local mode=type(arg)=="table" and arg[1] or nil
assert(mode=="--expect-red" or mode=="--require-fixed",
  "usage: lua verify-rrecollector-rc31-caption-collisions.lua --expect-red|--require-fixed")
local uiFile=assert(io.open("addons/RRECollector/ui.lua","rb"))
local ui=uiFile:read("*a"); uiFile:close()
ui=ui:gsub("\r\n","\n")
local block=assert(ui:match("%-%- RC25%-CAPTIONS%-BEGIN(.-)%-%- RC25%-CAPTIONS%-END"),
  "frozen caption source block missing")
local catalogRuntime={candidateCatalog=nil}
local priorRuntime=rawget(_G,"RRECollectorRuntime")
_G.RRECollectorRuntime=catalogRuntime
local loaded,loadErr=pcall(dofile,"addons/RRECollector/candidate_catalog.lua")
_G.RRECollectorRuntime=priorRuntime
assert(loaded,"candidate catalog bootstrap failed: "..tostring(loadErr))
local entries=assert(catalogRuntime.candidateCatalog and catalogRuntime.candidateCatalog.entries,
  "static candidate catalog missing")
assert(#entries==96,"expected the complete 96-entry static candidate catalog")
local names,allIds={},{}
for _,entry in ipairs(entries) do
  assert(type(entry.id)=="string" and #entry.id==17
    and entry.id:match("^A%x+$"),"invalid candidate ID")
  assert(not allIds[entry.id],"duplicate candidate ID: "..entry.id)
  assert(type(entry.name)=="string" and #entry.name>0,"missing candidate name")
  allIds[entry.id]=true
  names[entry.name]=names[entry.name] or {}
  names[entry.name][#names[entry.name]+1]=entry.id
end
local pre=[==[
local function safe(value,fallback)
  return type(value)=="string" and #value>0 and value or fallback
end
local function glyphCount(s)
  local count=0
  for i=1,#s do
    local b=s:byte(i)
    if b<128 or b>=192 then count=count+1 end
  end
  return count
end
local function line()
  local obj={shown=""}
  function obj:SetText(value) self.shown=value end
  function obj:GetWidth() return glyphCount(self.shown)*6 end
  return obj
end
]==]
local postfix=[==[
return function(name)
  local a,b=line(),line()
  layoutTileCaption(a,b,name)
  return a.shown,b.shown,a:GetWidth(),b:GetWidth()
end
]==]
local chunk,err=(loadstring or load)(pre..block..postfix,"RC31 catalog caption layout")
assert(chunk,"source-extracted caption layout could not compile: "..tostring(err))
local render=chunk()
local groups={
  {"shield three-way names",{"Shield of the Chosen","Shield of the Hero","Shield of the Vengeful"}},
  {"way three-way names",{"Way of the Mountain","Way of the River","Way of the Wind"}}
}
local tested={}
for _,group in ipairs(groups) do
  for _,name in ipairs(group[2]) do
    assert(names[name] and #names[name]==1,"expected one catalog entry for "..name)
    tested[#tested+1]=name
  end
end
local failNames,failures,checks={},0,0
local function check(label,ok,detail)
  checks=checks+1
  if ok then print("PASS "..label)
  else
    failures=failures+1;failNames[label]=true
    print("RED "..label..(detail and " ("..detail..")" or ""))
  end
end
for _,group in ipairs(groups) do
  local seen,distinct,duplicates={},true,{}
  for _,name in ipairs(group[2]) do
    local first,second=render(name)
    local signature=first.." | "..second
    if seen[signature] then
      distinct=false
      duplicates[#duplicates+1]=name.." == "..seen[signature].." => "..signature
    else seen[signature]=name end
  end
  check(group[1].." captions distinguish names",distinct,table.concat(duplicates,"; "))
end
local allFit=true
for _,name in ipairs(tested) do
  local _,_,width1,width2=render(name)
  if width1>46 or width2>46 then allFit=false end
end
check("all six catalog captions fit 46px mock width",allFit)
local first,second=render("Light")
check("short single word is preserved",first=="Light" and second=="")
local a,b=render("Amnesty")
local c,d=render("Void")
check("different short names remain distinguishable",a.."|"..b~=c.."|"..d)
if mode=="--expect-red" then
  assert(checks==5 and failures==2,
    "expected exactly two of five frozen-source red cases, observed "..failures)
  local expected={
    ["shield three-way names captions distinguish names"]=true,
    ["way three-way names captions distinguish names"]=true
  }
  for label in pairs(expected) do assert(failNames[label],"missing named RED: "..label) end
  for label in pairs(failNames) do assert(expected[label],"unexpected named RED: "..label) end
  print("EXPECTED_RED_RC31_CAPTIONS "..failures.."/"..checks.."; mock Text metrics only")
else
  assert(failures==0,"RC31 source captions still collide ("..failures.." groups)")
  print("PASS_RC31_CAPTIONS "..checks.." scenarios")
end
