# CURRENT HANDOFF — REA RIFT spellcasting research

**IMPORTANT TARGET SWITCH (user instruction Oct 27):** REA uses **RIFT installed and running on this physical PC**, **not VMware**. [Confirmed local target](REA-RIFT-LOCAL-PC-TARGET-2026-10-27.md), path `C:\Program Files (x86)\Glyph\Games\RIFT\Live\rift_x64.exe`, SHA `1935a05c9db6d468e34e0055014a4a99c1b5afceb1695884e24600f5c20a4be8`. Read-only process inspection at 13:21:39 UTC showed **one local running RIFT process**, PID 66436; recheck volatile PID before runtime use. Current SC-401 schema-name branch is parked after two nondecisive probes; continue SC-402 on this local binary, not Lab-2. No VMware guest hash is needed for this REA work.

**Updated:** October 27, 2026. **Next REA task:** `SC-402` — investigate local-client native castbar/readiness data flow, starting from source-backed `Inspect.Unit.Castbar` metadata; no whole-PE import. SC-306 Full/Short/None value mapping is parked until same-session UI evidence exists.
**Scope:** REA research only; RR2/Workbridge implementation remains separate. SC-305 used bounded **read-only live local process memory** to inspect one numeric setting (no writes/input/VM); no full REA/Ghidra import.

## Last accepted checkpoints

| Result | Local commit | What is actually established |
| --- | --- | --- |
| **SC0 PHASE COMPLETE** | `e76e6b2` | Two source-hash-verified RR2 snapshots contain identical 55 API-returned ability lookup IDs; learnability UI still unknown |
| **SC-101 COMPLETE** | `4eea4e9` | [55-row JSONL](REA-RIFT-SPELLCASTING-SC1-API-CATALOG-2026-10-27.jsonl) and [CSV](REA-RIFT-SPELLCASTING-SC1-API-CATALOG-2026-10-27.csv), unknown fields preserved |
| **SC-104 COMPLETE** | `4c29597` | 10/55 API-listed abilities have explicit `unusable=true`; listing ≠ readiness |
| **SC2 PHASE COMPLETE** | `41e7fc6` | [Observed cast lifecycle](REA-RIFT-SPELLCASTING-SC2-LIFECYCLE-2026-10-27.md): cooldown Begin → target dodge/hit → cooldown End, host input remains a separate receipt |
| **SC-303 COMPLETE** | `e7937a0` | [Cast/channel metadata and cadence](REA-RIFT-SPELLCASTING-SC303-TIMING-METADATA-2026-10-27.md): 9 cast-time entries, 2 channel flags, no sampled active castbar in 1,125 real samples; SC3 GCD still open |
| **October 27 LOCAL RIFT build PINNED** | `6a8c0ae` | [New x64 executable](REA-RIFT-BUILD-UPDATE-2026-10-27.md), SHA `1935a05c…be8`; local process path and sampled mapped code bytes later matched disk; VM is no longer a prerequisite |
| **SC-304 COMPLETE** | `9adc7cd` | [Clock-domain precision audit](REA-RIFT-SPELLCASTING-SC304-TIMING-2026-10-27.md): 565/560 samples, same-clock event order and source bracketing, but **no RTT or independently proven GCD** |
| **SC-404 COMPLETE (new-build data anchors)** | `d8ba4fa` | [New build source dossier](REA-RIFT-SPELLCASTING-SC404-NATIVE-DOSSIER-2026-10-27.md): `New.List`, `New.Detail`, `Unit.Castbar` strings and `.data` pointers; **no handler or guest compatibility proven** |
| **SC-401 PARKED** | `d4dc272` | [Native code xrefs](REA-RIFT-SPELLCASTING-SC401-NATIVE-XREFS-2026-10-27.md) led into generic allocator/tree/container management; enumeration callback remains unverified; reopen only on new evidence |
| **SC-305 COMPLETE** | `7b8de64` | [Local RIFT ability-queue setting field](REA-RIFT-SPELLCASTING-SC305-QUEUE-DOSSIER-2026-10-27.md): source-backed `ActionBars_AbilityQueue` at settings-object offset `+0xA4`; currently numeric **1**, user-facing mode not yet qualified |
| **SC-306 BLOCKED, not guessed** | See latest Git log | [Full/Short/None enum gap](REA-RIFT-SPELLCASTING-SC306-QUEUE-ENUM-GAP-2026-10-27.md): 329 static setting-global xref candidates clustered in 27 settings-region functions; current RIFT background and no matching UI-label evidence |

**Phase handoffs:** [SC0](REA-RIFT-SPELLCASTING-SC0-HANDOFF-2026-10-27.md) · [SC2](REA-RIFT-SPELLCASTING-SC2-HANDOFF-2026-10-27.md). [Task register](REA-RIFT-SPELLCASTING-TASKS-2026-10-27.json) is authoritative for the next ready task.

## Current blockers and next work

- **SC1 NOT COMPLETE:** the native RIFT spellbook/soul-tree/trainer UI and matching character level, active Role, points/rank are absent. SC-102 cannot claim "learnable at current level"; SC-103 names with multiple IDs cannot yet be mapped confidently to roles/ranks.
- **SC3 NOT COMPLETE:** SC-305 recovered the local native ability-queue setting storage and raw **1**, but the mapping to Full/Short/None and actual queue/cast behavior is unverified. Cross-ability shared GCD also remains unverified.
- **SC4 native REA active, no phase completion:** patched local PC binary source has confirmed RIP-relative code references to ability/castbar descriptor regions, with three bounded function SHA fingerprints. These are **not** verified native enumeration/casting handlers. Do not launch old >450s whole-PE imports.

**SC-402 next:** [SC-404 native API anchors](REA-RIFT-SPELLCASTING-SC404-NATIVE-DOSSIER-2026-10-27.md) include `Inspect.Unit.Castbar` (literal RVA `0x26d8d60`) and a data descriptor at `0x2f649f0`; [SC-401 source dossier](REA-RIFT-SPELLCASTING-SC401-NATIVE-XREFS-2026-10-27.md) bounds a code region `0x9b84f0–0x9b88cd`. Check its next source-backed call/value flow to determine whether it only builds API descriptors or reads actual cast state; do not infer a GCD from names. SC-306 queue-mode numeric mapping is **blocked** pending actual UI label evidence, not a reason to stall independent research. Game target stays physical PC RIFT, SHA `1935a05c…be8`; do not use VMware or change game focus for this probe.

**Resume:** check latest RRE Git HEAD/status and the SC task register, then one bounded read-only query. Existing RR2 remains clean and unmodified by REA; two historical untracked RRE raw-probe files must be preserved. This project has no promise of background work between Chat turns.
