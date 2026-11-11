# RRE RC-55 — new-build NAV dispatch evidence and v0.4.19 readiness (LEGION, 2026-11-11 ~07:16 EST)

> **New accepted offline result:** The current LEGION physical RIFT executable's type-7 `TtPathfinding` label and type-indexed dispatch pattern were requalified on SHA `1935a05c9db6d468e34e0055014a4a99c1b5afceb1695884e24600f5c20a4be8`. This is **static code behavior only**; navigation handler registration and live movement are still unverified. The current SHA was already documented October 27; new in RC-55 is the selected navigation requalification.

## Fresh RC-55 evidence and changes

- Independently verified machine via LEGION Workbridge `hostname.exe`. Only LEGION connector/physical RIFT path; no AMD-DESKTOP, VM lab, game input, UI reload, debugger, native memory write, live deployment, dependency installation or Git push.
- Physical `rift_x64.exe` PID 22648 path matches the current installed executable, 60,493,640 bytes. In-memory binary identity, current playable scene and addon load remain **unverified**.
- **Native breakthrough:** original-PE pathfinding/raycast strings at `0x2DCCF38`/`0x2DCCF00`; corresponding instruction-aligned RIP references at `0x102719`/`0x1027B3`. Exact build dispatch type7 uses `dispatcher+0x130+7*0x20 = +0x210` then indirect subtype handler call at `0x102833`. Click-to-move setting literal `0x26EC228`, root-pointer RVA `0x33958C0`, setting byte `+0x146` compared/written at `0xBD113D/0xBD114A`. Old-build source RVAs and static pointers are not portable. Full source-bound evidence: `docs/RRE-NAV-NEW-BUILD-LEGION-2026-11-11.md` and `.json`, job IDs included there.
- Independent manager original-PE byte check `rre-rc55-native-byte-independent-confirm-20261111` **exit0**, hash rechecked, **7/7 exact opcode bytes decoded correctly** in Capstone. No generic/native import attempted.
- **RC-55 release preflight:** `tools/deploy-rrecollector-onedrive.ps1` now gates solely v0.4.19 and calls strict source package validator before both preflight/deploy. Read-only `pwsh.exe` preflight `rre-rc55-v0419-deploy-preflight-readonly-20261111` **exit0**: installed v0.4.18 / source v0.4.19 / 11 expected files / strict source passed / `PREFLIGHT_OK_NO_FILES_CHANGED`. Direct package validator `rre-rc55-v0419-strict-package-20261111` exit0 with 11 sources. **No deployment took place.**
- **RC-55 exporter fix:** `tools/export-rrecollector-navigation-api.mjs` now renders producer-permitted backticks as Markdown-escaped text rather than malformed code spans. Independent bug reproduction `rc55-agent-backtick-repro-11`; added regression in `tools/test-export-rrecollector-navigation-api.mjs`.
- Tests: focused RC-55 exporter **11/11** (`rre-rc55-export-backtick-tests-20261111`); combined four relevant Node suites **53/53** (`rre-rc55-node-four-suites-20261111`); `git diff --check` exit0 with Git's nonfatal LF/CRLF warnings. Existing .NET production 97/97 pass is a *prior RC-53 record*, not retested for RC-55.
- Read-only reviewers: native original-byte investigation (7 primary job receipts); independent collector/exporter source review; live-receipt availability audit. Sole manager made all repository writes.
- Starting HEAD `2f68afa82e52f5ba8b79823e1d9e4d3df486462b` on `main` (previous RC-54), originally clean and 10 ahead of origin. RC-55 changed files: `tools/deploy-rrecollector-onedrive.ps1`, `tools/export-rrecollector-navigation-api.mjs`, `tools/test-export-rrecollector-navigation-api.mjs`, `docs/RRE-NAV-NEW-BUILD-LEGION-2026-11-11.md`, `docs/RRE-NAV-NEW-BUILD-LEGION-2026-11-11.json`, this handoff. Inspect current Git HEAD/status after local RC-55 commit; no remote publication.
- Live API capture still blocked: last documented installed v0.4.18 has no v0.4.19 `navigationProbe`; Workbridge roots list only `C:\work`, so original Documents\RIFT SavedVariables cannot be read through root-scoped APIs. Do not invent API observations or circumvent root policy.

## Three prioritized next decisions

1. **P1 — Real API:** With separately confirmed release authority, use v0.4.19 scripted backup+hash deployment, **operator** /rre navigation and normal game save, then authorized original SavedVariables acquisition and strict Markdown export. Preflight success is not install/load proof.
2. **P2 — Native discovery:** From the newly requalified `+0x210` dispatch and `+0x146` C2M setting anchors, select the *smallest* handler registration/producer or current-build destination setter probe. Do not resume broad type-7 scans or full Ghidra import.
3. **P3 — Coverage quality:** Once an authentic navigation index exists, decide whether the 18-document ordering oversamples generic spatial APIs and starves NPC/other-target details; do not expand a synthetic-only atlas spec prematurely.

