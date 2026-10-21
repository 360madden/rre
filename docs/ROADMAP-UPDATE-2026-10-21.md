# RRE updated roadmap and resumption checkpoint — October 21, 2026

**Superseded priority order:** Joey subsequently directed a behavior-first navigation pivot. Use [the active pivot](NAVIGATION-PIVOT-2026-10-21.md) and the current task board. M3-001 is now deferred; NAV-001/NAV-002 replace it on the primary path. The state and priorities below are the earlier morning checkpoint, not current scheduling instructions.

This dated plan supplements `ROADMAP.md` and `docs/roadmap-tasks.json`; those files remain the canonical milestone/ownership definitions. Preserve accepted evidence and existing task IDs. This checkpoint is a **read-only research-state review**, not an approval for new game input, process attachment, native capture, external-repository modification or deployment.

## Objective and project split

Build a small, evidence-backed RIFT prototype that can approach one valid selected target, recognize no progress or obstruction, stop/cancel reliably and leave a reproducible trace. **Reuse RIFT's existing click-to-move, follow, movement, physics and pathfinding facilities first.** A custom pathfinder requires a later explicit, evidence-based decision.

- `C:\work\rre` owns reverse-engineering research, offline world inspection, source/evidence verification, and the future prototype research contracts.
- `C:\work\riftreader2` remains the separate Lua/.NET data-acquisition and *supervised bounded control* system. A functioning RR2 control pulse does not certify RRE native navigation or real-scene recognition.
- Distinguish gameplay **entity identity**, physical **shape/hit ownership**, **camera projection**, and actual **route/clearance**. Screenshots add visual observations, not automatic semantic truth.

## Verified preflight (October 21; point-in-time)

| Check | Observed result |
| --- | --- |
| RRE main | `main`, HEAD `c84a67b3162e326f5bbe3e172d9a5c7af190326a`; two historical untracked raw-probe files remain preserved |
| RR2 | `codex/modular-foundation`, HEAD `5b9e4a37378b5ba89b57654c8f91643925d8ba60`; clean worktree |
| Specialist worktrees | C2M, Follow, Collision, Ghidra and Validation clean; **Pathfinding has two new untracked `m3_001_*jobtype_stack_encoding.py` files** and cannot receive a duplicate writer until ownership/review is resolved |
| Workbridge | Active `0.16.2-dev`, tunnel ready, six **command-job** slots; one unrelated Workbridge job occupied one slot at preflight. This is **not** an AI-agent count. Paged job-ID enumeration is available in the current tool catalog; old WB-G01 wording needs revalidation, not a blind core change |
| Last full RRE gate | **435 tests passed October 20**, including 58 visual tests. This October 21 documentation checkpoint **did not rerun** the full suite |
| Current visual follow-up | VE-002 accepted as Manager inspection of saved original pixels, **not** independent model code/vision QA; old-wheel zoom result remains **INCONCLUSIVE** |

Do not discard/untrack/overwrite historical RRE main probe files or Pathfinding's new scripts. No live VM/game identity or current screenshot was reacquired for this review.

## Updated priority and dependencies

| Sequence | Track / task IDs | Current state | Next deliverable / acceptance gate |
| --- | --- | --- | --- |
| **R0** | M0, coordination | Refresh required each session | Inspect main, all six worktrees and active jobs; determine the Pathfinding scripts' owner/progress without invoking duplicate work. Verify exact game build hash before each native claim. Record genuine available AI sessions separately from Workbridge jobs |
| **R1** | M3-001 and M2 C2M/Follow, M3-002 | **Native pathfinding READY**, code/interface unqualified | Bounded exact-build proof or explicitly bounded disproof of the same-`hkpMultiThreadedSimulation` nonnull `+0x160` queue, same queue's populated type-7 `+0x210` handler, actual type-7 producer and player-facing route. In parallel trace the **candidate click-to-move destination setter RVA 0x562BC0**, actual player/target ownership, coordinate frame, consumer and reliable cancel paths. No literal `7`, RTTI name, physics job or static RVA alone proves a playable route |
| **R2** | WA-005A/B/C, WA-005 | **Blocked on independent QA** | Obtain genuine independent full final-source review of inspector 1.1.1 with pinned complete packets and no unauthorized tool activity. Reproduce or reject findings, add failing-then-passing regressions for real defects, and obtain final delta review. Do not rerun the already failed provider/launcher configurations unchanged; local 66 inspector tests/435 suite are not independent review |
| **R3** | WA-007 and WA-006 | **Real-scene qualification blocked** | Reuse saved collision-key/lookup evidence, trace `0xFFFF` keyed-record producer offline without retrying the specifically blocked capture. Define future evidence acceptance for at least two simultaneous non-self entity IDs, bound physical hit/owner, same scene/coordinate frame, camera-only landmarks and scene/restart invalidation. No claim from the historical player-only receipt or synthetic inspector demo |
| **R4** | VE-001/VE-002, future visual follow-up | **Offline visual tooling accepted** | Reuse existing `tools/visual-evidence.py` `pin/run/verify/replay`, existing RR2 capture backend and unchanged source images. When new captures are separately authorized, use a tightly bound **immediate before -> immediate after -> settled** frame sequence, stationary landmark regions, game/VM/window/scene/action identity, and independent XYZ/heading checks where available. Explicitly inconclusive when image quality or timing is insufficient; no screenshot-only pathfinding/ownership claim |
| **R5** | M4A -> M4 | **M4A ACCEPTED; M4 BLOCKED** | Reuse the 13/13 deterministic M4A state-machine fixtures. Build a narrow offline adapter only after at least one genuinely qualified player/target/cancel/movement interface exists. The path may be native C2M, follow or native pathfinding; do **not** treat the Havok type-7 investigation as the only possible solution. Preserve stale source, target changed, invalid height, stuck, stop, telemetry gaps and no-actuation tests |
| **R6** | M5-T0 -> T1 -> T2 | **BLOCKED; separate live approval required** | T0 independently observed movement-and-stop, then T1 clear-ground one-destination trial, then T2 single obstacle-with-opening trial. Each requires exact current build/session, one VM-input owner, verified cancellation, timestamped imagery, telemetry and reproducible result; a synthetic pass never unlocks these automatically |
| **R7** | M6, then M7 | **BLOCKED / DEFERRED** | Demonstrate one repeatable actual selected-target approach or defensible failed attempt with stop and artifact replay. Only then measure bottlenecks and harden restarts, different scenes or updates |

