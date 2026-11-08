-- RRECollector RREC2: bounded read-only publication after a manual API capture.
-- No polling, inbound dispatch, game action, file, socket or process API.
local runtime = RRECollectorRuntime
local VERSION = runtime.VERSION
local finite = runtime.core.finite
local MAX_PAYLOAD, CHUNK_BYTES, MAX_PARTS, MAX_FRAME = 65536, 4096, 16, 8192
local MAX_SAFE, UINT32 = 9007199254740991, 4294967296
local ARRAY = {}
local session, lastSequence
local receipt = {status = "not-published", reason = "addon-load"}
RRECollector_WireFrames = nil

local function fail(code) error("wire-" .. code, 0) end
local function requireValue(ok, code) if not ok then fail(code) end end
local function integer(v, lo, hi)
  return finite(v) and v == math.floor(v) and v >= lo and v <= hi
end
local function hex(value, width, lower)
  requireValue(integer(value, 0, MAX_SAFE), "hex-value")
  local chars = lower and "0123456789abcdef" or "0123456789ABCDEF"
  local out = {}
  for i = width, 1, -1 do
    local digit = value % 16
    out[i] = chars:sub(digit + 1, digit + 1)
    value = math.floor(value / 16)
  end
  requireValue(value == 0, "hex-overflow")
  return table.concat(out)
end
local function nonempty(v, maximum)
  return type(v) == "string" and #v > 0 and #v <= maximum and v:find("%S") ~= nil
