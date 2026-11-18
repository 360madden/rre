-- Exercises the actual bounded manual Capture function with the actual publisher.
-- Host-only synthetic data. No game APIs, SavedVariables file, VM or network.
local root = assert(arg[1])
dofile(root .. "/addons/RRECollector/core.lua")
dofile(root .. "/addons/RRECollector/wire.lua")
local f = assert(io.open(root .. "/addons/RRECollector/main.lua", "rb"))
local source = f:read("*a"); f:close()
local section = assert(source:match("%-%- RC27%-CAPTURE%-BEGIN(.-)%-%- RC27%-CAPTURE%-END"))
local savedHelper = assert(source:match("(local function savedSnapshotComplete.-)local function nextSequence%("))
local prefix = [==[
local wire = RRECollectorRuntime.wire
local finite = RRECollectorRuntime.core.finite
local checks, notes, refreshes = 0, {}, 0
local function check(v, why) assert(v, why); checks = checks + 1 end
local function say(v) notes[#notes + 1] = v end
local function refreshUI() refreshes = refreshes + 1 end
local savedLoaded, lastMessage = true, "ready"
local function fixture(sequence)
  return {captureComplete=true,addonVersion=RRECollectorRuntime.VERSION,sequence=sequence,frameTime=10.5,realTime=1794078000,
    player={id="uFIXTURE",name="Fixture",calling="rogue",level=43},roleSlot=1,capabilities={player=true,experience=false},
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
check(RRECollectorData.captureAttempt.attemptSequence==1
  and RRECollectorData.captureAttempt.status=="complete"
  and RRECollectorData.captureAttempt.priorSequence==4
  and RRECollectorData.captureAttempt.resultSequence==5
  and RRECollectorData.captureAttempt.publicationStatus=="complete"
  and RRECollectorData.captureAttempt.counts.uniqueCount==1,
  "complete API capture and wire publication recorded separately")
local token=RRECollectorData.memoryPublication.session
prior=record
record=fixture(6);record.captureComplete=false
recordCapture()
check(RRECollectorData.latest==prior and RRECollectorData.sequence==5,"partial preserves prior-good")
check(RRECollector_WireFrames==nil and RRECollectorData.memoryPublication.reason=="capture-incomplete","partial clears wire")
check(RRECollectorData.captureAttempt.attemptSequence==2
  and RRECollectorData.captureAttempt.status=="incomplete-preserved"
  and RRECollectorData.captureAttempt.publicationReason=="capture-incomplete"
  and RRECollectorData.captureAttempt.preservedPrior,"incomplete receipt preserves prior")
record=fixture(6);record.abilityList.apiAvailable=false
recordCapture()
check(RRECollectorData.latest==prior and RRECollector_WireFrames==nil and RRECollectorData.memoryPublication.reason=="api-capture-error","API absence clears")
check(RRECollectorData.captureAttempt.attemptSequence==3
  and RRECollectorData.captureAttempt.status=="failed"
  and RRECollectorData.captureAttempt.publicationReason=="api-capture-error",
  "API absence has explicit publication refusal")
collect=function() error("synthetic failure") end
recordCapture()
check(RRECollectorData.latest==prior and RRECollectorData.sequence==5 and RRECollector_WireFrames==nil,"API exception preserves")
check(RRECollectorData.captureAttempt.attemptSequence==4
  and RRECollectorData.captureAttempt.status=="failed","exception receipt advances")
collect=function() return record end
local previousAttempt=RRECollectorData.captureAttempt
savedLoaded=false;recordCapture()
check(RRECollectorData.latest==prior and RRECollector_WireFrames==nil and wire.receipt().reason=="saved-not-ready","unloaded clears")
check(RRECollectorData.captureAttempt==previousAttempt,
  "unloaded handler cannot persist receipt")
savedLoaded=true;record=fixture(6);recordCapture()
check(RRECollectorData.memoryPublication.session==token and RRECollectorData.memoryPublication.sequence==6,"recovery same session")
check(RRECollectorData.captureAttempt.attemptSequence==5
  and RRECollectorData.captureAttempt.publicationStatus=="complete",
  "successful retry persists new receipt")
record=fixture(7)
record.abilities[1].name=RRECollectorRuntime.core.scalar(string.rep("a",2047)..string.char(0xC3,0xA9).."Z",2048)
recordCapture()
check(#record.abilities[1].name==2047 and RRECollectorData.memoryPublication.status=="complete"
  and RRECollector_WireFrames~=nil,"UTF8 byte cap retains complete publishable character prefix")
check(RRECollectorData.captureAttempt.attemptSequence==6,
  "valid UTF8 capture records new attempt")
record=fixture(8);record.abilities[1].name="\128";recordCapture()
check(RRECollectorData.latest==record and RRECollectorData.sequence==8,"wire rejection preserves new durable API snapshot")
check(RRECollector_WireFrames==nil and RRECollectorData.memoryPublication.reason=="utf8","wire rejection explicit")
check(RRECollectorData.captureAttempt.attemptSequence==7
  and RRECollectorData.captureAttempt.status=="complete"
  and RRECollectorData.captureAttempt.resultSequence==8
  and RRECollectorData.captureAttempt.publicationStatus==RRECollectorData.memoryPublication.status
  and RRECollectorData.captureAttempt.publicationReason=="utf8",
  "valid API snapshot and rejected UTF8 publication must stay distinct")
check(notes[#notes]=="Wire not published: utf8","wire failure receipt")
check(refreshes==4,"UI refresh only accepted API capture")
print("SC622_CAPTURE_WIRE_LIFECYCLE_PASS "..checks)
]==]
assert((loadstring or load)(prefix .. savedHelper .. section .. suffix, "SC622 manual Capture wire lifecycle"))()
