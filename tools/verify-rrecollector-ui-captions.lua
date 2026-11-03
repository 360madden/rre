-- RC-25: exercise the real two-line caption functions with natural Text metrics.
-- Run with a Lua 5.1-compatible interpreter from the repository root.
local f = assert(io.open("addons/RRECollector/ui.lua", "rb"))
local ui = f:read("*a"); f:close()
local block = assert(ui:match("%-%- RC25%-CAPTIONS%-BEGIN(.-)%-%- RC25%-CAPTIONS%-END"))
local pre = [==[
local checks = 0
local function check(ok, why) assert(ok, why); checks = checks + 1 end
local function safe(value, fallback)
  return type(value) == "string" and #value > 0 and value or fallback
end
local function glyphCount(s)
  local count = 0
  for i = 1, #s do
    local b = s:byte(i)
    if b < 128 or b >= 192 then count = count + 1 end
  end
  return count
end
local function line()
  local obj = {shown = ""}
  function obj:SetText(v) self.shown = v end
  function obj:GetWidth() return glyphCount(self.shown) * 6 end
  return obj
end
]==]
local post = [==[
local a,b = line(),line()
layoutTileCaption(a,b,"Shield of the Hero")
check(a.shown == "Shield", "first row consumes only fitting words")
check(b.shown == "of t...", "overflow shows measured second row with ellipsis")
check(a:GetWidth() <= 46 and b:GetWidth() <= 46, "both rows fit exact 46px width")
layoutTileCaption(a,b,"Patron's Shield")
check(a.shown == "Patr..." and b.shown == "Shield", "long first word and second row")
layoutTileCaption(a,b,"Light")
check(a.shown == "Light" and b.shown == "", "single short word stays on top")
layoutTileCaption(a,b,"Éclair Strike")
check(a.shown == "Éclair" and b.shown == "Strike", "UTF-8 complete word preserved")
layoutTileCaption(a,b,"ÉÉÉÉÉÉÉÉÉÉÉ Strike")
check(a.shown == "ÉÉÉÉ..." and b.shown == "Strike", "UTF-8 ellipsis preserves codepoint boundaries")
check(a:GetWidth() <= 46 and b:GetWidth() <= 46, "non-ASCII rows measured")
layoutTileCaption(a,b,"")
check(a.shown == "Empty" and b.shown == "", "empty slot fallback")
print("PASS " .. checks .. " RC-25 measured two-row caption assertions (mock Text metrics)")
]==]
local compile = loadstring or load
assert(compile(pre .. block .. post, "RC-25 captions"))()
