# SC-304 — Spellcasting clock domains and measurement precision

**October 27, 2026.** **Result:** SC-304 historical timing-evidence qualification complete; **SC3 overall remains open**. REA research only. The new host RIFT executable is separately pinned in [the October 27 build checkpoint](REA-RIFT-BUILD-UPDATE-2026-10-27.md); this timing analysis exclusively applies to the **historical October 26 captures on the previous executable hash**.

## Immutable evidence

[Machine-readable bracketing and quantiles](REA-RIFT-SPELLCASTING-SC304-CLOCK-EVIDENCE-2026-10-27.json), SHA-256 `c6f6f59b71de3a12d844dbf45723c52a80d8762b9fa985777c2a1cc3e2ff5fab`.

RR2 originals and exact SHA-256:
- Ranged trial 1: `artifacts/casting-20261025-01/ranged-evidence-03/evidence.json`, SHA `1bd8694f91abb17704cd7a769b4cb63f2f334b5d00853b220f040a627c63e695`.
- Ranged trial 2: `artifacts/casting-20261025-01/ranged-evidence-04/evidence.json`, SHA `9e81dccdf53640c5ae8f874b6bad16d38f75faeee06be7999032e9695d934630`.
- Result summary: `artifacts/exports/casting-ranged-20261026-01/report.json`, SHA `bca100aeb70f9bb6f95afd927971103909c45826f68fa1223e5f57f6d888372e`.
- Host-action receipt: `artifacts/exports/casting-ranged-20261026-01/evidence/ranged-cast-02/action.json`, SHA `e4530baaa6d2dfdd9615109de5a669161c92d5037be55e364b361040ea2524d2`.

All original paths above are relative to `C:\work\riftreader2`; REA did not mutate them.

## Actual sampled time precision

| Source measure | Trial 1: Dodge | Trial 2: Hit |
| --- | ---: | ---: |
| Samples | 565 | 560 |
| Sample times strictly ascending | Yes | Yes |
| Minimum adjacent sample step | 29.297 ms | 35.156 ms |
| 5th-percentile step | 101.563 ms | 101.563 ms |
| Median step | **105.469 ms** | **107.422 ms** |
| 95th-percentile step | **113.281 ms** | **113.281 ms** |
| Maximum adjacent step | 142.578 ms | 164.063 ms |
| Gaps over 250 ms | 0 | 0 |
| Samples with active ability in `Unit.Castbar` | 0 | 0 |

These intervals are measured from **adjacent recorded values of `Inspect.Time.Frame`**, not from native scheduler timestamps. Polling at about 9–10 Hz does not resolve every subframe UI state, instant cast or server-ack event. The numerical precision of reported floating-point clock values is **not** proven clock accuracy or server timestamp granularity.

## Timeline and what its intervals mean

Each trial has three game-API events in the same RIFT frame-clock domain:

| Trial | Cooldown Begin | Result event | Cooldown End | Begin → result event | Begin → End |
| --- | ---: | ---: | ---: | ---: | ---: |
| 1 | 19204.921875 | Dodge: 19205.107421875 | 19216.931640625 | **0.185546875 s** | 12.009765625 s |
| 2 | 19790.83984375 | 402 Life damage: 19791.587890625 | 19802.845703125 | **0.748046875 s** | 12.005859375 s |

The separate event timestamps fall between recorded polling frames. For the damage trial, cooldown Begin is bracketed by samples **19790.783203125–19790.892578125**, damage by **19791.525390625–19791.638671875**, and cooldown End by **19802.79296875–19802.90234375**. This demonstrates the intervals in which a periodic poll would see a state change. It does **not** create a start-to-hit RTT measurement: the events themselves are callback/reader frame-clock observations rather than verified server timestamps.

Trial 1's smaller Begin→Dodge event interval and Trial 2's larger Begin→Damage interval do not establish that one cast was processed faster. Differences in result/ability event arrival, animation, network transport, client scheduling and combat effects remain unseparated.

## Two distinct clocks that must not be subtracted

- **RIFT frame clock:** `Inspect.Time.Frame`, used by the RR2 ability and combat/cooldown event callbacks, within the same captured game session.
- **Host Windows UTC:** the saved targeted-click receipt starts `2026-10-26T06:37:56.882443+00:00` and completes `2026-10-26T06:37:57.0838804+00:00`. It reports delivery and release succeeded but `responseVerified=false`. Host UTC is not tied to the RIFT frame clock by any measured offset and drift.

There is **no source-backed conversion** between these two clock domains, so no valid input-to-cast or network latency calculation. Neither the ~12-second effective ability cooldown nor one older ~1.5-second melee cooldown proves a separate shared GCD. Without cross-ability readiness traces, the shared-lockout hypothesis remains **unverified**.

## Required next experiments (owned by RR2's independent workflow)

For a future independently authorized safe trial, sample **at least two distinct abilities on the same frame** and bind current queue mode Full/Short/None to its own original setting image; qualify exact current guest build, player/Role, matching unit/ability IDs, and fresh clocks. Capture bounded input UTC and, only if possible, a shared guest host-to-frame time correlation receipt (with uncertainty), without relying on names or interpolating missing input events. Confirm no active castbar only if an actual cast-time ability is attempted and observation coverage is sufficient; present trials are not that experiment.

**SC-304 exit:** we have a complete, reproducible measurement-precision ledger and an explicit statement of what cannot be inferred. This is a **task checkpoint**, not SC3 phase completion. Next REA research task **SC-404** is selected native build-compatibility investigation on the October 27 host executable, without a whole-PE REA import or changes to RR2/Workbridge.
