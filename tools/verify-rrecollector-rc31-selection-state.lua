-- RC-31 pre-gate RED fixture for selection/action state in real ui.lua.
-- Runs locally against source-extracted Lua, with no RIFT API or game input.
-- --expect-red recognizes nine v0.4.10 draw/navigation/control-handle defects.
-- This is NOT yet an in-handler Pin/Check action-guard test. --require-fixed
-- is intended for a later authorized source change after RC-30 acceptance.
local mode = type(arg) == "table" and arg[1] or nil
assert(mode == "--expect-red" or mode == "--require-fixed",
  "usage: lua verify-rrecollector-rc31-selection-state.lua --expect-red|--require-fixed")
local f = assert(io.open("addons/RRECollector/ui.lua", "rb"))
local src = f:read("*a"); f:close()
src = src:gsub("\r\n", "\n")
local selector = assert(src:match("(local function visibleKnownSelection%(%).-)\nlocal function loadSlots%(%)"),
  "RC31 visible selection guard source not found")
local drawStart = assert(src:find("local function draw()", 1, true),
  "ui.lua draw() not found")
local drawSource = src:sub(drawStart)
local fragment = assert(drawSource:match("(  local list = records%(%).-)\n  pageLabel:SetText"),
  "RC31 action-state extraction failed; review changed ui.lua")
local creationStart = assert(src:find('pageButtons.prev = button("RREPrev"', 1, true),
  "ui.lua Prev control not found")
local controlsSource = src:sub(creationStart)
local prevBody = assert(controlsSource:match('pageButtons%.prev = button%("RREPrev".-function%(%)(.-)\n  end%)'),
  "RC31 Prev callback extraction failed")
local nextBody = assert(controlsSource:match('pageButtons%.next = button%("RRENext".-function%(%)(.-)\n  end%)'),
  "RC31 Next callback extraction failed")
local refreshBody = assert(src:match("refresh = function%(clearChecks%)(.-)\n  end,"),
  "RC31 accepted-capture refresh extraction failed")

local prefix = [==[
local MAX_ROWS = 8
local page, mode, soul, pinSlot, pinBaseline, selectedId, selectedKind =
  1, "known", "All", 1, nil, nil, nil
local rows, checked, ready, slots = {}, {}, true, {}
local function saved() return {toolbarSlots={}} end
local function snapshotCalling() return "warrior" end
local function loadSlots() end
local states = {}
local function records() return rows end
local function control(name)
  return {
    setEnabled = function(enabled) states[name] = enabled == true end,
    setSelected = function() end,
    setText = function(value) states[name .. "Text"] = value end
  }
end
local modeButtons = { known=control("modeKnown"), static=control("modeStatic") }
local modeAccents = {
  known={SetVisible=function() end}, static={SetVisible=function() end}
}
local soulButton = control("soul")
local pageButtons = {prev=control("prev"), next=control("next")}
local pinControls = {pin=control("pin"), check=control("check"), undo=control("undo")}
local function renderControls()
]==]
local suffix1 = [==[
end
local function draw() renderControls() end
local function previousPage()
]==]
local suffix2 = [==[
end
local function nextPage()
]==]
local suffix3 = [==[
end
local function refresh(clearChecks)
]==]
local suffix4 = [==[
end
local function setup(items, choiceId, choiceKind, requestedPage, baseline)
  rows, selectedId, selectedKind, page, pinBaseline =
    items, choiceId, choiceKind, requestedPage or 1, baseline
  states = {pin=true, check=true, undo=true, prev=true, next=true}
end
local function read()
  return states, selectedId, selectedKind, page
end
return {
  setup=setup, render=renderControls, prev=previousPage, next=nextPage,
  refresh=refresh, setRows=function(value) rows=value end, read=read
}
]==]
-- Lua long-bracket strings discard their first newline; separate each
-- extracted callback body from the enclosing synthetic function explicitly.
local compilation = prefix .. selector .. "\n" .. fragment .. "\n" .. suffix1 .. prevBody ..
  "\n" .. suffix2 .. nextBody .. "\n" .. suffix3 .. refreshBody ..
  "\n" .. suffix4
