-- SC-103: operator-run, one-shot copy of sanitized prior hover result.
-- Paste into already loaded LuaPad separately, after the hover probe completes.
-- No game input, SavedVariables writes, raw tooltip payloads or addon edits.
local STATE_KEY = "__RRE_SC103_HOVER_PROBE_20261103"
local RESULT_KEY = "__RRE_SC103_HOVER_RESULT_20261103"
local MAX_AGE_SECONDS = 120
local ALLOWED_STATUS = {
  ABILITY_ID_CANDIDATE_UNVERIFIED_SOURCE = true, TIMEOUT_NO_VALID_ID = true,
  TIMEOUT_FRAME_LIMIT = true, TOOLTIP_API_FAILURE = true, CLOCK_UNAVAILABLE = true,
  ATTACH_REJECTED = true, MANUAL_CANCEL = true, SUPERSEDED = true,
  CANCELLED = true
}

local function finite(n)
  return type(n) == "number" and n == n and n ~= math.huge and n ~= -math.huge
end
local function report(message)
  if type(print) == "function" then pcall(print, "RRE SC103 copy: " .. message) end
end

local live = rawget(_G, STATE_KEY)
if type(live) == "table" and rawget(live, "done") == false then
  report("PENDING; original hover probe is still active")
else
  local record = rawget(_G, RESULT_KEY)
  rawset(_G, RESULT_KEY, nil) -- consume once, including malformed or expired records
  local okNow, now = pcall(function() return Inspect.Time.Frame() end)
  local valid = false
  local status, candidate, detached
  if type(record) == "table" then
    status = rawget(record, "status")
    candidate = rawget(record, "candidate")
    detached = rawget(record, "detachConfirmed")
    local started = rawget(record, "startedFrame")
    local finished = rawget(record, "finishedFrame")
    valid = rawget(record, "schema") == 1 and ALLOWED_STATUS[status] == true and
      (detached == true or detached == false) and
      finite(started) and finite(finished) and okNow and finite(now) and
      finished >= started and now >= finished and now - finished <= MAX_AGE_SECONDS
    if status == "ABILITY_ID_CANDIDATE_UNVERIFIED_SOURCE" then
      valid = valid and type(candidate) == "string" and #candidate == 17 and
        candidate:match("^A[0-9A-F]+$") ~= nil
    else
      valid = valid and candidate == nil
    end
  end
  if valid then
    report(status .. " id=" .. (candidate or "UNKNOWN") ..
      (detached and "" or " DETACH_UNCONFIRMED"))
  else
    report("NONE_OR_EXPIRED")
  end
end

