-- RRECollector v0.4.11: known API-listed ability catalog only.
local shared = RRECollectorRuntime.core
local call, fieldCopy = shared.call, shared.fieldCopy
local snapshotContext = RRECollectorRuntime.context.snapshot
local SCHEMA, VERSION = RRECollectorRuntime.SCHEMA, RRECollectorRuntime.VERSION
local MAX_LIST_ENTRIES, MAX_ABILITIES = 1024, 512
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
  -- Only pass an unchanged, fully qualified raw List into the batch endpoint.
  -- Invalid, duplicate or capped inputs use the existing bounded scalar fallback.
  if enumeration.apiAvailable and enumeration.enumerationComplete
    and enumeration.duplicates == 0 then
    batchOk, batch = call(newApi.Detail, rawList)
  end
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

RRECollectorRuntime.abilities = {
  collect = collect,
  copyDetail = function(detail) return fieldCopy(detail, FIELDS) end,
}
