-- RC-30: source-extracted presentation tests; no RIFT client or saved-file writes.
local f = assert(io.open("addons/RRECollector/ui.lua", "rb"))
local src = f:read("*a"); f:close()
local block = assert(src:match("%-%- RC30%-SLOT%-DISPLAY%-BEGIN(.-)%-%- RC30%-SLOT%-DISPLAY%-END"))
assert(src:find("local captionName, _, _, visibleCheck = slotDisplayLabels(id, a, state)", 1, true),
  "tile paint/caption must call the shared helper")
assert(src:find("local _, tooltipHeading, statusLabel = slotDisplayLabels(id, ability, state)", 1, true),
  "tooltip must call the shared helper")
local prefix = [==[
local checks = 0
local function check(ok, why) assert(ok, why); checks = checks + 1 end
local function safe(value, fallback)
  return type(value) == "string" and #value > 0 and value or fallback
end
]==]
local suffix = [==[
local caption, title, state, checkObject = slotDisplayLabels(nil, nil, nil)
check(caption == "Empty" and title == "Empty slot", "true nil slot is empty")
check(state == "Not checked this session" and checkObject == nil,
  "nil slot cannot inherit status")

local known = {name = "Shield of the Chosen", icon = "icon.dds"}
local checked = {status = "READY (not cast proof)", tint = {0,1,1,1}}
caption, title, state, checkObject = slotDisplayLabels("A-VALID", known, checked)
check(caption == known.name and title == known.name, "known name unchanged")
check(state == checked.status and checkObject == checked, "known explicit check reused")

local savedId = "A-HISTORICAL"
local savedSlots = {savedId, nil, "A-VALID"}
local baseline = {slots = savedSlots, nextSlot = 3}
local original = savedSlots
caption, title, state, checkObject = slotDisplayLabels(savedSlots[1], nil, checked)
check(caption == "Not in list", "stale saved ID is not empty")
check(title == "ID not in current API-known snapshot", "tooltip states exact provenance gap")
check(state == "NOT IN SNAPSHOT" and checkObject == nil,
  "stale saved ID cannot reuse prior cyan/positive check")

caption, title, state, checkObject = slotDisplayLabels("", nil, checked)
check(caption == "Not in list" and state == "NOT IN SNAPSHOT",
  "blank saved string is invalid, not an empty slot")
caption, title, state, checkObject = slotDisplayLabels("A-UNKNOWN-NAME", {}, checked)
check(caption == "Unnamed ability" and title == "Unnamed ability",
  "known record with missing name does not become empty")
check(state == checked.status and checkObject == checked,
  "known unnamed record retains its explicit check")

local utfName = "Éclair 星"
caption, title = slotDisplayLabels("A-UTF", {name=utfName}, nil)
check(caption == utfName and title == utfName, "UTF-8 name unchanged")
check(savedSlots == original and savedSlots[1] == savedId and savedSlots[3] == "A-VALID",
  "presentation does not change saved IDs")
check(savedSlots[2] == nil and baseline.slots == original and baseline.nextSlot == 3,
  "sparse slots and pin baseline unchanged")

local _, _, staleStatus, staleCheck = slotDisplayLabels(savedId, nil,
  {status = "UNUSABLE", tint = {1, 0, 0, 1}})
check(staleStatus == "NOT IN SNAPSHOT" and staleCheck == nil,
  "stale check never inherits a red unusable/locked classification")
print("PASS " .. checks .. " RC-30 stale-slot presentation assertions")
]==]
local compile = loadstring or load
assert(compile(prefix .. block .. suffix, "RC-30 slot presentation"))()
