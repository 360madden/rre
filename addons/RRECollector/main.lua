-- RRECollector v0.4.11: manual commands, SavedVariables, diagnostics and UI bootstrap.
-- No polling, game actions, process access, or dependencies on other addons.
local ADDON = "RRECollector"
local VERSION, SCHEMA = RRECollectorRuntime.VERSION, RRECollectorRuntime.SCHEMA
local say, finite = RRECollectorRuntime.core.say, RRECollectorRuntime.core.finite
local collect = RRECollectorRuntime.abilities.collect
local candidateLookup = RRECollectorRuntime.candidates.lookup
local candidateVersion = RRECollectorRuntime.candidateCatalog.version
local savedLoaded = false
local lastMessage = "waiting-for-saved-variables"
local MAX_AUTOMATIC_CANDIDATE_RETRIES = 2
local pendingContextRetry, automaticCandidateRetries = false, 0
local function refreshUI(clearChecks)
  local ui = RRECollectorRuntime.ui
  if type(ui) == "table" and type(ui.refresh) == "function" then
    pcall(ui.refresh, clearChecks)
  end
end

local function candidateStatus()
  local report = RRECollectorData.candidateLookup
  if type(report) ~= "table" then
    say("Static Warrior candidate lookup not yet recorded; /rre candidates.")
    local attempt = RRECollectorData.candidateAttempt
    if type(attempt) == "table" then
      say("Last candidate attempt " .. tostring(attempt.status or "?")
        .. ": " .. tostring(attempt.reason or "?") .. ".")
    end
    return
  end
  local c = report.counts or {}
  say("Candidate lookup #" .. tostring(report.sequence or "?")
    .. " " .. tostring(report.catalogVersion or "?")
    .. ": " .. tostring(c.listed or "?") .. " currently listed, "
    .. tostring(c.unlisted or "?") .. " unlisted, "
    .. tostring(c.unlistedReturned or 0) .. " unlisted returned by Detail.")
  say("Queries " .. tostring(c.queried or 0) .. ", policy "
    .. tostring(report.policy or "?") .. "; not a lock/learnability conclusion.")
end

local function status()
  if not savedLoaded then
    say("v" .. VERSION .. " saved data not loaded; capture unavailable.")
    return
  end
  local latest = RRECollectorData.latest
  if type(latest) ~= "table" then
    say("v" .. VERSION .. " ready; no snapshot. Use /rre capture.")
    candidateStatus()
    return
  end
  local list = latest.abilityList or {}
  local p = latest.player or {}
  say("v" .. VERSION .. " capture #" .. tostring(latest.sequence)
    .. " " .. tostring(p.name or "[name unknown]") .. " lvl "
    .. tostring(p.level or "?") .. " " .. tostring(p.calling or "?"))
  say("Known API IDs " .. tostring(list.uniqueCount or 0)
    .. " | details " .. tostring(list.detailCount or 0)
    .. " | failed " .. tostring(list.detailFailures or 0)
    .. " | ignored " .. tostring(list.ignored or 0)
    .. " | truncated " .. tostring(list.truncated or 0)
    .. " | complete " .. tostring(latest.captureComplete == true))
  say("Role slot " .. tostring(latest.roleSlot or "?")
    .. " | combat role " .. tostring(p.role or "?")
    .. " | saved on next normal UI reload/logout.")
  candidateStatus()
end

