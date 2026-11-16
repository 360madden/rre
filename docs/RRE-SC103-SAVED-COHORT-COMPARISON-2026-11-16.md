# SC-103 — 0.4.20 saved-known cohort vs historical 69 (offline only)

**Date:** November 16, 2026, ~11:45 EST. **Owner:** single RRE manager on independently verified AMD-DESKTOP (Workbridge 0.16.5-dev; `hostname.exe` job `RRE_hour_20261116_1141_host_verify` exit 0). **Scope:** existing RRECollector SavedVariables and committed historical Warrior crosswalk read-only; no game/process, UI, reload, addon, RR2/REA, or cross-host action.

## Source identities and method

- Original existing RRECollector character SavedVariables: 68,055 bytes, SHA-256 `1165680f8d9fb09c9e22ab3aeb6fde8c223551ba3846dfec9d55a1c22f969ad3`; root/latest addonVersion `0.4.20`, previous source receipt [RC-30 saved revision](RRECOLLECTOR-RC30-SAVED-REVISION-2026-11-16.md). The source was read using the existing stable-read literal Lua parser and SHA-gated **before** extracting any data. Original source mtime is 2026-11-16T15:20:22.890Z, not a proven in-game event time.
- Historical 69-known cohort: [November 2 exact-ID crosswalk](REA-RIFT-SPELLCASTING-SC103-EXACT-ID-CROSSWALK-2026-11-02.json), SHA-256 `00c1cc8896591bd2c7dfedf0a831f689179fbfb0ac5369dcc63cfcf8b5ec79f5` (retained snapshot version `0.1.0`). Historical static 96-ID Warrior catalog: [source](REA-RIFT-SPELLCASTING-SC103-WARRIOR-STATIC-ABILITIES-2026-11-02.json), SHA-256 `c48797e3cde754bbc8ce6812eb9dbfbe2549c1d271efde6468bfae10fbe6a3ae`.
- Read-only job `RRE_hour_20261116_1141_SC103_newsaved_crosswalk_ro`, exit 0, reused `parseSavedLuaBytes` and `buildAbilityCrosswalk`. Independent job `RRE_hour_20261116_1141_SC103_independent_cohort_compare_ro`, exit 0, did **not** reuse the crosswalk builder: it compared the saved current ID set directly against historical sets and independently checked known/static intersection, names, and the one requested candidate status. Both jobs verified original SHA values and returned only bounded aggregate/ability facts, not player metadata.

## Source-qualified findings

| Check | Historical 0.1.0 cohort | Current retained 0.4.20 cohort |
| --- | ---: | ---: |
| Known API ability IDs | 69 | **55** |
| Known matching the 96-ID Warrior static catalog | 39 | **39** |
| Known outside the Warrior static catalog | 30 | **16** |
| Static catalog IDs not in current known | 57 | **57** |
| Known/static exact-name disagreements | 0 | **0** |

- The entire current 55-ID set is a **subset** of the historical 69 IDs: **55 retained, 14 absent, zero newly introduced**. **All 14 absent IDs belonged to the historical *outside-static-catalog* group**; zero of the 39 previously listed Paladin/Void Knight/Paragon static IDs disappeared. By soul, the static-known numbers remain **Paladin 28/34, Void Knight 7/33, Paragon 4/29**.
- Source-listed `Protector's Fury` (`A0E2112FD6FE262EE`, Paladin) is **not** in the 55 known IDs; the separately retained `candidateLookup` still labels it `no-detail`. Candidate lookup version is **0.4.14**, not the new `latest` version 0.4.20. There is **no new modern Legendary variant ID** from this offline comparison.
- The new latest 0.4.20 snapshot passes the existing *offline structural* readiness gate, with `freshnessVerified=false`, `processBuildVerified=false`, `eventDeliveryVerified=false`, and `eventComparisonReady=false`.

## Decision and stop boundary

This is a **saved-revision cohort change**, not proof that 14 abilities were removed from the game, that a particular role or character changed, or that any spell is eligible, unlearned, Legendary, rank-qualified or castable. Saved rows from different times do not establish the live process, simultaneous role state, new RIFT build or the origin of the writer. A `no-detail` candidate is not a negative eligibility verdict. **SC-103 remains blocked** on the independently evidenced selected variant/current rank and same-trial UI/API identity; **RC-30 v0.4.10 operator acceptance remains separate and pending**.

**Next actionable evidence:** only when independently authorized and owner-scoped, correlate a *same-trial* current selected Legendary/Normal Protector's Fury UI state, role/rank, and bounded exact-ID Detail/List response; preserve screenshots, versions and source hashes. Do not rerun the unchanged full catalog or expand speculative native scans. No RR2 feed update is warranted.
