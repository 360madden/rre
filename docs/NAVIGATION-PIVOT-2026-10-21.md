# Navigation research pivot — October 21, 2026

**Latest checkpoint:** NAV-001 is accepted in `6c8a566`; reuse the [source-pinned capability audit](navigation-capability-audit.md). The [NAV-002 ground-request/stop packet](navigation-first-behavior-test.md) is drafted and consistency-checked but not execution-ready. Current gesture/binding evidence, location-bound delivery, time-aligned reference observations and execution ownership/approval remain explicit prerequisites. The initial NAV-001 READY/NAV-002 queued statements below describe the pivot's earlier checkpoint, not current scheduling. See `roadmap-tasks.json` for current states. No type-7 dependency, new live authority or independent review was introduced by this follow-up.

Adopted following Joey's direction to repivot navigation research so it does not stall on dead ends. This supersedes the priority order in ROADMAP-UPDATE-2026-10-21.md. ROADMAP.md and roadmap-tasks.json remain authoritative. Model: GPT-6 Astra Pro. Reasoning level: unavailable; machine metadata stays blank.

## Decision

**Behavior-first, reuse-first, evidence-bounded.** The next question is not “where is the entire pathfinding engine?” It is “which existing player-facing movement mode can we identify, observe, stop and evaluate in one small scene?” Investigate internals only to close a specific missing link for that test.

The earlier plan still made M4-001 depend on M3-001, despite describing alternative native routes. That dependency made the type-7 Havok investigation a practical blocker. Remove it from the primary path. Preserve its results, but defer further speculative expansion unless new evidence links it to actual player movement.

This is not a claim that type-7 is irrelevant or native pathfinding is absent. It is a priority decision under uncertainty. It does not authorize a replacement pathfinder, game input, process attachment, native capture, runtime changes, or edits to RR2. Existing live-approval and source-access boundaries remain intact.

## Current evidence and what it does not establish

The fresh preflight began at RRE main 1ecd1d059d5197210ea9ad4cdf98fb5616a9dd21. Workbridge reports 0.16.3-dev. Five specialist worktrees are clean; Pathfinding still contains two untracked jobtype-stack-encoding scripts. Those and the two historical main probe files are preserved. Workbridge diagnostics showed one unrelated RogueTV job, not an RRE reviewer or research worker. No new workers are launched by this pivot.

- C2M has a retained candidate destination setter/consumer at RVA 0x562BC0. Player ownership, coordinate semantics, actual gesture and obstacle routing are not established.
- Follow research identifies separate state-clear paths and a common input-dispatch relationship. That is not evidence of actual in-world stopping or obstacle avoidance.
- RR2 has separately recorded supervised input and observation capabilities. Reuse their evidence and capture path, not their conclusions outside the tested scope. Input delivery/key-up is not proof that a latched follow or destination request stopped.
- M4A's 13 synthetic traces and VE-001/VE-002 are accepted within their offline scopes. Do not rebuild them. The last pre-pivot full gate was 435 tests; a new run must be reported separately.
- The historical keybinding descriptions conflict with Joey's earlier correction. Do not rely on a conventional WASD/QE mapping or the prior roadmap's Q/E claim. Verify the active lab's actual binding evidence before a future trial.

Sources: docs/agents/c2m.json; docs/agents/follow.json; docs/m4a-acceptance-report.md; docs/visual-evidence.md; docs/old-wheel-image-review-2026-10-21.md. These are saved findings, not current live observations.

## Primary sequence

| Step | Deliverable | What unlocks the next step |
| --- | --- | --- |
| NAV-001: smallest useful evidence audit | One compact capability matrix for existing player-facing C2M/follow, reference player/target observations, and cancellation. Use retained source/evidence first. Rank by a demonstrated player link, testability and missing evidence, not by an appealing engine label. | Exact source references; what is known, unknown, or contradicted; one chosen next discriminating test or explicit blocker. No live success inferred. |
| NAV-002: one behavior-test readiness packet | Specify one existing input route, actual binding/gesture evidence, target/coordinate meaning, observation source and age, bounded activation, cancellation candidate and independent stop criterion. Identify the authorized execution owner and every missing permission/data prerequisite. | A source-reviewed, offline-checked protocol ready for M4 preparation, or a concrete blocker. No need to prove the whole engine or to pass T0 before preparing T0. |
| M4: minimum offline adapter | Extend the accepted M4A replay only where required by the chosen route. Retain stale-data, wrong-identity, target-change, no-progress and cancellation checks. | Reviewed adapter and verified input/telemetry contracts. Actual native response remains for T0/T1; a typed function address alone is not a usable contract. |
| M5-T0: movement and stop | Separately authorized, supervised observation of activation and cancellation for the selected mode. | Recorded cessation of movement with adequate fresh samples; an input acknowledgement alone cannot pass. |
| M5-T1: clear-ground destination | One native request and bound observation. | Supported target-directed movement or an honestly classified failure. |
| M5-T2: obstruction with an opening | One native request; no hidden manual steering, repeated re-aiming or replacement planner. | Distinguish route-around behavior, straight-line steering, stop-at-obstacle and inconclusive evidence. Failure to route is useful capability information, not permission to invent a native route. |
| M6 | Reproducible selected-target approach using the demonstrated capability and verified selected-target identity. | Actual arrival/cancel/failure trace. Optimize only afterward. |

