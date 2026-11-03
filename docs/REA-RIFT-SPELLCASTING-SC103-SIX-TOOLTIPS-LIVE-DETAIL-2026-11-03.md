# SC-103 continuation — Paladin Soul Tree screenshots versus current-client candidate Details

**November 3, 2026 UTC.** Physical-PC RIFT research, offline exact-ID join only. No new game commands, role changes, player input, SavedVariables writes, addon deployment or native code claims.

## Pinned sources and independent scopes

- Current-client candidate metadata: [RC-29 sanitized 353-ID atlas](REA-RIFT-SPELLCASTING-SC103-353-ID-DETAIL-ATLAS-2026-11-03.json), SHA-256 `5da0b32bc6fd67e86b883d44155c86fb5ff05cab1655b216ebed2fb4e5cd5fb7`. This is a prior physical v0.4.4 candidate lookup carried in the v0.4.8 saved root; the file modification time is **not** an API capture timestamp.
- Historical screenshot transcriptions and static-name/ID associations: [SC-103 six Paladin tooltips](REA-RIFT-SPELLCASTING-SC103-PALADIN-TOOLTIP-METADATA-2026-11-02.json), SHA-256 `d9008e8d64860858299ea975817263c8cd2373d81f703c448b7ea2c7c8a65c43`; [SC-102 screenshot receipt](REA-RIFT-SPELLCASTING-SC102-PALADIN-TOOLTIPS-2026-11-02.md), SHA-256 `04967c6f967c21049062b551ccf986436c63a3c66500095c3a4e3275df41d96d`. The November 1 UI shows level 45, Righteous Defender, Paladin 45 / Void Knight 15 / Paragon 0; these images **do not show exact modern ability IDs** and are not synchronous with candidate results.
- Reproducible, source-hash-pinned check: `node --test tools/verify-rift-sc103-ui-detail.mjs` — **3/3 PASS** (six exact-ID matches, five Detail results, four numerical cooldown comparisons). Independent Extra High read-only audit **APPROVE**, job `rre-sc103-six-tooltip-independent-audit-20261103-1`, exit 0; all five proposed next-case source claims and three soul totals cross-checked.

## Six exact-ID joins

All six UI-named candidates are absent from the preserved **69-ID API List**. Their ID associations originate in a historical source-hashed static Warrior file; the candidate Detail lookup supplies additional **current-client metadata**, not a screenshot-observed modern ID.

| UI name | Historical exact-ID candidate | Candidate Detail | Explicit `unusable` | UI cooldown → Detail cooldown |
| --- | --- | --- | --- | --- |
| Light's Benediction | `AFDD9D7E2A8F0E50B` | Returned | `true` | UI absent → Detail absent |
| Vengeful Decree | `A768CF3B63EE8D6ED` | Returned | `true` | 30 s → 30.0000019 s |
| Aegis of the Light | `AFA78C0D582C9F2E5` | Returned | `true` | 30 s → 30.0000019 s |
| Sanctuary | `A37397DC597DDAF03` | Returned | `true` | 90 s → 90.0000076 s |
| Protector's Fury | `A0E2112FD6FE262EE` | **No Detail** | **Missing** | UI variant tooltip; no API cooldown |
| Call of the Divine | `A411792DB5CF7E0E4` | Returned | `true` | 25 s → 25.0000019 s |

The four nonzero cooldown comparisons agree within 0.001 seconds (single-precision/API representation), providing corroborating **mechanics similarity**. They do **not** establish the current UI's runtime ID, same-session role allocation, eligibility, action-bar binding, or cast success. `No Detail` for Protector's Fury is not evidence of permanent locking, and a displayed Normal/Legendary variant is not a stable-ID match.

## Full three-soul lookup stratification (one original saved lookup)

