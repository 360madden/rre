# RRE — Consolidated resume handoff (November 21, 2026, ~4:20 PM EST)

**Project:** RIFT Reverse Engineering (RRE)
**Coordinator:** active ChatGPT session; no independently executing AI workers were launched in this checkpoint
**Host:** **AMD-DESKTOP**, Workbridge 0.16.5-dev; repository **`C:\work\rre`**, branch `main`
**Before this handoff commit:** `e174f2608c647c11c4c016419f4fd5782c52d0f2` and `origin/main` synchronized
**Source of truth:** current `AGENTS.md` physical-only target override, `ROADMAP.md`, `docs/roadmap-tasks.json`, and the source-hashed notes linked below.

## Current verified status — do not infer more than the evidence

| Area | Current result | Proof boundary |
|---|---|---|
| Git checkout | `main...origin/main` matched at pre-handoff HEAD; no tracked dirt | Only nine long-standing unrelated untracked backup/research entries |
| Roadmap | **47 tasks**, **11 milestones**, 37 integrated / 8 blocked / 2 deferred, 9 WA-006 source pins and mutation negative passed | `rre_20261121_handoff_roadmap_01`, exit 0 |
| RRECollector addon on AMD-DESKTOP | v0.4.23 installed, **12/12** source-to-install SHA matches; TOC metadata includes Email | `rre_20261121_handoff_package_01`, exit 0; does not prove current UI load |
| SavedVariables | Root `0.4.23`, original file **68,045 B**, SHA-256 `e2333cd0aee47d510071a46904cc817e156afef107f8fa58dcf3b07583ce1c87`, modified 2026-11-21 12:43:14 EST | Last accepted abilities `0.4.20`, sequence 2, 55 records, `memoryPublication.status=not-published`; no `captureAttempt`, `unitAttempt`, or `unitSnapshotSequence` |
| Unit evidence | No v0.4.23 manual unit witness persisted; first-failure exporter and parser fixes source-verified | `rre_20261121_handoff_readiness_01`, exit 0: `unitValidation.status=absent`; `acceptedUnitsPresent=false` |
| Physical RIFT window **now** | **PID 48468**, HWND **7145554**; `rift_x64`, background window; executable path `C:\Program Files (x86)\Glyph\Games\RIFT\Live\rift_x64.exe` | PID started **2026-11-21 16:12:49.399744 EST** (`rre_20261121_consolidated_handoff_process_01`, exit 0). Previous PID **37676** belongs to an *older process epoch*, not this one; no current mapped-memory image attestation |
| WA-006 / WA-007 | **BLOCKED** | 18 historical native nonself candidates in PID 51524, one unrelated older self-only Lua/native crosswalk in PID 18092; no same-scene/current-epoch two-nonself exact-ID correlation or proven physics gameplay owner |

**Historical current-build disk source:** November 17 build `STABLE-1-1179-a-1256672` executable 60,574,536 bytes, SHA-256 `df954b798331e18359be62a31cc74b49fc3f50b87385ebb080a5448256322c01`. This is **on-disk/archived source identity**, not proof that the newly running PID 48468 has matching mapped bytes or that a previous debugger/adapter is compatible. Revalidate process, file and owner before any live experiment.

**RIFT operating constraints:** Only the local physical RIFT client on an independently verified AMD-DESKTOP or LEGION may be considered; **no VMware labs**. No new game input, camera movement, `/reloadui`, addon deployment, debugger attach, native memory access, game restart, or OS restart was performed for this handoff. Do not assume a prior user-approved operation gives permission for unrelated live tests. RC-30 Pin/Undo/Reload and RC-88 quests investigations remain **operator-stopped**. Do not use Codex CLI, Ollama, OpenCode or FreeBuff as substitute subagents. Real AI agents and ordinary Workbridge command slots are distinct; Workbridge RRE agent registry currently lists **zero** tasks/owners.

## Completed and pushed milestones to preserve

| Git commit | Result |
|---|---|
| `e174f26` | **V2 lossless all-calling static catalog**: strict offline Lua literal parser `tools/parse-pab-soul-literal.mjs`, updated inventory generator/tests, separate source-hashed JSON and report. **56/56 soul files, 1,434 entries, 1,433 unique IDs**. Cleric Purifier's two *Flame Lance* declarations preserved individually with original lines 18/22; cross-calling *Dismiss Pet* ID retained under Cleric Druid and Rogue Ranger. V1 preserved unmodified. |
| `0a3b654` | Initial offline all-calling index: 55/56 sources, 1,405 entries, Purifier originally quarantined (historical V1 record only). |
| `100bef0` | Strict exporter now handles a genuine first failed `/rre units` as `snapshotState=attempt-only` rather than claiming malformed snapshot; readiness and Lua 5.1→SavedVariables→Node tests verified; **45/45** combined regression and **67/67** WA-006 G2 prior tests. |
| `758a229` | Pinned native Windows Lua 5.1 producer → original-literal SavedVariables → strict Node export round-trip (7 then 9 scenarios in later milestone). |
| `609081b` | Readiness checker only treats a complete, structurally valid v0.4.23 unit snapshot as accepted; no fabricated success from a positive sequence. |
| `9bcbdec` | v0.4.23 physically installed on AMD-DESKTOP after a hash-confirmed backup of all 11 former v0.4.21 files. Rollback: `C:\work\rre\artifacts\rrecollector-v0421-backup-20261121-1214-est`. No rollback executed. |
| `c7aae0a` | WA-006 G2 preliminary Lua API sampling triage; explicitly rejects false native/scene/time acceptance. |

