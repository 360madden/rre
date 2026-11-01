# REA RIFT spellcasting — canonical Chat-mode resumption handoff

**Updated November 1, 2026. Owner: REA research. Target: LOCAL physical-PC RIFT, not VMware.**
**Latest checkpoints:** SC-604 interim mechanism map committed; SC-413 native diagnostic-source hypothesis parked; SC-414 twelve-screenshot visual audit blocked on source-qualified UI. **Next offline task: SC-415 saved SpellDump artifact discovery.** SC1/SC3/SC4/SC5/SC6 remain open.

## First reads after an interrupted Chat session

1. Workbridge `git_status(project="rre")` and `git_history(limit=4)` — **never reuse an old guessed HEAD**. Check any previously recorded command IDs before retrying. Keep two unrelated historical untracked files untouched: `docs/rea-raw-probe-profile-2026-10-18.json` and `tools/agents/ghidra/prepare_raw_probe.py`.
2. Read this file and [SC task register](REA-RIFT-SPELLCASTING-TASKS-2026-10-27.json); load only the next task's source dossier. Do **not** reread old 5 MB RR2 event captures unless a direct discrepancy requires it.
3. Original **physical-PC** executable: `C:\Program Files (x86)\Glyph\Games\RIFT\Live\rift_x64.exe`, SHA-256 `1935a05c9db6d468e34e0055014a4a99c1b5afceb1695884e24600f5c20a4be8`, length 60,493,640 bytes. Rehash before making new native claims. There were **zero local `rift_x64.exe` processes at 2026-11-01T18:46:10.7580551Z**. This is an observation at that time, not a permanent assumption.
4. Never modify RiftReader2/Workbridge source, restart game/VM, or issue mouse/keyboard/cast commands from this REA task. Historical RR2 records are read-only *old-build* evidence (SHA `7c356c9dde9e12fcbff3c08d953b0630b48b1510a0ffb36e4ec164606e7b17bd`), **not** proof of today's local client role/ability state.

## Accepted milestones and precise limits

| Area | State and verified source |
| --- | --- |
| **SC0 baseline and SC2 observed lifecycle** | **MAJOR PHASES COMPLETE** at old-build evidence scope; [SC0 handoff](REA-RIFT-SPELLCASTING-SC0-HANDOFF-2026-10-27.md) and [SC2 handoff](REA-RIFT-SPELLCASTING-SC2-HANDOFF-2026-10-27.md). |
| **SC1 spellbook** | **ACTIVE/BLOCKED:** historical 55-ID API catalog, 54/55 consistent details, but no local same-character spellbook/soul/role-level/queue-mode match. [SC-414](REA-RIFT-SPELLCASTING-SC414-SCREENSHOT-AUDIT-2026-11-01.md) reviewed 12 original late-October screenshots; none supplied a qualified spellbook/queue settings panel. A saved `SpellDump` initialization message is an output-location lead only. |
| **SC3 timing** | **ACTIVE/BLOCKED:** GCD and Full/Short/None queue enum unmeasured. Old source ~105–107 ms polling cannot prove server RTT, [clock audit](REA-RIFT-SPELLCASTING-SC304-TIMING-2026-10-27.md). |
| **SC4 native** | **ACTIVE/BLOCKED:** source-backed `/cast` callback `0x6C7450`, `/use` `0x6C7B90` and shared-context reads; [SC-412](REA-RIFT-SPELLCASTING-SC412-WRITER-GAP-2026-11-01.md) field-writer search and [SC-413](REA-RIFT-SPELLCASTING-SC413-ERROR-BRANCH-GAP-2026-11-01.md) error-text predecessor comparison are parked with exact original-source evidence. No source-qualified native ability resolver, cast-submission gate, GCD or server acknowledgment. |
| **SC5 outcomes** | **ACTIVE:** source-backed [SC-502 exact-ID attribution](REA-RIFT-SPELLCASTING-SC502-OUTCOME-2026-11-01.md) from historical events, while channel/proc/interruption SC-503 remains blocked. |
| **SC6 procedural continuity** | **SC-603 handoff complete; SC-604 interim source-backed synthesis accepted**, including current native queue config and honest historical event attribution. [SC-604 report](REA-RIFT-SPELLCASTING-SC604-INTERIM-MECHANISM-2026-11-01.md) and [machine map](REA-RIFT-SPELLCASTING-SC604-INTERIM-MECHANISM-2026-11-01.json). **SC-601/602 final synthesis/export and SC6 major phase remain open** pending SC1 and SC3 evidence. |

**Recent checkpoints:** `53ab715` (SC-603), `91db363` (SC-412), `1b537a0` (SC-604), `b0fac21` (SC-413). Read actual current Git HEAD for SC-414 integration and any newer work.

## Next research transaction — SC-415

**Question:** Did October 29's saved physical-PC RIFT chat message showing **SpellDump initialization** leave an accessible actual ability snapshot/export, or only addon source/commands?

- [SC-414 image audit](REA-RIFT-SPELLCASTING-SC414-SCREENSHOT-AUDIT-2026-11-01.md) directly reviewed 12 original saved JPGs, including enlarged `2026-10-29_020726.jpg` (SHA `e6f296be4f74765324023335f14ed1130d216dca547b13235b5ce1580d7052aa`). It shows RR2 Casting and SpellDump initialization text, **not** a proven exported spellbook. Source date/folder does not qualify current PE/character/role automatically.
- Two bounded read-only source groups: (1) currently disabled `SpellDump.disabled` and `spelldump2.disabled` addon directories under `C:\Users\mrkoo\OneDrive\Documents\RIFT\Interface\AddOns`, to learn exact export behavior; (2) existing accessible `rre`/`riftreader2` archived logs, saved reports or snapshots matching the October 29 label/time. No new addon activation or game input.
- Accept a found dump only with exact ability IDs, actual file hash, timestamp, character/role/session provenance and source interpretation; **initialization text by itself is not a dump**. If two bounded inventories find no saved output, park SC-415 and request the existing local-PC capture owner for a later same-character API+spellbook comparison.
- Do not revisit the 12 already reviewed images, restart the game, change installed addons or infer Full/Short/None mode from the native raw value 1.

## Chat-mode durability

One manager integrates. Workbridge **36 command/coordination slots are not 36 real AI agents**; parallel source-analysis commands may run without pretending they are independent reasoning sessions. Commit each accepted positive or negative finding together with its source SHA, exact job IDs and board status. Docs/board-only updates: run register/link/source checks and `node tools/validate-roadmap.mjs`, **not** the entire historical 500+ navigation suite. Never promise unattended research after a Chat turn ends.
