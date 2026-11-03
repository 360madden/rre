# SC-103 — staged, operator-run LuaPad tooltip candidate probe

**Date:** 2026-11-03
**Status:** **OFFLINE-STAGED, NOT DEPLOYED, NOT RUN IN RIFT**. Exact modern Protector's Fury/Legendary variant ID remains unknown; SC-103 remains blocked.
**Owner/scope:** RRE physical-PC research manager, RRE-owned tools and documentation only. No installed addon, game process, VMware lab, Workbridge service or SavedVariables modification.

## Why this exists

The already installed JAB and Rusty's Action Bars call `Inspect.Tooltip()` to clear tooltips for **their own action slots**, but do not provide a demonstrated native Soul Tree ID sampler. The installed LuaPad **disk source** now declares **v2.0.0-preview3** and exposes `/lp`; its Run path compiles operator-pasted Lua via `loadstring`/`load` and executes through `xpcall`. Joey separately reports a simple LuaPad test working in physical RIFT, but this exact SC-103 probe has **not** been verified in a current process. A source-qualified `Inspect.Tooltip()` excerpt describes `type, shown` and `type, unit, buff`, with `type = "ability"` possible; it does **not guarantee** a native Soul Tree hover exposes a modern exact ability ID.

## Staged files and proven source

| Local RRE file | Exact SHA-256 | Role |
| --- | --- | --- |
| `tools/sc103_luapad_hover_probe.lua` | `8c19e4024c950f23df442c3bd91f699f48e060821878a3ae36e4fe237b59cab0` | Self-contained operator-pasted one-shot Lua; no TOC or installed addon |
| `tools/test_sc103_luapad_hover_probe.lua` | `3486fdee95f16e318b98076a67d3d259905898ce8ef188ffd76afd5c349af3fd` | Synthetic API/event/time/high-FPS/exact-detach/result-copy/payload fixtures only |
| `tools/sc103_luapad_copy_result.lua` | `66d4ccf422674bef7613d6554b2b973d36e44a78cc71265d7f980f6375c71d26` | Optional operator-run, one-shot sanitized result retrieval |

**API source:** Previously saved in-client `Inspect.Tooltip()` text is 596 chars, SHA-256 `14b6dea5b4e532bda5433028bd10218adbdb82568f1f2e9f2ae41c92f75633a1`. `Command.Event.Attach` is separately documented (716-character saved source); existing RiftReader2Casting uses `Event.System.Update.Begin` and `Inspect.Time.Frame`. Installed Rusty's Action Bars provides source examples of `Command.Event.Detach(event, nil, label)`. These are source patterns; current-game runtime compatibility was **not** exercised by RRE. Installed `RIFT_API_Docs/LLM_RIFT_API/Event/command_event_detach.md` (SHA-256 `2f71ab75e3be5ca351ffda3d1246afd4e695fb4b871bb21d4db03969b3060988`) confirms that a `nil` handler is a **wildcard** and only one matching registration is removed; the current probe therefore passes its **exact `onFrame` handler** for detachment. This is source-qualified behavior, not a live execution receipt.

**LuaPad v2 source check (physical installed disk files, November 3):** `luapad/RiftAddon.toc` SHA-256 `6964316872bdde7e9eaf34bec489e1309ae499b6011119a0925267d6dcb119e0` declares `Version = "2.0.0-preview3"`; `luapad/main.lua` SHA-256 `81030e95f23c1f11ec7c9ddfc0fbebd9b4760a650c3348eccf311531d6774c34` has Run at lines 296–331: temporarily redirects `print` only during synchronous LuaPad execution and restores it immediately. Thus initial `ARMED_12_SECONDS` is in Output, but later async callback results go to **RIFT chat**. Its **Copy Output** button at lines 221–239 reads Output and calls `Command.CopyToClipboard`. This is source-qualified **disk** behavior, not proof preview3 is loaded in the current RIFT process or that clipboard copying worked. No installed LuaPad or other addon was changed by RRE.

## Exact bounds and observable behavior

