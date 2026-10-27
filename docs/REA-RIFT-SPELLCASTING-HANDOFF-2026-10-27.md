# CURRENT HANDOFF — REA RIFT spellcasting research

**Updated:** October 27, 2026. **Next REA task:** `SC-303` — characterize saved cast-time/channel/cooldown metadata and sampling limits.  
**Scope:** REA research only; RR2/Workbridge implementation and live controls remain separately owned. All tasks through this handoff were **file-based** with no new gameplay input or REA binary import.

## Last accepted checkpoints

| Result | Local commit | What is actually established |
| --- | --- | --- |
| **SC0 PHASE COMPLETE** | `e76e6b2` | Two source-hash-verified RR2 snapshots contain identical 55 API-returned ability lookup IDs; learnability UI still unknown |
| **SC-101 COMPLETE** | `4eea4e9` | [55-row JSONL](REA-RIFT-SPELLCASTING-SC1-API-CATALOG-2026-10-27.jsonl) and [CSV](REA-RIFT-SPELLCASTING-SC1-API-CATALOG-2026-10-27.csv), unknown fields preserved |
| **SC-104 COMPLETE** | `4c29597` | 10/55 API-listed abilities have explicit `unusable=true`; listing ≠ readiness |
| **SC2 PHASE COMPLETE** | `41e7fc6` | [Observed cast lifecycle](REA-RIFT-SPELLCASTING-SC2-LIFECYCLE-2026-10-27.md): cooldown Begin → target dodge/hit → cooldown End, host input remains a separate receipt |

**Phase handoffs:** [SC0](REA-RIFT-SPELLCASTING-SC0-HANDOFF-2026-10-27.md) · [SC2](REA-RIFT-SPELLCASTING-SC2-HANDOFF-2026-10-27.md). [Task register](REA-RIFT-SPELLCASTING-TASKS-2026-10-27.json) is authoritative for the next ready task.

## Current blockers and next work

- **SC1 NOT COMPLETE:** the native RIFT spellbook/soul-tree/trainer UI and matching character level, active Role, points/rank are absent. SC-102 cannot claim "learnable at current level"; SC-103 names with multiple IDs cannot yet be mapped confidently to roles/ranks.
- **SC3 NOT COMPLETE:** shared GCD and client queue require cross-ability readiness and verified Full/Short/None queue setting. One 1.5s melee recovery or 12s ranged recovery alone is not GCD proof.
- **SC4 native REA:** deferred until a concrete source-linked hypothesis; don't launch old >450s whole PE imports.

**SC-303 immediate input:** inspect the already-exported [55-ID catalog](REA-RIFT-SPELLCASTING-SC1-API-CATALOG-2026-10-27.jsonl), original RR2 `ranged-evidence-04/evidence.json` and existing castbar/cooldown event source. Determine how many abilities have explicit cast/channel metadata, which recorded samples actually show an active castbar, and what sampling intervals permit. Write one concise source-pinned finding, focused validation, commit it; do not invent game events or change live controls.

**Resume:** check latest RRE Git HEAD/status and the SC task register, then one bounded read-only query. Existing RR2 remains clean and unmodified by REA; two historical untracked RRE raw-probe files must be preserved. This project has no promise of background work between Chat turns.
