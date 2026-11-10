-- RRECollector v0.4.16: manual commands, SavedVariables, diagnostics and UI bootstrap.
-- No polling, game actions, process access, or dependencies on other addons.
local ADDON = "RRECollector"
local VERSION, SCHEMA = RRECollectorRuntime.VERSION, RRECollectorRuntime.SCHEMA
local say, finite = RRECollectorRuntime.core.say, RRECollectorRuntime.core.finite
local collect = RRECollectorRuntime.abilities.collect
local wire = RRECollectorRuntime.wire
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
  local latest = RRECollectorData.latest
  local player = type(latest) == "table" and latest.player or nil
  local calling = type(player) == "table" and player.calling or nil
  if type(calling) == "string" and not calling:lower():find("warrior", 1, true) then
    say("Static candidate research is Warrior-only; not applicable to " .. calling .. ".")
    return
  end
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
  local c = type(report.counts) == "table" and report.counts or {}
  say("Candidate lookup #" .. tostring(report.sequence or "?")
    .. " " .. tostring(report.catalogVersion or "?")
    .. ": " .. tostring(c.listed or "?") .. " currently listed, "
    .. tostring(c.unlisted or "?") .. " unlisted, "
    .. tostring(c.unlistedReturned or 0) .. " unlisted returned by Detail.")
  say("Queries " .. tostring(c.queried or 0) .. ", policy "
    .. tostring(report.policy or "?") .. "; not a lock/learnability conclusion.")
end

local function savedSnapshotComplete(latest)
  if type(latest) ~= "table" or latest.captureComplete ~= true
    or type(latest.abilityList) ~= "table"
    or type(latest.player) ~= "table"
    or type(latest.abilities) ~= "table" then return false end
  local list, count = latest.abilityList, #latest.abilities
  if count < 1 or count > 512 or list.uniqueCount ~= count
    or list.detailCount ~= count or list.detailFailures ~= 0
    or list.apiAvailable ~= true or list.enumerationComplete ~= true
    or list.ignored ~= 0 or list.truncated ~= 0
    or type(latest.player.calling) ~= "string" then return false end
  local seen = {}
  for i = 1, count do
    local item = rawget(latest.abilities, i)
    local id = type(item) == "table" and item.lookupId or nil
    if type(id) ~= "string" or #id ~= 17
      or not id:match("^A[0-9A-F]+$") or seen[id] then return false end
    seen[id] = true
  end
  return true
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
  local list = type(latest.abilityList) == "table" and latest.abilityList or {}
  local p = type(latest.player) == "table" and latest.player or {}
  -- A previous capture survives addon updates; identify it by its saved version.
  local captureVersion = type(latest.addonVersion) == "string"
    and latest.addonVersion:match("^%d+%.%d+%.%d+$")
    and latest.addonVersion or "unknown"
  local versionNote = captureVersion ~= VERSION
    and (" | loaded v" .. VERSION) or ""
  say("v" .. captureVersion .. " capture #" .. tostring(latest.sequence)
    .. " " .. tostring(p.name or "[name unknown]") .. " lvl "
    .. tostring(p.level or "?") .. " " .. tostring(p.calling or "?")
    .. versionNote)
  say("Known API IDs " .. tostring(list.uniqueCount or 0)
    .. " | details " .. tostring(list.detailCount or 0)
    .. " | failed " .. tostring(list.detailFailures or 0)
    .. " | ignored " .. tostring(list.ignored or 0)
    .. " | truncated " .. tostring(list.truncated or 0)
    .. " | complete " .. tostring(savedSnapshotComplete(latest)))
  say("Role slot " .. tostring(latest.roleSlot or "?")
    .. " | combat role " .. tostring(p.role or "?")
    .. " | saved on next normal UI reload/logout.")
  -- A retained SavedVariables publication receipt can outlive the Lua frames.
  -- Report ONLY the transient current-load receipt as live publication status.
  local publication = type(wire) == "table" and type(wire.receipt) == "function"
    and wire.receipt() or nil
  if type(publication) == "table" and publication.status == "complete" then
    say("Current-load RREC2 published: seq=" .. tostring(publication.sequence)
      .. " parts=" .. tostring(publication.parts) .. ".")
  else
    say("Current-load RREC2 not published: " .. tostring(type(publication) == "table"
      and publication.reason or "no capture this UI load")
      .. "; saved API capture and wire publication are separate.")
  end
  candidateStatus()
end

