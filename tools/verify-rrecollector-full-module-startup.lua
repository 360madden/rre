-- RRECollector v0.4.21 exact-source, nine-module offline startup/capture/profession smoke.
-- Run from the repository root with the pinned native Windows Lua 5.1.4 runtime.
-- TOC order is independently enforced by verify-rrecollector-package.mjs.
-- ALL RIFT APIs here are synthetic; no game, installed addon, or live UI proof.
local checks, events, eventTokens, lines = 0, {}, {}, {}
local slashEvent = {}
local listCalls, detailBatchCalls, detailScalarCalls = 0, 0, 0
local abilityId = "A0000000000000001"
-- All documentation responses below are synthetic; only the real producer runs.
local professionMode, professionIndexCalls, professionCalls = "normal", 0, {}
local professionIndex = {
  ["Inspect.Craft.List"] = true, ["Inspect.Fishing.Detail"] = true,
  ["Event.Profession.Updated"] = true, ["Inspect.Ability.New.List"] = true,
  ["Other.Craft.List"] = true,
}
local oversizedProfessionIndex
local questMode, questListCalls, questDetailCalls = "normal", 0, 0
local questId = "q-synthetic-1"
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
  -- Candidate functions deliberately throw if called: only type inspection is safe.
  Craft = {List = function() error("crafting API must not be called") end},
  Fishing = {Detail = function() error("fishing API must not be called") end},
  Documentation = function(name)
    if name == nil then
      professionIndexCalls = professionIndexCalls + 1
      if professionMode == "index-error" then error("synthetic documentation index failure") end
      if professionMode == "oversize" then
        if not oversizedProfessionIndex then
          oversizedProfessionIndex = {}
          for i = 1, 2050 do oversizedProfessionIndex["Inspect.Craft.Mock" .. i] = true end
        end
        return oversizedProfessionIndex
      end
      return professionIndex
    end
    professionCalls[#professionCalls + 1] = name
    if name == "Inspect.Craft.List" then return string.rep("D", 700) end
    if name == "Inspect.Fishing.Detail" then error("synthetic description failure") end
    return nil
  end,
  Quest = {
    List = function()
      questListCalls = questListCalls + 1
      if questMode == "throw" then error("synthetic Quest.List failure") end
      if questMode == "empty" then return {} end
      return {[questId] = true}
    end,
    Detail = function(id)
      questDetailCalls = questDetailCalls + 1
      assert(id == questId, "unexpected quest ID")
      return {id = id, name = "Synthetic Quest", complete = false,
        objective = {{description = "Gather one", count = 1, countDone = 0,
          complete = false, indicator = {}}}}
    end,
  },
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
runtime.command("professions")
check("professions gated before saved-data load",
  RRECollectorData.professionProbe == nil
  and RRECollectorData.professionProbeSequence == nil
  and professionIndexCalls == 0 and #professionCalls == 0)
runtime.command("quests")
check("quests gated before saved-data load without API calls",
  RRECollectorData.questSnapshot == nil
  and RRECollectorData.questAttempt == nil
  and questListCalls == 0 and questDetailCalls == 0)
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

-- Exercise the real profession collector and slash path without game API effects.
local priorLatest, priorPublication, priorSequence =
  RRECollectorData.latest, RRECollectorData.memoryPublication, RRECollectorData.sequence
-- A nonnil preexisting receipt is essential: checking nil would be false-ready.
local priorGeneralProbe = {sentinel = "preserved-general-probe"}
local priorCandidateLookup = {sentinel = "preserved-candidate-lookup"}
RRECollectorData.probe = priorGeneralProbe
RRECollectorData.candidateLookup = priorCandidateLookup
events["RRECollector.Slash"](nil, "professions")
local profession = RRECollectorData.professionProbe
check("real profession slash publishes separately sequenced report",
  type(profession) == "table" and profession.sequence == 1
  and RRECollectorData.professionProbeSequence == 1
  and profession.addonVersion == "0.4.21" and profession.player.calling == "rogue")
check("profession index filters and sorts only supported API names",
  profession.documentationStatus == "index-available"
  and profession.index.scanned == 5 and profession.index.matched == 3
  and profession.index.retained == 3 and profession.index.ignored == 2
  and profession.index.names[1] == "Event.Profession.Updated"
  and profession.index.names[2] == "Inspect.Craft.List"
  and profession.index.names[3] == "Inspect.Fishing.Detail")
local professionPathCount = 0
for _ in pairs(profession.pathTypes) do professionPathCount = professionPathCount + 1 end
local allowedProfessionPaths = {}
for _, stem in ipairs({
  "Craft", "Crafting", "Profession", "Tradeskill", "TradeSkill",
  "Recipe", "Fishing", "Survival", "Skill",
}) do
  for _, suffix in ipairs({"List", "Detail"}) do
    allowedProfessionPaths["Inspect." .. stem .. "." .. suffix] = true
  end
end
local exactDocumentationCalls, seenDocumentationNames = true, {}
for _, name in ipairs(professionCalls) do
  if not allowedProfessionPaths[name] or seenDocumentationNames[name] then
    exactDocumentationCalls = false
  end
  seenDocumentationNames[name] = true
end
for name in pairs(allowedProfessionPaths) do
  if not seenDocumentationNames[name] or profession.pathTypes[name] == nil then
    exactDocumentationCalls = false
  end
end
check("profession inspects 18 exact path types without invoking them",
  professionPathCount == 18
  and profession.pathTypes["Inspect.Craft.List"] == "function"
  and profession.pathTypes["Inspect.Fishing.Detail"] == "function"
  and profession.pathTypes["Inspect.Profession.List"] == "nil")
check("profession documentation uses only the 18 exact allowlisted paths",
  exactDocumentationCalls and #professionCalls == 18)
check("profession documentation is bounded, clipped and fault-isolated",
  professionIndexCalls == 1 and #professionCalls == 18
  and profession.documents["Inspect.Craft.List"].status == "returned"
  and #profession.documents["Inspect.Craft.List"].text == 512
  and profession.documents["Inspect.Craft.List"].textTruncated == true
  and profession.documents["Inspect.Fishing.Detail"].status == "error"
  and profession.documentErrors == 1)
check("profession discovery leaves ability and general probe unchanged",
  RRECollectorData.latest == priorLatest
  and RRECollectorData.memoryPublication == priorPublication
  and RRECollectorData.sequence == priorSequence
  and RRECollectorData.probe == priorGeneralProbe
  and RRECollectorData.candidateLookup == priorCandidateLookup)

professionMode = "index-error"
events["RRECollector.Slash"](nil, "professions")
check("documentation index exception yields explicit bounded report",
  RRECollectorData.professionProbeSequence == 2
  and RRECollectorData.professionProbe.documentationStatus == "index-error"
  and RRECollectorData.professionProbe.index.scanned == 0)
local savedProfession = RRECollectorData.professionProbe
local collectProfessions = runtime.capabilities.professions
runtime.capabilities.professions = function() error("synthetic producer exception") end
events["RRECollector.Slash"](nil, "professions")
runtime.capabilities.professions = collectProfessions
check("profession producer exception preserves previous receipt",
  RRECollectorData.professionProbe == savedProfession
  and RRECollectorData.professionProbeSequence == 2
  and RRECollectorData.latest == priorLatest
  and RRECollectorData.probe == priorGeneralProbe
  and RRECollectorData.candidateLookup == priorCandidateLookup)

professionMode = "oversize"
events["RRECollector.Slash"](nil, "professions")
local capped = RRECollectorData.professionProbe
check("oversized profession index obeys both scan and match caps",
  RRECollectorData.professionProbeSequence == 3
  and capped.index.scanned == 2048 and capped.index.scanLimitReached == true
  and capped.index.matched == 2048 and capped.index.retained == 96
  and capped.index.truncated == 1952)

local originalDocumentation = Inspect.Documentation
Inspect.Documentation = nil
events["RRECollector.Slash"](nil, "professions")
Inspect.Documentation = originalDocumentation
check("missing documentation produces explicit no-API report",
  RRECollectorData.professionProbeSequence == 4
  and RRECollectorData.professionProbe.documentationStatus == "missing"
  and RRECollectorData.professionProbe.index.scanned == 0
  and RRECollectorData.latest == priorLatest
  and RRECollectorData.probe == priorGeneralProbe
  and RRECollectorData.candidateLookup == priorCandidateLookup)

-- Exercise the real quest producer through the registered slash and saved state.
local priorProfession, priorAbility = RRECollectorData.professionProbe, RRECollectorData.latest
local beforeQuestLines = #lines
events["RRECollector.Slash"](nil, "quests")
local journal = RRECollectorData.questSnapshot
check("real quest slash publishes a recorded journal and diagnostic",
  type(journal) == "table" and journal.status == "recorded"
  and journal.complete == true and journal.sequence == 1
  and RRECollectorData.questSnapshotSequence == 1
  and #journal.quests == 1 and journal.quests[1].id == questId
  and #journal.quests[1].objectives == 1
  and journal.quests[1].objectives[1].countDone == 0
  and RRECollectorData.questAttempt.status == "recorded"
  and questListCalls == 1 and questDetailCalls == 1)
check("quest slash emits new journal-specific output",
  #lines > beforeQuestLines
  and table.concat(lines, "\n", beforeQuestLines + 1):find("Quest journal #1 recorded", 1, true) ~= nil)
check("quest capture preserves ability and other research receipts",
  RRECollectorData.latest == priorAbility
  and RRECollectorData.sequence == priorSequence
  and RRECollectorData.memoryPublication == priorPublication
  and RRECollectorData.professionProbe == priorProfession
  and RRECollectorData.probe == priorGeneralProbe
  and RRECollectorData.candidateLookup == priorCandidateLookup)

questMode = "throw"
events["RRECollector.Slash"](nil, "quests")
check("throwing quest List preserves prior journal and records attempt",
  questListCalls == 2 and questDetailCalls == 1
  and RRECollectorData.questSnapshot == journal
  and RRECollectorData.questSnapshotSequence == 1
  and RRECollectorData.questAttempt.status == "error")
local originalQuestApi = Inspect.Quest
Inspect.Quest = nil
events["RRECollector.Slash"](nil, "quests")
Inspect.Quest = originalQuestApi
check("missing quest API preserves prior journal with unavailable receipt",
  RRECollectorData.questSnapshot == journal
  and RRECollectorData.questSnapshotSequence == 1
  and RRECollectorData.questAttempt.status == "unavailable"
  and questListCalls == 2)
local previousQuestAttempt = RRECollectorData.questAttempt
local originalQuestCapture = runtime.quests.capture
runtime.quests.capture = function() error("synthetic quest producer failure") end
events["RRECollector.Slash"](nil, "quests")
runtime.quests.capture = originalQuestCapture
check("quest producer exception preserves journal and prior attempt",
  RRECollectorData.questSnapshot == journal
  and RRECollectorData.questSnapshotSequence == 1
  and RRECollectorData.questAttempt == previousQuestAttempt
  and RRECollectorData.questAttempt.status == "unavailable"
  and RRECollectorData.latest == priorAbility)

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
