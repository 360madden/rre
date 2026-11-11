-- RRECollector capability receipts: one-shot, guarded API discovery.
-- No game actions, arbitrary API invocation, polling or full documentation export.
local MAX_INDEX_SCAN = 2048
local MAX_MATCHES = 96
local MAX_NAME = 160
local MAX_DOC = 512

local TARGET_PATHS = {
  "Inspect.Documentation",
  "Inspect.Ability.New.List", "Inspect.Ability.New.Detail",
  "Inspect.Role.List", "Inspect.TEMPORARY.Role",
  "Inspect.Setting.List", "Inspect.Setting.Detail",
  "Inspect.Soul.List", "Inspect.Soul.Detail",
  "Inspect.Action.List", "Inspect.Action.Detail",
  "Inspect.Queue.Status", "Inspect.Queue.Handler",
  "UI.Native.Soul", "UI.Native.Ability", "UI.Native.BarMain",
}
local DOCUMENTED_NAMES = {
  "Inspect.Role.List",
  "Inspect.Setting.List", "Inspect.Setting.Detail",
  "Inspect.Soul.List", "Inspect.Soul.Detail",
  "Inspect.Action.List", "Inspect.Action.Detail",
  "Inspect.Queue.Status",
}

local function resolveType(path)
  local root, suffix = path:match("^(%w+)%.(.+)$")
  local current = nil
  if root == "Inspect" then
    current = type(Inspect) == "table" and Inspect or nil
  elseif root == "UI" then
    current = type(UI) == "table" and UI or nil
  end
  if current == nil then return "nil" end
  for part in suffix:gmatch("[^.]+") do
    if type(current) ~= "table" then return "nil" end
    local ok, value = pcall(function() return current[part] end)
    if not ok then return "error" end
    current = value
    if current == nil then return "nil" end
  end
  return type(current)
end

