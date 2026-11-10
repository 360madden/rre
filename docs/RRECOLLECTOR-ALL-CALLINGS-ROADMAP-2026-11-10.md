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

## First next commands

- Inspect current `git status`, `addons/RRECollector/{ui,abilities,candidates,main,core}.lua`, manifest and test fixtures.
- Build a source-extracted calling-neutral UI fixture and candidate-scope fixture.
- Run `node tools/verify-rrecollector-package.mjs`, focused Lua/Node checks, `git diff --check`; integrate and checkpoint.
