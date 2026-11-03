# SC-103 — staged, operator-run LuaPad tooltip candidate probe

**Date:** 2026-11-03
**Status:** **OFFLINE-STAGED, NOT DEPLOYED, NOT RUN IN RIFT**. Exact modern Protector's Fury/Legendary variant ID remains unknown; SC-103 remains blocked.
**Owner/scope:** RRE physical-PC research manager, RRE-owned tools and documentation only. No installed addon, game process, VMware lab, Workbridge service or SavedVariables modification.

## Why this exists

The already installed JAB and Rusty's Action Bars call `Inspect.Tooltip()` to clear tooltips for **their own action slots**, but do not provide a demonstrated native Soul Tree ID sampler. Installed LuaPad v1.8 exposes `/lp` and executes operator-pasted Lua through `xpcall(loadstring(...), ...)`. Its in-game loading in the *current PID* is unverified. A source-qualified RIFT-client `Inspect.Tooltip()` documentation excerpt describes `type, shown` and `type, unit, buff`, with `type = "ability"` possible, yet does **not guarantee** the native Soul Tree's hovered item returns a modern exact ability ID.

## Staged files and proven source

| Local RRE file | Exact SHA-256 | Role |
| --- | --- | --- |
| `tools/sc103_luapad_hover_probe.lua` | `4b8a19e44dd5444393f631d1517bb6b18bcaee6a4cd9ac8c8b1d689caeed11c3` | Self-contained operator-pasted one-shot Lua; no TOC or installed addon |
| `tools/test_sc103_luapad_hover_probe.lua` | `194fbf53d9b2feb5a62d38b80d5ac1e0f2dc9eb7bd7bcc7841ae848424ff3e0c` | Synthetic API/event/time/payload fixtures only |

**API source:** Previously saved in-client `Inspect.Tooltip()` text is 596 chars, SHA-256 `14b6dea5b4e532bda5433028bd10218adbdb82568f1f2e9f2ae41c92f75633a1`. `Command.Event.Attach` is separately documented (716-character saved source); existing RiftReader2Casting uses `Event.System.Update.Begin` and `Inspect.Time.Frame`. Installed Rusty's Action Bars provides source examples of `Command.Event.Detach(event, nil, label)`. These are source patterns; current-game runtime compatibility was **not** exercised by RRE.

## Exact bounds and observable behavior

- The probe does **nothing unless an operator manually copies its text into a working LuaPad editor and clicks Run**. No file under the RIFT `Interface/AddOns` tree is changed by staging these two RRE files.
- It verifies all required APIs and a monotonic frame clock before attaching one `Event.System.Update.Begin` listener. A repeat Run supersedes the prior listener through a unique temporary global slot.
- It waits **0.6 seconds** to avoid sampling the editor button, then watches at most **12 seconds of frame-clock time / 900 delivered frame callbacks** and stops earlier on a consistent result or error. The earliest observed bound wins. **Important:** this is not a standalone wall-clock watchdog: if the game stops delivering update events, no callback runs to enforce the deadline. When frames resume the time gate can expire, or an operator can cancel/re-arm; do not assume automatic expiry during a frozen client.
- Accepts a candidate **only** if `Inspect.Tooltip` returns `type == "ability"` and a string matching precisely `A` followed by **16 hexadecimal characters**, **identical across three consecutive frames**. Print result prefix: `ABILITY_ID_CANDIDATE_UNVERIFIED_SOURCE` with only that uppercase ability-shaped ID.
- Otherwise prints a bounded `UNKNOWN` status, such as `TIMEOUT_NO_VALID_ID`, `TOOLTIP_API_FAILURE`, `CLOCK_UNAVAILABLE`, or a missing-API/registration status. Never prints raw `shown` variants, arbitrary objects, unit/buff IDs, source pointer values or the third/fourth tooltip results.
- Detaches on success, timeout, cancellation and error. If detachment fails, the handler is marked inert and the result says `DETACH_UNCONFIRMED`. No game cast, movement, role change, UI click/macro automation, disk write, SavedVariables serialization or network action exists in the probe.
- **The returned ID is not automatically a Protector's Fury ID or a Legendary variant.** It can be misattributed if another ability tooltip was hovered; screenshot-level correlation with the native tooltip and current role is still required.

## Offline testing (not a live proof)

The **previous exact source/fixture pair** (source SHA `b97bf0a1...`, fixture SHA `84f7704a...`) was transferred byte-for-byte and executed in an isolated **Lua 5.4 shared-library runtime**. FreeBuff subsequently identified a transient tooltip-error defect in the staged probe. The current exact source/fixture hashes above were transferred byte-for-byte using a bounded read-only Workbridge Python bundle, checked after decompression against both SHA-256 values, and the revised complete fixture ran in an isolated assistant-container Lua 5.4 shared-library runtime. **119 assertions passed**, printing `SC103_HOVER_PROBE_OFFLINE_TESTS_PASS 119`. No repository, game, or installed addon files were changed by this test.

