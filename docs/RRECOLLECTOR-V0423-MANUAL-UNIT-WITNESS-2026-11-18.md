# RRECollector v0.4.23 bounded manual unit witness — 2026-11-18 16:24 EST

Host: AMD-DESKTOP, Workbridge 0.16.5-dev, C:\work\rre, main. Prior independent v0.4.22 capture receipt milestone committed and pushed as 5ddf7ab23020ebb6805c8676909e8e403f572414. No current physical-RIFT game input, addon deployment, UI reload, memory capture or VMware access.

## Source implementation

- Added addons/RRECollector/units.lua loaded after wire.lua and before ui.lua; ten Lua runtime modules, strict TOC/core VERSION 0.4.23. The only new action is manual /rre units. It makes at most one Inspect.Unit.Lookup("player"), one Inspect.Unit.List(), and eight nonself Inspect.Unit.Detail(id), with at most 128 List table entries examined. API uses the source-retained historical ID-key/specifier-value mapping; current-build behavior is not live-qualified.
- Enforce exact unit ID u+16 hex digits, bounded specifier text, sorted candidate Detail subset when List fully enumerated, exact returned Detail.id match before any XYZ coordinates can be retained, finite coordinate/clocks (zero valid), explicit capped/partial/unavailable/error/empty/complete statuses and counters. No unsupported scene completeness, native identity, coordinate-frame, clock atomicity, world census or live freshness claim.
- Character SavedVariables RRECollectorData.unitSnapshots retains at most two newest accepted reports; separate unitSnapshotSequence and unitAttempt monotonically count accepted reports versus all post-load manual attempts. Failed calls preserve prior snapshots. Ability latest/sequence, previous captureAttempt, candidate/probe/quest records, UI controls and RREC2 frames/payload are independent.
- Source-only README, contract, JS SavedVariables/nav/quest adapters, C# RREC2/quest/binding strict version allowlists updated for 0.4.23 while historical versions remain admitted. A separate v0.4.22 release commit remains independently reproducible.

## Verified offline

- Pinned native Windows Lua 5.1.4 unit module fixture: 39 assertions, including API absence, failed List/Detail, 128/129 cap, nine-to-eight Detail clipping, sorted selection, invalid IDs/specifiers, mismatched/missing Detail ID, NaN/Infinity exclusion, zero retention, bounded clocks and no native qualification.
- Exact ten-module Lua startup/manual slash integration: 39 synthetic scenarios, including SavedVariables-load gate, two snapshots, exception preservation, unchanged ability latest/sequence and unchanged RREC2 frames.
- Existing Lua capture preservation 18, actual wire lifecycle 22; strict package verifier 12 source files, version 0.4.23, installedShaMatches null, runtimeUiVerified false.
- JS SavedVariables adapter 34/34; nav/quest exporters 57/57; C# reader production-only 105/105.
- Remaining gates before commit: roadmap 47 tasks, git diff --check, inspect exact changed files/status; commit and push scoped source only, then verify HEAD/remote.

## Open boundaries and next action

P0: Produce strict, source-SHA-bound offline unit-witness exporter/validator and cross-source negative controls before inferring native WA006 identification. New API report is not evidence that any physical build1179 unit was observed.
P1: Coordinate a separately authorized physical-RIFT operator window and verify current process image/load provenance before any manual /rre units, UI reload or native reader use. Existing process started before Nov17 postpatch update capture; disk1179 does not prove mapped image.
P2: Retain the existing source defect: /rre quests references runtime.quests absent from TOC and the mock injected it. RC-88 and RC-30 user stops remain in force; do not restart either feature without new direction.

Nine inherited unrelated untracked backup/probe paths remain preserved. No new external AI provider or dependency installed. Git milestone receipt to be verified separately.
