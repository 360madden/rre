# RRECollector v0.4.6 — read-only RIFT ability toolbar and research scaffold

A standalone addon for the physical-PC RIFT client. It does not depend on RiftReader2, BotDsBridge, SpellDump, ProjectAbilityBook, or other addons. Its source is under RRE; the game loads a separate installed copy from `Interface/AddOns/RRECollector`. Source edits do not affect a running client's already-loaded Lua until its next normal UI load.

## Source and evidence

- **v0.1 baseline:** Atank L45 Warrior, Righteous Defender role, 69/69 API-known ability IDs and detail records, separately confirmed by SpellDump v2.1.0.
- **v0.2:** the independent API capability receipt observed 1,910 indexed documentation names, 22 research-relevant names, zero documented probe errors; existing `latest` remained untouched.
- **v0.3:** adds 96 static Warrior candidate IDs from source-hashed, disabled ProjectAbilityBook Paladin (34), Void Knight (33), and Paragon (29) files. In the prior Atank snapshot, 39 of these exact IDs were listed and 57 were absent. These are **candidates**, not evidence of a learned, locked, unlearned, currently available, or castable ability. The six named Paladin IDs from original screenshots are among the absent candidates.
- **v0.4:** adds a display-only eight-icon toolbar and eight-row ability browser. It reuses the existing current-known and static catalogs, offers manual bounded Detail checks and guarded Capture/Retry buttons, and persists a small diagnostic for candidate-lookup deferrals. No icon auto-casts or continuously polls readiness.
- **v0.4.6:** one shared plain-button skin for commands and the working restricted reload surface; four-sided borders, equal base typography measured with GetWidth/GetHeight, visible press offset, distinct selected/disabled states. Ability icons retain square proportions, gain two-line labels and full-name hover cards. No ability or candidate logic changed.
- **v0.4.5:** fixes a documented security-parent violation in the Reload UI control. The clickable, plain-styled Frame now lives in its own restricted UI context, with parent security enabled before the child. Macro setup is read back through EventMacroGet; registration and actual hardware-click execution are reported separately. The normal toolbar remains unsecured and its appearance unchanged.
- **v0.4.4:** isolates the secure Reload UI macro from ordinary mouse Down/Up handlers, matching the installed Gadgets plain-Frame pattern. Records the result of macro setup in character-scoped uiReloadMacro (registered or failed). This setup receipt is not proof a click executed reloadui.
- **v0.4.3:** replaces themed stretched RIFT buttons with conventional rectangular, hover/pressed/disabled controls. Captions use centered natural-size RIFT Text frames (no fixed text aspect ratio), measured available width and bounded font reduction to prevent clipping on short controls. The restricted Reload UI macro uses a matching plain frame and stays click-only; a rejected macro disables that control without blocking the toolbar.
- **v0.4.2:** remembers toolbar position, clamps expanded/collapsed layout, improves UI initialization diagnostics, synchronizes Hide with browser visibility, and adds a guarded, click-only native Reload UI button. Live game verification remains pending.
- **v0.4.1:** after a startup deferral specifically caused by missing Warrior player context, attempts at most two guarded, event-driven retries on addon startup completion and player full availability. Records the automatic retry count; never polls every frame or overwrites earlier successful snapshots. Swaps flat command rectangles for RIFT-native buttons with built-in hover/pressed/disabled styling; ability rows and icon slots gain subtle hover, press and selection accents.
- The static source inventory is preserved as `docs/REA-RIFT-SPELLCASTING-SC103-WARRIOR-STATIC-ABILITIES-2026-11-02.json`, with per-file SHA-256 provenance.

## Installation and loading

Deploy only this `RRECollector` directory into the physical-PC `RIFT/Interface/AddOns/RRECollector` directory, preserving the complete `RiftAddon.toc` metadata **including Email**. The TOC loads: `core.lua`, `context.lua`, `abilities.lua`, `capabilities.lua`, `candidate_catalog.lua`, `candidates.lua`, `ui.lua`, `main.lua`, in that order.

The candidate lookup runs after character-scoped SavedVariables load when a Warrior player and `Inspect.Ability.New.List/Detail` are available, unless a successful receipt for this static catalog version already exists. On the exact `warrior-player-context-not-ready` startup deferral, it can automatically retry on `Event.Addon.Startup.End` or a `player` entry in `Event.Unit.Availability.Full`, with a combined limit of two automatic retries. No periodic polling, input, casting, or gameplay commands are issued. `/rre candidates` and the toolbar **Retry** remain manual fallbacks. The game operator controls any UI reload or logout. Existing saved records survive these attempts.

