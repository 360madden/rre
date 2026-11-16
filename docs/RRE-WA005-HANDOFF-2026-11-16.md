# RRE WA-005 acceptance handoff — 2026-11-16 after midnight EST

## Resume exactly here

- Independently verify **AMD-DESKTOP**, Workbridge host/version and `C:\work\rre` before any new local action. Physical RIFT is only a potential future target after task-specific approval. **No VMware operations**; no live process/input/reload/restart/deployment was part of this work.
- Read `AGENTS.md`, the top (newest) of `ROADMAP.md`, `docs/roadmap-tasks.json` (`inspectorQaCurrent`, WA-005A/B/C, WA-005, WA-006/007), [November 15 independent QA](RRE-WA005-INDEPENDENT-QA-2026-11-15.md), and [November 16 exact-original-PE acceptance](RRE-WA005-LEGACY-PE-ACCEPTANCE-2026-11-16.md).
- Code milestone local commit **`701cbc45500dc27cb2b43a44b1653c8cb58bdf35`**; prior documentation checkpoint **`f5dc35e5d5a3b82ec1ff56e478451edf00e9abe2`** and inspector QA code **`88b7fa84b28bfbcee509ab49a56f96715662c65d`**. Verify HEAD; a separate scoped documentation/status commit is expected after this handoff.
- No push. Keep **nine inherited untracked** backup/probe paths undisturbed; generated test artifacts remain ignored.

## Accepted outcome

- WA-005A/B/C independent no-tool static source/delta reviews accepted for world-inspector v1.1.2, source SHA **`fdbc066c2da4a929fc8219a839ba8c02d72aad741f8157c8584cac5933347eb6`**. Reviewer runtime session IDs unavailable, no fabricated event-trace attestation. Previous 67/67 inspector and 358/358 Node tests passed.
- P0 original RIFT PE found **read-only** in sibling RR2 artifact `C:\work\riftreader2\artifacts\power-locator-20261025-01\rift_x64.exe`, size **59,963,840**, SHA-256 **`7c356c9dde9e12fcbff3c08d953b0630b48b1510a0ffb36e4ec164606e7b17bd`**; archived file untouched.
- New `--legacy-pe` option preflights exact old build before any test, supplies `RRE_LEGACY_PE` exclusively to collision/pathfinding tests, and verifies unchanged file at end. Wrong build (60,493,640B SHA `1935a05c...`) and missing flag both reject with exit2 before creating output.
- Full nine-group research suite **550/550 PASSED, exit0** in job **`rre_20261116_0804_fullgate_original_01`**, receipt `artifacts/research-gate-original-pe-20261116-0502-v1/validation.json`, receipt SHA **`c19bb7c7f6698eb6a1c9a65a6feec2dd94ab13405dd8acb6f58757e1bd82b249`**. Group tests: validation171, C2M30, follow73, collision47, pathfinding57, navigation97, visual58, adapter17; roadmap validator passed. `sourcesUnchanged:true`, `duplicatePythonTestIds:0`, `legacyPeFixture.unchangedAtEnd:true`.
- Focused positive collision 9/9 and pathfinding 39/39; selector 6/6 including negative exact-build checks; independent source architecture audit found no blocking issue. **WA-005 offline acceptance can be integrated.**
- **Not completed:** real distinct non-self units + collision owner + camera orientation/projection, player clearance or path planning. WA-006 and WA-007 remain blocked; RC-88, RC-30 live controls, SC-103/306 and NAV-002 are not thereby cleared. Standalone legacy CLI verifiers still have installed-path defaults in some files; only the discovered research-gate tests have been migrated to explicit fixture selection.

## Exact safe repeat

PowerShell in `C:\work\rre`, with a **new output directory**:

```powershell
& 'C:\work\rre\.venv\Scripts\python.exe' -B tools/validate-research.py --legacy-pe 'C:\work\riftreader2\artifacts\power-locator-20261025-01\rift_x64.exe' --output-dir 'artifacts\research-gate-next'
```

Do not weaken SHA/RVA checks or substitute the installed executable.

## Prioritized bounded follow-ups

1. **P0 — WA-006 evidence protocol:** Identify exact producer for fresh player and distinct other-ID, actual hit owner, calibrated camera matrix, capture age/session/scene, and missing/unknown semantics. Read-only design first; request task-specific approval before any physical-RIFT action.
2. **P1 — native standalone-tool hygiene:** Inventory independent historical verifier CLIs that still default to the installed game and propose explicit SHA-pinned archive arguments. Scope only helpers whose operational use justifies it. Preserve old manifests.
3. **P2 — artifact durability:** Keep explicit archive locator + SHA and repeat command in task board/handoff, periodically test the fail-closed selector. Do not duplicate or replace binary implicitly.
