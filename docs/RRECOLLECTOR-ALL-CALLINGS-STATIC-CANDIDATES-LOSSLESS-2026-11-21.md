# RRECollector — Lossless all-calling static ability inventory (V2)

**Saturday, November 21, 2026 · AMD-DESKTOP · approximately 4:03 PM EST**

## Decision and scope

The earlier source inventory quarantined Cleric/Purifier.lua because its Lua table repeats the ability name "Flame Lance" with two different IDs. This milestone introduces a dedicated, **bounded non-executing literal-table parser** that preserves every occurrence, including original source lines and IDs. It does not weaken the strict SavedVariables parser.

Only RRE offline tools and research artifacts changed. Production RRECollector v0.4.23, the physical game, OneDrive's disabled ProjectAbilityBook addon, unrelated repositories, character SavedVariables, and the prior V1 artifact were not modified. Historical source comments such as "current" and "bugged" are not validated current-game capability claims.

## Verified source outcome

| Calling | Soul files parsed | Static ability entries |
|---|---:|---:|
| Cleric | 11/11 | 306 |
| Mage | 12/12 | 323 |
| Primalist | 11/11 | 182 |
| Rogue | 11/11 | 300 |
| Warrior | 11/11 | 323 |
| **Total** | **56/56** | **1,434** |

The index has **1,433 unique ability IDs**. The same ID A40C51A65DBA71310 appears in Cleric Druid and Rogue Ranger for "Dismiss Pet"; both source owners are retained. Exactly **one duplicate-name group** exists: Cleric Purifier, category "2Damage", ability "Flame Lance":

- Source line 18: ID A060ED54D21F2B259, third-party adjacent comment "current".
- Source line 22: ID A1A35B21D4891044E, third-party adjacent comment "bugged".

All **29** original Purifier entries are indexed without discarding either Flame Lance declaration. Purifier source SHA-256 remains fbcdf9383c93204c976dc526b126fe6b49c677aa169e87f25fc13b1aefa4835c. **Zero files remain quarantined.**

The ID/name/category/icon values from all **55 previously accepted files** match independent replay through the older strict SavedVariables reader with zero differences. The historic 96-entry Warrior Paladin/VoidKnight/Paragon catalog also matches its original source IDs, names, categories, souls, and source-file hashes.

## Reproducible evidence

- Parser: tools/parse-pab-soul-literal.mjs. Rejects executable statements, unknown syntax, malformed ability IDs, duplicate categories and duplicate ID/Icon leaf properties. Preserves repeated ability-name keys with their original line numbers.
- Generator: tools/inventory-pab-static-abilities.mjs. Outputs schemaVersion 2, sourceLine, duplicateNames, raw source SHA-256, and unqualified static-only provenance.
- Regression: tools/test-inventory-pab-static-abilities.mjs — **9/9 passing**, verified under job rre20261121_lossless_v2_final_regression_01. The tests include exact V2 dataset reproduction from the 56 original sources.
- New source-hashed dataset: docs/RRECOLLECTOR-ALL-CALLINGS-STATIC-CANDIDATES-LOSSLESS-2026-11-21.json, **449,055 bytes**, SHA-256 **5685fa02b82b9802739f85348dcf1d0514a8b1b3e39353cf80f96135cc36908c**.
- Ordered 56-source manifest SHA-256: **898f651e8fd272dc220fe0c32aecbb3e937dac750d6d9b912b1f94ab561eb5bb**.

Previous source-hashed V1 JSON docs/RRECOLLECTOR-ALL-CALLINGS-STATIC-CANDIDATES-2026-11-21.json, SHA-256 16f6f61d8f35537fc149a78f968d268d81799061e883ec8cd659bddde9855d17, is preserved as historical evidence. The V1 findings note still accurately describes the earlier quarantine stage.

To reproduce from C:\work\rre using PowerShell: run node --test tools/test-inventory-pab-static-abilities.mjs, or node tools/inventory-pab-static-abilities.mjs with the complete disabled ProjectAbilityBook folder path. The optional --output flag writes only a new JSON filename in the repository's docs folder, using exclusive-create behavior to prevent overwriting old evidence.

## Evidence limits

Static source catalogs do not prove an ability is learned, castable, unlocked, reachable, or present in the current game build. The disabled addon source was **never executed**. No gameplay, process memory, input, RIFT UI reload or test of a current API capture occurred. WA-006 remains blocked for independent native non-player identity and scene/time qualification.

## Ranked follow-ups

**P0:** Obtain a genuine operator-controlled /rre units and /rre capture on the physical v0.4.23 client, then persist and validate the original SavedVariables. Result: a genuine current-build success/failure receipt. Requires Joey/current game owner.

**P1:** If requested, plan a narrowly scoped calling-filtered static candidate lookup from V2, with limits and versioned source pins. Result: reproducible candidate subset; no uncontrolled 1,433-ID in-game sweep. Can proceed offline autonomously.

**P2:** Continue WA-006 exact native gameplay-ID/scene/UTC qualification only when independently observed nonself Lua and native samples exist. Result: a defensible match or explicit rejection. Requires a coordinated live observation window.
