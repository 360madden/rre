-- RC-32 offline startup candidate-retention regression.
-- Source-extracts the real SavedVariables startup branch from main.lua.
-- Never invokes RIFT, input, SavedVariables on disk, or addon deployment.
-- Usage: lua tools/verify-rrecollector-rc32-startup-retention.lua --expect-red
--        lua tools/verify-rrecollector-rc32-startup-retention.lua --require-fixed
-- Expanded eight-case frozen-source expectation: 3 RED and 5 PASS in --expect-red.
-- After an authorized source fix, --require-fixed must yield 8 PASS.
--
-- Failure is deliberately strict: changing/extracting the startup branch
-- incompatibly requires fixture review, not an automatic green result.

local mode = type(arg) == "table" and arg[1] or nil
if mode ~= "--expect-red" and mode ~= "--require-fixed" then
  io.stderr:write("Usage: lua verify-rrecollector-rc32-startup-retention.lua --expect-red|--require-fixed\n")
  os.exit(2)
end

local path = "addons/RRECollector/main.lua"
local file, openErr = io.open(path, "rb")
assert(file, "cannot read " .. path .. ": " .. tostring(openErr))
local source = file:read("*a")
file:close()
source = source:gsub("\r\n", "\n")
-- Anchor inside the actual SavedVariables event callback, never an earlier
-- candidate-retry/handler local that may appear after source fixes.
local savedHook = assert(source:find("local savedEvent = ", 1, true),
  "main.lua SavedVariables callback not found")
local savedSource = source:sub(savedHook)
local branch = savedSource:match("(local prior = RRECollectorData%.candidateLookup.-)\n%s*local ui = RRECollectorRuntime%.ui")
assert(branch, "main.lua startup candidate-retention branch not found; review fixture extraction")

