# RC-79 — quest objectives and map-location input for automation

**November 11, 2026, LEGION. Source implementation and focused offline checks complete; Lua execution and physical-client validation pending.** RRECollector v0.4.20 adds manual `/rre quests` and an offline JSON exporter. It provides quest goals for later automation; it does not accept, complete, turn in or travel to a quest.

## Result and use

The existing ability toolbar and separate casting observer already supply ability selection/readiness and secure hardware-click actions. RRE previously lacked a quest-journal capture. The new path records current quest identities, explicit completion/failure/tracking flags, objective quantities and only referenced map indicators. Ability/candidate/profession/navigation receipts remain separate. No timer, event subscription, combat action or inbound command is added.

After an authorized version-matched load, manual `/rre quests` and a normal SavedVariables flush:

```powershell
node tools/export-rrecollector-quests.mjs "FULL_PATH_TO_RRECollector.lua" --output "NEW_goals.json"
```

The original is parsed as literal Lua, never executed. The output binds SHA256, byte size, modification time, producer version and sequence. `nextObjectives` prioritizes tracked/watched remaining objectives, suppresses completed/failed quests and wrong-identity locations, and preserves objectives without coordinates. It does not calculate distances across unqualified map/zone frames. Offline files never establish current freshness, travel feasibility or actual completion.

## Capture and failure behavior

- Existing `capabilities.lua` holds the new isolated quest module; the package stays at nine ordered startup scripts and eleven files. `/rre quests` saves separate `questSnapshot`, `questSnapshotSequence` and a bounded `questAttempt` diagnostic.
- Player identity/capability and finite frame/real clocks must be available before journal enumeration. A missing/failed API or unbound player preserves the previous journal; it cannot replace it with an apparently successful empty snapshot.
- Every API lookup, invocation and projected member read is guarded. Unknown booleans remain absent. Quantities must be nonnegative safe integers. Lookup IDs remain separate from returned `sourceId`; missing/mismatched identity is partial and cannot produce a destination.
- Limits: scan256/retain128 quests, scan64/retain32 objectives per quest, scan32/retain16 indicators per objective, **512 total objectives**, **512 total indicator placements**, **128 unique map calls**, and **131,072 bytes of projected content text**. The text budget includes every repeated map placement; bounded IDs and existing context are separate. These are not a whole-file size claim. The original reader retains its two-million-byte refusal.
- Truncation, malformed/duplicate IDs, missing detail/objectives/coordinates and quota exhaustion remain explicit partial results. Partial rows can still expose individually qualified remaining objectives. Impossible status/counter combinations are rejected by the exporter.
- Quest records stay outside RREC2. Node/C# readers continue to accept .19 and .20 under the unchanged ability/context/Experience contract. The navigation exporter accepts either producer, enforces the requested version and rejects a retained .19 probe under a .20 root.

## Evidence and validation

The local installed RIFT_API_Docs Markdown derivatives document `Inspect.Quest.List`, `Inspect.Quest.Detail`, objective descriptions/count/countDone/complete/indicators, and `Inspect.Map.Detail` coordinates/title/description. These are documentation leads, not fresh API responses. Original source hashes:

- Quest List: `f81dc7be45818c559952afd020c7bcc20691b23d5a6c87fdf2bf9676a2a9c7e6`.
- Quest Detail: `f8c25419ed5fb7588c9228916a0ef84f90bd876565a2c2102727ace9ecdcb1de`.
- Map Detail: `f9e87ffe3ed28a95157509964d0e6d48572200173c5164b1756df13e1618eff1`.

Focused checks: quest exporter **12/12**, navigation + saved adapter **42/42**, profession receipt **12/12**, existing collector cross-calling/candidate checks **20/20**, C# production contracts **99/99**. Strict eleven-file source package passed. PowerShell7 deployment **preflight only** passed, observed installed .18/source .20 and changed no installed files. Legacy Windows PowerShell refused script execution; no policy was changed, and the existing PowerShell7 runtime ran the ordinary preflight.

The actual-source Lua regression is [verify_quest_capture.lua](../tools/agents/quest_journal/verify_quest_capture.lua). No qualifying local Lua interpreter was found; its assertions have **not executed**. Lua5.1 compatibility received independent source review only.

The full existing research gate ran once: `artifacts/rc79-research-gate-20261111-2133/validation.json`, **507 tests enumerated, overall FAILED**. Validation had10 missing historical helper errors; collision2 old-source/fixture errors; pathfinding9 errors/1failure from old pinned-source expectations; navigation97 ran with2skips, which the gate rejects. C2M30, follow73, visual58 and review-adapter17 passed. Source inventory remained unchanged throughout. Failing historical lane code is unchanged by RC-79. This is not a full-suite pass and no old hash was rebaselined.

Independent review caught and fixed global serialized-size multiplication, cached-map expansion, identity mismatches, invalid quantities, unbound player context and impossible exporter statuses. User authorized commits/pushes. A separate bounded request for RRECollector-only deployment, UI reload and read-only quest/ability capture is pending; no deployment or game command was performed for this source milestone.
