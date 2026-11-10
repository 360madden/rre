-- Offline regression for RRECollector manual readiness; no RIFT client or input.
-- Execute from repository root with Lua 5.1 or newer.
local checks = 0
local function check(value, name)
  assert(value, name)
  checks = checks + 1
end

RRECollectorRuntime = {}
dofile("addons/RRECollector/core.lua")
RRECollectorRuntime.context = {snapshot = function() return {} end}
dofile("addons/RRECollector/abilities.lua")

local file = assert(io.open("addons/RRECollector/ui.lua", "rb"))
local source = assert(file:read("*a"))
file:close()
local beginAt = assert(source:find("local function apiCheck(id)", 1, true), "apiCheck source missing")
local endAt = assert(source:find("\nlocal function checkPinned()", beginAt, true), "apiCheck boundary missing")
local extracted = source:sub(beginAt, endAt - 1)
local compile = loadstring or load
local chunk = assert(compile("local runtime, knownMap, Inspect, color = ...\n"
  .. extracted .. "\nreturn apiCheck", "RRECollector actual apiCheck"))
local ID = "A0123456789ABCDEF"
local current
local Inspect = {Ability = {New = {Detail = function()
  if current == "throw-call" then error("Detail call error") end
  return current
end}}}
local colors = {grey = {}, red = {}, amber = {}, cyan = {}}
local apiCheck = chunk(RRECollectorRuntime, function() return {[ID] = {}} end, Inspect, colors)

local function verify(detail, expected, label)
  current = detail
  local ok, result = pcall(apiCheck, ID)
  check(ok, label .. ": API field getter must not crash")
  check(type(result) == "table" and result.status == expected,
    label .. ": expected " .. expected .. ", got " .. tostring(result and result.status))
end

verify({passive = false, unusable = false, outOfRange = false,
  currentCooldownRemaining = 0}, "API NO BLOCK*", "ordinary zero cooldown")
verify({passive = true}, "PASSIVE", "passive status")
verify({unusable = false, outOfRange = true}, "OUT OF RANGE", "range status")
verify({unusable = false, outOfRange = false, currentCooldownRemaining = 2},
  "COOLDOWN 2.0s", "finite cooldown")
verify({unusable = false, outOfRange = false, currentCooldownRemaining = math.huge},
  "READINESS UNKNOWN", "nonfinite cooldown is not printable")
verify(setmetatable({unusable = false, outOfRange = false, currentCooldownRemaining = 0},
  {__index = function(_, key)
    if key == "passive" then error("blocked passive getter") end
  end}), "READINESS UNKNOWN", "throwing passive getter")
verify({unusable = false, outOfRange = false, currentCooldownRemaining = 0},
  "READINESS UNKNOWN", "missing passive remains unknown")
verify(setmetatable({outOfRange = false, currentCooldownRemaining = 0},
  {__index = function(_, key)
    if key == "unusable" then error("blocked unusable getter") end
  end}), "READINESS UNKNOWN", "throwing readiness getter")
verify("throw-call", "DETAIL UNKNOWN", "throwing Detail call")
local absent = apiCheck("AFFFFFFFFFFFFFFFF")
check(absent.status == "NOT IN SNAPSHOT", "unknown ability remains unknown")
print("COLLECTOR_PROXY_READINESS_PASS " .. checks)
