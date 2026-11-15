-- RRECollector status must not label malformed retained catalogs complete.
-- Source-extracted actual function; synthetic SavedVariables stay in memory only.
local checks = 0
local function check(ok, why) assert(ok, why); checks = checks + 1 end
local file = assert(io.open("addons/RRECollector/main.lua", "rb"))
local source = assert(file:read("*a")); file:close()
local startAt = assert(source:find("local function candidateStatus()", 1, true))
local endAt = assert(source:find("\nlocal function showPage(", startAt, true))
local compile = loadstring or load
local chunk = assert(compile(
  "local RRECollectorData, say, VERSION, savedLoaded = ...\n"
  .. source:sub(startAt, endAt - 1) .. "\nreturn status",
  "RRECollector actual status"))

local printed = {}
local function say(v) printed[#printed + 1] = v end
local list = {uniqueCount = 1, detailCount = 1, detailFailures = 0,
  ignored = 0, truncated = 0}
local player = {name = "Atank", calling = "warrior", level = 45}
local abilities = {{lookupId = "A0123456789ABCDEF", name = "Fixture"}}
local latest = {addonVersion = "0.4.14", sequence = 7, captureComplete = true,
  abilityList = list, player = player, abilities = abilities}
local saved = {latest = latest}
local status = chunk(saved, say, "0.4.14", true)
local function expectComplete(label, value)
  printed = {}
  local ok, err = pcall(status)
  check(ok, label .. ": status executes: " .. tostring(err))
  local output = table.concat(printed, "\n")
  check(output:find("| complete " .. tostring(value), 1, true),
    label .. ": expected truthful complete " .. tostring(value))
end

expectComplete("valid current", true)
latest.addonVersion = "0.4.13"
expectComplete("valid retained historical capture", true)
latest.addonVersion = "0.4.14"

latest.captureComplete = false
expectComplete("saved partial", false)
latest.captureComplete = true

latest.abilityList = 42
expectComplete("numeric ability list", false)
latest.abilityList = list

latest.player = 7
expectComplete("numeric player", false)
latest.player = player

latest.abilities = 99
expectComplete("numeric abilities", false)
latest.abilities = abilities

latest.abilities = nil
expectComplete("missing abilities", false)
latest.abilities = abilities

check(saved.latest == latest and latest.sequence == 7 and latest.captureComplete
  and latest.abilityList == list and latest.player == player
  and latest.abilities == abilities, "status never mutates retained capture")
print("COLLECTOR_STATUS_COMPLETE_SHAPE_PASS " .. checks)
