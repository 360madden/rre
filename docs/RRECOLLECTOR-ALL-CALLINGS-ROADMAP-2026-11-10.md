# RC-33 — All-callings RRECollector compatibility and reliability (2026-11-10 EST)

Host: LEGION (fresh `hostname.exe` verification). Repository: `C:\work\rre`. Operator: Joey.
Owner: single RRE manager on `main`; independent reviewers read-only. Applies to the same addon on physical LEGION and future synced clients, without operating VMware from LEGION.

## Requirement

RRECollector must render and capture current API-known abilities, player context and valid saved pins without assuming Warrior. Target all RIFT callings/roles/builds and any profession actions exposed by the bounded `Inspect.Ability.New.List/Detail` API. Do not promise unavailable/unlearned skills or profession-specific APIs. Keep historical 96-ID Paladin/VoidKnight/Paragon source research explicitly Warrior-only.

## Confirmed starting evidence

- Historical Rogue Bolinao RRECollector v0.4.11: 54/54 current ability Details captured (SC-610 historical Lab-2; not current LEGION runtime acceptance).
- Current v0.4.14 `abilities.lua` is calling-neutral; `ui.lua` filters Known against Warrior source IDs when soul != All; filter cycles only three Warrior souls; `candidates.lua` defers non-Warriors with ambiguous context error.
- First capture can leave toolbar empty because `loadSlots()` runs at UI construction, before the first snapshot.
- Current version's exact live UI and Rogue SavedVariables are not yet verified on LEGION.

## Practical milestone gates

| Gate | Scope | Evidence / stop condition |
|---|---|---|
| **RC33-A** | Audit all-calling/crafting scope and existing failures; independent code reviews | Class matrix with proven API support, unsupported candidates, reproducible defects |
| **RC33-B** | Fix calling-neutral Known browser, truthful Warrior-only Candidates/retries, first-capture slots, stale/invalid display | Real-source regression tests for Rogue, Mage, Cleric, Primalist, Warrior, unknown calling; no combat/game actions |
| **RC33-C** | Audit recovery, malformed saved data, role switches, counts/caps, wire integrity, GUI callbacks | Focused test suites PASS; no known reproducible critical failure left unfixed |
| **RC33-D** | Synchronize source addon version, TOC, window title and startup chat; update documentation | Lua parse, package validation, existing suite and Git diff check PASS |
| **RC33-E** | Safely deploy **only RRECollector** to verified LEGION OneDrive `Documents\Rift\Interface\AddOns\RRECollector`, with backup, TOC last | Exact source-to-installed file hashes and no other addon touched. Installation != live load |
| **RC33-F** | In-game Rogue + Warrior runtime acceptance when a fresh LEGION physical-client window and authorization are available | Version-matched visible title/startup chat, per-character snapshot, all-ability list, 8 pins, no misleading Warrior filter; record pending if not observed |

## Operating rules

1. Verify actual target machine and git state before each write/deployment. Preserve user changes and existing installed addon; do not touch VMware from LEGION.
2. Keep `main` a single writer. Reviewers only inspect. Use no FreeBuff/Ollama.
3. Scoped regressions first; then complete addon/repo gate once after integration. Commit practical milestones; never force push/divergent histories.
4. No game keyboard/mouse/reload/restart is implied by source, packaging, or OneDrive deployment. Any missing live evidence is explicitly **pending**, not green.
5. User-facing SITREP: color status, elapsed time, exact tests, what works vs what remains unverified.

## Execution checkpoint — 17:26 EST, LEGION

- **RC33-A:** complete; historical Rogue Bolinao 54/54 proof, all-callings capture-path review; independent reader and Lua reviews completed read-only.
- **RC33-B/C:** patched Known all-callings browsing, non-Warrior static-empty explanation, calling/sequence saved-label, guarded nested data and first-capture slots, robust prior-snapshot acceptance, empty-capture/sequence handling. Source-level tests **27/27** PASS; independent review found no remaining obvious Lua syntax error, but Lua interpreter and in-game behavior not yet verified.
- **RC33-D:** source, TOC, docs and title/chat all share **v0.4.15**. Strict package check PASS; C# production **87/87** PASS including .15 Rogue/Experience. Full historical .NET suite blocked by absent `artifacts/sc628-live-context-20261107-1533/wire/request.json` after 160 passed, not treated as a source regression. Lua runtime and parser absent; no installation attempted.
- **RC33-E:** fresh `hostname.exe` returned **LEGION**. Existing OneDrive install was **v0.4.14**. Installer backed up all 11 originals to `artifacts/RRECollector-installed-v0414-LEGION-20261110-172557-165` and deployed v0.4.15 with TOC last; independent strict package parity **11/11** PASS, `runtimeUiVerified=false`.
- **RC33-F:** **OPEN**. No game reload/restart or input. RIFT toolbar title/startup chat and fresh Rogue/Warrior snapshots must be verified after an authorized, normal physical-game UI load. OneDrive cloud propagation to other hosts is not independently verified. Profession data outside `Inspect.Ability.New.List/Detail` remains unsupported pending verified API discovery.
- **Next bughunt:** prior BH-03 stale/off-page Pin/Check, BH-06 publication status, BH-12 scan count and BH-13 display disambiguation remain explicit potential follow-ups; this RC33 checkpoint is not a claim of bug-free software.

