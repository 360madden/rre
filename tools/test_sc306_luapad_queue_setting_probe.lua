-- Offline-only synthetic fixture for the SC-306 single-setting LuaPad probe.
local SOURCE = "tools/sc306_luapad_queue_setting_probe.lua"
local assertions, totalCalls, listCalls = 0, 0, 0

local function expect(ok, message)
  assertions = assertions + 1
  assert(ok, message)
end

local function makeApi(detail)
  return {
    Setting = {
      Detail = function(key)
        totalCalls = totalCalls + 1
        expect(key == "ActionBars_AbilityQueue", "unexpected setting key")
        return detail(key)
      end,
      List = function()
        listCalls = listCalls + 1
        error("broad setting enumeration is forbidden")
      end,
    },
  }
end

local function run(name, inspect, status, forbidden)
  local before = totalCalls
  local oldInspect, oldPrint = Inspect, print
  local outputs = {}
  Inspect = inspect
  print = function(line)
    outputs[#outputs + 1] = tostring(line)
  end
  local chunk, loadError = loadfile(SOURCE)
  if not chunk then
    Inspect, print = oldInspect, oldPrint
    error(loadError)
  end
  local ok, errorText = pcall(chunk)
  Inspect, print = oldInspect, oldPrint
  expect(ok, name .. ": unexpected Lua error: " .. tostring(errorText))
  local joined = table.concat(outputs, "\n")
  expect(joined:find("[SC306] " .. status, 1, true) ~= nil, name .. ": missing status: " .. joined)
  if forbidden then
    expect(joined:find(forbidden, 1, true) == nil, name .. ": leaked " .. forbidden)
  end
  return totalCalls - before, joined
end

local count = run("no Inspect", nil, "API_UNAVAILABLE")
expect(count == 0, "no Inspect must not call API")
count = run("no Setting", {}, "API_UNAVAILABLE")
expect(count == 0, "no Setting must not call API")
count = run("no Detail", { Setting = {} }, "API_UNAVAILABLE")
expect(count == 0, "no Detail must not call API")
count = run("error", makeApi(function() error("secret error path") end), "CALL_ERROR", "secret")
expect(count == 1, "error case calls exactly once")
count = run("nil", makeApi(function() return nil end), "NO_DETAIL_TABLE nil")
expect(count == 1, "nil case calls exactly once")
count = run("other", makeApi(function() return 123 end), "NO_DETAIL_TABLE number")
expect(count == 1, "non-table case calls exactly once")
count = run("no id", makeApi(function() return { value = "secret-value" } end), "KEY_UNCONFIRMED", "secret")
expect(count == 1, "missing id case calls exactly once")
count = run("wrong id", makeApi(function() return { id = "Account.Secret", value = "hidden" } end), "KEY_UNCONFIRMED", "hidden")
expect(count == 1, "wrong id case calls exactly once")
local exact = "ActionBars_AbilityQueue"
count = run("numeric", makeApi(function() return { id = exact, value = 1 } end), "EXACT_KEY_NUMBER 1")
expect(count == 1, "numeric case calls exactly once")
count = run("boolean", makeApi(function() return { id = exact, value = false } end), "EXACT_KEY_BOOLEAN false")
expect(count == 1, "boolean case calls exactly once")
count = run("safe string", makeApi(function() return { id = exact, value = "Short" } end), "EXACT_KEY_STRING Short")
expect(count == 1, "string case calls exactly once")
count = run("digit string", makeApi(function() return { id = exact, value = "2" } end), "EXACT_KEY_STRING 2")
expect(count == 1, "digit string calls exactly once")
count = run("redacted string", makeApi(function() return { id = exact, value = "Account=123-45-6789" } end), "EXACT_KEY_STRING_REDACTED", "Account=")
expect(count == 1, "redacted case calls exactly once")
count = run("alnum secret", makeApi(function() return { id = exact, value = "AccountNumber12345" } end), "EXACT_KEY_STRING_REDACTED", "AccountNumber")
expect(count == 1, "alnum secret is redacted")
count = run("large number", makeApi(function() return { id = exact, value = 123456789012 } end), "EXACT_KEY_NUMBER_REDACTED", "123456789012")
expect(count == 1, "large number is redacted")
count = run("metatable spoof", makeApi(function()
  return setmetatable({ value = "hidden" }, { __index = function() error("unsafe field access") end })
end), "KEY_UNCONFIRMED", "hidden")
expect(count == 1, "metatable id cannot authorize a value")
count = run("metatable value", makeApi(function()
  return setmetatable({ id = exact }, { __index = function() error("unsafe value lookup") end })
end), "EXACT_KEY_UNSUPPORTED_TYPE nil")
expect(count == 1, "metatable value not invoked")
count = run("table value", makeApi(function() return { id = exact, value = { secret = 1 } } end), "EXACT_KEY_UNSUPPORTED_TYPE table")
expect(count == 1, "table case calls exactly once")
count = run("nil value", makeApi(function() return { id = exact } end), "EXACT_KEY_UNSUPPORTED_TYPE nil")
expect(count == 1, "nil value case calls exactly once")
count = run("NaN", makeApi(function() return { id = exact, value = 0 / 0 } end), "NONFINITE_NUMBER")
expect(count == 1, "NaN case calls exactly once")
count = run("infinite", makeApi(function() return { id = exact, value = math.huge } end), "NONFINITE_NUMBER")
expect(count == 1, "infinite case calls exactly once")
expect(listCalls == 0, "Inspect.Setting.List must never be called")
print("SC306_LUA53_OFFLINE_PASS " .. assertions .. " checks")
