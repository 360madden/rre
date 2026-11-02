# RC-14 — full 11-source Warrior static ability reference

**Date:** November 2, 2026 (physical-PC source evidence)  
**State:** Accepted at **disabled source inventory** scope only; no new current-client Detail result.  
**Owner:** RRE/REA manager  
**Machine data:** [11-soul static reference](REA-RIFT-SPELLCASTING-SC103-WARRIOR-ALL-SOULS-STATIC-2026-11-02.json)  
**Read-only rebuild:** node tools/build-warrior-static-reference.mjs (JSON to stdout; accepts an optional explicit Warrior source directory)  
**Focused verification:** node --test tools/verify-warrior-static-reference.mjs — 3/3 passed.

## Decision-changing coverage

The previous v0.3 RRECollector candidate catalog deliberately covered Atank's **three selected Warrior souls** (Paladin, VoidKnight, Paragon). A bounded read-only inspection of the already installed, disabled ProjectAbilityBook addon found **11 Warrior source files**. Parsing all 11 with the existing RRE literal-only Lua decoder produced:

| Source comparison | Exact IDs |
| --- | ---: |
| Source rows and **unique IDs** across 11 Warrior Lua files | **323** |
| Already in the prior three-soul static catalog | 96 |
| Additional source-only IDs from the other eight souls | **227** |
| Matching Atank's preserved 69 API-listed IDs | 39 |
| Source IDs not listed in Atank's 69 | 284 |
| Atank API-listed IDs outside all 11 Warrior source files | 30 |
| **Distinct union: all Warrior source IDs + prior API-listed IDs** | **353** |

| Warrior soul | Static IDs | In preserved Atank API list |
| --- | ---: | ---: |
| Beastmaster | 36 | 0 |
| Champion | 28 | 0 |
| Liberator | 27 | 0 |
| Paladin | 34 | 28 |
| Paragon | 29 | 4 |
| Reaver | 22 | 0 |
| Riftblade | 29 | 0 |
| Tempest | 30 | 0 |
| VoidKnight | 33 | 7 |
| Warchanter | 26 | 0 |
| Warlord | 29 | 0 |
| **Total** | **323** | **39** |

Each static record preserves modern-format exact ID, source display name, named soul, source category and decoded icon path; it records original-96 membership, prior-69 API List membership, and explicit unknown role-slot/unlock/usability. No legacy source ID is silently upgraded to a runtime-learnable or castable status.

### Same-name IDs must not collapse

The old three-soul source showed three IDs called **Building Fury**. Across the full 11-soul source, **nine separate Building Fury IDs** exist (Beastmaster, Champion, Paladin, Paragon, Reaver, Riftblade, Tempest, VoidKnight, Warlord). They are distinct exact IDs, not one cross-soul ID. There were **zero duplicate exact IDs** across the 323 entries. The four prior-known Changing Role IDs are separate API records outside these source files.

### Source and replay boundary

- All 11 source Lua file byte hashes are pinned individually in the machine JSON. The three previously accepted Warrior source files match their exact prior hashes.
- The extractor reuses the existing bounded, literal-only SavedVariables Lua parser after changing only the expected assignment name in memory; it never executes addon Lua.
- The prior 96 static records and RC-13 atlas are pinned by SHA, checked for exact-ID/name/soul/category equivalence, and left unchanged. The earlier catalog kept literal doubled Lua backslashes in icon strings; RC-14 normalizes that representation for comparison and exports decoded icon paths.
- The new reference can be regenerated while the disabled addon source is available on the physical PC. It does not reproduce source Lua files or modify their installation.
- The verifier checks byte-for-byte reproducibility, malicious/changed source failure, prior-catalog and atlas mismatch rejection, 323 unique IDs, nine Building Fury identities, and absent private/player/target state.

**Do not change installed RRECollector v0.3 yet.** Its 96 candidate canaries are still awaiting an actual saved candidateLookup result. Broadening live probes to all 323 IDs now would add API traffic without validating the current read-only canary path, and would confound the installed-source/saved-receipt gate. If that receipt arrives, join by exact ID against the three-soul RC-13 and all-soul RC-14 references; keep negative Detail responses inconclusive rather than claiming locked or unlearnable.

SC-103 role/rank and eligibility, RC-08 live lookup, and SC3 timing/queue remain unproven. No game input, reload, client process action, or addon deployment was performed in RC-14.
