# RC-11 / SC-103 — Complete section map for 69 API-known RIFT abilities

**November 2, 2026. Owner:** RRE/REA manager. **Status:** accepted as a bounded *spellbook-section association*, not as a learned/rank/role-slot eligibility map.

## Decision-changing result

All **69** exact modern IDs in Atank's preserved physical-PC known-ability List/Detail snapshot are represented once in a categorized offline index.

| Source/UI section | Exact API-known IDs | Association method |
| --- | ---: | --- |
| Paladin | 28 | Exact ID in source-hashed Paladin static catalog |
| Void Knight | 7 | Exact ID in source-hashed Void Knight static catalog |
| Paragon | 4 | Exact ID in source-hashed Paragon static catalog |
| General | 7 | API name aligned to General screenshot tab |
| Role | 4 | Role-change API family aligned to four visible UI role entries **without slot assignment** |
| Ascended Powers | 5 | API name aligned to Ascended Powers screenshot tab |
| Patron Abilities | 14 | API name aligned to Patron screenshot tabs |
| **Total** | **69** | 39 exact static soul-ID joins + 30 name-to-tab associations |

[Machine-readable 69-ID section map](REA-RIFT-SPELLCASTING-SC103-KNOWN-UI-SECTIONS-2026-11-02.json) keeps each exact ID, name, section, proof method, and explicitly null role slot. It also records the full source hash and image manifest.

The four **Changing Role** entries have distinct IDs in the current API snapshot. The visible Role tab instead gives role-slot display names (Beast/Warlord, Righteous Defender, Role 3, Role 4). Neither their order nor any modern ID-to-slot mapping is proven by the screenshots. All four are section-classified but intentionally **not assigned** to slot numbers or names.

## Source provenance and negative prerequisite probe

- Current-known exact IDs and source-soul joins: accepted [SC-103 69↔96 crosswalk](REA-RIFT-SPELLCASTING-SC103-EXACT-ID-CROSSWALK-2026-11-02.json), SHA-256 00c1cc8896591bd2c7dfedf0a831f689179fbfb0ac5369dcc63cfcf8b5ec79f5. The existing RRECollector SavedVariables snapshot and full source catalog were **not recaptured**.
- Section UI reference: accepted [SC-102 screenshot audit](REA-RIFT-SPELLCASTING-SC102-UI-SPELLDUMP-2026-11-02.md), SHA-256 67f0d6387c0332a096be61c2defdc69797ef05921692445fa2b61b4da7d709ab. All **six** relevant original JPGs were independently rehashed in place; all matched. The screenshot originals are not committed or embedded.
- Three original disabled ProjectAbilityBook Warrior files were SHA-matched: Paladin e4af0446..., VoidKnight b8dd0a75..., Paragon 67981693.... Their per-ability leaf properties are exactly **Icon** and **ID**; a bounded search yielded **zero** occurrences of rank/level/points/prerequisite terms. They do not encode rank requirements or prove eligibility. Two separate bounded checks (sample and three-file property census) closed this route without a source rewrite.
- Exact original game/API builds remain distinguished. This is a join between a physical-PC saved known-list and historical/static UI/addon sources; the UI images do not display modern stable IDs.

## Reproduce without game input

From C:\work\rre:

    node tools/build-spellbook-section-map.mjs
    node --test tools/verify-spellbook-section-map.mjs

The generator reads only the two pinned tracked source files and produces sanitized JSON on stdout, with no private player, target or stats dump. It checks each known ID and all seven section counts, rejects unknown names or broken static IDs, and requires distinct unresolved role IDs. The focused tests passed **3/3**. The checked-in JSON is a deterministic snapshot of this generator output.

## Boundaries and next milestone

The name-to-section associations for non-soul abilities are not screenshots of stable IDs. The section map says **which spellbook group corresponds to a name**, not which character role slot, rank, prerequisite, current usability or action-bar binding is operative. The **57 source candidates absent from the API-known List remain unknown**. The evidence cannot by itself determine a global cooldown or server cast success.

**RC-08 remains blocked** on the first normal persisted v0.3 RRECollector candidateLookup receipt. Once available, compare its exact-ID responses to this section map and the 69↔96 crosswalk without changing the API-known/unknown boundary. No additional addon, RIFT input, client restart, or trainer dialogue was required for RC-11.
