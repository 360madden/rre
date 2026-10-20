# World awareness: local world inspector

Authorized by Joey on October 20, 2026 after proposing entity identity, collision-hit ownership, camera projection, player clearance and native-navigation reuse. Repository: `C:/work/rre`. The Manager is this ChatGPT session; independent reviewers may work only in their assigned lanes. Model reported by the Manager: GPT-6 Astra Pro. Reasoning level: not available (leave blank in machine records).

## Current checkpoint

WA-001..004 are integrated as contract `02fbcc1` and implementation/research `5478207`. The file-only inspector has a real historical player-only report and a separately labeled synthetic multi-object report. The final regression run passed 80 distinct tests. WA-005 is blocked on unfinished independent full-code review, not on failing tests. WA-006 still needs actual simultaneous non-self entities, a qualified physical hit/owner and camera calibration. Read [the research/validation record](world-awareness-research-2026-10-20.md) and the machine task board before resuming; do not redo the accepted consumer or treat it as live recognition.

## Goal and non-goals

Build a read-only inspector for one small RIFT scene, retaining object identity, source coordinates, source age and uncertainty; eventually associate physics hits with scene objects and independently validate camera projection. A rendered label, memory offset or positive unit test is not live recognition or navigability proof.

Three distinct layers must never be collapsed: gameplay entities/semantics; physical shapes/surfaces; screen projection/visibility. A unit list need not contain scenery, a collision shape need not have a gameplay name, and an on-screen point need not be unobstructed or reachable.

This track runs alongside M3-001; it is not blocked on the unknown type-7 handler. M3 research is preserved. No replacement pathfinder, game input, debugger attachment, memory writes, process control, dependency installation, or edits to RiftReader/RiftReader2/Workbridge are authorized here. Source files and saved observations from those repositories may be read. No public publishing.

## Ordered tasks (machine status is in docs/roadmap-tasks.json)

| ID | Owner | Deliverable | Acceptance |
|---|---|---|---|
| WA-001 | Manager | This roadmap and an explicit observation/inspector contract | Bounds, provenance, identity/empty-list ambiguity, no-actuation boundary and task dependencies defined; roadmap validator passes |
| WA-002 | C2M research lane, Manager integration | Source-pinned entity/API audit and concrete capture gaps | Read actual producer code, distinguish player/target/party/nearby scopes, preserve unknown coverage and conflicting same-ID observations; no claim Unit.List works from its name |
| WA-003 | Collision research lane, Manager integration | Bounded exact-build query/result ownership investigation | Reuse original PE/scanners, record bytes and V7 receipt, distinguish geometric result from an entity ID; qualify at least one result-copy/owner link or explicitly leave it unresolved |
| WA-004 | Manager | File-only world inspector and deterministic offline fixtures | Parse saved data without executing Lua, deduplicate by object ID not name, preserve conflicts/missing positions, explicitly partial coverage, self-contained local report; no game/process/network path |
| WA-005 | Validation lane/Manager | Regression tests and independent review | Wrong schema, malformed/nonfinite data, stale/unbound data, reused IDs, duplicate role records, unknown collision/visibility, projection math and overwrite prevention checked; evidence report retains source hashes |
| WA-006 | Manager, future observation owner | Real small-scene entity/collision/camera qualification | Independently observed player and distinct other entities, known surface/hit, current scene binding, camera-only variation and restart/scene invalidation; no inference from synthetic fixtures |

WA-001 precedes implementation. WA-002 and WA-003 may be researched in parallel. WA-004 depends on WA-001 and WA-002, not type-7. WA-005 reviews the implemented result. WA-006 stays blocked until actual multi-object/geometry/camera evidence and the applicable observation permissions exist. Successful WA-001..005 does not complete WA-006, M4, M5 or M6.

## First useful implementation slice

A file-only inspector is the initial consumer, not a new live collector. Reuse saved ReaderBridge JSON where available; do not execute SavedVariables Lua or silently substitute synthetic objects for missing game captures. Supply separately labeled synthetic fixtures for deterministic tests. Record original input SHA-256, source kind, source format, missing binding, data freshness and coverage. Unknown is not zero, absent is not empty, and an unavailable nearby list is not a proof that no nearby objects exist.

Produce a local HTML/JSON report with a table, a raw X/Z coordinate plot with separate Y heights, and candidate projection only when an explicit camera transform with matching input hash is supplied. The raw X/Z plot is not a validated walkability map. All physical obstruction, support, line-of-sight and reachability fields remain unknown without qualified sources.

Do not propagate an entity across separate captures by a name, heap pointer, coordinates, or coincidental ID. A future tracking key requires qualified session/scene/generation. A self-selected player and the player record must not become two different physical objects.

## Research priorities after the first slice

1. Qualify actual available unit enumeration and its limits, with at least two distinct non-self IDs and fresh coordinates. Check load/unload, missing details and list caps. Distinguish logical unit IDs from reusable native addresses.
2. Trace the hit-result chain near `0xF671C0 -> 0x13D44D0` and result conversion helpers; determine whether hit point, normal, shape and owner are returned or lost. Do not equate a hit vector with an object ID.
3. Map physics shape/collidable to scene transform and, where present, gameplay entity. Investigate the existing character-proxy lead separately for actual player clearance.
4. Revalidate camera candidates by camera-only rotation/zoom, viewport changes and independent landmarks. Projection is not occlusion. A bridge/road pair sharing X/Z must remain vertically distinct.
5. Connect qualified observations to native navigation only after ownership and movement contracts are established.

## Resumption and ownership

Refresh Git HEAD/status, six existing worker worktrees and actual command jobs before new writers. Preserve the two historical untracked raw-probe files. The Manager alone owns `ROADMAP.md`, task board, this document, contract, shared inspector and final integration. Reviewers use separate lane worktrees; no nested agents and no writes outside their lane. Read-only review jobs can return text for Manager preservation without modifying their worktrees. Failed or permission-denied agent runs are not completed research.

Keep a checkpoint with source commits, input hashes, real job IDs/exit codes, accepted versus unproven findings and the next specific experiment. Work does not continue after the session unless separately scheduled.
