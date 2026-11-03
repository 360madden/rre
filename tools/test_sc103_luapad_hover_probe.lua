-- Offline synthetic tests for tools/sc103_luapad_hover_probe.lua.
-- Invoke with a standalone Lua 5.1-compatible interpreter from the RRE root.
-- No RIFT process, SavedVariables, network, or game input.
local FILE = "tools/sc103_luapad_hover_probe.lua"
local COPY_FILE = "tools/sc103_luapad_copy_result.lua"
local LABEL = "RRE_SC103_HOVER_PROBE_20261103"
local KEY = "__RRE_SC103_HOVER_PROBE_20261103"
local RESULT_KEY = "__RRE_SC103_HOVER_RESULT_20261103"
local QUARANTINE_KEY = "__RRE_SC103_HOVER_DETACH_QUARANTINE_20261103"
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
  if opts.foreignSameLabelListener then state.foreignSameLabelListener = function() end end
  rawset(_G, KEY, nil)
  rawset(_G, RESULT_KEY, nil)
  rawset(_G, QUARANTINE_KEY, nil)
  _G.Event = {System = {Update = {Begin = {}}}}
  if opts.registryModel then
    state.registrations = {}
    if state.foreignSameLabelListener then
      state.registrations[1] = {event=Event.System.Update.Begin, handler=state.foreignSameLabelListener, label=LABEL}
    end
  end
  _G.Inspect = {
    Time = {Frame = function()
      if opts.clockUnavailable then error("mock-clock-fault") end
       if type(opts.frameReadSequence) == "table" and #opts.frameReadSequence > 0 then return table.remove(opts.frameReadSequence, 1) end
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
      if opts.registryModel then
        state.registrations[#state.registrations + 1] = {event=event, handler=handler, label=label}
      end
      if opts.returnNil then return nil end
      return true
    end,
    Detach = function(event, handler, label)
      check(event == Event.System.Update.Begin, "detach event")
      check(label == LABEL, "detach label")
      state.detachCalls = state.detachCalls + 1
      if opts.foreignSameLabelListener then
        state.detachedHandler = handler or state.foreignSameLabelListener
      end
      if opts.rejectDetach then return false end
      if opts.registryModel then
        local selected = nil
        for index, registration in ipairs(state.registrations) do
          if registration.event == event and
             (handler == nil or registration.handler == handler) and
             (label == nil or registration.label == label) then
            selected = index; break
          end
        end
        if not selected then return false end
        state.detachedHandler = state.registrations[selected].handler
        table.remove(state.registrations, selected) -- One matching registration only.
      end
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
check(type(rawget(_G, RESULT_KEY)) == "table", "terminal candidate cached for copy")
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
-- A clock can regress without ever crossing its initial start timestamp.
-- Never accept three otherwise-stable tooltip frames across that regression.
local middleClock = setup()
middleClock.tick(1.0, "ability", id)
middleClock.tick(0.9, "ability", id)
middleClock.tick(0.8, "ability", id)
check(middleClock.outputs[2]:find("CLOCK_UNAVAILABLE", 1, true) ~= nil,
  "intermediate clock regression must stop")
check(middleClock.outputs[2]:find("id=UNKNOWN", 1, true) ~= nil,
  "intermediate clock regression must not identify a spell")
check(middleClock.detachCalls == 1, "intermediate clock regression detaches once")
local middleRecord = rawget(_G, RESULT_KEY)
check(middleRecord == nil or middleRecord.candidate == nil, "intermediate clock regression caches no ID")
-- Equal frame timestamps are not regressions and remain valid until stall guard.
local plateauClock = setup()
plateauClock.tick(1.0, "ability", id)
plateauClock.tick(1.0, "ability", id)
check(plateauClock.detachCalls == 0, "equal clock plateau remains armed")
plateauClock.tick(1.1, "ability", id)
check(plateauClock.outputs[2]:find("ABILITY_ID_CANDIDATE_UNVERIFIED_SOURCE", 1, true) ~= nil,
  "clock progression after plateau still permits stable candidate")
check(plateauClock.detachCalls == 1, "plateau success detaches exactly once")
-- A final frame-clock re-read may regress after the last validated tooltip sample.
-- Reject the candidate entirely, even if the new value is still after start.
local finishClock = setup({frameReadSequence = {0, 1.0, 1.1, 1.2, 0.9}})
finishClock.tick(1.0, "ability", id)
finishClock.tick(1.1, "ability", id)
finishClock.tick(1.2, "ability", id)
check(finishClock.outputs[2]:find("CLOCK_UNAVAILABLE", 1, true) ~= nil,
  "completion clock regression must fail closed")
check(finishClock.outputs[2]:find("id=UNKNOWN", 1, true) ~= nil,
  "completion clock regression must not print candidate")
check(finishClock.detachCalls == 1, "completion regression detaches once")
check(rawget(_G, RESULT_KEY) == nil, "completion regression stores no candidate record")
finishClock.time = 1.3
dofile(COPY_FILE)
check(finishClock.outputs[#finishClock.outputs]:find("NONE_OR_EXPIRED", 1, true) ~= nil,
  "completion regression cannot be copied later")
-- Deadline updates must be included in the completion-clock monotonic floor.
local timeoutFinishClock = setup({frameReadSequence={0, 11.0, 12.1, 11.9}})
timeoutFinishClock.tick(11.0, "unit", id)
timeoutFinishClock.tick(12.1, "unit", id)
check(timeoutFinishClock.outputs[#timeoutFinishClock.outputs]:find("CLOCK_UNAVAILABLE", 1, true) ~= nil,
  "deadline completion must reject a clock below the triggering update")
check(rawget(_G, RESULT_KEY) == nil, "deadline clock regression must not cache timeout")
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
check(rawget(_G, KEY) == nil, "global cleared despite failed detach")

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

-- Permissive registry model of RIFT's documented one-match wildcard behavior.
-- Actual RIFT duplicate-label acceptance and wildcard ordering are unverified.
local overlapping = setup({foreignSameLabelListener=true, registryModel=true})
check(#overlapping.registrations == 2, "foreign-first model starts with two registrations")
check(overlapping.registrations[1].handler == overlapping.foreignSameLabelListener, "foreign registration is first")
check(overlapping.registrations[2].handler == overlapping.handler, "probe registration is second")
overlapping.tick(1, "ability", id)
overlapping.tick(1.1, "ability", id)
check(#overlapping.registrations == 2, "both registrations remain before candidate")
overlapping.tick(1.2, "ability", id)
check(overlapping.detachCalls == 1, "duplicate-label model attempts one detach")
check(overlapping.detachedHandler == overlapping.handler, "exact probe handler selected for detachment")
check(#overlapping.registrations == 1, "one matching registration removed")
check(overlapping.registrations[1].handler == overlapping.foreignSameLabelListener, "foreign callback stays registered")
check(overlapping.outputs[2]:find("ABILITY_ID_CANDIDATE_UNVERIFIED_SOURCE", 1, true) ~= nil,
  "exact-detach model retains successful candidate")
local failedRegistry = setup({registryModel=true, rejectDetach=true})
check(#failedRegistry.registrations == 1, "failed-detach setup has one registration")
failedRegistry.tick(1, "ability", id)
failedRegistry.tick(1.1, "ability", id)
failedRegistry.tick(1.2, "ability", id)
check(#failedRegistry.registrations == 1, "failed Detach never removes its registration")
check(failedRegistry.outputs[2]:find("DETACH_UNCONFIRMED", 1, true) ~= nil, "failed registry detachment warns operator")
check(rawget(_G, RESULT_KEY).detachConfirmed == false, "failed-detach record persists for operator")
local failedReceipt = rawget(_G, RESULT_KEY)
local staleCallback = failedRegistry.handler
check(pcall(dofile, FILE), "rerun after failed detach must not throw")
check(#failedRegistry.registrations == 1, "failed-detach rerun must NOT attach another callback")
check(failedRegistry.handler == staleCallback, "blocked rerun does not change registered handler")
check(failedRegistry.outputs[#failedRegistry.outputs]:find("BLOCKED_UNCONFIRMED_DETACH", 1, true) ~= nil,
  "blocked rerun reports reload UI requirement")
check(rawget(_G, RESULT_KEY) == failedReceipt, "blocked rerun preserves failure receipt")
local oldMessages = #failedRegistry.outputs
staleCallback()
check(#failedRegistry.outputs == oldMessages, "quarantined callback remains inert")

-- Missing clock and API features fail closed without a new listener.
local i = setup({clockUnavailable = true})
check(i.handler == nil, "missing clock prevents event registration")
check(i.outputs[1]:find("BLOCKED_CLOCK", 1, true) ~= nil, "clock blocked status")
local j = setup()
for n = 1, 901 do j.tick(1, "unit", "uPRIVATE") end
check(j.outputs[#j.outputs]:find("TIMEOUT_FRAME_LIMIT", 1, true) ~= nil, "frame budget enforced")
check(j.detachCalls == 1, "frame budget detaches")

-- The 12-second window must not shrink merely because the game updates at 144 FPS.
local highFps = setup()
for frame = 1, 1440 do highFps.tick(frame / 144, "unit", "uPRIVATE") end
check(highFps.detachCalls == 0, "144 FPS for ten seconds does not time out early")
check(highFps.calls > 900, "high FPS test exercised beyond old total frame cap")
highFps.tick(10 + 1 / 144, "ability", id)
highFps.tick(10 + 2 / 144, "ability", id)
highFps.tick(10 + 3 / 144, "ability", id)
check(highFps.detachCalls == 1, "three stable samples succeed after ten seconds")
check(highFps.outputs[2]:find("ABILITY_ID_CANDIDATE_UNVERIFIED_SOURCE", 1, true) ~= nil,
  "high FPS candidate still qualified")

local k = setup()
Inspect.Tooltip = nil
local missingApiOk = pcall(dofile, FILE)
check(missingApiOk, "missing API reports instead of throwing")
check(k.outputs[#k.outputs]:find("BLOCKED_REQUIRED_API", 1, true) ~= nil, "missing API blocked")
check(rawget(_G, KEY) == nil, "missing API leaves no listener")

-- Time expiry combined with rejected detachment must report both facts and go inert.
local l = setup({rejectDetach = true})
l.tick(12.01, "unit", "uPRIVATE")
check(l.outputs[2]:find("TIMEOUT_NO_VALID_ID", 1, true) ~= nil,
  "time expiry classified when detach fails")
check(l.outputs[2]:find("DETACH_UNCONFIRMED", 1, true) ~= nil,
  "time expiry exposes rejected detach")
check(l.detachCalls == 1, "exactly one detach attempted on timeout")
check(rawget(_G, KEY) == nil, "global cleared after timeout-detach failure")
local expiredOutputCount = #l.outputs
l.tick(13, "ability", id)
check(#l.outputs == expiredOutputCount, "failed-detach listener remains inert after timeout")

-- No update callbacks means no frame-clock advance: operator cancellation is essential.
local m = setup()
check(m.attached and #m.outputs == 1, "no automatic wall-clock callback if game stops updates")
local pending = rawget(_G, KEY)
check(type(pending) == "table", "listener pending without frame events")
pending.stop("MANUAL_CANCEL")
check(m.detachCalls == 1, "manual cancel detaches pending listener")
check(m.outputs[2]:find("MANUAL_CANCEL", 1, true) ~= nil, "manual cancel reported")
check(rawget(_G, KEY) == nil, "manual cancel clears pending state")

-- A transient tooltip API fault interrupts consecutive-valid-sample counting.
local intermittent = {tooltipErrors = false}
local n = setup(intermittent)
n.tick(1.0, "ability", id)
n.tick(1.1, "ability", id)
check(n.detachCalls == 0, "two matches alone not sufficient")
intermittent.tooltipErrors = true
n.tick(1.2, "ability", id)
intermittent.tooltipErrors = false
n.tick(1.3, "ability", id)
check(n.detachCalls == 0, "tooltip fault resets stability; third good reading is not enough")
n.tick(1.4, "ability", id)
check(n.detachCalls == 0, "two post-fault samples still insufficient")
n.tick(1.5, "ability", id)
check(n.detachCalls == 1, "three uninterrupted post-fault samples accepted")


-- A completed result stays in session memory until a separate operator-run copy.
local copyCase = setup()
copyCase.tick(1.0, "ability", id)
copyCase.tick(1.1, "ability", id)
copyCase.tick(1.2, "ability", id)
local saved = rawget(_G, RESULT_KEY)
check(type(saved) == "table" and saved.schema == 1, "result record schema")
check(saved.status == "ABILITY_ID_CANDIDATE_UNVERIFIED_SOURCE" and saved.candidate == id, "cache stores exact sanitized candidate")
check(saved.startedFrame == 0 and saved.finishedFrame == 1.2, "cache stores finite frame-clock bounds")
check(saved.detachConfirmed == true, "cache stores detachment outcome")
local allowedFields = {schema=true, status=true, candidate=true, startedFrame=true, finishedFrame=true, detachConfirmed=true}
for key in pairs(saved) do check(allowedFields[key] == true, "cache has no extra payload field") end
local firstCopyOk, firstCopyErr = pcall(dofile, COPY_FILE)
check(firstCopyOk, "copy snippet runs: " .. tostring(firstCopyErr))
check(copyCase.outputs[#copyCase.outputs]:find(id, 1, true) ~= nil, "copy snippet prints candidate synchronously")
check(rawget(_G, RESULT_KEY) == nil, "copy snippet consumes result")
local secondCopyOk = pcall(dofile, COPY_FILE)
check(secondCopyOk, "second copy runs safely")
check(copyCase.outputs[#copyCase.outputs]:find("NONE_OR_EXPIRED", 1, true) ~= nil, "second copy cannot replay consumed candidate")

local activeCopy = setup()
local pendingCopyOk = pcall(dofile, COPY_FILE)
check(pendingCopyOk and activeCopy.outputs[#activeCopy.outputs]:find("PENDING", 1, true) ~= nil, "copy reports active listener")
check(rawget(_G, KEY) ~= nil, "copy does not stop an active listener")
rawget(_G, KEY).stop("MANUAL_CANCEL")

local staleCopy = setup()
staleCopy.tick(1.0, "ability", id)
staleCopy.tick(1.1, "ability", id)
staleCopy.tick(1.2, "ability", id)
staleCopy.time = 122
dofile(COPY_FILE)
check(staleCopy.outputs[#staleCopy.outputs]:find("NONE_OR_EXPIRED", 1, true) ~= nil, "expired result rejected")
check(rawget(_G, RESULT_KEY) == nil, "expired result consumed")

local backwardsCopy = setup()
backwardsCopy.tick(1.0, "ability", id)
backwardsCopy.tick(1.1, "ability", id)
backwardsCopy.tick(1.2, "ability", id)
backwardsCopy.time = 1.1
dofile(COPY_FILE)
check(backwardsCopy.outputs[#backwardsCopy.outputs]:find("NONE_OR_EXPIRED", 1, true) ~= nil, "backwards retrieval clock rejected")

-- A temporary frame-clock API failure must not destroy a completed result.
local retryCopy = setup()
retryCopy.tick(1.0, "ability", id)
retryCopy.tick(1.1, "ability", id)
retryCopy.tick(1.2, "ability", id)
local preservedCopyRecord = rawget(_G, RESULT_KEY)
check(type(preservedCopyRecord) == "table", "recoverable copy has a valid cached record")
local previousCopyClock = Inspect.Time.Frame
Inspect.Time.Frame = function() error("transient frame-clock fault") end
check(pcall(dofile, COPY_FILE), "clock-fault copy attempt must not throw")
check(rawget(_G, RESULT_KEY) == preservedCopyRecord, "clock-fault copy preserves result for retry")
check(retryCopy.outputs[#retryCopy.outputs]:find("BLOCKED_CLOCK_RETRY", 1, true) ~= nil,
  "clock-fault copy prints bounded retry instruction")
Inspect.Time.Frame = previousCopyClock
retryCopy.time = 2
check(pcall(dofile, COPY_FILE), "clock recovery permits copy retry")
check(retryCopy.outputs[#retryCopy.outputs]:find(id, 1, true) ~= nil,
  "clock recovery returns original validated candidate")
check(rawget(_G, RESULT_KEY) == nil, "successful retry consumes the cached record once")

local injected = setup()
rawget(_G, KEY).stop("MANUAL_CANCEL")
rawset(_G, RESULT_KEY, {schema=1, status="ABILITY_ID_CANDIDATE_UNVERIFIED_SOURCE", candidate="uPRIVATE", startedFrame=0, finishedFrame=0, detachConfirmed=true})
injected.time = 1
dofile(COPY_FILE)
check(injected.outputs[#injected.outputs]:find("NONE_OR_EXPIRED", 1, true) ~= nil, "malformed candidate cannot print")
check(table.concat(injected.outputs):find("uPRIVATE", 1, true) == nil, "malformed payload never exported")
check(rawget(_G, RESULT_KEY) == nil, "malformed record consumed")

-- Blocked re-runs must preserve the last completed evidence for Copy Output.
local blockedApiRerun = setup()
blockedApiRerun.tick(1.0, "ability", id)
blockedApiRerun.tick(1.1, "ability", id)
blockedApiRerun.tick(1.2, "ability", id)
local apiReceipt = rawget(_G, RESULT_KEY)
check(type(apiReceipt) == "table", "API-blocked rearm has a completed receipt")
Inspect.Tooltip = nil
check(pcall(dofile, FILE), "missing-API rerun executes safely")
check(blockedApiRerun.outputs[#blockedApiRerun.outputs]:find("BLOCKED_REQUIRED_API", 1, true) ~= nil,
  "missing-API rerun reports block")
check(rawget(_G, RESULT_KEY) == apiReceipt, "blocked required-API rerun keeps completed receipt")
local blockedClockRerun = setup()
blockedClockRerun.tick(1.0, "ability", id)
blockedClockRerun.tick(1.1, "ability", id)
blockedClockRerun.tick(1.2, "ability", id)
local clockReceipt = rawget(_G, RESULT_KEY)
check(type(clockReceipt) == "table", "clock-blocked rearm has a completed receipt")
Inspect.Time.Frame = function() return 0/0 end
check(pcall(dofile, FILE), "unavailable-clock rerun executes safely")
check(blockedClockRerun.outputs[#blockedClockRerun.outputs]:find("BLOCKED_CLOCK", 1, true) ~= nil,
  "unavailable-clock rerun reports block")
check(rawget(_G, RESULT_KEY) == clockReceipt, "blocked initial-clock rerun keeps completed receipt")

local rearmedCopy = setup()
rearmedCopy.tick(1.0, "ability", id)
rearmedCopy.tick(1.1, "ability", id)
rearmedCopy.tick(1.2, "ability", id)
check(type(rawget(_G, RESULT_KEY)) == "table", "completed result exists before rearm")
local staleHandler = rearmedCopy.handler
check(pcall(dofile, FILE), "rearm after terminal result")
check(rawget(_G, RESULT_KEY) == nil, "new Run invalidates stale result")
staleHandler()
check(rawget(_G, RESULT_KEY) == nil, "old completed callback cannot overwrite new Run")
rawget(_G, KEY).stop("MANUAL_CANCEL")

local rejectedCopy = setup({rejectDetach=true})
rejectedCopy.tick(1.0, "ability", id)
rejectedCopy.tick(1.1, "ability", id)
rejectedCopy.tick(1.2, "ability", id)
dofile(COPY_FILE)
check(rejectedCopy.outputs[#rejectedCopy.outputs]:find("DETACH_UNCONFIRMED", 1, true) ~= nil, "failed detach warning survives copy")

local timeoutCopy = setup()
timeoutCopy.tick(12.1, "unit", "uPRIVATE")
dofile(COPY_FILE)
check(timeoutCopy.outputs[#timeoutCopy.outputs]:find("TIMEOUT_NO_VALID_ID", 1, true) ~= nil, "noncandidate status copy")
check(timeoutCopy.outputs[#timeoutCopy.outputs]:find("uPRIVATE", 1, true) == nil, "noncandidate payload redacted")

_G.print = oldPrint
oldPrint("SC103_HOVER_PROBE_OFFLINE_TESTS_PASS " .. checks)
