# CURRENT HANDOFF — REA RIFT spellcasting research

**IMPORTANT TARGET SWITCH (user instruction Oct 27):** REA uses **RIFT installed and running on this physical PC**, **not VMware**. [Confirmed local target](REA-RIFT-LOCAL-PC-TARGET-2026-10-27.md), path `C:\Program Files (x86)\Glyph\Games\RIFT\Live\rift_x64.exe`, SHA `1935a05c9db6d468e34e0055014a4a99c1b5afceb1695884e24600f5c20a4be8`. Read-only process inspection at 13:21:39 UTC showed **one local running RIFT process**, PID 66436; recheck volatile PID before runtime use. Continue SC-401 on this local binary, not Lab-2. No need for a VMware guest hash to study local game executable.

**Updated:** October 27, 2026. **Next REA task:** `SC-401` — targeted client-side enumeration-handler/xref investigation from the NEW build's `Inspect.Ability.New.List` descriptor; no whole-PE import.
**Scope:** REA research only; RR2/Workbridge implementation and live controls remain separately owned. All tasks through this handoff were **file-based** with no new gameplay input or REA binary import.

## Last accepted checkpoints

| Result | Local commit | What is actually established |
| --- | --- | --- |
| **SC0 PHASE COMPLETE** | `e76e6b2` | Two source-hash-verified RR2 snapshots contain identical 55 API-returned ability lookup IDs; learnability UI still unknown |
| **SC-101 COMPLETE** | `4eea4e9` | [55-row JSONL](REA-RIFT-SPELLCASTING-SC1-API-CATALOG-2026-10-27.jsonl) and [CSV](REA-RIFT-SPELLCASTING-SC1-API-CATALOG-2026-10-27.csv), unknown fields preserved |
| **SC-104 COMPLETE** | `4c29597` | 10/55 API-listed abilities have explicit `unusable=true`; listing ≠ readiness |
| **SC2 PHASE COMPLETE** | `41e7fc6` | [Observed cast lifecycle](REA-RIFT-SPELLCASTING-SC2-LIFECYCLE-2026-10-27.md): cooldown Begin → target dodge/hit → cooldown End, host input remains a separate receipt |
| **SC-303 COMPLETE** | `e7937a0` | [Cast/channel metadata and cadence](REA-RIFT-SPELLCASTING-SC303-TIMING-METADATA-2026-10-27.md): 9 cast-time entries, 2 channel flags, no sampled active castbar in 1,125 real samples; SC3 GCD still open |
| **October 27 RIFT host build PINNED** | `6a8c0ae` | [New x64 host executable](REA-RIFT-BUILD-UPDATE-2026-10-27.md), SHA `1935a05c…be8`; 7 PE section hashes verified; current running VM is **Lab-2**, guest build unknown |
| **SC-304 COMPLETE** | `9adc7cd` | [Clock-domain precision audit](REA-RIFT-SPELLCASTING-SC304-TIMING-2026-10-27.md): 565/560 samples, same-clock event order and source bracketing, but **no RTT or independently proven GCD** |
| **SC-404 COMPLETE (new-build data anchors)** | `d8ba4fa` | [New build source dossier](REA-RIFT-SPELLCASTING-SC404-NATIVE-DOSSIER-2026-10-27.md): `New.List`, `New.Detail`, `Unit.Castbar` strings and `.data` pointers; **no handler or guest compatibility proven** |
| **SC-401 PARTIAL (code xrefs)** | See latest Git log | [New-build code xrefs](REA-RIFT-SPELLCASTING-SC401-NATIVE-XREFS-2026-10-27.md): three `.pdata`-bounded functions reference metadata regions; **enumeration and cast implementations remain unverified** |

**Phase handoffs:** [SC0](REA-RIFT-SPELLCASTING-SC0-HANDOFF-2026-10-27.md) · [SC2](REA-RIFT-SPELLCASTING-SC2-HANDOFF-2026-10-27.md). [Task register](REA-RIFT-SPELLCASTING-TASKS-2026-10-27.json) is authoritative for the next ready task.

## Current blockers and next work

- **SC1 NOT COMPLETE:** the native RIFT spellbook/soul-tree/trainer UI and matching character level, active Role, points/rank are absent. SC-102 cannot claim "learnable at current level"; SC-103 names with multiple IDs cannot yet be mapped confidently to roles/ranks.
- **SC3 NOT COMPLETE:** shared GCD and client queue require cross-ability readiness and verified Full/Short/None queue setting. One 1.5s melee recovery or 12s ranged recovery alone is not GCD proof.
- **SC4 native REA active, no phase completion:** patched local PC binary source has confirmed RIP-relative code references to ability/castbar descriptor regions, with three bounded function SHA fingerprints. These are **not** verified native enumeration/casting handlers. Do not launch old >450s whole-PE imports.

**SC-401 next:** continue from the [source-backed instruction dossier](REA-RIFT-SPELLCASTING-SC401-NATIVE-XREFS-2026-10-27.md), not a repeated whole-image scan. New-host SHA `1935a05c9db6d468e34e0055014a4a99c1b5afceb1695884e24600f5c20a4be8`; candidate ability-descriptor function `0x9b0376–0x9b0776` references `.data` around `0x2f62d00`, plus castbar region `0x9b84f0–0x9b88cd`. Follow one source-backed call target (e.g. `0x12942a0`) or caller to determine whether this is only schema initialization or a real enumeration handler. **No callable ability implementation proven.** Preserve historical pins and do not assume current Lab-2 game equals new host build.

**Resume:** check latest RRE Git HEAD/status and the SC task register, then one bounded read-only query. Existing RR2 remains clean and unmodified by REA; two historical untracked RRE raw-probe files must be preserved. This project has no promise of background work between Chat turns.
