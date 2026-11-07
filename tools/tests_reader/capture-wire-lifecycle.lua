-- Exercises the actual bounded manual Capture function with the actual publisher.
-- Host-only synthetic data. No game APIs, SavedVariables file, VM or network.
local root = assert(arg[1])
dofile(root .. "/addons/RRECollector/core.lua")
dofile(root .. "/addons/RRECollector/wire.lua")
local f = assert(io.open(root .. "/addons/RRECollector/main.lua", "rb"))
local source = f:read("*a"); f:close()
local section = assert(source:match("%-%- RC27%-CAPTURE%-BEGIN(.-)%-%- RC27%-CAPTURE%-END"))
local prefix = [==[
local wire = RRECollectorRuntime.wire
local checks, notes, refreshes = 0, {}, 0
local function check(v, why) assert(v, why); checks = checks + 1 end
local function say(v) notes[#notes + 1] = v end
local function refreshUI() refreshes = refreshes + 1 end
local savedLoaded, lastMessage = true, "ready"
local function fixture(sequence)
  return {captureComplete=true,addonVersion="0.4.12",sequence=sequence,frameTime=10.5,realTime=1794078000,
    player={id="uFIXTURE",name="Fixture",calling="rogue",level=43},roleSlot=1,capabilities={player=true},
    abilityList={apiAvailable=true,batchDetailAvailable=true,enumerationComplete=true,rawEntries=1,uniqueCount=1,
      detailCount=1,detailFailures=0,duplicates=0,ignored=0,truncated=0,fallbackCalls=0},
    abilities={{lookupId="A0000000100000000",name="Fixture",passive=false,cooldown=0}}}
end
local prior = fixture(4)
local RRECollectorData = {latest=prior,sequence=4}
local record = fixture(5)
local collect = function() return record end
]==]
local suffix = [==[
recordCapture()
check(RRECollectorData.latest==record and RRECollectorData.sequence==5,"accepted snapshot")
check(RRECollector_WireFrames~=nil and RRECollectorData.memoryPublication.status=="complete","manual capture publishes")
check(notes[#notes]:match("Wire RREC2 session=[0-9a-f]+ seq=5 parts="),"local completion receipt")
local token=RRECollectorData.memoryPublication.session
prior=record
record=fixture(6);record.captureComplete=false
recordCapture()
check(RRECollectorData.latest==prior and RRECollectorData.sequence==5,"partial preserves prior-good")
check(RRECollector_WireFrames==nil and RRECollectorData.memoryPublication.reason=="capture-incomplete","partial clears wire")
record=fixture(6);record.abilityList.apiAvailable=false
recordCapture()
check(RRECollectorData.latest==prior and RRECollector_WireFrames==nil and RRECollectorData.memoryPublication.reason=="api-capture-error","API absence clears")
collect=function() error("synthetic failure") end
recordCapture()
check(RRECollectorData.latest==prior and RRECollectorData.sequence==5 and RRECollector_WireFrames==nil,"API exception preserves")
collect=function() return record end
savedLoaded=false;recordCapture()
check(RRECollectorData.latest==prior and RRECollector_WireFrames==nil and wire.receipt().reason=="saved-not-ready","unloaded clears")
savedLoaded=true;record=fixture(6);recordCapture()
check(RRECollectorData.memoryPublication.session==token and RRECollectorData.memoryPublication.sequence==6,"recovery same session")
record=fixture(7);record.abilities[1].name="\128";recordCapture()
check(RRECollectorData.latest==record and RRECollectorData.sequence==7,"wire rejection preserves new durable API snapshot")
check(RRECollector_WireFrames==nil and RRECollectorData.memoryPublication.reason=="utf8","wire rejection explicit")
check(notes[#notes]=="Wire not published: utf8","wire failure receipt")
check(refreshes==3,"UI refresh only accepted API capture")
print("SC622_CAPTURE_WIRE_LIFECYCLE_PASS "..checks)
]==]
assert((loadstring or load)(prefix .. section .. suffix, "SC622 manual Capture wire lifecycle"))()
