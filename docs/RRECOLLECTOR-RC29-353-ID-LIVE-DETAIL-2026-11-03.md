# RC-29 / SC-103 — 353-ID atlas with current-client candidate Detail evidence

**Date:** November 3, 2026 UTC. **Target:** physical-PC RIFT Live, character-scoped prior RRECollector SavedVariables. **Scope:** offline, read-only literal-Lua parsing and a source-hash-bound JSON export. No game input, reload, new ability capture, or VM use.

## Accepted union and explicit-ID responses

| Set | Count | Interpretation |
| --- | ---: | --- |
| Historical Warrior static IDs across 11 soul files | 323 | Source candidates only |
| Previously API-listed exact IDs | 69 | Preserved earlier current-role List/Detail capture |
| Exact-ID union, deduplicated | **353** | Current API listed plus historical source possibilities |
| Original three-soul candidate IDs with saved lookup entries | 96 | 39 prior listed; 57 previously unlisted |
| Candidate Detail returned | 51 | One listed control, **50** previously unlisted |
| Candidate Detail absent | 7 | Neither permanent lock nor unlearnability proven |
| Already-listed and not independently queried in this lookup | 38 | Prior API List evidence remains |
| Duplicate name groups preserved | 2 | Distinct exact IDs are never merged by name |

## New current-client field observation

Of the **50 formerly unlisted IDs that returned Detail**, **49** have the explicit boolean `unusable=true`. The remaining one, **Strike Like Iron** (ID `A3FE90373692BAF3E`), has `passive=true` and no `unusable` field. No returned unlisted record has an explicit `unusable=false` value. Other field presence among the 50: 32 contain a `cooldown` value, 23 `rangeMax`, 49 `costPower`, all 50 names and descriptions; none contains `outOfRange` or `currentCooldownRemaining`.

This is **a timestamp/context-bound API response**, not proof of an invariant lock, learnability rule, current cast outcome or future eligibility. Explicit `true`, `false`, zero, and missing fields stay distinct in the machine atlas. The summary's `currentlyCastable`, `learnableNow` and `unlockState` remain `unknown`.

## Reproducibility

- Generator: `tools/build-rift-ability-atlas-live.mjs`
- Focused test: `tools/verify-rift-ability-atlas-live.mjs` — **4/4 PASS** (353-ID union, false/zero/absent preservation, explicit runtime target privacy sentinels in candidate/prior Detail, reject mismatched or duplicate IDs). Decoder `tools/verify-rrecollector-saved.mjs` — **4/4 PASS**, including explicit numeric Lua entries and `target` exclusion.
- Machine atlas: `docs/REA-RIFT-SPELLCASTING-SC103-353-ID-DETAIL-ATLAS-2026-11-03.json`
- Sanitized atlas SHA-256: `5da0b32bc6fd67e86b883d44155c86fb5ff05cab1655b216ebed2fb4e5cd5fb7` (255,210 bytes). A recursive key audit found **zero target, targetUnit, ownerUnit, player, account, or email fields**. The initial uncommitted export contained two runtime `detail.target` keys; that draft and its temporary duplicate were recoverably deleted before this canonical JSON was regenerated.
- Source SavedVariables SHA-256: `bf6f34adac5256f2875ee787d549f7f93d7f5942959bf1c4c8dedfa4979bf276` (physical v0.4.8 saved root; lookup originally recorded by v0.4.4). The source filename/account path, player/target IDs and private stats are not copied into the generated atlas.
- Each static catalog, prior 126-ID atlas, exact generator script and imported saved-data decoder SHA-256 is recorded in `sourceIndex`; the source saved-data SHA is pinned without copying its private filename/account path. A second export-level scalar-field whitelist rejects unknown fields even if the lower-level decoder later changes. Output creation uses no-overwrite mode.
- Independent Extra High reviewer: **APPROVE** after read-only artifact audit job `rre-rc29-independent-readonly-audit-20261103-1` (exit 0). Verified source inputs, 353 unique exact IDs, no target/player/unit fields or runtime-unit identifiers, no returned-Detail `id` mismatch, and missing passive flags. Final syntax/JSON checks, `git diff --check`, and **8/8 combined Node tests** passed.

The next discriminating SC-103 question is how the explicit current `unusable` flag changes with a controlled role/soul/rank/context difference, not a repeat of the same 96-ID Detail query. SC-103 eligibility is **still blocked** because rank thresholds and learnable/locked state are not API-proven by these records.
