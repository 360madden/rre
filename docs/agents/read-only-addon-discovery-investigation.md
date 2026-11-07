# SC-616 — Richer addon discovery: retain batch capture and add bounded transitions

Read-only investigation returned by `/root/addon_discovery_research`, November7,2026. Manager independently inspected current RRECollector code and the client-generated API reference. **Recommended shape: existing batch snapshots + manually armed, capped event receipts + final touched-ID batch.** No source change, deployment, live event proof or new addon is claimed.

## Existing features already worth retaining

`addons/RRECollector/abilities.lua:6-16` bounds list/unique sizes and whitelists36 Detail fields. Lines51-68 perform one List and one batch Detail when enumeration is complete, with bounded scalar fallback. Lab2's accepted54-ID capture is already efficient; broad per-frame rescanning would add work without establishing better evidence. `main.lua:193-223` preserves a prior complete snapshot on failure/partial capture. `ui.lua:391-425` already supports manual readiness inspection and leaves GCD/LOS unknown. `context.lua:6-9` records identity/resources/combat/XYZ; it currently omits useful documented context fields. `capabilities.lua:8-24` does not yet probe the proposed event/Buff/Castbar paths. Exact file hashes and retained source copies are in the [machine receipt](read-only-addon-discovery-investigation.json).

The complete client-generated API Atlas reference used for manager review has1940/1940entries,0errors, client label `Oct 23 2026 11:32:27 RIFT-BUILD-12`, internal `STABLE-1-1178-A-1256632`. Its client-version fields match SC614's saved Lab2 capture; that is a reference match, not fresh proof every event endpoint exists or delivers on Lab2. The feature agent also read the separately hashed1939-entry reference. Neither snapshot is a new runtime capability receipt.

## Prioritized changes and gates

| Priority | Change | Discovery value / implementation boundary |
| --- | --- | --- |
| P0 | Extend one-shot capability probe to exact Ability.New event paths, Unit.Castbar and Buff List/Detail/events | Small; proves present/nil/error before relying on historical docs. No arbitrary function dispatch. |
| P1 | Add manual Arm/Stop event witness, initially at most256 normalized events and256 touched ability IDs | Highest value: real add/remove/usability/range/target/cooldown transitions with bounded memory. Handlers no-op while disarmed; normalize exact event payload types and preserve false/zero. |
| P1 | Extend context whitelist with zone, availability, focus, planar/planarMax, mentoring, target relation/type/radius | Small; binds scene and target changes better. Preserve raw zone identity; resolve/display names only through separately verified APIs. |
| P2 | Separate optional castbar/buff arm mode for player and selected target | Correlates an observed action with castbar/effects. Does not independently prove command acceptance, exact-target success or server execution. Avoid broad combat-event ingestion initially. |
| P2 | Calling-specific, offline-generated/source-hashed candidate catalogs with frame budget/cancellation | Useful only when a specific static-ID question resumes. Current Warrior-only candidate lookup correctly defers for Lab2 Rogue; do not disguise it as a missing Rogue runtime ability. |

The documented ability events are Add, Remove, Usable.True/False, Range.True/False, Target, Cooldown.Begin/End. At Arm take baseline List/Detail/context; append bounded scalar event receipts with local sequence and Frame/Real clocks; at Stop batch-read only touched IDs and capture final List/context. Persist a separate receipt rather than replacing `latest`. Record dropped/malformed counts and explicit unavailable fields. Prefer deltas to continuous broad polling, but measure event volume and stop cost before claiming performance gains.

The initial256 caps are a proposed design bound, not measured sufficiency or an implemented contract. A small event module is plausible; exact code size/performance remains unknown until implementation. API Atlas already supplies broad API documentation/search and bounded collection patterns; keep that responsibility there. RR2 remains the telemetry/native-control workflow. RRECollector stays one focused research witness.

## What richer features can and cannot establish

- **K/API-listed:** existing snapshots are strong; Add/Remove receipts can establish delivered changed-state observations.
- **U/current readiness:** range/usability/cooldown/target events materially improve transition evidence. Independent GCD, LOS and final cast/server outcomes remain separate.
- **L/learnable and F/future-locked:** unresolved. An explicit-ID Detail response or absence does not prove eligibility/locks.
- **B/game bindings:** unresolved through the examined exact paths. `Inspect.Action.List/Detail` and `Inspect.Soul.List/Detail` are absent in the documentation index and were nil in accepted older runtime probe. RRE pins are research display state, not game action-bar bindings. Other hypothetical APIs remain unknown, not globally disproved.

Offline acceptance should fake exact Event/Command APIs and verify disarmed no-ops, attach paths, monotonic sequence, false-vs-missing, caps/drop counts, malformed IDs, prior-good preservation, touched-ID batching, exceptions and absence of game-action calls. Run current package/TOC/script-order and literal-parser checks. A future Lab2 deployment requires an intentionally versioned source/install receipt, matching loaded UI, fresh capability receipt, reviewed Arm/Stop, an explicitly scoped operator state change, normal saved receipt and at least one expected event reconciled to baseline/final API observations. Event silence is inconclusive; one session is not restart qualification.

No addon implementation or live qualification occurred in SC616. No Lab1/physical live work, external repo edit, Ollama or FreeBuff. See [SC617 transport investigation](read-only-addon-protocol-investigation.md) for how richer receipts could reach an external consumer; a data format does not itself create a transport.