- The probe does **nothing unless an operator manually copies its text into a working LuaPad editor and clicks Run**. No file under the RIFT `Interface/AddOns` tree is changed by staging these three RRE files.
- It checks required APIs and a valid initial frame-clock reading before attaching one `Event.System.Update.Begin` listener, then monitors frame-clock progress during updates. A repeat Run supersedes the prior listener through a unique temporary global slot.
- It waits **0.6 seconds** to avoid sampling the editor button, then watches at most **12 seconds of advancing frame-clock time** with an independent guard for **900 consecutive callbacks during which the frame clock does not advance**. High FPS by itself no longer shortens the 12-second window; an actual stable candidate or API error still ends it sooner. **Important:** there is no independent wall-clock watchdog: if game update callbacks stop, neither guard runs. When frames resume, the time gate can expire, or an operator can cancel/re-arm; do not assume expiry during a frozen client.
- Accepts a candidate **only** if `Inspect.Tooltip` returns `type == "ability"` and a string matching precisely `A` followed by **16 hexadecimal characters**, **identical across three consecutive frames**. Print result prefix: `ABILITY_ID_CANDIDATE_UNVERIFIED_SOURCE` with only that uppercase ability-shaped ID.
- Otherwise prints a bounded `UNKNOWN` status, such as `TIMEOUT_NO_VALID_ID`, `TOOLTIP_API_FAILURE`, `CLOCK_UNAVAILABLE`, or a missing-API/registration status. Never prints raw `shown` variants, arbitrary objects, unit/buff IDs, source pointer values or the third/fourth tooltip results.
- Detaches by exact registered callback on success, timeout, cancellation and error (avoids one-match wildcard ambiguity if another handler shares a label). If detachment fails, the handler is marked inert and the result says `DETACH_UNCONFIRMED`. No game cast, movement, role change, UI click/macro automation, disk write, SavedVariables serialization or network action exists in the probe.
- **The returned ID is not automatically a Protector's Fury ID or a Legendary variant.** It can be misattributed if another ability tooltip was hovered; screenshot-level correlation with the native tooltip and current role is still required.
- On completion the probe may retain **one sanitized session-memory result**: allowlisted status, optional validated A+16-hex ID, finite start/finish frame clocks and detachment outcome—never raw tooltip/unit data. A new probe Run clears prior results. The separate copy helper prints and consumes the result only when an operator runs it; it does not inspect the tooltip or modify game state. Initial API/clock blockage or an unavailable completion clock can leave no retrievable record.

## Offline testing (not a live proof)

The historical source/fixture pair (SHA prefixes `b97bf0a1...` / `84f7704a...`) passed 110 Lua 5.4 assertions; a later source/fixture pair (`4b8a19e4...` / `194fbf53...`) passed 119 assertions after fixing the FreeBuff-identified transient tooltip-error stability defect. The previous high-FPS pair (`5e1c08f5...` / `343d904d...`) was read from Workbridge and executed entirely **in memory** through an existing assistant-container Lua 5.4 shared library, without writing scratch files, modifying addons or touching the game. A new 144-FPS/10-second fixture failed against the original 900-*total*-frame cutoff, then passed after the clock-progress/stall guard fix. **128 Lua 5.4 synthetic assertions passed**. The **prior exact-handler pair** (`f094213f...` / `146b5d42...`) added a competing-listener test and passed **136/136**. The **current three-file source/helper/fixture pair above** adds an optional sanitized one-shot copy record: a cache-required fixture failed against the old source and passed after implementation. **211/211 Lua 5.4 synthetic assertions pass**, printing `SC103_HOVER_PROBE_OFFLINE_TESTS_PASS 211`. Lua 5.1/physical RIFT execution remains unverified.

**Test coverage and limits:** The 211 assertions cover three-frame ID qualification, non-ability/unit/table payload suppression, initial settle, 12-second elapsed-clock expiry, a frozen-clock callback guard, realistic high-FPS progress, API failures, clock drift, event attach/exact-handler detachment with same-label collision, rerun, cancellation, reset after transient tooltip error, copy-once, PENDING, rearm invalidation, stale callback isolation, frame-clock expiry/backward checks, malformed input redaction and copied failed-detach warnings. The current source continues to use conventional Lua 5.1 syntax, but **Lua 5.1/RIFT-runtime compilation, current-PID LuaPad loading and native-tooltip ID results remain unverified**. Do not promote synthetic tests to an in-game success claim.

## Independent local reasoning review

Two independently prompted **local Gemma 4 12B reasoning workers**, each using one allowlisted read-only source-file tool call, finished in a supervised Ollama session (107,199 ms total). The manager accepted one missing combined negative test and rejected two source-inconsistent suggestions; a second worker confirmed the inability to infer selected Legendary state from an ID-shaped tooltip result. The [source-qualified worker receipt and critique](REA-RIFT-SPELLCASTING-LOCAL-REASONING-WORKER-PILOT-2026-11-03.md) records model/tool limits, failed Codex-provider attempts, findings and verified corrections. No model worker edited files or operated the game.

## New FreeBuff review and targeted correction (same day)

Two real **FreeBuff CLI reviews** completed using isolated Windows ConPTY source-copy sessions: SC-103 (59.3 seconds) and RC-30 (50.3 seconds). The SC-103 reviewer correctly identified that a transient tooltip API fault retained the prior 2/3 stable-sample state. The staged RRE source now clears `state.lastId` and `state.stable` on failure; the new regression fixture tests the condition. Full source hashes, actual FreeBuff completion receipts, proof limits and a parked RC-30 risk are recorded in [the FreeBuff review report](REA-RIFT-SPELLCASTING-FREEBUFF-REVIEW-2026-11-03.md). The operator now prefers **FreeBuff, not Ollama** for future agent delegation; the older Gemma/Ollama review above is historical only.

