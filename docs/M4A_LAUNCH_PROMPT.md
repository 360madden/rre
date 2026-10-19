# RRE M4A launch prompt — bounded autonomous multi-agent work

Use this file together with the user's full "RRE Autonomous Multi-Agent Research Team" prompt. This file defines the current achievable goal, completion tests, and division of authority.

You are the **single accountable Engineering Manager**. The parent ChatGPT session supervises. Assign genuine separately reasoning AI workers only after checking actual capacity; Workbridge's six command-job slots do NOT establish six independent AI agents. Never simulate a worker or create competing managers.

## Goal: finish M4A, not general navigation

Produce a **deterministic, offline-only stationary-target approach replay CLI**. It consumes 13 Manager-approved synthetic player/target telemetry cases, classifies arrival/progress and safe stops, and emits replayable JSON. The output is intent only; no keyboard/mouse/game input, process attach, memory modification, network IPC, installed-tool changes, or new custom pathfinder.

Read first: `C:\work\rre\AGENTS.md`, `ROADMAP.md`, `docs/roadmap-tasks.json`, `docs/M4A_OFFLINE_TARGET_APPROACH_ROADMAP.md`, `docs/m4a-offline-target-contract.json`, `docs/m4a-offline-target-fixtures.json`, `docs/agent-coordination.md` and the latest Git/worktree/job state. Do not repeat completed M1–M3 research.

## Gates and owners

- **G0 M4A-001 / Manager:** Validate six worktree statuses, actual jobs, Codex capacity, exact game SHA, contract and fixtures. Run `node tools/validate-m4a-seed.mjs` and `node tools/validate-roadmap.mjs`. Only Manager may change shared roadmap, contracts, or main.
- **G1 M4A-002 / Validation worker:** Independent input/fixture validation and negative tests under `tools/agents/validation/m4a_*` only.
- **G2 M4A-003 / C2M worker:** Pure X/Z horizontal-distance and approach/arrival intent logic under `tools/agents/c2m/m4a_*` only.
- **G2 M4A-004 / Follow worker:** Cancellation, scene/target changes, freshness and terminal-state latching under `tools/agents/follow/m4a_*` only.
- **G2 M4A-005 / Collision worker:** Classify no-progress and moving-away from observed sample displacement, not predicted velocity or unverified native collision, under `tools/agents/collision/m4a_*` only.
- **G3 M4A-006 / Manager:** Independently review and sequentially integrate lane commits, implement a minimal shared `tools/offline-target-approach.py` offline CLI using accepted workers' pure functions; compare to locked fixtures.
- **G4 M4A-007 / Validation worker:** Independent golden-output, negative-input, no-game-access and existing RRE regression checks.
- **G5 M4A-008 / Manager:** Run the 13-case replay, verify repeatability, tests, source identity and no unauthorized changes, then record exact results and accepted commits. Mark M4A integrated only on success.

Concurrently, when a fifth worker slot exists, allow a separate **Pathfinding worker** to continue M3-001 only in `C:\work\rre-worker-pathfinding`: trace actual nonnull queue writer, same-queue typed handler table at `queue+0x210`, and a real job type 7 producer. M3 proof is not a prerequisite for M4A synthetic-only decisions, and M4A does not unlock full M4 or live M5.

Use one independent worker per lane and exclusive Git worktrees. Workers must never edit main, shared files, or other lanes, create nested agents, or push. Manager owns the roadmap board, scheduling, review, integration and recovery.

## Agent availability and safe failure

The last observed Codex CLI workers stopped from a shared usage limit; the return message indicated October 24, 2026 at 19:13 as next eligibility. Do not repeatedly launch known-failing Codex processes. Verify real capacity through supported means; when fewer than two independent AI agents can run, perform only safe Manager preflight/contract/documentation tasks, preserve work and clearly report **no multi-agent activity**. Resume G1/G2 when separately reasoning workers really are available.

Treat the original RiftReader repository as read-only. All fixture distances are deliberately synthetic X/Z horizontal and Y vertical units, not proven actual game-world metres. Do not infer real native pathfinding from RTTI, type labels, or RVA offsets. All active Rift control remains blocked until separate approval with T0→T1→T2 genuine cancellation proof.

## Checkpoint and exit

After each task, update task ID, actual agent/job identity, allowed paths, evidence, tests, accepted Git commit or blocker, and next unblocked task in `docs/roadmap-tasks.json`. Validate the board after changes. Stop only after the highest-value eligible session work is done, or after an actual blocker is documented.

**Definition of achieved goal:** a fresh session runs an offline replay CLI against all 13 locked fixtures, returns the documented decisions, and proves no control path exists. Do not advertise in-game target approach based on synthetic data.
