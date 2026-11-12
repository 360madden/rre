-- Run from the repository root: lua tools/agents/quest_journal/verify_quest_capture.lua
local passed = 0
local actions = 0
Command = setmetatable({}, {__index = function() actions = actions + 1; error("gameplay action forbidden") end})
local function check(condition, label)
  assert(condition, label); passed = passed + 1
end
local function capture(api, context)
  RRECollectorRuntime = nil
  dofile("addons/RRECollector/core.lua")
  RRECollectorRuntime.context = {snapshot = context or function()
    return {capabilities = {player = true}, player = {id = "player-one", coordX = 10}, frameTime = 1, realTime = 2}
  end}
  Inspect = api
  dofile("addons/RRECollector/capabilities.lua")
  return RRECollectorRuntime.quests.capture()
end
local result = capture(nil)
check(result.status == "unavailable" and result.questListStatus == "missing-api", "missing API")
check(result.complete == false and #result.quests == 0, "unavailable is not empty success")
local contextReads = 0
result = capture({Quest = {List = function() contextReads = contextReads + 1; return {} end}},
  function() return {player = {}, capabilities = {player = false}, frameTime = 1, realTime = 2} end)
check(result.status == "unavailable" and result.questListStatus == "context-unavailable"
  and not result.complete and contextReads == 0, "unbound player cannot replace journal with empty success")
result = capture({Quest = {List = function() error("private data") end}})
check(result.status == "error" and result.questListStatus == "error", "throwing List")
result = capture({Quest = {List = function() return false end}})
check(result.questListStatus == "invalid-result", "non-table List")
result = capture({Quest = {List = function() return {} end}})
check(result.status == "empty" and result.complete and #result.quests == 0, "empty journal")
local calls, reads = 0, 0
local api = {Quest = {
  List = function() return {z = true, [1] = "a", [2] = "a", [3] = {}, ignored = false} end,
  Detail = function(id)
    calls = calls + 1
    return {id = id, name = id, complete = false, failed = false,
      objective = {[1] = {description = "One", count = 3, countDone = 0, complete = false,
        indicator = {b = true, [1] = "a", [2] = "a", arbitrary = "not-an-id"}},
        [2] = {description = "Two", indicator = {[1] = 123}}}}
  end}, Map = {Detail = function(id)
    reads = reads + 1; return {id = id, coordX = 0, coordY = 0, coordZ = 5, title = tostring(id)}
  end}}
result = capture(api)
check(#result.quests == 2 and calls == 2, "bounded de-duplicated quest calls")
check(result.quests[1].id == "a" and result.quests[2].id == "z", "stable sorted IDs")
check(result.counts.duplicateQuestIds == 1 and result.counts.malformedQuestEntries == 2, "malformed and duplicate count")
check(result.quests[1].sourceId == "a" and result.quests[1].id == "a", "lookup ID preserved")
local objective = result.quests[1].objectives[1]
check(objective.complete == false and objective.countDone == 0, "false and zero preserved")
check(objective.indicators[1].id == "a" and objective.indicators[2].id == "b", "set and array indicators sorted")
check(objective.indicators[1].location.coordX == 0, "zero coordinate preserved")
check(objective.indicators[1].id == "a" and objective.indicators[1].location.sourceId == "a", "location ID provenance")
check(reads == 3 and result.counts.mapReads == 3, "unique map calls reused across quests")
check(result.quests[1].objectives[2].indicators[1].id == 123, "numeric location ID preserved")
check(result.status == "partial" and not result.complete, "malformed receipt is partial")
check(result.context.player.id == "player-one", "context copied")
result = capture({Quest = {List = function() return {q = true} end}})
check(result.quests[1].status == "missing-api" and not result.complete, "missing Detail")
result = capture({Quest = {List = function() return {q = true} end, Detail = function() error("not exposed") end}})
check(result.quests[1].status == "error" and result.counts.detailFailures == 1, "throwing Detail")
result = capture({Quest = {List = function() return {q = true} end, Detail = function() return nil end}})
check(result.quests[1].status == "no-detail", "nil Detail")
local dangerous = setmetatable({}, {__index = function() error("private proxy field") end})
result = capture({Quest = {List = function() return {q = true} end, Detail = function() return dangerous end}})
check(result.counts.fieldErrors > 0 and not result.complete, "guarded Detail proxy members")
result = capture({Quest = dangerous})
check(result.status == "unavailable" and result.counts.fieldErrors == 2, "guarded API proxy members")
result = capture({Quest = {List = function() return {} end}}, function() error("context") end)
check(result.status == "unavailable" and result.counts.contextErrors == 1, "context failure preserves prior journal")
local function oneQuest(detail, map)
  if detail.id == nil then detail.id = "q" end
  return {Quest = {List = function() return {q = true} end, Detail = function() return detail end}, Map = map}
end
result = capture(oneQuest({name = "q"}))
check(result.quests[1].objectiveStatus == "missing" and #result.quests[1].objectives == 0, "missing objectives remain unknown")
check(result.status == "partial" and result.counts.missingObjectiveTables == 1, "unknown objectives prevent complete claim")
result = capture(oneQuest({objective = {{indicator = {a = true}}}}))
check(result.quests[1].objectives[1].indicators[1].status == "missing-api", "missing Map API")
result = capture(oneQuest({objective = {{indicator = {a = true}}}}, {Detail = function() return nil end}))
check(result.quests[1].objectives[1].indicators[1].status == "no-detail", "missing map detail")
result = capture(oneQuest({objective = {{indicator = {a = true}}}}, {Detail = function() error("map") end}))
check(result.quests[1].objectives[1].indicators[1].status == "error", "throwing map detail")
result = capture(oneQuest({complete = "false", objective = {{count = 0/0, countDone = math.huge, indicator = false}}}))
check(result.quests[1].complete == nil and result.counts.malformedFields == 3, "wrong typed/nonfinite fields rejected")
check(result.quests[1].objectives[1].indicatorStatus == "invalid", "invalid indicators explicit")
local many, detailCalls = {}, 0
for i = 1, 300 do many[i] = "q" .. tostring(i) end
result = capture({Quest = {List = function() return many end, Detail = function()
  detailCalls = detailCalls + 1; return {}
end}})
check(result.counts.questEntriesScanned == 256 and result.counts.questScanTruncated == 1, "quest scan bound")
check(#result.quests == 128 and detailCalls == 128 and result.counts.droppedQuests == 128, "quest retain bound")
many[257], many[258], many[259], many[260] = nil, nil, nil, nil
for i = 261, 300 do many[i] = nil end
result = capture({Quest = {List = function() return many end, Detail = function() return {} end}})
check(result.counts.questScanTruncated == 1 and not result.complete, "exact scan bound is conservatively partial")
local objectives, indicators = {}, {}
for i = 1, 40 do indicators[i] = "m" .. i end
for i = 1, 70 do objectives[i] = {indicator = indicators} end
result = capture(oneQuest({objective = objectives}, {Detail = function() return {} end}))
check(result.counts.objectiveEntriesScanned == 64 and result.counts.objectiveScanTruncated == 1, "objective scan bound")
check(#result.quests[1].objectives == 32 and result.counts.droppedObjectives == 32, "objective retain bound")
check(result.counts.indicatorEntriesScanned == 32 * 32 and result.counts.indicatorScanTruncated == 32, "indicator scan bound")
check(#result.quests[1].objectives[1].indicators == 16 and result.counts.droppedIndicators == 16 * 32, "indicator retain bound")
objectives = {}
for i = 1, 16 do
  indicators = {}
  for j = 1, 16 do indicators[j] = "m" .. i .. "-" .. j end
  objectives[i] = {indicator = indicators}
end
result = capture(oneQuest({objective = objectives}, {Detail = function() return {coordX = 1} end}))
check(result.counts.mapReads == 128 and result.counts.mapLimitReached == 128, "unique map call bound")
check(not result.complete, "map cap prevents complete claim")
result = capture(oneQuest({name = string.rep("x", 2050)}))
check(#result.quests[1].name == 2048 and result.counts.truncatedFields == 1 and not result.complete, "text cap reported")
result = capture(oneQuest({objective = {{indicator = {9007199254740990, 9007199254740991}}}}, {Detail = function(id)
  return {id = id, coordX = id}
end}))
check(result.counts.mapReads == 2 and result.quests[1].objectives[1].indicators[1].id ~= result.quests[1].objectives[1].indicators[2].id,
  "safe integer IDs do not collide in map cache")
result = capture({Quest = {List = function() return {q = true} end, Detail = function() return {} end}})
check(result.quests[1].status == "missing-identity" and not result.complete, "empty Detail is incomplete")
result = capture(oneQuest({id = "different", objective = {{indicator = {m = true}}}}, {Detail = function() error("must not resolve wrong quest") end}))
check(result.quests[1].id == "q" and result.quests[1].sourceId == "different" and result.quests[1].status == "id-mismatch",
  "quest mismatch preserves original identity")
check(result.counts.mapReads == 0 and result.quests[1].objectives[1].indicators[1].status == "quest-identity-unqualified",
  "quest mismatch suppresses destinations")
result = capture(oneQuest({objective = {{indicator = {m = true}}}}, {Detail = function() return {id = "other", coordX = 1, coordY = 2, coordZ = 3} end}))
local mismatch = result.quests[1].objectives[1].indicators[1]
check(mismatch.status == "id-mismatch" and mismatch.location.sourceId == "other" and mismatch.location.coordX == nil,
  "map mismatch suppresses coordinates")
result = capture(oneQuest({objective = {{indicator = {m = true}}}}, {Detail = function() return {coordX = 1, coordY = 2, coordZ = 3} end}))
check(result.quests[1].objectives[1].indicators[1].status == "missing-identity"
  and result.quests[1].objectives[1].indicators[1].location.coordX == nil, "missing map identity is unqualified")
result = capture(oneQuest({objective = {{indicator = {m = true}}}}, {Detail = function() return {id = "m"} end}))
check(result.quests[1].objectives[1].indicators[1].status == "position-unavailable" and not result.complete, "missing map position explicit")
result = capture(oneQuest({objective = {{count = -1, countDone = 1.5}}}))
check(result.counts.malformedFields == 2 and result.quests[1].objectives[1].count == nil
  and result.quests[1].objectives[1].countDone == nil, "invalid quantities are not clamped or accepted")
many, objectives = {}, {}
for i = 1, 128 do many[i] = "q" .. i end
for i = 1, 32 do objectives[i] = {indicator = {m = true}} end
result = capture({Quest = {List = function() return many end, Detail = function(id)
  return {id = id, objective = objectives}
end}, Map = {Detail = function(id) return {id = id, coordX = 1, coordY = 2, coordZ = 3} end}})
check(result.counts.objectivesRetained == 512 and result.counts.objectiveBudgetExceeded > 0, "global objective bound")
check(result.counts.indicatorsRetained == 512 and not result.complete, "global indicator reference bound")
objectives = {}
for i = 1, 32 do
  indicators = {}; for j = 1, 16 do indicators[j] = "m" .. j end
  objectives[i] = {description = string.rep("x", 2048), indicator = indicators}
end
result = capture(oneQuest({objective = objectives}, {Detail = function(id)
  return {id = id, coordX = 1, coordY = 2, coordZ = 3, title = string.rep("t", 2048), description = string.rep("d", 2048)}
end}))
check(result.counts.textBytesRetained <= 131072 and result.counts.textBudgetExceeded > 0 and not result.complete,
  "global text budget charged per emitted cached location")
local textBytes = 0
for _, quest in ipairs(result.quests) do
  for _, obj in ipairs(quest.objectives) do
    textBytes = textBytes + #(obj.description or "")
    for _, indicator in ipairs(obj.indicators) do
      local loc = indicator.location or {}
      textBytes = textBytes + #(loc.title or "") + #(loc.description or "")
    end
  end
end
check(textBytes == result.counts.textBytesRetained, "text counter matches serialized repeated placements")
check(result.quests[1].objectives[1].indicators[1] ~= result.quests[1].objectives[2].indicators[1], "map cache emits distinct projections")
objectives = {}; for i = 1, 32 do objectives[i] = {indicator = {"a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n", "o", "p"}} end
result = capture({Quest = {List = function() return {q1 = true, q2 = true} end, Detail = function(id)
  return {id = id, objective = objectives}
end}, Map = {Detail = function(id) return {id = id, coordX = 1, coordY = 2, coordZ = 3} end}})
check(result.counts.indicatorsRetained == 512 and result.counts.indicatorBudgetExceeded == 512, "global references refuse second quest expansion")
check(actions == 0, "no gameplay command lookup or invocation")
print("quest capture: " .. passed .. "/" .. passed .. " assertions passed")
