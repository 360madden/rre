# SC-502 — Exact ability, caster and target combat-event attribution

**Date:** November 1, 2026. **Result:** completed at **historical source-data attribution** level. **SC5 phase not yet complete.** REA-only offline analysis; local Windows physical-PC RIFT remains the chosen native target, while these specific prior combat observations were recorded on a **different, older RIFT executable**. No gameplay input, process attach, memory modification, or changes in RiftReader2/Workbridge.

## Evidence sources and cross-build boundary

[Machine-readable original-event reconciliation](REA-RIFT-SPELLCASTING-SC502-EVENT-ATTRIBUTION-2026-11-01.json), SHA-256 `73bfe67b4a79f3c6c983113d439ef503ba622235f362a2cb16e39e803714ea16`.

Original RR2 source files (read-only, paths relative to `C:\work\riftreader2`):

| Source | SHA-256 |
| --- | --- |
| `artifacts/casting-20261025-01/ranged-evidence-03/evidence.json` | `1bd8694f91abb17704cd7a769b4cb63f2f334b5d00853b220f040a627c63e695` |
| `artifacts/casting-20261025-01/ranged-evidence-04/evidence.json` | `9e81dccdf53640c5ae8f874b6bad16d38f75faeee06be7999032e9695d934630` |
| `artifacts/exports/casting-ranged-20261026-01/report.json` | `bca100aeb70f9bb6f95afd927971103909c45826f68fa1223e5f57f6d888372e` |
| `artifacts/casting-20261025-01/trial-evidence-01/evidence.json` | `0cec9b6ac40d229510033a9acd9a355a0b043174a7fa87763aea71afa77125db` |
| `artifacts/exports/casting-dummy-20261026-01/summary.json` | `09919b58e93d5615a04161cba419a1de3674b853c1eeefd65f8a5e64a1e2d15d` |
| `artifacts/casting-20261025-01/reuse-replay-result.json` | `6970b905904dd66757c08d20ae79e180909501dbd6053ea63f047812fcf1e6de` |

These events come from the previously recorded game build `7c356c9dde9e12fcbff3c08d953b0630b48b1510a0ffb36e4ec164606e7b17bd`. The **physical PC's original executable was separately rehashed November 1** and still matches `1935a05c9db6d468e34e0055014a4a99c1b5afceb1695884e24600f5c20a4be8`. No new live cast outcome has been collected from the latter build in this REA pass.

## The attribution rule

A modern ability event qualifies as the **selected ability on selected target** only when all three match the trial record:

1. `event.caster === trial.playerId`;
2. `event.abilityNew === trial.abilityId` (modern ability ID, not legacy `ability` or spell name);
3. `event.target === trial.targetId`.

Classify events sharing the ability ID but aimed at other targets separately as **same-ability area effects**. Classify another ability's events on the selected target separately as **autoattacks or unrelated abilities**. Self-targeted outcomes must not be counted as enemy-target results. A missing modern ID remains **unqualified** until a separately sourced mapping is validated; never silently fall back to matching ability names. The raw event records and derived verdicts are preserved independently.

## The actual combat-event ledger

| Historical scenario | Raw retained combat events | Selected-target Light's Decree | Other ability / other targets |
| --- | ---: | --- | --- |
| **Trial 1: selected target dodged** | **11** | One exact-ID **Dodge**, **zero** Light's Decree damage to selected dummy | One separate **self-targeted Dodge** record with the same ability; **nine Auto Attack events** against selected dummy: **eight damage hits totaling 959** and **one Miss** |
| **Trial 2: selected target hit** | **4** | One exact-ID **402 Life damage** to selected dummy | Same Light's Decree ability damaged three **other** dummy IDs for **243 + 243 + 240 = 726** additional damage, distinct from selected target |
| **Trial 2: all targets combined** | Four damage events | 402 | 726; **total = 1,128**, which must *not* be reported as selected-target damage |

**Concrete discovery:** the selected-target first trial's original record actually starts with a self-targeted Dodge at frame clock `19204.974609375`; the selected dummy's Dodge follows at `19205.107421875`. Both share the modern Light's Decree ability ID, but their target IDs differ. Filtering solely on caster+ability or solely on name would conflate them. The nine later Auto Attack events carry a **different modern ability ID** `A4FDE7DEC3FDF0909`. They are not Light's Decree damage despite affecting the same selected dummy and occurring during the same recording.

The successful second trial's selected dummy ID `u80000001EB003765` received 402. Three other dummy IDs (`u80000001EB00377C`, `u80000001EB003768` and `u80000001EB003767`) each received a separately attributable area hit from the **same modern ability ID**. This is strong source-backed evidence for multi-target event routing, not proof of exact geometric hitbox distance or server mechanics.

### Melee provenance: original raw record versus later accepted normalization

The initial Aggressive Block source contains three combat events: an **118-damage** event named Aggressive Block with legacy ID `a000000006663BAE9`, and two separate Auto Attack damages of **149** and **153**. Importantly, this *original* event recorded `matchesAbility=false` and the original trial `hit=false` because `abilityNew` was not present/matched in that source format. Do **not** rewrite the original capture's verdict.

A later independent RR2 summary reports the same selected modern ability `A6663BAE96C8E85E6`, selected dummy and **118 intended damage**, while the later saved offline replay reports `intended-hit-confirmed`, 118 damage and seven events. Those receipts support a later **corrected normalization path**, but the replay record contains its *own* `sourceSha256` and is not proof that the first historical raw file was a modern-ID match as originally captured. Likewise, the later summary's six autoattack events need not equal the initial three-event source. Preserve the distinction between snapshots/windows.

## Coverage limits: healing, overhealing, interrupts and damage types

The two ranged `trial.events` arrays contain **no heal or overheal result events**, and their `healingConfirmed` / `overhealObserved` flags are false. This is a bounded statement about those retained trial recordings, **not** proof that RIFT has no healing mechanics or that the existing RR2 recorder cannot capture healing. Reference addon evidence (`docs/reference/riftmeter-api-reuse.md`) describes combat Heal/Miss/Immune/Resist/Parry subscriptions and overhealing fields; that implementation evidence is distinct from an actual observed healing event.

Similarly, a Dodge is an **observed target outcome**, not native `/cast` request rejection. A missed Auto Attack is not a miss by the selected Light's Decree ability. A positive target damage event is not evidence of GCD or queue duration. Future experiments should preserve event kind, exact modern ability ID, caster, target, timestamp/source domain, actual amount, and optional healing/absorbed/overkill fields rather than reducing combat to one damage counter.

## SC-502 exit and next offline work

**SC-502's narrow acceptance criteria are met:** actual historical raw events distinguish selected-target hit/dodge from self-target and extra-area effects, modern vs legacy ability namespaces remain separate, initial failed modern matching is not concealed, and healing/overheal/conditional cases remain explicitly unknown. No target/game input was performed.

**SC5 major phase remains ACTIVE, not complete.** SC-503 conditional, channel and interruption cases remain blocked on appropriate source observations. Further REA native or live research must use the local PC source build with fresh identity and should not infer cross-build runtime equivalence. The next *independent offline research question* should be chosen from remaining ready SC tasks (e.g. SC-103 role/rank identity constraints), not repeated string scans.

**Parallel execution receipts:** seven initial independent read-only jobs, four targeted second-pass jobs and subsequent source follow-ups. One melee job failed because a different saved source encoded `events` as an object rather than an array; the original failure was preserved and a narrower shape-aware inspection passed. Every result was coordinated by one integration owner; Workbridge's 36 coordination slots do not themselves create 36 AI agents.
