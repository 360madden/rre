-- SC-103: bounded manual LuaPad tooltip-ID candidate probe, source-only stage.
-- Paste into already-loaded LuaPad and click Run only as a separate operator action.
-- Does not cast, click, move, change roles, modify addons, or write SavedVariables.
-- A returned ID is a hovered ability-shaped *candidate*, NOT a Legendary selector.
local STATE_KEY = "__RRE_SC103_HOVER_PROBE_20261103"
local RESULT_KEY = "__RRE_SC103_HOVER_RESULT_20261103"
local QUARANTINE_KEY = "__RRE_SC103_HOVER_DETACH_QUARANTINE_20261103"
local LABEL = "RRE_SC103_HOVER_PROBE_20261103"
local WINDOW_SECONDS = 12
local MAX_STALLED_FRAMES = 900
local REQUIRED_STABLE_FRAMES = 3
local INITIAL_SETTLE_SECONDS = 0.6
local RECORDABLE_STATUS = {
  ABILITY_ID_CANDIDATE_UNVERIFIED_SOURCE = true, TIMEOUT_NO_VALID_ID = true,
  TIMEOUT_FRAME_LIMIT = true, TOOLTIP_API_FAILURE = true, CLOCK_UNAVAILABLE = true,
  ATTACH_REJECTED = true, MANUAL_CANCEL = true, SUPERSEDED = true,
  CANCELLED = true
}

local previous = rawget(_G, STATE_KEY)
if type(previous) == "table" and type(previous.stop) == "function" then
  pcall(previous.stop, "SUPERSEDED")
end
local quarantined = rawget(_G, QUARANTINE_KEY) == true

local canRun =
  type(Inspect) == "table" and type(Inspect.Tooltip) == "function" and
  type(Inspect.Time) == "table" and type(Inspect.Time.Frame) == "function" and
  type(Command) == "table" and type(Command.Event) == "table" and
  type(Command.Event.Attach) == "function" and
  type(Command.Event.Detach) == "function" and
  type(Event) == "table" and type(Event.System) == "table" and
  type(Event.System.Update) == "table" and Event.System.Update.Begin ~= nil

local function notice(message)
  if type(print) == "function" then
    pcall(print, "RRE SC103 hover: " .. message)
  end
end

if quarantined then
  notice("BLOCKED_UNCONFIRMED_DETACH; reload UI before another Run")
elseif not canRun then
  notice("BLOCKED_REQUIRED_API; no listener installed")
else
  local okClock, start = pcall(Inspect.Time.Frame)
  if not okClock or type(start) ~= "number" or start ~= start or
     start == math.huge or start == -math.huge then
    notice("BLOCKED_CLOCK; no listener installed")
  else
    local update = Event.System.Update.Begin
    local state = {
      done = false, attached = false, stalledFrames = 0, lastClock = start,
      failures = 0, lastId = nil, stable = 0
    }
    local onFrame
    local function complete(reason, candidate)
      if state.done then return end
      state.done = true
      local detached = true
      if state.attached then
        local okDetach, result = pcall(Command.Event.Detach, update, onFrame, LABEL)
        detached = okDetach and result ~= false
        if not detached then rawset(_G, QUARANTINE_KEY, true) end -- Fail closed until UI reload.
      end
      local ownsSlot = rawget(_G, STATE_KEY) == state
      if ownsSlot then
        rawset(_G, STATE_KEY, nil)
        -- Retain fixed statuses, exact ability-shaped scalars and finite frame times only.
        -- Never retain raw tooltip payloads, unit IDs or callback errors.
        if RECORDABLE_STATUS[reason] then
          local okFinish, finished = pcall(Inspect.Time.Frame)
          local finishValid = okFinish and type(finished) == "number" and finished == finished and
             finished ~= math.huge and finished ~= -math.huge and finished >= state.lastClock
          if not finishValid then
            reason, candidate = "CLOCK_UNAVAILABLE", nil
          end
          if finishValid then
            local safeId = nil
            if reason == "ABILITY_ID_CANDIDATE_UNVERIFIED_SOURCE" and
               type(candidate) == "string" and #candidate == 17 and
               candidate:match("^A[0-9A-Fa-f]+$") then safeId = candidate:upper() end
            if reason ~= "ABILITY_ID_CANDIDATE_UNVERIFIED_SOURCE" or safeId then
              rawset(_G, RESULT_KEY, {
                schema = 1, status = reason, candidate = safeId,
                startedFrame = start, finishedFrame = finished, detachConfirmed = detached
              })
            end
          end
        end
      end
      local detail = candidate and (" id=" .. candidate) or " id=UNKNOWN"
      notice(reason .. detail .. (detached and "" or " DETACH_UNCONFIRMED"))
    end
    state.stop = function(reason)
      complete(reason or "CANCELLED", nil)
    end

    onFrame = function()
      if state.done then return end
      local okTime, now = pcall(Inspect.Time.Frame)
      if not okTime or type(now) ~= "number" or now ~= now or
         now == math.huge or now == -math.huge or now < start or now < state.lastClock then
        complete("CLOCK_UNAVAILABLE"); return
      end
      if now - start >= WINDOW_SECONDS then complete("TIMEOUT_NO_VALID_ID"); return end
      -- A high-FPS client must not lose its 12-second observation window.
      -- Only a frame clock that stays frozen for 900 callbacks trips the guard.
      if now > state.lastClock then
        state.lastClock = now
        state.stalledFrames = 0
      else
        state.stalledFrames = state.stalledFrames + 1
        if state.stalledFrames >= MAX_STALLED_FRAMES then complete("TIMEOUT_FRAME_LIMIT"); return end
      end
      if now - start < INITIAL_SETTLE_SECONDS then return end

      -- NEVER stringify or export non-ability tooltip payloads.
      local okTooltip, kind, shown = pcall(Inspect.Tooltip)
      if not okTooltip then
        -- A failed read interrupts any previously matched sequence.
        state.failures = state.failures + 1
        state.lastId = nil
        state.stable = 0
        if state.failures >= 3 then complete("TOOLTIP_API_FAILURE") end
        return
      end
      local candidate = nil
      if kind == "ability" and type(shown) == "string" and
         #shown == 17 and shown:match("^A[0-9A-Fa-f]+$") then
        candidate = shown:upper()
      end
      if candidate == nil then
        state.lastId = nil
        state.stable = 0
        return
      end
      if state.lastId == candidate then
        state.stable = state.stable + 1
      else
        state.lastId = candidate
        state.stable = 1
      end
      if state.stable >= REQUIRED_STABLE_FRAMES then
        complete("ABILITY_ID_CANDIDATE_UNVERIFIED_SOURCE", candidate)
      end
    end

    rawset(_G, RESULT_KEY, nil) -- Only a ready-to-arm Run invalidates the previous receipt.
    rawset(_G, STATE_KEY, state)
    local okAttach, attached = pcall(Command.Event.Attach, update, onFrame, LABEL)
    if not okAttach or attached == false then
      complete("ATTACH_REJECTED")
    else
      state.attached = true
      notice("ARMED_12_SECONDS; hover native Protector's Fury only")
    end
  end
end
