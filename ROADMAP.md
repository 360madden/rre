# RRE navigation research roadmap

Initialized: 2026-10-19 (America/New_York)  
Repository: C:\work\rre  
Mission: produce a **working prototype**, not a production system, that can approach a valid selected target, reuse native movement/pathfinding and collision facilities where verified, recognize obstruction or lack of progress, cancel reliably, and preserve test evidence.

**Reuse first:** Investigate the game's movement, follow, click-to-move, native routing and collision before proposing a custom pathfinder. A profiling label, RTTI name, offset or RVA is a lead, not proof of an active callable interface. An import timeout is not evidence that native pathfinding does not exist.

## Authoritative workflow

- **ROADMAP.md** (this file) defines milestones, gate criteria, priorities, dependencies, and the order of work.
- **docs/roadmap-tasks.json** is the Manager-owned task register for per-lane statuses, ownership, job/commit evidence, and blockers. It must agree with the actual worktree and job states.
- **AGENTS.md** and **docs/agent-coordination.md** govern permitted operations, the six established worktrees, branch isolation, and file ownership.
- Only **one Manager/Coordinator** maintains this roadmap, task register, shared code integration and main. The parent ChatGPT supervises; workers own one narrow worktree/lane. Workers do not spawn subagents, edit main, merge, cherry-pick, push, or edit another lane's files.
- Verify **actual AI agent runtime capacity** independently from Workbridge's reported limit of **six concurrent command jobs**. If six genuine agent slots exist, use one Manager plus at most five workers, queue the sixth lane, and rotate only when slots free. Do not launch fake/duplicate agents or fill slots with unproductive tasks.
- A task is complete only when a worker's evidence, validation and owned changes have been accepted and integrated by the Manager. Jobs left unfinished or of unknown status are not successes.

## Ordered milestones

| Stage | Current status (2026-10-19 checkpoint) | Exit criteria | Parallel work |
| --- | --- | --- | --- |
| **M0 — Inventory and safe coordination** | **Completed this pass; refresh next session** | Inspect all six worktrees, main's dirty files, current jobs, source hashes, and assigned owners; reserve ownership; identify already-completed tasks | Manager only |
| **M1 — Trustworthy research tools** | **V1–V7 integrated for bounded offline captures** | Review already-written V1–V5 hardening, rerun strict synthetic tests and bounded exact-build query, inspect diffs, integrate only after passing review; characterize V6 parser warnings and V7 reproducibility gaps | Manager owns shared code; Validation and Ghidra research in disjoint lanes |
| **M2 — Native movement and cancellation contract** | **M2-001/M2-002 static results integrated; gameplay still unverified** | Explain C2M input → segment query → destination setter/consumer, qualify input ownership/coordinates, and identify normal cancellation gestures without inventing contracts | C2M and Follow workers |
| **M3 — Native pathfinding and obstacle reuse** | **M3-001 physics-owner evidence integrated; type-7 handler still unresolved** | Identify type-7 handler registration and actual producer/output, route or steering data if present; characterize active ray/linear/shape casts and collision results; record evidence-based native reuse decision | Pathfinding and Collision workers |
| **M4A — Offline selected-target approach rehearsal** | **G0 complete; G1/G2 externally blocked by verified Codex usage limit until Oct 24, 2026 7:13 PM (CLI report)** | Achievable standalone offline-only target-approach state machine, 13 synthetic fixtures with deterministic safe stop reasons, independent QA; **not M4/M5 completion** | Manager contract; C2M, Follow, Collision, Validation in exclusive lanes; Pathfinding remains M3 |
| **M4 — Offline prototype harness** | **Blocked on useful M2/M3 interface clarity** | Reuse RiftReader qualified player and selected-target telemetry; implement narrowly scoped offline trace/replay and synthetic failure tests for stale source, invalid target, no progress, height mismatch, cancellation and state transitions | One integration owner + independent QA |
| **M5 — Controlled in-game trials T0 → T1 → T2** | **Blocked** | Separately approved supervised gameplay, fresh scene/process binding and proven cancellation. T0 movement-and-stop must pass before T1 clear-ground single destination. T1 must pass before T2 obstacle-with-opening single destination. No custom re-aiming/presteps in diagnostic trials | One game-input owner; read-only observers |
| **M6 — Stationary target approach** | **Blocked on M4/M5** | Valid selected-target identity/location, reachable approach position, observed progress, arrival, cancellation, and useful failure logs; repeatable in one small test area | Integration owner + QA |
| **M7 — Optimize and harden after a prototype** | **Deferred** | Measure real bottlenecks before speeding up; expand terrain, cold-restart/patch re-resolution and reliability only after the earlier gates pass | Later |

