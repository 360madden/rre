# REA RIFT spellcasting — canonical Chat-mode resumption handoff

**Updated November 1, 2026. Owner: REA research. Target: LOCAL physical-PC RIFT, not VMware.**
**Latest checkpoint:** SC-604 map committed; SC-413 native diagnostic, SC-414 saved screenshots, and SC-415 SpellDump output hypotheses all source-documented and parked. **SC-102 is next but BLOCKED on current physical-PC API + spellbook/soul UI evidence from the existing capture owner.** SC1/SC3/SC4/SC5/SC6 remain open.

## First reads after an interrupted Chat session

1. Workbridge `git_status(project="rre")` and `git_history(limit=4)` — **never reuse an old guessed HEAD**. Check any previously recorded command IDs before retrying. Keep two unrelated historical untracked files untouched: `docs/rea-raw-probe-profile-2026-10-18.json` and `tools/agents/ghidra/prepare_raw_probe.py`.
2. Read this file and [SC task register](REA-RIFT-SPELLCASTING-TASKS-2026-10-27.json); load only the next task's source dossier. Do **not** reread old 5 MB RR2 event captures unless a direct discrepancy requires it.
3. Original **physical-PC** executable: `C:\Program Files (x86)\Glyph\Games\RIFT\Live\rift_x64.exe`, SHA-256 `1935a05c9db6d468e34e0055014a4a99c1b5afceb1695884e24600f5c20a4be8`, length 60,493,640 bytes. Rehash before making new native claims. There were **zero local `rift_x64.exe` processes at 2026-11-01T18:46:10.7580551Z**. This is an observation at that time, not a permanent assumption.
4. Never modify RiftReader2/Workbridge source, restart game/VM, or issue mouse/keyboard/cast commands from this REA task. Historical RR2 records are read-only *old-build* evidence (SHA `7c356c9dde9e12fcbff3c08d953b0630b48b1510a0ffb36e4ec164606e7b17bd`), **not** proof of today's local client role/ability state.

## Accepted milestones and precise limits

| Area | State and verified source |
| --- | --- |
| **SC0 baseline and SC2 observed lifecycle** | **MAJOR PHASES COMPLETE** at old-build evidence scope; [SC0 handoff](REA-RIFT-SPELLCASTING-SC0-HANDOFF-2026-10-27.md) and [SC2 handoff](REA-RIFT-SPELLCASTING-SC2-HANDOFF-2026-10-27.md). |
| **SC1 spellbook** | **BLOCKED:** 55 historical API IDs are cataloged but current physical-PC known/learnable/rank/role status is unproven. [SC-414](REA-RIFT-SPELLCASTING-SC414-SCREENSHOT-AUDIT-2026-11-01.md) found no qualifying UI across 12 sampled originals; [SC-415](REA-RIFT-SPELLCASTING-SC415-SPELLDUMP-OUTPUT-GAP-2026-11-01.md) found only copyable-addon source and no source-qualified October 29 exported list in bounded accessible paths. Actual new API+UI source needed. |
| **SC3 timing** | **ACTIVE/BLOCKED:** GCD and Full/Short/None queue enum unmeasured. Old source ~105–107 ms polling cannot prove server RTT, [clock audit](REA-RIFT-SPELLCASTING-SC304-TIMING-2026-10-27.md). |
| **SC4 native** | **ACTIVE/BLOCKED:** source-backed `/cast` callback `0x6C7450`, `/use` `0x6C7B90` and shared-context reads; [SC-412](REA-RIFT-SPELLCASTING-SC412-WRITER-GAP-2026-11-01.md) field-writer search and [SC-413](REA-RIFT-SPELLCASTING-SC413-ERROR-BRANCH-GAP-2026-11-01.md) error-text predecessor comparison are parked with exact original-source evidence. No source-qualified native ability resolver, cast-submission gate, GCD or server acknowledgment. |
| **SC5 outcomes** | **ACTIVE:** source-backed [SC-502 exact-ID attribution](REA-RIFT-SPELLCASTING-SC502-OUTCOME-2026-11-01.md) from historical events, while channel/proc/interruption SC-503 remains blocked. |
| **SC6 procedural continuity** | **SC-603 handoff complete; SC-604 interim source-backed synthesis accepted**, including current native queue config and honest historical event attribution. [SC-604 report](REA-RIFT-SPELLCASTING-SC604-INTERIM-MECHANISM-2026-11-01.md) and [machine map](REA-RIFT-SPELLCASTING-SC604-INTERIM-MECHANISM-2026-11-01.json). **SC-601/602 final synthesis/export and SC6 major phase remain open** pending SC1 and SC3 evidence. |

**Recent checkpoints:** `91db363` (SC-412), `1b537a0` (SC-604), `b0fac21` (SC-413), `277358c` (SC-414). Read current Git HEAD for the SC-415 integration hash and any subsequent work.

## Next evidence gate — SC-102 (currently blocked on a local source)

**Need:** one current **physical-PC** RIFT same-character/same-role comparison of known-ability API records with spellbook, soul/trainer and action-bar UI. Offline source-only research has reached its stopping rule; do not claim SC1 or SC3 phase completion.

- [SC-414](REA-RIFT-SPELLCASTING-SC414-SCREENSHOT-AUDIT-2026-11-01.md) source-hashed 12 late-October original screenshots; none had a source-qualified spellbook or selected queue-mode UI. [SC-415](REA-RIFT-SPELLCASTING-SC415-SPELLDUMP-OUTPUT-GAP-2026-11-01.md) checked accessible saved SpellDump addon output paths. Its source creates a **copyable UI dump** but does not auto-persist complete ability records; no qualified October 29 export was found in bounded checks, and a broad ignored RR2 archive scan was time-limited.
- The **existing RR2/local-PC live-capture owner** must provide executable SHA, current character ID/calling/level, active role/soul allocation, exact-time `Inspect.Ability.New.List/Detail` IDs and fields, spellbook/soul/trainer screenshots and action-bar snapshot. Preserve null/missing metadata, rank and ID variants, and reason-coded known/learnable/locked/usable/bound distinctions.
- For SC3, separately bind **two abilities' same-frame readiness** and current `Full/Short/None` selected UI mode to the native raw `ActionBars_AbilityQueue` field; raw `1` alone has no proved mode mapping.
- No RRE-owned game input, addon activation, process manipulation, VM use or full-client import. Do not rerun parked SC-412/413/414/415 routes without an explicitly new discriminator. If current local game/session evidence is unavailable, remain blocked with this durable handoff.

## Chat-mode durability

One manager integrates. Workbridge **36 command/coordination slots are not 36 real AI agents**; parallel source-analysis commands may run without pretending they are independent reasoning sessions. Commit each accepted positive or negative finding together with its source SHA, exact job IDs and board status. Docs/board-only updates: run register/link/source checks and `node tools/validate-roadmap.mjs`, **not** the entire historical 500+ navigation suite. Never promise unattended research after a Chat turn ends.
