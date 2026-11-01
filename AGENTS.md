# RRE agent coordination (2026-10-18)

**Current REA spellcasting location — user decision October 27:** Work on the RIFT installation **local to the physical PC** at `C:\Program Files (x86)\Glyph\Games\RIFT\Live\rift_x64.exe` (SHA `1935a05c9db6d468e34e0055014a4a99c1b5afceb1695884e24600f5c20a4be8`), not VMware Lab-1 or Lab-2. Read [physical-PC target policy](docs/REA-RIFT-LOCAL-PC-TARGET-2026-10-27.md). Historical VM patch holds below govern older navigation/guest work and do NOT require VM access for this REA track. Keep RR2/Workbridge repositories separate and commit one narrow useful finding per Chat-mode step.

**Active REA spellcasting research — October 27:** This ChatGPT project uses REA for RIFT native/gameplay-mechanism research; **RiftReader2 and Workbridge are separate development workflows**. For the current spellcasting task, read the [five-pass REA casting roadmap](docs/REA-RIFT-SPELLCASTING-ROADMAP-2026-10-27.md), [independent task register](docs/REA-RIFT-SPELLCASTING-TASKS-2026-10-27.json), [short resume handoff](docs/REA-RIFT-SPELLCASTING-HANDOFF-2026-10-27.md), and [proved custom-addon playbook](docs/REA-RIFT-SPELLCASTING-SC605-CUSTOM-ADDON-PLAYBOOK-2026-11-01.md). This **SC task register** governs casting scope; the NAV-only board below still governs historical navigation tasks. Prefer one bounded Chat-mode task and a local commit per verified research milestone; do not start unrelated RR2/Workbridge development or long provider imports.

**Patch hold (October 22):** Read `docs/RIFT-UPDATE-IMPACT-2026-10-22.md` before future native or NAV-002/M5 work. A new RIFT client update was reported; the physical-host executable has the old SHA, but the VM guest executable is not yet requalified and the RR2 status endpoint was unreachable. Do not copy old-build RVAs/offsets/absolute pointers into the current guest, change expected hashes, restart receivers or issue game inputs on this evidence. First establish the actual guest build and use the current RR2 control owner for status recovery.

This repository researches Rift native navigation and reverse engineering. Current research is offline and **reuse-first**: identify the game's existing pathfinding, movement, click-to-move, follow, and collision implementations before proposing a replacement planner. A string, class name, or RVA is a research lead, not a verified runnable interface.

## Mandatory milestone roadmap

- Read `ROADMAP.md` and `docs/roadmap-tasks.json` before starting a task; follow milestone dependencies and exit gates. This is mandatory, not an optional planning document.
- Active navigation is **NAV-002/P0–P4** under `docs/NAVIGATION-WORKFLOW-OPTIMIZATION-2026-10-22.md`. Do not build another generic NAV evidence tool when the missing evidence is a fresh visually verified playable scene, an actual bound ground click, advancing player samples or real cancellation. NAV-001 and NAV-003..006 are accepted offline; type-7 M3 is deferred. Park a lead after two distinct probes without decision-changing evidence; never bypass blocked routes or guess controls.
- Every task must have a board ID, exclusive lane and owned paths, evidence requirements, and completion test. Only the single designated manager updates the roadmap/board, allocates work, integrates, or records deviations. Run `node tools/validate-roadmap.mjs` after every task-board change and before integrating roadmap changes.
- Before resuming work, reconcile actual command jobs, branch/worktree statuses and uncommitted files. Do not assume an old Codex worker has stopped or create a second writer in its lane.
- Workbridge's six concurrent command-job slots are not evidence of six independent AI agents. Verify real worker support and capacity, and queue tasks that cannot be assigned without conflicts.
- The initial roadmap preserves pre-existing dirty hardening/raw-probe changes in main and untracked pathfinding query files; do not overwrite, reset or clean them without explicit ownership review.

## Authority and scope

- Follow this file, the assigned lane in `docs/agent-coordination.md`, and any applicable source-repository AGENTS.md.
- No RRE-owned live Rift input (mouse, keyboard, movement, commands), memory modification, debugger attach, injection, process control, privileged operation, network publishing, executable/game-settings edits, or changes to REA, Ghidra, RiftReader, RiftReader2, Workbridge or unrelated addons. **Narrow user-approved exception (November 1, SC-417/418):** the manager may create and update standalone RRE-owned read-only research addons under `addons/RRECollector/` and additively deploy that package to the physical-PC RIFT `Interface/AddOns/RRECollector` directory with source/install hashes. No other game files are included. Game-side commands remain operator-performed unless separately authorized.
- Do not launch another coding agent, subagent, or a nested swarm. The manager owns delegation.
- Read-only research on the matching native Rift executable and the prior RiftReader evidence is allowed. All claims must state exact build identity, sources, method, and uncertainty.
- No full-program REA/Ghidra import retry without the manager's explicit direction. Two recorded attempts exceeded 450 seconds; repeated unchanged attempts add no value.
- Avoid long-running work and resource contention. Do not install dependencies or change shared environments; use the preexisting RRE virtual environment read-only if needed.
- Tooling efficiency: first demonstrate that an existing Workbridge, RR2 or installed imaging capability actually fails before writing a replacement. Use hash-bound original saved images and visual inspection when behavior depends on screen state; a saved capture from a disconnected/loading screen cannot prove a playable scene. For code edits run focused tests first and the full gate **once per coherent source integration**; for documentation/board edits run the roadmap validator, link/diff checks and no redundant 500+ test rerun. Keep one short current handoff and exact observed job exits.

## Proven custom-addon research route (SC-605; user decision November 1)

- **Use the successful 69/69 ability capture as a learning example**, not just an isolated implementation: [SC-605 decision/playbook](docs/REA-RIFT-SPELLCASTING-SC605-CUSTOM-ADDON-PLAYBOOK-2026-11-01.md), [SC-417 source](addons/RRECollector/) and [SC-418 source-hashed result](docs/REA-RIFT-SPELLCASTING-SC418-FIRST-CAPTURE-2026-11-01.md).
- When a missing runtime observation is exposed by a documented RIFT Lua API, **prefer a small addition to RRECollector early**. Reuse known addon patterns, capture the specific character/role/build and flags in one manual snapshot, verify the SavedVariables output, and commit. Do not keep coordinating multiple partial addons or repeat broad native searches for data the API already provides.
- Keep tooling **scaffolding-sized**: complete TOC metadata (including `Email`), bounded List/Detail with explicit unknowns, one focused offline check, one user-driven in-game capture and source-hash receipts. Missing API capability remains a native/UI research question; an addon cannot prove unlearned spells or native cast/queue internals absent an exposed interface.
- Do not modify another repo or existing addon as part of this route. Manager owns RRE addon source, deployment decisions, roadmap and handoff; separate game-input ownership remains in force.

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
- For visual game-behavior claims, retain screenshot evidence tied to the exact VM/game/action and use `docs/visual-evidence.md`. Reuse the existing RR2 capture path; the RRE consumer is offline. Keep command delivery, visual diagnostics, telemetry and gameplay conclusions separate. Preserve original images; ambiguous or unbound evidence is inconclusive. A text-only source review is not visual validation, and a generated image review packet is not proof of image delivery to a reviewer. Screenshot integration grants no new live-input authority.

## Completion

Write a concise technical report and machine-readable summary in your lane only, self-review the changes, run targeted validation, commit only your lane files, and return your commit SHA and verifiable evidence paths. Stop when the allotted noninteractive job budget is exhausted; do not leave untracked persistent jobs.