### Critical-path decision

**Avoid an indefinite Havok type-7 rabbit hole.** Pursue type-7 producer/handler proof and player-facing C2M/follow interface proof as **parallel candidate native-reuse routes**. If one route is actually qualified, the Manager may propose a specific M4 dependency update backed by evidence and tests. Until then M4, M5 and M6 remain blocked. An inconclusive scan is neither a callable pathfinding API nor proof that no native pathfinder exists.

The next useful standalone milestone is an **M3 evidence/decision packet**: exact pinned native bytes and data flow, newly checked Pathfinding scripts with ownership resolved, reproducible tests, a clear candidate/qualified/rejected disposition, and a small exact next search if unresolved. The manager integrates only reviewed lane-owned changes; the historical two raw-probe files are out of scope.

## Worker deployment and conflict isolation

Prefer **one dedicated Manager + up to five genuinely available specialist AI workers**, never six workers plus a competing manager. The verified Workbridge six-command limit does not allocate six AI model sessions. If independent agent capacity is unavailable, perform read-only lanes sequentially and leave blocked review tasks blocked.

| Ownership | Narrow lane / allowed work |
| --- | --- |
| Manager | Owns `main`, this roadmap, board, cross-source contract, code integration, validation and resumption. No competing manager |
| Pathfinding worktree | M3-001 only; first reconcile its two existing untracked scripts, then exact-build same-queue/jobtype proof. Do not start a second writer |
| C2M worktree | Bound gameplay entity/target and destination setter/consumer static contract; WA-005A independent review only when lane is available |
| Follow worktree | Cancellation and follow-state semantics; WA-005B independent review only with exclusive slot |
| Collision worktree | Shape, hit, player clearance and keyed-record ownership offline; do not bypass blocked WA-007 capture |
| Validation worktree | Independent reproducible QA, code-review acceptance checks, fixture provenance and image/telemetry disagreement cases |
| Ghidra worktree | **Queued/rotating sixth specialist lane** for bounded REA/Ghidra questions only. No repeated unchanged whole-program import |

All workers own distinct files and worktrees, return actual process/model/session identity, evidence, exit codes, tested changes and commit hash. Manager only integrates. Stop on timeout/unknown/permission block and inspect saved outcomes before retry. Preserve unknown model/reasoning fields as blank; current response model family is GPT-6, reasoning level not independently available.

## Screenshot and live-evidence checklist

For a future separately approved input trial, record **(1) identity-bound scene and input binding, (2) immediate pre-action frame, (3) action delivery/key release/stop, (4) immediate after and settled frames, (5) independently acquired player/target XYZ or heading where available, (6) image matcher diagnostic and direct reviewer pixels, (7) contradiction/uncertainty and output hashes**. A filename in a packet does not prove images were delivered to a reviewer. The earlier keybinding summary was not reliable in light of Joey's correction. Verify the actual active lab's bindings from bound evidence; do not assume Q/E or A/D semantics or silently swap turning and strafing.

## Resume sequence

1. Verify `git status`/HEAD in RRE and RR2, all six worktrees, Workbridge diagnostics and known job IDs. Preserve existing changes. Confirm the two Pathfinding scripts' active owner before touching them.
2. Read `ROADMAP.md`, `docs/roadmap-tasks.json`, this checkpoint, `docs/old-wheel-image-review-2026-10-21.md`, and topic-specific evidence. Do not recreate VE-001/VE-002 or M4A.
3. Select first unblocked, non-conflicting narrow research task: M3-001 exact-build analysis if its lane is genuinely free; otherwise independent file-only M2/C2M/Follow or validation work. Independent WA-005 remains blocked until a viable reviewer is verified.
4. Verify source hashes; perform targeted checks and actual exit-code inspection. Before any accepted code/integration change run the appropriate unified gate, validate `docs/roadmap-tasks.json`, preserve source evidence and commit only intended files.
5. Record milestone ID, one accountable owner, evidence source/version, test/exit, integrated SHA or explicit blocker, next ready task, model identity if actually available and no invented reasoning level.

**Next stop condition:** M3 candidate-disposition packet accepted on main, or an exact documented blocker with surviving scripts and a smaller next test. Do not claim autonomous target navigation, object identity, native pathfinding or new live-game authority before the corresponding gates pass.
