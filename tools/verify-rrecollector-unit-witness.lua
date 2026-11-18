-- Offline v0.4.23 bounded unit witness regression; no RIFT interaction.
dofile("addons/RRECollector/core.lua")
dofile("addons/RRECollector/units.lua")
local capture = RRECollectorRuntime.units.capture
local checks = 0
local function check(value, why) assert(value, why); checks = checks + 1 end
local selfId, calls = "u0000000000000001", {}
local function id(n) return "u" .. string.format("%016X", n) end
local current, customDetail
local function setList(values)
  current = values
  calls = {list = 0, lookup = 0, detail = 0, detailIds = {}, clock = 0}
  Inspect = {Time = {
    Frame = function() calls.clock = calls.clock + 1; return calls.clock * 0.5 end,
    Real = function() return 1795030000 end
  }, Unit = {
    Lookup = function(spec)
      calls.lookup = calls.lookup + 1
      check(spec == "player", "only player Lookup permitted")
      return selfId
    end,
    List = function() calls.list = calls.list + 1; return current end,
    Detail = function(unit)
      calls.detail = calls.detail + 1
      calls.detailIds[#calls.detailIds + 1] = unit
      if customDetail then return customDetail(unit) end
      return {id = unit, coordX = 0, coordY = -2, coordZ = 3}
    end
  }}
end

Inspect = nil
local r = capture()
check(r.status == "unavailable" and r.reason == "missing-unit-api"
  and #r.records == 0, "missing API safely unavailable")
setList({})
Inspect.Unit.Lookup = function() return nil end
r = capture()
check(r.status == "unavailable" and r.reason == "player-id-unavailable"
  and calls.list == 0, "missing self rejects List")
setList({})
Inspect.Unit.List = function() error("synthetic List failure") end
r = capture()
check(r.status == "error" and r.reason == "unit-list-error"
  and calls.list == 0, "List exception no Detail")
setList({})
Inspect.Unit.List = function() return nil end
r = capture()
check(r.status == "unavailable" and r.reason == "unit-list-non-table"
  and calls.detail == 0, "non-table distinguished")
setList({})
r = capture()
check(r.status == "empty" and r.reason == "no-nonself-listed"
  and r.listEnumerationComplete and r.detailSampleComplete
  and calls.list == 1 and calls.detail == 0, "empty List not missing API")
check(r.frameStart == 0.5 and r.frameEnd == 1
  and r.realStart == 1795030000 and r.realEnd == 1795030000,
  "frame and real clock bounds retained")
check(not r.atomicSnapshot and not r.nativeIdentityVerified
  and not r.coordinateFrameVerified, "truth boundaries remain false")

setList({[selfId] = "player", [id(2)] = "group01"})
r = capture()
check(r.status == "complete" and r.counts.selfEntries == 1
  and r.counts.nonselfEligible == 1 and r.counts.qualifiedXYZ == 1
  and r.counts.detailsCalled == 1, "exact bounded nonself capture")
check(r.records[1].id == id(2) and r.records[1].specifier == "group01"
  and r.records[1].idBinding == "matched" and r.records[1].xyzComplete
  and r.records[1].coordX == 0 and r.records[1].coordY == -2,
  "actual key-value orientation, zero and negative coordinates")
check(calls.lookup == 1 and calls.list == 1 and calls.detail == 1,
  "manual API call budget per capture")

setList({[id(2)] = "x", [id(3)] = "y"})
customDetail = function(unit)
  if unit == id(2) then return {id = id(999), coordX = 2, coordY = 3, coordZ = 4} end
  return {coordX = 0, coordY = 2, coordZ = 3}
end
r = capture()
check(r.status == "partial" and r.reason == "detail-identity-unqualified"
  and r.counts.idMismatches == 1 and r.counts.idMissing == 1,
  "missing/mismatched exact Detail IDs unqualified")
check(r.records[1].coordX == nil and r.records[2].coordX == nil
  and not r.records[1].xyzComplete and not r.records[2].xyzComplete,
  "unbound coordinates not carried into qualification")
customDetail = nil

setList({[id(2)] = "x", [id(3)] = "y"})
customDetail = function(unit)
  if unit == id(2) then return {id = unit, coordX = 0, coordY = 0/0, coordZ = 1} end
  return {id = unit, coordX = 0, coordY = math.huge, coordZ = -math.huge}
end
r = capture()
check(r.status == "partial" and r.reason == "xyz-incomplete"
  and r.counts.qualifiedXYZ == 0, "NaN and infinities never qualify XYZ")
check(r.records[1].coordX == 0 and r.records[1].coordY == nil
  and r.records[2].coordZ == nil, "zero remains distinct from absent coordinate")
customDetail = nil

setList({[id(2)] = "x", [id(3)] = "y"})
customDetail = function(unit)
  if unit == id(2) then error("synthetic Detail failure") end
  return {id = unit, coordX = 0, coordY = 1, coordZ = 2}
end
r = capture()
check(r.status == "partial" and r.reason == "detail-errors"
  and r.counts.detailErrors == 1 and r.counts.qualifiedXYZ == 1,
  "individual Detail exception isolated and counted")
customDetail = nil

setList({["uINVALID000000000"] = "x", [id(2)] = "\n", [id(3)] = "valid"})
r = capture()
check(r.status == "partial" and r.reason == "invalid-list-entries"
  and r.counts.invalidEntries == 2 and r.counts.detailsCalled == 1,
  "invalid IDs/specifiers never selected")

local many = {}
for n=2, 10 do many[id(n)] = "u" .. tostring(n) end
setList(many)
r = capture()
check(r.status == "partial" and r.reason == "detail-sample-cap"
  and r.counts.nonselfEligible == 9 and r.counts.detailsCalled == 8
  and not r.detailSampleComplete and #r.records == 8,
  "nine IDs bounded to eight Details")
for i = 1, 8 do
  check(calls.detailIds[i] == id(i + 1), "deterministic sorted subset " .. i)
end

many = {}
for n=2, 129 do many[id(n)] = "u" .. tostring(n) end
setList(many)
r = capture()
check(r.status ~= "capped" and r.counts.examined == 128
  and r.listEnumerationComplete and calls.detail == 8,
  "128 entries exactly within List cap")
many[id(130)] = "u130"
setList(many)
r = capture()
check(r.status == "capped" and r.reason == "list-cap-reached"
  and r.counts.examined == 128 and not r.listEnumerationComplete
  and not r.detailSampleComplete and calls.detail <= 8,
  "129 entries explicitly capped; bounded Detail count")
check(r.limits.listEntries == 128 and r.limits.detailCalls == 8,
  "limits self-describing")
print("RRE_UNIT_WITNESS_PASS " .. checks)
