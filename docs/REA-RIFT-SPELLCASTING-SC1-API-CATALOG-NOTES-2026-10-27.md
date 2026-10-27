# SC-101 — Source-pinned 55-ability RIFT API catalog

**Date:** October 27, 2026  
**Result:** Completed **API-returned ability catalog export**; this is **not** the full native spellbook, complete learnability at level, or a fresh live snapshot. REA-only file-based extraction of saved RR2 evidence.

## Export and provenance

- [Full machine catalog](REA-RIFT-SPELLCASTING-SC1-API-CATALOG-2026-10-27.jsonl): **55 JSONL records**, UTF-8, SHA-256 `ee8fd5ac7576fe0f1adf0611db7086328289f6f8a21acca12f31afc4c3eeceb6`.
- [Readable CSV](REA-RIFT-SPELLCASTING-SC1-API-CATALOG-2026-10-27.csv): **55 data rows**, SHA-256 `231ec91a2d092ab6588af157c6789aa125500dc7578511c71f0a9bce8cd4fd01`.
- Source (read-only): `C:\work\riftreader2\artifacts\casting-20261025-01\ranged-evidence-04\evidence.json`, SHA-256 `9e81dccdf53640c5ae8f874b6bad16d38f75faeee06be7999032e9695d934630`; peer trial 03 SHA `1bd8694f91abb17704cd7a769b4cb63f2f334b5d00853b220f040a627c63e695` has the identical set of lookup IDs.
- Source addon version `0.2.0`, historical player label `Atank` and ID `u035400012FA2D207`, 2026-10-26 RIFT build SHA `7c356c9dde9e12fcbff3c08d953b0630b48b1510a0ffb36e4ec164606e7b17bd`. Current level/active soul allocation/role **not verified by this exported snapshot**.
- `sourceKind=RIFT-API-AVAILABLE-ABILITY` means **returned by `Inspect.Ability.New.List`** at the source snapshot, not "learned from trainer", "eligible at current level", "usable immediately" or "known to all roles".
- JSONL `metadata` explicitly uses `null` when an original static field was not returned. `reportedKeys` preserves original source-field presence, so a missing `false` cannot be invented. CSV blanks are unknown; use JSONL for boolean/source precision.
- Volatile `target`, `unusable` and `currentCooldown*` from the historical capture are *not* exported as timeless spell properties; the original source retains them for separately time-bound readiness research.

## Findings useful for actual spellcasting research

| API returned example | Exact lookup ID | Cast metadata | Research interpretation |
| --- | --- | --- | --- |
| Aggressive Block | `A6663BAE96C8E85E6` | No cast-time field; `rangeMax=3` | Do not infer instant from missing field |
| Light's Decree | `A6B8B16CD6F8B3DB9` | `cooldown≈12s`; `rangeMax=20` | Observed actual hit/dodge in prior RR2 tests; not independent GCD |
| Ascended Resurrection | `A38DFCB8220EE4A2D` | `castingTime=8s` | Potential nonzero cast-time research anchor, subject to actual usability/target permissions |
| Nexus Infusion | `A251F2E341BED68A3` | `castingTime≈6s`; `channeled=true` | Potential channel timing anchor; effect/ticks not yet qualified |
| Planar Lure | `A2F23B7DA3B6FE174` | `castingTime=2s`; `cooldown=5s` | Historical `unusable=true` in separate readiness snapshot; source alone does not say why |
| Soul Recall | `A3C5AEC64D3793518` | `castingTime=8s`; `cooldown≈3600s` | Do not use for repeated timing tests |
| Wall of Light | `A2CD5149A46EE1393` | `castingTime=4s`; `channeled=true`; `cooldown=75s` | Potential channel test, blocked on separate RR2 authorization |

**No name-based merge:** 55 unique ability lookup IDs represent 50 distinct displayed names. `Building Fury` has three IDs (all present with passive true), and `Changing Role` has four IDs (2s cast time each). These might indicate distinct ranks/roles/variants but **the names and count do not prove which**. SC-103 remains an independent identity/role/rank qualification.

**Completeness limits:** the API list can include passives, contextual abilities, role switches and utilities. It cannot by itself establish all unlearned soul-tree/trainer/mastery spells at a given level. This is why **SC-102/SC1 phase completion remains blocked** on a source-verified native RIFT spellbook/soul/trainer UI with same character, exact current level and role.

**Next REA task:** SC-104, inspect the existing fresh-readiness code and historical source samples to differentiate "API listed" from current ability usability; SC-201 request/outcome analysis can proceed independently. Do not modify RR2 or issue any gameplay input under this task.

## Acceptance

The conversion was single-pass, source-SHA-guarded, and performed without changes to RR2. The accompanying validation must confirm 55 rows/IDs, equality to both captured inventories, duplicate-name preservation, missing-value semantics, exact output SHA and no unexpected user data. One source-backed commit is the completion marker for SC-101.