local fn, err = (loadstring or load)(compilation, "RC31 selection state")
if not fn then
  local index = 0
  for line in (compilation .. "\n"):gmatch("(.-)\n") do
    index = index + 1
    if index >= 28 and index <= 48 then
      io.stderr:write(string.format("EXTRACT %d: %s\n", index, line))
    end
  end
end
assert(fn, "RC31 extracted Lua failed to compile: " .. tostring(err))
local ui = fn()
local function rows(count)
  local out = {}
  for i=1,count do
    out[i]={id=string.format("A%016X",i), kind="known"}
  end
  return out
end
local failures, checks, badNames = 0, 0, {}
local function check(label, condition)
  checks=checks+1
  if condition then print("PASS " .. label) else
    failures=failures+1; badNames[label]=true; print("RED " .. label)
  end
end
-- The current frozen draw() never disables Pin or Check.
ui.setup(rows(8), nil, nil, 1, nil)
ui.render()
local state = ui.read()
check("pin disabled with no selection", state.pin == false)
check("check disabled with no selection", state.check == false)

-- A known ID may still exist in the list but fall on another page.
ui.setup(rows(16), string.format("A%016X",1), "known", 2, nil)
ui.render()
state = ui.read()
check("pin disabled for off-page selection", state.pin == false)
check("check disabled for off-page selection", state.check == false)

-- Accepted Capture can reorder records while selectedId remains unchanged.
local original = rows(8)
ui.setup(original, original[8].id, "known", 1, nil)
ui.render()
local shifted = rows(9)
shifted[9] = original[8]
for i=8,2,-1 do shifted[i]=original[i-1] end
shifted[1] = {id="AFFFFFFFFFFFFFFFE",kind="known"}
ui.setRows(shifted)
ui.refresh(true)
state = ui.read()
check("pin disabled after capture moved selection off-page", state.pin == false)
check("check disabled after capture moved selection off-page", state.check == false)

-- Rendering a visible API-known row permits both ordinary actions.
local visible = rows(8)
ui.setup(visible, visible[1].id, "known", 1, nil)
ui.render()
state = ui.read()
check("visible known selection enables actions",
  state.pin == true and state.check == true and state.pinText == "Pin to #1")

ui.setup(rows(16), string.format("A%016X",9), "known", 2, nil)
ui.prev()
local _, selId, selKind, currentPage = ui.read()
check("Prev clears both selection fields",
  currentPage == 1 and selId == nil and selKind == nil)

ui.setup(rows(16), string.format("A%016X",1), "known", 1, nil)
ui.next()
_, selId, selKind, currentPage = ui.read()
check("Next clears both selection fields",
  currentPage == 2 and selId == nil and selKind == nil)

ui.setup(rows(8), nil, nil, 1, nil)
ui.render()
state = ui.read()
check("Undo disabled without pin baseline", state.undo == false)
ui.setup(rows(8), nil, nil, 1, {})
ui.render()
state = ui.read()
check("Undo enabled with pin baseline", state.undo == true)

-- The real Check button must be retained in pinControls, or the extracted
-- draw-state test could green while its real handle remains unreachable.
local storedCheckHandle = src:match('pinControls%.check%s*=%s*button%("RRECheckSelected"') ~= nil
check("Check button handle retained for redraw", storedCheckHandle)

local wanted = {
  ["pin disabled with no selection"]=true,
  ["check disabled with no selection"]=true,
  ["pin disabled for off-page selection"]=true,
  ["check disabled for off-page selection"]=true,
  ["pin disabled after capture moved selection off-page"]=true,
  ["check disabled after capture moved selection off-page"]=true,
  ["Prev clears both selection fields"]=true,
  ["Next clears both selection fields"]=true,
  ["Check button handle retained for redraw"]=true
}
if mode == "--expect-red" then
  assert(checks == 12 and failures == 9,
    "expected nine of twelve frozen-source defects, observed " .. failures)
  for name in pairs(wanted) do assert(badNames[name], "missing expected RED: " .. name) end
  for name in pairs(badNames) do assert(wanted[name], "unexpected RED: " .. name) end
  print("EXPECTED_RED_RC31_SELECTION " .. failures .. "/" .. checks ..
    " named scenarios; no addon changes")
else
  assert(failures == 0,
    "RC31 draw/page/control-handle safeguards not yet implemented (" .. failures .. " defects)")
  print("PASS_RC31_SELECTION " .. checks .. " scenarios")
end
