-- RRECollector v0.4.6: shared plain controls and readable research icons.
-- Manual clicks only; icons do not cast and status is not a native action-bar verdict.
local runtime = RRECollectorRuntime
local say = runtime.core.say
local MAX_ROWS, MAX_SLOTS = 8, 8
local WIDTH, BAR_HEIGHT, BROWSER_HEIGHT = 636, 128, 452
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
local function secureReloadButton(header)
  local status, reason = "failed", "not-initialized"
  local function publish()
    if type(RRECollectorData) == "table" then
      RRECollectorData.uiReloadMacro = {
        addonVersion = runtime.VERSION, status = status, reason = reason
      }
    end
  end
  local ok, failure = pcall(function()
    local secureContext = UI.CreateContext("RRECollectorReloadSecure")
    if type(secureContext.SetStrata) == "function" then
      secureContext:SetStrata("topmost")
    end
    -- Parent MUST be restricted before securing any child.
    secureContext:SetSecureMode("restricted")
    local frame = UI.CreateFrame("Frame", "RREReloadSecureClick", secureContext)
    frame:SetPoint("TOPLEFT", header, "TOPLEFT", 471, 4)
    frame:SetWidth(81); frame:SetHeight(28)
    frame:SetBackgroundColor(color.button[1], color.button[2],
      color.button[3], color.button[4])
    frame:SetMouseMasking("full")
    reloadFrame = frame
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
  end)
  if not ok then
    status, reason = "failed", tostring(failure):sub(1, 120)
    say("Secure Reload UI unavailable: " .. reason)
    if reloadFrame then pcall(reloadFrame.SetVisible, reloadFrame, false) end
  end
  publish()
end
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
local function knownMap()
  local map = {}
  for _, a in ipairs(known()) do
    if type(a.lookupId) == "string" then map[a.lookupId] = a end
  end
  return map
end
local function candidateMap()
  local map, report = {}, saved().candidateLookup
  if type(report) == "table" and type(report.entries) == "table" then
    for _, entry in ipairs(report.entries) do
      if type(entry.id) == "string" then map[entry.id] = entry end
    end
  end
  return map
end
local function records()
  local result, filter = {}, soul
  if mode == "known" then
    for _, a in ipairs(known()) do
      local src = sourceById[a.lookupId]
      if filter == "All" or (src and src.soul == filter) then
        result[#result + 1] = {
          kind = "known", id = a.lookupId, name = a.name,
          detail = a, source = src
        }
      end
    end
  else
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
      if type(a.lookupId) == "string" and a.passive ~= true
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
  if detail.unusable == false and detail.outOfRange == false and left == 0 then
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
  local status = type(report) == "table" and
    ("saved " .. tostring((report.counts or {}).queried or 0) .. " queries") or
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
    and ("SAVED API-LISTED | " .. (src and src.soul or "other/unknown")
      .. " | base CD " .. (type(cd) == "number" and tostring(cd) .. "s" or "?"))
    or ("HISTORICAL STATIC | " .. (src and src.soul or "?")
      .. " | " .. (item.lookup and safe(item.lookup.status, "?") or "not checked"))
  local live = item.kind == "known" and checked[item.id]
  local extra = live and (" | manual check: " .. live.status) or ""
  local description = item.detail and item.detail.description or
    (item.lookup and item.lookup.detail and item.lookup.detail.description)
  return short(safe(item.name, "?"), 62) .. "\nID " .. tostring(item.id)
    .. "\n" .. short(meta .. extra, 96)
    .. "\n" .. short(safe(description, "No description in this source"), 104)