## Slash commands

- `/rre status` — snapshot and candidate receipt counts.
- `/rre capture` — manually refresh **current API-listed** abilities, player, role, optional stats/target; updates only `RRECollectorData.latest`.
- `/rre probe` — manually refresh bounded API documentation/path receipt; updates only `RRECollectorData.probe`.
- `/rre candidates` — bounded explicit-ID research lookup; updates only `RRECollectorData.candidateLookup` when the API responds and the Warrior context is present.
- `/rre page N` — preview eight known captured IDs from `latest`.
- `/rre ui` — show/hide the toolbar if its in-game frame is available. The toolbar is visible by default after SavedVariables load.
- `/rre export` and `/rre help` — persistence help and command summary.

RIFT writes character-scoped SavedVariables on a normal UI reload or logout; console “recorded” means in-memory only until then. The prior 69-ID capture and 1910-name probe must remain preserved. The current frame clock is **not UTC**.

## On-screen research toolbar (v0.4.1)

- Eight icon slots display selected **API-known** abilities from the preserved catalog, with fallback names. Hovering adds a cyan top accent; pressing briefly depresses the background; clicking selects and performs one guarded, read-only current `Inspect.Ability.New.Detail` check. Icons **never cast** spells.
- **Browse** opens paginated **Known** (saved live API-listed) and **Candidates** (historical static source) views. Native buttons respond to hover and press; selected mode has a cyan underline, ability rows have hover/pressed/selected feedback, the current Soul filter value is visible, and Prev/Next disable at the page limits. **Soul filter** cycles All / Paladin / Void Knight / Paragon. Select a Known row and **Pin selected** to replace the next icon slot; selections save with the character's next normal UI flush.
- **Check 8** and **Check selected** perform bounded, manual Detail reads. Red indicates an explicit API `unusable`/out-of-range response, amber a reported cooldown, grey unknown/passive, cyan only explicit API no-block flags. **No color proves successful casting**; GCD, facing, line of sight, target requirements and changed state between clicks remain unverified. There is no timer or background scan.
- **Capture** refreshes the known API list using the same guarded `/rre capture` handler; **Retry** invokes the existing bounded candidate canary lookup. `RRECollectorData.candidateAttempt` stores `recorded` or `deferred`, a short fixed reason and an automatic-retry count; no previous successful catalog is overwritten on failure.
- Drag the title area to reposition. **Hide** collapses the entire toolbar; `/rre ui` reopens it. If UI creation fails, all original slash commands and saved snapshots remain usable.

**Runtime status:** Source and installation checks alone do not verify the toolbar. A fresh Nov 2 save at 15:18 UTC reported root addon v0.3.0 but lacked `candidateLookup`; v0.4's deferred-attempt diagnostic and click retry are designed to distinguish its cause at the next normal load/save.

## Candidate lookup policy and interpretation

The lookup uses `Inspect.Ability.New.List()` only as a current-known membership control. It then attempts individual `Inspect.Ability.New.Detail(id)` queries: one listed control, up to eight *unlisted* canaries (six screenshot-named Paladin entries plus one Void Knight and one Paragon), and only if an unlisted ID returns identifying metadata, the remaining unlisted static IDs. Source corpus capped at 128, ability list at 1,024 raw entries. No unbounded scans or periodic polling.

Each candidate carries exact ID, static name/soul/category, `listed` flag, query phase/status, and whitelisted API detail fields only where returned. `candidateLookup.counts` and `policy` report whether expansion occurred. Status `no-detail` or `lookup-error` means **the explicit call did not return usable data**, not that the ability is unavailable or has a particular unlock level. Unqueried candidates are marked `not-attempted-canary-stop`. The data contract remains schema 1; the three independent saved records are not merged. Duplicate ability names across distinct IDs (for example Building Fury) remain distinct.

## Focused verification / exit gate

Run `node tools/verify-rrecollector-candidates.mjs`, `node tools/validate-roadmap.mjs` when changing a board, and `git diff --check`. Verify source/physical-PC installed hashes for all ten files. A correct TOC and identical installed hashes establish packaging, **not** a live addon/API result. The runtime gate is a subsequent normal game UI load, screenshot-visible v0.4 toolbar, and saved `RRECollectorData.candidateLookup` or `candidateAttempt` diagnostic receipt with source/character/build reconciliation. No additional game control has been authorized for RRE.
