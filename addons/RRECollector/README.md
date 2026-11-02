# RRECollector v0.4.0 — read-only RIFT ability toolbar and research scaffold

A standalone addon for the physical-PC RIFT client. It does not depend on RiftReader2, BotDsBridge, SpellDump, ProjectAbilityBook, or other addons. Its source is under RRE; the game loads a separate installed copy from `Interface/AddOns/RRECollector`. Source edits do not affect a running client's already-loaded Lua until its next normal UI load.

## Source and evidence

- **v0.1 baseline:** Atank L45 Warrior, Righteous Defender role, 69/69 API-known ability IDs and detail records, separately confirmed by SpellDump v2.1.0.
- **v0.2:** the independent API capability receipt observed 1,910 indexed documentation names, 22 research-relevant names, zero documented probe errors; existing `latest` remained untouched.
- **v0.3:** adds 96 static Warrior candidate IDs from source-hashed, disabled ProjectAbilityBook Paladin (34), Void Knight (33), and Paragon (29) files. In the prior Atank snapshot, 39 of these exact IDs were listed and 57 were absent. These are **candidates**, not evidence of a learned, locked, unlearned, currently available, or castable ability. The six named Paladin IDs from original screenshots are among the absent candidates.
- **v0.4:** adds a display-only eight-icon toolbar and eight-row ability browser. It reuses the existing current-known and static catalogs, offers manual bounded Detail checks and guarded Capture/Retry buttons, and persists a small diagnostic for candidate-lookup deferrals. No icon auto-casts or continuously polls readiness.
- The static source inventory is preserved as `docs/REA-RIFT-SPELLCASTING-SC103-WARRIOR-STATIC-ABILITIES-2026-11-02.json`, with per-file SHA-256 provenance.

## Installation and loading

Deploy only this `RRECollector` directory into the physical-PC `RIFT/Interface/AddOns/RRECollector` directory, preserving the complete `RiftAddon.toc` metadata **including Email**. The TOC loads: `core.lua`, `context.lua`, `abilities.lua`, `capabilities.lua`, `candidate_catalog.lua`, `candidates.lua`, `ui.lua`, `main.lua`, in that order.

The v0.3 candidate lookup runs **once after character-scoped SavedVariables load** when a Warrior player and `Inspect.Ability.New.List/Detail` are available, unless a saved successful receipt for the same static catalog version already exists. It does not poll, send input, cast, call gameplay commands, or act on UI. If the API/player context is not ready, startup defers safely; `/rre candidates` is the optional manual retry. The game operator controls any UI reload or logout. Existing saved records survive these attempts.

## Slash commands

- `/rre status` — snapshot and candidate receipt counts.
- `/rre capture` — manually refresh **current API-listed** abilities, player, role, optional stats/target; updates only `RRECollectorData.latest`.
- `/rre probe` — manually refresh bounded API documentation/path receipt; updates only `RRECollectorData.probe`.
- `/rre candidates` — bounded explicit-ID research lookup; updates only `RRECollectorData.candidateLookup` when the API responds and the Warrior context is present.
- `/rre page N` — preview eight known captured IDs from `latest`.
- `/rre ui` — show/hide the toolbar if its in-game frame is available. The toolbar is visible by default after SavedVariables load.
- `/rre export` and `/rre help` — persistence help and command summary.

RIFT writes character-scoped SavedVariables on a normal UI reload or logout; console “recorded” means in-memory only until then. The prior 69-ID capture and 1910-name probe must remain preserved. The current frame clock is **not UTC**.

## On-screen research toolbar (v0.4)

- Eight icon slots display selected **API-known** abilities from the preserved catalog, with fallback names. Clicking an icon selects it and performs one guarded, read-only current `Inspect.Ability.New.Detail` check. Icons **never cast** spells.
- **Browse** opens paginated **Known** (saved live API-listed) and **Candidates** (historical static source) views. **Soul filter** cycles All / Paladin / Void Knight / Paragon. Select a Known row and **Pin selected** to replace the next icon slot; selections save with the character's next normal UI flush.
- **Check 8** and **Check selected** perform bounded, manual Detail reads. Red indicates an explicit API `unusable`/out-of-range response, amber a reported cooldown, grey unknown/passive, cyan only explicit API no-block flags. **No color proves successful casting**; GCD, facing, line of sight, target requirements and changed state between clicks remain unverified. There is no timer or background scan.
- **Capture** refreshes the known API list using the same guarded `/rre capture` handler; **Retry** invokes the existing bounded candidate canary lookup. `RRECollectorData.candidateAttempt` stores `recorded` or `deferred` plus a short fixed reason; no previous successful catalog is overwritten on failure.
- Drag the title area to reposition. **Hide** collapses the entire toolbar; `/rre ui` reopens it. If UI creation fails, all original slash commands and saved snapshots remain usable.

**Runtime status:** Source and installation checks alone do not verify the toolbar. A fresh Nov 2 save at 15:18 UTC reported root addon v0.3.0 but lacked `candidateLookup`; v0.4's deferred-attempt diagnostic and click retry are designed to distinguish its cause at the next normal load/save.

## Candidate lookup policy and interpretation

The lookup uses `Inspect.Ability.New.List()` only as a current-known membership control. It then attempts individual `Inspect.Ability.New.Detail(id)` queries: one listed control, up to eight *unlisted* canaries (six screenshot-named Paladin entries plus one Void Knight and one Paragon), and only if an unlisted ID returns identifying metadata, the remaining unlisted static IDs. Source corpus capped at 128, ability list at 1,024 raw entries. No unbounded scans or periodic polling.

Each candidate carries exact ID, static name/soul/category, `listed` flag, query phase/status, and whitelisted API detail fields only where returned. `candidateLookup.counts` and `policy` report whether expansion occurred. Status `no-detail` or `lookup-error` means **the explicit call did not return usable data**, not that the ability is unavailable or has a particular unlock level. Unqueried candidates are marked `not-attempted-canary-stop`. The data contract remains schema 1; the three independent saved records are not merged. Duplicate ability names across distinct IDs (for example Building Fury) remain distinct.

## Focused verification / exit gate

Run `node tools/verify-rrecollector-candidates.mjs`, `node tools/validate-roadmap.mjs` when changing a board, and `git diff --check`. Verify source/physical-PC installed hashes for all ten files. A correct TOC and identical installed hashes establish packaging, **not** a live addon/API result. The runtime gate is a subsequent normal game UI load, screenshot-visible v0.4 toolbar, and saved `RRECollectorData.candidateLookup` or `candidateAttempt` diagnostic receipt with source/character/build reconciliation. No additional game control has been authorized for RRE.