**Latest focused reruns, this handoff:** `rre_20261121_handoff_pab_9tests_01` **9/9**, `rre_20261121_handoff_roadmap_01` **47/47 tasks**, `rre_20261121_handoff_package_01` **12/12 installed files**, and `rre_20261121_handoff_readiness_01` **saved diagnostics reproduced**, all exit 0. Original V2 dataset `docs/RRECOLLECTOR-ALL-CALLINGS-STATIC-CANDIDATES-LOSSLESS-2026-11-21.json` is **449,055 bytes**, SHA-256 `5685fa02b82b9802739f85348dcf1d0514a8b1b3e39353cf80f96135cc36908c`, ordered original-source manifest SHA-256 `898f651e8fd272dc220fe0c32aecbb3e937dac750d6d9b912b1f94ab561eb5bb`.

**Important static/native caution:** `docs/RRE-WA006-VTABLE-RECONCILIATION-2026-11-18.md` corrects the ambiguous adjacency of constructor references to vptrs `0x271E468` and `0x271E470`; the repeated pointer to `0x78D920` is source-real but **does not** establish that the same wrapper receiver executes its `+8` store. Preserve `sameWrapperField8WriterQualified=false`, `ownerQualified=false` and `runtimeQualified=false`. Avoid repeating the already-negative broad scans.

## Most useful next execution sequence

1. **P0 — Physical Collector acceptance, operator-coordinated (recommended):** First re-verify host, new physical PID/start/HWND and current game owner. Confirm visible loaded v0.4.23 and any addon errors. Only then manually issue `/rre status`, `/rre capture`, `/rre units` in a suitable gameplay scene and use normal `/reloadui` or logout to persist. A UI reload is **not** a game/Windows restart, but still needs game-control authorization. Run the existing strict readiness checker on **original** character SavedVariables, and `tools/export-rrecollector-units.mjs` after a new unit attempt. **Expected:** version-matched accepted capture(s), or a precise error/unavailable/partial reason; never invent live acceptance. **Execution:** Joey/game operator for input; coordinator can autonomously validate persisted files.
2. **P1 — Build a narrow calling-filtered static candidate research plan (offline autonomous):** Consume V2 data without modifying its original source, preserve calling/soul/ID/line provenance, start with a few source-hashed canary IDs rather than a 1,433-ID in-game sweep. Do not label static source IDs as known, learned, unlockable or castable. Defer installing any new RRECollector release until the current v0.4.23 acceptance gate is understood. **Expected:** reviewed versioned candidate subset and reproducible tests, without game input.
3. **P2 — WA-006 current native receiver / entity qualification (offline first; controlled live evidence later):** Reuse existing source-pinned verifier, archived native and Lua receipts, and G2 rejection-only validators. Prioritize a concrete instruction-aligned dispatch/receiver for `0x78D920` or same-epoch independent nonself Lua/native unit IDs, with authentic original hashes, process-start ticks, time brackets, and separate scene witness. No current-build offsets presumed valid from a disk SHA. **Expected:** specific new source-qualified relationship or documented rejection, not an unsupported gameplay-owner claim.

## Reproduction commands (PowerShell, in C:\work\rre)

```powershell
node tools/validate-roadmap.mjs
node --test tools/test-inventory-pab-static-abilities.mjs
node --test tools/test-rrecollector-units-lua-roundtrip.mjs tools/test-export-rrecollector-units.mjs tools/test-audit-rrecollector-readiness.mjs
node tools/verify-rrecollector-package.mjs --installed "C:\Users\mrkoo\OneDrive\Documents\RIFT\Interface\AddOns\RRECollector"
git status --short
```

Files to read first: `docs/REA-RIFT-SPELLCASTING-SESSION-HANDOFF-2026-11-21.md` (full incremental chronology), `docs/RRECOLLECTOR-V0423-PHYSICAL-INSTALL-2026-11-21.md` (backup and parity), `docs/RRECOLLECTOR-ALL-CALLINGS-STATIC-CANDIDATES-LOSSLESS-2026-11-21.md` (V2 static source), `docs/RRE-WA006-VTABLE-RECONCILIATION-2026-11-18.md` (critical native false-positive correction), `docs/RRE-WA006-RECORDED-EVIDENCE-REUSE-PLAN-2026-11-16.md` (WA-006 evidence gates).

**Worktree preservation:** Nine inherited untracked paths (seven `docs/rc*-host-backup-20261102/` / `docs/rc32-v0410-host-backup-20261105/`-style backup folders, `docs/rea-raw-probe-profile-2026-10-18.json`, and `tools/agents/ghidra/prepare_raw_probe.py`) were **not** part of this handoff and must not be staged or deleted. Git commit and push status for *this new handoff* must be verified separately in the conversation, rather than assumed from this file.