**Critical path:** Fresh M0 preflight → essential M1 validation → **M2 and M3 may advance in parallel** → M4 native-integration harness (after interface clarity) → separately authorized M5 live trials → M6 observed target approach. M7 is deferred. **M4A is a preparatory offline rehearsal, parallel with unfinished M3; its deterministic synthetic pass does not unlock M4 or M5.** Use `docs/M4A_OFFLINE_TARGET_APPROACH_ROADMAP.md` and the M4A task IDs in `docs/roadmap-tasks.json`. Do not gate preparatory fixture tests on nonblocking V6/V7 work, but never promote unverified data to a working native interface.

## Baseline facts that must survive every handoff

- Qualified Rift executable SHA-256: **7c356c9dde9e12fcbff3c08d953b0630b48b1510a0ffb36e4ec164606e7b17bd**. Research version: STABLE-1-1169-a-1256556. Recheck exact build before new claims; use RVAs and document static/live image-base distinctions.
- Existing six-lane work is already on main: Ghidra c7131df, C2M 9058e5a, collision 8f2bee1, follow 80fa5b3, pathfinding 40d4fbd, validation e3f0df6, coordination c7815b7. Refresh HEAD before any integration.
- Pathfinding category **type 7 / TtPathfinding** selects table at queue offset **+0x210**. Verified type-1 producer **0x8A8D8** is virtual slot 18 of Havok **hkpMultiThreadedSimulation** (vtable 0x2725568) and reads the simulation object's +0x160 queue field; separate wrapper 0x8F204 directly calls the type-3 producer in one branch. This is physics-dispatch ownership evidence, **not** a populated type-7 handler. Type-7 producer/route output and player use remain **unknown**. See docs/agents/pathfinding.md and tools/agents/pathfinding/m3-001-followup-summary.json.
- The current C2M code has candidate event/segment query, destination setter **RVA 0x562BC0**, and matching consumer. Player ownership, world frame, actual gesture and obstacle behavior are **unverified**.
- Follow-state clear at **0x534200** and a separate destination-state clear at **0x534990** are static code findings; actual in-world cancellation is **not yet demonstrated**.
- Havok collision/raycast/linear-cast code provides native candidates, but a player-walkability/clearance contract is **unverified**.
- Two REA/Ghidra whole-program attempts on the full client timed out near 450 seconds with no result. Headerless raw x64 was rejected by Windows REA. A **synthetic 2,560-byte PE** containing 603 bytes of matching dispatcher code successfully yielded one REA procedure observation in 19.6 seconds; this proves a small-PE tool path, not full binary or navigation success. See `docs/rea-small-pe-probe-2026-10-19.md`.
- The previous QA report identified V1–V7. **V1–V5** hardening was independently validated with 13 regression tests and committed as `81b5864`. **V6's 825 pefile warnings** were explained by duplicate same-parent assignment on shared UnwindInfo objects and committed as `a4fac10`, without claiming universal unwind correctness. **V7** immutable run/source/version manifests are now verified for bounded static/names scans on this exact build; see `docs/navigation-v7-checkpoint-2026-10-19.md`. This is not full-program or live navigation evidence.
- Reject old shortcuts: the custom proximity graph is **not** a native navmesh; the +/-40 player-centered box is **not** a fixed goal; cached field **+0xD8** is **not** a proven persistent destination; projected-target delta is **not** actual velocity under wall slide.

Research sources: docs/navigation-research-2026-10-18.md; docs/agents/; docs/navigation-tool-hardening-2026-10-18.md; docs/native-navigation-experiment.json.

## Per-task manager protocol

