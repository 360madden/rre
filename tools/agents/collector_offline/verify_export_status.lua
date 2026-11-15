-- RRECollector /rre export source-extracted regression; no RIFT or SavedVariables I/O.
-- Run from repository root with Lua 5.1+.
local checks = 0
local function check(ok, why) assert(ok, why); checks = checks + 1 end
local file = assert(io.open("addons/RRECollector/main.lua", "rb"))
local source = assert(file:read("*a")); file:close()
local startAt = assert(source:find("local function onSlash(_, raw)", 1, true))
local endAt = assert(source:find(
  "\n-- UI buttons reuse the same guarded slash-command behavior", startAt, true))
local section = source:sub(startAt, endAt - 1)
local compile = loadstring or load
local chunk = assert(compile(
  "local say, RRECollectorData, savedLoaded, VERSION = ...\n"
  .. section .. "\nreturn onSlash", "RRECollector actual onSlash"))

local messages = {}
local function say(line) messages[#messages + 1] = line end
local saved = {addonVersion = "0.4.14"}
local slash = chunk(say, saved, true, "0.4.14")
local function report(value)
  saved.latest = value
  messages = {}
  slash(nil, "export")
  check(#messages > 0, "export always explains outcome")
  check(saved.latest == value, "export never changes snapshot")
  return table.concat(messages, "\n")
end

local empty = report(nil)
check(not empty:find("Full snapshot", 1, true), "no snapshot is not full")
check(empty:lower():find("capture", 1, true), "no snapshot offers capture command")

local malformed = report("not-a-capture")
check(not malformed:find("Full snapshot", 1, true), "malformed snapshot is not full")

local incomplete = {addonVersion = "0.4.14", captureComplete = false, sequence = 5}
local partial = report(incomplete)
check(not partial:find("Full snapshot", 1, true), "incomplete capture is not full")
check(partial:lower():find("incomplete", 1, true)
  or partial:lower():find("partial", 1, true), "incomplete capture is labeled")

local current = {addonVersion = "0.4.14", captureComplete = true, sequence = 6}
local full = report(current)
check(full:find("RRECollectorData.latest", 1, true)
  or full:find("SavedVariables", 1, true), "complete snapshot location given")
check(full:lower():find("reload", 1, true)
  or full:lower():find("logout", 1, true), "disk flush is stated")

local historical = {addonVersion = "0.4.13", captureComplete = true, sequence = 7}
local stale = report(historical)
check(stale:find("0.4.13", 1, true), "saved snapshot version shown")
check(stale:find("0.4.14", 1, true), "loaded addon version distinguished")
check(saved.addonVersion == "0.4.14" and saved.latest == historical
  and historical.sequence == 7, "historical save retained untouched")
print("COLLECTOR_EXPORT_STATUS_PASS " .. checks)
