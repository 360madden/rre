-- RRECollector v0.4.16: calling-neutral known browser, guarded pins, measured captions.
-- Manual clicks only; icons do not cast and status is not a native action-bar verdict.
local runtime = RRECollectorRuntime
local say = runtime.core.say
local MAX_ROWS, MAX_SLOTS = 8, 8
local WIDTH, BAR_HEIGHT, BROWSER_HEIGHT, TOOLTIP_HEIGHT = 636, 128, 452, 82
local X, Y = 295, 98
local color = {
  background = {0.035, 0.063, 0.086, 0.97},
  header = {0.075, 0.125, 0.166, 0.98},
  button = {0.102, 0.190, 0.239, 0.98},
  row = {0.084, 0.148, 0.182, 0.97},
  rowHover = {0.145, 0.280, 0.330, 0.99},
  rowPressed = {0.045, 0.090, 0.126, 1},
  rowSelected = {0.105, 0.215, 0.276, 1},
  muted = {0.125, 0.157, 0.176, 1},
  cyan = {0.220, 0.730, 0.810, 1},
  amber = {0.932, 0.714, 0.302, 1},
  red = {0.850, 0.270, 0.290, 1},
  text = {0.936, 0.963, 0.977, 1},
  grey = {0.640, 0.710, 0.742, 1}
}
local root, bar, browser, title, summary, pageLabel, detailLabel, reloadFrame
local rowButtons, tiles, tileIcons = {}, {}, {}
local slotTooltip, slotTooltipText
local modeButtons, modeAccents, pageButtons, soulButton = {}, {}, {}, nil
local tileHovered, tilePressed = {}, {}
local mode, soul, page = "known", "All", 1
local selectedId, selectedKind = nil, nil
local browserVisible, barVisible = false, true
local ready, pinSlot = false, 1
local slots, checked = {}, {}
local pinBaseline = nil
local pinControls = {}
local sourceById = {}
for _, entry in ipairs(runtime.candidateCatalog.entries or {}) do
  sourceById[entry.id] = entry
end

local function safe(value, fallback)
  if type(value) == "string" and #value > 0 then return value end
  return fallback or "unknown"
end
local function short(value, length)
  local v = safe(value, "?")
  if #v <= length then return v end
  local n = length - 3
  while n > 1 do
    local b = string.byte(v, n + 1)
    if not b or b < 128 or b >= 192 then break end
    n = n - 1
  end
  return v:sub(1, n) .. "..."
end
local function paint(frame, tint)
  frame:SetBackgroundColor(tint[1], tint[2], tint[3], tint[4])
end
local function block(name, parent, left, top, width, height, tint)
  local f = UI.CreateFrame("Frame", name, parent)
  f:SetPoint("TOPLEFT", parent, "TOPLEFT", left, top)
  f:SetWidth(width); f:SetHeight(height)
  paint(f, tint)
  return f
end
local function text(name, parent, left, top, width, height, font, value, tint, wrap)
  local f = UI.CreateFrame("Text", name, parent)
  f:SetLayer(2)
  f:SetPoint("TOPLEFT", parent, "TOPLEFT", left, top)
  f:SetWidth(width); f:SetHeight(height)
  f:SetFontSize(font); f:SetWordwrap(wrap == true)
  f:SetMouseMasking("limited")
  local c = tint or color.text
  f:SetFontColor(c[1], c[2], c[3], c[4])
  f:SetText(value or "")
  return f
end
-- RC23-CONTROLS-BEGIN
-- Normal visual children are shared by ordinary and restricted click surfaces.
-- Their pointer callbacks never change the protected host or its click macro.
local function buttonVisual(name, host, width, height, caption)
  local fill = block(name .. "Fill", host, 1, 1, width - 2, height - 2, color.button)
  fill:SetLayer(0); fill:SetMouseMasking("limited")
  local edges = {
    block(name .. "BorderTop", host, 0, 0, width, 1, color.grey),
    block(name .. "BorderBottom", host, 0, height - 1, width, 1, color.header),
    block(name .. "BorderLeft", host, 0, 1, 1, height - 2, color.grey),
    block(name .. "BorderRight", host, width - 1, 1, 1, height - 2, color.header)
  }
  for _, edge in ipairs(edges) do
    edge:SetLayer(1); edge:SetMouseMasking("limited")
  end
  local label = UI.CreateFrame("Text", name .. "Caption", host)
  label:SetLayer(3); label:SetMouseMasking("limited"); label:SetWordwrap(false)
  label:SetPoint("CENTER", host, "CENTER", 0, 0)
  local enabled, hovered, pressed, selected = true, false, false, false
  local function dimensionsFit()
    local okW, w = pcall(label.GetWidth, label)
    local okH, h = pcall(label.GetHeight, label)
    if not okW or not okH or type(w) ~= "number" or type(h) ~= "number"
      or w ~= w or h ~= h or w < 0 or h < 0 then return true end
    return w <= width - 12 and h <= height - 6
  end
  local function setCaption(value)
    value = tostring(value or ""):gsub("[\r\n]", " ")
    -- All commands begin at the same size. Use actual unconstrained Text metrics,
    -- not character-count estimates, deprecated APIs, or stretched glyphs.
    label:SetText(value)
    for size = 13, 11, -1 do
      label:SetFontSize(size)
      if dimensionsFit() then return end
    end
    -- Unexpected localized/long captions use a bounded UTF-8-safe ellipsis.
    local rest = value
    for _ = 1, 160 do
      if #rest == 0 then break end
      local n = #rest
      while n > 1 and rest:byte(n) >= 128 and rest:byte(n) < 192 do n = n - 1 end
      rest = rest:sub(1, n - 1)
      label:SetText(rest .. "...")
      if dimensionsFit() then return end
    end
    label:SetText("...")
  end
  local function render()
    paint(fill, not enabled and color.muted or pressed and color.rowPressed
      or hovered and color.rowHover or selected and color.rowSelected or color.button)
    local light = not enabled and color.muted or selected and color.cyan
      or hovered and color.cyan or color.grey
    local dark = not enabled and color.muted or color.background
    paint(edges[1], pressed and dark or light)
    paint(edges[3], pressed and dark or light)
    paint(edges[2], pressed and light or dark)
    paint(edges[4], pressed and light or dark)
    local ink = not enabled and color.grey or selected and color.cyan or color.text
    label:SetFontColor(ink[1], ink[2], ink[3], ink[4])
    label:SetPoint("CENTER", host, "CENTER", pressed and 1 or 0, pressed and 1 or 0)
  end
  local mouse = Event.UI.Input.Mouse
  local function attach(event, handler, suffix)
    if event then host:EventAttach(event, handler, name .. suffix) end
  end
  if mouse.Cursor then
    attach(mouse.Cursor.In, function() hovered = enabled; render() end, " enter")
    attach(mouse.Cursor.Out, function() hovered, pressed = false, false; render() end, " leave")
  end
  if mouse.Left then
    attach(mouse.Left.Down, function() if enabled then pressed = true; render() end end, " down")
    attach(mouse.Left.Up, function() pressed = false; render() end, " up")
    attach(mouse.Left.Upoutside, function() pressed, hovered = false, false; render() end, " cancel")
  end
  setCaption(caption); render()
  return {
    frame = host, label = label, setText = setCaption,
    isEnabled = function() return enabled end,
    setEnabled = function(value)
      enabled = value == true
      if not enabled then pressed, hovered = false, false end
      render()
    end,
    setSelected = function(value) selected = value == true; render() end
  }
