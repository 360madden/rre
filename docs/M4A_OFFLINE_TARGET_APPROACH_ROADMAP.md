# M4A: Offline stationary-target approach — executable micro-roadmap

**Created:** 2026-10-19 (America/New_York)  
**Repository:** C:\work\rre  
**Parent plan:** ROADMAP.md / docs/roadmap-tasks.json  
**Priority:** P1 preparatory slice, in parallel with ongoing M3 native-pathfinding research.  
**Authority:** Manager-only writes to shared plans/contracts; workers write only their assigned existing lane files.

**Current execution checkpoint — 2026-10-19:** G0/M4A-001 is **integrated** in commit `899a158f0da7ef800f3dfd9a69275aa6106ca165` (follow-up task-board status commit recorded in main history). Exact-build and six-worktree preflight passed; all **13 synthetic cases / 24 samples** pass `node tools/validate-m4a-seed.mjs`. The original RRE evidence and roadmap validators passed. G1/G2 tasks M4A-002 through M4A-005 are dependency-ready but **no genuine independent Codex worker was launched** in this manager-only session. A fresh direct Codex worker admission on **2026-10-19 17:17 EDT** verified that the quota is *still blocked*: job `rre-m4a-c2m-capacity-and-work-20261019-01`, thread `01a15606-e9ec-7be0-ac23-6d8348faa47c`, exit **1**, with retry reported for **2026-10-24 19:13 local**. The other three agents were not launched; all four research worktrees are clean. G1/G2 are now **blocked on capacity**, even though their G0 dependencies are met. The offline replay CLI does **not** yet exist and M4A is not complete.

## Achievable target: one bounded, testable deliverable

Create a **deterministic offline target-approach decision/replay prototype**. It consumes a time-ordered sequence of *synthetic or previously saved* player/selected-target telemetry and returns annotated, replayable **decision intents** (approach, arrived, safe-stop reason). It must **never** issue movement commands, interact with a running game/process, attach a debugger, modify memory, or claim a validated native route.

**Success, measurable without live game:**

1. One local CLI with an explicitly offline/replay-only API can run all supplied cases and generate deterministic JSON containing one state-transition trace per case.
2. The suite handles **at least eight** test scenarios: already-arrived, approaching-and-arriving, stuck/no-progress, moving away, stale sample, selected target changed, operator cancellation, unsafe height, and missing/invalid target. Include nonmonotonic time and invalid numeric input tests.
3. Input/output and horizontal/vertical coordinate conventions are documented, grounded in existing RiftReader provenance, and tagged as **synthetic/offline**. A fixture cannot be promoted to *live* evidence.
4. The state machine is fail-closed on invalid data, target changes, time gaps, and unsafe conditions. Once terminal, it does not restart without a new explicit replay/session reset.
5. No runtime game-control backend, native route API, network request, install, or full-binary REA analysis is added. Output "approach intent" is a hypothesis/decision for downstream research, never an issued input command.
6. Each owned lane passes tests and commits only allowed paths; independent QA and Manager acceptance check deterministic replay results, source identity, no conflicting edits, and exact provenance. All previous RRE regression tests remain green.
7. The final acceptance report shows passed/failed fixture counts, branch/commit IDs, important limitations, and states that **M4 and M5 are still gated**.

**Non-goal:** Full working in-game navigation or a recovered native pathfinding ABI. Those require later M3/M4/M5 evidence/approval.

## Why this scope is achievable now

