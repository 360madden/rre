# RRECollector v0.2.0 (source-only modular scaffold)

A standalone, one-shot, read-only RIFT addon for the RRE spellcasting roadmap. No dependency on RiftReader2, BotDsBridge or other addons. **v0.2.0 is a source-only modular split, not yet installed or live verified**; the previously installed v0.1.0 produced the accepted 69/69 SC-418 catalog. Preserve that evidence until a separately operator-driven v0.2 smoke check.

## Install

Copy this whole directory to the physical PC's RIFT Interface/AddOns/RRECollector directory. The RIFT client loads installed copies, not this Git checkout. Do not overwrite existing addons. Reload the UI or restart the game through the game operator.

## Source module layout

`RiftAddon.toc` loads these scripts in order: `core.lua` (shared safe scalar/API wrappers, version/schema), `context.lua` (player/target/role/stats), `abilities.lua` (current known API List/Detail and completeness) and `main.lua` (slash commands, status/page, SavedVariables lifecycle). They share only the `RRECollectorRuntime` namespace; no `require` or other addon dependency. The `RRECollectorData.latest` schema remains **1**, and existing `/rre` commands retain their names and semantics. RC-02 will add one bounded manual API capability probe after RC-01 acceptance.

## Commands

- /rre help: list commands.
- /rre status: inspect load/capture status and counts.
- /rre capture: snapshot character identity, combat-role type, best-effort role slot/names, optional stats and target, known/available ability IDs and details.
- /rre page N: show eight captured ability names/lookup IDs (1-based).
- /rre export: show persistence instructions.

The collector is idle unless /rre capture is invoked. Captures go to character-scoped SavedVariables RRECollectorData.latest, then RIFT normally flushes them on /reloadui or logout. The exported frame clock is not UTC. Neither a successful source copy nor a syntax check proves live loading.

## Data contract

Schema 1 includes player, roleSlot (if the current client exposes Inspect.TEMPORARY.Role), roleNames, stats, target, clientVersion, frameTime, abilityList counts/completeness, abilities, detailErrors and capability flags. Raw ability lookup IDs are sorted. False/zero metadata remains meaningful; absent fields mean unknown, never false. Batch Inspect.Ability.New.Detail is tried first; a missing record gets a per-ID fallback. Enumeration caps: 1024 raw entries, 512 distinct IDs; any ignored/truncated entries or failed details mark captureComplete=false.

Inspect.Ability.New.List is a current API ability set, NOT a catalog of every unlearned trainer/soul/locked spell. No gameplay commands, auto-casting, polling, external process interaction or unrestricted file writes are performed.

## Operator smoke check (once)

1. When deployment is approved for a later milestone, check the installed RiftAddon.toc version 0.2.0 and all four TOC-listed Lua hashes against Git. Current host v0.1 package must remain untouched until that step.
2. From the game, run /rre status and /rre capture; verify a nonzero, correctly identified catalog with /rre status and /rre page 1.
3. Execute a normal UI reload/logout and inspect the character SavedVariables record. Match character, active role, and spellbook screenshots before treating it as SC-102 evidence.

Physical-PC client is the authoritative REA target. VMware lab catalogs are separate supplementary observations and must never be merged by name or level alone.
