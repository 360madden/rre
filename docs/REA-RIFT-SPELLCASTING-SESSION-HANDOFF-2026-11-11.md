# RRE RC-54 — Navigation API Markdown exporter handoff (LEGION, 2026-11-11 00:04 EST)

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