**Historical result: 110 assertions passed under the previous exact source/fixture pair.** That suite covered three-frame ID qualification, non-ability/unit/table payload suppression, initial settle, time and frame limits, API failures, clock drift, event attach/detach and cancellation. A new intermittent-error test requires the matching-ID sequence to restart after a failed `Inspect.Tooltip()` call. A **source-extracted Lua 5.4 red/green check** independently reproduced the original failure and passed after resetting `state.lastId` and `state.stable` in the error branch. **Full revised suite: 119 Lua 5.4 assertions PASS** under the exact current source and fixture hashes; this supersedes the old 110-assertion fixture result, which remains valid only for the historical pair. The source uses conventional Lua 5.1 syntax, but **Lua 5.1/RIFT-runtime compilation, actual LuaPad loading, and native-tooltip ID results remain unverified**. Do not promote synthetic tests to an in-game success claim.

## Independent local reasoning review

Two independently prompted **local Gemma 4 12B reasoning workers**, each using one allowlisted read-only source-file tool call, finished in a supervised Ollama session (107,199 ms total). The manager accepted one missing combined negative test and rejected two source-inconsistent suggestions; a second worker confirmed the inability to infer selected Legendary state from an ID-shaped tooltip result. The [source-qualified worker receipt and critique](REA-RIFT-SPELLCASTING-LOCAL-REASONING-WORKER-PILOT-2026-11-03.md) records model/tool limits, failed Codex-provider attempts, findings and verified corrections. No model worker edited files or operated the game.

## New FreeBuff review and targeted correction (same day)

Two real **FreeBuff CLI reviews** completed using isolated Windows ConPTY source-copy sessions: SC-103 (59.3 seconds) and RC-30 (50.3 seconds). The SC-103 reviewer correctly identified that a transient tooltip API fault retained the prior 2/3 stable-sample state. The staged RRE source now clears `state.lastId` and `state.stable` on failure; the new regression fixture tests the condition. Full source hashes, actual FreeBuff completion receipts, proof limits and a parked RC-30 risk are recorded in [the FreeBuff review report](REA-RIFT-SPELLCASTING-FREEBUFF-REVIEW-2026-11-03.md). The operator now prefers **FreeBuff, not Ollama** for future agent delegation; the older Gemma/Ollama review above is historical only.

## Operator trial procedure — future only

**Preflight:** Confirm the physical client still has the intended character and matching RIFT build, and that LuaPad is *actually loaded*; an installed TOC alone is not proof. Keep RRECollector v0.4.10 frozen and the Workbridge GUI capture quarantine untouched. This procedure is optional and explicitly **not performed by this checkpoint**.

1. In the game, show the native **Righteous Defender** Soul Tree for Atank (if still current), with **Paladin 45 / Void Knight 15 / Paragon 0** and Legendary counters **0/3 / 0/2 / 0/1** as previously observed. Don't change role, Soul points, mentor level or talent allocations.
2. Open the already installed LuaPad via `/lp` if available, move its window away from the relevant Soul Tree icon, and copy/paste the *exact* `C:\work\rre\tools\sc103_luapad_hover_probe.lua` contents into the LuaPad editor. Click **Run** once. This is a **manual operator action**, not an automatic RRE command.
3. On `ARMED_12_SECONDS`, move the mouse directly to native **Protector's Fury** and hold the tooltip visible (avoid passing over another ability). Observe the single status line. If an exact ability candidate appears, **take an operator screenshot** with the native tooltip and status together. Do not assume the returned scalar distinguishes Normal versus Legendary.
4. If the result is `UNKNOWN`, `BLOCKED_REQUIRED_API`, `DETACH_UNCONFIRMED` or no status appears, **stop** rather than forcing repeat trials or modifying installed addons. Reconcile the cause in a new bounded source-review step. Never paste arbitrary third-party scripts or a raw-tooltip dumper to compensate.

**Evidence required for acceptance (G1 visual-only until separately repeated/session-bound evidence; not G2/G3 by itself):** Source-qualified screenshot bytes/UTC provenance plus visible role/tooltip, exact status and *an independently supported association* of the returned ID with that tooltip. Current screenshot still shows all zero Legendary counters, so no selected Legendary can be proven from this character's demonstrated state. An exact current tooltip candidate may resolve one normal/tooltip ID, **not** selection or eligibility.

## Research state and stop conditions

- SC-103 **BLOCKED** until exact modern rank/variant/role mapping is justified by fresh role-bound evidence; the parked `Ability.New.List` native forwarding trace remains untouched.
- RC-30 **still requires** its own eight-slot → Pin → Undo before Reload UI → saved 0.4.10 evidence; this script does not certify RC-30 or unlock addon changes.
- Workbridge's quarantined `DESKTOP_TREE_UNSETTLED` GUI lease remains the separate desktop owner's responsibility. This tool does **not** capture screenshots, focus the game or bypass that lease.
- No automation or additional service is introduced; this is a **manually triggered, short-lived, source-and-test-qualified candidate probe**.
