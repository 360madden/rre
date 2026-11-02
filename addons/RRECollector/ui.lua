-- RRECollector v0.4.2: read-only in-game research toolbar with native buttons.
-- Manual clicks only; icons do not cast and status is not a native action-bar verdict.
local runtime = RRECollectorRuntime
local say = runtime.core.say
local MAX_ROWS, MAX_SLOTS = 8, 8
local WIDTH, BAR_HEIGHT, BROWSER_HEIGHT = 636, 110, 452
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
local root, bar, browser, title, summary, pageLabel, detailLabel
local rowButtons, tiles, tileIcons = {}, {}, {}
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
-- RiftButton supplies built-in RIFT hover/pressed/disabled visuals without a library.
local function button(name, parent, left, top, width, height, caption, handler)
  local f = UI.CreateFrame("RiftButton", name, parent)
  f:SetPoint("TOPLEFT", parent, "TOPLEFT", left, top)
  f:SetWidth(width); f:SetHeight(height)
  f:SetText(caption)
  f:EventAttach(Event.UI.Input.Mouse.Left.Click, function()
    local ok = pcall(handler)
    if not ok then say("Toolbar action failed safely; snapshots preserved.") end
  end, name .. " click")
  return {frame = f, label = f}
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
    t.accent:SetVisible(marked == true)
    if marked then paint(t.accent, tilePressed[i] and color.amber or color.cyan) end
    t.label:SetText(tostring(i) .. " " .. short(a and a.name or "?", 7))
    local valid = a and type(a.icon) == "string" and #a.icon > 0
    if valid then
      local ok = pcall(icon.SetTexture, icon, "Rift", a.icon)
      icon:SetVisible(ok)
    else icon:SetVisible(false) end
  end
  local list = records()
  local total = math.max(1, math.ceil(#list / MAX_ROWS))
  if page > total then page = total end
  if page < 1 then page = 1 end
  modeButtons.known.frame:SetEnabled(mode ~= "known")
  modeButtons.static.frame:SetEnabled(mode ~= "static")
  modeAccents.known:SetVisible(mode == "known")
  modeAccents.static:SetVisible(mode == "static")
  soulButton.frame:SetText("Soul: " .. (soul == "VoidKnight" and "Void Knight" or soul))
  pageButtons.prev.frame:SetEnabled(page > 1)
  pageButtons.next.frame:SetEnabled(page < total)
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
    browserVisible = false; browser:SetVisible(false)
    say("Toolbar hidden. /rre ui to reopen.")
  end)
  -- Restricted RIFT macro: requires an actual click; no autonomous reload.
  local reload = UI.CreateFrame("RiftButton", "RREReloadUI", head)
  reload:SetPoint("TOPLEFT", head, "TOPLEFT", 471, 4)
  reload:SetWidth(81); reload:SetHeight(27); reload:SetText("Reload UI")
  local macroOk, macroError = pcall(function()
    reload:SetSecureMode("restricted")
    reload:EventMacroSet(Event.UI.Input.Mouse.Left.Click, "reloadui")
  end)
  if not macroOk then
    reload:SetEnabled(false)
    say("Reload UI button unavailable: " .. tostring(macroError):sub(1, 100))
  end
  for i = 1, MAX_SLOTS do
    local index = i
    local tile = block("RRESlot" .. i, bar, 12 + (i - 1) * 56, 47,
      50, 56, color.muted)
    tile:SetMouseMasking("full")
    local slotLabel = text("RRESlotLabel" .. i, tile, 3, 40,
      44, 14, 10, tostring(i), color.text)
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
    local accent = block("RRESlotAccent" .. i, tile, 0, 0, 50, 2, color.cyan)
    accent:SetMouseMasking("limited")
    accent:SetVisible(false)
    local icon = UI.CreateFrame("Texture", "RRESlotIcon" .. i, tile)
    icon:SetLayer(1)
    icon:SetPoint("TOPLEFT", tile, "TOPLEFT", 7, 4)
    icon:SetWidth(36); icon:SetHeight(36)
    icon:SetMouseMasking("limited")
    tiles[i], tileIcons[i] = {frame = tile, label = slotLabel, accent = accent}, icon
  end
  summary = text("RRESummary", bar, 470, 43, 158, 70, 11, "", color.grey, true)
  browser = block("RREBrowser", bar, 0, 116, WIDTH, BROWSER_HEIGHT,
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