| Static candidate soul | Prior listed, not re-queried | Detail returned | No Detail | Newly unlisted positive |
| --- | ---: | ---: | ---: | ---: |
| Paladin | 27 | 6, including 1 listed control | 1 | 5 |
| Void Knight | 7 | 23 | 3 | 23 |
| Paragon | 4 | 22 | 3 | 22 |
| **Total** | **38** | **51** | **7** | **50** |

Paragon had **0 points in the older screenshot**, yet 22 formerly unlisted Paragon candidate IDs returned Detail in the later save. This makes it especially important **not to classify a positive arbitrary-ID Detail response as learned or currently eligible**. Because allocation and Detail were observed at different times, this is a cross-source caution, not a same-frame proof about that specific allocation.

## Five deliberately contrasting exact-ID cases

These are **proposed evidence-gathering cases**, not verified locked/learnable statuses; each ID was checked against the canonical atlas.

| Case | Exact-ID evidence | Next discriminating observation |
| --- | --- | --- |
| **Protector's Fury** `A0E2112FD6FE262EE` | Paladin, no Detail; screenshot shows Normal/Legendary descriptions | Same-role visible variant/rank plus one bounded exact-ID Detail |
| **Building Fury (Paragon)** `A6F1D01307CF516B9` | Prior API-listed passive; original candidate lookup did not re-query | Same-session Paragon points plus API List membership; do not equate historical 0 points to current role |
| **Strike Like Iron** `A3FE90373692BAF3E` | Unlisted Paragon passive returned Detail, `unusable` absent | Visible talent rank in the same role; distinguish metadata exposure from actual activation |
| **Call of the Divine** `A411792DB5CF7E0E4` | Unlisted Paladin Detail, `unusable=true`; UI documents a Light's Shield condition | First establish allocation/known state, later isolate prerequisite-buff state without changing other context |
| **Aegis of the Light** `AFA78C0D582C9F2E5` | Unlisted Paladin Detail, `unusable=true`, 30s cooldown; UI says No Global Cooldown | First establish known/allocated state, later a separate controlled timing observation |

**Start with Protector's Fury** because its no-detail response distinguishes it from the five other visible Paladin tooltip candidates. Stop after any observation that fails to resolve an exact ambiguity; do not repeat a broad 96-ID scan.

## Ranked next observations and stop rule

1. **P1 — Current v0.4.9 runtime gate (RC-26).** Operator confirms a version-matched RIFT UI/Save and performs one reversible known-ability Pin → Undo with original eight slot IDs intact. This is separate from SC-103 spell eligibility; no RRE-owned game input is authorized by this report.
2. **P2 — One same-session role/ability comparison before any change.** Collect one bounded UI screenshot showing role/soul points and one fresh operator-triggered RRECollector List/Detail with the same game build and role, focusing on Aegis of the Light and Protector's Fury. Identify what the UI actually calls normal/legendary and whether those exact IDs are Listed, Detail-returned and flagged unusable. Do not infer rank thresholds from ability level alone.
   **Query-route prerequisite:** Existing RRECollector broad candidate refresh is not a proven single-ID probe route. Before this comparison, inspect the current commands and either qualify an already supported bounded exact-ID query or implement and test one small manual probe; do not repeat the 96-ID scan by default.
3. **P3 — Optional controlled role delta, only if Joey chooses an existing safe alternate preset.** Record before/after role allocation and the same exact-ID List/Detail flags, then restore the original role. A changed `unusable` or List status is evidence of **context sensitivity**, not by itself of learnability or actual cast success. Avoid respec, spell casting and bulk repeated probes.
4. **P4 — Keep stale-slot presentation separate.** An independent UI review found v0.4.9 labels a saved ID absent from the current known snapshot as “Empty”; defer any UI-source change until the installed v0.4.9 runtime gate is settled. Preserve saved IDs.

**Exit:** The six-ability source-bound crosswalk is accepted at offline metadata scope. SC-103 remains **blocked** for per-ability rank/learnability and castability until temporally aligned UI and API evidence exists.
