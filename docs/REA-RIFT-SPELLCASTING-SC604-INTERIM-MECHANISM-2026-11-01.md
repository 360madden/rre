# SC-604 — Interim RIFT spellcasting mechanism map

**Checkpoint:** November 1, 2026 (America/New_York)  
**Status:** Evidence-backed interim synthesis, **not** a recovered end-to-end native casting implementation.  
**Research owner:** REA / RRE. The immediate research target is the **physical-PC RIFT installation**, not the VMware labs. No game input, memory modification, or client restart was needed for this synthesis.

## Scope: two different executable builds

| Evidence family | SHA-256 | Provenance and limits |
| --- | --- | --- |
| Current original physical-PC `rift_x64.exe` | `1935a05c9db6d468e34e0055014a4a99c1b5afceb1695884e24600f5c20a4be8` | Original PE static code/ABI and prior read-only process observations. Its native RVAs are **not** older VM code addresses. |
| Historical RiftReader2 RIFT capture | `7c356c9dde9e12fcbff3c08d953b0630b48b1510a0ffb36e4ec164606e7b17bd` | Saved Lua API, event and clock evidence. Does **not** qualify today's local character, build, role, queue state, or server behavior. |

The companion [machine-readable evidence graph](REA-RIFT-SPELLCASTING-SC604-INTERIM-MECHANISM-2026-11-01.json) pins 14 research-source file hashes, proof levels and unresolved edges. All 14 source hashes were independently rechecked on November 1. Neither build family can be joined into one proved live call chain.

## Source-backed mechanism slices

| Mechanism | Verified finding and source | What remains unknown |
| --- | --- | --- |
| **Native command entry** (new build, original PE) | `/cast` callback RVA `0x6C7450` and `/use` callback RVA `0x6C7B90`; distinct unknown-ability/item diagnostic literals. [SC-407](REA-RIFT-SPELLCASTING-SC407-CAST-ENTRY-2026-10-27.md), [SC-409](REA-RIFT-SPELLCASTING-SC409-COMPARISON-2026-11-01.md) | Ability resolver, successful cast submission, server acceptance and actual active queue |
| **Native helper graph** (new build, original PE) | `/cast` and `/use` slices share **17 distinct direct call targets**, but have separate command-specific callees. Shared target `0x7DE6F0` is not cast-specific. [SC-409](REA-RIFT-SPELLCASTING-SC409-COMPARISON-2026-11-01.md) | Meaning of unqualified shared and unique helpers |
| **Native command context** (new build, original PE) | Cast helper `0x57CDA0` reads byte `+0x358` at RVA `0x57CDC4`; use helper `0x57DB60` reads `+0x358` at `0x57DBA3` and pointer `+0x340` at `0x57DBAC`. [SC-411](REA-RIFT-SPELLCASTING-SC411-CONTEXT-2026-11-01.md) | Runtime object identity and meaning of either field; neither is proved to encode GCD, casting, authorization or a queue |
| **Context writer search** (new build, original PE) | Two bounded probes in [SC-412](REA-RIFT-SPELLCASTING-SC412-WRITER-GAP-2026-11-01.md): 38 nearby `.pdata` regions / 8,507 source bytes show no **direct** exact-offset writers; command call sites prepare pointer arguments. | No global-absence proof. SC-412 is **parked**, not a reason for an exhaustive search |
| **Native queue configuration** (new build) | [SC-305](REA-RIFT-SPELLCASTING-SC305-QUEUE-DOSSIER-2026-10-27.md) ties `ActionBars_AbilityQueue` to a settings-object `+0xA4` 32-bit field and a prior **read-only raw value 1**. | Which of `Full`/`Short`/`None` equals 1; whether a request queued; shared GCD. [SC-306](REA-RIFT-SPELLCASTING-SC306-QUEUE-ENUM-GAP-2026-10-27.md) is blocked |
| **Historical known-ability API** (old build) | `Inspect.Ability.New.List/Detail` returned **55 distinct IDs**, **50 names**, identical ID sets across two captures; 54/55 detail objects match. [SC-101](REA-RIFT-SPELLCASTING-SC1-API-CATALOG-NOTES-2026-10-27.md), [SC-103](REA-RIFT-SPELLCASTING-SC103-RANK-ROLE-GAP-2026-11-01.md) | Actual current physical-PC spellbook, learned vs currently learnable/locked, role/rank/soul attribution |
| **Historical availability** (old build) | **10/55** records explicitly set `unusable=true`; 45 omit the field (**unknown**, not usable). [SC-104](REA-RIFT-SPELLCASTING-SC104-READINESS-2026-10-27.md) | Why each ability is unusable, server admission, and whether it will be learnable |
| **Historical cast outcomes** (old build) | Exact modern ability ID + caster + target separates Light's Decree selected-target **Dodge** from a later **402-damage** result. In the latter capture, **726** additional damage across three *other* targets must not be attributed to the selected target. One self-targeted Dodge, eight separate Auto Attack damage hits totaling 959, and one Auto Attack Miss are excluded. [SC-502](REA-RIFT-SPELLCASTING-SC502-OUTCOME-2026-11-01.md) | Current-build parity, channel/proc/interrupt/healing classes, native/server response |
| **Historical melee attribution** (old build) | Original Aggressive Block 118-damage raw event omitted `abilityNew`, so the original exact-ID comparison recorded `matchesAbility=false` / `hit=false`. A separate later normalized/replay report attributed 118 intended damage. [SC-502](REA-RIFT-SPELLCASTING-SC502-OUTCOME-2026-11-01.md) | Later attribution does not retroactively prove the raw modern-ID match or current-build behavior |
| **Historical timing** (old build) | Two saved captures sampled roughly **105–107 ms** apart; one ability's Cooldown Begin/End spans approximately **12.01 s**. [SC-304](REA-RIFT-SPELLCASTING-SC304-TIMING-2026-10-27.md) | Independent global cooldown, queue window, cast/channel duration, client-server RTT and clock conversion |
| **Failure categories** (separate sources) | Native unknown-ability text, old API-reported unusability, old RR2 out-of-range readiness, and a post-activation target Dodge are distinct types of evidence. [SC-501](REA-RIFT-SPELLCASTING-SC501-LOCAL-REJECTION-2026-10-27.md), [SC-502](REA-RIFT-SPELLCASTING-SC502-OUTCOME-2026-11-01.md) | Whether and where the server rejects a request; these observations cannot be flattened into one failure path |

