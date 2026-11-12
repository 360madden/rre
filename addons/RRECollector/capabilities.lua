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


-- RC-79: bounded manual quest journal, separate from capability probes.
do
-- RC-79 candidate: one manual, read-only quest-journal snapshot. Lua 5.1 compatible.
-- List/Detail documentation is a lead; this module does not establish live acceptance.
RRECollectorRuntime = RRECollectorRuntime or {}
local runtime = RRECollectorRuntime
local core = runtime.core or {}
local LIMITS = {questScan = 256, quests = 128, objectiveScan = 64, objectives = 32,
  indicatorScan = 32, indicators = 16, mapReads = 128, textBytes = 2048,
  totalObjectives = 512, totalIndicators = 512, textBudgetBytes = 131072,
  shapeSamples = 8, shapeFields = 16, shapeStringBytes = 256,
  shapeEncodedBytes = 8192, shapeMapReads = 16}
local function finite(value)
  return type(value) == "number" and value == value
    and value ~= math.huge and value ~= -math.huge
end
local function field(value, key)
  if type(value) ~= "table" then return nil, false end
  local ok, result = pcall(function() return value[key] end)
  return result, ok
end
local function identifier(value)
  if type(value) == "string" then
    return #value > 0 and #value <= 256 and not value:find("[%z\1-\31\127]")
  end
  return finite(value) and value >= 0 and value <= 9007199254740991
    and value == math.floor(value)
end
local function idLess(a, b)
  if type(a) == type(b) then return a < b end
  return type(a) == "number"
end
local function idKey(id)
  return type(id) .. ":" .. (type(id) == "number" and string.format("%.0f", id) or id)
end
local function copyLimits()
  local result = {}; for key, value in pairs(LIMITS) do result[key] = value end
  return result
