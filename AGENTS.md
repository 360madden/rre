# RRE agent coordination (2026-10-18)

This repository researches Rift native navigation and reverse engineering. Current research is offline and **reuse-first**: identify the game's existing pathfinding, movement, click-to-move, follow, and collision implementations before proposing a replacement planner. A string, class name, or RVA is a research lead, not a verified runnable interface.

## Mandatory milestone roadmap

- Read `ROADMAP.md` and `docs/roadmap-tasks.json` before starting a task; follow milestone dependencies and exit gates. This is mandatory, not an optional planning document.
- Every task must have a board ID, exclusive lane and owned paths, evidence requirements, and completion test. Only the single designated manager updates the roadmap/board, allocates work, integrates, or records deviations. Run `node tools/validate-roadmap.mjs` after every task-board change and before integrating roadmap changes.
- Before resuming work, reconcile actual command jobs, branch/worktree statuses and uncommitted files. Do not assume an old Codex worker has stopped or create a second writer in its lane.
- Workbridge's six concurrent command-job slots are not evidence of six independent AI agents. Verify real worker support and capacity, and queue tasks that cannot be assigned without conflicts.
- The initial roadmap preserves pre-existing dirty hardening/raw-probe changes in main and untracked pathfinding query files; do not overwrite, reset or clean them without explicit ownership review.

## Authority and scope

- Follow this file, the assigned lane in `docs/agent-coordination.md`, and any applicable source-repository AGENTS.md.
- No live Rift input (mouse, keyboard, movement, commands), memory modification, debugger attach, injection, process control, privileged operation, network publishing, or changes to installed game, REA, Ghidra, RiftReader, RiftReader2, Workbridge, or user settings. The existing RiftReader instructions require independent approval for live inputs; this assignment does not grant it.
- Do not launch another coding agent, subagent, or a nested swarm. The manager owns delegation.
- Read-only research on the matching native Rift executable and the prior RiftReader evidence is allowed. All claims must state exact build identity, sources, method, and uncertainty.
- No full-program REA/Ghidra import retry without the manager's explicit direction. Two recorded attempts exceeded 450 seconds; repeated unchanged attempts add no value.
- Avoid long-running work and resource contention. Do not install dependencies or change shared environments; use the preexisting RRE virtual environment read-only if needed.

## File ownership / isolation

Each worker runs in a **separate Git worktree and branch**. Treat your worktree as the only writable source tree. Only create/edit your lane's files: `docs/agents/<lane>.md`, `docs/agents/<lane>.json`, and optional `tools/agents/<lane>/...` tests/helper. Do not change `README.md`, this AGENTS file, tracked shared research, other workers' files, or generated artifacts in the main worktree. Worktrees are not shared writable directories.

Manager owns `main`, integration, cross-lane edits, cherry-picks, and final verification. Workers must not merge, rebase, cherry-pick, or push. A worker may make a local commit containing **only their owned files** after validation; report commit hash, changed files, tests, unresolved questions. If committing is blocked, leave owned changes and report it without altering Git identity.

## Evidence requirements

- Distinguish **directly observed native code**, **existing documented runtime evidence**, **hypothesis/inference**, and **unresolved**.
- Include RVAs relative to the matching executable (preferred static base 0x140000000); check hash `7c356c9dde9e12fcbff3c08d953b0630b48b1510a0ffb36e4ec164606e7b17bd`.
- Reuse `tools/inspect-navigation-static.py`, `tools/inspect-navigation-names.py`, and original RiftReader scripts instead of rebuilding the decoder; use bounded, targeted research.
- Read `docs/navigation-research-2026-10-18.md`, `docs/navigation-findings.json`, and `docs/navigation-workflow.md` as baseline.
- Never equate the historical custom proximity graph with a native Rift navmesh, the rejected player-centered volume with a fixed goal, or cached +0xD8 with a verified navigation destination.
- Report concrete next validation, failures, and what cannot yet be concluded. Do not claim an in-game navigation success without a recorded game-world test.

## Completion

Write a concise technical report and machine-readable summary in your lane only, self-review the changes, run targeted validation, commit only your lane files, and return your commit SHA and verifiable evidence paths. Stop when the allotted noninteractive job budget is exhausted; do not leave untracked persistent jobs.
