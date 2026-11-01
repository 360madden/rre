-- RRECollector 0.1.0: manual, character-scoped RIFT API observations.
-- No polling, game actions, process access, or dependencies on other addons.
local ADDON = "RRECollector"
local VERSION = "0.1.0"
local SCHEMA = 1
local MAX_LIST_ENTRIES = 1024
local MAX_ABILITIES = 512
local MAX_STATS = 256
local FIELDS = {
  "id", "idNew", "name", "description", "target", "castingTime",
  "channeled", "cooldown", "currentCooldownBegin",
  "currentCooldownDuration", "currentCooldownRemaining",
  "currentCooldownExpired", "currentCooldownPaused", "unusable",
  "outOfRange", "rangeMin", "rangeMax", "costPower", "costMana",
  "costEnergy", "costCharge", "costSpirit", "costPlanarCharge",
  "positioned", "passive", "continuous", "autoattack", "weapon",
  "stealthRequired", "gainCharge", "racial", "icon", "focusMin", "focusMax"
}
local UNIT_FIELDS = {
  "id", "name", "calling", "level", "role", "health", "healthMax",
  "power", "powerMax", "mana", "manaMax", "energy", "energyMax",
  "charge", "spirit", "combo", "combat", "coordX", "coordY", "coordZ"
}
local savedLoaded = false
local lastMessage = "waiting-for-saved-variables"

local function say(line)
  line = "[RRECollector] " .. tostring(line or "")
  local console = type(Command) == "table" and Command.Console or nil
  if type(console) == "table" and type(console.Display) == "function" then
    local ok, result = pcall(console.Display, "general", true, line, false)
    if ok and result ~= false then return end
  end
  if type(print) == "function" then pcall(print, line) end
end

local function finite(value)
  return type(value) == "number" and value == value
    and value ~= math.huge and value ~= -math.huge
end

local function scalar(value, stringLimit)
  if type(value) == "boolean" then return value end
  if finite(value) then return value end
  if type(value) == "string" then
    local limit = stringLimit or 2048
    if #value <= limit then return value end
    return value:sub(1, limit)
  end
  return nil
end

local function call(fn, ...)
  if type(fn) ~= "function" then return false, nil end
  local ok, result = pcall(fn, ...)
  if not ok then return false, nil end
  return true, result
end

local function fieldCopy(source, names)
  local result = {}
  if type(source) ~= "table" then return result end
  for _, key in ipairs(names) do
    local ok, value = pcall(function() return source[key] end)
    if ok then
      local accepted = scalar(value)
      if accepted ~= nil then result[key] = accepted end
    end
  end
  return result
end

local function mapCopy(source, maximum)
  local result, count, dropped = {}, 0, 0
  if type(source) ~= "table" then return result, 0, 0 end
  for key, value in pairs(source) do
    if type(key) == "string" or type(key) == "number" then
      local accepted = scalar(value, 256)
      if accepted ~= nil then
        count = count + 1
        if count <= maximum then result[tostring(key)] = accepted
        else dropped = dropped + 1 end
      end
    end
  end
  return result, count, dropped
end

local function snapshotContext()
  local api = type(Inspect) == "table" and Inspect or {}
  local unitApi = type(api.Unit) == "table" and api.Unit or {}
  local timeApi = type(api.Time) == "table" and api.Time or {}
  local roleApi = type(api.Role) == "table" and api.Role or {}
  local tempApi = type(api.TEMPORARY) == "table" and api.TEMPORARY or {}
  local sysApi = type(api.System) == "table" and api.System or {}

  local result = {capabilities = {}, player = {}, target = {},
    roleNames = {}, stats = {}}
  local ok, clock = call(timeApi.Frame)
  result.capabilities.frameTime = ok and finite(clock)
  if result.capabilities.frameTime then result.frameTime = clock end
  local rok, realTime = call(timeApi.Real)
  result.capabilities.realTime = rok and finite(realTime)
  if result.capabilities.realTime then result.realTime = realTime end
  local vok, version = call(sysApi.Version)
  result.capabilities.clientVersion = vok
  if vok then
    if type(version) == "table" then
      result.clientVersion = mapCopy(version, 32)
    else
      result.clientVersion = scalar(version, 256)
    end
  end

  local pok, player = call(unitApi.Detail, "player")
  result.capabilities.player = pok and type(player) == "table"
  if result.capabilities.player then
    result.player = fieldCopy(player, UNIT_FIELDS)
  end
  local lookupOk, playerId = call(unitApi.Lookup, "player")
  if lookupOk and result.player.id == nil then
    result.player.id = scalar(playerId, 128)
  end
  local targetOk, targetId = call(unitApi.Lookup, "player.target")
  if targetOk and targetId ~= nil then
    local detailOk, target = call(unitApi.Detail, targetId)
    result.capabilities.target = detailOk and type(target) == "table"
    if result.capabilities.target then
      result.target = fieldCopy(target, UNIT_FIELDS)
    end
    if result.target.id == nil then
      result.target.id = scalar(targetId, 128)
    end
  else
    result.capabilities.target = false
  end

  local roleOk, role = call(tempApi.Role)
  result.capabilities.roleSlot = roleOk and
    (type(role) == "string" or finite(role))
  if result.capabilities.roleSlot then result.roleSlot = role end
  local namesOk, names = call(roleApi.List)
  result.capabilities.roleList = namesOk and type(names) == "table"
  if result.capabilities.roleList then
    result.roleNames = mapCopy(names, 32)
  end
  local statsOk, stats = call(api.Stat)
  result.capabilities.stats = statsOk and type(stats) == "table"
  if result.capabilities.stats then
    local copied, _, truncated = mapCopy(stats, MAX_STATS)
    result.stats = copied
    result.statsTruncated = truncated
  end
  return result