**Before assigning:** inspect git status/history/worktrees and actual jobs, reconcile docs/roadmap-tasks.json, identify unowned ready tasks, check the milestone gate, assign each lane exclusive paths and a narrow acceptance test. Do not relaunch an active task or overwrite uncommitted results.

**Each worker receives:** task ID, single research question, branch/worktree, allowed writable paths, read-only sources, exact build hash, required outputs, validation command, time/job budget, stop conditions, and forbidden actions. Worker returns commit or blocker plus evidence. Only Manager modifies roadmap/board and shared code.

**After each task:** verify lane-owned changes, tests, source hashes and limitations. Integrate reviewed commits sequentially, verify main, update task status plus next ready task, and record deviations. Use at most the verified available agent/command concurrency; preserve a command slot for supervision when needed.

**After timeout/crash:** check job status, worktree dirty paths and evidence. Mark unknown/blocked until verified. Recover from the last durable checkpoint, never create a second writer in the same lane. Do not promise work continues after this conversation without an actual supported scheduled execution mechanism.

## Hard gates (never bypass)

**G0 — Exclusive ownership:** One writer per file/branch; Manager owns main and roadmap. Existing dirty files are preserved; do not reset, checkout or overwrite them to make the tree look clean.

**G1 — Evidentiary discipline:** Every native conclusion carries build hash, bytes/source or runtime capture, observed-vs-inferred labeling, and explicit uncertainties. Static proof is not gameplay success.

**G2 — Integration discipline:** Reviewed diff, no out-of-lane modifications, relevant tests pass, correct parent/commit, board updated. Never silently mark a failed run successful.

**G3 — Native reuse decision:** A new pathfinder requires a future **explicit** decision after native facility/behavior investigation and documented alternatives. It is not the automatic fallback after inconclusive evidence.

**G4 — Live authorization:** No game input, debugger attachment, process control, memory modifications, injection, or installed-tool changes under this roadmap. RiftReader's separate live-input approval is required before movement trials. No observer time limit substitutes for a verified in-game cancellation. **T0 precedes T1; T1 precedes T2.**

**G5 — Working prototype:** The final claim requires observed target approach/obstacle trial with a replayable trace and controlled stop. Static results, green synthetic tests, or scripts simply starting do not meet the gate.

## Immediate roadmap-driven next actions

1. **M0 refresh each session:** Recheck worktree status, exact game hash, actual independent agent sessions and jobs. Five earlier Pathfinding query files were byte-verified and committed under `f11bbb3`, and type-1 physics ownership findings under `fe63ab2`; do not redo them. Two historical untracked raw-x64 probe files remain preserved in main. When Codex remains quota-limited, report zero available independent workers honestly.
2. **M1 accepted:** V7 now produces standalone write-once manifests that pin recorder and existing scanner versions, input/helper/transitive-local SHA, full commands, parser warnings and bounded coverage. All 21 integrated regression tests passed. Do not re-run already accepted M1 work merely to keep agents busy.
3. **M3 priority:** The saved M3-001 continuation is validated and integrated (commit fe63ab2) without proving type-7 use. Next identify what assigns a nonnull queue to Havok simulation +0x160, then find a **same-queue** handler writer at queue+0x210 and a genuine producer with **job type 7**. Do not confuse virtual method slot 18 with job type 7, infer ownership from offset alone, or implement a replacement pathfinder without evidence.
4. **M4A preparatory demo:** Locked synthetic contract/13 fixtures and G0 completed in commits `899a158`/`4de0666`. A genuine Codex thread attempted M4A-003 on October 19 and stopped with a usage-limit error (exit 1) before writing code. Remaining G1/G2 worker tasks are explicitly **blocked**, not running; retry only after a fresh quota/capacity check on or after Oct 24, 2026 at 7:13 PM (as the CLI reported). After real workers deliver validated code, continue G3→G5. **Full M4** still waits for native interface evidence.
5. **M5 approval gate:** T0/T1/T2 remain blocked without separate approval and demonstrated real cancellation. No game input was sent this pass. AI worker usage was exhausted; do not respawn agents while unavailable.

**Checkpoint:** milestone → task ID / exclusive owner → new evidence → test and exit result → integrated commit or blocker → next unblocked task. The Manager changes task ordering only by documenting the reason and updating dependencies first.
