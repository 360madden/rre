-- RRECollector v0.4.21 exact-source, nine-module offline startup/capture smoke.
-- Run from the repository root with the pinned native Windows Lua 5.1.4 runtime.
-- TOC order is independently enforced by verify-rrecollector-package.mjs.
-- ALL RIFT APIs here are synthetic; no game, installed addon, or live UI proof.
local checks, events, eventTokens, lines = 0, {}, {}, {}
local slashEvent = {}
local listCalls, detailBatchCalls, detailScalarCalls = 0, 0, 0
local abilityId = "A0000000000000001"
local function check(label, condition)
  checks = checks + 1
  assert(condition, "FAIL full startup: " .. label)
  print("PASS " .. label)
end

Command = {
  Console = {Display = function(_, _, line)
    lines[#lines + 1] = line
    return true
  end},
  Slash = {Register = function(name)
    assert(name == "rre")
    return slashEvent
  end},
  Event = {Attach = function(event, fn, name)
    assert(type(fn) == "function" and events[name] == nil)
    events[name], eventTokens[name] = fn, event
    return true
  end}
}
Event = {
  Addon = {Startup = {End = {}}, SavedVariables = {Load = {End = {}}}},
  Unit = {Availability = {Full = {}}}
}
-- Deliberately omit UI. The slash-command fallback must survive unavailable UI.
UI = nil
Inspect = {
  Time = {Frame = function() return 1 end, Real = function() return 2 end},
  System = {Version = function() return "4.4" end},
  Unit = {
    Detail = function(which)
      if which == "player" then
        return {id = "u0000000000000001", name = "Synthetic Rogue",
          calling = "rogue", level = 43}
      end
    end,
    Lookup = function(which)
      if which == "player" then return "u0000000000000001" end
    end
  },
  TEMPORARY = {Role = function() return 1 end},
  Role = {List = function() return {} end},
  Stat = function() return {} end,
  Experience = function() return {} end,
  Ability = {New = {
    List = function()
      listCalls = listCalls + 1
      return {[abilityId] = true}
    end,
    Detail = function(arg)
      if type(arg) == "table" then
        detailBatchCalls = detailBatchCalls + 1
        return {[abilityId] = {idNew = abilityId, name = "Synthetic Ability"}}
      end
      detailScalarCalls = detailScalarCalls + 1
      if arg == abilityId then
        return {idNew = abilityId, name = "Synthetic Ability"}
      end
    end
  }}
}
RRECollectorData = {sequence = 0}
local order = {
  "core.lua", "context.lua", "abilities.lua", "capabilities.lua",
  "candidate_catalog.lua", "candidates.lua", "wire.lua", "ui.lua", "main.lua"
}
for _, name in ipairs(order) do
  local path = "addons/RRECollector/" .. name
  local chunk, err = loadfile(path)
  assert(chunk, "missing/invalid real source " .. path .. ": " .. tostring(err))
  chunk()
end
check("nine exact modules load in approved order", #order == 9)
local runtime = RRECollectorRuntime
check("shared version and schema", runtime.VERSION == "0.4.21" and runtime.SCHEMA == 1)
check("real source exports registered",
  type(runtime.context.snapshot) == "function"
  and type(runtime.abilities.collect) == "function"
  and type(runtime.capabilities.probe) == "function"
  and type(runtime.candidates.lookup) == "function"
  and type(runtime.wire.publish) == "function"
  and type(runtime.ui.start) == "function"
  and type(runtime.command) == "function")
check("slash and saved handlers attached to exact events",
  type(events["RRECollector.Slash"]) == "function"
  and eventTokens["RRECollector.Slash"] == slashEvent
  and type(events["RRECollector.SavedVariables"]) == "function"
  and eventTokens["RRECollector.SavedVariables"] == Event.Addon.SavedVariables.Load.End)
check("event-driven retries attached to exact events",
  type(events["RRECollector.CandidateStartupRetry"]) == "function"
  and eventTokens["RRECollector.CandidateStartupRetry"] == Event.Addon.Startup.End
  and type(events["RRECollector.CandidatePlayerRetry"]) == "function"
  and eventTokens["RRECollector.CandidatePlayerRetry"] == Event.Unit.Availability.Full)
runtime.command("capture")
check("capture gated before saved-data load",
  RRECollectorData.latest == nil and listCalls == 0)
events["RRECollector.SavedVariables"](nil, "OtherAddon")
check("foreign saved event ignored",
  RRECollectorData.addonVersion == nil and RRECollectorData.schemaVersion == nil)
events["RRECollector.SavedVariables"](nil, "RRECollector")
check("own saved event initializes current version",
  RRECollectorData.addonVersion == "0.4.21"
  and RRECollectorData.schemaVersion == 1 and RRECollectorData.sequence == 0)
events["RRECollector.SavedVariables"](nil, "RRECollector")
check("duplicate own saved event is idempotent",
  RRECollectorData.sequence == 0 and RRECollectorData.addonVersion == "0.4.21")
check("missing UI handled without breaking slash commands",
  runtime.ui.start() == false and type(runtime.command) == "function")
runtime.command("capture")
local record = RRECollectorData.latest
check("complete real collector capture after saved load",
  type(record) == "table" and record.captureComplete == true
  and record.sequence == 1 and RRECollectorData.sequence == 1
  and record.addonVersion == "0.4.21" and #record.abilities == 1)
check("Rogue player and empty Experience table retained",
  record.player.calling == "rogue" and record.player.level == 43
  and record.capabilities.experience == true
  and type(record.experience) == "table" and next(record.experience) == nil)
check("bounded exact batch API used", listCalls == 1
  and detailBatchCalls == 1 and detailScalarCalls == 0
  and record.abilities[1].lookupId == abilityId)
local publication = RRECollectorData.memoryPublication
check("current-load wire publication completes",
  type(publication) == "table" and publication.status == "complete"
  and runtime.wire.receipt().status == "complete")
local frames = RRECollector_WireFrames
local validFrames = type(frames) == "table" and type(publication.parts) == "number"
  and publication.parts >= 1 and #frames == publication.parts
if validFrames then
  for i = 1, publication.parts do
    local frame = frames[i]
    if type(frame) ~= "string" or frame:sub(1, 6) ~= "RREC2|"
      or frame:sub(-9) ~= "|ENDRREC2" then validFrames = false; break end
  end
end
check("all announced RREC2 frames have valid delimiters", validFrames)
local beforeSlash = #lines
events["RRECollector.Slash"](nil, "status")
local afterStatus = #lines
events["RRECollector.Slash"](nil, "help")
local afterHelp = #lines
check("registered slash status and help produce distinct new text",
  afterStatus > beforeSlash and afterHelp > afterStatus
  and table.concat(lines, "\n", beforeSlash + 1, afterStatus):find("capture #1", 1, true) ~= nil
  and table.concat(lines, "\n", afterStatus + 1, afterHelp):find("commands:", 1, true) ~= nil)
print("PASS_RRECOLLECTOR_FULL_STARTUP " .. checks .. " synthetic scenarios")
