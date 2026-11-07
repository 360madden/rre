-- SC622 synthetic host-only producer checks; no RIFT APIs or game I/O.
local root, output = assert(arg[1]), assert(arg[2])
local checks = 0
local function check(value, reason) assert(value, reason); checks = checks + 1 end
dofile(root .. "/addons/RRECollector/core.lua")
local VERSION = RRECollectorRuntime.VERSION
local function loadWire() dofile(root .. "/addons/RRECollector/wire.lua"); return RRECollectorRuntime.wire end
local wire = loadWire()
local function record(sequence)
  return {captureComplete = true, addonVersion = VERSION, sequence = sequence or 1,
    frameTime = 12.125, realTime = 1794078000,
    player = {id = "uFIXTURE", name = "Bolinao fixture", calling = "rogue", level = 43, combat = false, power = 0,
      race = "mathosian", raceName = "Mathosian", zone = "zFIXTURE"},
    roleSlot = 1, capabilities = {player = true},
    abilityList = {apiAvailable = true, batchDetailAvailable = true, enumerationComplete = true,
      rawEntries = 1, uniqueCount = 1, detailCount = 1, detailFailures = 0, duplicates = 0, ignored = 0, truncated = 0, fallbackCalls = 0},
    abilities = {{lookupId = "A0000000100000000", name = "\195\137clair \230\176\180 \240\159\152\128", passive = false, cooldown = 0, target = "uTARGET", description = "controls\0\1\31\n\"\\"}}}
end
check(RRECollector_WireFrames == nil and wire.receipt().reason == "addon-load", "load clears wire")
local first = wire.publish(record())
check(first.status == "complete" and #first.session == 32 and first.parts == #RRECollector_WireFrames, "valid publication")
local token = first.session
check(wire.publish(record()).reason == "sequence" and RRECollector_WireFrames == nil, "duplicate clears")
check(wire.publish(record(2)).session == token, "same load session")
wire.beginAttempt(); check(RRECollector_WireFrames == nil and wire.receipt().status == "pending", "attempt clears")
wire.abort("fixture-abort"); check(RRECollector_WireFrames == nil and wire.receipt().reason == "fixture-abort", "abort clears")
local sequence = 3
local function reject(mutate, reason)
  local r = record(sequence); sequence = sequence + 1; mutate(r)
  local result = wire.publish(r)
  check(result.status == "failed" and result.reason == reason and RRECollector_WireFrames == nil, "reject " .. reason)
end
for _, malformed in ipairs({"\128", "\192\128", "\194", "\224\128\128", "\237\160\128", "\240\128\128\128", "\244\144\128\128", "\245\128\128\128", "\255"}) do
  reject(function(r) r.abilities[1].name = malformed end, "utf8")
end
reject(function(r) r.stats = {["bad\128"] = true} end, "utf8")
reject(function(r) r.abilityList.duplicates = 500 end, "counts")
reject(function(r) r.abilityList.fallbackCalls = 2 end, "counts")
reject(function(r) r.abilityList.batchDetailAvailable = false end, "counts")
reject(function(r) r.abilities[1].cooldown = 0 / 0 end, "ability-field")
reject(function(r) r.abilities[1].name = string.rep("x", 4097) end, "string-limit")
reject(function(r) r.abilities[1].unknown = false end, "ability-field")
reject(function(r) r.abilities[2] = r.abilities[1] end, "ability-shape")
reject(function(r) r.abilities[1].lookupId = "A0000000100000000\n" end, "ability-id")
reject(function(r) r.captureComplete = false end, "capture-unqualified")
reject(function(r) r.stats = {}; r.stats.self = r.stats end, "context-shape")
reject(function(r) r.stats = {}; for i = 1, 257 do r.stats["k" .. i] = i end end, "context-shape")
reject(function(r) r.stats = {}; for i = 1, 256 do r.stats["k" .. i] = string.rep("x", 256) end end, "payload-limit")
reject(function(r) r.player.extra = false end, "context-shape")
reject(function(r) r.roleNames = {{nested = false}} end, "context-shape")
reject(function(r) r.statsTruncated = false end, "context-shape")
reject(function(r) r.capabilities.stats = {} end, "context-shape")
reject(function(r) r.clientVersion = {nested = {}} end, "context-shape")
reject(function(r) r.scope = false end, "context-shape")
local fallback = record(sequence); sequence = sequence + 1
fallback.abilityList.batchDetailAvailable = false; fallback.abilityList.fallbackCalls = 1
check(wire.publish(fallback).status == "complete", "scalar fallback coherent")
local duplicates = record(sequence); sequence = sequence + 1
duplicates.abilityList.rawEntries = 2; duplicates.abilityList.duplicates = 1
check(wire.publish(duplicates).status == "complete", "duplicates coherent")
local multiple = record(sequence)
multiple.abilities[1].description = string.rep("\195\169", 2048)
local result = wire.publish(multiple)
check(result.status == "complete" and result.parts >= 2 and result.session == token, "multipart UTF8 complete")
for _, frame in ipairs(RRECollector_WireFrames) do
  check(#frame <= 8192 and not frame:find("[\128-\255]"), "bounded ASCII frame")
end
local f = assert(io.open(output, "wb"))
f:write("RRE_WIRE_FIXTURE_PASS ", checks, " ", result.session, " ", result.sequence, " ", result.parts, "\n")
for _, frame in ipairs(RRECollector_WireFrames) do f:write(frame, "\n") end
f:close()
loadWire(); check(RRECollector_WireFrames == nil, "reload clears wire")
print("RRE_WIRE_FIXTURE_PASS " .. checks)