end

local function abilityIds(source)
  local ids, seen = {}, {}
  local report = {rawEntries = 0, ignored = 0, duplicates = 0,
    truncated = 0, uniqueCount = 0, enumerationComplete = false}
  if type(source) ~= "table" then return ids, report end
  for key, value in pairs(source) do
    report.rawEntries = report.rawEntries + 1
    if report.rawEntries > MAX_LIST_ENTRIES then
      report.truncated = report.truncated + 1
    else
      local id = nil
      if type(key) == "string" then
        id = key
      elseif type(key) == "number" and type(value) == "string" then
        id = value
      end
      if type(id) ~= "string" or #id == 0 or #id > 128 then
        report.ignored = report.ignored + 1
      elseif seen[id] then
        report.duplicates = report.duplicates + 1
      elseif #ids >= MAX_ABILITIES then
        report.truncated = report.truncated + 1
      else
        seen[id] = true
        ids[#ids + 1] = id
      end
    end
  end
  table.sort(ids)
  report.uniqueCount = #ids
  report.enumerationComplete = report.ignored == 0 and report.truncated == 0
  return ids, report
end

local function collect()
  local context = snapshotContext()
  local api = type(Inspect) == "table" and Inspect or {}
  local abilitiesApi = type(api.Ability) == "table" and api.Ability or {}
  local newApi = type(abilitiesApi.New) == "table" and abilitiesApi.New or {}
  local listOk, rawList = call(newApi.List)
  local ids, enumeration = abilityIds(rawList)
  enumeration.apiAvailable = listOk and type(rawList) == "table"
  local batchOk, batch = false, nil
  if enumeration.apiAvailable then batchOk, batch = call(newApi.Detail, rawList) end
  enumeration.batchDetailAvailable = batchOk and type(batch) == "table"
  local records, failures, fallback = {}, {}, 0
  for _, id in ipairs(ids) do
    local detail = enumeration.batchDetailAvailable and batch[id] or nil
    if type(detail) ~= "table" then
      fallback = fallback + 1
      local detailOk, individual = call(newApi.Detail, id)
      if detailOk and type(individual) == "table" then detail = individual end
    end
    if type(detail) == "table" then
      local item = fieldCopy(detail, FIELDS)
      item.lookupId = id
      records[#records + 1] = item
    else
      failures[#failures + 1] = id
    end
  end
  enumeration.detailCount = #records
  enumeration.detailFailures = #failures
  enumeration.fallbackCalls = fallback
  local sequence = (type(RRECollectorData.sequence) == "number"
    and RRECollectorData.sequence or 0) + 1
  local result = {
    schemaVersion = SCHEMA, addonVersion = VERSION,
    source = "RIFT Inspect.Ability.New.List/Detail",
    scope = "current-api-enumerated-abilities-not-all-unlearned-spells",
    sequence = sequence, frameTime = context.frameTime,
    realTime = context.realTime, clientVersion = context.clientVersion,
    player = context.player, target = context.target,
    roleSlot = context.roleSlot, roleNames = context.roleNames,
    stats = context.stats, statsTruncated = context.statsTruncated,
    capabilities = context.capabilities, abilityList = enumeration,
    abilities = records, detailErrors = failures,
    captureComplete = enumeration.apiAvailable
      and enumeration.enumerationComplete and #failures == 0
      and context.capabilities.player
  }
  return result
end

local function status()
  if not savedLoaded then
    say("v" .. VERSION .. " saved data not loaded; capture unavailable.")
    return
  end
  local latest = RRECollectorData.latest
  if type(latest) ~= "table" then
    say("v" .. VERSION .. " ready; no snapshot. Use /rre capture.")
    return
  end
  local list = latest.abilityList or {}
  local p = latest.player or {}
  say("v" .. VERSION .. " capture #" .. tostring(latest.sequence)
    .. " " .. tostring(p.name or "[name unknown]") .. " lvl "
    .. tostring(p.level or "?") .. " " .. tostring(p.calling or "?"))
  say("Known API IDs " .. tostring(list.uniqueCount or 0)
    .. " | details " .. tostring(list.detailCount or 0)
    .. " | failed " .. tostring(list.detailFailures or 0)
    .. " | ignored " .. tostring(list.ignored or 0)
    .. " | truncated " .. tostring(list.truncated or 0)
    .. " | complete " .. tostring(latest.captureComplete == true))
  say("Role slot " .. tostring(latest.roleSlot or "?")
    .. " | combat role " .. tostring(p.role or "?")
    .. " | saved on next normal UI reload/logout.")
end

local function showPage(page)
  if not savedLoaded or type(RRECollectorData.latest) ~= "table" then
    say("No snapshot. Use /rre capture."); return
  end
  local records = RRECollectorData.latest.abilities or {}
  local totalPages = math.max(1, math.ceil(#records / 8))
  if not finite(page) or page < 1 or page > totalPages
    or page ~= math.floor(page) then
    say("Page must be 1-" .. tostring(totalPages)); return
  end
  say("Ability page " .. tostring(page) .. "/" .. tostring(totalPages))
  for i = (page - 1) * 8 + 1, math.min(page * 8, #records) do
    local entry = records[i]
    say(tostring(i) .. ". " .. tostring(entry.lookupId)
      .. " " .. tostring(entry.name or "[name unknown]"))
  end
end

local function help()
  say("v" .. VERSION .. " commands: /rre status | capture | page N | export | help")
  say("Captures known API abilities, role context, stats and target. No casting.")
end

local function onSlash(_, raw)
  local ok, failure = pcall(function()
    local value = type(raw) == "string" and raw:lower() or ""
    if #value > 80 then say("Command too long."); return end
    local action, argument = value:match("^%s*(%S*)%s*(%S*)%s*$")
    if action == nil then say("Use /rre help."); return end
    if action == "" or action == "help" then
      help()
    elseif action == "status" then
      status()
    elseif action == "capture" then
      if not savedLoaded then
        say("SavedVariables not ready; retry after initialization.")
        return
      end
      local captureOk, record = pcall(collect)
      if not captureOk or type(record) ~= "table" then
        lastMessage = "capture-error"
        say("Capture failed safely; no prior snapshot overwritten.")
        return
      end
      RRECollectorData.latest = record
      RRECollectorData.sequence = record.sequence
      lastMessage = record.captureComplete and "capture-complete" or "capture-partial"
      say("Capture " .. lastMessage .. ": " ..
        tostring(record.abilityList.uniqueCount) .. " IDs, " ..
        tostring(record.abilityList.detailCount) ..
        " details. /rre status; /reloadui to save.")
    elseif action == "page" then
      showPage(tonumber(argument))
    elseif action == "export" then
      say("Full snapshot stored in character SavedVariables: RRECollectorData.latest.")
      say("Use a normal /reloadui or logout to flush; /rre page N previews 8 names.")
    else
      say("Unknown command. Use /rre help.")
    end
  end)
  if not ok then
    lastMessage = "command-error"
    say("Command error. Use /rre status; no game action was sent.")
  end
end

local slashOk, slashResult = pcall(function()
  local event = Command.Slash.Register("rre")
  if type(event) ~= "table" then return false end
  Command.Event.Attach(event, onSlash, "RRECollector.Slash")
  return true
end)
if not slashOk or not slashResult then
  lastMessage = "slash-unavailable"
  say("Slash command registration failed.")
end

local savedEvent = type(Event) == "table" and Event.Addon
  and Event.Addon.SavedVariables and Event.Addon.SavedVariables.Load
  and Event.Addon.SavedVariables.Load.End
if savedEvent then
  local attached = pcall(Command.Event.Attach, savedEvent, function(_, identifier)
    if identifier ~= ADDON or savedLoaded then return end
    if type(RRECollectorData) ~= "table" then RRECollectorData = {} end
    RRECollectorData.schemaVersion = SCHEMA
    RRECollectorData.addonVersion = VERSION
    savedLoaded = true
    lastMessage = "ready"
    say("v" .. VERSION .. " ready. /rre capture")
  end, "RRECollector.SavedVariables")
  if not attached then
    lastMessage = "saved-event-unavailable"
    say("SavedVariables event attachment failed.")
  end
else
  lastMessage = "saved-event-missing"
  say("SavedVariables API unavailable.")
end
