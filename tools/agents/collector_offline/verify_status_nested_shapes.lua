-- RRECollector /rre status guards malformed retained nested SavedVariables.
-- Source-extracted from the real addon; no game, UI, or saved-file mutation.
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
  "RRECollector actual status and candidateStatus"))

local lines = {}
local function say(v) lines[#lines + 1] = v end
local latest = {addonVersion = "0.4.14", sequence = 8, captureComplete = true,
  player = {name = "Atank", level = 45, calling = "warrior", role = 1},
  roleSlot = 1,
  abilityList = {uniqueCount = 69, detailCount = 69, detailFailures = 0,
    ignored = 0, truncated = 0}}
local saved = {latest = latest, candidateLookup = {sequence = 3,
  catalogVersion = "fixture", counts = {
    listed = 39, unlisted = 57, unlistedReturned = 50, queried = 58},
  policy = "fixed-canary"}}
local status = chunk(saved, say, "0.4.14", true)
local function run(label)
  lines = {}
  local ok, failure = pcall(status)
  check(ok, label .. ": no Lua error: " .. tostring(failure))
  check(#lines > 0, label .. ": status remains visible")
  return table.concat(lines, "\n")
end

local normal = run("normal")
check(normal:find("Known API IDs 69", 1, true), "normal catalog count")
check(normal:find("39 currently listed", 1, true), "normal candidate count")
check(saved.latest == latest, "healthy snapshot identity retained")
latest.addonVersion = "0.4.13"
local historical = run("healthy historical")
check(historical:find("v0.4.13 capture #8", 1, true), "historical version shown")
check(historical:find("loaded v0.4.14", 1, true), "loaded version remains distinct")
latest.addonVersion = "0.4.14"

saved.candidateLookup.counts = 17
local badCounts = run("numeric candidate counts")
check(badCounts:find("Known API IDs 69", 1, true), "valid ability snapshot survives broken candidate counts")
check(not badCounts:find("17 currently listed", 1, true), "wrong-type count not reported as real")

saved.candidateLookup.counts = nil
run("missing candidate counts")

latest.abilityList = 42
local badList = run("numeric ability list")
check(badList:find("Known API IDs 0", 1, true), "wrong-type ability list not presented as real")

latest.abilityList = {uniqueCount = 69}
latest.player = 7
local badPlayer = run("numeric player")
check(badPlayer:find("[name unknown]", 1, true), "wrong-type player replaced with unknown")

saved.latest = "malformed"
local noSnapshot = run("malformed latest")
check(noSnapshot:find("no snapshot", 1, true), "wrong-type latest handled")

check(saved.candidateLookup.counts == nil and saved.latest == "malformed",
  "status does not overwrite malformed saved values")
print("COLLECTOR_STATUS_NESTED_SHAPES_PASS " .. checks)
