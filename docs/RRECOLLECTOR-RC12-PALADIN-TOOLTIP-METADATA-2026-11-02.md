# RC-12 — Six source-backed, unlisted Paladin ability tooltip records

**November 2, 2026. Owner:** RRE/REA manager. **Status:** completed as structured **UI-tooltip evidence** only; not a current unlocked spellbook or GCD measurement.

## Delivered

[Six-entry machine-readable tooltip dataset](REA-RIFT-SPELLCASTING-SC103-PALADIN-TOOLTIP-METADATA-2026-11-02.json) pairs six original physical-PC Soul Tree tooltip names with exact *static* ProjectAbilityBook Paladin candidate IDs and faithfully typed visible mechanics. The source screenshot is never represented as if it printed a modern ability ID. The existing RRECollector 69-known and 96-static datasets are not modified.

| Tooltip name | Static candidate ID | Visible Power | Visible cooldown | GCD text |
| --- | --- | ---: | ---: | --- |
| Light's Benediction | AFDD9D7E2A8F0E50B | 20 | Not shown / unknown | Not shown |
| Vengeful Decree | A768CF3B63EE8D6ED | 22 | 30s | Not shown |
| Aegis of the Light | AFA78C0D582C9F2E5 | 10 | 30s | **No Global Cooldown** |
| Sanctuary | A37397DC597DDAF03 | 20 | 90s | Not shown |
| Protector's Fury | A0E2112FD6FE262EE | 10 | Not shown / unknown | Not shown |
| Call of the Divine | A411792DB5CF7E0E4 | 20 | 25s | Not shown |

The JSON additionally retains melee/range labels, visible damage examples (where shown), short mitigation/healing/proc descriptions, Light's Shield prerequisite text for Call of the Divine, and separate Normal/Legendary tooltip *descriptions* of Protector's Fury. Unshown cooldowns and GCD labels remain **null**, never invented zero or false. Displayed numeric damage/heal examples are character-context tooltip values, not general-purpose scaling formulas.

## Source and proof tier

- Six original JPGs: filenames 2026-11-01_210639.jpg, 210642.jpg, 210645.jpg, 210653.jpg, 210657.jpg, 210700.jpg under the user's existing RIFT Screenshots directory. All **6/6 SHA-256 hashes were rechecked unchanged** against [SC-102's original screenshot audit](REA-RIFT-SPELLCASTING-SC102-PALADIN-TOOLTIPS-2026-11-02.md), SHA-256 04967c6f967c21049062b551ccf986436c63a3c66500095c3a4e3275df41d96d. Neither raw screenshots nor private stats were added to RRE.
- All six names exactly pair with unique IDs in the static Paladin source SHA-256 e4af04464201adbc5cbae9d07cab0e36a9da616b5b30abd466f8ca44c8f92f28; all six IDs are **absent** from the preserved 69 known via [SC-103 exact-ID crosswalk](REA-RIFT-SPELLCASTING-SC103-EXACT-ID-CROSSWALK-2026-11-02.json), SHA-256 00c1cc8896591bd2c7dfedf0a831f689179fbfb0ac5369dcc63cfcf8b5ec79f5.
- Source labels such as Instant, AE, and No Global Cooldown are **UI-text observations**. The static ID associations are exact-name source joins, not same-frame live Detail responses. No rank, unlock, learned, castable, individual role or slot fact is inferred.

**SC-3 consequence:** at least one visible Paladin tooltip specifically advertises **No Global Cooldown**. A universal assumption that every ability incurs the same GCD contradicts this text; actual shared-lockout transitions and the Full/Short/None queue configuration remain unmeasured. Aegis is also **not in the current known List**, so it is not an observed usable probe.

## Replay and limits

From C:\work\rre:

    node --test tools/verify-paladin-tooltip-metadata.mjs

The source-hash and exact-ID verifier passed **3/3**. It rejects static-ID mismatches, invented current-known membership, absent screenshot provenance, extra unverified no-GCD claims, or unshown cooldowns represented as zero. No Lua addon change, new user screenshot, game control, native attach, restart, or external dependency was needed.

**Next gate:** RC-08 still awaits an actual saved v0.3 candidateLookup. That result can be joined to these six names/IDs, but negative Detail output must not be interpreted as a rank or lock condition.
