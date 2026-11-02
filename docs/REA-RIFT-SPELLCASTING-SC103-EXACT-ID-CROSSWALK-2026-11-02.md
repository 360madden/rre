# SC-103 offline exact-ID crosswalk — current API-known vs Warrior static catalog

**Date:** November 1/2, 2026 across local/UTC clocks. **Owner:** REA manager. **Milestone:** RC-09, accepted at **offline source-join scope only**; SC-103 rank/eligibility still open.

## Result

A reusable, read-only parser now extracts **exactly 69** `RRECollectorData.latest.abilities` from the preserved Atank character SavedVariables file **without executing Lua** or copying private player stats. The extracted known-ability details are joined by exact `lookupId` to the 96 IDs in the source-hashed disabled ProjectAbilityBook Warrior files. Both inputs are independently auditable.

| Warrior soul | Static candidates | Exact IDs in Atank's known 69 | Static IDs absent from known 69 |
| --- | ---: | ---: | ---: |
| Paladin | 34 | 28 | 6 |
| Void Knight | 33 | 7 | 26 |
| Paragon | 29 | 4 | 25 |
| **Total** | **96** | **39** | **57** |

**Zero** mismatches were found among the 39 static exact IDs and their current-known API detail names. The remaining **30** known API abilities are outside these *three* source files; do not assume they are unattainable or classify their spellbook section without further source evidence.

One static duplicate-name group is important for the SC-103 role/variant problem:

| Static name | Soul | Exact stable ID | In known 69? |
| --- | --- | --- | --- |
| Building Fury | Paladin | `A6ACAFC287CF516B9` | Yes |
| Building Fury | Void Knight | `A768776D17CF516B9` | Yes |
| Building Fury | Paragon | `A6F1D01307CF516B9` | Yes |

These are three **distinct IDs attached to three soul source entries**, not one ID to deduplicate and **not proof of three ranks**. Exact ID, source soul and detail should remain linked independently.

## Durable outputs and extraction

- [Machine-readable 96-entry crosswalk](REA-RIFT-SPELLCASTING-SC103-EXACT-ID-CROSSWALK-2026-11-02.json) includes source soul/category/icon, exact known membership, full whitelisted current-known scalar Detail fields where present, exact-name match or null, and the 30 other known API records. The absent 57 have **no fabricated current Detail fields**.
- [Source static 96 IDs](REA-RIFT-SPELLCASTING-SC103-WARRIOR-STATIC-ABILITIES-2026-11-02.json) retains disabled source file paths and SHA-256 hashes; unchanged prior known SavedVariables SHA-256 is `242259d4f20709574b45676ed6a6ebdaef64e5a8d99b22341abb5291bccdfb12`. The `latest` record's addonVersion is `0.1.0`, although the file's root metadata was subsequently updated by v0.2.
- `tools/read-rrecollector-saved.mjs`: dependency-free, read-only subset parser for character-scoped `RRECollectorData` Lua **literals**. It imposes byte/depth/value limits, rejects expressions and duplicate keys, accepts saved escaped physical newlines, and emits a sanitized exact-ID JSON crosswalk to stdout. It performs no file writes, input, polling, or game calls.
- `tools/verify-rrecollector-saved.mjs`: **3 focused tests passed** (0/false and multiline retention, rejection of unsafe Lua, exact-ID source crosswalk). A separate real-file read-only integration completed with **69 known / 96 static / 39 matched / 57 unlisted / 30 outside**, zero mismatched names.

## Truth boundary and next gate

This is an **offline crosswalk** using prior known API data plus a potentially stale disabled source list. The absence of 57 IDs from `Inspect.Ability.New.List` is not an unlock-level, trainer, rank, readiness, or castability predicate. The 30 known-but-nonstatic IDs likewise need distinct classification.

RRECollector v0.3.0 remains **9/9 physical-PC source/install hash matched** and includes an opportunistic, bounded `Inspect.Ability.New.Detail(id)` candidate lookup at the next normal load. Read-only process inspection observed a new RIFT PID 17412 started at **2026-11-02T04:36:24Z**, four seconds after the saved v0.2 root file's last write; therefore the absence of a saved v0.3 `candidateLookup` in that file does not establish a current-session addon-load failure. Do not force UI reload or enter game commands under RRE authority. **RC-08 remains blocked on a normal SavedVariables flush or independently observed addon error**, followed by comparison to this crosswalk. The parser can ingest that future `candidateLookup` without another manually transcribed list.

**No Game input, process manipulation, client addon beyond already approved RRECollector, external app install, or unrelated repository changes were performed.**
