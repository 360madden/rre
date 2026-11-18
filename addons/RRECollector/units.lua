-- RRECollector manual bounded multi-unit witness; no polling, targeting or game actions.
-- Historical Inspect.Unit.List maps unit ID -> specifier; live behavior unverified.
local runtime = RRECollectorRuntime
local call, finite = runtime.core.call, runtime.core.finite
local MAX_LIST, MAX_DETAILS, MAX_TEXT = 128, 8, 80

local function unitId(value)
  if type(value) ~= "string" or #value ~= 17
    or not value:match("^u[0-9A-Fa-f]+$") then return nil end
  return value
end
local function specifier(value)
  if type(value) ~= "string" or #value < 1 or #value > MAX_TEXT
    or value:find("[%c|]") then return nil end
  return value
end
local function number(value)
  if finite(value) and math.abs(value) <= 1000000000000 then return value end
  return nil
end
local function clock(fn)
  local ok, value = call(fn)
  return ok and number(value) or nil
end
local function field(source, key)
  if type(source) ~= "table" then return nil end
  local ok, value = pcall(function() return source[key] end)
  return ok and value or nil
end

local function capture()
  local api = type(Inspect) == "table" and Inspect or {}
  local unit = type(api.Unit) == "table" and api.Unit or {}
  local time = type(api.Time) == "table" and api.Time or {}
  local report = {
    schemaVersion = runtime.SCHEMA, addonVersion = runtime.VERSION,
    scope = "manual-bounded-unit-api-witness", status = "unavailable",
    reason = "missing-unit-api", limits = {listEntries = MAX_LIST, detailCalls = MAX_DETAILS},
    counts = {examined = 0, invalidEntries = 0, selfEntries = 0,
      nonselfEligible = 0, detailsCalled = 0, detailErrors = 0,
      idMismatches = 0, idMissing = 0, qualifiedXYZ = 0},
    records = {}, listEnumerationComplete = false,
    detailSampleComplete = false, coordinateFrameVerified = false,
    nativeIdentityVerified = false, atomicSnapshot = false
  }
  report.frameStart = clock(time.Frame)
  report.realStart = clock(time.Real)
  local function finish(status, reason)
    report.status, report.reason = status, reason
    report.frameEnd = clock(time.Frame)
    report.realEnd = clock(time.Real)
    return report
  end
  if type(unit.List) ~= "function" or type(unit.Detail) ~= "function"
    or type(unit.Lookup) ~= "function" then return finish("unavailable", "missing-unit-api") end
  local selfOk, rawSelf = call(unit.Lookup, "player")
  local selfId = selfOk and unitId(rawSelf) or nil
  if not selfId then return finish("unavailable", "player-id-unavailable") end
  report.selfId = selfId
  local listOk, values = call(unit.List)
  if not listOk then return finish("error", "unit-list-error") end
  if type(values) ~= "table" then return finish("unavailable", "unit-list-non-table") end
  local eligible, capped = {}, false
  for rawId, rawSpec in pairs(values) do
    if report.counts.examined >= MAX_LIST then capped = true; break end
    report.counts.examined = report.counts.examined + 1
    local id, spec = unitId(rawId), specifier(rawSpec)
    if not id or not spec then
      report.counts.invalidEntries = report.counts.invalidEntries + 1
    elseif id == selfId then
      report.counts.selfEntries = report.counts.selfEntries + 1
    else
      eligible[#eligible + 1] = {id = id, specifier = spec}
    end
  end
  report.counts.nonselfEligible = #eligible
  report.listEnumerationComplete = not capped
  report.detailSampleComplete = not capped and #eligible <= MAX_DETAILS
  table.sort(eligible, function(a, b) return a.id < b.id end)
  for i = 1, math.min(#eligible, MAX_DETAILS) do
    local entry = eligible[i]
    local item = {id = entry.id, specifier = entry.specifier,
      idBinding = "missing", detailStatus = "missing", xyzComplete = false}
    report.counts.detailsCalled = report.counts.detailsCalled + 1
    local detailOk, detail = call(unit.Detail, entry.id)
    if not detailOk then
      item.detailStatus = "error"
      report.counts.detailErrors = report.counts.detailErrors + 1
    elseif type(detail) == "table" then
      item.detailStatus = "returned"
      local detailId = field(detail, "id")
      if detailId == nil then
        report.counts.idMissing = report.counts.idMissing + 1
      elseif detailId ~= entry.id then
        item.idBinding = "mismatch"
        report.counts.idMismatches = report.counts.idMismatches + 1
      else
        item.idBinding = "matched"
        local x, y, z = number(field(detail, "coordX")),
          number(field(detail, "coordY")), number(field(detail, "coordZ"))
        if x ~= nil then item.coordX = x end
        if y ~= nil then item.coordY = y end
        if z ~= nil then item.coordZ = z end
        if x ~= nil and y ~= nil and z ~= nil then
          item.xyzComplete = true
          report.counts.qualifiedXYZ = report.counts.qualifiedXYZ + 1
        end
      end
    end
    report.records[#report.records + 1] = item
  end
  if capped then return finish("capped", "list-cap-reached") end
  if #eligible == 0 then
    return finish(report.counts.invalidEntries > 0 and "partial" or "empty",
      report.counts.invalidEntries > 0 and "invalid-list-entries" or "no-nonself-listed")
  end
  if #eligible > MAX_DETAILS then return finish("partial", "detail-sample-cap") end
  if report.counts.invalidEntries > 0 then return finish("partial", "invalid-list-entries") end
  if report.counts.detailErrors > 0 then return finish("partial", "detail-errors") end
  if report.counts.idMismatches > 0 or report.counts.idMissing > 0 then
    return finish("partial", "detail-identity-unqualified")
  end
  if report.counts.qualifiedXYZ < #eligible then return finish("partial", "xyz-incomplete") end
  return finish("complete", "bounded-sample-complete")
end

runtime.units = {capture = capture}
