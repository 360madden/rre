-- RC-31 frozen-source browser-label ambiguity and identity controls.
-- Read-only, synthetic four-ID row/Detail/Pin/Undo regression; no game input.
-- Modes: --expect-red (frozen v0.4.10), --require-fixed (future distinct labels).
local mode = type(arg) == "table" and arg[1] or nil
assert(mode == "--expect-red" or mode == "--require-fixed",
  "usage: lua verify-rrecollector-rc31-browser-duplicate-identity.lua --expect-red|--require-fixed")
local f = assert(io.open("addons/RRECollector/ui.lua", "rb"))
local src = f:read("*a"); f:close()
src = src:gsub("\r\n", "\n")
local function fragment(first, after)
  local a = assert(src:find(first, 1, true), "missing source start: " .. first)
  local b = assert(src:find(after, a + #first, true), "missing source end: " .. after)
  return src:sub(a, b - 1)
end
local selectedText = fragment("local function selectedText(items)", "-- RC24-TOOLTIP-BEGIN")
local renderSource = fragment(
  "  for i = 1, MAX_ROWS do\n    local item = list[(page - 1) * MAX_ROWS + i]",
  '  if mode == "static" and snapshotCalling() ~= nil')
local selectSource = fragment("local function selectAt(index)", "-- RC27-PIN-BEGIN")
local selector = fragment("local function visibleKnownSelection()", "local function loadSlots()")
local pinSource = fragment("local function pinSelected()", "-- RC27-PIN-END")

local prelude = [==[
local MAX_ROWS, MAX_SLOTS, page, pinSlot, pinBaseline = 8, 8, 1, 1, nil
local mode, soul, selectedId, selectedKind = "known", "All", nil, nil
local rows, known, slots, rowButtons, checked = {}, {}, {}, {}, {}
local RRECollectorData = {toolbarSlots={}}
local function safe(x, fallback) return type(x)=="string" and #x>0 and x or fallback end
local function short(x, n) return #x>n and x:sub(1,n-3) .. "..." or x end
local function records() return rows end
local function knownMap() return known end
local function saved() return RRECollectorData end
local function say(x) end
local function draw() end
for i=1,4 do
  local id=string.format("A%016X",i)
  rows[i]={id=id, kind="known", name="Changing Role", source={soul="Other"}}
  known[id]={name="Changing Role"}
end
for i=1,MAX_SLOTS do
  slots[i]="ORIGINAL_"..i
  RRECollectorData.toolbarSlots[i]=slots[i]
end
for i=1,MAX_ROWS do
  rowButtons[i]={
    frame={SetVisible=function(self,v) self.visible=v end},
    setSelected=function(v) end,
    label={SetText=function(self,v) self.value=v end}
  }
end
]==]
local tail = [==[
local original = RRECollectorData.toolbarSlots
renderRows()
local baselineLabel = rowButtons[1].label.value
local duplicate = true
for i=2,4 do
  if rowButtons[i].label.value ~= baselineLabel then duplicate=false end
end
local identityPass = 0
for i=1,4 do
  local id=rows[i].id
  selectAt(i)
  assert(selectedId==id and selectedKind=="known", "row/ID binding "..i)
  assert(selectedText(records()):find("ID "..id,1,true), "detail ID "..i)
  pinSelected()
  assert(slots[1]==id and RRECollectorData.toolbarSlots[1]==id, "pin ID "..i)
  assert(pinBaseline ~= nil and pinSlot==2, "undo baseline "..i)
  undoPins()
  assert(pinBaseline==nil and pinSlot==1 and RRECollectorData.toolbarSlots==original,
    "undo reference/target "..i)
  for j=1,MAX_SLOTS do
    assert(slots[j]=="ORIGINAL_"..j and original[j]==slots[j],
      "undo slot "..i.."/"..j)
  end
  identityPass=identityPass+1
end
return {duplicate=duplicate, identityPass=identityPass, baselineLabel=baselineLabel}
]==]
local program = table.concat({
  prelude, selectedText,
  "local function renderRows()\n  local list=records()\n" .. renderSource .. "\nend\n",
  selector, selectSource, pinSource, tail}, "\n")
local build, err = (loadstring or load)(program, "RC31 source-extracted duplicate-ID paths")
assert(build, "unable to parse source fragments: " .. tostring(err))
local result = build()
assert(result.identityPass==4, "distinct ID controls not complete")
if mode=="--expect-red" then
  assert(result.duplicate, "frozen browser-label ambiguity did not reproduce")
  assert(result.baselineLabel=="[API] Changing Role   [Other]", "unexpected source label")
  print("EXPECTED_RED_RC31_DUPLICATE_ROW_LABEL 1/5; ID/Detail/Pin/Undo controls 4/4 PASS")
else
  assert(not result.duplicate, "RC31 still renders identical labels for four distinct API-known IDs")
  print("PASS_RC31_DUPLICATE_ROW_LABEL 5/5")
end
print("LIMIT synthetic IDs/rows/SavedVariables; no current RIFT font or game behavior")