local function showPage(page)
  if not savedLoaded or type(RRECollectorData.latest) ~= "table" then
    say("No snapshot. Use /rre capture."); return
  end
  local records = RRECollectorData.latest.abilities or {}
  local totalPages = math.max(1, math.ceil(#records / 8))
  if not finite(page) or page < 1 or page > totalPages
    or page ~= math.floor(page) then
    say("Page must be 1-" .. tostring(totalPages)); return
  end
  say("Ability page " .. tostring(page) .. "/" .. tostring(totalPages))
  for i = (page - 1) * 8 + 1, math.min(page * 8, #records) do
    local entry = records[i]
    say(tostring(i) .. ". " .. tostring(entry.lookupId)
      .. " " .. tostring(entry.name or "[name unknown]"))
  end
end

local function help()
  say("v" .. VERSION .. " commands: /rre status | capture | probe | candidates | ui | page N | export | help")
  say("Current abilities in latest; explicit static-ID queries in candidateLookup. No casting.")
end

local function runCandidateLookup(trigger)
  if not savedLoaded then
    say("SavedVariables not ready; candidate lookup deferred.")
    return false
  end
  local ok, report, reason = pcall(candidateLookup)
  if not ok or type(report) ~= "table" or report.apiReady ~= true then
    local code = not ok and "lua-exception" or
      (type(reason) == "string" and #reason <= 80 and reason or "api-report-unavailable")
    lastMessage = "candidate-lookup-deferred"
    if trigger == "startup" then
      pendingContextRetry = code == "warrior-player-context-not-ready"
    elseif trigger == "manual" then
      pendingContextRetry = false
    end
    RRECollectorData.candidateAttempt = {
      schemaVersion = SCHEMA, addonVersion = VERSION, trigger = trigger,
      status = "deferred", reason = code,
      automaticRetries = automaticCandidateRetries
    }
    say("Candidate lookup " .. tostring(trigger) .. " deferred: "
      .. code .. "; previous records preserved.")
    refreshUI(false)
    return false
  end
  -- API readiness is necessary but not sufficient: reject unusable Detail batches.
  -- Keep a previously recorded catalog and its sequence byte-for-byte intact.
  local counts = report.counts
  local function validCount(value)
    return type(value) == "number" and value == value
      and value >= 0 and value < math.huge
      and value == math.floor(value)
  end
  local countersValid = type(counts) == "table"
    and validCount(counts.queried) and counts.queried > 0
    and validCount(counts.errors) and validCount(counts.inconclusiveTables)
    and counts.errors + counts.inconclusiveTables <= counts.queried
  local rejectedStatus, rejectedReason
  if not countersValid then
    rejectedStatus, rejectedReason = "incomplete", "detail-invalid-counts"
  elseif counts.errors > 0 then
    if counts.errors == counts.queried then
      rejectedStatus, rejectedReason = "failed", "detail-all-error"
    else
      rejectedStatus, rejectedReason = "incomplete", "detail-partial-error"
    end
  elseif counts.inconclusiveTables == counts.queried then
    rejectedStatus, rejectedReason = "incomplete", "detail-all-inconclusive"
  end
  if rejectedReason then
    pendingContextRetry = false
    lastMessage = "candidate-lookup-" .. rejectedStatus
    RRECollectorData.candidateAttempt = {
      schemaVersion = SCHEMA, addonVersion = VERSION, trigger = trigger,
      status = rejectedStatus, reason = rejectedReason,
      automaticRetries = automaticCandidateRetries
    }
    say("Candidate lookup " .. tostring(trigger) .. " " .. rejectedStatus
      .. ": " .. rejectedReason .. "; previous records preserved.")
    refreshUI(false)
    return false
  end
  pendingContextRetry = false
  local sequence = (type(RRECollectorData.candidateSequence) == "number"
    and RRECollectorData.candidateSequence or 0) + 1
  report.sequence = sequence
  report.trigger = trigger
  RRECollectorData.candidateLookup = report
  RRECollectorData.candidateSequence = sequence
  RRECollectorData.candidateAttempt = {
    schemaVersion = SCHEMA, addonVersion = VERSION, trigger = trigger,
    status = "recorded", reason = "none",
    automaticRetries = automaticCandidateRetries
  }
  lastMessage = "candidate-lookup-recorded"
  local c = report.counts or {}
  say("Candidate lookup #" .. tostring(sequence) .. " " .. tostring(trigger)
    .. ": " .. tostring(c.listed or 0) .. " listed / "
    .. tostring(c.unlisted or 0) .. " unlisted; "
    .. tostring(c.unlistedReturned or 0) .. " unlisted details returned; "
    .. tostring(c.queried or 0) .. " bounded Detail calls.")
  say("Separate candidateLookup recorded in memory; normal UI reload/logout flushes SavedVariables.")
  refreshUI(false)
  return true
end

-- At most two event-driven automatic retries after the exact startup context deferral.
-- No frame polling, casting, or action queue input; manual Retry remains available.
local function retryDeferredCandidateLookup(trigger)
  if not savedLoaded or not pendingContextRetry
    or automaticCandidateRetries >= MAX_AUTOMATIC_CANDIDATE_RETRIES then return end
  automaticCandidateRetries = automaticCandidateRetries + 1
  pendingContextRetry = false
  if not runCandidateLookup(trigger) and
    automaticCandidateRetries < MAX_AUTOMATIC_CANDIDATE_RETRIES then
    local attempt = RRECollectorData.candidateAttempt
    pendingContextRetry = type(attempt) == "table"
      and attempt.reason == "warrior-player-context-not-ready"
  end
end

-- RC27-CAPTURE-BEGIN
-- Transient API/context failures must never replace a complete prior catalog.
local function recordCapture()
  if not savedLoaded then
    say("SavedVariables not ready; retry after initialization.")
    return
  end
  local captureOk, record = pcall(collect)
  if not captureOk or type(record) ~= "table"
    or type(record.abilityList) ~= "table"
    or record.abilityList.apiAvailable ~= true then
    lastMessage = "capture-error"
    say("Capture unavailable; prior ability snapshot preserved.")
    return
  end
  local prior = RRECollectorData.latest
  if type(prior) == "table" and prior.captureComplete == true
    and record.captureComplete ~= true then
    lastMessage = "capture-incomplete-preserved"
    say("Capture incomplete; previous complete ability snapshot preserved.")
    return
  end
  RRECollectorData.latest = record
  RRECollectorData.sequence = record.sequence
  lastMessage = record.captureComplete and "capture-complete" or "capture-partial"
  say("Capture " .. lastMessage .. ": " ..
    tostring(record.abilityList.uniqueCount) .. " IDs, " ..
    tostring(record.abilityList.detailCount) ..
    " details. /rre status; /reloadui to save.")
  refreshUI(true)
end
-- RC27-CAPTURE-END

local function onSlash(_, raw)
  local ok, failure = pcall(function()
    local value = type(raw) == "string" and raw:lower() or ""
    if #value > 80 then say("Command too long."); return end
    local action, argument = value:match("^%s*(%S*)%s*(%S*)%s*$")
    if action == nil then say("Use /rre help."); return end
    if action == "" or action == "help" then
      help()
    elseif action == "status" then
      status()
    elseif action == "probe" then
      if not savedLoaded then
        say("SavedVariables not ready; retry after initialization.")
        return
      end
      local probeOk, report = pcall(RRECollectorRuntime.capabilities.probe)
      if not probeOk or type(report) ~= "table" then
        lastMessage = "probe-error"
        say("Probe failed safely; prior ability and probe snapshots preserved.")
        return
      end
      local nextProbe = (type(RRECollectorData.probeSequence) == "number"
        and RRECollectorData.probeSequence or 0) + 1
      report.sequence = nextProbe
      RRECollectorData.probe = report
      RRECollectorData.probeSequence = nextProbe
      lastMessage = "probe-recorded"
      local index = report.index or {}
      say("API probe #" .. tostring(nextProbe) .. ": documentation "
        .. tostring(report.documentationStatus) .. ", matching names "
        .. tostring(index.retained or 0) .. ", doc errors "
        .. tostring(report.documentErrors or 0) .. ".")
      say("Probe saved separately in RRECollectorData.probe after normal /reloadui/logout; current known ability snapshot unchanged.")
    elseif action == "candidates" then
      runCandidateLookup("manual")
    elseif action == "ui" then
      local ui = RRECollectorRuntime.ui
      if type(ui) ~= "table" or type(ui.toggle) ~= "function" then
        say("Toolbar module unavailable; slash commands still work.")
      else
        local toggled, shown = pcall(ui.toggle)
        if not toggled or shown == false then say("Toolbar could not be toggled.") end
      end
    elseif action == "capture" then
      recordCapture()
    elseif action == "page" then
      showPage(tonumber(argument))
    elseif action == "export" then
      say("Full snapshot stored in character SavedVariables: RRECollectorData.latest.")
      say("Separate research receipts: RRECollectorData.probe and .candidateLookup.")
      say("Use a normal /reloadui or logout to flush; /rre page N previews 8 names.")
    else
      say("Unknown command. Use /rre help.")
    end
  end)
  if not ok then
    lastMessage = "command-error"
    say("Command error. Use /rre status; no game action was sent.")
  end
end

-- UI buttons reuse the same guarded slash-command behavior; no game casts.
RRECollectorRuntime.command = function(raw) onSlash(nil, raw) end

local slashOk, slashResult = pcall(function()
  local event = Command.Slash.Register("rre")
  if type(event) ~= "table" then return false end
  Command.Event.Attach(event, onSlash, "RRECollector.Slash")
  return true
end)
if not slashOk or not slashResult then
  lastMessage = "slash-unavailable"
  say("Slash command registration failed.")
end

-- Both events are present in the documented RIFT addon API and installed addons.
-- Startup.End can follow SavedVariables.Load.End; Unit.Availability.Full is
-- consulted only for the player specifier. Both are no-ops after success/limit.
local startupEnd = type(Event) == "table" and Event.Addon
  and Event.Addon.Startup and Event.Addon.Startup.End
if startupEnd then
  pcall(Command.Event.Attach, startupEnd, function()
    retryDeferredCandidateLookup("auto-startup-end")
  end, "RRECollector.CandidateStartupRetry")
end
local playerFull = type(Event) == "table" and Event.Unit
  and Event.Unit.Availability and Event.Unit.Availability.Full
if playerFull then
  pcall(Command.Event.Attach, playerFull, function(_, units)
    if not pendingContextRetry or type(units) ~= "table" then return end
    for _, specifier in pairs(units) do
      if specifier == "player" then
        retryDeferredCandidateLookup("auto-player-full")
        return
      end
    end
  end, "RRECollector.CandidatePlayerRetry")
end

local savedEvent = type(Event) == "table" and Event.Addon
  and Event.Addon.SavedVariables and Event.Addon.SavedVariables.Load
  and Event.Addon.SavedVariables.Load.End
if savedEvent then
  local attached = pcall(Command.Event.Attach, savedEvent, function(_, identifier)
    if identifier ~= ADDON or savedLoaded then return end
    if type(RRECollectorData) ~= "table" then RRECollectorData = {} end
    RRECollectorData.schemaVersion = SCHEMA
    RRECollectorData.addonVersion = VERSION
    savedLoaded = true
    lastMessage = "ready"
    say("v" .. VERSION .. " ready. /rre status")
    local prior = RRECollectorData.candidateLookup
    local priorCounts = type(prior) == "table" and prior.counts or nil
    local queried = type(priorCounts) == "table" and priorCounts.queried or nil
    local errors = type(priorCounts) == "table" and priorCounts.errors or nil
    local inconclusive = type(priorCounts) == "table"
      and priorCounts.inconclusiveTables or nil
    -- Backward-compatible older cached reports may omit this newer counter.
    if inconclusive == nil then inconclusive = 0 end
    local function validSavedCount(value)
      return type(value) == "number" and value == value
        and value >= 0 and value < math.huge
        and value == math.floor(value)
    end
    if type(prior) == "table" and prior.catalogVersion == candidateVersion
      and prior.apiReady == true
      and validSavedCount(queried) and queried > 0
      and validSavedCount(errors) and errors < queried
      and validSavedCount(inconclusive) and inconclusive < queried
      and errors + inconclusive < queried then
      say("Prior candidate lookup retained for this catalog; /rre candidates to refresh.")
    else
      runCandidateLookup("startup")
    end
    local ui = RRECollectorRuntime.ui
    if type(ui) == "table" and type(ui.start) == "function" then
      local uiOk, started = pcall(ui.start)
      if not uiOk or started == false then
        say("Toolbar not available; /rre status remains functional.")
      end
    end
  end, "RRECollector.SavedVariables")
  if not attached then
    lastMessage = "saved-event-unavailable"
    say("SavedVariables event attachment failed.")
  end
else
  lastMessage = "saved-event-missing"
  say("SavedVariables API unavailable.")
end
