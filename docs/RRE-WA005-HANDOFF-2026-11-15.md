# RRE WA-005 handoff — 2026-11-15 11:45 PM EST

## Where to resume

- **Machine:** AMD-DESKTOP only, independently verify Workbridge + `hostname.exe` again before any local action. Repo: `C:\work\rre` on `main`. Do not use VMware. Physical RIFT is not authorized for this offline QA resumption.
- **Starting point:** implementation/review commit `88b7fa84b28bfbcee509ab49a56f96715662c65d`; verify HEAD and task board, as a separate scoped task-status commit follows.
- **Read first:** `AGENTS.md`, `ROADMAP.md`, `docs/roadmap-tasks.json` (`inspectorQaCurrent` and WA-005A/B/C/WA-005), and the detailed [WA-005 independent QA report](RRE-WA005-INDEPENDENT-QA-2026-11-15.md).
- **Inspector:** `tools/world-inspector.py` v1.1.2, SHA-256 `fdbc066c2da4a929fc8219a839ba8c02d72aad741f8157c8584cac5933347eb6`. Test SHA `fce86d3672d4fe9f1bc0df17a64520ca2d3ebd801a2af301ff2b9a986cdff25e`. Contract SHA `1ecfdbc7d3d06140a7101db10e519b39a64d5ac170aa3d8f93c2ba24e1bd5aa4`.

## Validated and accepted

- WA-005A/B/C **independent static source/delta reviews completed** by separate no-tool ChatGPT subagents. Reviewer IDs and provenance in the report; external runtime session IDs were not exposed and are not asserted.
- Fixed Unicode `Cc` control characters in consumed strings (C0/DEL/C1); conservative dotted group/raid alias exclusion. Manager reproduced **9 Unicode** and **3 alias** failing subtests before fixes; **67/67 inspector tests pass** after.
- Final Node suite **358/358 passed**; `tools/validate-roadmap.mjs` passed **47 tasks / 11 milestones / 0 failures**, status after board edit 36 integrated, 9 blocked, 2 deferred.
- Fresh v1.1.2 synthetic report `artifacts/world-inspector-v112-20261116-demo-final/` verified. Prior untouched v1.1.1 synthetic and recorded publications also verified. All remain file-only/non-live.

## Actual blocker — do not bypass

- **WA-005 overall remains blocked.** Fresh full research suite job `rre_20261116_0552_wa_full_research_final_01` exited **1** (514 tests executed; collision/pathfinding groups fail; source hashes unchanged). Log at `artifacts/research-gate-wa005-20261116-0439/validation.json`.
- Cause: historical collision/pathfinding verifiers require original RIFT executable SHA `7c356c9dde9e12fcbff3c08d953b0630b48b1510a0ffb36e4ec164606e7b17bd`. The **currently installed physical AMD-DESKTOP PE** is 60,493,640 bytes, SHA `1935a05c9db6d468e34e0055014a4a99c1b5afceb1695884e24600f5c20a4be8` (read-only hash verified). A mismatched PE must not be passed to old-RVA disassembly; do not edit hash constants or tests merely to force green.
- No original PE archived path has yet been verified in this turn. Seek only explicit, read-only, bounded source discovery; if no exact old PE is available, preserve the blocker. Do not touch installed game files or replay blocked native capture.
- WA-006 still lacks real coherent non-self/player/physics/camera evidence; WA-007 capture is stopped. RC-88 collector and RC-30 Pin/Undo/Reload are stopped, SC-103/SC-306/NAV-002 blocked. No VM, input, reload, deployment, memory attach, or game restart was performed.

## Next three priorities

1. **P0 — exact old-PE source audit:** In bounded read-only candidate archives, locate and hash any preserved *original* 59,963,840-byte `rift_x64.exe` matching `7c356c9d…`. If absent, stop; do not transplant current-game RVAs into old tests.
2. **P1 — compatibility-safe fixture selection:** If a verified archive exists, propose an explicit offline fixture path/expected hash for legacy tests and obtain architecture review before implementation. The verification must remain exact-build fail-closed.
3. **P2 — world scene qualification planning:** Once WA-005 whole-suite prerequisite is resolved, design a separately authorized physical-scene sample for WA-006; keep RRECollector/VM/live game gates intact.

## Preservation

Nine inherited untracked RRE backup/probe paths were left untouched, including the seven `docs/rc*-backup-*` folders, `docs/rea-raw-probe-profile-2026-10-18.json` and `tools/agents/ghidra/prepare_raw_probe.py`. No push was made; remote branch already lagged local `main` before this session.