**Proven slice boundaries:** The new-build native command table and helper reads are original machine-code evidence. The old-build API and combat outcomes are actual saved gameplay evidence. The transition from a present-day native `/cast` callback to a resolved ability, network request, server validation, cast state and effect **has not yet been proven**. A command receipt, a cooldown observation and a damage event are not interchangeable.

## Priority evidence needed to advance

| Priority | Next narrowly scoped evidence | Owner / method | Unlocks |
| --- | --- | --- | --- |
| **P1 — Offline now** | Compare original `/cast` unknown-ability branch predicates against `/use` unknown-item branch as a negative control; stop after two nondecisive bounded probes | REA local physical-PC PE static analysis; new SC-413 candidate | May discriminate native ability lookup/error admission without redoing SC-408/412 |
| **P2 — Current UI/API** | One same-character, same-role, time-bound local PC ability `List/Detail`, spellbook, soul/trainer and action-bar evidence set; record level, role, souls and SHA | Existing RR2/live-capture owner; separate supervised capture | SC-102/103 learned vs learnable/locked and role/rank mapping |
| **P3 — Current timing** | Two distinct abilities' same-frame readiness across one transition, selected queue mode UI, source clock and action/result IDs | Existing RR2/live-capture owner; separately authorized controlled observation | SC-301/302/306 GCD and queue-mode tests |
| **P4 — Representative exceptions** | Source-bound channel, interrupt, proc, heal and ground-target examples one family at a time | Existing live-capture owner; saved evidence to REA | SC-503 |
| **P5 — Full integration** | Connect original current-build resolver/submit path to same-build qualified state/effect evidence and export sanitized replay | REA synthesis after prerequisites | SC-601/602 final native-mechanism model |

No queue-mode enum mapping, complete learnable spellbook, universal GCD, successful server acknowledgment, or current-host cast-effect chain should be inferred before those observations exist.

## Milestone verdict and restart

- **Complete major phases:** SC0 source baseline and SC2 observed cast-lifecycle vocabulary (at their documented historical-evidence scope).
- **Open:** SC1 spellbook, SC3 timing/queue, SC4 native code, SC5 exceptional outcomes, SC6 integration. SC-603 handoff continuity is done, but SC6 is **not** complete.
- **Accepted blocked result:** SC-412 writer/constructor hypothesis parked after two independent bounded probes; do not repeat it without new discriminating evidence.
- **Next investigation:** SC-413's error-branch predecessor comparison, if a qualified bounded source lead can be captured. Otherwise seek current physical-PC UI/API evidence with the existing live-capture owner.

Resume from [canonical handoff](REA-RIFT-SPELLCASTING-HANDOFF-2026-10-27.md) and [SC task register](REA-RIFT-SPELLCASTING-TASKS-2026-10-27.json), refreshing Git HEAD and pending jobs before any new write. Preserve unrelated October raw-probe untracked files. This report is a synthesis of accepted evidence, **not** a claim that a live RIFT process was attached or that any new cast was performed.