end
local function stringJson(value, maximum)
  requireValue(#value <= (maximum or 4096), "string-limit")
  -- Lua strings are bytes. Reject invalid UTF-8 rather than publishing a JSON
  -- document that a strict external consumer cannot decode.
  local i = 1
  while i <= #value do
    local a = value:byte(i)
    local length, low, high = 1, 128, 191
    if a < 128 then length = 1
    elseif a >= 194 and a <= 223 then length = 2
    elseif a >= 224 and a <= 239 then
      length = 3
      if a == 224 then low = 160 elseif a == 237 then high = 159 end
    elseif a >= 240 and a <= 244 then
      length = 4
      if a == 240 then low = 144 elseif a == 244 then high = 143 end
    else fail("utf8") end
    requireValue(i + length - 1 <= #value, "utf8")
    for offset = 1, length - 1 do
      local b = value:byte(i + offset)
      requireValue(b >= (offset == 1 and low or 128) and b <= (offset == 1 and high or 191), "utf8")
    end
    i = i + length
  end
  return '"' .. value:gsub('[%z\1-\31\\"]', function(c)
    if c == '"' then return '\\"' end
    if c == '\\' then return '\\\\' end
    return "\\u00" .. hex(c:byte(), 2, false)
  end) .. '"'
end
local function encode(value, stringMaximum)
  local pieces, seen, bytes, nodes = {}, {}, 0, 0
  local function add(piece)
    bytes = bytes + #piece
    requireValue(bytes <= MAX_PAYLOAD, "payload-limit")
    pieces[#pieces + 1] = piece
  end
  local function visit(v, depth)
    nodes = nodes + 1
    requireValue(nodes <= 10000 and depth <= 6, "structure-limit")
    local kind = type(v)
    if kind == "string" then add(stringJson(v, stringMaximum))
    elseif kind == "boolean" then add(v and "true" or "false")
    elseif kind == "number" then
      requireValue(finite(v), "nonfinite")
      local text = string.format("%.17g", v)
      requireValue(not text:find(",", 1, true), "number-locale")
      add(text)
    elseif kind == "table" then
      requireValue(not seen[v], "cycle")
      seen[v] = true
      if getmetatable(v) == ARRAY then
        add("[")
        for i = 1, #v do
          if i > 1 then add(",") end
          visit(rawget(v, i), depth + 1)
        end
        add("]")
      else
        local keys = {}
        for key in next, v do
          requireValue(type(key) == "string" and #key <= 128, "object-key")
          keys[#keys + 1] = key
          requireValue(#keys <= 512, "object-count")
        end
        table.sort(keys)
        add("{")
        for i, key in ipairs(keys) do
          if i > 1 then add(",") end
          add(stringJson(key)); add(":"); visit(rawget(v, key), depth + 1)
        end
        add("}")
      end
      seen[v] = nil
    else fail("unsupported-value") end
  end
  visit(value, 0)
  return table.concat(pieces)
end
local B64 = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"
local function base64(raw)
  local out = {}
  for i = 1, #raw, 3 do
    local a, b, c = raw:byte(i, i + 2)
    local n = a * 65536 + (b or 0) * 256 + (c or 0)
    local x = math.floor(n / 262144) % 64
    local y = math.floor(n / 4096) % 64
    local z = math.floor(n / 64) % 64
    out[#out + 1] = B64:sub(x + 1, x + 1) .. B64:sub(y + 1, y + 1)
      .. (b and B64:sub(z + 1, z + 1) or "=")
      .. (c and B64:sub(n % 64 + 1, n % 64 + 1) or "=")
  end
  return table.concat(out)
end
local function adler32(raw)
  local a, b = 1, 0
  for i = 1, #raw do a = (a + raw:byte(i)) % 65521; b = (b + a) % 65521 end
  return hex(b * 65536 + a, 8, true)
end
local function hash32(raw)
  local value = 0
  for i = 1, #raw do value = (value * 131 + raw:byte(i)) % UINT32 end
  return value
end
local function newSession(record)
  return hex(math.floor(record.realTime * 1000) % UINT32, 8, true)
    .. hex(math.floor(record.frameTime * 1000000) % UINT32, 8, true)
    .. hex(hash32(record.player.id), 8, true)
    .. hex(hash32(VERSION .. ":" .. record.sequence .. ":" .. string.format("%.17g", record.frameTime)), 8, true)
end
local CONTEXT = {"player", "target", "roleSlot", "roleNames", "clientVersion", "frameTime", "realTime",
  "capabilities", "scope", "stats", "statsTruncated", "experience"}
local COUNTS = {"rawEntries", "uniqueCount", "detailCount", "detailFailures", "duplicates", "ignored", "truncated", "fallbackCalls"}
local UNIT_FIELDS = {}
for _, key in ipairs({"id", "name", "calling", "level", "role", "health", "healthMax", "power", "powerMax", "mana", "manaMax",
  "energy", "energyMax", "charge", "spirit", "combo", "combat", "coordX", "coordY", "coordZ", "race", "raceName", "zone"}) do UNIT_FIELDS[key] = true end
local CAPABILITIES = {}
for _, key in ipairs({"frameTime", "realTime", "clientVersion", "player", "target", "roleSlot", "roleList", "stats", "experience"}) do CAPABILITIES[key] = true end
local function scalarValue(value, maximum)
  return type(value) == "boolean" or finite(value) or (type(value) == "string" and #value <= maximum)
end
local function scalarMap(value, maximum, stringMaximum, allowed, booleans)
  requireValue(type(value) == "table", "context-shape")
  local count = 0
  for key, item in next, value do
    count = count + 1
    requireValue(count <= maximum and type(key) == "string" and #key <= 128 and (not allowed or allowed[key]), "context-shape")
    requireValue(booleans and type(item) == "boolean" or not booleans and scalarValue(item, stringMaximum), "context-shape")
  end
end
local function validateContext(record)
  scalarMap(record.player, 23, 2048, UNIT_FIELDS)
  if record.target ~= nil then scalarMap(record.target, 23, 2048, UNIT_FIELDS) end
  scalarMap(record.capabilities, 9, 256, CAPABILITIES, true)
  -- The ninth capability and optional object are a v0.4.14-only contract.
  requireValue(type(record.capabilities.experience) == "boolean", "context-shape")
  if record.capabilities.experience then
    requireValue(type(record.experience) == "table", "context-shape")
    local count = 0
    for key, value in next, record.experience do
      count = count + 1
      requireValue(count <= 3 and (key == "accumulated" or key == "needed" or key == "rested")
        and finite(value), "context-shape")
    end
  else
    requireValue(record.experience == nil, "context-shape")
  end
  if record.roleNames ~= nil then scalarMap(record.roleNames, 32, 256) end
  if record.stats ~= nil then scalarMap(record.stats, 256, 256) end
  if type(record.clientVersion) == "table" then scalarMap(record.clientVersion, 32, 256)
  elseif record.clientVersion ~= nil then requireValue(scalarValue(record.clientVersion, 256), "context-shape") end
  if record.scope ~= nil then requireValue(type(record.scope) == "string" and #record.scope <= 4096, "context-shape") end
  if record.statsTruncated ~= nil then requireValue(integer(record.statsTruncated, 0, MAX_SAFE), "context-shape") end
end
local function build(record)
  requireValue(type(record) == "table" and record.captureComplete == true and record.addonVersion == VERSION, "capture-unqualified")
  requireValue(integer(record.sequence, 1, MAX_SAFE) and (not lastSequence or record.sequence > lastSequence), "sequence")
  requireValue(finite(record.frameTime) and record.frameTime >= 0 and finite(record.realTime) and record.realTime >= 0, "clocks")
  requireValue(record.frameTime <= MAX_SAFE / 1000000 and record.realTime <= MAX_SAFE / 1000, "clocks")
  local player, c = record.player, record.abilityList
  requireValue(type(player) == "table" and nonempty(player.id, 128) and nonempty(player.name, 256)
    and nonempty(player.calling, 128) and finite(player.level) and player.level > 0, "player")
  requireValue((finite(record.roleSlot) or nonempty(record.roleSlot, 128)) and type(record.capabilities) == "table"
    and record.capabilities.player == true, "context")
  validateContext(record)
  requireValue(type(c) == "table" and c.apiAvailable == true and c.enumerationComplete == true
    and type(c.batchDetailAvailable) == "boolean", "list")
  for _, key in ipairs(COUNTS) do requireValue(integer(c[key], 0, 1024), "counts") end
  requireValue(c.uniqueCount >= 1 and c.uniqueCount <= 512 and c.detailCount == c.uniqueCount
    and c.rawEntries == c.uniqueCount + c.duplicates and c.fallbackCalls <= c.uniqueCount
    and (c.batchDetailAvailable or c.fallbackCalls == c.uniqueCount)
    and c.detailFailures == 0 and c.ignored == 0 and c.truncated == 0, "counts")
  requireValue(type(record.abilities) == "table", "abilities")
  local allowed = {}
  for _, key in ipairs({"lookupId", "id", "idNew", "name", "description", "target", "castingTime", "channeled", "cooldown",
    "currentCooldownBegin", "currentCooldownDuration", "currentCooldownRemaining", "currentCooldownExpired", "currentCooldownPaused",
    "unusable", "outOfRange", "rangeMin", "rangeMax", "costPower", "costMana", "costEnergy", "costCharge", "costSpirit",
    "costPlanarCharge", "positioned", "passive", "continuous", "autoattack", "weapon", "stealthRequired", "gainCharge",
    "racial", "icon", "focusMin", "focusMax"}) do allowed[key] = true end
  local abilities, ids = setmetatable({}, ARRAY), {}
  for i = 1, c.uniqueCount do
    local row = rawget(record.abilities, i)
    requireValue(type(row) == "table" and type(row.lookupId) == "string" and #row.lookupId == 17
      and row.lookupId:match("^A[0-9A-F]+$") and not ids[row.lookupId], "ability-id")
    ids[row.lookupId] = true
    local copy = {}
    for key, value in next, row do
      requireValue(allowed[key] == true and (type(value) == "string" or type(value) == "boolean" or finite(value)), "ability-field")
      copy[key] = value
    end
    abilities[i] = copy
  end
  for key in next, record.abilities do requireValue(integer(key, 1, c.uniqueCount), "ability-shape") end
  local context = {}
  for _, key in ipairs(CONTEXT) do if record[key] ~= nil then context[key] = record[key] end end
  local token = session or newSession(record)
  local counts = {apiAvailable = true, enumerationComplete = true, batchDetailAvailable = c.batchDetailAvailable}
  for _, key in ipairs(COUNTS) do counts[key] = c[key] end
  local document = {schemaVersion = 1, producer = "RRECollector", addonVersion = VERSION,
    session = token, sequence = record.sequence, source = "rift-api", counts = counts, context = context, abilities = abilities}
  local payload = encode(document)
  local checksum = adler32(payload)
  local parts = math.floor((#payload + CHUNK_BYTES - 1) / CHUNK_BYTES)
  requireValue(parts >= 1 and parts <= MAX_PARTS, "part-limit")
  local frames = {}
  for part = 1, parts do
    local raw = payload:sub((part - 1) * CHUNK_BYTES + 1, part * CHUNK_BYTES)
    local body = encode({schemaVersion = 2, producer = "RRECollector", addonVersion = VERSION, session = token,
      sequence = record.sequence, part = part, parts = parts, encoding = "base64", payloadBytes = #payload,
      adler32 = checksum, data = base64(raw)}, 5464)
    local frame = "RREC2|" .. token .. "|" .. hex(record.sequence, 16, false) .. "|" .. hex(#body, 8, false)
      .. "|" .. body .. "|ENDRREC2"
    requireValue(#frame <= MAX_FRAME, "frame-limit")
    frames[part] = frame
  end
  return frames, {status = "complete", addonVersion = VERSION, session = token, sequence = record.sequence,
    parts = parts, payloadBytes = #payload, adler32 = checksum, abilities = c.uniqueCount}
end
local function beginAttempt()
  RRECollector_WireFrames = nil
  receipt = {status = "pending", reason = "capture-attempt"}
end
local function abort(reason)
  RRECollector_WireFrames = nil
  receipt = {status = "failed", reason = reason or "capture-unavailable"}
  return receipt
end
local function publish(record)
  beginAttempt()
  local ok, frames, result = pcall(build, record)
  if not ok then
    local reason = type(frames) == "string" and frames:match("wire%-([a-z0-9%-]+)") or nil
    receipt = {status = "failed", reason = reason or "publisher-error"}
    return receipt
  end
  -- This retains one complete generation, not a cross-process atomicity claim.
  session, lastSequence = result.session, result.sequence
  receipt = result
  RRECollector_WireFrames = frames
  return receipt
end
runtime.wire = {beginAttempt = beginAttempt, abort = abort, publish = publish, receipt = function() return receipt end}
