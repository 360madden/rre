-- RC-32 pre-gate RED fixture. Source-extracts the real handler; no game/addon writes.
-- Run with --expect-red against frozen v0.4.10; --require-fixed after a later authorized fix.
local f = assert(io.open("addons/RRECollector/main.lua", "rb"))
local src = f:read("*a"); f:close()
local section = assert(src:match("(local function runCandidateLookup%(trigger%).-)\n%-%- At most two event%-driven"),
  "candidate handler extraction failed (inspect source before updating fixture)")
local prefix = [==[
local savedLoaded, lastMessage = true, "ready"
local automaticCandidateRetries, pendingContextRetry = 0, false
local candidateVersion, SCHEMA, VERSION = "test-catalog", 1, "0.4.10"
local notes, refreshes = {}, 0
local function say(s) notes[#notes + 1] = tostring(s) end
local function refreshUI() refreshes = refreshes + 1 end
local nextReport, RRECollectorData
local function candidateLookup() return nextReport end
]==]
local suffix = [==[
local function report(queried, errors, noDetail)
  local entries = {}
  for i = 1, 96 do entries[i] = {id = string.format("A%016X", i)} end
  return {schemaVersion = 1, addonVersion = VERSION, catalogVersion = candidateVersion,
    apiReady = true, entries = entries,
    counts = {catalog = 96, listed = 39, unlisted = 57, queried = queried,
      errors = errors, noDetail = noDetail or 0, returned = queried-errors-(noDetail or 0),
      unlistedReturned = 0, skipped = 96-queried}}
end
local failures, checks = 0, 0
local function check(why, condition)
  checks = checks + 1
  if not condition then failures = failures + 1; print("RED " .. why)
  else print("PASS " .. why) end
end
local function reset(prior)
  local old = prior and report(9, 0, 3) or nil
  local latest, probe, toolbar = {magic="latest"}, {magic="probe"}, {magic="toolbar"}
  RRECollectorData = {candidateLookup=old, candidateSequence=prior and 7 or 0,
    latest=latest, probe=probe, toolbarSlots=toolbar}
  notes, refreshes, lastMessage = {}, 0, "ready"
  return old, latest, probe, toolbar
end
local function unchanged(latest, probe, toolbar)
  return RRECollectorData.latest == latest and RRECollectorData.probe == probe
    and RRECollectorData.toolbarSlots == toolbar
end
local old, latest, probe, toolbar = reset(true)
nextReport = report(9, 9)
runCandidateLookup("manual")
check("all-error preserves useful prior", RRECollectorData.candidateLookup == old
  and RRECollectorData.candidateSequence == 7
  and RRECollectorData.candidateAttempt.status ~= "recorded"
  and unchanged(latest, probe, toolbar))
old, latest, probe, toolbar = reset(true)
nextReport = report(9, 2)
runCandidateLookup("manual")
check("partial-error preserves useful prior", RRECollectorData.candidateLookup == old
  and RRECollectorData.candidateSequence == 7
  and RRECollectorData.candidateAttempt.status ~= "recorded"
  and unchanged(latest, probe, toolbar))
old, latest, probe, toolbar = reset(false)
nextReport = report(9, 9)
runCandidateLookup("manual")
check("all-error without prior not successful", RRECollectorData.candidateAttempt.status ~= "recorded"
  and unchanged(latest, probe, toolbar))
old, latest, probe, toolbar = reset(false)
nextReport = report(9, 2)
runCandidateLookup("manual")
check("partial-error without prior classified incomplete", RRECollectorData.candidateAttempt.status ~= "recorded"
  and unchanged(latest, probe, toolbar))
old, latest, probe, toolbar = reset(true)
nextReport = report(9, 0, 9)
local noDetail = nextReport
runCandidateLookup("manual")
check("error-free no-detail can replace", RRECollectorData.candidateLookup == noDetail
  and RRECollectorData.candidateSequence == 8
  and unchanged(latest, probe, toolbar))
old, latest, probe, toolbar = reset(true)
nextReport = report(9, 0)
local positive = nextReport
runCandidateLookup("manual")
check("successful lookup advances", RRECollectorData.candidateLookup == positive
  and RRECollectorData.candidateSequence == 8
  and unchanged(latest, probe, toolbar))
old, latest, probe, toolbar = reset(true)
nextReport = nil
runCandidateLookup("manual")
check("deferred failure preserves prior", RRECollectorData.candidateLookup == old
  and RRECollectorData.candidateSequence == 7
  and RRECollectorData.candidateAttempt.status == "deferred"
  and unchanged(latest, probe, toolbar))
local expectRed = type(arg) == "table" and arg[1] == "--expect-red"
if expectRed then
  assert(failures == 4, "expected exactly four frozen-source defects; observed " .. failures)
  print("EXPECTED_RED_RC32_CANDIDATES " .. failures .. "/7 scenarios; no addon changes")
else
  assert(failures == 0, "RC32 candidate protection not yet implemented (" .. failures .. " defects)")
  print("PASS_RC32_CANDIDATES " .. checks .. " scenarios")
end
]==]
assert((loadstring or load)(prefix .. section .. suffix, "RC32 candidate preservation"))()
