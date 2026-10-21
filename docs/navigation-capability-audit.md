# NAV-001 — Minimum navigation capability audit

Date: October 21, 2026. Manager: GPT-6 Astra Pro; reasoning metadata unavailable. Starting RRE commit: `e9c72f788ef86e8cd43118d767eebe5b14399890`.

This completes an evidence audit, not a native navigation trial. The [machine record](navigation-capability-audit.json) pins 15 source/evidence files and gives exact source ranges. Original binaries were not rehashed or accessed, no game/VM input occurred, and no independent reviewer was launched. Historical static findings remain historical. Read-only inspection found newer, uncommitted RR2 dispatch-fence work; it was preserved rather than edited or treated as deployed.

## Decision

**Prepare one ordinary ground-destination request, then observe activation and candidate cancellation. Do not resume the type-7 investigation or trace another receiver pointer as a prerequisite.**

A normal, reviewed client gesture can demonstrate its connection to the player through independent observations. We do not need a recovered native calling convention, complete camera matrix, selected-target feed, or complete object model to prepare that UI-level test. None of these shortcuts permits assuming the current gesture, input binding, click location or physical stop.

Follow remains an alternative, not the first route: the inspected RR2 producer exports the player, not a selected non-self entity. A meaningful follow test additionally needs target identity/position and later no-resume evidence. Manual W/S-style pulses are transport evidence, not a destination or pathfinding capability; do not repeat those baselines merely to keep research moving.

## Compact capability matrix

| Candidate/component | Supported by retained or inspected evidence | Missing / disposition |
| --- | --- | --- |
| Ordinary click-to-move | Saved event -> segment query -> destination setter/consumer chain. RRE source reports preserve exact-build evidence. | Current gesture and enable setting are unverified; current player ownership is not established by the RVA. Select for a UI-level readiness test, not native invocation. [S01, S02] |
| Follow | A `follow` name/command-family association and distinct follow-state handling exist in saved static research. | Actual command syntax/target, current target observations, stop and no-resume behavior are unqualified. Keep as secondary route. [S02, S07, S08] |
| Manual movement cancellation candidate | Saved input-action branches call follow-clear and C2M-clear separately. Historical short movement trials establish bounded input and displacement only within their own scope. | Use the current verified **backward action**, not a guessed key. The input-update path can return early while follow is active; clearing fields or releasing keys does not prove physical stopping. [S02, S09] |
| RR2 native action transport | Client action carries keys, hold duration, button, relative deltas and wheel. Native response distinguishes input insertion/release from game response. | No destination client-X/Y member in the inspected action. Mouse button down/up is possible, but camera cursor preparation can preserve an arbitrary cursor or reposition it; it is not an exact reviewed ground-point contract. [S04-S06] |
| Player observations | Source reads player ID and XYZ. The saved October 19 receipt contains one player with successful coordinate fields. | Historical receipt is not fresh today; `gameReady` is false. Current rate, scene binding and during/post-cancel coverage must be qualified. [S07, S08] |
| Selected target | V1 research mentions an optional typed target path. | RR2 `observation.target` is the **process identity**, not a selected entity. Do not invent an entity ID from PID, player ID or synthetic goal. A selected-target consumer is later work. [S07, S08] |
| Old V1 arrival/obstacle runner | Its source implements foreground click delivery. | It also performs lateral detours, repeated re-aiming and heading presteps. That behavior cannot isolate one native request's obstacle routing. Reuse observations/transport selectively, not the whole driver. [S03] |
| Input coordination | RR2 has committed offline queue work and newer working-tree dispatch-fence work. | Its current status explicitly says not live-enabled. Do not duplicate it, deploy it here, or infer exclusive live ownership from passing fake-guest tests. [S11, S12] |

## Binding contradiction remains visible

Historical movement/usability prose says Q/E strafe. Joey previously disputed that mapping for RIFT-Lab-1. This run did **not** view original binding pixels or inspect the active game, so it cannot adjudicate the conflict. Both current activation gesture and cancellation key remain null in the machine packet. A fresh identity-bound binding/setting review by the execution owner must settle them before input. No default WASD/QE semantics are adopted. [S09, S10]

## Two important limitations reproduced, not merely proposed

The unchanged accepted M4A functions were exercised in a new disposable, offline-only report:

1. `early_guard` returned `cancelled` when cancellation was requested, and again when the later synthetic player X changed from 2 to 4. This correctly terminates the original decision/intention state machine, but it is **not evidence that physical motion stopped**. A physical-stop evaluator must continue reading independent observations after command cancellation. [S13, S15]
2. For a hypothetical detour with direct distances `10 -> 11.180339887498949 -> 5 -> 0`, `classify_progress` returned `moving-away` on the first outward leg. Applying that terminal rule to a native-route experiment could reject a successful detour before observing it. Keep raw trajectories and the observation budget; do not assume distance must fall at every sample. This is a synthetic counterexample, not an observed RIFT route. [S14, S15]

Job `rre-nav001-semantics-20261021-01` exited 0 with **3 assertions**. Result: `artifacts/navigation-capability-audit-20261021-01/semantic-counterexamples.json`, SHA-256 `6fa88c5ca35a8c0fa218efde7ecd41ea707f5da4cbf6a54ce60b0aeb94bbe37d`. No original fixture, replay source or policy was changed. These checks are not additions to the historical 435-test count.

## Next smallest discriminating test

The [NAV-002 packet](navigation-first-behavior-test.md) asks: **does one verified ordinary ground request start movement, and does one approved currently bound backward-action pulse stop it before arrival?**

It has one activation, one planned cancel, no repeated click, no re-aiming, no scripted detour and no injected native function. Before use, the execution owner supplies the current setting/gesture/binding, a location-bound action path, and advancing player observations aligned with the action interval. A deadline is a trigger for reviewed takeover, not proof that latched motion stopped.

Current report status: **NAV-001 audit complete; NAV-002 packet drafted but not execution-ready.** The remaining inputs are concrete interface/observation prerequisites, not an excuse for new engine scans. The RR2 owner already controls the relevant transport/coordination work. RRE owns only this evidence contract and later file-only analysis until further scope is established.

## Resume without repeating this audit

Read the two machine records and recheck their source hashes. If an externally owned file changed, inspect the actual delta instead of redoing every source or accepting an old hash. Supply the missing route-specific evidence through the existing owner; do not touch the preserved Pathfinding scripts, launch duplicate workers, or build another capture/queue framework. After two distinct non-decisive probes park the specific lead, preserving what failed and the evidence needed to reopen it.