## RC-34 follow-on reliability milestone (17:34 EST)

Review of the earlier full-codebase BH-03, BH-06, BH-12 and BH-13 showed four additional collector/UI defects not fully covered by RC-33. The manager is implementing **v0.4.16** with these concrete gates:

1. **RC34-A (action integrity):** page-visible API-known identity required at both click and disabled-button render; new Capture and page navigation clear stale selection; retained Check control can be disabled.
2. **RC34-B (presentation/data truth):** all same-name rows show their exact unique ID; icon captions keep distinguishing suffixes; current-load wire receipt shown separately from saved API capture; scanned documentation counters stay within cap.
3. **RC34-C (verification):** repair historical RC31 source-extracted harness boundaries, focus Node tests, C# production reader compatibility (.12 through .16), strict TOC/version/title/init-chat consistency, diff/roadmap checks. Lua interpreter absent on LEGION, so Lua runtime tests and in-game behavior are *pending*, not green.
4. **RC34-D (installation):** backup current 11 installed v0.4.15 files, copy only v0.4.16 RRECollector from this repo to verified LEGION OneDrive with TOC last, then require 11/11 hashes. No forced game reload or cross-host sync claims.
5. **RC34-E (live acceptance):** manual physical-game Rogue/Warrior Capture after normal UI load and matching SavedVariables/title/chat; classify any remaining unknown profession UI separately.

**Safety/ownership:** exact machine check, no VMware from LEGION, single writer, no FreeBuff/Ollama, no game input/restart/reload.

## Execution checkpoint — 17:47 EST, LEGION (RC-34)

- **RC34-A/B implementation:** bounded page-current Pin/Check selection (including disabled control state), clear selection on new Capture and page changes, exact source IDs at start of same-name rows, distinguishing tile suffixes, explicit saved character/calling/role/sequence and separate current-load wire receipt. API documentation scan bound to at most 2048 entries.
- **Version and consumers:** RRECollector source/TOC/window title/startup chat share **0.4.16**. RREC2 C# production reader and Node/Python SavedVariables adapters admit 0.4.16 while retaining older versions and 0.4.14+ Experience contract.
- **Verification:** final focused Node 31/31 PASS (`rre-rc34-final-node-20261110-01`); C# production-only 89/89 PASS (`rre-rc34-first-dotnet-20261110-01`); full Node autodiscovery 38/38 PASS (`rre-rc34-final-node-auto-20261110-01`); strict source package v0.4.16 PASS (`rre-rc34-final-package-20261110-01`). RC31 Lua source-extracted fixtures updated, but not executable on LEGION without Lua interpreter. Full historical .NET suite still blocked by missing archived SC628 fixture; cannot call that suite green.
- **Physical OneDrive:** `hostname.exe` verified **LEGION** (`rre-rc34-final-host-check-20261110-01`). Final deployment backed up 11 previous installed files at `artifacts/RRECollector-installed-v0416-LEGION-20261110-174700-526`; copied only 11 RRECollector files to `C:\Users\mrkoo\OneDrive\Documents\Rift\Interface\AddOns\RRECollector` with TOC last. Independent strict verifier `rre-rc34-v0416-final-final-11of11-20261110-01` exit0 **11/11 SHA parity**, `runtimeUiVerified=false`. Earlier RC33 v0.4.14 and RC34 v0.4.15 backup paths retained.
- **RC34-E still OPEN:** no physical game reload, input, runtime screenshot, Rogue/Warrior manual Capture, startup-chat version or saved-file receipt. OneDrive propagation to another host and any profession-specific API are not verified. Historical Rogue 54/54 cannot establish new runtime acceptance.
- **Next RC35 proposal:** bounded, non-playing runtime `Inspect.Documentation` discovery for Craft/Profession/Tradeskill/Recipe/Fishing/Survival, with guarded exact API path status and separate receipt, before promising those categories. Preserve current v0.4.16 until source/regression and in-game test are qualified.

