# SC-104 — API listing vs momentary usability in RIFT

**Date:** October 27, 2026. **Status:** source-backed offline readiness classification completed.  
**Owner:** REA research only; RR2 source and game state were **read-only**. Native client implementation of these checks remains unverified.

## Direct falsifier of a misleading interpretation

The October 26 `ranged-evidence-04/evidence.json` contains **55** ability records returned by RR2's `Inspect.Ability.New.List()` → batch `Detail()` routine. **10/55** explicitly report `unusable=true`, even though they appear in the list. Therefore:

> **API-listed/available ≠ presently usable.**

The other 45 records have no `unusable` field in that collected catalog. Their omission is **unknown**, not proof of `unusable=false` or readiness. It is also not evidence of trainer eligibility, rank or current soul allocation.

Source exact SHA: `9e81dccdf53640c5ae8f874b6bad16d38f75faeee06be7999032e9695d934630`; RR2 casting model: `82aa8395a36fbc2c3f83ff32392dcb4bbc43aa6bd18fd39a4339ab01c264a812`.

## Tri-state classification

| Dimension | Meaning | Valid observation | Default for unqualified data |
| --- | --- | --- | --- |
| `apiListed` | An ability lookup ID was returned in `New.List()` | In the 55-ID source: true for those 55 | **Unknown** for IDs not in the source (absence cannot prove unlearned) |
| `currentlyKnown` | The current character/Role has actually learned/owns the ability | RIFT spellbook/role or explicit trained/learned evidence | **Unknown** from the API list alone |
| `learnableNow` | Currently eligible to learn it despite possibly not knowing it | Same-role soul/trainer/mastery/quest UI and prerequisites | **Unknown** from this source |
| `usableAtTime` | May execute against the current target in the current game context | Fresh exact-ID ability detail, player/target, resources, cooldown, castbar and actual response | **Unknown** from a static inventory or missing `unusable` |
| `boundToBar` | Bound to action bar or macro | Same-time UI/bindings | **Unknown** for all entries without direct bar evidence |

**Examples from one historical evidence bundle:**

- `Discharge` (`A23A6E91642EDEA34`): returned by the API and explicitly `unusable=true` in the catalog. This does **not** prove whether its missing prerequisite is proc, combo, target, stance or another condition.
- `Retaliation` (`A338ECD701DCD52C0`) and `Wall of Light` (`A2CD5149A46EE1393`): also API-listed with `unusable=true`. Wall of Light has `castingTime=4`, `channeled=true` and `cooldown=75`; it should **not** be assumed ready for channel experiments.
- `Light's Decree` (`A6B8B16CD6F8B3DB9`): the saved `last` selected-ability reading has `status=ready` and `reason=observed-ready` at **frame-clock 19870.970703125**, exact player/target IDs and costPower20. This is a **RR2 diagnostic readiness verdict at that frame**, not a guaranteed server acceptance. Earlier recorded same-ability trials separately observed both a Dodge and exact-target 402-damage result.

No attempt was made to synchronize the catalog array to the selected-ability `last` frame; their relative timings within the saved bundle are not fully qualified.

## Existing RR2 readiness decision path — research interpretation, not native REA code

In `addon/RiftReader2Casting/model.lua` (`self:Read()`), the already implemented diagnostic checks:

1. Player frame/identity, alive player and target, selected ability detail; without these it is `blocked`, source unavailable or identity changed.
2. Unsupported ability type (`passive`, `positioned`, `autoattack`), effective target mismatch or `outOfRange`; these block selection context, **not learning**.
3. Castbar availability and remaining effective cooldown. Positive `currentCooldownRemaining` yields `waiting/cooldown-ability-or-gcd`. This is **not independent GCD proof**; cooldown paused/invalid remain distinct reasons.
4. Active cast/channel produces a separate `waiting` reason.
5. `unusable` flag and resource sufficiency; Power/Mana/Energy/Charge/Spirit/Planar values can block use.
6. Only after those checks, `status=ready` and `reason=observed-ready`, meaning the **reader's** diagnostics have no reported blocker; the RIFT game remains responsible for cast admission.

The code's order matters. For example a selected ability with a positive cooldown is labelled waiting before the `unusable` condition is checked; therefore a single displayed reason is not exhaustive proof of every potential restriction. Missing cost fields remain unknown. The model checks `ad.target~=target` and does not validate all ability types equally; do not turn its Cast picker into a general spellbook completeness oracle.

## What REA has and still needs

**Supported now:** API available-list can include unusable entries; exact IDs and names need separate treatment; the RR2 selected-readiness reason model separates cooldown waiting, active cast/channel, reported unusability, target/range and resource conditions.

**Unknown:** truly learned/learnable at current level, exact shared GCD/native queue state, authoritative client/server cast rejection, independent rank/Role differences and native implementation addresses.

SC-104 is a completed **source interpretation task**, not SC1 phase completion. **SC1 needs SC-102's native spellbook/role/eligibility UI and SC-103's variant/rank evidence** before it can be labelled complete. Independent SC-201/SC2 outcome tracing can proceed using saved exact-event evidence even if SC1 remains blocked.

## Provenance and verification

Reader source and exported catalog source hashes are recorded in [SC0](REA-RIFT-SPELLCASTING-SC0-BASELINE-2026-10-27.md) and [SC-101](REA-RIFT-SPELLCASTING-SC1-API-CATALOG-NOTES-2026-10-27.md). Validation must confirm the 10 explicit `unusable=true` records, 45 missing-field records, and preserved exact selected-ability status on the historical JSON. No live game input, native analysis session, RR2 code change or controller action was used.
