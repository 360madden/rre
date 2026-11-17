-- WA006_G2_V1: bounded, read-only RIFT unit observation.
-- UNTESTED IN LIVE RIFT. Run only under an approved, exclusive physical test window.
-- Maximum 128 List entries examined and 8 nonself Detail calls.
-- No movement, targeting, casting, SavedVariables modification or reload.

local M = "WA006_G2_V1"
local records = {}
local function emit(s) records[#records + 1] = M .. "|" .. s end
local function safe(s)
  if type(s) ~= "string" or #s == 0 or #s > 80 or s:find("[%c|]") then return nil end
  return s
end
local function unitId(s)
  s = safe(s)
  if not s or #s ~= 17 or not s:match("^u[0-9A-Fa-f]+$") then return nil end
  return s
end
local function number(v)
  if type(v) == "number" and v == v and v > -math.huge and v < math.huge then
    return string.format("%.6f", v)
  end
  return "unknown"
end
local function clock(fn)
  if type(fn) ~= "function" then return "unknown" end
  local ok, value = pcall(fn)
  return ok and number(value) or "unknown"
end

local unit = type(Inspect) == "table" and Inspect.Unit
local tm = type(Inspect) == "table" and Inspect.Time
if type(unit) ~= "table" or type(unit.List) ~= "function"
    or type(unit.Detail) ~= "function" or type(unit.Lookup) ~= "function" then
  emit("ERROR|missing-unit-api")
else
  local okSelf, rawSelf = pcall(unit.Lookup, "player")
  local selfId = okSelf and unitId(rawSelf) or nil
  if not selfId then
    emit("ERROR|player-id-unavailable")
  else
    emit("BEGIN|self=" .. selfId .. "|frame=" .. clock(type(tm) == "table" and tm.Frame)
      .. "|real=" .. clock(type(tm) == "table" and tm.Real))
    local okList, units = pcall(unit.List)
    if not okList or type(units) ~= "table" then
      emit("ERROR|unit-list-unavailable")
    else
      local examined, details, validXYZ, errors, seen, capped = 0, 0, 0, 0, {}, false
      for rawId, rawSpec in pairs(units) do
        if examined >= 128 then capped = true; break end
        examined = examined + 1
        local id, spec = unitId(rawId), safe(rawSpec)
        if id and spec and id ~= selfId and not seen[id] and details < 8 then
          seen[id] = true
          details = details + 1
          local okDetail, d = pcall(unit.Detail, id)
          if okDetail and type(d) == "table" and d.id ~= nil and d.id ~= id then
            errors = errors + 1
            emit("ERROR|detail-id-mismatch|id=" .. id)
          else
            local x, y, z = "unknown", "unknown", "unknown"
            local idBinding = "missing"
            if okDetail and type(d) == "table" then
              x, y, z = number(d.coordX), number(d.coordY), number(d.coordZ)
              if d.id == id then idBinding = "matched" end
            end
            if idBinding == "matched" and x ~= "unknown"
                and y ~= "unknown" and z ~= "unknown" then
              validXYZ = validXYZ + 1
            end
            emit("ROW|id=" .. id .. "|specifier=" .. spec
              .. "|x=" .. x .. "|y=" .. y .. "|z=" .. z
              .. "|idBinding=" .. idBinding)
          end
        end
      end
      emit("END|examined=" .. examined .. "|details=" .. details
        .. "|validXYZ=" .. validXYZ .. "|errors=" .. errors
        .. "|capped=" .. tostring(capped)
        .. "|frameEnd=" .. clock(type(tm) == "table" and tm.Frame)
        .. "|realEnd=" .. clock(type(tm) == "table" and tm.Real)
        .. "|status=exploratory-only")
    end
  end
end
local report = table.concat(records, "\n")
if type(print) == "function" then pcall(print, report) end
return report