## RC-35 plan — profession API discovery (after stable v0.4.16)

**Problem:** Fishing and Survival appear as profession-related General spellbook entries in historical UI evidence yet were not among that character's 69 API-known abilities. Current collector cannot claim complete profession coverage. Historical documentation neither proves nor disproves current profession inspectors.

1. **RC35-A investigation:** inspect source, historical UI/Inspector references and exact exposed API names; do not guess a profession data producer.
2. **RC35-B implementation:** bounded manual `/rre professions` capability-only receipt. Scan at most 2048 `Inspect.Documentation` names; retain at most 96 relevant names, document snippets at most 512 bytes, and query only a short allowlisted set of exact candidate path types. Persist separately as `RRECollectorData.professionProbe` with schema/version, context and receipt; never call profession/crafting gameplay functions. Prior `.latest`, `.probe` and `.candidateLookup` remain intact.
3. **RC35-C regression:** source code path and, if a Lua interpreter is available, executable Lua5.1 behavior tests for type failures, bounds, invalid saved sequences, receipt preservation and slash failure. Verify title/init chat/TOC/shared-version and downstream readers before a source release.
4. **RC35-D release:** independent verification, safe LEGION OneDrive backup + exact SHA parity, new version-only deployment, local commit and fast-forward push. In-game load and independent propagation remain separate.
5. **RC35-E discovery acceptance:** manual LEGION physical RIFT invocation after authorized normal UI load; inspect persisted exact API paths/doc names. Only implement a real profession-data producer on proved current callable APIs and return schema. If none exist, keep an explicit unsupported/unknown result, not fabricated skill data.

## RC-35 execution checkpoint — 18:00 EST (LEGION)

- **Newly found and fixed P1 integrity defects:** source-producer `captureComplete` previously accepted any `Unit.Detail(player)` table regardless of missing id/name/calling/level, and accepted empty Detail `{}` as a full result. v0.4.17 now requires substantive Detail (name/idNew/description), retries inconclusive batches by bounded scalar fallback, requires qualified player, role and clock bounds, rejects invalid ID shapes; prior complete saved snapshot is not overwritten on transient capture incompleteness. Also sanitizes candidate/probe sequence and fixes two-character captions.
- **New bounded manual `/rre professions`:** indexes at most 2048 documented names, keeps 96 matching names, inspects 18 exact candidate path types and bounded descriptions without calling any profession, recipe or crafting action. Saves `RRECollectorData.professionProbe` and its sequence independently of current ability `.latest`, existing `.probe` and `.candidateLookup`. This is **API discovery only**; no claim Fishing/Survival or crafting data is now collected.
- **Offline verification:** focused Node **33/33** (`rre-rc35-v17-focused-final-20261110-01`); broader Node autodiscovery **38/38** (`rre-rc35-v17-autodiscover-20261110-01`); .NET10 production **91/91** (`rre-rc35-v17-dotnet-prod-20261110-01`); strict source package v0.4.17 (`rre-rc35-v17-package-final-20261110-01`); `git diff --check` PASS before handoff; reader also admits retained .12-.16. Lua 5.1 runtime/interpreter unavailable on LEGION, and full historical .NET fixture still absent.
- **OneDrive release:** previous installed v0.4.16 backed up as `C:\work\rre\artifacts\RRECollector-installed-v0416-LEGION-20261110-175953-865`; after final README correction a second backup of early v0.4.17 saved at `C:\work\rre\artifacts\RRECollector-installed-v0417-LEGION-20261110-180035-975`. Only RRECollector's 11 source files installed to the verified OneDrive path, TOC last, no game action. Strict installed verifier job `rre-rc35-v0417-final-installed-11of11-20261110-01` pending result at checkpoint; never claim runtime success from file parity.
- **Open live gates:** physical RIFT UI must load title `RRE v0.4.17 research` and chat `v0.4.17 ready`; manual Rogue/Warrior captures, persisted frames and `/rre professions` documentation output still absent. No other machines' OneDrive propagation checked.

## First next commands

- Inspect current `git status`, `addons/RRECollector/{ui,abilities,candidates,main,core}.lua`, manifest and test fixtures.
- Build a source-extracted calling-neutral UI fixture and candidate-scope fixture.
- Run `node tools/verify-rrecollector-package.mjs`, focused Lua/Node checks, `git diff --check`; integrate and checkpoint.
