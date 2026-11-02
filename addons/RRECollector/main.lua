-- RRECollector v0.2.0: manual commands, SavedVariables and bootstrap.
-- No polling, game actions, process access, or dependencies on other addons.
local ADDON = "RRECollector"
local VERSION, SCHEMA = RRECollectorRuntime.VERSION, RRECollectorRuntime.SCHEMA
local say, finite = RRECollectorRuntime.core.say, RRECollectorRuntime.core.finite
local collect = RRECollectorRuntime.abilities.collect
local savedLoaded = false
local lastMessage = "waiting-for-saved-variables"

local function status()
  if not savedLoaded then
    say("v" .. VERSION .. " saved data not loaded; capture unavailable.")
    return
  end
  local latest = RRECollectorData.latest
  if type(latest) ~= "table" then
    say("v" .. VERSION .. " ready; no snapshot. Use /rre capture.")
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
  say("v" .. VERSION .. " commands: /rre status | capture | page N | export | help")
  say("Captures known API abilities, role context, stats and target. No casting.")
end

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
    elseif action == "capture" then
      if not savedLoaded then
        say("SavedVariables not ready; retry after initialization.")
        return
      end
      local captureOk, record = pcall(collect)
      if not captureOk or type(record) ~= "table" then
        lastMessage = "capture-error"
        say("Capture failed safely; no prior snapshot overwritten.")
        return
      end
      RRECollectorData.latest = record
      RRECollectorData.sequence = record.sequence
      lastMessage = record.captureComplete and "capture-complete" or "capture-partial"
      say("Capture " .. lastMessage .. ": " ..
        tostring(record.abilityList.uniqueCount) .. " IDs, " ..
        tostring(record.abilityList.detailCount) ..
        " details. /rre status; /reloadui to save.")
    elseif action == "page" then
      showPage(tonumber(argument))
    elseif action == "export" then
      say("Full snapshot stored in character SavedVariables: RRECollectorData.latest.")
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
    say("v" .. VERSION .. " ready. /rre capture")
  end, "RRECollector.SavedVariables")
  if not attached then
    lastMessage = "saved-event-unavailable"
    say("SavedVariables event attachment failed.")
  end
else
  lastMessage = "saved-event-missing"
  say("SavedVariables API unavailable.")
end