RiftReader v1 already documents current-position telemetry, target information, a route planner and fail-closed navigation states. Reuse that terminology and prior evidence as **read-only references** (e.g. \`C:\rift modding\RiftReader\docs\navigation-waypoint-v1.md\`). RRE M1 is integrated and V7 provenance tooling exists; M2 C2M/follow findings are integrated. **M3 remains incomplete:** \`TtPathfinding\` (job type 7, table \`queue+0x210\`) does not yet have a demonstrated populated handler/producer/player link. The new offline simulator must work without that interface.

All game-specific claims are keyed to binary SHA256:
\`7c356c9dde9e12fcbff3c08d953b0630b48b1510a0ffb36e4ec164606e7b17bd\`.
Do not read it for ordinary synthetic tests; its identity is only metadata. Never convert the observed virtual-table **slot 18** of \`hkpMultiThreadedSimulation\` into job type 7.

## Architecture boundary and data contract

- **New shared, Manager-owned:** \`docs/m4a-offline-target-contract.json\` and \`docs/m4a-offline-target-fixtures.json\`. Treat these as the locked contract and test inputs after G1.
- **Integration output (future):** \`tools/offline-target-approach.py\` (pure replay CLI; Manager integrates reviewed work) and its own tests under \`tools/agents/validation/\`.
- **Simulation source:** \`source.kind = synthetic-fixture\`, with no PID/HWND/process state. Historical snapshots, if later adopted, need their original hash, timestamp and offline/staleness label. Do not read live addresses for this task.
- **Frame:** use X/Z as horizontal coordinates and Y as vertical. Units are *fixture-defined meters*, not independently proven Rift-world meters. Distance is horizontal X/Z; vertical difference is evaluated separately. Raw yaw and forward-key movement bearing are not interchangeable.
- **Sample:** monotonic \`tMs\`, \`sceneId\`, finite \`player.{x,y,z}\`, a stable \`target.{id,x,y,z}\` or \`null\`, \`cancelRequested\`, and provenance. No injected or generated control input.
- **Decision:** \`approach-intent\` is a **recommendation only**, never a pointer write or keypress; \`arrived\`, \`cancelled\`, \`telemetry-stale\`, \`target-changed\`, \`target-unavailable\`, \`height-unsafe\`, \`no-progress\`, \`moving-away\`, and \`invalid-sample\` are explicit stopping/refusal states. Any terminal state remains terminal for the rest of that replay.
- **Order of guards:** reject invalid sample/source/scene/time → manual cancellation → target existence/identity → height safety → horizontal arrival → moving-away/no-progress/time checks → emit intent. Precise ordering for simultaneous failures is fixed in fixtures/test contract.
- **Fixtures:** a small locked corpus with expected terminal outcome and optional state-trace checkpoints. No synthetic replay is evidence of real navigation correctness.
- **No-route guarantee:** the replay evaluator must not create waypoints, terrain surfaces, Havok casts or its own A*/navmesh. It only classifies a given observed trajectory.

## Dependency-ordered micro-roadmap

| Gate | Board task | Lane / exclusive ownership | Work and measurable exit |
| --- | --- | --- | --- |
| **G0: Baseline** | M4A-001 | **Manager**; ROADMAP, board, contract/fixtures | Verify repository/game hash, six worktrees, active jobs, prior tests; create locked offline-only contract and initial scenario fixtures. **Exit:** roadmap validator, fixture-contract validation, Manager Git checkpoint. |
| **G1: Fixture integrity** | M4A-002 | **Validation**; \`tools/agents/validation/m4a_*\` | Build synthetic fixture/contract validator, include negative tests for bad timestamps, source provenance, malformed numbers, changed target. **Exit:** deterministic pass/fail test output and report. Depends M4A-001. |
| **G2: Intent calculation** | M4A-003 | **C2M**; \`tools/agents/c2m/m4a_*\` | Implement pure, side-effect-free sample-to-intent recommendation. No game call. **Exit:** arrival/approach-distance tests and no-actuation verification. Depends M4A-001. |
| **G2: Safety transitions** | M4A-004 | **Follow**; \`tools/agents/follow/m4a_*\` | Deterministic cancellation, scene/target change, stale telemetry, terminal-state latching. **Exit:** independent state transition tests. Depends M4A-001. |
| **G2: Progress classifier** | M4A-005 | **Collision**; \`tools/agents/collision/m4a_*\` | Classify no-progress and moving-away from sampled displacements, not guessed velocity/obstacle collision. **Exit:** stalled/wrong-way tests and explicit "obstruction unknown" label. Depends M4A-001. |
| **G3: Assembly** | M4A-006 | **Manager**; shared \`tools/offline-target-approach.py\` | Review and integrate disjoint worker contributions, connect replay CLI, add deterministic JSON output, run fixture corpus. **Exit:** all expected outcomes match, no input/process APIs. Depends M4A-002/003/004/005. |
| **G4: Independent QA** | M4A-007 | **Validation**; \`tools/agents/validation/m4a_*\` | Independent golden-output tests, mutation/negative cases, run original RRE suite and manifest checks. **Exit:** no regression, clear failures, reproducible hashes. Depends M4A-006. |
| **G5: Acceptance** | M4A-008 | **Manager**; roadmap + acceptance report | Verify Git branch/source ownership, CLI behavior, evidence, safety. Mark **M4A** integrated only if all gates pass. **Exit:** one clear demo command and acceptance record. Depends M4A-007. |

**Independent parallel M3 lane:** M3-001 pathfinding research may run at the same time as G1/G2 in its **own** worktree, but cannot edit M4A files, block the offline simulator's finite test corpus, or claim native route capability without evidence. REA/Ghidra research remains optional and may be omitted when it adds no value.

## Maximum-useful-agent plan

When at least six *real AI reasoning sessions* are available, use **one dedicated Manager + up to five workers**: C2M, Follow, Collision, Validation and independent Pathfinding. If only four workers exist, queue Pathfinding or the lowest-priority unblocked lane. Avoid giving an idle Ghidra worker a redundant job. The Manager alone updates shared files, decides task readiness, and sequentially cherry-picks disjoint branch commits.

**Workbridge's six concurrent command jobs are not AI agents.** Before starting workers, validate actual installed Codex/subagent capability, current usage, and unknown existing processes. Previous Codex CLI jobs reported a quota stop until **2026-10-24 at 19:13**; unless a fresh supported check shows it recovered, do not launch Codex loops that will predictably fail. When unavailable, Manager may complete preflight/contract/documentation but must not pretend that single-agent tool calls are delegated workers.

## Acceptance examples (fixtures, not movement commands)

1. Already within 1.5 fixture meters → \`arrived\`.
2. Stable target, advancing trajectory into arrival radius → intermediate \`approach-intent\` then \`arrived\`.
3. Position stationary past the 1,500 ms progress window → \`no-progress\`.
4. Horizontal distance worsens more than 0.75 fixture meters → \`moving-away\`.
5. Consecutive sample time gap exceeds 1,200 ms → \`telemetry-stale\`.
6. Target identity changes while replaying → \`target-changed\`.
7. Operator cancellation appears → \`cancelled\` immediately.
8. Target/actor vertical difference exceeds 2.0 fixture meters → \`height-unsafe\`.
9. Missing target identity or non-finite coordinate → \`target-unavailable\` / \`invalid-sample\`.
10. Timestamp duplicates or reverses → \`invalid-sample\`.

Values are chosen for synthetic fixture reproducibility, **not tuned from qualified Rift movement trials**. Native and gameplay validation may later revise them under a separate documented decision.

## Handoffs and failure recovery

- Every task has a single ID, assigned lane/worktree, writable paths, dependencies, acceptance checks, agent/job IDs and commit hash. These live in \`docs/roadmap-tasks.json\`.
- Worker reports contain the sample-contract version, source hashes, observed versus inferred claims, commands, exact exit codes and unresolved limitations. "Passed" requires tests, not just agent statements.
- Manager validates \`node tools/validate-roadmap.mjs\`, \`node tools/verify-integrated-navigation.mjs\`, existing Python unit tests, fixture integrity, and only reviewed source/diff before accepting.
- On quota/timeouts inspect command status and worktree; preserve partial artifacts and record \`blocked\` or \`review\`. Never start a second writer in a lane or call a queued task "running".
- No background execution is promised after the active chat session. A resumed session must reconcile current Git and process state, then choose the next dependency-unblocked task.

## Relationship to overall native-navigation roadmap

**M4A is offline rehearsal infrastructure, not M4 completion.** Full M4 must still wait for useful M3 native pathfinding/obstacle/selected-target interface evidence. Live trials M5 require separate authorization and actual cancellation with T0 → T1 → T2 gates. M6 stationary-target approach **in-game** remains blocked until M4/M5. M7 performance/patch-hardening stays deferred.

**Success means a transparent, deterministic, testable offline approach-decision demo.** Not a simulated claim that Rift itself navigated, and not unbounded redesign.
