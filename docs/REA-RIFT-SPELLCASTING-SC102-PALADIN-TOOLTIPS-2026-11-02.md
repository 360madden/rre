# SC-102 — Named Paladin Soul Tree tooltips versus current API-known abilities (2026-11-02)

**Decision: ACCEPT bounded SC-102/RC-04 reconciliation** at a documented coverage limit. Eleven additional source-hashed physical-PC screenshot originals identify **six named Paladin ability tooltips** absent from the current Atank 69-ID RRECollector/SpellDump catalog and **five unselected Paladin branch talents**. Each ability name has an exact-name candidate ID in an installed *static* ProjectAbilityBook Paladin file, but **no screenshot displays a live stable ID or explicit per-ability unlock threshold**. Do not promote the six IDs to live API-known, learned, currently usable, eligible-now or specifically locked status. A Warrior trainer dialogue is unnecessary.

## Source boundaries

- User supplied eleven screenshots named `2026-11-01_210619.jpg` through `2026-11-01_210700.jpg`. Read-only physical-PC host check `rre-sc102-paladin-tooltip-origin-20261102-a1` **exit 0** found **11/11 same-named original JPGs** under `C:\Users\mrkoo\OneDrive\Documents\RIFT\Screenshots\`; sizes and SHA-256 are listed below. Attached chat images may be transformed derivatives; no byte identity is asserted and no raw images were committed.
- Images show **Atank, level 45**, **Righteous Defender**, **Paladin 45 / Void Knight 15 / Paragon 0**, **60 points spent / 0 remaining**. These are host-local UI observations, not simultaneous process/PE/role-slot-and-ID runtime proof. See [earlier 14-image and SpellDump receipt](REA-RIFT-SPELLCASTING-SC102-UI-SPELLDUMP-2026-11-02.md).
- Preserved Atank current RRECollector SavedVariables SHA-256: `242259d4f20709574b45676ed6a6ebdaef64e5a8d99b22341abb5291bccdfb12`, API build `STABLE-1-1178-A-1256632` (operator-attributed physical-PC capture), **69 exact current-list abilities**, independently matched by SpellDump v2.1.0. The runtime probe found no `Inspect.Soul.List/Detail` or `Inspect.Action.List/Detail` at the tested exact API paths.
- Static host `projectabilitybook.disabled/Callings/Warrior/Paladin.lua` SHA-256 `e4af04464201adbc5cbae9d07cab0e36a9da616b5b30abd466f8ca44c8f92f28` supplies *candidate* soul ability names/IDs, **not current learned or unlock state**. Read-only crosswalk job `rre-sc102-paladin-static-known-crosswalk-20261102-a1` **exit 0** confirmed all six exact name/ID pairings in static file and **zero** matching candidate ID strings anywhere in the preserved current RRECollector SavedVariables.

## Original physical-host screenshot manifest

| Original JPG filename | Bytes | Host SHA-256 | UI tooltip |
| --- | ---: | --- | --- |
| `2026-11-01_210619.jpg` | 1,493,287 | `816e6953a0838d46d1f01d41bbcb2e04a71a87cb604cdb1f5d4d9a103dcf5e07` | Front Line Training, Rank 0/2 |
| `2026-11-01_210624.jpg` | 1,493,105 | `db9affbc53e36e9f921499a99552ca573893ed94e4a9884e82a8952ddd1289ae` | Invigoration, Rank 0/2 |
| `2026-11-01_210627.jpg` | 1,493,113 | `bc3471453981920a0f4386fff71042036c633f93b1f8dc8400e417f558dc4b38` | Divine Grace, Rank 0/2 |
| `2026-11-01_210631.jpg` | 1,482,557 | `b3a254cf7583a1ffcb60961006dd8f3eace21e73fa0ce4ae0fe42ce0ba9cddbc` | Resolution, Rank 0/2 |
| `2026-11-01_210634.jpg` | 1,482,323 | `c0509664722a98121e9692aac2947bc161bca19bf138eb7d5750d6267d1c7b54` | Vengeful Wrath, Rank 0/5 |
| `2026-11-01_210639.jpg` | 1,476,342 | `01146c28f7b070130bbeed2daa70b544b42ac185337dd8042a6f552e14b7212d` | Sanctuary |
| `2026-11-01_210642.jpg` | 1,475,312 | `124cb46b8ca4b7fc1eec14fa8eeecab34fa50ce862c2b305d7840a53d7c5b1bc` | Vengeful Decree |
| `2026-11-01_210645.jpg` | 1,476,287 | `620a62e4a061c52ba0c8e5509cb8a6477d246dddd8a3385aeffd9965f5decedc` | Call of the Divine |
| `2026-11-01_210653.jpg` | 1,466,845 | `60b5d8272d4bf5aa9c1a35782f61ff9849a5cc97b1926a48f69098b69bdafbd5` | Light's Benediction |
| `2026-11-01_210657.jpg` | 1,472,404 | `8e55e970c30aab7cd242a5175efd8dd1969b626859ffe2229781f28ba263103a` | Aegis of the Light |
| `2026-11-01_210700.jpg` | 1,483,076 | `f5ff8c9b10e5ce00c34046fe6862f8259ce66089191979c7b6ad90e2a444f03d` | Protector's Fury, Legendary/Normal variants |

## Six named Paladin soul ability crosswalks

| UI tooltip name | Static candidate ID | JPG suffix | Visible tooltip mechanics | In preserved 69-ID API list? |
| --- | --- | --- | --- | --- |
| Light's Benediction | `AFDD9D7E2A8F0E50B` | `210653` | Instant melee-weapon Life damage, 20 Power; reduces damage taken 7% for 15s | **No** |
| Vengeful Decree | `A768CF3B63EE8D6ED` | `210642` | AE damage, 22 Power, 20m, 30s cooldown, up to five enemies | **No** |
| Aegis of the Light | `AFA78C0D582C9F2E5` | `210657` | Instant self-buff, 10 Power, no GCD, 30s cooldown, short mitigation and healing | **No** |
| Sanctuary | `A37397DC597DDAF03` | `210639` | Area protection, 20 Power, 30m, 90s cooldown, 30% mitigation for 4s | **No** |
| Protector's Fury | `A0E2112FD6FE262EE` | `210700` | Instant melee-weapon self-buff, 10 Power, separate Normal/Legendary tooltip descriptions | **No** |
| Call of the Divine | `A411792DB5CF7E0E4` | `210645` | AE taunt/teleport under Light's Shield condition, 20 Power, 30m, 25s cooldown | **No** |

**Proof-tier rule:** Names and mechanics are **direct UI-visible**; candidate IDs are **source-hashed static-addon associations**, not screenshot-extracted/live runtime IDs; absence means **not found in the preserved exact API-known catalog**. Neither absence nor character level nor visual allocation alone proves whether each ability is future-gated by character level, soul allocation, role, rank/variant or something else. Tooltip cooldowns are UI descriptions, not independently returned API fields for these absent IDs.

**Five branch talents with explicit zero ranks:** Front Line Training **0/2**, Invigoration **0/2**, Divine Grace **0/2**, Resolution **0/2**, Vengeful Wrath **0/5**. Rank zero qualifies **unallocated in this visible role**, not a specific current API ability ID or a permanent lock.

## K/L/F/U/B decision and stop rule

| Dimension | Qualified result |
| --- | --- |
| **K — API-known** | 69 exact current-list IDs; **six named visual candidates absent**, with six static crosswalks |
| **L — learnable/eligible now** | **Unknown** for six; no explicit learn-now or purchase predicate shown |
| **F — locked/unavailable** | **Unknown at per-ID reason level**; branch ranks, grey/red tier icons and points provide context but not exact required level/points for each candidate |
| **U — usable now** | **Unknown** for six; no same-frame readiness or successful cast |
| **B — bound on action bar** | **Unknown** by exact stable ID and slot; icon resemblance is insufficient |

**Bounded task completion:** SC-102 acceptance allows either an eligible-but-not-known example **or a precise insufficient-coverage reason**. Here the six-name discrepancy, static IDs, five rank-zero talents and explicit unresolved predicates satisfy the second route. **Close SC-102 and RC-04 at this scope**, not the entire SC1 milestone. Future live-ID/threshold or bar-slot research, if explicitly needed, belongs in a separately specified task. **Do not demand a Warrior trainer list or simultaneous windows**, install another addon, or repeat the 69-ID catalog to close this.

No game input, code changes, native attach, VM interaction or private raw file committed by RRE.
