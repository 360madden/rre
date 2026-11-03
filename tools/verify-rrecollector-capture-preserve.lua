-- RC-27: source-extracted capture preservation tests; no RIFT/game I/O.
local f = assert(io.open("addons/RRECollector/main.lua", "rb"))
local src = f:read("*a"); f:close()
local section = assert(src:match("%-%- RC27%-CAPTURE%-BEGIN(.-)%-%- RC27%-CAPTURE%-END"))
local prefix = [==[
local checks, refreshes, notes = 0, 0, {}
local function check(v, why) assert(v, why); checks=checks+1 end
local function say(v) notes[#notes+1] = v end
local function refreshUI() refreshes=refreshes+1 end
local savedLoaded, lastMessage = true, "ready"
local prior={captureComplete=true, abilities={{lookupId="A1"}},magic="baseline"}
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
record={captureComplete=false,sequence=5,abilityList={apiAvailable=true,uniqueCount=1,detailCount=0}}
recordCapture(); preserved("incomplete Detail retains completed catalog")
check(lastMessage=="capture-incomplete-preserved", "partial recorded as non-destructive")
record={captureComplete=false,sequence=5}
recordCapture(); preserved("malformed response preserves snapshot")
collect=function() error("API throws") end
recordCapture(); preserved("exception preserves snapshot")
collect=function() return record end
savedLoaded=false; recordCapture(); preserved("unloaded save refuses capture")
savedLoaded=true
record={captureComplete=true,sequence=5,abilityList={apiAvailable=true,uniqueCount=3,detailCount=3}}
recordCapture()
check(RRECollectorData.latest==record and RRECollectorData.sequence==5,
  "complete successful refresh replaces prior")
check(refreshes==1 and lastMessage=="capture-complete", "UI refreshed only on success")
local partialOld={captureComplete=false}
RRECollectorData.latest=partialOld
record={captureComplete=false,sequence=6,abilityList={apiAvailable=true,uniqueCount=3,detailCount=2}}
recordCapture()
check(RRECollectorData.latest==record and RRECollectorData.sequence==6,
  "partial replaces prior partial when API present")
print("PASS "..checks.." RC-27 capture preservation assertions (mock handler)")
]==]
local compile = loadstring or load
assert(compile(prefix .. section .. suffix, "RC-27 capture"))()