end
local function button(name, parent, left, top, width, height, caption, handler)
  local f = block(name, parent, left, top, width, height, color.button)
  f:SetMouseMasking("full")
  local visual = buttonVisual(name, f, width, height, caption)
  f:EventAttach(Event.UI.Input.Mouse.Left.Click, function()
    if not visual.isEnabled() then return end
    local ok, failure = pcall(handler)
    if not ok then say(name .. " action failed: " .. tostring(failure):sub(1, 130)) end
  end, name .. " click")
  return visual
end
-- RC23-CONTROLS-END
-- RIFT's SetSecureMode API requires every restricted frame to have a
-- restricted parent. Keep the secure hardware-click surface in its OWN context;
-- the rest of the toolbar and ordinary buttons remain normal.
-- RC24-RELOAD-BEGIN
local function secureReloadButton(header)
  local status, reason = "failed", "not-initialized"
  local function publish()
    if type(RRECollectorData) == "table" then
      RRECollectorData.uiReloadMacro = {
        addonVersion = runtime.VERSION, status = status, reason = reason
      }
    end
  end
  local frame
  local ok, failure = pcall(function()
    -- A secure combat state can reject both macro setup and cleanup.
    local secureFn = type(Inspect) == "table" and type(Inspect.System) == "table"
      and Inspect.System.Secure
    if type(secureFn) == "function" then
      local stateOk, inSecure = pcall(secureFn)
      if not stateOk or inSecure ~= false then error("secure-system-active") end
    end
    local secureContext = UI.CreateContext("RRECollectorReloadSecure")
    if type(secureContext.SetStrata) == "function" then
      secureContext:SetStrata("topmost")
    end
    -- Parent MUST be restricted before securing any child.
    secureContext:SetSecureMode("restricted")
    frame = UI.CreateFrame("Frame", "RREReloadSecureClick", secureContext)
    frame:SetPoint("TOPLEFT", header, "TOPLEFT", 471, 4)
    frame:SetWidth(81); frame:SetHeight(28)
    frame:SetBackgroundColor(color.button[1], color.button[2],
      color.button[3], color.button[4])
    frame:SetMouseMasking("full")
    -- Keep the normal child hidden before restriction; later secure-state
    -- failures cannot strand a visible topmost control without a macro.
    frame:SetVisible(false)
    buttonVisual("RREReloadSecure", frame, 81, 28, "Reload UI")
    frame:SetSecureMode("restricted")
    -- Only a real click can trigger the command; not an addon Lua action.
    local result = frame:EventMacroSet(Event.UI.Input.Mouse.Left.Click, "reloadui")
    if result == false then error("reload-macro-registration-rejected") end
    if type(frame.EventMacroGet) == "function" then
      if frame:EventMacroGet(Event.UI.Input.Mouse.Left.Click) ~= "reloadui" then
        error("reload-macro-readback-mismatch")
      end
      status, reason = "registered", "readback-matched"
    else
      -- The macro can still be valid on builds missing the optional readback API.
      status, reason = "unverified", "readback-API-unavailable"
    end
    local shown, showResult = pcall(frame.SetVisible, frame, true)
    if not shown or showResult == false then
      error("reload-surface-show-rejected: " .. tostring(showResult))
    end
  end)
  if not ok then
    status, reason = "failed", tostring(failure):sub(1, 120)
    say("Secure Reload UI unavailable: " .. reason)
    if frame then pcall(frame.SetVisible, frame, false) end
  else
    -- A rejected macro must never leave a showable reload control behind.
    reloadFrame = frame
  end
  publish()
