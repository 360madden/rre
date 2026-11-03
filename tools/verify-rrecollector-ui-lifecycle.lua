-- RC-24: source-extracted visibility, reload-registration and tooltip regression checks.
-- Runs without RIFT. This fixture uses the actual Lua function bodies.
local f = assert(io.open("addons/RRECollector/ui.lua", "rb"))
local source = f:read("*a"); f:close()
local function extract(name)
  local block = source:match("%-%- RC24%-" .. name .. "%-BEGIN(.-)%-%- RC24%-" .. name .. "%-END")
  return assert(block, name .. " block missing")
end
local prefix = [==[
local count, notes, drawCount = 0, {}, 0
local function check(value, label) assert(value, label); count = count + 1 end
local function say(message) notes[#notes + 1] = message end
local function draw() drawCount = drawCount + 1 end
local runtime = {VERSION = "0.4.7"}
local color = {button = {.1, .2, .3, 1}}
local RRECollectorData = {}
local Event = {UI = {Input = {Mouse = {Left = {Click = "click"}}}}}
local reloadFrame, bar, browser
local ready, barVisible, browserVisible = true, true, true
local WIDTH, BAR_HEIGHT, BROWSER_HEIGHT, TOOLTIP_HEIGHT = 636, 128, 452, 82
local rejectMacro, lastCreated, secureEnvironment, rejectSurfaceShow = false, nil, false, false
local Inspect = {System = {Secure = function() return secureEnvironment end}}
local methods = {}
function methods:SetStrata(value) self.strata = value end
function methods:SetSecureMode(mode)
  if self.parent and mode == "restricted" and self.parent.secureMode ~= "restricted" then
    error("Incorrect security mode")
  end
  self.secureMode = mode
end
function methods:SetPoint(...) self.point = {...} end
function methods:SetWidth(value) self.width = value end
function methods:SetHeight(value) self.height = value end
function methods:SetBackgroundColor(...) self.color = {...} end
function methods:SetMouseMasking(mode) self.mask = mode end
function methods:SetVisible(value)
  if self.rejectVisibility or (value and self.name == "RREReloadSecureClick" and rejectSurfaceShow)
    then error("secure state denies SetVisible") end
  if self.returnFalse then return false end
  self.visible = value
end
function methods:EventMacroSet(event, command)
  if rejectMacro then
    self.rejectVisibility = true
    error("macro registration failed during secure state")
  end
  check(self.secureMode == "restricted", "macro host restricted")
  self.macroEvent, self.macroCommand = event, command
end
function methods:EventMacroGet(event)
  if self.macroEvent == event then return self.macroCommand end
end
local function makeFrame(name, parent)
  return setmetatable({name = name, parent = parent, visible = true}, {__index = methods})
end
local UI = {
  CreateContext = function(name) return makeFrame(name) end,
  CreateFrame = function(kind, name, parent)
    local frame = makeFrame(name, parent)
    lastCreated = frame
    return frame
  end
}
local function buttonVisual() end
]==]
local suffix = [==[
rejectMacro = true
secureReloadButton({})
check(reloadFrame == nil, "failed macro not published as reloadFrame")
check(lastCreated.visible == false and lastCreated.rejectVisibility,
  "failed macro remains hidden when restricted cleanup is denied")
check(RRECollectorData.uiReloadMacro.status == "failed", "failure diagnostic written")
rejectMacro = false
secureEnvironment = true
local previousCreated = lastCreated
secureReloadButton({})
check(reloadFrame == nil and lastCreated == previousCreated,
  "secure preflight prevents topmost construction")
secureEnvironment = false
rejectSurfaceShow = true
secureReloadButton({})
check(reloadFrame == nil and lastCreated.visible == false,
  "denied final show leaves host hidden and unpublished")
check(RRECollectorData.uiReloadMacro.status == "failed", "denied show reports failure")
rejectSurfaceShow = false
secureReloadButton({})
check(reloadFrame ~= nil and reloadFrame.visible and reloadFrame.macroCommand == "reloadui",
  "working macro published and shown")
check(RRECollectorData.uiReloadMacro.status == "registered", "success diagnostic written")
bar, browser = makeFrame("bar"), makeFrame("browser")
reloadFrame.rejectVisibility = true
check(changeToolbarVisibility(false) == false, "denied secure hide returns false")
check(barVisible and browserVisible and bar.visible and browser.visible and reloadFrame.visible,
  "denied secure hide preserves state and visibility")
check(#notes > 0, "failure reported")
reloadFrame.rejectVisibility = false
bar.rejectVisibility = true
check(changeToolbarVisibility(false) == false, "denied bar hide returns false")
check(barVisible and reloadFrame.visible and bar.visible, "bar failure rolls back secure sibling")
bar.rejectVisibility = false
browser.rejectVisibility = true
check(changeToolbarVisibility(false) == false, "denied browser hide returns false")
check(barVisible and reloadFrame.visible and bar.visible and browser.visible,
  "browser failure rolls back both siblings")
browser.rejectVisibility = false
check(changeToolbarVisibility(false) == true, "normal hide succeeds")
check(not barVisible and not browserVisible and not bar.visible and not browser.visible
  and not reloadFrame.visible, "normal hide keeps siblings synchronized")
reloadFrame.rejectVisibility = true
check(changeToolbarVisibility(true) == false, "denied secure show returns false")
check(not barVisible and not bar.visible and not reloadFrame.visible, "denied show unchanged")
reloadFrame.rejectVisibility = false
check(changeToolbarVisibility(true) == true, "normal show succeeds")
check(barVisible and bar.visible and reloadFrame.visible and not browserVisible,
  "show restores toolbar and reload but keeps browser closed")
check(tooltipYOffset(1080, 98) == 131, "normal tooltip below")
local above = tooltipYOffset(1080, 950)
check(above == -85 and 950 + above >= 0 and 950 + above + 82 <= 1080,
  "bottom-edge tooltip above and visible")
local small = tooltipYOffset(170, 50)
check(50 + small >= 0 and 50 + small + 82 <= 170, "small viewport tooltip clamped")
print("PASS " .. count .. " RC-24 lifecycle/geometry assertions (mock RIFT frames)")
]==]
local compile = loadstring or load
assert(compile(prefix .. extract("RELOAD") .. "\n" .. extract("VISIBILITY") .. "\n"
  .. extract("TOOLTIP") .. "\n" .. suffix, "RC-24 lifecycle"))()
