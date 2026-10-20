# M4A final acceptance — deterministic offline target-approach replay

**Decision:** **ACCEPTED — M4A preparatory offline prototype only**  
**Date:** October 19, 2026, America/New_York  
**Authoritative repository:** `C:\work\rre`  
**Scope:** No live Rift, no player control, no native route API, no valid in-game navigation claim.

## Achievable deliverable accepted

The Manager integrated one runnable, deterministic command-line prototype: `tools/offline-target-approach.py`. It consumes the locked `docs/m4a-offline-target-contract.json` and `docs/m4a-offline-target-fixtures.json`, classifies a time-ordered synthetic player/selected-target trajectory, and emits an ordered JSON trace of *decision intents*, terminal states and failure reasons. It never issues real movement.

The locked fixture set contains **13 scenarios / 24 samples**, including arrival, approaching, moving away, no progress, stale telemetry, target/scene changes, manual cancellation, unsafe vertical separation, missing target, invalid numeric coordinate, nonmonotonic time and terminal-state latching.

**One-command reproduction (read-only console output):**

```powershell
cd C:\work\rre
.\.venv\Scripts\python.exe -B tools\offline-target-approach.py
```

Command exit **0** means all 13 scenarios match their expected states. This command writes no output file. Optional exclusive output is permitted only as a **new** JSON filename under `C:\work\rre\artifacts\` and cannot overwrite a prior capture.

## Independent QA and final verification

| Verification | Actual evidence | Outcome |
| --- | --- | --- |
| Independent-authored golden replay QA | `rre-m4a-resume-g4-independent-golden-tests-20261019-01` | 14/14, exit 0 |
| Integrated Validation suite (golden + fixture + original RRE) | `rre-m4a-resume-g4-validation-all-tests-20261019-01` | 71/71, exit 0 |
| C2M geometry | `rre-m4a-resume-g4-c2m-geometry-tests-20261019-01` | 30/30, exit 0 |
| Follow/cancellation safety | `rre-m4a-resume-g4-follow-safety-tests-20261019-01` | 73/73, exit 0 |
| Collision-lane observed progress | `rre-m4a-resume-g4-collision-progress-tests-20261019-01` | 32/32, exit 0 |
| **Distinct test total** | 71 + 30 + 73 + 32 | **206 passed, zero failures** |
| Locked synthetic fixture validation | `rre-m4a-resume-g5-locked-fixtures-validate-20261019-01` | 13 cases / 24 samples, exit 0 |
| Manager's roadmap consistency | `rre-m4a-resume-g5-roadmap-validate-20261019-01` | 9 milestones / 24 tasks before final board checkpoint, exit 0 |
| Historical integrated evidence provenance | `rre-m4a-resume-g5-integrity-validate-20261019-01` | Passed, exit 0 |
| Exact native research executable identity | `rre-m4a-resume-g5-native-binary-hash-20261019-01` | Pinned SHA256 match, exit 0 |
| Final fresh offline replay | `rre-m4a-resume-g5-final-replay-20261019-01` | 13/13 matching, exit 0 |

**Output byte-for-byte repeatability:**

- Initial replay file: `artifacts/m4a-replay-integration-20261019-01.json`.
- Independently repeated file: `artifacts/m4a-replay-integration-20261019-02.json`.
- Fresh final acceptance run: `artifacts/m4a-g5-acceptance-20261019-01.json`.
- All three: **12,248 bytes**, SHA256 `289c1f5bdace882c0b4665ed4b6b61ec86aad459bfff12849e66fbf6d4cddda7`.
- All 13 case outcomes matched their locked golden sequences.

**Input/output and implementation checks:**

| Artifact | Exact raw SHA256 on accepted checkout |
| --- | --- |
| `tools/offline-target-approach.py` | `5b940d5bdca4b80b8940cb357bb1d2f677e9397df96fc056ab3752fc3e7e6a12` |
| `tools/agents/validation/m4a_test_replay_integration.py` | `3d7a320e0c7e43d2b2e1888dbe114043088176bdeee011dfd635b316ea70882d` |
| `docs/m4a-offline-target-contract.json` | `491c1316f2f58607c22441e8bf5411905edb7bb723433ae7fc3e60ecaf1b6394` |
| `docs/m4a-offline-target-fixtures.json` | `5661a734d513e5a3eac6915d071ebc07d3a4b6fa78f59c9fc3277b08907dbd29` |
| Original Rift executable | `7c356c9dde9e12fcbff3c08d953b0630b48b1510a0ffb36e4ec164606e7b17bd` |

The replay records `mode=offline-replay-only`, `inputSource=synthetic-fixture`, `observedInGame=false`, `nativePathfindingVerified=false`, `gameInputSent=false` and `commandsIssued=0`. Independent QA tests refused live-source metadata, corrupt coordinates, output outside the artifacts directory, and attempts to overwrite existing output. Static AST checks found no listed game-control, process, memory or networking imports in the five runtime modules. AST-only inspection is *not* a general code-security proof, but supports the narrow nonactuating implementation audit.

## Manager/worker provenance

The parent ChatGPT session served as the **one Manager**, with four genuinely independent OpenCode coding-agent sessions in exclusive worktrees: C2M, Follow, Collision and Validation. Only the Manager reviewed, ran independent tests, committed lane files, and sequentially cherry-picked accepted work.

| Task | Worker commit | Main integrated commit |
| --- | --- | --- |
| M4A-003 C2M | `60e14c39d3c7c220481b6774d42f161bb3bab3dc` | `091a494567b7bbacdfd6061203b0c55ea5a1175e` |
| M4A-004 Follow | `0967b96158dd2e18fd0fb78480e92136aa0fc9b9` | `1b8addbb46c86e1e97070d67a3639e8414da7ab6` |
| M4A-005 Collision | `01a061833c17770b2abea5010192b2a4713e2a59` | `7adeeaf3673baf89786f67fdb397b94332d9f163` |
| M4A-002 fixture QA | `88925b89bcf5fe41d0f42fcfb662bd8a473035fc` | `ae8fbeeb773ff48d50d192ed68361869924b4756` |
| M4A-006 Manager CLI | Manager-owned | `c0ada6124cac73b7e44f7f2acd90a0be6d87002e` |
| M4A-007 independent QA | `dc315de28ad0e67a65b95c3811232a95de87e2fe` | `39b13568e94f8316e5dc85129ec2fb4d0a405493` |
| M4A-007 G4 manager checkpoint | Manager-owned | `8a3e874a0228137c2ec72ca15fc4c55e8e1c642b` |

A Codex worker failed at its external usage cap; preinstalled OpenCode bypassed that blocker without modifying account settings or installing software. The first OpenCode assignments had safe external-directory read denial, corrected by embedding required contract data within lane-specific prompts. Some agent outputs required human-style Manager review: one worker changed underscores to hyphenated status codes, another corrected flat sample schema and initial zero timestamp, and the original fixture-audit worker timed out before the Manager repaired its status vocabulary. The first two independent golden-QA agent attempts timed out; a third OpenRouter free-model agent authored 14 QA tests, revised them after review, and the Manager executed them independently on integrated main. Tool jobs and shell commands are not counted as additional AI agents.

All six specialist Git worktrees were clean at final pre-acceptance inspection. Main retained exactly two preexisting, **untracked** raw-x64 research probe files that were not modified or included in any commit.

## Explicit limitations and next critical path

**M4A accepted is NOT the overall navigation project's M4, M5 or M6 milestone.** In particular:

- The replay consumes **synthetic** trajectories and produces **non-actuating approach intents**, not real movement. Its synthetic thresholds and X/Z/Y distances are not gameplay-calibrated.
- There is **no verified populated Rift type-7 `TtPathfinding` job handler**, no qualified type-7 job producer, native route contract, player/target ownership link or reusable in-game pathfinder.
- The prior Havok simulation queue and vtable evidence qualifies a *type-1 physics* producer, not proof that player route finding is available.
- **Next ready roadmap task M3-001:** find the same-object/same-queue nonnull assignment to the simulation queue `+0x160` and typed handler entry at `queue+0x210`; verify a real type-7 job producer and route output before claiming native pathfinding.
- **Full M4** integration remains blocked pending useful native interface evidence; **M5 T0→T1→T2** requires separately approved supervised real movement and independently proven cancellation; **M6** in-game selected-target approach and **M7** optimization are not complete.
- No game process attach, memory modification, live game inputs, debugger or REA whole-client import, installed-tool updates, A*/custom navmesh, remote Git publishing, or unattended work was used in this acceptance pass.

This record establishes a reproducible and useful *offline research subsystem* and a safe basis for future qualified navigation work. The authoritative final task status and Manager acceptance commit are maintained in `ROADMAP.md` and `docs/roadmap-tasks.json`.
