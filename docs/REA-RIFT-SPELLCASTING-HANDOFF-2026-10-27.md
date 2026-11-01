# REA RIFT spellcasting — canonical Chat-mode resumption handoff

**Updated November 1, 2026. Owner: REA research. Target: LOCAL physical-PC RIFT, not VMware.**
**Latest accepted checkpoint: SC-604 interim mechanism map** (readable report plus source-pinned JSON). **Next bounded native task: SC-413** (unknown-ability branch predecessor compared with /use negative control). **SC6 full synthesis remains incomplete.**

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
| **SC4 native** | **ACTIVE:** source-backed `/cast` callback RVA `0x6c7450`, 17 shared `/cast`/`/use` target RVAs, command-context `+0x358` reads and `+0x340` use pointer. [SC-412 writer hypothesis](REA-RIFT-SPELLCASTING-SC412-WRITER-GAP-2026-11-01.md) was parked after two bounded negative probes. Meaning of shared fields, ability resolver, successful cast submission and server path are unknown. |
| **SC5 outcomes** | **ACTIVE:** source-backed [SC-502 exact-ID attribution](REA-RIFT-SPELLCASTING-SC502-OUTCOME-2026-11-01.md) from historical events, while channel/proc/interruption SC-503 remains blocked. |
| **SC6 procedural continuity** | **SC-603 handoff complete; SC-604 interim source-backed synthesis accepted**, including current native queue config and honest historical event attribution. [SC-604 report](REA-RIFT-SPELLCASTING-SC604-INTERIM-MECHANISM-2026-11-01.md) and [machine map](REA-RIFT-SPELLCASTING-SC604-INTERIM-MECHANISM-2026-11-01.json). **SC-601/602 final synthesis/export and SC6 major phase remain open** pending SC1 and SC3 evidence. |

**Recent checkpoints:** `ccb0bf2` (SC-410), `550b9f3` (SC-409), `093c21e` (SC-411), `53ab715` (SC-603), `91db363` (SC-412). The SC-604 integration commit is recorded in Git history; read current HEAD rather than assume a static hash here.

## Next research transaction — SC-413

**Question:** do the source-byte branch predicates immediately upstream of the native `/cast` unknown-ability diagnostic differ meaningfully from the `/use` unknown-item negative control, and can that discriminate an ability-lookup result without assigning invented semantics?

- Original physical-PC PE SHA is pinned above. Examine only known diagnostic xref neighborhoods: `/cast` `0x6C78B2/0x6C78DD/0x6C7922` versus `/use` `0x6C86A7/0x6C86D2/0x6C8716`. Confirm original bytes, exact branch/producer instruction RVAs and `.pdata` boundaries; use [SC-409](REA-RIFT-SPELLCASTING-SC409-COMPARISON-2026-11-01.md) and [SC-412](REA-RIFT-SPELLCASTING-SC412-WRITER-GAP-2026-11-01.md).
- Do **not** repeat generic SC-408 helper tracing, SC-412 `+0x358` writer scans or full-program REA imports. One discriminating source claim per research transaction; stop after at most two substantively different non-decisive probes.
- Record source SHA, job IDs, positive/negative result and explicit unresolved ability-resolution/queue/server boundary. Commit a coherent result or a parked blocker, then refresh the handoff.

## Chat-mode durability

One manager integrates. Workbridge **36 command/coordination slots are not 36 real AI agents**; parallel source-analysis commands may run without pretending they are independent reasoning sessions. Commit each accepted positive or negative finding together with its source SHA, exact job IDs and board status. Docs/board-only updates: run register/link/source checks and `node tools/validate-roadmap.mjs`, **not** the entire historical 500+ navigation suite. Never promise unattended research after a Chat turn ends.
