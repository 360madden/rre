-- RC-27: source-extracted pin/undo tests; no RIFT process or SavedVariables file.
local f = assert(io.open("addons/RRECollector/ui.lua", "rb"))
local src = f:read("*a"); f:close()
local section = assert(src:match("%-%- RC27%-PIN%-BEGIN(.-)%-%- RC27%-PIN%-END"))
local prefix = [==[
local checks, draws, notes = 0, 0, {}
local function check(v, why) assert(v, why); checks = checks + 1 end
local function say(v) notes[#notes+1] = v end
local function draw() draws = draws + 1 end
local MAX_SLOTS = 8
local slots = {"A1","A2","A3","A4","A5","A6","A7","A8"}
local pinSlot, pinBaseline = 1, nil
local selectedId, selectedKind = "B", "known"
local knownIDs = {B=true,C=true}
local function knownMap() return knownIDs end
local savedOriginal = {"A1","A2","A3","A4","A5","A6","A7","A8"}
local latest = {magic="preserve"}
local probe = {magic="preserve"}
local candidateLookup = {magic="preserve"}
local RRECollectorData = {toolbarSlots=savedOriginal,latest=latest,probe=probe,candidateLookup=candidateLookup}
local function saved() return RRECollectorData end
]==]
local suffix = [==[
pinSelected()
check(slots[1]=="B" and pinSlot==2, "first click replaces slot 1")
check(RRECollectorData.toolbarSlots ~= savedOriginal, "new table written")
check(RRECollectorData.toolbarSlots[2]=="A2", "other slot preserved")
check(RRECollectorData.latest==latest and RRECollectorData.probe==probe
  and RRECollectorData.candidateLookup==candidateLookup, "research receipts unchanged")
selectedId="C"; pinSelected()
check(slots[2]=="C" and pinSlot==3, "second pin uses next slot")
undoPins()
check(pinBaseline==nil and pinSlot==1, "undo resets baseline and destination")
check(RRECollectorData.toolbarSlots==savedOriginal, "original table identity restored")
for i=1,8 do check(slots[i]=="A"..i, "slot "..i.." restored") end
local oldDraws=draws
undoPins()
check(draws==oldDraws, "repeat undo is inert")
selectedKind="static"; pinSelected()
check(pinBaseline==nil and RRECollectorData.toolbarSlots==savedOriginal,
  "static candidate rejected")
selectedKind="known"; selectedId="Z"; pinSelected()
check(pinBaseline==nil and RRECollectorData.toolbarSlots==savedOriginal,
  "unknown ID rejected")
selectedId="B"; pinSlot=8; pinSelected()
check(slots[8]=="B" and pinSlot==1, "last slot wraps next destination")
undoPins()
check(slots[8]=="A8" and pinSlot==8, "wrap undo restores destination")
RRECollectorData.toolbarSlots=nil
pinSlot=1; pinBaseline=nil
pinSelected()
check(type(RRECollectorData.toolbarSlots)=="table", "initially absent table created")
undoPins()
check(RRECollectorData.toolbarSlots==nil and slots[1]=="A1",
  "absent original table restored exactly")
RRECollectorData=nil
pinSelected()
check(pinBaseline==nil, "missing SavedVariables refuses mutation")
print("PASS "..checks.." RC-27 pin/undo assertions (mock UI state)")
]==]
local compile = loadstring or load
assert(compile(prefix .. section .. suffix, "RC-27 pins"))()