## Prior RC-54 exporter checkpoint (preserved)


> Source-only/offline milestone. The physical RIFT client has **not** produced a v0.4.19 navigation receipt. The exporter is implemented and tested with **synthetic fixtures only**; it does not assert current API facts.

## Ownership and context

- Machine: **LEGION verified via Workbridge**. Repository: `C:\work\rre`, branch `main`.
- Starting commit: `c9ff52e346bfb5ec87b81f1410aaccb1c2d85a0b` (RC-53, v0.4.19 bounded `/rre navigation` Lua discovery, source-only).
- Previous comprehensive handoff: `docs/REA-RIFT-SPELLCASTING-SESSION-HANDOFF-2026-11-10.md` (RC-53 section).
- Sole writer managed RC-54 changes; independent read-only reviewers inspected exporter against the source producer. No cross-host contact, VM use, game input, Windows/RIFT restart, Workbridge root bypass, deployment, new tool installation or remote push.

## Concrete RC-54 deliverable

- Added `tools/export-rrecollector-navigation-api.mjs` with `summarizeNavigationReceipt(saved, source)`, `renderNavigationMarkdown(qualifiedReceipt)`, `readNavigationReceipt(originalPath, requiredVersion)` and a CLI.
- CLI (Windows terminal opened at `C:\work\rre`), after a **real** physical RIFT `/rre navigation` + normal SavedVariables persistence:
  `node.exe tools/export-rrecollector-navigation-api.mjs "C:\verified\path\RRECollector.lua" --require-version 0.4.19 --output "C:\work\rre\artifacts\navigation-api.md"`
  Replace example path; `--output` uses exclusive `wx` create and will never overwrite an existing document.
- Reuses the literal-only Lua SavedVariables parser and original-file stable reader (2 MB cap, path/file-change guards). Reports original-byte SHA-256, byte size and mtime. No arbitrary Lua execution or game calls.
- Exact source contract: saved-root/probe version **0.4.19**, bound sequence, schema/scope, 8 exact guarded `Inspect` member-type paths, 2,048 scanned names, 96 retained names, 18 exact retained-name documentation entries, 512 UTF-8 bytes per excerpt, matched/ignored/truncated counter consistency, priority ordering then Lua-equivalent UTF-8 bytewise order. Empty Lua `{}` document maps are handled.
- Markdown enumerates qualified names, path types and returned bounded doc strings; clearly labels `observed-without-index`, partial scans, and lack of verified current-game load or movement control. Escapes HTML and Markdown image/link/emphasis syntax in data so descriptions remain inert research text. Source names with producer-permitted Unicode/punctuation are not falsely rejected.
- Updated `addons/RRECollector/README.md` with exact CLI and source-only qualifications.
- Added `tools/test-export-rrecollector-navigation-api.mjs` with valid synthetic fixtures, absent/stale/malformed data, ordering, cap/partial status, unavailable-index state, UTF-8/escaping, source byte hash, and exclusive no-overwrite CLI tests.

## Verified tests and limitations

- **65/65 PASS** combined Node: 10 RC-54 exporter + 14 collector source/calling + 29 SavedVariables adapter + 12 profession reader. `git diff --check` exit0.
- RC-53 package remains v0.4.19 **strict-pass**, 11 addon files. RC-53 .NET10 production-only tests **97/97 PASS**, unchanged by this exporter.
- Independent reviewers found and manager fixed: (1) extra ASCII regex incompatible with Lua producer, (2) misleading bounded-index status for documentation unavailable, (3) active Markdown images/links from documentation. Tests cover each.
- Entire new exporter remains **offline/synthetic** until a source-verified original `RRECollector.lua` with `navigationProbe` exists. Do not generate a factual current RIFT API library from these tests. No Lua 5.1 runner available. The historical full .NET checks trial stops at a missing Lab2 fixture, not counted as full-pass.
- Workbridge still admits only `C:\work` (`additionalRoots=[]`); original user Documents\RIFT SavedVariables cannot be read by this connector until separately coordinated allowed-root change/restart. v0.4.19 was **not installed** into the physical client; deployment script intentionally permits only prior v0.4.18.

## Prioritized next actions

1. **Actual data:** qualify a Lua 5.1 offline runner or a version-matched physical RIFT v0.4.19 addon load, manually invoke `/rre navigation`, persist SavedVariables and obtain original SHA-qualified file through authorized roots. No RIFT restart inherently needed.
2. **First API reference:** run strict exporter against genuine original; inspect `scanLimitReached`, counts, returned docs and evidence caveats; then deliver source-backed Markdown to the ChatGPT project.
3. **RRE/RR2 research:** investigate only source-supported navigation/position/target APIs from that reference and native REA disassembly as complementary evidence; don't infer gameplay-control APIs from names alone. Preserve SC-103 spellcasting and RC-53 collector boundaries.