## Operator trial procedure — future only

**Preflight:** Confirm the physical client still has the intended character and matching RIFT build, and that LuaPad is *actually loaded*; an installed TOC alone is not proof. Keep RRECollector v0.4.10 frozen and the Workbridge GUI capture quarantine untouched. This procedure is optional and explicitly **not performed by this checkpoint**.

1. In the game, show the native **Righteous Defender** Soul Tree for Atank (if still current), with **Paladin 45 / Void Knight 15 / Paragon 0** and Legendary counters **0/3 / 0/2 / 0/1** as previously observed. Don't change role, Soul points, mentor level or talent allocations.
2. Open the already installed LuaPad via `/lp` if available, move its window away from the relevant Soul Tree icon, and copy/paste the *exact* `C:\work\rre\tools\sc103_luapad_hover_probe.lua` contents into the LuaPad editor. Click **Run** once. This is a **manual operator action**, not an automatic RRE command.
3. Watch LuaPad's **Output** pane for `ARMED_12_SECONDS`, then move the cursor directly to native **Protector's Fury** and hold the tooltip visible (avoid crossing another ability). Because the result is asynchronous, watch **RIFT chat** for `ABILITY_ID_CANDIDATE_UNVERIFIED_SOURCE`, timeout or failure; **Copy Output after the first Run captures synchronous text, not this async result**. **Capture native tooltip, role/Legendary counters and RIFT chat status in a screenshot before moving the cursor back to LuaPad**, since doing so can dismiss the tooltip. If an exact ability candidate appears, take one operator screenshot showing the **native tooltip, role context and RIFT chat result** together. Do not assume the scalar distinguishes Normal versus Legendary.
4. If the result is `UNKNOWN`, `BLOCKED_REQUIRED_API`, `DETACH_UNCONFIRMED` or no status appears, **stop** rather than forcing repeat trials or modifying installed addons. Reconcile the cause in a new bounded source-review step. Never paste arbitrary third-party scripts or a raw-tooltip dumper to compensate.
5. **Optional copyable result, after that screenshot:** Within **120 seconds of advancing `Inspect.Time.Frame` time** after completion, replace the LuaPad editor contents with the exact `C:\work\rre\tools\sc103_luapad_copy_result.lua`, click **Run once**, then click LuaPad **Copy Output**. The helper only prints synchronously in Output; the button performs the attempted clipboard transfer. `PENDING` means the original probe is still active; `NONE_OR_EXPIRED` does **not** establish a negative ability result. Retrieval consumes the record once, even if malformed or expired. The 120-second age check occurs **only when the helper runs** (not a wall-clock timer or automatic purge); missing/backward clocks reject it. Stop on `DETACH_UNCONFIRMED`. Copied text alone does not prove which native tooltip was hovered.


**Optional operator-run cancellation if no terminal status arrives:** In the already-open LuaPad editor, replace the probe text with this small snippet and click **Run once**. It calls the probe's existing in-memory stop method; it does not change SavedVariables or installed addons:

```lua
local s = rawget(_G, "__RRE_SC103_HOVER_PROBE_20261103")
if type(s) == "table" and type(s.stop) == "function" then
  s.stop("MANUAL_CANCEL")
else
  print("RRE SC103 hover: NO_ACTIVE_PROBE")
end
```

If cancellation reports `DETACH_UNCONFIRMED`, **stop all further probe runs**; the listener cannot be assumed removed. `NO_ACTIVE_PROBE` means only that the temporary global slot is absent, **not** that a previously failed detachment has been repaired. This snippet is an operator instruction and was **not run in game**.

**Evidence required for acceptance (G1 visual-only until separately repeated/session-bound evidence; not G2/G3 by itself):** Source-qualified screenshot bytes/UTC provenance plus visible role/tooltip, exact status and *an independently supported association* of the returned ID with that tooltip. Current screenshot still shows all zero Legendary counters, so no selected Legendary can be proven from this character's demonstrated state. An exact current tooltip candidate may resolve one normal/tooltip ID, **not** selection or eligibility. A copied result is only a convenience receipt; it cannot replace native-tooltip plus RIFT-chat visual correlation.

## Research state and stop conditions

- SC-103 **BLOCKED** until exact modern rank/variant/role mapping is justified by fresh role-bound evidence; the parked `Ability.New.List` native forwarding trace remains untouched.
- RC-30 **still requires** its own eight-slot → Pin → Undo before Reload UI → saved 0.4.10 evidence; this script does not certify RC-30 or unlock addon changes.
- Workbridge's quarantined `DESKTOP_TREE_UNSETTLED` GUI lease remains the separate desktop owner's responsibility. This tool does **not** capture screenshots, focus the game or bypass that lease.
- No automation or additional service is introduced; this is a **manually triggered, short-lived, source-and-test-qualified candidate probe**.
