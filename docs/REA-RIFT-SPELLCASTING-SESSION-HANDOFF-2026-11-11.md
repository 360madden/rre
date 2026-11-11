# RRE RC-57 — current-build native event/query to C2M setter (LEGION, 2026-11-11 ~07:28 EST)

> **Third original-byte milestone:** A focused, bounded direct-caller check on the current LEGION RIFT PE connects query success at `0x6A64EC` to the RC-56 destination setter at `0x5749C0` via one verified `call` at `0x6A650D`. This is still a static code chain, **not** live movement or player input acceptance.

## Fresh RC-57 checkpoint

- Source: LEGION physical `rift_x64.exe` SHA-256 `1935a05c9db6d468e34e0055014a4a99c1b5afceb1695884e24600f5c20a4be8` (same verified current build as RC-55/56); no VMware, AMD-DESKTOP, game input, process attachment, game-file or memory changes, UI reload, addon deployment, new package, or remote push.
- One E8 direct-call candidate and one PE boundary-qualified caller in `[0x6A62B1,0x6A652E)`. Query `call 0xF7CD20` at `0x6A64EC`, `test al,al` at `0x6A64F1`, `je 0x6A6516` at `0x6A64F3`; receiver from `[r14+0x10]` at `0x6A6501`, setter `call 0x5749C0` at `0x6A650D`, event consumed flag `[rsi+0x18]=1` at `0x6A6512`.
- Independent manager `rre-rc57-manager-original-byte-confirm-20261111` exit0: original PE source hash matches, 637-byte code-window SHA `e820bb56a8d8b4ed6f21d61314d40ce003e01ec4a17e3c5d795da0f2a1e1fa09`, **142/142 instructions** decoded within region, exact call targets verified. Independent agent discovery job `rre-rc57-native-newbuild-c2m-direct-call-20261111` exit0.
- New files: `docs/RRE-C2M-EVENT-NEW-BUILD-LEGION-2026-11-11.md`, `docs/RRE-C2M-EVENT-NEW-BUILD-LEGION-2026-11-11.json`, plus this checkpoint. Sole main-branch writer: manager; one read-only agent, stopped on useful one-probe finding.
- Last accepted commit before RC-57: `a7342735715b2151804c121f6878cbb3f78a5fc4` (RC-56). Recheck Git HEAD, status, SHA-qualified docs after integration. No RC-57 addon changes; prior RC-55 v0.4.19 preflight and 53/53 relevant Node checks still stand.
- Remaining gates: specific input-event type/button, callback registration and local-player receiver identity, real game-world destination/motion, stop/cancel, and type-7 route linkage **unqualified**. Do not promote static code to a callable automation contract.
- Next tasks (ranked): **1.** read-only callback ownership/registration with one bounded discriminator; **2.** event type/button meaning from the already selected range; **3.** separately authorized operator-owned physical RIFT movement/stop observation. No broad type-7 scans or Ghidra PE imports.

## Prior RC-56 checkpoint (preserved)


> **Second verified native milestone:** Two bounded original-byte probes located the current executable's click-to-move destination **setter** and **consumer entry**; manager independently requalified their complete `.pdata` windows. Still static-only, not active gameplay movement or a qualified player-owned pointer chain.

## Fresh RC-56 checkpoint

- Host: **LEGION**, physical RIFT executable only; original SHA-256 `1935a05c9db6d468e34e0055014a4a99c1b5afceb1695884e24600f5c20a4be8`. No VM, AMD-DESKTOP, game input/reload, process attach, game-file or memory write, deployment, network push or new dependency.
- Previous accepted local RC-55 commit: `b4ac7ed2ada41e38329bfebe95c81d266b5da80b` on `main` (11 ahead of origin, clean immediately after RC-55).
- **Static C2M setter:** old `0x562BC0` -> current `0x5749C0`; unique **20-byte** source signature; full unwind `[0x5749C0,0x574A18)`, 88 bytes, 21 instructions, SHA `e6427f87b5f3f2a407bd742142181cffe82125a2b9943b80a690b8aa374d6075`. Setter clears old state, writes supplied 12-byte destination to receiver `+0xB90` component `+0x60/+0x68`, sets `+0x1A8` bit0.
- **Static consumer entry:** old `0x5765D0` -> current `0x588420`; unique **14-byte** signature; unwind `[0x588420,0x5884A7)`, 135 bytes, 32 instructions, SHA `2b57dcbdb4c7a84f243a5ba8ad35f5b1988f4135c1401158a8e9b7cee8e3ec26`. It reads the same component and tests the activation bit. Further consumer branches uninspected.
- Current new direct clear call targets `0x5460A0` and `0x546830`. This confirms selected cross-build static state relationship, **not** current player ownership, event delivery, actual movement, cancellation, route planning or collision.
- Evidence saved: `docs/RRE-C2M-NEW-BUILD-LEGION-2026-11-11.md` and `.json`. Native jobs `rre-rc56-native-c2m-samebytes-20261111` and `rre-rc56-native-c2m-setter-consumer-20261111` exit0, two-probe stop. Independent manager `rre-rc56-native-independent-window-verify-20261111` exit0, exact full-window SHA and all **53 decoded instructions**.
- One read-only agent investigated and stopped; manager alone wrote documentation and commits. Starting worktree for RC-56 was clean; selected RC-56 changed files are the two reports plus this handoff.
- **Next:** (1) one bounded current-build event callback direct-caller and owner trace for new setter `0x5749C0`; (2) small consumer continuation for near-stop state; (3) separately authorized manual runtime player XYZ + click/stop proof only after current client version, exact session and input ownership. Do not repeat broad type-7 scans.
- Offline RC-55 Node tests remain **53/53**, package preflight v0.4.19 exit0; **no new addon source changes or live tests in RC-56**. RC-56 JSON/provenance and Git diff checks are its relevant acceptance; no full .NET test rerun warranted.

## Prior RC-55 checkpoint (preserved)


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
