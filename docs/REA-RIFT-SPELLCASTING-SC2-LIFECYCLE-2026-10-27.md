# SC2 — Observed RIFT ability-use lifecycle (REA research)

**Date:** October 27, 2026. **Phase result:** **complete at the game-API/evidence layer**, NOT a reverse-engineered native or server-side request path.  
**Owner:** REA. Existing live trials were performed and retained by RiftReader2; **REA sent no game inputs**.

## Source-bound inputs

- [Extracted ordered event timeline](REA-RIFT-SPELLCASTING-SC2-TIMELINE-2026-10-27.json), SHA-256 `1236f5eb182b38df50daa1f237070ea21ea9cfc94ac490908ace1b53a5f5e728`.
- RR2 `artifacts/exports/casting-ranged-20261026-01/report.json` — SHA `bca100aeb70f9bb6f95afd927971103909c45826f68fa1223e5f57f6d888372e`.
- RR2 `artifacts/exports/casting-ranged-20261026-01/evidence/ranged-cast-02/action.json` — SHA `e4530baaa6d2dfdd9615109de5a669161c92d5037be55e364b361040ea2524d2`.
- RR2 `artifacts/exports/casting-dummy-20261026-01/summary.json` — SHA `09919b58e93d5615a04161cba419a1de3674b853c1eeefd65f8a5e64a1e2d15d`.
- RR2 `docs/workflows/casting-handoff-2026-10-26.md` — SHA `b1f7125715cc29584c43d99321b900ff6365fbbd2d5c3da66468a3725c9340b5`.
- For real API semantics, the current RR2 `RiftReader2Casting/model.lua` source SHA is `82aa8395a36fbc2c3f83ff32392dcb4bbc43aa6bd18fd39a4339ab01c264a812`.

These are **historical game observations** tied to the guest file SHA `7c356c9dde9e12fcbff3c08d953b0630b48b1510a0ffb36e4ec164606e7b17bd`, selected dummy ID `u80000001EB003765` and player ID `u035400012FA2D207`. A fresh new session needs fresh process/source identity.

## Observed request-to-outcome stages

| Stage | Evidence | Confidence/limit |
| --- | --- | --- |
| Diagnostic target/ability selection | RR2 selected modern ID and target; pre-readiness could be blocked by target, cost or range | **RR2 application check**, not necessarily all native restrictions |
| Physically controlled command | Sanitized second-ranged trial receipt records an exact reviewed client-point left click, down/up inserted and released | **Host input delivered**; `responseVerified=false` explicitly forbids treating it as game consumption/acknowledgment |
| RIFT's own apparent cooldown transition | API `Event.Ability.New.Cooldown.Begin` for the selected modern ID | Game API cooldown observation, not separately proven GCD or server request acceptance |
| Effect/avoidance | Exact-ID combat events: dodge or damage with modern `abilityNew` and matching caster+target | Game observed intended-target result; a dodge is **not** "cast input failed" |
| Recovery | `Event.Ability.New.Cooldown.End` and later observed-ready | Ability-readiness observation; not independent shared global cooldown |

**Important nonobservations:** No authoritative client native spell dispatch function, spell packet, server acknowledgement, queue object, cast start timestamp, native cooldown clock or exact projectile travel-time mechanism has yet been recovered by REA. Empty `Unit.Castbar` metadata for a saved selected ability does not prove all spells are instant.

### Source-timed Light's Decree outcomes

| Trial | RIFT frame-clock Begin | Outcome event | Frame-clock End | Effective cooldown | Interpretation |
| --- | ---: | --- | ---: | ---: | --- |
| 1 | 19204.921875 | **Dodge** at 19205.107421875; same selected target and modern ID, zero damage | 19216.931640625 | 12.009765625 s | Ability produced a target avoidance event; not a missing cast |
| 2 | 19790.83984375 | **402 Life damage** at 19791.587890625; same selected target and modern ID | 19802.845703125 | 12.005859375 s | Intended target was damaged; other-target AOE damage 726 excluded |

Both trials began with Power 100, dipped to 80 and later returned to 100. Trial 1 had 9 separate autoattack events; Trial 2 had none. The selected ability ID is `A6B8B16CD6F8B3DB9`. These observations do **not** independently prove cooldown sharing, GCD duration, castbar onset or action-to-effect latency.

**Clock guard:** The RIFT frame-clock values within a trial can be ordered, but the host action receipt's UTC timestamps cannot be subtracted from `Inspect.Time.Frame` without a verified clock mapping. The 0.1855s and 0.7480s intervals from cooldown Begin to observed outcome are **event separations**, not server RTT or confirmed projectile travel times.

### Separate melee acceptance

Prior Aggressive Block (`A6663BAE96C8E85E6`) was initially **out of range** according to RR2 readiness, then a separate supervised attempt yielded 118 damage to the exact selected dummy. Effective cooldown recovery measured 1.513671875 s and Power 100 → 80 → 100. The RR2 source calls this an **effective ability/GCD** cooldown—not a separately qualified global cooldown. The saved source includes 6 distinct autoattack events, which do not count as the ability hit.

### Failure and outcome classification for SC-202

| Observed case | Proper classification | What cannot be concluded |
| --- | --- | --- |
| Aggressive Block reported out of range before an attempt | **Pre-activation RR2 readiness restriction**, per its documented API readout | Not a proven native cast packet rejection |
| Discharge listed with `unusable=true` in saved ability catalog | **Contextual API-reported unusability**, not unlearned | Specific missing proc/requirement still unknown |
| Light's Decree exact-target `Dodge` | **Target avoidance after ability activity**, not positive damage | Not a failure to deliver input; not a claim of damage |
| Light's Decree exact-target 402 damage | **Positive exact-ID effect**, distinct from extra area hits | Not proof of precise LOS, hitbox range or shared GCD |
| Melee 118 damage with separate autoattack | **Positive ability outcome**, autoattacks separated | No universal timing or server GCD inference |
| No matched event in incomplete capture | **Inconclusive**, not categorical failure | Need proven coverage and exact IDs |

**Generalized observed state vocabulary:** `catalog-listed` / `diagnostic-blocked` / `diagnostic-waiting` / `diagnostic-ready` / `physical-input-delivered` / `cooldown-begin-observed` / `target-dodge/miss/resist/immune` / `target-hit/heal` / `cooldown-end-observed` / `inconclusive`. This is an **observational model**; it is not a claim that native code has identical states.

## SC2 exit decision and handoff

SC-201 and SC-202 complete the **observable request/cooldown/effect and refusal-vs-avoidance taxonomy**, with exact saved player, target and ability IDs. **SC2 phase exit is met at G1/G2 evidence scope**: one or more positively observed outcomes and distinct blocked/avoided outcomes with source-specific caveats. Internal client-side request/queue lifecycle and server authority remain SC4 research hypotheses.

**Next active research:** SC-301 cross-ability shared GCD and SC-302 queue-policy contrast require **new RR2-owned correlated observations**. SC-303 catalog cast/channel metadata may proceed offline. Native RIFT assembly is a later selective investigation only after a source-linked, answerable question; do not start a full import now.

**Phase handoff:** [SC2 handoff](REA-RIFT-SPELLCASTING-SC2-HANDOFF-2026-10-27.md) is the durable completion receipt. Update the independent task board and canonical handoff after committing this document. No REA game control, guest modification, credential use or remote Git push was performed.
