# RC-10 — Source-hashed, sanitized interim spellcasting evidence replay

**November 2, 2026. Owner:** RRE/REA manager. **Result:** completed as a reproducibility *preparation* milestone, not SC-601/SC-602 completion. The latter still depends on missing current live/queue/native evidence.

## Delivered

- tools/replay-spellcasting-evidence.mjs produces a deterministic, read-only JSON export on stdout from four explicitly pinned, accepted source artifacts. It also independently rehashes the 14 reports indexed in the SC-604 mechanism model.
- tools/verify-spellcasting-replay.mjs uses Node's built-in test runner: deterministic replay and no raw unit IDs; rejection of mixed old/current builds; rejection of exact-ID crosswalk corruption and modified event attribution.
- **No raw SavedVariables contents, player identifiers, unit/target IDs, resources, stats, commands, executable bytes, or game input** are included in the export. The script reads only tracked RRE evidence; no dependencies are installed and no files are written.

Run from C:\work\rre:

    node tools/replay-spellcasting-evidence.mjs
    node --test tools/verify-spellcasting-replay.mjs

The first command writes JSON to **stdout** (redirect it only if an operator chooses to save a file). It deliberately fails closed on source hash drift instead of silently accepting changed research documents. When new live capture changes the accepted snapshots, explicitly review and re-pin the inputs.

## Verified independent cross-checks

| Predicate | Replay result |
| --- | --- |
| Original SC-604 indexed reports | 14/14 exact SHA-256 matches |
| Source-hashed static Warrior candidates | 96, in three souls |
| Current API-known entries represented | 69: 39 exact static overlaps and 30 known outside |
| Static absent from current API-known List | 57, **not** a lock/unlock verdict |
| Three Building Fury source records | Three distinct exact IDs across Paladin, Void Knight, Paragon |
| Historical Light's Decree trial 1 | One selected-target Dodge; zero selected-target ability damage |
| Historical Light's Decree trial 2 | 402 selected-target ability damage; 726 to other targets |
| Historical Aggressive Block raw modern-ID match | False; later normalized replay is not substituted |
| Source/build boundary | Historical RR2 capture SHA 7c356c9d..., different from current physical client SHA 1935a05c... |
| Focused replay tests | **3/3 passed** |

The game-client build hashes are retained in full in the JSON export. SC-604's indexed research reports are rehashed from files in this repository; hashes of three original disabled ProjectAbilityBook Warrior Lua files are **catalog-attested only**, because those original files are outside this RRE tracked research set. The old on-disk character RRECollector.lua is not re-read by this script: its source SHA is inherited from the previously accepted exact-ID crosswalk.

## Unresolved and next gate

This is a deterministic interim evidence selection, not a synthetic cast test or a live server trace. An identical historical ability ID and present known-ability name do **not** demonstrate current-build cast behavior. Shared GCD, current queue selection and label mapping, successful native cast submission, server acceptance, and rank/learnability remain unverified.

**RC-08** is still the direct critical path: inspect candidateLookup only after the existing v0.3 addon produces a real SavedVariables receipt through the operator's normal RIFT UI lifecycle. **SC-601/SC-602 final integration** remain unclosed. SC-306 and SC-402 were reviewed and remain parked without new discriminating UI/readiness evidence.

Source changes: two new offline tools and this report; separate documentation/register updates. No change to installed addon, RIFT, RiftReader2, Workbridge, VMware labs, or native settings.
