# RC-13 — exact-ID ability atlas, source-qualified offline union

**Date:** 2026-11-02 UTC  
**State:** Accepted at offline/data-join scope; **not** RC-08 live candidate-lookup completion.  
**Owner:** RRE/REA manager  
**Artifact:** [Machine-readable 126-ID atlas](REA-RIFT-SPELLCASTING-SC103-ABILITY-ATLAS-2026-11-02.json)  
**Rebuild:** node tools/build-rift-ability-atlas.mjs (read-only JSON to stdout)  
**Focused check:** node --test tools/verify-rift-ability-atlas.mjs — three tests.

## Exact-ID outcome

The atlas joins four existing SHA256-pinned, accepted sources, preserving the ID in every record and marking where the ID came from. It is **one lookupable, deterministic source index**, not another installed RIFT addon or a new in-game capture.

| Set | Count |
| --- | ---: |
| Unique IDs across accepted static/API sources | **126** |
| Listed in Atank's prior saved Inspect.Ability.List/Detail | 69 |
| From disabled ProjectAbilityBook's three Warrior soul files | 96 |
| Exact IDs present in both | 39 |
| Static soul candidates **not listed** in the saved 69 | **57** |
| Previously listed API IDs outside those three static files | 30 |
| Previously known IDs associated with seven spellbook UI sections | 69 |
| Unlisted static candidates with source-hashed Soul Tree tooltip transcription | 6 |

| Source soul | Static candidates | In prior API list | Not in prior list |
| --- | ---: | ---: | ---: |
| Paladin | 34 | 28 | 6 |
| VoidKnight | 33 | 7 | 26 |
| Paragon | 29 | 4 | 25 |

Every record includes exact ID/name, source soul/category/icon where present, prior API-listed status, a whitelisted prior Detail metadata subset or null, known UI section and its association basis if available, any Soul Tree tooltip metadata, and explicit unknown unlock/usability and null role-slot fields.

Among the **69** prior API Details, **61** include a description, **39** include a cooldown number and **30** omit that field. An omitted cooldown remains null and **never** becomes a zero-second cooldown. Static absence from the prior list is **not** evidence of locked, learnable, eligible, or unusable state.

## Paired tooltip records: ID provenance differs from UI mechanics provenance

Six not-listed Paladin candidates are independently exact-name joined to static IDs and UI tooltips: Light's Benediction, Vengeful Decree, Aegis of the Light, Sanctuary, Protector's Fury, and Call of the Divine. The tooltip screenshots do **not** display those modern IDs. Their Power, range, listed cooldowns, effects and conditions remain *UI-only transcription*, never mislabeled as an API Detail or cast measurement.

Aegis of the Light has the explicit tooltip text **“No Global Cooldown”** plus a displayed 30-second cooldown. This is one claimed tooltip exception, not a measurement of the character's shared GCD, remaining cooldown or live usability. Missing tooltip cooldowns (Light's Benediction, Protector's Fury) remain null.

Distinct same-name ability IDs remain separate:

- **Building Fury:** three IDs, across Paladin/VoidKnight/Paragon.
- **Changing Role:** four IDs; **none** is assigned to a specific role-slot number.

## Audit and live boundary

The generator requires four exact source file hashes and fails closed on ID/name/soul/UI-section or tooltip-source mismatches. Its output excludes raw target, unit IDs, player stats, volatile cooldown snapshots and other live character fields. The focused verifier checks reproducibility, source tampering, privacy field exclusion, unknown/null preservation and the single explicit tooltip no-GCD assertion.

**RC-08 blocker unchanged:** The physical-PC v0.3.0 addon copy remains source-hash matched, but the saved RRECollectorData.candidateLookup receipt has not been observed; the prior latest and probe are intact. No game input, reload, restart, other addon or manual trainer list was required for RC-13. The next allowed check is a passive read after an operator-controlled normal SavedVariables flush. Once an actual v0.3 lookup result is available, compare it by **exact ID** against this atlas and preserve errors/negative-detail unknowns independently. Do not infer unlock/rank/timing from these static and UI sources.

The main spellcasting SC1 eligibility and SC3 queue/GCD milestones remain open.