end
local function capture()
  local report = {schemaVersion = 1, addonVersion = runtime.VERSION,
    scope = "quest-journal-snapshot", status = "unavailable", complete = false,
    context = {}, api = {}, limits = copyLimits(), quests = {},
    counts = {questEntriesScanned = 0, questsRetained = 0, duplicateQuestIds = 0,
      malformedQuestEntries = 0, droppedQuests = 0, questScanTruncated = 0,
      objectiveEntriesScanned = 0, objectivesRetained = 0, malformedObjectives = 0,
      droppedObjectives = 0, objectiveScanTruncated = 0, objectiveBudgetExceeded = 0,
      missingObjectiveTables = 0,
      indicatorEntriesScanned = 0, indicatorsRetained = 0, duplicateIndicators = 0,
      malformedIndicators = 0, droppedIndicators = 0, indicatorScanTruncated = 0,
      indicatorBudgetExceeded = 0, textBytesRetained = 0, textBudgetExceeded = 0,
      mapReads = 0, mapLimitReached = 0, detailFailures = 0, mapFailures = 0,
      fieldErrors = 0, malformedFields = 0, truncatedFields = 0, contextErrors = 0}}
  local partial = false
  local shapes = {schemaVersion = 1, scope = "unsupported-indicator-diagnostics",
    coverage = "bounded-sample", samples = {}, histogram = {},
    counts = {seen = 0, sampled = 0, dropped = 0, fieldsScanned = 0,
      stringsTruncated = 0, encodedBytesRetained = 0, fieldReadErrors = 0, mapReads = 0}}
  report.indicatorShapes = shapes
  local diagnosticMapFn, diagnosticMapCache = nil, {}
  local function issue(name)
    report.counts[name] = report.counts[name] + 1; partial = true
  end
  local function read(source, name)
    local value, ok = field(source, name)
    if not ok and type(source) == "table" then issue("fieldErrors") end
    return value
  end
  local function copyFields(source, destination, strings, numbers, booleans, chargeText)
    if chargeText == nil then chargeText = true end
    for _, name in ipairs(strings or {}) do
      local value = read(source, name)
      if type(value) == "string" then
        if #value > LIMITS.textBytes then issue("truncatedFields") end
        local cap = LIMITS.textBytes
        if chargeText then
          cap = math.min(cap, LIMITS.textBudgetBytes - report.counts.textBytesRetained)
          if cap < math.min(#value, LIMITS.textBytes) then issue("textBudgetExceeded") end
        end
        local copied = type(core.scalar) == "function" and core.scalar(value, cap) or value:sub(1, cap)
        destination[name] = copied
        if chargeText then report.counts.textBytesRetained = report.counts.textBytesRetained + #copied end
      elseif value ~= nil then issue("malformedFields") end
    end
    for _, name in ipairs(numbers or {}) do
      local value = read(source, name)
      local quantity = name == "count" or name == "countDone"
      if finite(value) and (not quantity or (value >= 0 and value <= 9007199254740991 and value == math.floor(value))) then
        destination[name] = value
      elseif value ~= nil then issue("malformedFields") end
    end
    for _, name in ipairs(booleans or {}) do
      local value = read(source, name)
      if type(value) == "boolean" then destination[name] = value
      elseif value ~= nil then issue("malformedFields") end
    end
  end
  local function sourceId(source, destination)
    local value = read(source, "id")
    if identifier(value) then destination.sourceId = value
    elseif value ~= nil then issue("malformedFields") end
  end
  local function shapeScalar(value)
    local kind = type(value)
    local result = {type = kind}
    if kind == "boolean" then result.value = value
    elseif kind == "number" then
      result.finite = finite(value); if result.finite then result.value = value end
    elseif kind == "string" then
      local remaining = LIMITS.shapeEncodedBytes - shapes.counts.encodedBytesRetained
      local preview = value:sub(1, math.min(LIMITS.shapeStringBytes, remaining))
      local binary = preview:find("[^\32-\126]") ~= nil
      if binary then
        preview = preview:sub(1, math.floor(remaining / 2))
        result.encoding = "hex-bytes"
        result.preview = (preview:gsub(".", function(byte) return string.format("%02X", byte:byte()) end))
      else result.encoding, result.preview = "ascii", preview end
      result.sourceBytes, result.retainedBytes = #value, #preview
      result.truncated = #preview < #value
      if result.truncated then shapes.counts.stringsTruncated = shapes.counts.stringsTruncated + 1 end
      shapes.counts.encodedBytesRetained = shapes.counts.encodedBytesRetained + #result.preview
    end
    return result
  end
  local function diagnosticLookup(candidate)
    local cached = diagnosticMapCache[candidate]
    local reused = cached ~= nil
    if not cached then
      cached = {status = "missing-api", identityMatches = false}
      diagnosticMapCache[candidate] = cached
      if type(diagnosticMapFn) == "function" then
        if shapes.counts.mapReads >= LIMITS.shapeMapReads then cached.status = "limit"
        else
          shapes.counts.mapReads = shapes.counts.mapReads + 1
          local ok, detail = pcall(diagnosticMapFn, candidate)
          if not ok then cached.status = "error"
          elseif detail == nil then cached.status = "no-detail"
          elseif type(detail) ~= "table" then cached.status = "invalid-detail"
          else
            local returned, readOk = field(detail, "id")
            if not readOk then shapes.counts.fieldReadErrors = shapes.counts.fieldReadErrors + 1 end
            if identifier(returned) then cached.returnedId = returned end
            if not readOk or not identifier(returned) then cached.status = "missing-identity"
            elseif returned ~= candidate then cached.status = "id-mismatch"
            else
              cached.identityMatches, cached.status = true, "returned"
              for _, key in ipairs({"coordX", "coordY", "coordZ"}) do
                local coordinate, coordinateOk = field(detail, key)
                if coordinateOk and finite(coordinate) then cached[key] = coordinate end
                if not coordinateOk then shapes.counts.fieldReadErrors = shapes.counts.fieldReadErrors + 1 end
              end
              if cached.coordX == nil or cached.coordY == nil or cached.coordZ == nil then
                cached.status = "position-unavailable"
              end
            end
          end
        end
      end
    end
    local result = {status = cached.status, cached = reused, identityMatches = cached.identityMatches,
      coordinateFrameVerified = false, questAssociationVerified = false,
      identifier = shapeScalar(candidate)}
    if cached.returnedId ~= nil then result.returnedId = shapeScalar(cached.returnedId) end
    for _, key in ipairs({"coordX", "coordY", "coordZ"}) do result[key] = cached[key] end
    return result
  end
  local function unsupportedIndicator(item, quest, objective, entryKind)
    shapes.counts.seen = shapes.counts.seen + 1
    local signature = type(item.key) .. "/" .. type(item.value)
    shapes.histogram[signature] = (shapes.histogram[signature] or 0) + 1
    if #shapes.samples >= LIMITS.shapeSamples then
      shapes.counts.dropped = shapes.counts.dropped + 1; return
    end
    local sample = {questId = quest.id, objectiveKey = objective.key, entryKind = entryKind,
      status = "unsupported-shape", key = shapeScalar(item.key), value = shapeScalar(item.value),
      candidateLookups = {}}
    if type(item.value) == "table" then
      local key, count = nil, 0
      sample.value.fields, sample.value.fieldsTruncated = {}, false
      while count < LIMITS.shapeFields do
        local ok, nextKey, value = pcall(next, item.value, key)
        if not ok then
          shapes.counts.fieldReadErrors = shapes.counts.fieldReadErrors + 1
          sample.value.fieldReadError = true; break
        end
        if nextKey == nil then break end
        key, count = nextKey, count + 1
        shapes.counts.fieldsScanned = shapes.counts.fieldsScanned + 1
        sample.value.fields[#sample.value.fields + 1] = {key = shapeScalar(nextKey), value = shapeScalar(value)}
        if count == LIMITS.shapeFields then sample.value.fieldsTruncated = true end
      end
    end
    for _, source in ipairs({"key", "value"}) do
      local candidate = item[source]
      if type(candidate) == "string" and identifier(candidate) then
        local lookup = diagnosticLookup(candidate); lookup.candidateSource = source
        sample.candidateLookups[#sample.candidateLookups + 1] = lookup
      end
    end
    shapes.samples[#shapes.samples + 1] = sample
    shapes.counts.sampled = shapes.counts.sampled + 1
  end
  local function entries(source, maximum, scanCounter, truncatedCounter)
    local result, key, count = {}, nil, 0
    while true do
      local nextKey, value = next(source, key)
      if nextKey == nil then break end
      count = count + 1; report.counts[scanCounter] = report.counts[scanCounter] + 1
      result[#result + 1] = {key = nextKey, value = value}
      key = nextKey
      -- At the exact bound conservatively mark coverage partial without probing further.
      if count >= maximum then issue(truncatedCounter); break end
    end
    return result
  end
  local function listIds(source, maximumScan, maximumRetained, counters, onUnsupported)
    local values, seen = {}, {}
    for _, item in ipairs(entries(source, maximumScan, counters.scan, counters.truncated)) do
      local id
      -- Accept sets only when the value is true. Arbitrary string keys are not IDs.
      if type(item.key) == "string" and item.value == true then id = item.key
      elseif finite(item.key) and item.key >= 1 and item.key == math.floor(item.key) then id = item.value end
      if identifier(id) then
        local token = idKey(id)
        if seen[token] then issue(counters.duplicates)
        else seen[token] = true; values[#values + 1] = id end
      else
        issue(counters.malformed)
        if onUnsupported then onUnsupported(item) end
      end
    end
    table.sort(values, idLess)
    if #values > maximumRetained then
      report.counts[counters.dropped] = report.counts[counters.dropped] + #values - maximumRetained
      partial = true
      for i = #values, maximumRetained + 1, -1 do values[i] = nil end
    end
    return values
  end
  local inspect = type(Inspect) == "table" and Inspect or {}
  local questApi, mapApi = read(inspect, "Quest"), read(inspect, "Map")
  local listFn, detailFn, mapFn = read(questApi, "List"), read(questApi, "Detail"), read(mapApi, "Detail")
  diagnosticMapFn = mapFn
  report.api.questList, report.api.questDetail, report.api.mapDetail = type(listFn), type(detailFn), type(mapFn)
  local contextApi = runtime.context
  if type(contextApi) == "table" and type(contextApi.snapshot) == "function" then
    local ok, value = pcall(contextApi.snapshot)
    if ok and type(value) == "table" then report.context = value else issue("contextErrors") end
  else issue("contextErrors") end
  local context = report.context
  local player = type(context.player) == "table" and context.player or {}
  local capabilities = type(context.capabilities) == "table" and context.capabilities or {}
  if capabilities.player ~= true or not identifier(player.id)
    or not finite(context.frameTime) or context.frameTime < 0
    or not finite(context.realTime) or context.realTime < 0 then
    if report.counts.contextErrors == 0 then issue("contextErrors") end
    report.questListStatus = "context-unavailable"
    return report
  end
  if type(listFn) ~= "function" then report.questListStatus = "missing-api"; return report end
  local listOk, questList = pcall(listFn)
  if not listOk then report.questListStatus = "error"; report.status = "error"; return report end
  if type(questList) ~= "table" then
    report.questListStatus = "invalid-result"; report.status = "error"; return report
  end
  report.questListStatus = "returned"
  local questIds = listIds(questList, LIMITS.questScan, LIMITS.quests,
    {scan = "questEntriesScanned", truncated = "questScanTruncated", duplicates = "duplicateQuestIds",
      malformed = "malformedQuestEntries", dropped = "droppedQuests"})
  local mapCache = {}
  local function cachedLocation(id)
    local token = idKey(id)
    if mapCache[token] then return mapCache[token] end
    local result = {id = id, status = "missing-api"}
    mapCache[token] = result
    if type(mapFn) ~= "function" then issue("mapFailures"); return result end
    if report.counts.mapReads >= LIMITS.mapReads then
      result.status = "limit"; issue("mapLimitReached"); return result
    end
    report.counts.mapReads = report.counts.mapReads + 1
    local ok, value = pcall(mapFn, id)
    if not ok then result.status = "error"; issue("mapFailures")
    elseif value == nil then result.status = "no-detail"; issue("mapFailures")
    elseif type(value) ~= "table" then result.status = "invalid-detail"; issue("mapFailures")
    else
      result.status, result.location = "returned", {}
      sourceId(value, result.location)
      if result.location.sourceId == nil then result.status = "missing-identity"; issue("mapFailures")
      elseif result.location.sourceId ~= id then result.status = "id-mismatch"; issue("mapFailures") end
      copyFields(value, result.location, {"title", "description"},
        result.status == "returned" and {"coordX", "coordY", "coordZ"} or {}, nil, false)
      if result.status == "returned" and (result.location.coordX == nil or result.location.coordY == nil
        or result.location.coordZ == nil) then result.status = "position-unavailable"; issue("mapFailures") end
    end
    return result
  end
  local function location(id, quest)
    if quest.status ~= "returned" then return {id = id, status = "quest-identity-unqualified"} end
    local cached = cachedLocation(id)
    -- SavedVariables repeats shared tables. Charge text for EVERY emitted placement.
    local result = {id = cached.id, status = cached.status}
    if cached.location then
      result.location = {sourceId = cached.location.sourceId}
      copyFields(cached.location, result.location, {"title", "description"}, {"coordX", "coordY", "coordZ"})
    end
    return result
  end
  local function objectives(source, quest)
    quest.objectives = {}
    local values = read(source, "objective")
    if values == nil then quest.objectiveStatus = "missing"; issue("missingObjectiveTables"); return end
    if type(values) ~= "table" then quest.objectiveStatus = "invalid"; issue("malformedObjectives"); return end
    quest.objectiveStatus = "returned"
    local items = {}
    for _, item in ipairs(entries(values, LIMITS.objectiveScan, "objectiveEntriesScanned", "objectiveScanTruncated")) do
      if identifier(item.key) and type(item.value) == "table" then items[#items + 1] = item
      else issue("malformedObjectives") end
    end
    table.sort(items, function(a, b) return idLess(a.key, b.key) end)
    local allowed = math.min(#items, LIMITS.objectives, LIMITS.totalObjectives - report.counts.objectivesRetained)
    local budgetDropped = math.min(#items, LIMITS.objectives) - allowed
    if budgetDropped > 0 then report.counts.objectiveBudgetExceeded = report.counts.objectiveBudgetExceeded + budgetDropped end
    if #items > allowed then
      report.counts.droppedObjectives = report.counts.droppedObjectives + #items - allowed
      partial = true
    end
    for i = 1, allowed do
      local item = items[i]
      local objective = {key = item.key, indicators = {}}
      copyFields(item.value, objective, {"description"}, {"count", "countDone"}, {"complete"})
      local indicators = read(item.value, "indicator")
      if indicators == nil then objective.indicatorStatus = "missing"
      elseif type(indicators) ~= "table" then
        objective.indicatorStatus = "invalid"; issue("malformedIndicators")
        unsupportedIndicator({value = indicators}, quest, objective, "container")
      else
        objective.indicatorStatus = "returned"
        local ids = listIds(indicators, LIMITS.indicatorScan, LIMITS.indicators,
          {scan = "indicatorEntriesScanned", truncated = "indicatorScanTruncated", duplicates = "duplicateIndicators",
            malformed = "malformedIndicators", dropped = "droppedIndicators"},
          function(entry) unsupportedIndicator(entry, quest, objective, "entry") end)
        local retain = math.min(#ids, LIMITS.totalIndicators - report.counts.indicatorsRetained)
        if retain < #ids then
          report.counts.indicatorBudgetExceeded = report.counts.indicatorBudgetExceeded + #ids - retain
          report.counts.droppedIndicators = report.counts.droppedIndicators + #ids - retain
          partial = true
        end
        for j = 1, retain do
          objective.indicators[#objective.indicators + 1] = location(ids[j], quest)
          report.counts.indicatorsRetained = report.counts.indicatorsRetained + 1
        end
      end
      quest.objectives[#quest.objectives + 1] = objective
      report.counts.objectivesRetained = report.counts.objectivesRetained + 1
    end
  end
  for _, id in ipairs(questIds) do
    local quest = {id = id, status = "missing-api", objectives = {}}
    if type(detailFn) ~= "function" then issue("detailFailures")
    else
      local ok, detail = pcall(detailFn, id)
      if not ok then quest.status = "error"; issue("detailFailures")
      elseif detail == nil then quest.status = "no-detail"; issue("detailFailures")
      elseif type(detail) ~= "table" then quest.status = "invalid-detail"; issue("detailFailures")
      else
        quest.status = "returned"; sourceId(detail, quest)
        if quest.sourceId == nil then quest.status = "missing-identity"; issue("detailFailures")
        elseif quest.sourceId ~= id then quest.status = "id-mismatch"; issue("detailFailures") end
        copyFields(detail, quest, {"name", "summary", "description", "domain", "mode", "categoryName", "tag", "tagName"},
          nil, {"complete", "failed", "track", "watch"})
        objectives(detail, quest)
      end
    end
    report.quests[#report.quests + 1] = quest
  end
  report.counts.questsRetained = #report.quests
  report.complete = not partial
  report.status = partial and "partial" or (#questIds == 0 and "empty" or "recorded")
  return report
end
runtime.quests = {capture = capture}

end
