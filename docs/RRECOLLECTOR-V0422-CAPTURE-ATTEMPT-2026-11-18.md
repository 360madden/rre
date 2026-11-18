# RRECollector v0.4.22 source-only capture-attempt milestone — 2026-11-18 16:15 EST

Host: AMD-DESKTOP, named Workbridge 0.16.5-dev, C:\work\rre, main. Prework WA006 correction already pushed as be569e9b97670faa9bf1b74278625fd753cca1bc.

## Implemented

- New independent bounded character-scoped SavedVariables receipt RRECollectorData.captureAttempt after each post-load manual Capture, including attempted/accepted sequence distinction, reason/status, prior preservation, selected counters/clocks, and separate RREC2 publication status/reason.
- /rre status exposes the last recorded attempt; a normal UI reload/logout is needed for SavedVariables disk persistence.
- Source RRECollectorRuntime.VERSION and TOC 0.4.22. Same ability capture, snapshot preservation, RREC2 wire format, and game UI behavior. C# RREC2/Lab2/quest readers and JS adapters/exporters admit 0.4.22 alongside historical versions.
- Installed OneDrive addon v0.4.21 and running physical RIFT were not modified. RC-30/RC-88 remain stopped, no game/VM input, process memory, or reload.

## Offline verified

- Pinned Windows Lua 5.1.4 fixture: preservation 18 assertions; real wire lifecycle 22; exact-module startup 34 scenarios.
- Node package strict pass (11 sources); SavedVariables adapter 33 tests; navigation/quest exporters 54 tests.
- .NET reader production-only 103 checks; roadmap 47 tasks and WA006 source negative control pass.
- Existing Fengari dependency directory was absent; first two optional runner attempts exited2 (LUA_FIXTURE_RUNTIME_UNAVAILABLE), then pinned native Lua 5.1 tests passed.
- Tests are synthetic/offline. No 0.4.22 installed-addon parity, current-client Capture, live RREC2 or WA006 native qualification.

## Source issue and next work

The existing /rre quests branch references RRECollectorRuntime.quests.capture(), but the TOC's nine modules never initialize runtime.quests. The full-startup fixture injects a synthetic quest producer, masking this. RC-88 is stopped; no quest implementation was resumed. Investigate only when scope is reopened.

Two independent read-only reviewers confirmed manual /rre units is feasible to implement offline using the source-hashed tools/agents/collision/wa006_g2_one_shot.lua: historically Inspect.Unit.List maps ID to specifier. Proposed caps are 128 List entries, eight nonself Detail calls, explicit ID-to-XYZ binding, separate SavedVariables sequence, and no RREC2 changes. Current-build live API semantics remain unverified; real physical testing requires a new operator window.

Preserve nine inherited untracked backup/probe items and the Nov17 physical PID/start-time versus updated on-disk 1179 build uncertainty. Git commit/push outcome must be verified separately.
