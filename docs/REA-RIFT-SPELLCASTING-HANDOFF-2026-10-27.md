# REA RIFT spellcasting — canonical Chat-mode resumption handoff

**Updated November 1, 2026. Owner: REA research. Target: LOCAL physical-PC RIFT, not VMware.**
**Latest checkpoints: SC-604 interim mechanism map committed; SC-413 bounded error-path check parked** after mirrored native text-formatting comparison. **Next offline task: SC-414 saved physical-PC screenshot audit.** SC6 final mechanism synthesis remains incomplete.

## First reads after an interrupted Chat session

1. Workbridge `git_status(project="rre")` and `git_history(limit=4)` — **never reuse an old guessed HEAD**. Check any previously recorded command IDs before retrying. Keep two unrelated historical untracked files untouched: `docs/rea-raw-probe-profile-2026-10-18.json` and `tools/agents/ghidra/prepare_raw_probe.py`.
2. Read this file and [SC task register](REA-RIFT-SPELLCASTING-TASKS-2026-10-27.json); load only the next task's source dossier. Do **not** reread old 5 MB RR2 event captures unless a direct discrepancy requires it.
3. Original **physical-PC** executable: `C:\Program Files (x86)\Glyph\Games\RIFT\Live\rift_x64.exe`, SHA-256 `1935a05c9db6d468e34e0055014a4a99c1b5afceb1695884e24600f5c20a4be8`, length 60,493,640 bytes. Rehash before making new native claims. There were **zero local `rift_x64.exe` processes at 2026-11-01T18:46:10.7580551Z**. This is an observation at that time, not a permanent assumption.
4. Never modify RiftReader2/Workbridge source, restart game/VM, or issue mouse/keyboard/cast commands from this REA task. Historical RR2 records are read-only *old-build* evidence (SHA `7c356c9dde9e12fcbff3c08d953b0630b48b1510a0ffb36e4ec164606e7b17bd`), **not** proof of today's local client role/ability state.

## Accepted milestones and precise limits

| Area | State and verified source |
| --- | --- |
| **SC0 baseline and SC2 observed lifecycle** | **MAJOR PHASES COMPLETE** at old-build evidence scope; [SC0 handoff](REA-RIFT-SPELLCASTING-SC0-HANDOFF-2026-10-27.md) and [SC2 handoff](REA-RIFT-SPELLCASTING-SC2-HANDOFF-2026-10-27.md). |
| **SC1 spellbook** | **ACTIVE/BLOCKED:** 55 API-listed historical ability IDs, 54/55 detailed records equal across two captures; [SC103 rank/Role gap](REA-RIFT-SPELLCASTING-SC103-RANK-ROLE-GAP-2026-11-01.md). Actual local same-character spellbook/soul/role-level snapshots missing. |
| **SC3 timing** | **ACTIVE/BLOCKED:** GCD and Full/Short/None queue enum unmeasured. Old source ~105–107 ms polling cannot prove server RTT, [clock audit](REA-RIFT-SPELLCASTING-SC304-TIMING-2026-10-27.md). |
| **SC4 native** | **ACTIVE/BLOCKED:** source-backed `/cast` callback `0x6C7450`, `/use` `0x6C7B90` and shared-context reads; [SC-412](REA-RIFT-SPELLCASTING-SC412-WRITER-GAP-2026-11-01.md) field-writer search and [SC-413](REA-RIFT-SPELLCASTING-SC413-ERROR-BRANCH-GAP-2026-11-01.md) error-text predecessor comparison are parked with exact original-source evidence. No source-qualified native ability resolver, cast-submission gate, GCD or server acknowledgment. |
| **SC5 outcomes** | **ACTIVE:** source-backed [SC-502 exact-ID attribution](REA-RIFT-SPELLCASTING-SC502-OUTCOME-2026-11-01.md) from historical events, while channel/proc/interruption SC-503 remains blocked. |
| **SC6 procedural continuity** | **SC-603 handoff complete; SC-604 interim source-backed synthesis accepted**, including current native queue config and honest historical event attribution. [SC-604 report](REA-RIFT-SPELLCASTING-SC604-INTERIM-MECHANISM-2026-11-01.md) and [machine map](REA-RIFT-SPELLCASTING-SC604-INTERIM-MECHANISM-2026-11-01.json). **SC-601/602 final synthesis/export and SC6 major phase remain open** pending SC1 and SC3 evidence. |

**Recent checkpoints:** `093c21e` (SC-411), `53ab715` (SC-603), `91db363` (SC-412), `1b537a0` (SC-604). The SC-413 evidence commit should be discovered by querying current Git HEAD; do not assume hashes persist across interrupted sessions.

## Next research transaction — SC-414

**Question:** can an already-saved **physical-PC RIFT** screenshot supply actual visual evidence of the active character's spellbook, soul/role allocation or selected Ability Queue setting, with a credible build/time/identity binding?

- Workbridge has access to `C:\Users\mrkoo\OneDrive\Documents\RIFT\Screenshots`. The newest RIFT JPGs include late-October 2026 files, but their filenames alone prove **no specific UI content**. Enumerate at most 12 relevant originals, retain source SHA and timestamp, and visually review actual pixels using an existing supported image path before classifying UI.
- A screenshot without current process/build/character identity may be a visual clue but **not** a matching present-day API or queue-mode proof. Keep `Inspect.Ability.New.List/Detail` IDs, active role/soul and UI labels distinct unless source-bound in the same local session.
- Do **not** create an imaging-tool substitute until existing capture/preview routes are checked. A bounded attempt to use Pillow in `rre/.venv` and `C:\Python314` found it unavailable; no dependencies were installed. No live game input or screenshots are requested by this offline task.
- If no source-qualified spellbook/queue image is found in the bounded set, record the exact insufficiency and park; require the existing local-PC live-capture owner for a future new observation. Do not reopen generic SC-413 text-formatting xrefs.

## Chat-mode durability

One manager integrates. Workbridge **36 command/coordination slots are not 36 real AI agents**; parallel source-analysis commands may run without pretending they are independent reasoning sessions. Commit each accepted positive or negative finding together with its source SHA, exact job IDs and board status. Docs/board-only updates: run register/link/source checks and `node tools/validate-roadmap.mjs`, **not** the entire historical 500+ navigation suite. Never promise unattended research after a Chat turn ends.
