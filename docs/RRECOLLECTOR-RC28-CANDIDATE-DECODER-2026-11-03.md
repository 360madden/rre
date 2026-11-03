# RC-28 — Numeric-keyed candidate SavedVariables decoder repair

**Date:** November 3, 2026 UTC. **Scope:** offline RRE/SC-103 decoding only; no addon installation or game input.

## Defect and correction

`tools/read-rrecollector-saved.mjs` already normalizes both implicit Lua arrays and tables whose entries have explicit integer keys through `asArray()`. The current-known `latest.abilities` path used this helper, but `candidateLookup.entries` previously required `Array.isArray`. Lua text such as `entries = { [1] = {...} }` is decoded to an object, so a legitimate candidate response could be silently omitted from the crosswalk even with `liveCandidateLookupSaved=true`.

The candidate branch now uses `asArray(saved?.candidateLookup?.entries)` and ignores malformed non-object entries. The existing 96-ID exact-ID join and unknown eligibility classification remain unchanged.

## Evidence and checks

- `node --test tools/verify-rrecollector-saved.mjs`: **4/4 pass**, including a new implicit-array versus explicit `[1]` numeric-key regression and retained zero/false values.
- `node tools/verify-rrecollector-candidates.mjs`: **6/6 pass** after the UI's shorter read-only legend was updated in its matching structural assertion.
- The fix is a decoder capability correction, **not** proof that a prior real host export was wrong. A fresh read of a source-hashed physical SavedVariables file is needed to quantify candidate records in a merged atlas.
- The physical Atank candidate API result remains **50 returned Details / seven no-detail among 57 formerly unlisted IDs; zero lookup errors**, per RC-08. Detail does not imply learned, learnable, unlocked, or castable.

## Next discriminator

Use the source-hashed real RC-08 SavedVariables representation and 353-ID Warrior/static+known reference to build one exact-ID augmented atlas, retaining original raw entry status, source times, missing-versus-false/zero, and unknown eligibility. No broad API rescan is justified.
