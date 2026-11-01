# REA RIFT spellcasting — canonical Chat-mode resumption handoff

**Updated November 1, 2026. Owner: REA research. Target: LOCAL physical-PC RIFT, not VMware.**
**Next substantive native task after handoff: SC-412** (bounded writer/producer of the common `+0x358` command-context byte). **SC6 full synthesis is NOT complete.** This is a durable checkpoint only.

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
| **SC4 native** | **ACTIVE:** actual source-backed `/cast` callback at RVA `0x6c7450`, but no cast-submission handler proven. [SC-409 cast vs use](REA-RIFT-SPELLCASTING-SC409-COMPARISON-2026-11-01.md) proves **17 common direct callee targets**; [SC-410 PE import map](REA-RIFT-SPELLCASTING-SC410-IMPORT-MAP-2026-11-01.md) proves **32 DLLs/811 imports**; [SC-411 context offsets](REA-RIFT-SPELLCASTING-SC411-CONTEXT-2026-11-01.md) proves **`+0x358` comparison in both command branches** and use-side `+0x340` pointer access. Semantics unknown. |
| **SC5 outcomes** | **ACTIVE:** source-backed [SC-502 exact-ID attribution](REA-RIFT-SPELLCASTING-SC502-OUTCOME-2026-11-01.md) from historical events, while channel/proc/interruption SC-503 remains blocked. |
| **SC6 procedural continuity** | **SC-603 handoff capability verified and checkpointed**. SC-601 full synthesis / SC-602 portable export still depend on SC1 spellbook and SC3 GCD evidence; do not claim SC6 phase complete. |

**Recent local commits to preserve:** `ccb0bf2` (SC-410), `550b9f3` (SC-409), `093c21e` (SC-411). The SC-603 handoff/checkpoint commit will come **after** this file; read current Git HEAD rather than expecting any static hash inside the handoff.

## Next research transaction — SC-412

**Question:** what *writes or constructs* the `+0x358` context flag read in both `/cast` and `/use`?

- [SC411 exact-source machine record](REA-RIFT-SPELLCASTING-SC411-CONTEXT-OFFSETS-2026-11-01.json). Cast-specific helper original `.pdata` region `0x57cda0–0x57d028`: source instruction at `0x57cdc4` is `cmp byte ptr [rcx+0x358],0`. Use-specific helper `0x57db60–0x57dbd7` saves first RCX pointer to RBX, then `0x57dba3` tests `[rbx+0x358]` and `0x57dbac` loads `[rbx+0x340]`.
- Use **one targeted bounded source producer/caller-context probe** first, not a full image displacement search, and record the original code bytes/hash, `.pdata` extent, hypotheses and falsifier. Never assign a meaning like `isCasting`, `inCombat` or `abilityQueue` from the offset alone.
- If two materially different bounded probes do not reveal a decision-changing producer, **park SC-412** and move to another original-client subsystem or a qualified new-source observation. A blocked result with a complete evidence receipt merits a commit, not an endless retry.

## Chat-mode durability

One manager integrates. Workbridge **36 command/coordination slots are not 36 real AI agents**; parallel source-analysis commands may run without pretending they are independent reasoning sessions. Commit each accepted positive or negative finding together with its source SHA, exact job IDs and board status. Docs/board-only updates: run register/link/source checks and `node tools/validate-roadmap.mjs`, **not** the entire historical 500+ navigation suite. Never promise unattended research after a Chat turn ends.
