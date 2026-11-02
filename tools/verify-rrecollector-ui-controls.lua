-- Execute from C:/work/rre with a Lua interpreter. No game process or saved data is touched.
-- Exercises the actual shared control source using a small RIFT UI model, not game-render validation.
local f = assert(io.open("addons/RRECollector/ui.lua", "rb"))
local source = f:read("*a"); f:close()
local controls = assert(source:match("%-%- RC23%-CONTROLS%-BEGIN.-%-%- RC23%-CONTROLS%-END"), "control block missing")
local prefix = [==[
local frames, calls, count, secured = {}, 0, 0, false
local function check(x, why) assert(x, why); count = count + 1 end
local M = {}
function M:SetSecureMode(v) self.secure=v end
function M:SetWidth(v) self.width=v end
function M:SetHeight(v) self.height=v end
function M:SetPoint(...) if secured and self.secure=='restricted' then error('protected host moved') end; self.point={...} end
function M:SetLayer(v) self.layer=v end
function M:SetMouseMasking(v) self.mask=v end
function M:SetWordwrap(v) self.wrap=v end
function M:SetFontSize(v) self.font=v end
function M:SetText(v) self.text=v end
function M:SetFontColor(...) self.ink={...} end
function M:SetBackgroundColor(...) if secured and self.secure=='restricted' then error('protected host recolored') end; self.bg={...} end
function M:GetWidth() return self.width or #(self.text or '')*(self.font or 13)*0.52 end
function M:GetHeight() return self.height or (self.font or 13)*1.2 end
function M:GetFullWidth() error('disabled GetFullWidth called') end
function M:EventAttach(e,h) self.events[e]=h end
function M:EventMacroSet(e,m) self.macro=m; self.macroEvent=e end
UI={CreateFrame=function(kind,name,parent) local f=setmetatable({kind=kind,name=name,parent=parent,events={},secure='normal'}, {__index=M});frames[name]=f;return f end}
Event={UI={Input={Mouse={Cursor={In='enter',Out='leave'},Left={Down='down',Up='up',Upoutside='cancel',Click='click'}}}}}
local color={button={.1,.19,.24,1},grey={.64,.71,.74,1},header={.075,.125,.166,1},muted={.125,.157,.176,1},rowPressed={.045,.09,.126,1},rowHover={.145,.28,.33,1},rowSelected={.105,.215,.276,1},cyan={.22,.73,.81,1},background={.035,.063,.086,1},text={.936,.963,.977,1}}
local function paint(f,c) f:SetBackgroundColor((unpack or table.unpack)(c)) end
local function block(n,p,x,y,w,h,c) local f=UI.CreateFrame('Frame',n,p);f:SetPoint('TOPLEFT',p,'TOPLEFT',x,y);f:SetWidth(w);f:SetHeight(h);paint(f,c);return f end
local function say(s) error(s) end
]==]
local suffix = [==[
local v=button('Test',{},0,0,81,28,'Reload UI',function() calls=calls+1 end)
check(v.label.font==13,'uniform normal font')
check(v.label.width==nil and v.label.height==nil,'unconstrained label dimensions')
check(v.label:GetWidth()<=69,'caption fits')
check(frames.TestBorderTop and frames.TestBorderBottom and frames.TestBorderLeft and frames.TestBorderRight,'four edges')
check(frames.TestFill.mask=='limited' and v.label.mask=='limited','visuals pass input')
local old=frames.TestFill.bg[1]
v.frame.events.enter();check(frames.TestFill.bg[1]~=old,'hover changes fill')
v.frame.events.down();check(v.label.point[4]==1 and v.label.point[5]==1,'press offsets label')
v.frame.events.up();check(v.label.point[4]==0,'release resets position')
v.frame.events.click();check(calls==1,'one ordinary click')
v.frame.events.down();v.frame.events.cancel();check(v.label.point[4]==0 and calls==1,'outside release cancels without action')
v.setEnabled(false);v.frame.events.down();v.frame.events.click();check(calls==1 and v.label.point[4]==0,'disabled is inert')
v.setEnabled(true);v.setSelected(true);check(v.label.ink[2]==color.cyan[2] and v.isEnabled(),'selected is not disabled')
v.setText(string.rep('Verylong',20));check(v.label:GetWidth()<=69 and v.label.font>=11,'bounded long text fit')
v.setText('魂魂魂魂魂魂魂魂魂魂魂魂魂')
-- Check UTF-8 boundary without depending on Lua 5.3's utf8 library.
local rest=v.label.text:gsub('魂',''):gsub('%.','')
check(rest=='','UTF8 truncation valid')
for _,item in ipairs({{'Browse',72},{'Check 8',73},{'Capture',73},{'Retry',65},{'Reload UI',81},{'Hide',69},{'Candidates',102},{'Soul: Void Knight',130}}) do
 local c=button('Width'..item[1],{},0,0,item[2],28,item[1],function()end)
 check(c.label:GetWidth()<=item[2]-12,'label fits '..item[1])
end
local f=UI.CreateFrame('Frame','Secure',{})
local secureVisual=buttonVisual('SecureLook',f,81,28,'Reload UI')
f:SetSecureMode('restricted');f:EventMacroSet('click','reloadui');secured=true
f.events.enter();f.events.down();f.events.up();f.events.cancel()
check(f.macro=='reloadui' and f.events.click==nil,'macro binding untouched; no Lua click handler')
check(secureVisual.label.font==13 and secureVisual.label.secure=='normal','secure label same font on normal child')
check(secureVisual.label.point[4]==0,'secure visual cancellation resets')
secured=false
print('PASS '..count..' control behavior assertions (mock RIFT UI)')
]==]
local compile = loadstring or load
assert(compile(prefix .. controls .. "\n" .. suffix, "RC23 controls"))()
