-- Source-extracted RRECollector status() regression; no game, input, or save writes.
-- Run from the RRE repository root with an existing Lua 5.1+ interpreter.
local checks = 0
local function check(ok, why) assert(ok, why); checks = checks + 1 end
local f = assert(io.open("addons/RRECollector/main.lua", "rb"))
local source = assert(f:read("*a")); f:close()
local startAt = assert(source:find("local function status()", 1, true))
local endAt = assert(source:find("\nlocal function showPage(", startAt, true))
local section = source:sub(startAt, endAt - 1)
local compile = loadstring or load
local chunk = assert(compile(
  "local VERSION, savedLoaded, RRECollectorData, say, candidateStatus = ...\n"
  .. section .. "\nreturn status", "RRECollector actual status"))

local output = {}
local function say(line) output[#output + 1] = line end
local latest = {
  addonVersion = "0.4.14", sequence = 7, captureComplete = true,
  player = {name = "Atank", level = 45, calling = "warrior", role = 1},
  roleSlot = 1,
  abilityList = {uniqueCount = 69, detailCount = 69, detailFailures = 0,
    ignored = 0, truncated = 0},
}
local saved = {addonVersion = "0.4.14", latest = latest}
local status = chunk("0.4.14", true, saved, say, function() end)
local function firstLine(version)
  latest.addonVersion = version
  output = {}
  status()
  check(#output >= 3 and type(output[1]) == "string", "status prints capture")
  return output[1]
end

local fresh = firstLine("0.4.14")
check(fresh:find("v0.4.14 capture #7", 1, true), "current capture version")
check(not fresh:lower():find("stale", 1, true), "current capture not stale")

local old = firstLine("0.4.13")
check(old:find("v0.4.13 capture #7", 1, true), "show actual retained capture version")
check(old:find("v0.4.14", 1, true), "show currently loaded addon version")
check(old:lower():find("saved", 1, true) or old:lower():find("prior", 1, true)
  or old:lower():find("histor", 1, true) or old:lower():find("stale", 1, true)
  or old:lower():find("loaded", 1, true),
  "historical capture distinguished from current load")

local missing = firstLine(nil)
check(missing:lower():find("unknown", 1, true) or missing:find("?", 1, true),
  "missing capture version displayed as unknown")
check(not missing:find("v0.4.14 capture #7", 1, true),
  "missing capture version never upgraded to loaded version")

local malformed = firstLine("not-a-version")
check(malformed:lower():find("unknown", 1, true) or malformed:find("?", 1, true),
  "malformed capture version is unknown")
check(not malformed:find("v0.4.14 capture #7", 1, true),
  "malformed capture version never upgraded")

local wrongType = firstLine({})
check(wrongType:lower():find("unknown", 1, true) or wrongType:find("?", 1, true),
  "non-string capture version is unknown")
check(saved.latest == latest and saved.addonVersion == "0.4.14"
  and latest.sequence == 7 and latest.abilityList.uniqueCount == 69,
  "status does not rewrite retained SavedVariables")
print("COLLECTOR_SAVED_VERSION_STATUS_PASS " .. checks)