NAV-001 is the next unblocked task. NAV-002 is queued behind it. M4 remains blocked on the chosen interface and readiness packet, not on type-7 or complete world recognition. Live trials remain blocked on their existing approvals and prerequisites. This avoids a circular requirement to prove movement before preparing the first movement-and-stop experiment.

## Research stopping and reopening rules

Every lead must name one falsifiable question, its cheapest permitted discriminating check, the output that would change the next decision, one owner, and a bounded execution budget.

**After two materially different probes without decision-changing evidence, park the lead.** An unchanged rerun does not become a new probe. Stop immediately on an authorization/tool block; preserve its result and do not route around it. A failed tool is not negative evidence about the game.

A parked lead can reopen only with a recorded new trigger: an independently observed player behavior, a direct caller/data-flow connection to that behavior, a newly qualified source/locator, or a changed tool condition that directly removes the recorded blocker. Merely finding another offset, class name, literal 7 or test-count increase is insufficient. Review priority after every probe, not after an indefinite scan chain.

Record supported, rejected, unresolved or blocked, with source hashes, coverage, contrary evidence and the next decision. Rejection is scoped to the tested hypothesis/build; incomplete scans never prove global absence. Preserve negative evidence so another session does not rediscover the same dead end.

New tooling is justified only by a reproduced failure blocking the current experiment; use the narrowest fix. Do not rebuild capture, reports, agent orchestration or a world model to avoid a concrete missing-data question. No routine repeated full-program imports or broad scans.

## Only require evidence the current experiment needs

For the first clear-ground point trial, require current player identity/position, destination semantics, observation timing, a testable control/cancel protocol and interpretable visual evidence. Add a selected-target ID when testing selected-target approach. Add camera calibration when projecting screen pixels into world coordinates. Add hit/shape semantics when making a physical-geometry claim.

Do not make complete nearby-object enumeration, every collision-owner backlink, full camera reconstruction or all WA-006 acceptance a prerequisite for every navigation experiment. WA-005 still blocks acceptance of the unreviewed inspector itself; it does not block independent work that does not consume that component. Unavailable independent review remains unavailable, not silently waived.

Use immediate-before, immediate-after and settled frames, with timestamps and fresh telemetry samples during the relevant interval when available. Preserve the observed path, not just endpoint distance. Falling distance does not prove an obstacle route; unchanged position does not identify a wall. A native detour may temporarily increase target distance, so M4A's synthetic moving-away policy must be evaluated before reuse, not blindly applied to native routing. No progress, occlusion and reachability remain distinct.

For a suspected latched command, establish an applicable cancel/recovery protocol before a live trial. T0 qualifies actual stopping; do not assume releasing a key or stopping the host clears native follow/C2M state. Keep the experiment within its specifically approved bounds and stop on stale or conflicting evidence.

## Deferred work and ownership

M3-001 is DEFERRED with evidence preserved, not completed or disproved. Reconcile the two Pathfinding scripts before any later writes to that lane; their presence does not block unrelated NAV-001 work. Collision-owner and broad world-awareness research continue only when they answer a selected test's requirement or are independently productive within their own scope.

The Manager owns this plan, the board and shared integration. C2M and Follow are the first relevant specialist sources; reviewers work in distinct lanes only when genuinely available. Do not populate six agent slots merely because six command slots exist. No new dependency, paid provider, worker launcher or external repository change is part of this pivot.

## Progress definition and resumption

Progress means a decision-relevant unknown removed: an actual input route identified; a real cancellation criterion supported; the cheapest experiment made ready; native behavior classified; or a concrete lead rejected with reusable evidence. More functions decoded, reports generated or tests counted are supporting work, not navigation milestones.

Resume from NAV-001 and the active task graph. Do not resume M3-001 merely because a historical handoff calls it the critical path. Each accepted step records exact inputs, limitations, command exits, source changes and the next eligible task. This pivot changes research order, not the standard of evidence or live authorization.

## Pivot validation

The initial roadmap check exited 1 because it hard-coded the already accepted M4A as the current goal. The corrected checker preserves that complete acceptance record under historicalM4A while allowing the registered behavior-first goal to advance. It also checks the actual dependency graph, including indirect dependencies, rather than relying on roadmap prose.

Twelve focused validation cases passed with exit 0 in rre-nav-pivot-checks-20261021-01: current pivot and subsequent NAV-002 goal accepted; restored direct/indirect type-7 prerequisites, universal WA-006 dependency, missing readiness, fabricated live authority, unbounded-probe policy and bypassed T0/T1 gates rejected. Original M4A no-input acceptance remains enforced. Saved results: artifacts/navigation-pivot-validation-20261021-01.json.

The fresh unified gate rre-nav-pivot-full-gate-20261021-01 exited 0 on October 21: **435 tests passed**, roadmap validation passed, and tool-source hashes were unchanged during the run. The 12 focused policy cases are separate checks, not newly added tests counted in 435. Full results: artifacts/research-gate-navigation-pivot-20261021-01/validation.json. These checks validate the planning/tooling change, not game behavior. NAV-001 remains READY; NAV-002 remains queued; no new live trial or independent AI review was performed.
