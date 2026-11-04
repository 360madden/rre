-- SC-306: operator-pasted, read-only single-setting probe for RIFT LuaPad.
-- Historical Inspect.Setting.Detail API; never enumerates or modifies settings.
-- This cannot establish Full/Short/None without a same-session UI observation.
local KEY = "ActionBars_AbilityQueue"

local function emit(status, detail)
  local line = "[SC306] " .. status
  if detail ~= nil then line = line .. " " .. detail end
  print(line)
end

if type(Inspect) ~= "table"
    or type(Inspect.Setting) ~= "table"
    or type(Inspect.Setting.Detail) ~= "function" then
  emit("API_UNAVAILABLE")
  return
end

local ok, item = pcall(Inspect.Setting.Detail, KEY)
if not ok then
  emit("CALL_ERROR")
  return
end
if type(item) ~= "table" then
  emit("NO_DETAIL_TABLE", type(item))
  return
end
local id = rawget(item, "id")
if type(id) ~= "string" or id ~= KEY then
  emit("KEY_UNCONFIRMED", "id_type=" .. type(id))
  return
end

local value = rawget(item, "value")
local valueType = type(value)
if valueType == "number" then
  if value ~= value or value == math.huge or value == -math.huge then
    emit("NONFINITE_NUMBER")
    return
  end
  if value == 0 or value == 1 or value == 2 then
    emit("EXACT_KEY_NUMBER", tostring(value))
  else
    emit("EXACT_KEY_NUMBER_REDACTED")
  end
elseif valueType == "boolean" then
  emit("EXACT_KEY_BOOLEAN", tostring(value))
elseif valueType == "string" then
  if value == "Full" or value == "Short" or value == "None"
      or value == "0" or value == "1" or value == "2" then
    emit("EXACT_KEY_STRING", value)
  else
    emit("EXACT_KEY_STRING_REDACTED")
  end
else
  emit("EXACT_KEY_UNSUPPORTED_TYPE", valueType)
end
emit("UI_LABEL_AND_NATIVE_CORRELATION_REQUIRED")
