-- RRECollector v0.2.0: player, target, role and stats snapshot.
local shared = RRECollectorRuntime.core
local call, finite, scalar = shared.call, shared.finite, shared.scalar
local fieldCopy, mapCopy = shared.fieldCopy, shared.mapCopy
local MAX_STATS = 256
local UNIT_FIELDS = {
  "id", "name", "calling", "level", "role", "health", "healthMax",
  "power", "powerMax", "mana", "manaMax", "energy", "energyMax",
  "charge", "spirit", "combo", "combat", "coordX", "coordY", "coordZ"
}

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

RRECollectorRuntime.context = { snapshot = snapshotContext }
