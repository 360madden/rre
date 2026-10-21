# NAV-002 — One ground request, observed activation, observed stop

Date: October 21, 2026. This is a **draft observation protocol, not an executable plan or live approval**. The [machine packet](navigation-first-behavior-test.json) is deliberately not ready: current identity, gesture, input point, cancellation key, timing evidence and measured position tolerance are unset. The [NAV-001 audit](navigation-capability-audit.md) explains why this route was selected.

## Question and minimum scope

Can one ordinary RIFT ground-destination gesture start the player moving, and can one currently verified backward-action pulse stop that movement before the destination is reached?

Use a nearby visible ground patch on the same unobstructed surface. The click location is identified in a fresh reviewed client image; **world XYZ for that patch is optional at this T0 stage**, provided a reviewer can distinguish stopping short from arrival. Do not invent a ground position or selected-target ID to satisfy M4A's synthetic target schema. A full camera matrix, object catalog and native function calling convention are not prerequisites for this UI-level experiment.

The current action contract can press a mouse button, but does not encode a reviewed destination client-X/Y. Its cursor preparation is for bounded camera operations and can preserve or relocate the cursor. The execution owner must qualify exact point delivery or an equivalently recorded, explicitly approved physical action before using it as a ground request. Do not run the legacy multi-click/re-aim driver as a substitute.

## Ownership and current blockers

RRE owns this specification and file-only interpretation. The existing RR2 owner owns any transport, telemetry or live-capture implementation. RR2 currently has unfinished dispatch-fence changes; this task does not edit, commit or deploy them. No independent code review is claimed here.

| ID | Required evidence / contract | Current disposition |
| --- | --- | --- |
| NAV-B01 | Exact lab/process/window/scene, current click-to-move enable setting and actual activation/cancel bindings | Missing. Historical Q/E prose conflicts with Joey's correction; no mapping is assumed. |
| NAV-B02 | One reviewed-location-bound request with actual delivery/release evidence and no silent retry | Missing for this experiment. Existing button/camera actions are not this complete contract. |
| NAV-B03 | Fresh advancing player samples before/during/after cancel, acquisition intervals, time alignment, scene images and measured stationary tolerance | Historical player-only shape exists, but current coverage and noise/timing qualification are missing. |
| NAV-B04 | Separate live approval, sole actual input owner, clear test area and reviewed operator takeover | Not granted or established by this packet. Offline queue tests are not proof of live exclusion. |

This does not require T0 already to have succeeded. T0 is the experiment that tests real cancellation. It does require a reviewed response to failure; releasing inputs or a script deadline does not bound a persistent native command. A single-owner supervised experiment need not wait for unrelated multi-agent features, but actual ownership must be established and no concurrent controller may be assumed harmless.

## Proposed sequence after all prerequisites are resolved

**Prepare without activation.** Verify current build/process epoch, player, scene, exact window/client geometry, foreground and absence of text input. Inspect the actual setting and movement binding pixels. Record one approved ground patch and one current backward-action cancellation candidate. Freeze acquisition, timing and position-tolerance policy from a stationary baseline. Preserve any stricter existing review/arm/freshness limits. Inadequate observation rate or ambiguous images mean no input.

**One activation.** Retain an immediate pre-action frame, then exactly one verified ordinary ground request. Record actual gesture, client point, capture identity, execution interval and delivery/release outcome. No W prestep, turn prestep, repeated click, scripted re-aim or custom detour. Begin retaining the whole player trajectory, not just an endpoint.

**Observe motion, then test cancel before arrival.** Confirm actual displacement in advancing independent samples, with the destination still ahead on clear ground. Use the one approved backward-action pulse and release. The proposed 100 ms duration is an experimental choice inside the historical transport bounds, not a current key-binding or timing qualification. Record cancellation delivery separately from game response. No activation retry is permitted if delivery is uncertain.

**Keep observing after cancellation intent.** Do not stop collecting because M4A says `cancelled`. Require sufficiently many new samples over a nontrivial interval, stable XYZ within a predeclared baseline-derived tolerance, consistent images, no resumed movement during the interval, and evidence that the stop was neither arrival nor obstacle contact. Preserve immediate-after and settled images and the original records.

**Close or take over.** The proposed 10-second post-activation observation budget triggers the approved cancel/takeover procedure; it is not proof of stopping. Scene changes, stale data, identity/focus changes, unexpected input or conflicting evidence abort interpretation. Use only the reviewed recovery plan. An uncertain run remains uncertain; never replay it automatically or label STOP/key-up as native cancellation.

## Observation policy: proposed, not calibrated

The machine packet proposes a maximum source age and inter-sample gap of 1,000 ms, at least three baseline samples spanning 1,500 ms, and at least three post-cancel samples spanning 2,000 ms after a proposed 1,000 ms settling allowance. More samples may be needed to satisfy both count and span. These are test-design values, not measured RIFT guarantees; an incapable observation source blocks the attempt rather than silently skipping checks.

`positionToleranceWorldUnits` remains null. Establish it from the actual stationary baseline, coordinate precision and an explicitly reviewed bound before activation; do not reuse the historical 0.05 reporting threshold as a calibrated noise limit or label raw coordinate units as metres. Require acquisition interval ordering in a shared guest monotonic clock or a conservatively verified clock mapping. Host receipt time alone cannot establish exact guest action latency.

## Outcomes and limits

A positive result requires observed movement **before** cancellation and observed stopping **after** it, away from arrival and blocking surfaces. Supported classifications are activation-and-stop observed, activation with failed cancellation, no activation observed under adequate coverage, inconclusive, or aborted. A stationary player that never moved cannot pass the stop test. A stopped-following message cannot certify C2M. Missing samples, arrival before cancellation or unexplained camera/scene changes are not passes.

A T0 pass qualifies only the observed C2M mode/scene/session. T1 clear-ground destination testing still follows T0; T2 obstacle-with-opening testing still follows T1. A genuine detour may initially increase target distance. Preserve the original M4A synthetic contract and add route-specific interpretation later rather than converting its `moving-away` terminal state into a general routing verdict.

## Narrow handoff; no new framework

Resolve NAV-B01 through the current execution owner's existing observation workflow. Resolve NAV-B02/B03 through the existing control/capture modules, after ownership and scope are agreed; do not create another recorder, queue, generic agent framework or native pathfinder. Keep current RR2 work intact. The delivery artifact must contain real image/sample/action records and their hashes, not filenames described as inspected pixels.

The RRE Manager checks the returned evidence, completes this readiness packet, then advances the minimum offline adapter. **NAV-002 remains blocked until its actual route/observation contract is resolved.** This is a concrete handoff, not a reason to restart speculative engine scans. After two distinct non-decisive probes, park the specific lead and retain the exact reopening trigger.
