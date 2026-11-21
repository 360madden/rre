# RRECollector — All-calling static ability source inventory
**Saturday, November 21, 2026 · AMD-DESKTOP · offline source research**

## Decision

A historical, **disabled** third-party ProjectAbilityBook addon provides bounded static candidates for all five RIFT character callings. The current production RRECollector **v0.4.23 remains unchanged** and its own installed static catalog remains the earlier source-hashed **96 Warrior IDs**. This inventory creates a future source-qualified expansion base, **not** a new API-known, learned, unlocked, available or castable catalog.

**Inputs:** exactly the 56 local `Callings/<calling>/<soul>.lua` files under `OneDrive\Documents\RIFT\Interface\AddOns\projectabilitybook.disabled`. Each original Lua source byte stream was SHA-256 hashed and parsed as a literal-only table using the existing fail-closed SavedVariables parser after replacing only its assignment prefix **in memory**. No Lua execution, RIFT game I/O, addon installation, process-memory action, external network request, or modification of ProjectAbilityBook occurred.

## Verified counts

| Calling | Soul source files | Parsed files | Static ability entries |
|---|---:|---:|---:|
| Warrior | 11 | 11 | 323 |
| Rogue | 11 | 11 | 300 |
| Mage | 12 | 12 | 323 |
| Cleric | 11 | 10 | 277 |
| Primalist | 11 | 11 | 182 |
| **Total** | **56** | **55** | **1,405** |

- **1,404 unique 17-character ability IDs** in the 1,405 accepted source entries.
- Exactly **one identical ID reused across two callings**: `A40C51A65DBA71310`, label **Dismiss Pet**, in Cleric `Druid.lua` and Rogue `Ranger.lua`. The index retains both owning source rows, not an invented class-specific ID.
- **One quarantined original source:** `Callings/Cleric/Purifier.lua`, SHA-256 `fbcdf9383c93204c976dc526b126fe6b49c677aa169e87f25fc13b1aefa4835c`. It declares `["Flame Lance"]` twice in the `2Damage` category:
  - Line 18: ID `A060ED54D21F2B259`, source comment `current`.
  - Line 22: ID `A1A35B21D4891044E`, source comment `bugged`.
  These source comments are *historical third-party claims*, not current-client API verification. Lua would overwrite one of the duplicate keys if executed. The safe parser rejects this file completely rather than silently dropping either record. Both source ID leads are retained **in this research note only**, and neither is an accepted indexed record until an explicit duplicate-preserving extraction is implemented.
- The existing Warrior source catalog `docs/REA-RIFT-SPELLCASTING-SC103-WARRIOR-STATIC-ABILITIES-2026-11-02.json` was independently cross-checked: **96/96 ID, name, category and soul tuples** exactly match the original Paladin, VoidKnight and Paragon source files; all three original SHA-256 hashes agree.

## Reproducible artifacts and commands

- Generator: `tools/inventory-pab-static-abilities.mjs`
- Regression: `tools/test-inventory-pab-static-abilities.mjs`
- Source-hashed dataset: `docs/RRECOLLECTOR-ALL-CALLINGS-STATIC-CANDIDATES-2026-11-21.json` (**404,174 bytes**, SHA-256 `16f6f61d8f35537fc149a78f968d268d81799061e883ec8cd659bddde9855d17`).
- Source-manifest SHA-256 (ordered original path/hash/quarantine statuses): `fb29d8fec967d848973feb37dff891cbb04cf41428f0140078c3e72bb8105953`.
- Read-only summary: `node tools/inventory-pab-static-abilities.mjs "FULL_PATH_TO_projectabilitybook.disabled"`.
- Reproduce JSON to an **absent** filename in the RRE `docs` folder using `--output "C:\work\rre\docs\NEW_STATIC_INDEX.json"`. Exclusive creation prevents silently overwriting existing research evidence.
- Focused verification: `node --test tools/test-inventory-pab-static-abilities.mjs` — **7/7 passed**, including safe parsing, ID validation, duplicate preservation, executable-Lua rejection, input-root constraints, command-line usage, 56-source real inventory and old Warrior 96-source parity.

## Acceptance limits and recommended sequence

**P0 — Physical v0.4.23 unit and ability evidence.** A current API capture remains the higher-value live blocker. The installed Collector has 12/12 source parity and its SavedVariables root is v0.4.23, but the last known accepted ability capture remains older and there is no current unit witness. This static dataset does **not** repair that evidence gap.

**P1 — Lossless Purifier representation.** Only if a broad static catalog is needed, implement a duplicate-aware source parser preserving both source-level Flame Lance IDs, category and per-line provenance. Never execute the old Lua to resolve duplicates; that would discard an entry. Do not label either ID live-known or unlocked.

**P2 — Calling-specific static catalog integration.** After the live v0.4.23 gate, propose a small versioned Collector expansion for class-filtered candidate lookups. Pin the new source manifest and distinguish historical/source IDs from `Inspect.Ability.New.List/Detail` results. No blanket 1,404-ID in-game Detail sweep, no casting, and no repurposing the existing 96 Warrior canaries as cross-class capabilities.

**WA-006 remains blocked.** An ability-ID index does not substantiate native entity identity, collision ownership, navigation or process-image qualification.
