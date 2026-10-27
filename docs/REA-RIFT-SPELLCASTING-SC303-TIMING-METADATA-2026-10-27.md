# SC-303 — Casting time, channel and sample-cadence research

**Date:** October 27, 2026. **Status:** bounded offline source analysis COMPLETE; **SC3 phase NOT complete** (GCD and ability queue still unverified).  
**Owner:** REA, reading saved RR2 data only. No in-game casting, native import or external project edits.

## Candidate abilities already visible in the 55-ID API catalog

Of the 55 historical API-returned records, **9 have explicit nonmissing `castingTime` metadata**, and **2 explicitly report `channeled=true`**. Selected examples:

| Exact modern ability ID | Name | Reported cast time | Channel flag | Other relevant evidence |
| --- | --- | ---: | --- | --- |
| `A38DFCB8220EE4A2D` | Ascended Resurrection | 8s | Missing | 35 reported max range; valid target/conditions unknown |
| `A251F2E341BED68A3` | Nexus Infusion | ~6s | **true** | Reported rangeMax 25; target and readiness still need qualification |
| `A2CD5149A46EE1393` | Wall of Light | 4s | **true** | Base cooldown 75s; `unusable=true` in saved ability detail, so not a ready test candidate |
| `A2F23B7DA3B6FE174` | Planar Lure | 2s | Missing | 5s cooldown; historically `unusable=true`, not ready without finding why |
| `A3C5AEC64D3793518` | Soul Recall | 8s | Missing | ~3600s base cooldown; **poor choice** for repeat testing |
| Four distinct IDs | Changing Role | 2s each | Missing | Role selection control, **not** evidence of damage-dealing cast mechanics |

These values are API metadata—not observed castbar spans. Missing cast-time/channel metadata is **unknown**, not zero or nonchanneled. Ability names and classes can be misleading; exact IDs remain primary.

## Direct timing sample audit

Sources (unchanged original files, paths under `C:\work\riftreader2\artifacts\casting-20261025-01\`):

- `ranged-evidence-03/evidence.json`, SHA-256 `1bd8694f91abb17704cd7a769b4cb63f2f334b5d00853b220f040a627c63e695`;
- `ranged-evidence-04/evidence.json`, SHA-256 `9e81dccdf53640c5ae8f874b6bad16d38f75faeee06be7999032e9695d934630`.

| Historical trial | Valid timed samples | Minimum step | Median step | Maximum step | Castbar ability seen in sampled `cast` |
| --- | ---: | ---: | ---: | ---: | --- |
| Light's Decree: dodge | 565 / 565 | 29.297 ms | **105.469 ms** | 142.578 ms | **0 samples** |
| Light's Decree: hit | 560 / 560 | 35.156 ms | **107.422 ms** | 164.063 ms | **0 samples** |

There were **no inter-sample gaps above 250ms** in these retained traces. The first had 113 samples labelled `cooldown-ability-or-gcd` and 452 labelled `observed-ready`; the second had 111 and 449 respectively. The recorder successfully observed effective cooldown waiting, **not a castbar windup/channel** in these two attempts.

**Implication:** an event may occur between 100ms-ish samples; this is not a 1ms source, and the absence of a sampled castbar does not prove Light's Decree is intrinsically instant. Neither cooldown-waiting classification can independently identify a shared GCD; no cross-ability readiness stream was captured.

## Falsifiable next-timing experiment, owned by RR2 only when separately authorized

To qualify a **cast-time ability**: select a specific known nonzero-`castingTime` ability with a **valid/safe target and confirmed current usability**, record consecutive `Unit.Castbar` start/begin/duration/remaining/end values, exactly one bounded cast attempt and typed outcome/cancellation, and compare against original API metadata in the **same RIFT frame clock**. If no usable cast-time candidate exists, record that explicit blocker; do not cast an unusable/resurrection/teleport/role-change ability just to produce data.

To qualify a **channel**: likewise capture full channel start, individual ticks/effects and interruption/end semantics. A 4-second metadata field is not by itself 4 seconds of confirmed ticks. An effect after a channel may have a separate travel/animation delay.

To qualify **GCD**: collect readiness simultaneously for at least two other independent abilities at each frame; previously recorded Light's Decree-only and Aggressive Block-only samples cannot do it. To study queue-mode delays, bind each trial to the actual Full/Short/None UI configuration. Host UTC action times cannot be subtracted directly from RIFT frame timestamps.

SC-303's question is now answered from saved evidence: **there are concrete metadata-bearing cast/channel candidates, but the existing real dummy traces contain no active castbar evidence and are too sparse to resolve subframe latency.** Keep SC3 **active, not complete** until its shared GCD/queue exit criteria are satisfied.

## Source and status handoff

One bounded read-only parser: Workbridge job `rea-sc303-sampling-source-audit-20261027-01`, exit 0. Original full source hashes remain preserved. Next SC-304 can formalize clock-domain and precision bounds (offline), while SC-301 and SC-302 remain blocked on independent RR2-operated cross-ability and queue-mode observations. No REA game control or server/client-native mechanism was asserted.
