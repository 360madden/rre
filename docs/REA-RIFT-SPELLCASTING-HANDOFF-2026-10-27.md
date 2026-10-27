# CURRENT HANDOFF — REA RIFT spellcasting research

**Updated:** October 27, 2026. **Next REA task:** `SC-404` — narrow, build-pinned native compatibility inventory for the newly patched physical-host RIFT executable; do not import the entire PE.  
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
| **SC-304 COMPLETE** | See latest Git history | [Clock-domain precision audit](REA-RIFT-SPELLCASTING-SC304-TIMING-2026-10-27.md): 565/560 samples, same-clock event order and source bracketing, but **no RTT or independently proven GCD** |

**Phase handoffs:** [SC0](REA-RIFT-SPELLCASTING-SC0-HANDOFF-2026-10-27.md) · [SC2](REA-RIFT-SPELLCASTING-SC2-HANDOFF-2026-10-27.md). [Task register](REA-RIFT-SPELLCASTING-TASKS-2026-10-27.json) is authoritative for the next ready task.

## Current blockers and next work

- **SC1 NOT COMPLETE:** the native RIFT spellbook/soul-tree/trainer UI and matching character level, active Role, points/rank are absent. SC-102 cannot claim "learnable at current level"; SC-103 names with multiple IDs cannot yet be mapped confidently to roles/ranks.
- **SC3 NOT COMPLETE:** shared GCD and client queue require cross-ability readiness and verified Full/Short/None queue setting. One 1.5s melee recovery or 12s ranged recovery alone is not GCD proof.
- **SC4 native REA:** deferred until a concrete source-linked hypothesis; don't launch old >450s whole PE imports.

**SC-404 next:** use the new [build inventory](REA-RIFT-BUILD-INVENTORY-2026-10-27.json), SHA `1935a05c9db6d468e34e0055014a4a99c1b5afceb1695884e24600f5c20a4be8`, as a *new separate* REA PE target. Preserve the old SHA and historical 55-ID/casting evidence. Find one specific client-native spell/ability/cooldown anchor or qualify a targeted blocker; do **not** run a whole-PE Ghidra import, transplant old RVAs, or assume current Lab-2 guest matches host. New current-session API/role/queue data are RR2-owned; do not change RR2. SC1 and SC3 remain incomplete pending source evidence.

**Resume:** check latest RRE Git HEAD/status and the SC task register, then one bounded read-only query. Existing RR2 remains clean and unmodified by REA; two historical untracked RRE raw-probe files must be preserved. This project has no promise of background work between Chat turns.
