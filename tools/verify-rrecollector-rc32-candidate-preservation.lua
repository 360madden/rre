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
  -- Mirror candidates.lua's 39 listed + 57 unlisted shape and query policy.
  -- A positive unlisted canary expands to all 57 unlisted IDs; no-positive
  -- attempts stop after one listed control and eight unlisted canaries.
  noDetail = noDetail or 0
  local returned = queried - errors - noDetail
  assert((queried == 9 or queried == 58) and returned >= 0)
  if queried == 9 then assert(returned <= 1, "unlisted positive requires expansion") end
  local entries, canaryIds = {}, {}
  local screenshots = {
    "AFDD9D7E2A8F0E50B", "A768CF3B63EE8D6ED", "AFA78C0D582C9F2E5",
    "A37397DC597DDAF03", "A0E2112FD6FE262EE", "A411792DB5CF7E0E4"
  }
  local remainingReturned, remainingNoDetail, remainingErrors = returned, noDetail, errors
  for i = 1, 96 do
    local listed = i <= 39
    local item = {
      id = screenshots[i - 39] or string.format("A%016X", i),
      name = "Synthetic ability " .. i,
      soul = i >= 40 and i <= 45 and "Paladin"
        or i == 46 and "VoidKnight" or i == 47 and "Paragon"
        or (i % 2 == 0 and "Reaver" or "Warlord"),
      category = "synthetic-test", listed = listed,
      status = listed and "listed-not-queried" or "not-attempted-canary-stop"
    }
    local queriedHere = i == 1 or (i >= 40 and i < 40 + queried - 1)
    if queriedHere then
      item.phase = listed and "listed-control"
        or (i <= 47 and "unlisted-canary" or "unlisted-expansion")
      if remainingReturned > 0 then
        item.status, item.detail = "returned", {name = item.name}
        remainingReturned = remainingReturned - 1
      elseif remainingNoDetail > 0 then
        item.status = "no-detail"
        remainingNoDetail = remainingNoDetail - 1
      else
        assert(remainingErrors > 0)
        item.status = "lookup-error"
        remainingErrors = remainingErrors - 1
      end
    end
    entries[i] = item
    if i >= 40 and i <= 47 then canaryIds[#canaryIds + 1] = item.id end
  end
  assert(remainingReturned == 0 and remainingNoDetail == 0 and remainingErrors == 0)
  if queried == 58 then assert(entries[40].status == "returned") end
  local unlistedQueried, listedReturned = queried - 1,
    (entries[1].status == "returned" and 1 or 0)
  return {
    schemaVersion = 1, addonVersion = VERSION, catalogVersion = candidateVersion,
    source = "synthetic-producer-shaped", scope = "static-candidates-explicit-ID-test",
    apiReady = true, listRawCount = 39, listUniqueCount = 39,
    entries = entries, canaryIds = canaryIds,
    policy = queried == 58 and "positive-canary-expanded-to-other-unlisted-IDs"
      or "no-positive-canary-stop",
    unlistedLookupComplete = unlistedQueried == 57,
    counts = {
      catalog = 96, listed = 39, unlisted = 57, queried = queried,
      listedControlQueried = 1, unlistedQueried = unlistedQueried,
      errors = errors, noDetail = noDetail, returned = returned,
      unlistedReturned = returned - listedReturned,
      inconclusiveTables = 0, skipped = 57 - unlistedQueried
    }
  }
end
local failures, checks, failedNames = 0, 0, {}
local function check(why, condition)
  checks = checks + 1
  if not condition then
    failures = failures + 1; failedNames[why] = true; print("RED " .. why)
  else print("PASS " .. why) end
end
local function clone(value)
  if type(value) ~= "table" then return value end
  local out = {}
  for key, item in pairs(value) do out[clone(key)] = clone(item) end
  return out
end
local function deeplyEqual(a, b)
  if type(a) ~= type(b) then return false end
  if type(a) ~= "table" then return a == b end
  for k, v in pairs(a) do if not deeplyEqual(v, b[k]) then return false end end
  for k in pairs(b) do if a[k] == nil then return false end end
  return true
end
local savedPriorSnapshot
local function rejected(kind)
  local a = RRECollectorData.candidateAttempt
  return type(a) == "table" and a.status == kind
    and type(a.reason) == "string" and a.reason:find("detail", 1, true) ~= nil
    and a.trigger == "manual" and a.automaticRetries == 0
end
local function reset(prior)
  local old = prior and report(58, 0, 7) or nil
  if old then old.sequence, old.trigger = 7, "manual" end
  savedPriorSnapshot = old and clone(old) or nil
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
local function priorIntact()
  return savedPriorSnapshot == nil
    or deeplyEqual(savedPriorSnapshot, RRECollectorData.candidateLookup)
end
local old, latest, probe, toolbar = reset(true)
nextReport = report(9, 9)
runCandidateLookup("manual")
check("all-error preserves useful prior", RRECollectorData.candidateLookup == old
  and RRECollectorData.candidateSequence == 7
  and rejected("failed") and priorIntact()
  and unchanged(latest, probe, toolbar))
old, latest, probe, toolbar = reset(true)
nextReport = report(9, 2, 7)
runCandidateLookup("manual")
check("partial-error preserves useful prior", RRECollectorData.candidateLookup == old
  and RRECollectorData.candidateSequence == 7
  and rejected("incomplete") and priorIntact()
  and unchanged(latest, probe, toolbar))
old, latest, probe, toolbar = reset(false)
nextReport = report(9, 9)
runCandidateLookup("manual")
check("all-error without prior not successful", rejected("failed")
  and RRECollectorData.candidateLookup == nil and RRECollectorData.candidateSequence == 0
  and unchanged(latest, probe, toolbar))
old, latest, probe, toolbar = reset(false)
nextReport = report(9, 2, 7)
runCandidateLookup("manual")
-- A no-prior partial may be preserved as explicitly incomplete evidence, or
-- discarded without advancing the sequence; it must not claim success.
check("partial-error without prior classified incomplete", rejected("incomplete")
  and ((RRECollectorData.candidateLookup == nil and RRECollectorData.candidateSequence == 0)
    or (RRECollectorData.candidateLookup == nextReport
      and RRECollectorData.candidateSequence == 1))
  and unchanged(latest, probe, toolbar))
old, latest, probe, toolbar = reset(true)
nextReport = report(9, 0, 9)
local noDetail = nextReport
runCandidateLookup("manual")
check("error-free no-detail can replace", RRECollectorData.candidateLookup == noDetail
  and RRECollectorData.candidateSequence == 8
  and unchanged(latest, probe, toolbar))
old, latest, probe, toolbar = reset(true)
nextReport = report(58, 0)
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
  local wanted = {
    ["all-error preserves useful prior"] = true,
    ["partial-error preserves useful prior"] = true,
    ["all-error without prior not successful"] = true,
    ["partial-error without prior classified incomplete"] = true
  }
  assert(checks == 7 and failures == 4, "expected exactly four of seven frozen-source defects; observed " .. failures)
  for name in pairs(wanted) do assert(failedNames[name], "missing expected red: " .. name) end
  for name in pairs(failedNames) do assert(wanted[name], "unexpected red: " .. name) end
  print("EXPECTED_RED_RC32_CANDIDATES " .. failures .. "/7 named scenarios; no addon changes")
else
  assert(failures == 0, "RC32 candidate protection not yet implemented (" .. failures .. " defects)")
  print("PASS_RC32_CANDIDATES " .. checks .. " scenarios")
end
]==]
assert((loadstring or load)(prefix .. section .. suffix, "RC32 candidate preservation"))()
