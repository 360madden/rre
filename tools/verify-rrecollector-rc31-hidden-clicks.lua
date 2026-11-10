-- RC-31 offline click-path regression for hidden API-known selection.
-- Source-extracts real Pin and Check callback bodies from frozen ui.lua.
-- No game API, SavedVariables disk writes, physical input or deployment.
-- Frozen v0.4.10: --expect-red yields 2 expected defects + 1 PASS control.
local mode = type(arg)=="table" and arg[1] or nil
assert(mode=="--expect-red" or mode=="--require-fixed",
  "usage: lua verify-rrecollector-rc31-hidden-clicks.lua --expect-red|--require-fixed")
local f=assert(io.open("addons/RRECollector/ui.lua","rb"))
local src=f:read("*a"); f:close()
src=src:gsub("\r\n","\n")
local selector=assert(src:match("(local function visibleKnownSelection%(%).-)\nlocal function loadSlots"),
  "visible selection guard source missing")
local pin=assert(src:match("(local function pinSelected%(%).-)\nlocal function undoPins"),
  "source-extracted Pin handler missing")
local checkBody=assert(src:match('button%("RRECheckSelected".-function%(%)(.-)\n%s*end%)'),
  "source-extracted Check selected callback missing")
local prelude=[==[
local MAX_SLOTS, MAX_ROWS, page, mode, soul, pinSlot = 8, 8, 2, "known", "All", 1
local selectedId, selectedKind, pinBaseline = nil, nil, nil
local slots, known, rows, checked, detailCalls, messages = {}, {}, {}, {}, {}, {}
local RRECollectorData = {}
local function knownMap() return known end
local function records() return rows end
local function saved() return RRECollectorData end
local function say(value) messages[#messages+1]=value end
local function draw() end
local function apiCheck(id)
  detailCalls[#detailCalls+1]=id
  return {status="synthetic-check", id=id}
end
]==]
local between=[==[
local function checkSelected()
]==]
local suffix=[==[
end
local function abilityId(i) return string.format("A%016X",i) end
local function setup(selectedIndex)
  rows,known,checked,detailCalls,messages,slots={},{},{},{},{},{}
  for i=1,16 do
    local id=abilityId(i)
    rows[i]={id=id,kind="known"}
    known[id]={name="Synthetic "..i}
  end
  for i=1,MAX_SLOTS do slots[i]="ORIGINAL_SLOT_"..i end
  local stored={}
  for i=1,MAX_SLOTS do stored[i]=slots[i] end
  local priorLatest,priorProbe={token="latest"},{token="probe"}
  RRECollectorData={toolbarSlots=stored,latest=priorLatest,probe=priorProbe}
  selectedId,selectedKind,pinSlot,pinBaseline=abilityId(selectedIndex),"known",1,nil
  page,mode,soul=2,"known","All"
  return stored,priorLatest,priorProbe
end
local function performPin(selectedIndex)
  local original,latest,probe=setup(selectedIndex)
  local chosen=selectedId
  pinSelected()
  local savedAfter=RRECollectorData.toolbarSlots
  local unchanged=savedAfter==original and pinSlot==1 and pinBaseline==nil
  local positiveStored=savedAfter~=original
    and type(savedAfter)=="table" and savedAfter[1]==chosen
  local positiveBaseline=type(pinBaseline)=="table"
    and type(pinBaseline.slots)=="table" and pinBaseline.savedSlots==original
    and pinBaseline.nextSlot==1
  for i=1,MAX_SLOTS do
    local baselineValue="ORIGINAL_SLOT_"..i
    if slots[i]~=baselineValue or original[i]~=baselineValue
      or type(savedAfter)~="table" or savedAfter[i]~=baselineValue then
      unchanged=false
    end
    if original[i]~=baselineValue then positiveStored=false end
    if i>1 and (slots[i]~=baselineValue or type(savedAfter)~="table"
      or savedAfter[i]~=baselineValue) then positiveStored=false end
    if type(pinBaseline)~="table" or type(pinBaseline.slots)~="table"
      or pinBaseline.slots[i]~=baselineValue then positiveBaseline=false end
  end
  local untouched=RRECollectorData.latest==latest and RRECollectorData.probe==probe
  return {
    unchanged=unchanged,unrelatedUntouched=untouched,
    pinChanged=slots[1]==chosen and pinSlot==2,
    persistedAsExpected=positiveStored, baselinePreserved=positiveBaseline,
    baseline=pinBaseline, original=original,
    stored=savedAfter, desiredId=chosen
  }
end
local function performCheck(selectedIndex)
  local original,latest,probe=setup(selectedIndex)
  local chosen=selectedId
  checkSelected()
  local savedStillOriginal=RRECollectorData.toolbarSlots==original
  for i=1,MAX_SLOTS do
    if original[i]~="ORIGINAL_SLOT_"..i
      or slots[i]~="ORIGINAL_SLOT_"..i then savedStillOriginal=false end
  end
  return {
    noDetail=#detailCalls==0 and checked[chosen]==nil,
    detailGood=#detailCalls==1 and detailCalls[1]==chosen
      and checked[chosen]~=nil,
    storageUntouched=savedStillOriginal and pinSlot==1 and pinBaseline==nil
      and RRECollectorData.latest==latest and RRECollectorData.probe==probe,
    desiredId=chosen
  }
end
return {pin=performPin,check=performCheck}
]==]
local compilation=prelude..selector.."\n"..pin.."\n"..between..checkBody.."\n"..suffix
local chunk,err=(loadstring or load)(compilation,"RC31 source click guards")
assert(chunk,"source-extracted click guards could not compile: "..tostring(err))
local handlers=chunk()
local failNames,failures,checks={},0,0
local function check(label,passed)
  checks=checks+1
  if passed then print("PASS "..label)
  else failNames[label]=true; failures=failures+1; print("RED "..label) end
end
-- A01 is API-known but hidden on page two (visible IDs A09..A16).
local hiddenPin=handlers.pin(1)
check("hidden known Pin leaves saved slots untouched",
  hiddenPin.unchanged and hiddenPin.unrelatedUntouched)
local hiddenCheck=handlers.check(1)
check("hidden known Check makes zero Detail calls",
  hiddenCheck.noDetail and hiddenCheck.storageUntouched)
-- A09 is visibly present on page two; both callbacks remain functional.
local visiblePin=handlers.pin(9)
local visibleCheck=handlers.check(9)
local valid=visiblePin.pinChanged and visiblePin.unrelatedUntouched
  and visiblePin.persistedAsExpected and visiblePin.baselinePreserved
  and visibleCheck.detailGood and visibleCheck.storageUntouched
check("visible known Pin and Check still operate", valid)

if mode=="--expect-red" then
  local expected={
    ["hidden known Pin leaves saved slots untouched"]=true,
    ["hidden known Check makes zero Detail calls"]=true
  }
  assert(checks==3 and failures==2,
    "expected exactly two of three frozen-source defects, observed "..failures)
  for label in pairs(expected) do assert(failNames[label],"missing expected RED: "..label) end
  for label in pairs(failNames) do assert(expected[label],"unexpected RED: "..label) end
  print("EXPECTED_RED_RC31_HIDDEN_CLICKS "..failures.."/"..checks.."; no addon changes")
else
  assert(failures==0,"RC31 hidden-selection click guards not yet implemented ("..failures.." defects)")
  print("PASS_RC31_HIDDEN_CLICKS "..checks.." scenarios")
end
