# REA RIFT spellcasting — current Chat-mode handoff

**Updated October 27, 2026. Target: LOCAL physical-PC RIFT, NOT VMware.** This handoff supersedes previous SC-401/SC-402 schema searches.

**Current task: SC-502 (READY).** [SC-501 offline source-backed failure taxonomy](REA-RIFT-SPELLCASTING-SC501-LOCAL-REJECTION-2026-10-27.md) is completed; the apparent ASCII `A` was actually UTF-16LE `ABILITY` used near an error template. Next analyze modern caster/ability/target IDs across saved hit, dodge and area events; retain missing heal/overheal evidence as unknown. No live RIFT input.

## Build, target and ownership

- RIFT local install `C:\Program Files (x86)\Glyph\Games\RIFT\Live\rift_x64.exe`, SHA `1935a05c9db6d468e34e0055014a4a99c1b5afceb1695884e24600f5c20a4be8`, 60,493,640 bytes.
- One local process was observed at PID **66436**, moduleBase **`0x7FF720420000`**, **volatile**, the game was background at last UI inspection. Nine bounded standard read-only process reads verified native rebased command table/code. No focus change, game input, memory write or injection.
- REA owns native research, `C:\work\rre` main. RiftReader2 and Workbridge are **independent projects and must not be edited**. Historical RR2 casts and old-build API record do not validate new RIFT cast effects or GCD.
- Reference [physical-PC target policy](REA-RIFT-LOCAL-PC-TARGET-2026-10-27.md), [tasks](REA-RIFT-SPELLCASTING-TASKS-2026-10-27.json), and old-build [SC0](REA-RIFT-SPELLCASTING-SC0-HANDOFF-2026-10-27.md) / [SC2](REA-RIFT-SPELLCASTING-SC2-HANDOFF-2026-10-27.md) completed phase handoffs.

## Latest source-backed native finding — SC-407

**Correct command mapping** based on original command name following its function-pointer block, verified by typed error text references:

| Command | Command literal RVA | Specialized native callback RVA |
| --- | --- | --- |
| `stopattack` | `0x26B6550` | `0x6C73F0` |
| **`cast`** | **`0x26B6598`** | **`0x6C7450`** |
| `use` | `0x26B65D8` | `0x6C7B90` |

Original selected `cast` native body `0x6C7450–0x6C7B71`, SHA `31c02f4e68ac0c8157ad4e8fd1f813fe724b02f607d9c67649bcd777d0890d85`. It contains exact references to text `Could not cast unknown ability: [%ABILITY]` at `0x6C78B2/0x6C78DD/0x6C7922`. Adjacent `use` code references `Could not use unknown item: [%ITEM]`. Runtime source pointer/byte comparisons passed **9/9**. This proves an entry and error branch, **NOT** game/server acceptance, a native learned-spellbook enumerator, shared GCD or queue mechanism.

- [SC-407 source dossier](REA-RIFT-SPELLCASTING-SC407-CAST-ENTRY-2026-10-27.md)
- [SC-407 machine data](REA-RIFT-SPELLCASTING-SC407-CAST-ENTRY-2026-10-27.json)
- Recent Workbridge jobs (passed): `rea-localpc-cast-handler-trace-20261027-01` and `rea-localpc-cast-command-runtime-code-20261027-01`. The earlier `rea-localpc-cast-dispatch-pointers-20261027-01` contains **wrong provisional labels**, corrected in SC-407; never reuse those labels.

**SC-408 remains parked. SC-501 completed at bounded evidence scope:** native error text `Could not cast unknown ability: [%ABILITY]` is linked to a **UTF-16LE `ABILITY` formatting key** at RVA `0x26b6030`, disproving the provisional `A`-prefix inference. Historical RR2 `unusable=true` and out-of-range diagnostics are distinct from a real target Dodge. Full native/server rejection mechanics remain unverified. Source QA 16/16; see [SC-501 record](REA-RIFT-SPELLCASTING-SC501-OFFLINE-2026-10-27.json).

## What remains open

- **SC1** native full spellbook/learnable-at-level/role and souls: no current local on-screen UI or role-scoped API baseline.
- **SC3** independent shared GCD, actual ability queue Full/Short/None mapping (raw setting `+0xA4` was `1` only), cast delay and server clock: unresolved. [SC-305](REA-RIFT-SPELLCASTING-SC305-QUEUE-DOSSIER-2026-10-27.md) is completed, [SC-306](REA-RIFT-SPELLCASTING-SC306-QUEUE-ENUM-GAP-2026-10-27.md) blocked until matching UI evidence.
- **SC4** active, not complete: SC-407 native `/cast` command entry verified; SC-408 generic callees parked. SC-501 corrected error-format evidence does not yet identify the native ability resolver or server acknowledgement.
- **SC5** active, not complete: SC-501 rejection taxonomy accepted; SC-502 outcome attribution is next; SC-503 proc/channel/interrupt research still needs qualifying source observations.
- No background work assumed: checkpoint each bounded finding and commit.

## Resume in next Chat mode

1. Read RRE Git HEAD/status, this one-page handoff and current task register; do not repeat broad searches or touch preserved unrelated untracked files.
2. Verify original local SHA before analyzing new source. Inspect one downstream call at a time, classify supported/rejected/unresolved.
3. Save original source bytes, build SHA, exact instruction RVA and result, tests, commit after one useful submilestone.
4. **Big colored completion header only when a complete major phase's exit criteria pass.** SC4 is not there yet.
