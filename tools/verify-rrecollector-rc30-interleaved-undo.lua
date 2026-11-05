-- RC-30: source-extracted interleaved Pin -> Capture -> Retry -> Undo safety.
-- Offline synthetic API/SavedVariables; never communicates with physical RIFT.
local function read(path)
  local f = assert(io.open(path, "rb"))
  local contents = f:read("*a")
  f:close()
  return contents:gsub("\r\n", "\n")
end
local ui = read("addons/RRECollector/ui.lua")
local main = read("addons/RRECollector/main.lua")
local function between(src, startAt, endAt)
  local a = assert(src:find(startAt, 1, true), "source anchor absent: " .. startAt)
  local b = assert(src:find(endAt, a + #startAt, true), "source terminator absent: " .. endAt)
  return src:sub(a, b - 1)
end
local pins = between(ui, "-- RC27-PIN-BEGIN", "-- RC27-PIN-END")
local uiRefreshStart = assert(ui:find("runtime.ui = {", 1, true))
local refreshImplementation = ui:sub(uiRefreshStart)
assert(refreshImplementation:find("toggle = toggle", 1, true),
  "not at expected UI refresh implementation")
local mainRefresh = between(main, "local function refreshUI(clearChecks)",
  "local function candidateStatus()")
local mainCandidate = between(main, "local function runCandidateLookup(trigger)",
  "-- At most two event-driven automatic retries")
local mainCapture = between(main, "-- RC27-CAPTURE-BEGIN", "-- RC27-CAPTURE-END")
local prefix = [==[
local checks=0
local function check(value, reason) assert(value, reason); checks=checks+1 end
local function say(_) end
local draws=0
local function draw() draws=draws+1 end
local function start() end
local function toggle() end
local MAX_SLOTS, pinSlot, pinBaseline=8,1,nil
local slots={}
local baselineSaved={}
for i=1,8 do slots[i]="ORIGINAL_"..i; baselineSaved[i]=slots[i] end
local selectedId,selectedKind="KNOWN_NEW","known"
local function knownMap() return {KNOWN_NEW=true} end
local originalLatest={captureComplete=true, marker="original"}
local originalCandidates={apiReady=true, marker="prior"}
local originalProbe={marker="unchanged"}
local RRECollectorData={toolbarSlots=baselineSaved,latest=originalLatest,
  candidateLookup=originalCandidates,probe=originalProbe,candidateSequence=5}
local function saved() return RRECollectorData end
local checked={KNOWN_NEW=true}
local runtime={}
local RRECollectorRuntime=runtime
local VERSION,SCHEMA="0.4.10",1
local savedLoaded=true
local lastMessage="ready"
local pendingContextRetry,automaticCandidateRetries=false,0
local collect=function()
  return {captureComplete=true,sequence=7,abilityList={apiAvailable=true,
    uniqueCount=69,detailCount=69},marker="new"}
end
local candidateLookup=function()
  -- Mirror the actual producer: one listed control plus 57 unlisted queries.
  return {apiReady=true,counts={listed=39,unlisted=57,
    listedControlQueried=1,unlistedQueried=57,queried=58,
    returned=51,unlistedReturned=50,noDetail=7,
    errors=0,inconclusiveTables=0,skipped=0},marker="new"}
end
]==]
local suffix = [==[
-- First pin establishes a reversible saved-table identity and eight-slot baseline.
pinSelected()
check(slots[1]=="KNOWN_NEW" and pinBaseline~=nil and pinSlot==2,
  "pin opens reversible baseline")
check(RRECollectorData.toolbarSlots~=baselineSaved,"pin writes new table")
check(RRECollectorData.latest==originalLatest and
  RRECollectorData.candidateLookup==originalCandidates,
  "pin keeps independent reports")

-- Execute real capture routine while pin still awaits Undo.
local oldChecks=checked
recordCapture()
local newlyCaptured=RRECollectorData.latest
check(newlyCaptured~=originalLatest and newlyCaptured.marker=="new",
  "complete capture updates only latest")
check(checked~=oldChecks and next(checked)==nil,
  "real refresh(true) clears checks")
check(pinBaseline~=nil and slots[1]=="KNOWN_NEW",
  "capture refresh must not cancel pending Undo")

-- Execute real candidate retry success during the same pending Undo.
check(runCandidateLookup("manual")==true,"successful candidate retry")
local newCandidateReport=RRECollectorData.candidateLookup
check(newCandidateReport~=originalCandidates and newCandidateReport.sequence==6,
  "candidate retry updates independent report sequence")
check(pinBaseline~=nil and slots[1]=="KNOWN_NEW",
  "candidate refresh must not cancel pending Undo")
check(RRECollectorData.probe==originalProbe, "probe untouched throughout")

undoPins()
check(pinBaseline==nil and pinSlot==1,"Undo resets target")
check(RRECollectorData.toolbarSlots==baselineSaved,
  "Undo restores original saved-table reference")
for i=1,8 do check(slots[i]=="ORIGINAL_"..i and baselineSaved[i]==slots[i],
  "Undo restores slot "..i) end
check(RRECollectorData.latest==newlyCaptured and
  RRECollectorData.candidateLookup==newCandidateReport,
  "Undo does not roll back successful research reports")
check(RRECollectorData.probe==originalProbe, "Undo preserves probe")

-- Second trial: incomplete capture and explicit Detail-query failure are
-- supposed to retain their previous good snapshots while Undo remains usable.
pinSelected()
collect=function()
  return {captureComplete=false,sequence=8,abilityList={apiAvailable=true,
    uniqueCount=1,detailCount=1},marker="incomplete"}
end
recordCapture()
check(RRECollectorData.latest==newlyCaptured,
  "incomplete capture preserves prior complete snapshot")
candidateLookup=function() error("synthetic failure",0) end
check(runCandidateLookup("manual")==false,"failed retry reports deferred")
check(RRECollectorData.candidateLookup==newCandidateReport and
  RRECollectorData.candidateSequence==6,
  "failed retry does not overwrite useful report")
check(pinBaseline~=nil and slots[1]=="KNOWN_NEW",
  "negative paths retain pending Undo")
undoPins()
check(RRECollectorData.toolbarSlots==baselineSaved and pinSlot==1,
  "Undo works after failed capture and query")
for i=1,8 do check(slots[i]=="ORIGINAL_"..i,"negative path slot "..i) end
check(RRECollectorData.latest==newlyCaptured and
  RRECollectorData.candidateLookup==newCandidateReport and
  RRECollectorData.probe==originalProbe,
  "failed-research interleave preserves all existing snapshots")
print("PASS_RC30_INTERLEAVED_UNDO "..checks.." synthetic source-extracted assertions")
print("LIMIT no live input, font evidence, physical SavedVariables, or RC-30 strict acceptance")
]==]
local program=table.concat({prefix,refreshImplementation,mainRefresh,
  pins,mainCandidate,mainCapture,suffix},"\n")
local fn,err=(loadstring or load)(program,"RC30 interleaved source-extracted")
assert(fn,"failed to compile source fragments: "..tostring(err))
fn()