-- The extracted code, not a duplicate hand-written predicate, decides
-- whether the previously persisted lookup is retained or refreshed.
local prelude = [[
local candidateVersion = "rc32-current-catalog"
local RRECollectorData = {}
local calls, messages = {}, {}
local function say(message) messages[#messages + 1] = tostring(message) end
local function runCandidateLookup(trigger) calls[#calls + 1] = trigger end
local function loadSavedCandidates(prior)
  RRECollectorData = { candidateLookup = prior }
  calls, messages = {}, {}
]]
local postlude = [[
  return calls, messages
end
return loadSavedCandidates
]]
local compile = loadstring or load
local chunk, compileErr = compile(prelude .. branch .. "\n" .. postlude, "rc32-real-startup-retention")
assert(chunk, "startup branch could not compile: " .. tostring(compileErr))
local loadSavedCandidates = chunk()

local function report(kind)
  -- Real catalog shape: 96 candidates, 39 listed, 57 unlisted;
  -- one listed control and eight canaries precede any expanded lookup.
  local rows, canaryIds = {}, {}
  local screenshotIds = {
    "AFDD9D7E2A8F0E50B", "A768CF3B63EE8D6ED", "AFA78C0D582C9F2E5",
    "A37397DC597DDAF03", "A0E2112FD6FE262EE", "A411792DB5CF7E0E4"
  }
  for i = 1, 96 do
    local listed = i <= 39
    rows[i] = {
      id = screenshotIds[i - 39] or string.format("A%016X", i),
      name = "RC32 synthetic candidate " .. i,
      soul = i >= 40 and i <= 45 and "Paladin"
        or i == 46 and "VoidKnight" or i == 47 and "Paragon"
        or (i % 2 == 0 and "Reaver" or "Warlord"),
      listed = listed,
      category = listed and "known" or "candidate",
      status = listed and "listed-not-queried" or "not-queried",
    }
    if i >= 40 and i <= 47 and kind ~= "zero-query" then
      canaryIds[#canaryIds + 1] = rows[i].id
    end
  end
  local counts = {
    catalog = 96,
    listed = 39,
    unlisted = 57,
    queried = 0,
    returned = 0,
    noDetail = 0,
    errors = 0,
    listedControlQueried = 0,
    unlistedQueried = 0,
    unlistedReturned = 0,
    inconclusiveTables = 0,
    skipped = 57,
  }
  local policy = "no-positive-canary-stop"
  local complete = false
  if kind == "valid" then
    -- One successful listed control, 50 positive unlisted results,
    -- seven nil/no-detail results. Exactly 58 Detail calls.
    rows[1].status, rows[1].phase = "returned", "listed-control"
    rows[1].detail = { name = rows[1].name }
    for i = 40, 96 do
      rows[i].phase = i <= 47 and "unlisted-canary" or "unlisted-expansion"
      if i <= 89 then
        rows[i].status = "returned"
        rows[i].detail = { name = rows[i].name }
      else
        rows[i].status = "no-detail"
      end
    end
    counts.queried = 58
    counts.returned = 51
    counts.noDetail = 7
    counts.listedControlQueried = 1
    counts.unlistedQueried = 57
    counts.unlistedReturned = 50
    counts.skipped = 0
    policy = "positive-canary-expanded-to-other-unlisted-IDs"
    complete = true
  elseif kind == "all-errors" then
    rows[1].status, rows[1].phase = "lookup-error", "listed-control"
    for i = 40, 47 do
      rows[i].status, rows[i].phase = "lookup-error", "unlisted-canary"
    end
    counts.queried = 9
    counts.errors = 9
    counts.listedControlQueried = 1
    counts.unlistedQueried = 8
    counts.skipped = 49
  elseif kind == "negative" or kind == "listed-only" then
    rows[1].status, rows[1].phase =
      kind == "negative" and "no-detail" or "returned", "listed-control"
    if kind == "listed-only" then rows[1].detail = {name = rows[1].name} end
    for i = 40, 47 do
      rows[i].status, rows[i].phase = "no-detail", "unlisted-canary"
    end
    counts.queried = 9
    counts.listedControlQueried = 1
    counts.unlistedQueried = 8
    counts.returned = kind == "listed-only" and 1 or 0
    counts.noDetail = kind == "listed-only" and 8 or 9
    counts.skipped = 49
  elseif kind ~= "zero-query" then
    error("unknown fixture kind: " .. tostring(kind))
  end
  for i = 40, 96 do
    if rows[i].status == "not-queried" then
      rows[i].status = "not-attempted-canary-stop"
    end
  end
  return {
    schemaVersion = 1, addonVersion = "0.4.10",
    source = "synthetic-static-candidates",
    scope = "static-Warrior-candidates-explicit-ID-API-query-not-unlock-proof",
    catalogVersion = "rc32-current-catalog",
    apiReady = true, listRawCount = 39, listUniqueCount = 39,
    player = {calling = "Warrior"}, roleSlot = 1,
    entries = rows, canaryIds = canaryIds,
    counts = counts,
    policy = policy,
    unlistedLookupComplete = complete,
    note = "nil/error not proof of locked, absent, or unlearnable ability",
    trigger = "manual",
    sequence = 1,
  }
end

local inconclusiveSaved = report("negative")
inconclusiveSaved.counts.noDetail = 0
inconclusiveSaved.counts.inconclusiveTables = 9
inconclusiveSaved.entries[1].status = "inconclusive-table"
inconclusiveSaved.entries[1].detail = {}
for i = 40, 47 do
  inconclusiveSaved.entries[i].status = "inconclusive-table"
  inconclusiveSaved.entries[i].detail = {}
end
local legacySaved = report("negative")
legacySaved.counts.inconclusiveTables = nil

local tests = {
  {
    name = "all-error prior must retry startup",
    saved = report("all-errors"),
    expected = 1,
    frozenRed = true,
  },
  {
    name = "valid prior retained for same catalog",
    saved = report("valid"),
    expected = 0,
    frozenRed = false,
  },
  {
    name = "catalog mismatch must retry startup",
    saved = report("valid"),
    expected = 1,
    frozenRed = false,
  },
  {
    name = "zero-query ambiguous prior must retry startup",
    saved = report("zero-query"),
    expected = 1,
    frozenRed = true,
  },
  {
    name = "error-free all-no-detail prior retained",
    saved = report("negative"),
    expected = 0,
    frozenRed = false,
  },
  {
    name = "listed-control-only valid prior retained",
    saved = report("listed-only"),
    expected = 0,
    frozenRed = false,
  },
  {
    name = "all-inconclusive saved report must retry startup",
    saved = inconclusiveSaved,
    expected = 1,
    frozenRed = true,
  },
  {
    name = "legacy no-inconclusive-counter report retained",
    saved = legacySaved,
    expected = 0,
    frozenRed = false,
  },
}
tests[3].saved.catalogVersion = "rc32-obsolete-catalog"

local failed, unexpected = 0, 0
for _, test in ipairs(tests) do
  local calls, messages = loadSavedCandidates(test.saved)
  local ok = #calls == test.expected
  if ok and test.expected == 1 then
    ok = calls[1] == "startup"
  end
  if ok and test.expected == 0 then
    ok = #messages == 1
      and messages[1] == "Prior candidate lookup retained for this catalog; /rre candidates to refresh."
  end
  local label = ok and "PASS" or "RED"
  print(string.format("%s %-52s calls=%d expected=%d", label, test.name, #calls, test.expected))
  if not ok then failed = failed + 1 end
  if mode == "--expect-red" and (not ok) ~= test.frozenRed then
    unexpected = unexpected + 1
    io.stderr:write("UNEXPECTED_BASELINE " .. test.name .. "\n")
  end
end

if mode == "--expect-red" then
  assert(unexpected == 0 and failed == 3,
    "expected-red startup baseline changed; review failures before proceeding")
  print(string.format("EXPECTED_RED_RC32_STARTUP %d/%d", failed, #tests))
else
  assert(failed == 0, "startup candidate-retention fix not yet implemented")
  print(string.format("FIXED_RC32_STARTUP %d/%d", #tests, #tests))
end