end
-- RC24-RELOAD-END
-- Wide ability rows retain left-aligned text, with hover, press and selection.
local function rowButton(name, parent, left, top, width, height, caption, handler)
  local f = block(name, parent, left, top, width, height, color.row)
  local accent = block(name .. "Accent", f, 0, 0, 3, height, color.row)
  accent:SetMouseMasking("limited")
  local label = text(name .. "Text", f, 10, 4, width - 18, height - 4,
    14, caption, color.text)
  f:SetMouseMasking("full")
  local hovered, pressed, selected = false, false, false
  local function render()
    local fill = pressed and color.rowPressed or hovered and color.rowHover
      or selected and color.rowSelected or color.row
    paint(f, fill)
    paint(accent, selected and color.amber or hovered and color.cyan or color.row)
    local ink = selected and color.amber or color.text
    label:SetFontColor(ink[1], ink[2], ink[3], ink[4])
    label:SetPoint("TOPLEFT", f, "TOPLEFT",
      pressed and 11 or 10, pressed and 5 or 4)
  end
  local mouse = Event.UI.Input.Mouse
  local cursor, leftMouse = mouse.Cursor, mouse.Left
  if cursor and cursor.In and cursor.Out then
    f:EventAttach(cursor.In, function() hovered = true; render() end, name .. " enter")
    f:EventAttach(cursor.Out, function() hovered = false; pressed = false; render() end,
      name .. " leave")
  end
  if leftMouse and leftMouse.Down and leftMouse.Up then
    f:EventAttach(leftMouse.Down, function() pressed = true; render() end,
      name .. " down")
    f:EventAttach(leftMouse.Up, function() pressed = false; render() end,
      name .. " up")
    if leftMouse.Upoutside then
      f:EventAttach(leftMouse.Upoutside,
        function() pressed = false; hovered = false; render() end,
        name .. " cancel")
    end
  end
  f:EventAttach(Event.UI.Input.Mouse.Left.Click, function()
    local ok = pcall(handler)
    if not ok then say("Ability row action failed safely.") end
  end, name .. " click")
  render()
  return {
    frame = f, label = label,
    setSelected = function(value)
      selected = value == true
      render()
    end
  }
end
local function saved()
  return type(RRECollectorData) == "table" and RRECollectorData or {}
end
local function clampPosition(x, y)
  local ok, w, h = pcall(function() return UIParent:GetWidth(), UIParent:GetHeight() end)
  if not ok or type(w) ~= "number" or type(h) ~= "number" then return x, y end
  local required = BAR_HEIGHT + (browserVisible and BROWSER_HEIGHT + 6 or 0)
  return math.floor(math.max(0, math.min(x, math.max(0, w - WIDTH)))),
    math.floor(math.max(0, math.min(y, math.max(0, h - required))))
end
local function savePosition()
  if type(RRECollectorData) == "table" then
    RRECollectorData.toolbarPosition = {x = X, y = Y}
  end
end
local function known()
  local v = saved().latest
  return type(v) == "table" and type(v.abilities) == "table" and v.abilities or {}
end
local function snapshotCalling()
  local latest = saved().latest
  local player = type(latest) == "table" and latest.player or nil
  return type(player) == "table" and type(player.calling) == "string"
    and player.calling or nil
end
local function knownMap()
  local map = {}
  for _, a in ipairs(known()) do
    if type(a) == "table" and type(a.lookupId) == "string" then
      map[a.lookupId] = a
    end
  end
  return map
end
-- RC30-SLOT-DISPLAY-BEGIN
-- A saved ID not found in the current API-known snapshot is not an empty slot.
-- Never change slots or SavedVariables while choosing presentation labels.
local function slotDisplayLabels(id, ability, check)
  if id == nil then
    return "Empty", "Empty slot", "Not checked this session", nil
  end
  if type(ability) ~= "table" then
    return "Not in list", "ID not in current API-known snapshot", "NOT IN SNAPSHOT", nil
  end
  local label = safe(ability.name, "Unnamed ability")
  local current = type(check) == "table" and check or nil
  return label, label, current and current.status or "Not checked this session", current
end
-- RC30-SLOT-DISPLAY-END
local function candidateMap()
  local map, report = {}, saved().candidateLookup
  if type(report) == "table" and type(report.entries) == "table" then
    for _, entry in ipairs(report.entries) do
      if type(entry) == "table" and type(entry.id) == "string" then
        map[entry.id] = entry
      end
    end
  end
  return map
end
local function records()
  -- API-known IDs come from the current calling, not the Warrior-only research catalog.
  local result, filter = {}, mode == "static" and soul or "All"
  if mode == "known" then
    local calling = snapshotCalling()
    local warrior = type(calling) == "string"
      and calling:lower():find("warrior", 1, true) ~= nil
    for _, a in ipairs(known()) do
      if type(a) == "table" and type(a.lookupId) == "string" then
        -- Never cross-label non-Warrior abilities using static Warrior IDs.
        local src = warrior and sourceById[a.lookupId] or nil
        result[#result + 1] = {
          kind = "known", id = a.lookupId, name = a.name,
          detail = a, source = src
        }
      end
    end
  elseif snapshotCalling() == nil or snapshotCalling():lower():find("warrior", 1, true) then
    local looked = candidateMap()
    for _, src in ipairs(runtime.candidateCatalog.entries or {}) do
      if filter == "All" or src.soul == filter then
        result[#result + 1] = {
          kind = "static", id = src.id, name = src.name,
          source = src, lookup = looked[src.id]
        }
      end
    end
  end
  table.sort(result, function(a, b)
    local an, bn = safe(a.name, a.id):lower(), safe(b.name, b.id):lower()
    if an == bn then return a.id < b.id end
    return an < bn
  end)
  return result