end
local function draw()
  if not ready then return end
  title:SetText("RRE v" .. runtime.VERSION .. " research")
  summary:SetText(summaryText())
  local map = knownMap()
  for i = 1, MAX_SLOTS do
    local t, icon, id = tiles[i], tileIcons[i], slots[i]
    local a = id and map[id] or nil
    local state = id and checked[id]
    local tint = state and state.tint or color.muted
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
    t.label:SetPoint("TOPLEFT", t.frame, "TOPLEFT", 3 + shift, 47 + shift)
    t.label:SetText(short(a and a.name or "Empty", 18))
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
      slotTooltip:SetPoint("TOPLEFT", bar, "TOPLEFT",
        math.min(12 + (hovered - 1) * 56, WIDTH - 336), BAR_HEIGHT + 3)
      slotTooltipText:SetText(safe(ability and ability.name, "Empty slot")
        .. "\n" .. safe(id, "No ability pinned") .. "\n"
        .. (state and state.status or "Not checked this session")
        .. " | read-only; does not cast")
    end
  end
  local list = records()
  local total = math.max(1, math.ceil(#list / MAX_ROWS))
  if page > total then page = total end
  if page < 1 then page = 1 end
  modeButtons.known.setSelected(mode == "known")
  modeButtons.static.setSelected(mode == "static")
  modeAccents.known:SetVisible(mode == "known")
  modeAccents.static:SetVisible(mode == "static")
  soulButton.setText("Soul: " .. (soul == "VoidKnight" and "Void Knight" or soul))
  pageButtons.prev.setEnabled(page > 1)
  pageButtons.next.setEnabled(page < total)
  pageLabel:SetText((mode == "known" and "API-known" or "Static candidates")
    .. " | " .. soul .. " | " .. #list .. " entries | page " .. page .. "/" .. total)
  for i = 1, MAX_ROWS do
    local item = list[(page - 1) * MAX_ROWS + i]
    local row = rowButtons[i]
    row.frame:SetVisible(item ~= nil)
    row.setSelected(item ~= nil and item.id == selectedId and item.kind == selectedKind)
    if item then
      local tag = item.kind == "known" and "[API] " or "[STATIC] "
      local source = item.source and item.source.soul or "Other"
      row.label:SetText(tag .. short(safe(item.name, item.id), 43)
        .. "   [" .. source .. "]")
    end
  end
  detailLabel:SetText(selectedText(list))
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
local function pinSelected()
  if selectedKind ~= "known" or not knownMap()[selectedId] then
    say("Select an API-known ability before pinning; static candidates are not verified.")
    return
  end
  slots[pinSlot] = selectedId
  local persisted = {}
  for i = 1, MAX_SLOTS do persisted[i] = slots[i] end
  local storage = saved()
  storage.toolbarSlots = persisted
  pinSlot = pinSlot % MAX_SLOTS + 1
  say("Toolbar pin updated; normal UI reload/logout saves the selection.")
  draw()
end
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
    barVisible = false; bar:SetVisible(false)
    if reloadFrame then pcall(reloadFrame.SetVisible, reloadFrame, false) end
    browserVisible = false; browser:SetVisible(false)
    say("Toolbar hidden. /rre ui to reopen.")
  end)
  secureReloadButton(head)
  for i = 1, MAX_SLOTS do
    local index = i
    local tile = block("RRESlot" .. i, bar, 12 + (i - 1) * 56, 47,
      52, 74, color.muted)
    tile:SetMouseMasking("full")
    local slotLabel = text("RRESlotLabel" .. i, tile, 3, 47,
      46, 25, 10, "", color.text, true)
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
      block("RRESlotBottom" .. i, tile, 0, 73, 52, 1, color.grey),
      block("RRESlotLeft" .. i, tile, 0, 1, 1, 72, color.grey),
      block("RRESlotRight" .. i, tile, 51, 1, 1, 72, color.grey)
    }
    for _, edge in ipairs(edges) do edge:SetMouseMasking("limited"); edge:SetLayer(4) end
    local icon = UI.CreateFrame("Texture", "RRESlotIcon" .. i, tile)
    icon:SetLayer(1)
    icon:SetPoint("TOPLEFT", tile, "TOPLEFT", 6, 5)
    icon:SetWidth(40); icon:SetHeight(40)
    icon:SetMouseMasking("limited")
    tiles[i], tileIcons[i] = {frame = tile, label = slotLabel, accent = accent, edges = edges}, icon
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
    mode, page, selectedId = "known", 1, nil; draw()
  end)
  modeButtons.static = button("RREStaticMode", browser, 114, 8, 102, 30,
    "Candidates", function()
    mode, page, selectedId = "static", 1, nil; draw()
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
    page = math.max(1, page - 1); draw()
  end)
  pageButtons.next = button("RRENext", browser, 431, 8, 67, 30, "Next >", function()
    page = page + 1; draw()
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
  button("RREPin", browser, 12, 416, 125, 28, "Pin selected", pinSelected)
  button("RRECheckSelected", browser, 143, 416, 172, 28,
    "Check selected", function()
      if selectedKind == "known" and selectedId then
        checked[selectedId] = apiCheck(selectedId)
      else say("Only API-known abilities support a manual Detail check.") end
      draw()
    end)
  text("RRELegend", browser, 327, 419, 290, 23, 11,
    "No auto-cast / no continuous readiness polling", color.grey)
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
  if left and left.Down and left.Up and cursor and cursor.Move then
    dragHandle:EventAttach(left.Down, beginDrag, "RRE drag begin")
    dragHandle:EventAttach(cursor.Move, moveDrag, "RRE drag move")
    dragHandle:EventAttach(left.Up, function() dragging = false end, "RRE drag end")
    if left.Upoutside then
      dragHandle:EventAttach(left.Upoutside, function() dragging = false end,
        "RRE drag cancel")
    end
  end
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
  barVisible = not barVisible
  bar:SetVisible(barVisible)
  if reloadFrame then pcall(reloadFrame.SetVisible, reloadFrame, barVisible) end
  if not barVisible then browserVisible = false; browser:SetVisible(false) end
  draw()
  return true
end
runtime.ui = {
  start = start,
  refresh = function(clearChecks)
    if clearChecks then checked = {} end
    if ready then draw() end
  end,
  toggle = toggle
}
