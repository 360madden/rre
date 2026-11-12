-- Full actual-package command fixture. Uses synthetic APIs only; no game input.
local passed, actions = 0, 0
local function check(value, label) assert(value, label); passed = passed + 1 end
local hooks, messages = {}, {}
local slash, savedEvent = {}, {}
Command = setmetatable({
  Console = {Display = function(_, _, line) messages[#messages + 1] = line end},
  Event = {Attach = function(_, fn, name) hooks[name] = fn end},
  Slash = {Register = function(name) check(name == "rre", "actual slash registered"); return slash end}
}, {__index = function() actions = actions + 1; error("gameplay command forbidden") end})
Event = {Addon = {SavedVariables = {Load = {End = savedEvent}}}}
local reads = {list = 0, detail = 0, map = 0}
local unavailable, listError = false, false
Inspect = {
  Time = {Frame = function() return 100 end, Real = function() return 1000 end},
  System = {Version = function() return "synthetic-build" end},
  Unit = {Lookup = function(specifier) if specifier == "player" then return "uSYNTHETIC" end end,
    Detail = function() if not unavailable then return {id = "uSYNTHETIC", name = "Fixture",
      calling = "mage", level = 1, role = "Fixture", coordX = 0, coordY = 1, coordZ = 2} end end},
  TEMPORARY = {Role = function() return 1 end}, Role = {List = function() return {"Fixture"} end},
  Stat = function() return {} end,
  Ability = {New = {List = function() return {} end, Detail = function() return nil end}},
  Quest = {List = function()
      reads.list = reads.list + 1; if listError then error("synthetic API error") end
      return {qSYNTHETIC = true}
    end,
    Detail = function(id)
      reads.detail = reads.detail + 1
      return {id = id, name = "Gather supplies", track = true, complete = false, failed = false,
        objective = {{description = "Collect supplies", count = 3, countDone = 1, complete = false,
          indicator = {mSYNTHETIC = true}}}}
    end},
  Map = {Detail = function(id)
    reads.map = reads.map + 1
    return {id = id, title = "Supply cache", coordX = 10, coordY = 2, coordZ = 30}
  end}
}
UI = nil
RRECollectorRuntime = nil
RRECollectorData = {latest = {kept = "ability"}, probe = {kept = "api"},
  professionProbe = {kept = "profession"}, navigationProbe = {kept = "navigation"}}
for _, file in ipairs({"core", "context", "abilities", "capabilities", "candidate_catalog",
  "candidates", "wire", "ui", "main"}) do
  dofile("addons/RRECollector/" .. file .. ".lua")
end
check(type(hooks["RRECollector.Slash"]) == "function", "actual slash handler attached")
check(type(hooks["RRECollector.SavedVariables"]) == "function", "actual saved handler attached")
hooks["RRECollector.SavedVariables"]({}, "RRECollector")
check(RRECollectorData.addonVersion == RRECollectorRuntime.VERSION, "actual loaded source version saved")
check(reads.list == 0 and reads.detail == 0 and reads.map == 0, "no startup quest polling")
local priorAbility, priorProbe = RRECollectorData.latest, RRECollectorData.probe
local priorProfession, priorNavigation = RRECollectorData.professionProbe, RRECollectorData.navigationProbe
hooks["RRECollector.Slash"]({}, "quests")
local snapshot = RRECollectorData.questSnapshot
check(type(snapshot) == "table" and snapshot.status == "recorded", "actual manual quest command records")
check(snapshot.sequence == 1 and RRECollectorData.questSnapshotSequence == 1, "actual sequence bound")
check(reads.list == 1 and reads.detail == 1 and reads.map == 1, "bounded actual API read path")
check(snapshot.quests[1].objectives[1].countDone == 1, "objective quantities preserved")
check(snapshot.quests[1].objectives[1].indicators[1].location.coordZ == 30, "exact map projection saved")
check(RRECollectorData.latest == priorAbility and RRECollectorData.probe == priorProbe
  and RRECollectorData.professionProbe == priorProfession and RRECollectorData.navigationProbe == priorNavigation,
  "other saved snapshots untouched")
listError = true; hooks["RRECollector.Slash"]({}, "quests")
check(RRECollectorData.questSnapshot == snapshot and RRECollectorData.questSnapshotSequence == 1,
  "API failure preserves journal and sequence")
check(RRECollectorData.questAttempt.status == "error", "API failure diagnostic saved")
listError, unavailable = false, true
local priorReads = reads.list; hooks["RRECollector.Slash"]({}, "quests")
check(reads.list == priorReads and RRECollectorData.questSnapshot == snapshot,
  "unbound player does not enumerate or erase journal")
check(RRECollectorData.questAttempt.status == "unavailable", "unbound player diagnostic saved")
check(actions == 0, "no gameplay command looked up or invoked")
print("QUEST_COMMAND_PASS " .. passed)
if arg and arg[1] == "--emit-saved" then
  local function literal(value)
    local kind = type(value)
    if kind == "string" then return string.format("%q", value) end
    if kind == "number" or kind == "boolean" then return tostring(value) end
    assert(kind == "table", "fixture serialization type")
    local keys, parts = {}, {}
    for key in pairs(value) do keys[#keys + 1] = key end
    table.sort(keys, function(a, b) return tostring(a) < tostring(b) end)
    for _, key in ipairs(keys) do parts[#parts + 1] = "[" .. literal(key) .. "]=" .. literal(value[key]) end
    return "{" .. table.concat(parts, ",") .. "}"
  end
  print("RRE_QUEST_SAVED RRECollectorData=" .. literal(RRECollectorData))
end
