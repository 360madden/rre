# SC0 — RIFT spellcasting research evidence baseline

**Date:** October 27, 2026  
**Owner:** REA research. RR2 is an evidence provider only. No new game action, controller access, binary import, or RR2/Workbridge source change.

## Source index (exact local SHA-256)

Paths are relative to `C:\work\riftreader2` unless noted.

| Source | SHA-256 | What is supported |
| --- | --- | --- |
| `artifacts/casting-20261025-01/ranged-evidence-03/evidence.json` | `1bd8694f91abb17704cd7a769b4cb63f2f334b5d00853b220f040a627c63e695` | Captured 55-item RIFT API ability inventory, earlier ranged attempt |
| `artifacts/casting-20261025-01/ranged-evidence-04/evidence.json` | `9e81dccdf53640c5ae8f874b6bad16d38f75faeee06be7999032e9695d934630` | Captured 55-item inventory, exact-ID later ranged outcome and player/target readings |
| `artifacts/casting-20261025-01/api-docs/api-docs.json` | `4750fee34596ee2f302183716ca3d8721cd5a22cce0fcbc3f9454227fc9f3352` | Installed RIFT API docs: `Inspect.Ability.New.List()` returns IDs of **available** abilities; batch `Inspect.Ability.New.Detail(ids)` provides details |
| `addon/RiftReader2Casting/model.lua` | `82aa8395a36fbc2c3f83ff32392dcb4bbc43aa6bd18fd39a4339ab01c264a812` | Existing RR2 implementation obtains the batched ability list, selected ability, player/target/castbar, resource and effective cooldown information |
| `docs/reference/spelldump-api-reuse.md` | `b9243cfe34a9436eca742e682d71f243506a70b253f3bcbaf2f962810feb6e7d` | Independent guest SpellDump reference uses the same batch API; its offensive categories can omit free/passive abilities |
| `docs/reference/riftmeter-api-reuse.md` | `77dacf90fe7c44f319fce2e19118f69ed57c049aabd0fd995eed7998c7b6fb99` | Existing combat addon uses exact `abilityNew`, caster/target and outcome details |
| `docs/validation/casting-ranged-2026-10-26.md` | `87336f71d597dccab933818b577d3e4455d765afff801c1c7008e709c0fc878e` | Existing independent RR2 event-based Dodge and 402 Life damage outcomes for Light's Decree |
| `artifacts/exports/casting-ranged-20261026-01/report.json` | `bca100aeb70f9bb6f95afd927971103909c45826f68fa1223e5f57f6d888372e` | Small two-trial, exact-ID result summary |
| `artifacts/casting-20261025-01/ability-list/screen/image.bmp` | `9456d8200fefc1f6c6af6140f533703e05794900a22bdea31b224f05c39d84e7` | Visually inspected October 26 **RR2 casting ability picker**, NOT the native RIFT spellbook, soul tree or trainer |

The source files above remain in RR2; **no raw 4–5 MB event capture has been duplicated into REA Git**.

## Verified sample facts

- The saved `ranged-evidence-03` and `ranged-evidence-04` snapshots each contain **55 API-returned ability records and 55 distinct lookup IDs**. The two ID sets are **identical**. Character label in the later source: `Atank`, player ID `u035400012FA2D207`; addon version `0.2.0`. This establishes one saved ability surface, not the active soul/Role allocation or all future learnable abilities.
- From the later 55 records, field **presence** counts: `passive` marked true in **7**, `castingTime` present in **9**, `channeled` present in **2**, `cooldown` present in **31**, `rangeMax` present in **27**, and `costPower` present in **33**. Absence means **unknown**, not instant, free, zero cooldown or false.
- Names are NOT primary IDs. `Building Fury` occurs under three distinct IDs; `Changing Role` appears under four distinct IDs. Never collapse or identify abilities by name alone.
- The API manual literally describes `New.List` as IDs of **"available abilities"**. Neither that wording nor the RR2 picker proves the complete set of currently learned, trainer-eligible, soul-tree-eligible or future/locked abilities at a given level.
- Historical guest executable SHA-256 reported by RR2 October 26 trial: `7c356c9dde9e12fcbff3c08d953b0630b48b1510a0ffb36e4ec164606e7b17bd`. The guest process and Role for a new study must be identified again; no cached process pointers survive restart.
- One ranged record reports `Light's Decree` modern ID `A6B8B16CD6F8B3DB9`, base cooldown about 12 seconds and Power expenditure of 20. The controlled second trial hit the exact dummy for 402 Life damage; the first exact-target event was a dodge. These results do NOT independently prove GCD, hitbox distance, facing, LOS or cast/channel duration.

## SC0 completed vs unknown

**SC0 evidence baseline is complete**: source inventory, source SHA checks, repeatable 55-ID set, current ability metadata coverage, and evidence limits are recorded. These are **existing RR2 observations interpreted for REA**, not a newly completed native client reverse engineering.

**Next SC-101:** preserve the actual 55-ID API-returned catalog as a source-pinned research table with missing values represented as unknown and ability identity by ID, NOT name. Historical level-45 Warrior context may be noted as separate RR2 handoff information, not a proven same-time Role/soul configuration.

**Blocked SC-102:** no source-verified native RIFT spellbook/soul-tree/trainer screenshot for the **same character, role and time** was located in the scoped reference review. The saved `ability-list/screen` is the RR2 picker. A later RR2-owned evidence handoff needs the actual level, calling, role, soul allocation and spellbook/eligibility UI. Don't infer `learnable-now` from `List()` or the level alone.

**SC2/SC3 timing caution:** existing single-ability effective cooldown values cannot isolate a global cooldown. The next independent shared-GCD question needs cross-ability readiness observations.

**Tool policy:** REA 6.5.0/Ghidra 12.1.2 should not run whole-PE import without a specific source-backed question. No new source code, installation, game input or native analysis was performed in SC0.

## Validation and handoff

Evidence checks: two source file hashes, ID-set equality, field presence counting and native-UI image classification; source provider still owns unchanged RR2 files. A documentation-only task needs SHA/JSON/link/Git diff validation, not the 530-test historic navigation suite.

**SC0 phase handoff:** see `REA-RIFT-SPELLCASTING-SC0-HANDOFF-2026-10-27.md`. The canonical short handoff moves to SC-101. Do not repeat the source discovery.