local function showPage(page)
  if not savedLoaded or type(RRECollectorData.latest) ~= "table" then
    say("No snapshot. Use /rre capture."); return
  end
  local records = RRECollectorData.latest.abilities
  if type(records) ~= "table" then
    say("Saved ability list malformed; /rre capture."); return
  end
  local totalPages = math.max(1, math.ceil(#records / 8))
  if not finite(page) or page < 1 or page > totalPages
    or page ~= math.floor(page) then
    say("Page must be 1-" .. tostring(totalPages)); return
  end
  say("Ability page " .. tostring(page) .. "/" .. tostring(totalPages))
  for i = (page - 1) * 8 + 1, math.min(page * 8, #records) do
    local entry = records[i]
    if type(entry) ~= "table" then
      say("Saved ability record malformed; /rre capture."); return
    end
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
    local notApplicable = code == "warrior-catalog-not-applicable"
    lastMessage = notApplicable and "candidate-lookup-not-applicable"
      or "candidate-lookup-deferred"
    if trigger == "startup" then
      pendingContextRetry = code == "warrior-player-context-not-ready"
    elseif trigger == "manual" then
      pendingContextRetry = false
    end
    RRECollectorData.candidateAttempt = {
      schemaVersion = SCHEMA, addonVersion = VERSION, trigger = trigger,
      status = notApplicable and "not-applicable" or "deferred", reason = code,
      automaticRetries = automaticCandidateRetries
    }
    if notApplicable then
      say("Warrior-only candidate catalog not applicable to this calling; /rre capture works across callings.")
    else
      say("Candidate lookup " .. tostring(trigger) .. " deferred: "
        .. code .. "; previous records preserved.")
    end
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
    and validCount(counts.listed)
    and validCount(counts.errors) and validCount(counts.inconclusiveTables)
    and validCount(counts.noDetail) and validCount(counts.returned)
    and validCount(counts.listedControlQueried) and counts.listedControlQueried <= 1
    and counts.listedControlQueried == (counts.listed > 0 and 1 or 0)
    and validCount(counts.listedControlReturned)
    and counts.listedControlReturned <= counts.listedControlQueried
    and counts.errors + counts.inconclusiveTables + counts.noDetail
      + counts.returned == counts.queried
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
  elseif counts.returned == 0 then
    rejectedStatus, rejectedReason = "incomplete", "detail-no-positive-result"
  elseif counts.listedControlQueried > 0 and counts.listedControlReturned == 0 then
    rejectedStatus, rejectedReason = "incomplete", "detail-listed-control-unverified"
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
  if type(wire) == "table" then wire.beginAttempt() end
  if not savedLoaded then
    if type(wire) == "table" then wire.abort("saved-not-ready") end
    say("SavedVariables not ready; retry after initialization.")
    return
  end
  local captureOk, record = pcall(collect)
  if not captureOk or type(record) ~= "table"
    or type(record.abilityList) ~= "table"
    or record.abilityList.apiAvailable ~= true then
    lastMessage = "capture-error"
    if type(wire) == "table" then RRECollectorData.memoryPublication = wire.abort("api-capture-error") end
    say("Capture unavailable; prior ability snapshot preserved.")
    return
  end
  local prior = RRECollectorData.latest
  if savedSnapshotComplete(prior) and record.captureComplete ~= true then
    lastMessage = "capture-incomplete-preserved"
    if type(wire) == "table" then RRECollectorData.memoryPublication = wire.abort("capture-incomplete") end
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
  if type(wire) == "table" then
    local publication = wire.publish(record)
    RRECollectorData.memoryPublication = publication
    if publication.status == "complete" then
      say("Wire RREC2 session=" .. publication.session .. " seq=" .. tostring(publication.sequence)
        .. " parts=" .. tostring(publication.parts) .. " bytes=" .. tostring(publication.payloadBytes))
    else say("Wire not published: " .. tostring(publication.reason or "unknown")) end
  end
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
      if not savedLoaded then
        say("SavedVariables not ready; no capture available to export.")
        return
      end
      local latest = RRECollectorData.latest
      if type(latest) ~= "table" then
        say("No snapshot to export. Use /rre capture first.")
        return
      end
      if not savedSnapshotComplete(latest) then
        say("Snapshot incomplete; use /rre capture to collect a complete one.")
        return
      end
      local captureVersion = type(latest.addonVersion) == "string"
        and latest.addonVersion:match("^%d+%.%d+%.%d+$")
        and latest.addonVersion or "unknown"
      say("Complete v" .. captureVersion .. " capture #" .. tostring(latest.sequence or "?")
        .. " held in RRECollectorData.latest (loaded addon v" .. VERSION .. ").")
      say("Separate research receipts: RRECollectorData.probe and .candidateLookup.")
      say("Use a normal /reloadui or logout to save; /rre page N previews 8 names.")
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
    if type(wire) == "table" then RRECollectorData.memoryPublication = wire.receipt() end
    savedLoaded = true
    lastMessage = "ready"
    say("v" .. VERSION .. " ready. /rre status")
    local prior = RRECollectorData.candidateLookup
    local priorCounts = type(prior) == "table" and prior.counts or nil
    local queried = type(priorCounts) == "table" and priorCounts.queried or nil
    local errors = type(priorCounts) == "table" and priorCounts.errors or nil
    local inconclusive = type(priorCounts) == "table"
      and priorCounts.inconclusiveTables or nil
    local noDetail = type(priorCounts) == "table" and priorCounts.noDetail or nil
    local returned = type(priorCounts) == "table" and priorCounts.returned or nil
    local listed = type(priorCounts) == "table" and priorCounts.listed or nil
    local controlQueried = type(priorCounts) == "table"
      and priorCounts.listedControlQueried or nil
    local controlReturned = type(priorCounts) == "table"
      and priorCounts.listedControlReturned or nil
    -- Retain backward-compatible missing inconclusive count; missing positive
    -- control evidence requires a fresh source-only probe, not a cached success.
    if inconclusive == nil then inconclusive = 0 end
    local function validSavedCount(value)
      return type(value) == "number" and value == value
        and value >= 0 and value < math.huge
        and value == math.floor(value)
    end
    if type(prior) == "table" and prior.catalogVersion == candidateVersion
      and prior.apiReady == true
      and validSavedCount(queried) and queried > 0
      and validSavedCount(errors) and errors == 0
      and validSavedCount(inconclusive) and inconclusive < queried
      and validSavedCount(noDetail) and validSavedCount(returned) and returned > 0
      and validSavedCount(listed)
      and validSavedCount(controlQueried) and controlQueried <= 1
      and controlQueried == (listed > 0 and 1 or 0)
      and validSavedCount(controlReturned) and controlReturned == controlQueried
      and errors + inconclusive + noDetail + returned == queried then
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