end
-- Actions require an API-known row visible on the current page, not merely
-- an ID that survives in an earlier snapshot or an off-page selection.
local function visibleKnownSelection()
  if mode ~= "known" or selectedKind ~= "known" or type(selectedId) ~= "string" then
    return nil
  end
  local items = records()
  local first = (page - 1) * MAX_ROWS + 1
  for i = first, math.min(first + MAX_ROWS - 1, #items) do
    local item = items[i]
    if item and item.kind == "known" and item.id == selectedId then return item end
  end
  return nil
end
local function loadSlots()
  local previous, available = saved().toolbarSlots, known()
  if type(previous) == "table" then
    for i = 1, MAX_SLOTS do
      if type(previous[i]) == "string" and #previous[i] <= 128 then
        slots[i] = previous[i]
      end
    end
  else
    local index = 1
    for _, a in ipairs(available) do
      if type(a) == "table" and type(a.lookupId) == "string" and a.passive ~= true
        and index <= MAX_SLOTS then
        slots[index] = a.lookupId
        index = index + 1
      end
    end
  end
end
local function apiCheck(id)
  local a = knownMap()[id]
  if not a then return {status = "NOT IN SNAPSHOT", tint = color.grey} end
  local api = type(Inspect) == "table" and Inspect.Ability
  local newer = type(api) == "table" and api.New
  local fn = type(newer) == "table" and newer.Detail
  if type(fn) ~= "function" then
    return {status = "DETAIL UNAVAILABLE", tint = color.grey}
  end
  local ok, detail = pcall(fn, id)
  if not ok or type(detail) ~= "table" then
    return {status = "DETAIL UNKNOWN", tint = color.grey}
  end
  -- Detail may be a proxy: individually guard property reads and drop nonfinite data.
  local copiedOk, clean = pcall(runtime.abilities.copyDetail, detail)
  if not copiedOk or type(clean) ~= "table" then
    return {status = "DETAIL UNKNOWN", tint = color.grey}
  end
  detail = clean
  if detail.passive == true then
    return {status = "PASSIVE", tint = color.grey}
  end
  if detail.outOfRange == true then
    return {status = "OUT OF RANGE", tint = color.red}
  end
  if detail.unusable == true then
    return {status = "UNUSABLE", tint = color.red}
  end
  if detail.currentCooldownPaused == true then
    return {status = "COOLDOWN PAUSED", tint = color.amber}
  end
  local left = detail.currentCooldownRemaining
  if type(left) == "number" and left == left and left > 0 then
    return {status = "COOLDOWN " .. string.format("%.1fs", left),
      tint = color.amber}
  end
  -- Missing flags are unknown, not false. Independent GCD/LOS are unverified.
  if detail.passive == false and detail.unusable == false
    and detail.outOfRange == false and left == 0 then
    return {status = "API NO BLOCK*", tint = color.cyan}
  end
  return {status = "READINESS UNKNOWN", tint = color.grey}
end
local function checkPinned()
  for i = 1, MAX_SLOTS do
    if slots[i] then checked[slots[i]] = apiCheck(slots[i]) end
  end
end
local function summaryText()
  local report, attempt = saved().candidateLookup, saved().candidateAttempt
  local calling = snapshotCalling()
  if type(calling) == "string" and not calling:lower():find("warrior", 1, true) then
    return "Known: " .. tostring(#known())
      .. "\n" .. short(calling, 15) .. " abilities"
      .. "\nWarrior IDs: N/A"
      .. "\nManual checks only"
  end
  local counts = type(report) == "table" and report.counts or nil
  local status = type(report) == "table" and
    ("saved " .. tostring((type(counts) == "table" and counts.queried) or 0) .. " queries") or
    "no saved receipt"
  local reason = type(attempt) == "table"
    and (safe(attempt.status, "?") .. ": " .. safe(attempt.reason, "-"))
    or "attempt not recorded"
  return "Known: " .. tostring(#known()) .. "   Static: "
    .. tostring(#(runtime.candidateCatalog.entries or {}))
    .. "\nCandidate: " .. short(status, 25)
    .. "\n" .. short(reason, 31)
    .. "\nManual checks are not live tracking"
end
local function selectedText(items)
  if not selectedId then return "Select a row, or click an icon. API readiness, GCD and LOS are unverified." end
  local item
  for _, r in ipairs(items) do
    if r.id == selectedId and r.kind == selectedKind then item = r; break end
  end
  if not item then return "Selected item is outside this filter." end
  local src = item.source
  local cd = item.detail and item.detail.cooldown
  local meta = item.kind == "known"
    and ("SAVED API-LISTED | " .. (src and src.soul or (snapshotCalling() or "soul unknown"))
      .. " | base CD " .. (type(cd) == "number" and tostring(cd) .. "s" or "?"))
    or ("HISTORICAL STATIC | " .. (src and src.soul or "?")
      .. " | " .. (item.lookup and safe(item.lookup.status, "?") or "not checked"))
  local live = item.kind == "known" and checked[item.id]
  local extra = live and (" | manual check: " .. live.status) or ""
  local lookupDetail = item.lookup and item.lookup.detail
  local description = item.detail and item.detail.description or
    (type(lookupDetail) == "table" and lookupDetail.description)
  return short(safe(item.name, "?"), 62) .. "\nID " .. tostring(item.id)
    .. "\n" .. short(meta .. extra, 96)
    .. "\n" .. short(safe(description, "No description in this source"), 104)
end
-- RC24-TOOLTIP-BEGIN
local function tooltipYOffset(screenHeight, barY)
  local below = BAR_HEIGHT + 3
  if type(screenHeight) ~= "number" or barY + below + TOOLTIP_HEIGHT <= screenHeight then
    return below
  end
  if barY >= TOOLTIP_HEIGHT + 3 then return -(TOOLTIP_HEIGHT + 3) end
  -- Very small viewports may require a card overlapping the bar.
  return math.max(-barY, screenHeight - barY - TOOLTIP_HEIGHT)
end
-- RC24-TOOLTIP-END
-- RC25-CAPTIONS-BEGIN
-- Each icon gets two independent natural-width Text lines. Automatic wrapping
-- and a fixed-height Text frame can silently clip the second line in RIFT.
local function tileLineFits(frame, value)
  frame:SetText(value)
  local ok, width = pcall(frame.GetWidth, frame)
  return ok and type(width) == "number" and width == width
    and width >= 0 and width <= 46
end
local function withoutLastGlyph(value)
  local n = #value
  while n > 1 do
    local b = value:byte(n)
    if b < 128 or b >= 192 then break end
    n = n - 1
  end
  return value:sub(1, n - 1)
end
local function fitTileLine(frame, value)
  if tileLineFits(frame, value) then return value end
  local prefix = value
  for _ = 1, 160 do
    prefix = withoutLastGlyph(prefix)
    local candidate = prefix .. "..."
    if tileLineFits(frame, candidate) then return candidate end
    if #prefix == 0 then break end
  end
  frame:SetText("...")
  return "..."
end
local function withoutFirstGlyph(value)
  if #value <= 1 then return "" end
  local first = 2
  while first <= #value do
    local byte = value:byte(first)
    if byte < 128 or byte >= 192 then break end
    first = first + 1
  end
  return value:sub(first)
end
local function fitTileTail(frame, value)
  if tileLineFits(frame, value) then return value end
  local suffix = value
  for _ = 1, 160 do
    suffix = withoutFirstGlyph(suffix)
    local candidate = "..." .. suffix
    if tileLineFits(frame, candidate) then return candidate end
    if #suffix == 0 then break end
  end
  frame:SetText("...")
  return "..."
end
local function layoutTileCaption(first, second, value)
  local words = {}
  for word in safe(value, "Empty"):gmatch("%S+") do words[#words + 1] = word end
  if #words == 0 then words[1] = "Empty" end
  local top, consumed = "", 0
  for i, word in ipairs(words) do
    local candidate = #top > 0 and (top .. " " .. word) or word
    if not tileLineFits(first, candidate) then break end
    top, consumed = candidate, i
  end
  if consumed == 0 then
    top, consumed = fitTileLine(first, words[1]), 1
  end
  first:SetText(top)
  local remaining = table.concat(words, " ", consumed + 1)
  second:SetText(remaining ~= "" and fitTileTail(second, remaining) or "")
end
-- RC25-CAPTIONS-END
local function draw()
  if not ready then return end
  title:SetText("RRE v" .. runtime.VERSION .. " research")
  summary:SetText(summaryText())
  local map = knownMap()
  for i = 1, MAX_SLOTS do
    local t, icon, id = tiles[i], tileIcons[i], slots[i]
    local a = id and map[id] or nil
    local state = id and checked[id]
    local captionName, _, _, visibleCheck = slotDisplayLabels(id, a, state)
    local tint = visibleCheck and visibleCheck.tint or color.muted
    local factor = tilePressed[i] and 0.63 or tileHovered[i] and 1.23 or 1
    paint(t.frame, {math.min(1, tint[1] * factor),
      math.min(1, tint[2] * factor), math.min(1, tint[3] * factor), tint[4]})
    local marked = tileHovered[i] or tilePressed[i]
      or (selectedKind == "known" and selectedId == id)
    local borderInk = marked and (tilePressed[i] and color.amber or color.cyan) or color.grey
    paint(t.accent, borderInk)
    for _, edge in ipairs(t.edges) do paint(edge, borderInk) end
    local shift = tilePressed[i] and 1 or 0
    icon:SetPoint("TOPLEFT", t.frame, "TOPLEFT", 6 + shift, 5 + shift)
    t.labelTop:SetPoint("TOPLEFT", t.frame, "TOPLEFT", 3 + shift, 47 + shift)
    t.labelBottom:SetPoint("TOPLEFT", t.frame, "TOPLEFT", 3 + shift, 61 + shift)
    if t.captionName ~= captionName then
      layoutTileCaption(t.labelTop, t.labelBottom, captionName)
      t.captionName = captionName
    end
    local valid = a and type(a.icon) == "string" and #a.icon > 0
    if valid then
      if t.texturePath ~= a.icon then
        local ok = pcall(icon.SetTexture, icon, "Rift", a.icon)
        t.texturePath = ok and a.icon or nil
        t.textureReady = ok
      end
      icon:SetVisible(t.textureReady == true)
    else icon:SetVisible(false) end
  end
  if slotTooltip then
    local hovered
    for i = 1, MAX_SLOTS do if tileHovered[i] then hovered = i; break end end
    slotTooltip:SetVisible(hovered ~= nil and barVisible)
    if hovered then
      local id = slots[hovered]
      local ability = id and map[id]
      local state = id and checked[id]
      local _, tooltipHeading, statusLabel = slotDisplayLabels(id, ability, state)
      local okH, screenHeight = pcall(UIParent.GetHeight, UIParent)
      slotTooltip:SetPoint("TOPLEFT", bar, "TOPLEFT",
        math.min(12 + (hovered - 1) * 56, WIDTH - 336),
        tooltipYOffset(okH and screenHeight or nil, Y))
      slotTooltipText:SetText(tooltipHeading
        .. "\n" .. (id == "" and "(empty saved ID)" or safe(id, "No ability pinned")) .. "\n"
        .. statusLabel
        .. " | read-only; does not cast")
    end
  end
  local list = records()
  local currentCapture = saved().latest
  local savedSeq = type(currentCapture) == "table" and currentCapture.sequence or nil
  local savedCalling = snapshotCalling() or "unknown"
  local savedPlayer = type(currentCapture) == "table" and currentCapture.player or nil
  local savedName = type(savedPlayer) == "table" and safe(savedPlayer.name, "unknown") or "unknown"
  local savedRole = type(currentCapture) == "table" and currentCapture.roleSlot or nil
  local total = math.max(1, math.ceil(#list / MAX_ROWS))
  if page > total then page = total end
  if page < 1 then page = 1 end
  modeButtons.known.setSelected(mode == "known")
  modeButtons.static.setSelected(mode == "static")
  modeAccents.known:SetVisible(mode == "known")
  modeAccents.static:SetVisible(mode == "static")
  soulButton.setText(mode == "known" and "All abilities"
    or ("Soul: " .. (soul == "VoidKnight" and "Void Knight" or soul)))
  soulButton.setEnabled(mode == "static")
  pageButtons.prev.setEnabled(page > 1)
  pageButtons.next.setEnabled(page < total)
  if pinControls.pin then
    pinControls.pin.setText("Pin to #" .. tostring(pinSlot))
    pinControls.pin.setEnabled(visibleKnownSelection() ~= nil)
  end
  if pinControls.check then pinControls.check.setEnabled(visibleKnownSelection() ~= nil) end
  if pinControls.undo then pinControls.undo.setEnabled(pinBaseline ~= nil) end
  pageLabel:SetText((mode == "known" and ("Saved " .. short(savedName, 10)
      .. " " .. short(savedCalling, 10) .. " r" .. short(tostring(savedRole or "?"), 2)
      .. " API #" .. tostring(savedSeq or "?")) or "Warrior-only static candidates")
    .. " | " .. soul .. " | " .. #list .. " entries | page " .. page .. "/" .. total)
  for i = 1, MAX_ROWS do
    local item = list[(page - 1) * MAX_ROWS + i]
    local row = rowButtons[i]
    row.frame:SetVisible(item ~= nil)
    row.setSelected(item ~= nil and item.id == selectedId and item.kind == selectedKind)
    if item then
      local tag = item.kind == "known" and "[API] " or "[STATIC] "
      local source = item.source and item.source.soul
        or (item.kind == "known" and (snapshotCalling() or "Soul unknown") or "Warrior")
      row.label:SetText(tag .. item.id .. "  "
        .. short(safe(item.name, item.id), 30)
        .. "   [" .. short(source, 18) .. "]")
    end
  end
  if mode == "static" and snapshotCalling() ~= nil
    and not snapshotCalling():lower():find("warrior", 1, true) then
    detailLabel:SetText("Warrior-only historical candidates do not apply to saved "
      .. short(savedCalling, 24) .. ". Choose Saved API for this calling.")
  else
    detailLabel:SetText(selectedText(list))
  end
end
local function execute(command)
  if type(runtime.command) == "function" then
    runtime.command(command)
  else say("Collector commands not ready.") end
  draw()
end
local function selectAt(index)
  local list = records()
  local item = list[(page - 1) * MAX_ROWS + index]
  if item then selectedId, selectedKind = item.id, item.kind; draw() end
end
-- RC27-PIN-BEGIN
-- A session baseline permits one Undo to restore ALL pins changed since the
-- first click. It preserves the original SavedVariables table (or nil) exactly.
local function pinSelected()
  if not visibleKnownSelection() or not knownMap()[selectedId] then
    say("Select a visible API-known row before pinning; off-page and static IDs are not eligible.")
    return
  end
  if type(RRECollectorData) ~= "table" then
    say("Character SavedVariables unavailable; pin was not changed.")
    return
  end
  local storage = saved()
  if not pinBaseline then
    local original = {}
    for i = 1, MAX_SLOTS do original[i] = slots[i] end
    pinBaseline = {slots = original, savedSlots = storage.toolbarSlots, nextSlot = pinSlot}
  end
  local changedSlot = pinSlot
  slots[pinSlot] = selectedId
  local persisted = {}
  for i = 1, MAX_SLOTS do persisted[i] = slots[i] end
  storage.toolbarSlots = persisted
  pinSlot = pinSlot % MAX_SLOTS + 1
  say("Pinned slot " .. tostring(changedSlot)
    .. ". Undo pins restores the session baseline before a UI reload/logout.")
  draw()
end
local function undoPins()
  if not pinBaseline then return end
  if type(RRECollectorData) ~= "table" then
    say("Character SavedVariables unavailable; cannot restore pins.")
    return
  end
  local baseline = pinBaseline
  for i = 1, MAX_SLOTS do slots[i] = baseline.slots[i] end
  RRECollectorData.toolbarSlots = baseline.savedSlots
  pinSlot = baseline.nextSlot
  pinBaseline = nil
  say("Toolbar pins restored to their pre-edit session state.")
  draw()
end
-- RC27-PIN-END
local function selectSlot(index)
  local id = slots[index]
  if not id then return end
  selectedId, selectedKind, soul, mode, page = id, "known", "All", "known", 1
  local list = records()
  for n, item in ipairs(list) do
    if item.id == id then page = math.ceil(n / MAX_ROWS); break end
  end
  browserVisible = true
  browser:SetVisible(true)
  local nx, ny = clampPosition(X, Y)
  if pcall(bar.SetPoint, bar, "TOPLEFT", UIParent, "TOPLEFT", nx, ny) then
    X, Y = nx, ny; savePosition()
  end
  checked[id] = apiCheck(id)
  draw()
end
-- RC24-VISIBILITY-BEGIN
local function setVisibleSafe(frame, desired)
  local ok, result = pcall(frame.SetVisible, frame, desired)
  if not ok then return false, result end
  if result == false then return false, "SetVisible rejected" end
  return true
end
local function changeToolbarVisibility(visible)
  if not ready then return false end
  if visible == barVisible then return true end
  local previousBar = barVisible
  -- Reload UI is a separate restricted sibling and must change first.
  if reloadFrame then
    local ok, reason = setVisibleSafe(reloadFrame, visible)
    if not ok then
      say("Toolbar unchanged; secure Reload UI visibility denied: " .. tostring(reason):sub(1, 100))
      return false
    end
  end
  local ok, reason = setVisibleSafe(bar, visible)
  if not ok then
    if reloadFrame then setVisibleSafe(reloadFrame, previousBar) end
    say("Toolbar unchanged; bar visibility failed: " .. tostring(reason):sub(1, 100))
    return false
  end
  if not visible then
    local browserOk, browserReason = setVisibleSafe(browser, false)
    if not browserOk then
      setVisibleSafe(bar, previousBar)
      if reloadFrame then setVisibleSafe(reloadFrame, previousBar) end
      say("Toolbar unchanged; browser visibility failed: " .. tostring(browserReason):sub(1, 100))
      return false
    end
  end
  barVisible = visible
  if not visible then browserVisible = false end
  draw()
  return true
end
-- RC24-VISIBILITY-END
local function createUI()
  local stored = saved().toolbarPosition
  if type(stored) == "table" and type(stored.x) == "number"
    and type(stored.y) == "number" and stored.x == stored.x and stored.y == stored.y then
    X, Y = clampPosition(stored.x, stored.y)
  end
  local ctx = UI.CreateContext("RRECollectorToolbar")
  bar = UI.CreateFrame("Frame", "RREToolbar", ctx)
  bar:SetPoint("TOPLEFT", UIParent, "TOPLEFT", X, Y)
  bar:SetWidth(WIDTH); bar:SetHeight(BAR_HEIGHT)
  paint(bar, color.background)
  local head = block("RREToolbarHead", bar, 0, 0, WIDTH, 36, color.header)
  local dragHandle = block("RREToolbarDrag", head, 0, 0, 165, 36, color.header)
  dragHandle:SetMouseMasking("full")
  title = text("RREToolbarTitle", dragHandle, 8, 6, 158, 27, 14,
    "RRE COLLECTOR", color.text)
  button("RREBrowse", head, 168, 4, 72, 28, "Browse", function()
    browserVisible = not browserVisible
    browser:SetVisible(browserVisible)
    if browserVisible then
      local nx, ny = clampPosition(X, Y)
      if pcall(bar.SetPoint, bar, "TOPLEFT", UIParent, "TOPLEFT", nx, ny) then
        X, Y = nx, ny; savePosition()
      end
    end
    draw()
  end)
  button("RRECheckPins", head, 245, 4, 73, 28, "Check 8", function()
    checkPinned(); draw()
  end)
  button("RRECapture", head, 323, 4, 73, 28, "Capture", function()
    execute("capture")
  end)
  button("RRERetry", head, 401, 4, 65, 28, "Retry", function()
    execute("candidates")
  end)
  button("RREHide", head, 557, 4, 69, 28, "Hide", function()
    if changeToolbarVisibility(false) then
      say("Toolbar hidden. /rre ui to reopen.")
    end
  end)
  secureReloadButton(head)
  for i = 1, MAX_SLOTS do
    local index = i
    local tile = block("RRESlot" .. i, bar, 12 + (i - 1) * 56, 47,
      52, 77, color.muted)
    tile:SetMouseMasking("full")
    local function captionLine(suffix, top)
      local label = UI.CreateFrame("Text", "RRESlotLabel" .. i .. suffix, tile)
      label:SetLayer(2); label:SetMouseMasking("limited")
      label:SetPoint("TOPLEFT", tile, "TOPLEFT", 3, top)
      label:SetFontSize(10); label:SetWordwrap(false)
      label:SetFontColor(color.text[1], color.text[2], color.text[3], color.text[4])
      label:SetText("")
      return label
    end
    local labelTop, labelBottom = captionLine("Top", 47), captionLine("Bottom", 61)
    tile:EventAttach(Event.UI.Input.Mouse.Left.Click, function()
      local ok = pcall(selectSlot, index)
      if not ok then say("Toolbar slot selection failed safely.") end
    end, "RRESlot" .. i .. " click")
    local pointer = Event.UI.Input.Mouse
    if pointer.Cursor and pointer.Cursor.In and pointer.Cursor.Out then
      tile:EventAttach(pointer.Cursor.In, function()
        tileHovered[index] = true; draw()
      end, "RRESlot" .. i .. " enter")
      tile:EventAttach(pointer.Cursor.Out, function()
        tileHovered[index], tilePressed[index] = false, false; draw()
      end, "RRESlot" .. i .. " leave")
    end
    if pointer.Left and pointer.Left.Down and pointer.Left.Up then
      tile:EventAttach(pointer.Left.Down, function()
        tilePressed[index] = true; draw()
      end, "RRESlot" .. i .. " down")
      tile:EventAttach(pointer.Left.Up, function()
        tilePressed[index] = false; draw()
      end, "RRESlot" .. i .. " up")
      if pointer.Left.Upoutside then
        tile:EventAttach(pointer.Left.Upoutside, function()
          tilePressed[index], tileHovered[index] = false, false; draw()
        end, "RRESlot" .. i .. " cancel")
      end
    end
    local accent = block("RRESlotAccent" .. i, tile, 0, 0, 52, 1, color.grey)
    accent:SetMouseMasking("limited"); accent:SetLayer(4)
    local edges = {
      block("RRESlotBottom" .. i, tile, 0, 76, 52, 1, color.grey),
      block("RRESlotLeft" .. i, tile, 0, 1, 1, 75, color.grey),
      block("RRESlotRight" .. i, tile, 51, 1, 1, 75, color.grey)
    }
    for _, edge in ipairs(edges) do edge:SetMouseMasking("limited"); edge:SetLayer(4) end
    local icon = UI.CreateFrame("Texture", "RRESlotIcon" .. i, tile)
    icon:SetLayer(1)
    icon:SetPoint("TOPLEFT", tile, "TOPLEFT", 6, 5)
    icon:SetWidth(40); icon:SetHeight(40)
    icon:SetMouseMasking("limited")
    tiles[i], tileIcons[i] = {
      frame = tile, labelTop = labelTop, labelBottom = labelBottom,
      accent = accent, edges = edges
    }, icon
  end
  slotTooltip = block("RRESlotTooltip", bar, 12, BAR_HEIGHT + 3, 332, 82, color.background)
  slotTooltip:SetLayer(50); slotTooltip:SetMouseMasking("limited")
  slotTooltipText = text("RRESlotTooltipText", slotTooltip, 8, 6, 316, 70,
    12, "", color.text, true)
  slotTooltip:SetVisible(false)
  summary = text("RRESummary", bar, 470, 43, 158, 81, 11, "", color.grey, true)
  browser = block("RREBrowser", bar, 0, BAR_HEIGHT + 6, WIDTH, BROWSER_HEIGHT,
    color.background)
  modeButtons.known = button("RREKnownMode", browser, 10, 8, 98, 30,
    "Known", function()
    mode, soul, page, selectedId = "known", "All", 1, nil; draw()
  end)
  modeButtons.static = button("RREStaticMode", browser, 114, 8, 102, 30,
    "Warrior IDs", function()
    mode, soul, page, selectedId = "static", "All", 1, nil; draw()
  end)
  modeAccents.known = block("RREKnownActive", browser, 10, 38, 98, 2, color.cyan)
  modeAccents.static = block("RREStaticActive", browser, 114, 38, 102, 2, color.cyan)
  modeAccents.known:SetMouseMasking("limited")
  modeAccents.static:SetMouseMasking("limited")
  soulButton = button("RRESoulFilter", browser, 222, 8, 130, 30, "Soul: All", function()
    local filters = {"All", "Paladin", "VoidKnight", "Paragon"}
    for i, f in ipairs(filters) do
      if soul == f then soul = filters[i % #filters + 1]; break end
    end
    page, selectedId = 1, nil; draw()
  end)
  pageButtons.prev = button("RREPrev", browser, 358, 8, 67, 30, "< Prev", function()
    if page > 1 then page = page - 1; selectedId, selectedKind = nil, nil end
    draw()
  end)
  pageButtons.next = button("RRENext", browser, 431, 8, 67, 30, "Next >", function()
    local totalPages = math.max(1, math.ceil(#records() / MAX_ROWS))
    if page < totalPages then page = page + 1; selectedId, selectedKind = nil, nil end
    draw()
  end)
  button("RRECloseBrowser", browser, 504, 8, 122, 30, "Close", function()
    browserVisible = false; browser:SetVisible(false)
  end)
  pageLabel = text("RREPage", browser, 12, 47, 610, 29, 13, "", color.cyan)
  for i = 1, MAX_ROWS do
    local index = i
    rowButtons[i] = rowButton("RRERow" .. i, browser, 12,
      79 + (i - 1) * 31, 610, 28, "-", function() selectAt(index) end)
  end
  detailLabel = text("RREDetail", browser, 13, 330, 607, 84,
    12, "", color.text, true)
  pinControls.pin = button("RREPin", browser, 12, 416, 125, 28,
    "Pin to #1", pinSelected)
  pinControls.check = button("RRECheckSelected", browser, 143, 416, 172, 28,
    "Check selected", function()
      if visibleKnownSelection() then
        checked[selectedId] = apiCheck(selectedId)
      else say("Select a visible API-known row before checking Detail.") end
      draw()
    end)
  pinControls.undo = button("RREUndoPins", browser, 321, 416, 106, 28,
    "Undo pins", undoPins)
  text("RRELegend", browser, 433, 419, 186, 23, 11,
    "No casting / polling", color.grey)
  browser:SetVisible(false)
  local dragging, offsetX, offsetY = false, 0, 0
  local function mouse()
    if type(Inspect) ~= "table" or type(Inspect.Mouse) ~= "function" then return nil end
    local ok, m = pcall(Inspect.Mouse)
    if ok and type(m) == "table" and type(m.x) == "number"
      and type(m.y) == "number" then return m end
    return nil
  end
  local function beginDrag()
    local m = mouse()
    if not m then return end
    offsetX, offsetY = m.x - X, m.y - Y
    dragging = true
  end
  local function moveDrag()
    if not dragging then return end
    local m = mouse()
    if not m or m.Left ~= true then dragging = false; return end
    local sw, sh = UIParent:GetWidth(), UIParent:GetHeight()
    if type(sw) ~= "number" or type(sh) ~= "number" then return end
    local desiredX, desiredY = clampPosition(m.x - offsetX, m.y - offsetY)
    if pcall(bar.SetPoint, bar, "TOPLEFT", UIParent, "TOPLEFT", desiredX, desiredY) then
      X, Y = desiredX, desiredY
      savePosition()
    end
  end
  local mouseEvent = Event.UI and Event.UI.Input and Event.UI.Input.Mouse
  local left = mouseEvent and mouseEvent.Left
  local cursor = mouseEvent and mouseEvent.Cursor
  -- RC25-DRAG-BEGIN
  if left and left.Down and left.Up then
    dragHandle:EventAttach(left.Down, beginDrag, "RRE drag begin")
    local globalMove = type(Event.Mouse) == "table" and Event.Mouse.Move
    local attach = type(Command) == "table" and type(Command.Event) == "table"
      and Command.Event.Attach
    local globallyAttached = false
    if globalMove and type(attach) == "function" then
      local ok, result = pcall(attach, globalMove, moveDrag, "RRE global drag move")
      globallyAttached = ok and result ~= false
    end
    if not globallyAttached and cursor and cursor.Move then
      dragHandle:EventAttach(cursor.Move, moveDrag, "RRE drag move")
    end
    dragHandle:EventAttach(left.Up, function() dragging = false end, "RRE drag end")
    if left.Upoutside then
      dragHandle:EventAttach(left.Upoutside, function() dragging = false end,
        "RRE drag cancel")
    end
  end
  -- RC25-DRAG-END
  loadSlots()
  ready = true
  draw()
end
local function start()
  if ready then draw(); return true end
  if type(UI) ~= "table" or type(UI.CreateFrame) ~= "function"
    or type(UI.CreateContext) ~= "function" or type(Event) ~= "table"
    or not Event.UI or not Event.UI.Input then
    say("Toolbar UI unavailable; slash commands still work.")
    return false
  end
  local ok, failure = pcall(createUI)
  if not ok then
    ready = false
    say("Toolbar initialization failed: " .. tostring(failure):sub(1, 140))
    return false
  end
  return true
end
local function toggle()
  if not ready then return start() end
  return changeToolbarVisibility(not barVisible)
end
runtime.ui = {
  start = start,
  refresh = function(clearChecks)
    if clearChecks then
      checked = {}
      selectedId, selectedKind = nil, nil
      -- A newly captured character may have started with no saved snapshot.
      -- Populate only untouched empty slots; never replace existing pins.
      if ready and type(slots) == "table" and next(slots) == nil
        and type(saved().toolbarSlots) ~= "table" then
        loadSlots()
      end
    end
    if ready then draw() end
  end,
  toggle = toggle
}
