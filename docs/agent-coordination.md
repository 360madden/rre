# RRE six-worker navigation investigation

**Historical first-wave manager:** browser ChatGPT conversation; six Codex CLI research workers had separate Git worktrees and branches. **For new waves (operator directive refreshed November 3):** attempt to launch genuine reasoning agents on independent narrow research/review tasks using a supported provider, including isolated local read-only CLI workers where viable. Preserve **one manager** (the active RRE integration owner); never start a second concurrent manager, duplicate file writers or nested uncontrolled agent trees. The manager alone owns `main` integration, shared registers and commits. Every worker requires an actual model/command receipt, bounded task, source/build qualification and nonconflicting path ownership. **Base branch:** `main`. Workbridge `0.16.4-dev` most recently reported **36 command slots**, but those are *not* reasoning-agent slots and must be rechecked per run. Prefer parallel genuinely independent tasks, not quota-burning volume. One-session orchestration; no unattended/background continuation is promised.

## Roadmap governance (current work)

The earlier six-worker research wave is integrated into main. This file preserves its lane ownership and handoffs; it does **not** assert those six Codex processes are still running. The Manager must use `../ROADMAP.md` for milestone order/gates and `roadmap-tasks.json` as the per-task status/owner registry. Read both before assigning work. Only the Manager may change these shared files or integrate to main. A fresh Git/worktree/job preflight is required before reusing an agent slot; preserve uncommitted changes and do not start duplicate lane writers. **No Workbridge command-job capacity value establishes an AI-agent count.**

## Baseline
Commit before worker branches: see main Git history after this document is committed. Matching `rift_x64.exe` SHA-256 is `7c356c9dde9e12fcbff3c08d953b0630b48b1510a0ffb36e4ec164606e7b17bd`. Prior evidence lives under `C:\work\rre\artifacts\navigation-20261018-01`; original RiftReader code is at `C:\rift modding\RiftReader` and must remain read-only.

## Exclusive lanes

| Lane | Worktree | Branch | Owned deliverables | Question |
| --- | --- | --- | --- | --- |
| pathfinding | `C:\work\rre-worker-pathfinding` | `research/nav-pathfinding` | `docs/agents/pathfinding.md`, `docs/agents/pathfinding.json` | Trace type-7 `TtPathfinding` dispatch at RVA 0xF3FA4 / table queue+0x210: registration, handlers, producers; determine what is evidence versus open. |
| c2m | `C:\work\rre-worker-c2m` | `research/nav-c2m` | `docs/agents/c2m.md`, `docs/agents/c2m.json` | Trace `Misc_EnableClickToMove` setting, current known UI read, candidate gameplay destination-input path, without live clicks. |
| follow | `C:\work\rre-worker-follow` | `research/nav-follow` | `docs/agents/follow.md`, `docs/agents/follow.json` | Trace follow-state clearing at RVA 0x534200 and direct callers; distinguish confirmed field changes and actual cancellation. |
| collision | `C:\work\rre-worker-collision` | `research/nav-collision` | `docs/agents/collision.md`, `docs/agents/collision.json` | Investigate Havok RTTI, ray/shape cast query and relationship of type-3 raycast work to obstacle detection. |
| ghidra | `C:\work\rre-worker-ghidra` | `research/nav-ghidra` | `docs/agents/ghidra.md`, `docs/agents/ghidra.json` | Diagnose REA 6.5.0/Ghidra 12.1.2 two import timeouts from saved logs and installed source; avoid further full imports. |
| validation | `C:\work\rre-worker-validation` | `research/nav-validation` | `docs/agents/validation.md`, `docs/agents/validation.json`, optionally tests under `tools/agents/validation/` | Independently audit static-analysis tools, evidence provenance, coverage and reproducibility; add narrowly scoped synthetic regression tests when useful. |

Worker outputs are disjoint, so manager cherry-picks do not need cross-lane content merges. Every worker owns only their named files. No shared main-branch edits by workers. All outside source/binaries are read-only.

## Reuse-first decision gates

1. Establish native functionality from a verified handler/behavior, not a class name/string.
2. If a native click/follow command already navigates, prefer wrapping/observing it.
3. If route, ground, or collision query is available, prefer reusing it to writing geometry/pathfinding.
4. Record negative and inconclusive evidence; do not interpret a timed-out REA import as a lack of native capability.
5. A new pathfinder requires a future explicit decision backed by evidence.

## Manager review and release checks

- Worktree and branch identity, isolated changed-path list, expected commit parent, no changes outside lane.
- Run status/diff/tests for each commit before cherry-picking to main.
- Verify sources and exact SHA-256, caveats, and no false pathfinding claims.
- Run syntax/JSON validation, ensure no original RiftReader or game files changed, check no live input issued.
- Integrate workers sequentially into main using cherry-pick and check clean worktree; summarize accepted and rejected worker findings and follow-ups.
- No push to remote without explicit request.
