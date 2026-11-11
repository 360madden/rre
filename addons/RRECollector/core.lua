-- RRECollector v0.4.19: shared read-only helpers; loaded first by RiftAddon.toc.
RRECollectorRuntime = RRECollectorRuntime or {}
RRECollectorRuntime.VERSION = "0.4.19"
RRECollectorRuntime.SCHEMA = 1

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
    if limit <= 0 then return "" end
    local endAt = limit
    -- Keep the byte cap, but never split a valid UTF-8 character at its boundary.
    -- Invalid source bytes remain the wire serializer's responsibility.
    local following = value:byte(endAt + 1)
    if following and following >= 128 and following <= 191 then
      while endAt > 0 do
        local byte = value:byte(endAt)
        if byte < 128 or byte > 191 then break end
        endAt = endAt - 1
      end
      endAt = endAt - 1
    end
    return value:sub(1, endAt)
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

RRECollectorRuntime.core = {
  say = say, finite = finite, scalar = scalar, call = call,
  fieldCopy = fieldCopy, mapCopy = mapCopy,
}
