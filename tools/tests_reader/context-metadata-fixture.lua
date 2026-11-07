-- Actual context module, synthetic API only. Verifies projection and call count.
local root = assert(arg[1])
dofile(root .. "/addons/RRECollector/core.lua")
local checks, calls = 0, 0
local target = nil
local function check(v, why) assert(v, why); checks = checks + 1 end
local player = {id="uFIXTURE",name="Fixture",calling="rogue",level=43,race="mathosian",raceName="Mathosian",zone="zOPAQUE",decoration=1704,combat=false,power=0}
Inspect = {Unit={Detail=function(id) calls=calls+1; if id=="player" then return player end; assert(id=="uTARGET");return target end,
  Lookup=function(id) if id=="player" then return "uFIXTURE" elseif id=="player.target" and target then return "uTARGET" end end},
  Time={Frame=function() return 1 end,Real=function() return 2 end},
  System={Version=function() return {build="fixture"} end},
  TEMPORARY={Role=function() return 1 end},Role={List=function() return {} end},Stat=function() return {} end}
dofile(root .. "/addons/RRECollector/context.lua")
local capture=RRECollectorRuntime.context.snapshot()
check(calls==1,"exactly existing player Detail call")
check(capture.player.race=="mathosian" and capture.player.raceName=="Mathosian" and capture.player.zone=="zOPAQUE","documented fields copied")
check(capture.player.decoration==nil,"undocumented decoration excluded")
check(capture.player.combat==false and capture.player.power==0,"old false zero preserved")
player.race=nil;player.raceName=nil;player.zone=nil
capture=RRECollectorRuntime.context.snapshot()
check(calls==2,"one Detail call per capture")
check(capture.player.race==nil and capture.player.raceName==nil and capture.player.zone==nil,"missing metadata stays absent")
player.race=false;player.raceName=0;player.zone=""
capture=RRECollectorRuntime.context.snapshot()
check(capture.player.race==false and capture.player.raceName==0 and capture.player.zone=="","provided scalars retained without invented semantics")
player.race={};player.raceName=function()end
capture=RRECollectorRuntime.context.snapshot()
check(capture.player.race==nil and capture.player.raceName==nil,"unsupported values omitted by existing scalar projector")
target={id="uTARGET",race="mathosian",raceName="Mathosian",zone="zTARGET",decoration=1704}
local before=calls
capture=RRECollectorRuntime.context.snapshot()
check(calls==before+2,"existing player and target Detail calls only")
check(capture.target.race=="mathosian" and capture.target.raceName=="Mathosian" and capture.target.zone=="zTARGET","target metadata projected")
check(capture.target.decoration==nil,"target decoration excluded")
print("SC628_CONTEXT_METADATA_PASS "..checks)