local function interestingName(name)
  if type(name) ~= "string" or #name == 0 or #name > MAX_NAME then
    return false
  end
  local prefixes = {
    "Inspect.Role.", "Inspect.Setting.", "Inspect.Soul.",
    "Inspect.Action.", "Inspect.Ability.New.", "Inspect.Queue.",
    "UI.Native.Soul", "UI.Native.Ability", "UI.Native.Bar",
  }
  for _, prefix in ipairs(prefixes) do
    if name:sub(1, #prefix) == prefix then return true end
  end
  return false
end

local function collectProbe()
  local context = RRECollectorRuntime.context.snapshot()
  local player = context.player or {}
  local result = {
    schemaVersion = RRECollectorRuntime.SCHEMA,
    addonVersion = RRECollectorRuntime.VERSION,
    source = "Inspect.Documentation and exact guarded path types",
    scope = "api-capability-only-not-learnability-or-actionbar-contents",
    frameTime = context.frameTime, realTime = context.realTime,
    clientVersion = context.clientVersion, roleSlot = context.roleSlot,
    player = {
      id = player.id, name = player.name, level = player.level,
      calling = player.calling, role = player.role,
    },
    pathTypes = {}, documents = {},
    documentationStatus = "missing",
    index = {scanned = 0, matched = 0, retained = 0,
      ignored = 0, truncated = 0, scanLimitReached = false, names = {}},
    documentErrors = 0,
  }
  for _, path in ipairs(TARGET_PATHS) do
    result.pathTypes[path] = resolveType(path)
  end

  local doc = type(Inspect) == "table" and Inspect.Documentation or nil
  if type(doc) ~= "function" then return result end
  local ok, index = pcall(doc)
  if not ok then
    result.documentationStatus = "index-error"
  elseif type(index) ~= "table" then
    result.documentationStatus = "index-non-table"
  else
    result.documentationStatus = "index-available"
    for name in pairs(index) do
      if result.index.scanned >= MAX_INDEX_SCAN then
        result.index.scanLimitReached = true
        break
      end
      result.index.scanned = result.index.scanned + 1
      if interestingName(name) then
        result.index.matched = result.index.matched + 1
        if #result.index.names < MAX_MATCHES then
          result.index.names[#result.index.names + 1] = name
        else
          result.index.truncated = result.index.truncated + 1
        end
      else
        result.index.ignored = result.index.ignored + 1
      end
    end
    table.sort(result.index.names)
    result.index.retained = #result.index.names
  end

  for _, name in ipairs(DOCUMENTED_NAMES) do
    local docOk, description = pcall(doc, name)
    if not docOk then
      result.documents[name] = {status = "error"}
      result.documentErrors = result.documentErrors + 1
    elseif type(description) == "string" then
      local clipped = #description > MAX_DOC
      result.documents[name] = {
        status = "returned", text = RRECollectorRuntime.core.scalar(description, MAX_DOC),
        textTruncated = clipped,
      }
    else
      result.documents[name] = {status = "other", returnType = type(description)}
    end
  end
  return result
end

-- Profession discovery is intentionally separate from combat ability capture.
-- API names and path types are observations, NOT a guarantee of a usable
-- profession schema; no crafting, recipe or skill function is invoked.
local PROFESSION_STEMS = {
  "Craft", "Crafting", "Profession", "Tradeskill", "TradeSkill",
  "Recipe", "Fishing", "Survival", "Skill"
}
local PROFESSION_TERMS = {
  "craft", "profession", "tradeskill", "recipe", "fishing", "survival"
}
local function professionName(name)
  if type(name) ~= "string" or #name == 0 or #name > MAX_NAME then return false end
  if name:sub(1, 8) ~= "Inspect." and name:sub(1, 8) ~= "Command."
    and name:sub(1, 6) ~= "Event." then return false end
  local lower = name:lower()
  for _, term in ipairs(PROFESSION_TERMS) do
    if lower:find(term, 1, true) then return true end
  end
  return false
end
local function collectProfessions()
  local context = RRECollectorRuntime.context.snapshot()
  local player = type(context.player) == "table" and context.player or {}
  local report = {
    schemaVersion = RRECollectorRuntime.SCHEMA,
    addonVersion = RRECollectorRuntime.VERSION,
    source = "Inspect.Documentation and exact guarded profession namespace types",
    scope = "profession-api-discovery-only-no-gameplay-or-ability-coverage-claim",
    frameTime = context.frameTime, realTime = context.realTime,
    clientVersion = context.clientVersion, roleSlot = context.roleSlot,
    player = {id = player.id, name = player.name, calling = player.calling,
      level = player.level, role = player.role},
    pathTypes = {}, documents = {}, documentationStatus = "missing",
    index = {scanned = 0, matched = 0, retained = 0, ignored = 0,
      truncated = 0, scanLimitReached = false, names = {}}, documentErrors = 0,
  }
  for _, stem in ipairs(PROFESSION_STEMS) do
    for _, suffix in ipairs({"List", "Detail"}) do
      local path = "Inspect." .. stem .. "." .. suffix
      report.pathTypes[path] = resolveType(path)
    end
  end
  local doc = type(Inspect) == "table" and Inspect.Documentation or nil
  if type(doc) ~= "function" then return report end
  local ok, index = pcall(doc)
  if not ok then report.documentationStatus = "index-error"
  elseif type(index) ~= "table" then report.documentationStatus = "index-non-table"
  else
    report.documentationStatus = "index-available"
    for name in pairs(index) do
      if report.index.scanned >= MAX_INDEX_SCAN then
        report.index.scanLimitReached = true; break
      end
      report.index.scanned = report.index.scanned + 1
      if professionName(name) then
        report.index.matched = report.index.matched + 1
        if #report.index.names < MAX_MATCHES then
          report.index.names[#report.index.names + 1] = name
        else report.index.truncated = report.index.truncated + 1 end
      else report.index.ignored = report.index.ignored + 1 end
    end
    table.sort(report.index.names)
    report.index.retained = #report.index.names
  end
  -- Inspect.Documentation(name) only; never invoke the candidate API itself.
  -- Cap single-name descriptions and document requests to 18 exact paths.
  for _, stem in ipairs(PROFESSION_STEMS) do
    for _, suffix in ipairs({"List", "Detail"}) do
      local name = "Inspect." .. stem .. "." .. suffix
      local docOk, description = pcall(doc, name)
      if not docOk then
        report.documents[name] = {status = "error"}
        report.documentErrors = report.documentErrors + 1
      elseif type(description) == "string" then
        report.documents[name] = {status = "returned", text = RRECollectorRuntime.core.scalar(description, MAX_DOC),
          textTruncated = #description > MAX_DOC}
      else
        report.documents[name] = {status = "other", returnType = type(description)}
      end
    end
  end
  return report
end

-- Manual movement/navigation research only. Documentation is introspected, never
-- used to execute a movement, targeting, map, slash or other gameplay command.
local NAVIGATION_PREFIXES = {
  "Inspect.Unit.", "Inspect.Map.", "Inspect.Target.", "Inspect.Player.",
  "Inspect.Location.", "Inspect.World.", "Inspect.Waypoint.", "Inspect.Path.",
  "Inspect.NPC.", "Inspect.Camera.", "Inspect.Follow.",
  "Event.Unit.", "Event.Map.", "Event.Target.", "Event.NPC.", "Event.Follow.",
  "Command.Map.", "Command.Target.", "Command.Follow.",
}
local NAVIGATION_TERMS = {
  "position", "coordinate", "location", "movement", "velocity",
  "heading", "waypoint", "target", "distance", "navigate", "path",
  "npc", "follow", "camera", "facing", "orientation", "rotation",
}
local NAVIGATION_PATHS = {
  "Inspect.Documentation", "Inspect.Unit.Detail", "Inspect.Unit.Lookup",
  "Inspect.Unit.List", "Inspect.Map.Detail", "Inspect.Map.List",
  "Inspect.Unit.Castbar", "Inspect.Unit.Availability",
}
local MAX_NAVIGATION_DOCS = 18

local function navigationName(name)
  if type(name) ~= "string" or #name == 0 or #name > MAX_NAME then return false end
  if name:sub(1, 8) ~= "Inspect." and name:sub(1, 8) ~= "Command."
    and name:sub(1, 6) ~= "Event." then return false end
  for _, prefix in ipairs(NAVIGATION_PREFIXES) do
    if name:sub(1, #prefix) == prefix then return true end
  end
  local lower = name:lower()
  for _, term in ipairs(NAVIGATION_TERMS) do
    if lower:find(term, 1, true) then return true end
  end
  return false
end

-- Sort *all* matched names before the cap: pairs() iteration order is not
-- stable, so clipping during enumeration could hide useful API leads.
-- Reserve known candidate Unit/Map Detail names if present, then spatial
-- terminology, targeting/NPC, maps and generic Unit entries. All are leads.
local function navigationPriority(name)
  if name == "Inspect.Unit.Detail" or name == "Inspect.Map.Detail"
    or name == "Inspect.Unit.Lookup" then return 0 end
  local lower = name:lower()
  for _, term in ipairs(NAVIGATION_TERMS) do
    if term ~= "target" and term ~= "npc"
      and lower:find(term, 1, true) then return 1 end
  end
  if lower:find("target", 1, true) or lower:find("npc", 1, true) then return 2 end
  if name:sub(1, #"Inspect.Map.") == "Inspect.Map." then return 3 end
  if name:sub(1, #"Inspect.Unit.") == "Inspect.Unit." then return 4 end
  return 5
end
local function collectNavigation()
  local context = RRECollectorRuntime.context.snapshot()
  local report = {
    schemaVersion = RRECollectorRuntime.SCHEMA,
    addonVersion = RRECollectorRuntime.VERSION,
    source = "Inspect.Documentation index, bounded names and guarded Inspect path types",
    scope = "navigation-api-name-discovery-only-no-gameplay-or-api-execution",
    frameTime = context.frameTime, realTime = context.realTime,
    clientVersion = context.clientVersion,
    pathTypes = {}, documents = {}, documentationStatus = "missing",
    index = {scanned = 0, matched = 0, retained = 0, ignored = 0,
      truncated = 0, scanLimitReached = false, names = {}},
    documentErrors = 0,
  }
  for _, path in ipairs(NAVIGATION_PATHS) do
    report.pathTypes[path] = resolveType(path)
  end
  local doc = type(Inspect) == "table" and Inspect.Documentation or nil
  if type(doc) ~= "function" then return report end
  local ok, index = pcall(doc)
  if not ok then
    report.documentationStatus = "index-error"
    return report
  elseif type(index) ~= "table" then
    report.documentationStatus = "index-non-table"
    return report
  end
  report.documentationStatus = "index-available"
  local matched = {}
  for name in pairs(index) do
    if report.index.scanned >= MAX_INDEX_SCAN then
      report.index.scanLimitReached = true
      break
    end
    report.index.scanned = report.index.scanned + 1
    if navigationName(name) then
      matched[#matched + 1] = name
    else
      report.index.ignored = report.index.ignored + 1
    end
  end
  table.sort(matched, function(a, b)
    local left, right = navigationPriority(a), navigationPriority(b)
    if left ~= right then return left < right end
    return a < b
  end)
  report.index.matched = #matched
  report.index.retained = math.min(#matched, MAX_MATCHES)
  report.index.truncated = #matched - report.index.retained
  for i = 1, report.index.retained do
    report.index.names[i] = matched[i]
  end
  -- Only request documentation for retained exact API names, never call them.
  for i = 1, math.min(report.index.retained, MAX_NAVIGATION_DOCS) do
    local name = report.index.names[i]
    local docOk, description = pcall(doc, name)
    if not docOk then
      report.documents[name] = {status = "error"}
      report.documentErrors = report.documentErrors + 1
    elseif type(description) == "string" then
      report.documents[name] = {status = "returned",
        text = RRECollectorRuntime.core.scalar(description, MAX_DOC),
        textTruncated = #description > MAX_DOC}
    else
      report.documents[name] = {status = "other", returnType = type(description)}
    end
  end
  return report
end

RRECollectorRuntime.capabilities = {
  probe = collectProbe, professions = collectProfessions, navigation = collectNavigation,
}
