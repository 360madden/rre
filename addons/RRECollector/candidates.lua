-- RRECollector v0.3.0: bounded, explicit-ID candidate lookup, no game actions.
-- This is a read-only question to Inspect.Ability.New.Detail, not a spell-unlock scan.
local shared = RRECollectorRuntime.core
local contextSnapshot = RRECollectorRuntime.context.snapshot
local abilityCopyDetail = RRECollectorRuntime.abilities.copyDetail
local catalog = RRECollectorRuntime.candidateCatalog
local MAX_CATALOG, MAX_LIST_ENTRIES, MAX_UNLISTED_CANARIES = 128, 1024, 8
local SCREENSHOT_CANARIES = {
  AFDD9D7E2A8F0E50B = true, -- Light's Benediction
  A768CF3B63EE8D6ED = true, -- Vengeful Decree
  AFA78C0D582C9F2E5 = true, -- Aegis of the Light
  A37397DC597DDAF03 = true, -- Sanctuary
  A0E2112FD6FE262EE = true, -- Protector's Fury
  A411792DB5CF7E0E4 = true, -- Call of the Divine
}

local function listedIds(rawList)
  local seen, rawCount, truncated, unique = {}, 0, 0, 0
  for key, value in pairs(rawList) do
    rawCount = rawCount + 1
    if rawCount > MAX_LIST_ENTRIES then
      truncated = truncated + 1
    else
      local id = nil
      if type(key) == "string" then id = key
      elseif type(key) == "number" and type(value) == "string" then id = value end
      if type(id) == "string" and #id > 0 and #id <= 128 and not seen[id] then
        seen[id] = true
        unique = unique + 1
      end
    end
  end
  return seen, rawCount, truncated, unique
end

local function lookup()
  if type(catalog) ~= "table" or type(catalog.entries) ~= "table"
    or #catalog.entries == 0 or #catalog.entries > MAX_CATALOG then
    return nil, "invalid-or-oversize-static-catalog"
  end
  local context = contextSnapshot()
  local player = context.player or {}
  if type(player.calling) ~= "string"
    or not player.calling:lower():find("warrior", 1, true) then
    return nil, "warrior-player-context-not-ready"
  end
  local api = type(Inspect) == "table" and Inspect or {}
  local ability = type(api.Ability) == "table" and api.Ability or {}
  local newApi = type(ability.New) == "table" and ability.New or {}
  if type(newApi.List) ~= "function" or type(newApi.Detail) ~= "function" then
    return nil, "ability-new-list-or-detail-unavailable"
  end
  local listOk, rawList = pcall(newApi.List)
  if not listOk or type(rawList) ~= "table" then
    return nil, "current-ability-list-not-ready"
  end
  local known, listRawCount, listTruncated, listUniqueCount = listedIds(rawList)
  if listTruncated > 0 then return nil, "current-ability-list-truncated" end
  local report = {
    schemaVersion = RRECollectorRuntime.SCHEMA,
    addonVersion = RRECollectorRuntime.VERSION,
    catalogVersion = catalog.version,
    source = catalog.source,
    scope = "static-Warrior-candidates-explicit-ID-API-query-not-unlock-proof",
    player = player, roleSlot = context.roleSlot, roleNames = context.roleNames,
    clientVersion = context.clientVersion,
    frameTime = context.frameTime, realTime = context.realTime,
    apiReady = true, listRawCount = listRawCount, listUniqueCount = listUniqueCount,
    entries = {}, canaryIds = {}, counts = {
      catalog = #catalog.entries, listed = 0, unlisted = 0, queried = 0,
      listedControlQueried = 0, listedControlReturned = 0,
      unlistedQueried = 0, returned = 0,
      unlistedReturned = 0, noDetail = 0, errors = 0,
      inconclusiveTables = 0, skipped = 0
    },
  }
  local counts, entries, byId = report.counts, report.entries, {}
  for _, source in ipairs(catalog.entries) do
    if type(source.id) ~= "string" or byId[source.id] then
      return nil, "invalid-or-duplicate-static-ID"
    end
    local listed = known[source.id] == true
    local item = {
      id = source.id, name = source.name, soul = source.soul,
      category = source.category, listed = listed,
      status = listed and "listed-not-queried" or "not-queried",
    }
    entries[#entries + 1] = item
    byId[source.id] = item
    if listed then counts.listed = counts.listed + 1
    else counts.unlisted = counts.unlisted + 1 end
  end

  local function query(item, phase)
    local ok, detail = pcall(newApi.Detail, item.id)
    counts.queried = counts.queried + 1
    if item.listed then counts.listedControlQueried = counts.listedControlQueried + 1
    else counts.unlistedQueried = counts.unlistedQueried + 1 end
    item.phase = phase
    if not ok then
      item.status = "lookup-error"
      counts.errors = counts.errors + 1
      return false
    end
    if type(detail) ~= "table" then
      item.status = "no-detail"
      counts.noDetail = counts.noDetail + 1
      return false
    end
    local fields = abilityCopyDetail(detail)
    item.detail = fields
    if type(fields.name) == "string" and #fields.name > 0
      or type(fields.idNew) == "string" and #fields.idNew > 0
      or type(fields.description) == "string" and #fields.description > 0 then
      item.status = "returned"
      counts.returned = counts.returned + 1
      if item.listed then counts.listedControlReturned = counts.listedControlReturned + 1 end
      if not item.listed then
        counts.unlistedReturned = counts.unlistedReturned + 1
      end
      return true
    end
    item.status = "inconclusive-table"
    counts.inconclusiveTables = counts.inconclusiveTables + 1
    return false
  end

  -- A known-list control distinguishes a broken Detail endpoint from a negative canary.
  for _, item in ipairs(entries) do
    if item.listed then query(item, "listed-control"); break end
  end
  local canaries, selected = {}, {}
  local function addCanary(item)
    if item and not item.listed and not selected[item.id]
      and #canaries < MAX_UNLISTED_CANARIES then
      selected[item.id] = true
      canaries[#canaries + 1] = item
    end
  end
  for _, item in ipairs(entries) do
    if SCREENSHOT_CANARIES[item.id] then addCanary(item) end
  end
  for _, soul in ipairs({ "VoidKnight", "Paragon" }) do
    for _, item in ipairs(entries) do
      if item.soul == soul and not item.listed then
        addCanary(item); break
      end
    end
  end
  for _, item in ipairs(canaries) do
    report.canaryIds[#report.canaryIds + 1] = item.id
    query(item, "unlisted-canary")
  end
  if counts.unlistedReturned > 0 then
    report.policy = "positive-canary-expanded-to-other-unlisted-IDs"
    for _, item in ipairs(entries) do
      if not item.listed and item.status == "not-queried" then
        query(item, "unlisted-expansion")
      end
    end
  elseif counts.unlisted == 0 then
    report.policy = "no-unlisted-candidates"
  else
    report.policy = "no-positive-canary-stop"
  end
  for _, item in ipairs(entries) do
    if item.status == "not-queried" then
      item.status = "not-attempted-canary-stop"
      counts.skipped = counts.skipped + 1
    end
  end
  report.unlistedLookupComplete = counts.unlistedQueried == counts.unlisted
  report.note = "nil/error means no result from this API call, not proof an ability is locked, absent, or unlearnable"
  return report
end

RRECollectorRuntime.candidates = { lookup = lookup }
