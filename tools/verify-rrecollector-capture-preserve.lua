-- RC-27: source-extracted capture preservation tests; no RIFT/game I/O.
dofile("addons/RRECollector/core.lua")
local f = assert(io.open("addons/RRECollector/main.lua", "rb"))
local src = f:read("*a"); f:close()
local section = assert(src:match("%-%- RC27%-CAPTURE%-BEGIN(.-)%-%- RC27%-CAPTURE%-END"))
local savedHelper = assert(src:match("(local function savedSnapshotComplete.-)local function nextSequence%("))
local prefix = [==[
local checks, refreshes, notes = 0, 0, {}
local finite = RRECollectorRuntime.core.finite
local function check(v, why) assert(v, why); checks=checks+1 end
local function say(v) notes[#notes+1] = v end
local function refreshUI() refreshes=refreshes+1 end
local savedLoaded, lastMessage = true, "ready"
local prior={captureComplete=true, abilities={{lookupId="A0000000100000000"}},
  abilityList={apiAvailable=true,enumerationComplete=true,uniqueCount=1,
    detailCount=1,detailFailures=0,ignored=0,truncated=0},
  player={id="uFIXTURE",name="Prior snapshot",calling="warrior",level=43},magic="baseline"}
local RRECollectorData={latest=prior,sequence=4}
local record
local collect=function() return record end
]==]
local suffix = [==[
local function preserved(why)
  check(RRECollectorData.latest==prior and RRECollectorData.sequence==4, why)
end
record={captureComplete=false,sequence=5,abilityList={apiAvailable=false,uniqueCount=0,detailCount=0}}
recordCapture(); preserved("API missing preserves completed catalog")
check(lastMessage=="capture-error", "missing API recognized")
check(RRECollectorData.captureAttempt.status=="failed"
  and RRECollectorData.captureAttempt.reason=="api-capture-error"
  and RRECollectorData.captureAttempt.attemptSequence==1
  and RRECollectorData.captureAttempt.priorSequence==4
  and RRECollectorData.captureAttempt.resultSequence==nil
  and RRECollectorData.captureAttempt.preservedPrior==true,
  "failed capture receipt records prior preservation without advancing capture sequence")
record={captureComplete=false,sequence=5,abilityList={apiAvailable=true,uniqueCount=1,detailCount=0}}
recordCapture(); preserved("incomplete Detail retains completed catalog")
check(lastMessage=="capture-incomplete-preserved", "partial recorded as non-destructive")
check(RRECollectorData.captureAttempt.attemptSequence==2
  and RRECollectorData.captureAttempt.status=="incomplete-preserved"
  and RRECollectorData.captureAttempt.reason=="capture-incomplete"
  and RRECollectorData.captureAttempt.counts.uniqueCount==1,
  "incomplete attempt counts retained separately from complete snapshot")
record={captureComplete=false,sequence=5}
recordCapture(); preserved("malformed response preserves snapshot")
check(RRECollectorData.captureAttempt.attemptSequence==3
  and RRECollectorData.captureAttempt.counts==nil,
  "malformed capture cannot leak earlier counts")
collect=function() error("API throws") end
recordCapture(); preserved("exception preserves snapshot")
check(RRECollectorData.captureAttempt.attemptSequence==4
  and RRECollectorData.captureAttempt.status=="failed", "API exception persisted")
collect=function() return record end
local previousAttempt=RRECollectorData.captureAttempt
savedLoaded=false; recordCapture(); preserved("unloaded save refuses capture")
check(RRECollectorData.captureAttempt==previousAttempt,
  "attempt cannot persist before SavedVariables load")
savedLoaded=true
record={captureComplete=true,sequence=5,abilityList={apiAvailable=true,uniqueCount=3,detailCount=3}}
recordCapture()
check(RRECollectorData.latest==record and RRECollectorData.sequence==5,
  "complete successful refresh replaces prior")
check(refreshes==1 and lastMessage=="capture-complete", "UI refreshed only on success")
check(RRECollectorData.captureAttempt.attemptSequence==5
  and RRECollectorData.captureAttempt.status=="complete"
  and RRECollectorData.captureAttempt.reason=="none"
  and RRECollectorData.captureAttempt.priorSequence==4
  and RRECollectorData.captureAttempt.resultSequence==5
  and RRECollectorData.captureAttempt.preservedPrior==false,
  "accepted complete capture has truthful independent receipt")
local partialOld={captureComplete=false}
RRECollectorData.latest=partialOld
record={captureComplete=false,sequence=6,abilityList={apiAvailable=true,uniqueCount=3,detailCount=2}}
recordCapture()
check(RRECollectorData.latest==record and RRECollectorData.sequence==6,
  "partial replaces prior partial when API present")
check(RRECollectorData.captureAttempt.attemptSequence==6
  and RRECollectorData.captureAttempt.status=="partial"
  and RRECollectorData.captureAttempt.resultSequence==6,
  "partial accepted with independent monotonic attempt counter")
record={captureComplete=false,sequence=7,frameTime=0/0,realTime=math.huge,
  abilityList={apiAvailable=true,uniqueCount=-2,detailCount=2.5,detailFailures=math.huge}}
recordCapture()
check(RRECollectorData.captureAttempt.attemptSequence==7
  and RRECollectorData.captureAttempt.frameTime==nil
  and RRECollectorData.captureAttempt.realTime==nil
  and RRECollectorData.captureAttempt.counts==nil,
  "nonfinite and invalid numeric metadata omitted from receipt")
print("PASS "..checks.." RC-27 capture preservation assertions (mock handler)")
]==]
local compile = loadstring or load
assert(compile(prefix .. savedHelper .. section .. suffix, "RC-27 capture"))()
