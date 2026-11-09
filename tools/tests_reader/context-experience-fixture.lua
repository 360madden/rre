-- SC629 offline-only Lua 5.1 contract; all APIs below are synthetic.
local root = assert(arg[1], "repository root")
dofile(root .. "/addons/RRECollector/core.lua")
local checks, experienceCalls, experienceLookups, statCalls = 0, 0, 0, 0
local function check(value, reason)
  assert(value, reason)
  checks = checks + 1
end
-- A byte cap must not leave an orphan UTF-8 lead/continuation byte.
local scalar = RRECollectorRuntime.core.scalar
local two = string.char(0xC3, 0xA9)
local three = string.char(0xE2, 0x82, 0xAC)
local four = string.char(0xF0, 0x9F, 0x98, 0x80)
check(scalar(string.rep("a", 2047) .. two .. "Z", 2048) == string.rep("a", 2047), "two-byte boundary truncated intact")
check(scalar(string.rep("a", 2047) .. three .. "Z", 2048) == string.rep("a", 2047), "three-byte boundary truncated intact")
check(scalar(string.rep("a", 2046) .. four .. "Z", 2048) == string.rep("a", 2046), "four-byte boundary truncated intact")
check(scalar(string.rep("a", 2046) .. two .. "Z", 2048) == string.rep("a", 2046) .. two, "exact UTF-8 boundary retained")
check(scalar(string.rep("a", 2050), 2048) == string.rep("a", 2048), "ASCII cap unchanged")
check(scalar(string.rep("b", 255) .. two .. "Z", 256) == string.rep("b", 255), "stats-map byte cap safe")
check(scalar(string.char(0xC3), 2048) == string.char(0xC3), "malformed source not silently sanitized")
local expHandler = function()
  experienceCalls = experienceCalls + 1
  return {accumulated = 0, needed = 1200, rested = 0}
end
local lookupFails = false
local abilityId = "A0000000100000000"
Inspect = setmetatable({
  Unit = {
    Detail = function(which)
      if which == "player" then
        return {id = "uFIXTURE", name = "Fixture", calling = "rogue", level = 43}
      end
      return nil
    end,
    Lookup = function(which)
      if which == "player" then return "uFIXTURE" end
      return nil
    end
  },
  Time = {Frame = function() return 12 end, Real = function() return 1794078000 end},
  System = {Version = function() return "fixture" end},
  TEMPORARY = {Role = function() return 1 end},
  Role = {List = function() return {} end},
  Stat = function() statCalls = statCalls + 1; return {health = 0} end,
  Ability = {New = {
    List = function() return {[abilityId] = true} end,
    Detail = function(argument)
      local item = {id = abilityId, name = "Fixture", cooldown = 0}
      if type(argument) == "table" then return {[abilityId] = item} end
      return item
    end
  }}
}, {
  __index = function(_, key)
    if key == "Experience" then
      experienceLookups = experienceLookups + 1
      if lookupFails then error("fixture lookup failure") end
      return expHandler
    end
    return nil
  end
})
RRECollectorData = {sequence = 0}
dofile(root .. "/addons/RRECollector/context.lua")
dofile(root .. "/addons/RRECollector/abilities.lua")
dofile(root .. "/addons/RRECollector/capabilities.lua")
local snapshot = RRECollectorRuntime.context.snapshot
local baseline = snapshot()
check(experienceCalls == 0 and experienceLookups == 0, "default context must never inspect Experience")
check(statCalls == 1 and baseline.stats.health == 0, "unchanged one stat call")
check(baseline.capabilities.experience == nil and baseline.experience == nil, "default has no Experience capability")
local probe = RRECollectorRuntime.capabilities.probe()
check(probe ~= nil and experienceCalls == 0 and experienceLookups == 0, "capability probe remains Experience-free")
local capture = RRECollectorRuntime.abilities.collect()
check(capture.captureComplete and experienceCalls == 1 and experienceLookups == 1, "one capture one Experience call")
check(statCalls == 3, "one Stat per each context including manual capture")
check(capture.capabilities.experience == true and capture.experience.accumulated == 0
  and capture.experience.needed == 1200 and capture.experience.rested == 0, "finite numbers and zeros retained")
local before = experienceCalls
local candidateContext = snapshot()
check(experienceCalls == before and candidateContext.capabilities.experience == nil, "future defaults remain opt-out")
local tested = snapshot(true)
check(experienceCalls == before + 1 and tested.capabilities.experience, "explicit opt-in calls once")
expHandler = function()
  experienceCalls = experienceCalls + 1
  return setmetatable({}, {
    __index = function(_, key)
      if key == "accumulated" then return 0 end
      if key == "needed" then return math.huge end
      if key == "rested" then error("member failure") end
    end,
    __pairs = function() error("must not traverse") end
  })
end
tested = snapshot(true)
check(tested.capabilities.experience == true and tested.experience.accumulated == 0, "proxy member retained")
check(tested.experience.needed == nil and tested.experience.rested == nil, "nonfinite and throwing members omitted")
expHandler = function() experienceCalls = experienceCalls + 1; return {} end
tested = snapshot(true)
check(tested.capabilities.experience == true and next(tested.experience) == nil, "successful empty table retained")
expHandler = function() experienceCalls = experienceCalls + 1; error("unavailable") end
tested = snapshot(true)
check(tested.capabilities.experience == false and tested.experience == nil, "API exception is false capability")
expHandler = function() experienceCalls = experienceCalls + 1; return "invalid" end
tested = snapshot(true)
check(tested.capabilities.experience == false and tested.experience == nil, "wrong return type is false capability")
lookupFails = true
tested = snapshot(true)
check(tested.capabilities.experience == false and tested.experience == nil, "throwing function lookup guarded")
before = experienceLookups
tested = snapshot()
check(experienceLookups == before and tested.capabilities.experience == nil, "default never touches throwing lookup")
print("SC629_CONTEXT_EXPERIENCE_PASS " .. checks)
