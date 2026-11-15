-- RRECollector /rre page must handle malformed retained SavedVariables.
-- Source-extracted actual showPage(); synthetic data only, no RIFT or disk changes.
local checks = 0
local function check(ok, why) assert(ok, why); checks = checks + 1 end
local file = assert(io.open("addons/RRECollector/main.lua", "rb"))
local source = assert(file:read("*a")); file:close()
local beginAt = assert(source:find("local function showPage(page)", 1, true))
local endAt = assert(source:find("\nlocal function help()", beginAt, true))
local compile = loadstring or load
local chunk = assert(compile(
  "local say, savedLoaded, RRECollectorData, finite = ...\n"
  .. source:sub(beginAt, endAt - 1) .. "\nreturn showPage",
  "RRECollector actual showPage"))

local lines = {}
local function say(value) lines[#lines + 1] = value end
local function finite(v)
  return type(v) == "number" and v == v and v ~= math.huge and v ~= -math.huge
end
local saved = {latest = {abilities = {}}}
local showPage = chunk(say, true, saved, finite)
local function page(records, number, label)
  saved.latest = {abilities = records}
  local original = saved.latest
  lines = {}
  local ok, err = pcall(showPage, number)
  check(ok, label .. ": no Lua exception: " .. tostring(err))
  check(saved.latest == original and saved.latest.abilities == records,
    label .. ": retained snapshot unchanged")
  return table.concat(lines, "\n")
end

local valid = page({{lookupId = "A0123456789ABCDEF", name = "Fixture"}},
  1, "one valid row")
check(valid:find("Ability page 1/1", 1, true), "valid page counter")
check(valid:find("Fixture", 1, true), "valid ID/name shown")

local nine = {}
for i = 1, 9 do nine[i] = {lookupId = "A" .. tostring(i), name = "Name" .. i} end
local second = page(nine, 2, "second page")
check(second:find("Ability page 2/2", 1, true)
  and second:find("9. A9 Name9", 1, true), "valid pagination unchanged")

local numeric = page(42, 1, "numeric ability list")
check(numeric:lower():find("invalid", 1, true)
  or numeric:lower():find("malformed", 1, true), "bad list explicitly diagnosed")
check(numeric:lower():find("capture", 1, true), "bad list offers recapture")

local text = page("not-a-list", 1, "string ability list")
check(text:lower():find("invalid", 1, true)
  or text:lower():find("malformed", 1, true), "non-table list diagnosed")

local row = page({{lookupId = "A1", name = "Good"}, 17},
  1, "numeric ability row")
check(row:lower():find("invalid", 1, true)
  or row:lower():find("malformed", 1, true), "bad row explicitly diagnosed")
check(row:lower():find("capture", 1, true), "bad row offers recapture")

local range = page({}, 3, "out-of-range")
check(range:find("Page must be 1-", 1, true), "invalid page still bounded")
print("COLLECTOR_PAGE_SAVED_SHAPES_PASS " .. checks)
