-- Offline synthetic tests for tools/sc103_luapad_hover_probe.lua.
-- Invoke with a standalone Lua 5.1-compatible interpreter from the RRE root.
-- No RIFT process, SavedVariables, network, or game input.
local FILE = "tools/sc103_luapad_hover_probe.lua"
local LABEL = "RRE_SC103_HOVER_PROBE_20261103"
local KEY = "__RRE_SC103_HOVER_PROBE_20261103"
local checks = 0
local function check(value, label)
  assert(value, label)
  checks = checks + 1
end

local oldPrint = print
local function setup(opts)
  opts = opts or {}
  local state = {
    time = 0, tooltipType = nil, shown = nil, calls = 0,
    attached = false, detachCalls = 0, outputs = {}, handler = nil
  }
  rawset(_G, KEY, nil)
  _G.Event = {System = {Update = {Begin = {}}}}
  _G.Inspect = {
    Time = {Frame = function()
      if opts.clockUnavailable then error("mock-clock-fault") end
      return state.time
    end},
    Tooltip = function()
      state.calls = state.calls + 1
      if opts.tooltipErrors then error("synthetic-tooltip-error") end
      return state.tooltipType, state.shown
    end
  }
  _G.Command = {Event = {
    Attach = function(event, handler, label)
      check(event == Event.System.Update.Begin, "attach event")
      check(label == LABEL, "attach label")
      if opts.rejectAttach then return false end
      state.attached = true
      state.handler = handler
      if opts.returnNil then return nil end
      return true
    end,
    Detach = function(event, handler, label)
      check(event == Event.System.Update.Begin, "detach event")
      check(label == LABEL, "detach label")
      state.detachCalls = state.detachCalls + 1
      if opts.rejectDetach then return false end
      state.attached = false
      if opts.returnNil then return nil end
      return true
    end
  }}
  _G.print = function(message) state.outputs[#state.outputs + 1] = message end
  local ok, err = pcall(dofile, FILE)
  check(ok, "snippet runs: " .. tostring(err))
  local function tick(time, kind, shown)
    state.time, state.tooltipType, state.shown = time, kind, shown
    if state.handler then state.handler() end
  end
  state.tick = tick
  return state
end
local id = "A1234567890ABCDEF"
check(#id == 17, "synthetic ID grammar")

-- Only a repeated exact ability-shaped scalar counts as a candidate.
local a = setup()
check(a.attached, "armed")
a.tick(0.3, "ability", id)
check(a.calls == 0, "initial settle prevents sample")
a.tick(1, "item", id)
a.tick(1.1, "ability", "uPRIVATE4567890A")
a.tick(1.2, "ability", {secret = id})
a.tick(1.3, "ability", id)
a.tick(1.4, "ability", id)
check(a.detachCalls == 0, "needs 3 identical frames")
a.tick(1.5, "ability", id)
check(a.detachCalls == 1, "one detach after candidate")
check(rawget(_G, KEY) == nil, "cleared temporary state")
check(#a.outputs == 2, "one arm and one result")
check(a.outputs[2]:find("ABILITY_ID_CANDIDATE_UNVERIFIED_SOURCE", 1, true) ~= nil, "candidate qualified wording")
check(a.outputs[2]:find(id, 1, true) ~= nil, "one scalar exact ID")
check(table.concat(a.outputs):find("uPRIVATE", 1, true) == nil, "no unit/blob data")
local already = #a.outputs
a.tick(1.6, "ability", id)
check(#a.outputs == already, "stale handler cannot report twice")

-- Invalid/native tooltip types must stop with UNKNOWN, not expose raw values.
local b = setup()
b.tick(1, "unit", "uPRIVATEUNIT")
b.tick(2, "buff", id)
b.tick(3, "ability", "A123")
b.tick(12.1, "ability", {id = id})
check(b.detachCalls == 1, "bounded expiry")
check(b.outputs[2]:find("TIMEOUT_NO_VALID_ID", 1, true) ~= nil, "timeout classified")
check(b.outputs[2]:find("id=UNKNOWN", 1, true) ~= nil, "no candidate")
check(table.concat(b.outputs):find("uPRIVATE", 1, true) == nil, "no unexpected export")

-- A backwards clock and a faulting API abort predictably.
local c = setup()
c.tick(-1, "ability", id)
check(c.outputs[2]:find("CLOCK_UNAVAILABLE", 1, true) ~= nil, "clock drift stops")
local d = setup({tooltipErrors=true})
d.tick(1, "ability", id)
d.tick(1.1, "ability", id)
d.tick(1.2, "ability", id)
check(d.outputs[2]:find("TOOLTIP_API_FAILURE", 1, true) ~= nil, "3 errors stop")
local e = setup({rejectAttach=true})
check(e.outputs[1]:find("ATTACH_REJECTED", 1, true) ~= nil, "attach rejection fails closed")
check(e.detachCalls == 0, "unattached handler not detached")
local f = setup({returnNil=true})
f.tick(1, "ability", id)
f.tick(1.1, "ability", id)
f.tick(1.2, "ability", id)
check(f.detachCalls == 1, "nil-return success matches RIFT API behavior")
local g = setup({rejectDetach=true})
g.tick(1, "ability", id)
g.tick(1.1, "ability", id)
g.tick(1.2, "ability", id)
check(g.outputs[2]:find("DETACH_UNCONFIRMED", 1, true) ~= nil, "detach warning")
local before = #g.outputs
g.tick(2, "ability", id)
check(#g.outputs == before, "inert when detach unconfirmed")

-- Re-running the snippet stops the previous listener before arming a replacement.
local h = setup()
local former = rawget(_G, KEY)
check(type(former) == "table", "one active listener state")
local rerunOk = pcall(dofile, FILE)
check(rerunOk, "rearm compiles and runs")
check(h.detachCalls == 1, "old listener detached on supersession")
local replacement = rawget(_G, KEY)
check(type(replacement) == "table" and replacement ~= former, "new state replaces old")
check(h.outputs[#h.outputs]:find("ARMED_12_SECONDS", 1, true) ~= nil, "new listener armed")
replacement.stop("MANUAL_CANCEL")
check(h.detachCalls == 2, "manual cancel detaches replacement")
check(rawget(_G, KEY) == nil, "manual cancel clears global")

-- Missing clock and API features fail closed without a new listener.
local i = setup({clockUnavailable = true})
check(i.handler == nil, "missing clock prevents event registration")
check(i.outputs[1]:find("BLOCKED_CLOCK", 1, true) ~= nil, "clock blocked status")
local j = setup()
for n = 1, 901 do j.tick(1, "unit", "uPRIVATE") end
check(j.outputs[#j.outputs]:find("TIMEOUT_FRAME_LIMIT", 1, true) ~= nil, "frame budget enforced")
check(j.detachCalls == 1, "frame budget detaches")

local k = setup()
Inspect.Tooltip = nil
local missingApiOk = pcall(dofile, FILE)
check(missingApiOk, "missing API reports instead of throwing")
check(k.outputs[#k.outputs]:find("BLOCKED_REQUIRED_API", 1, true) ~= nil, "missing API blocked")
check(rawget(_G, KEY) == nil, "missing API leaves no listener")

_G.print = oldPrint
oldPrint("SC103_HOVER_PROBE_OFFLINE_TESTS_PASS " .. checks)
