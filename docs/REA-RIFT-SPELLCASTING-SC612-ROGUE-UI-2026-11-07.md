# SC-612 — Lab-2 Rogue role, soul allocation and native ability groups

**November 7, 2026, 10:38 EST.** Fresh native UI evidence supplies the character context missing from [SC-610's 54-ID catalog](REA-RIFT-LAB2-CATALOG-2026-11-07.md): **Bolinao, level 43 Rogue, CUSTOM Role 1, Ranger 43 / Marksman 14 / Bard 0**, **57 points spent, 0 remaining**. A bounded Ranger spellbook page also places eight uniquely name-correlated API records into native **Builder / Finisher / Damage** groups.

Accepted scope is native UI context and those eight name joins. The [machine receipt](REA-RIFT-SPELLCASTING-SC612-ROGUE-UI-2026-11-07.json) retains original-image/action hashes, exact API candidate IDs, observations, uncertain outcomes and build/save invariants. It does not establish a complete spellbook, future unlocks, Legendary variant IDs, usable/bound state or casting/native execution.

## Instructions, target and source

SC-612 in the [casting register](REA-RIFT-SPELLCASTING-TASKS-2026-10-27.json) follows the [casting roadmap](REA-RIFT-SPELLCASTING-ROADMAP-2026-10-27.md), [SC-605 API/UI-first playbook](REA-RIFT-SPELLCASTING-SC605-CUSTOM-ADDON-PLAYBOOK-2026-11-01.md), [M2 routing contract](REA-RIFT-SPELLCASTING-OFFLINE-TOOL-ROUTING-M2-2026-11-03.md) and [external Lab-2 procedure](REA-RIFT-LAB2-EXTERNAL-MOUSE-2026-11-07.md). The sole manager owns this report, JSON, SC register and dated handoff; starting main was **942e7c6d66ac1ec376a66f3b44af8e2fe6757f9a**. No tool/addon implementation was changed.

Only VMware `RIFT-LAB-2` was used. Before/after read-only guest receipts at **15:12:32.7439676Z** and **15:35:43.3881249Z** agree on PID **9752**, start UTC ticks **639294897826627677**, executable `C:\RIFT_TRANSFER\RIFT\rift_x64.exe`, **60,493,640 bytes**, SHA-256 **1935a05c9db6d468e34e0055014a4a99c1b5afceb1695884e24600f5c20a4be8**. Retained original guest bytes independently match. These are bracketed observations, not continuous or mapped-memory attestation.

The existing host `vncdotool 1.4.2` route performed **5 reviewed hovers, 8 reviewed clicks and 4 capture-only observations**. Each operation has fresh original imagery and VM-epoch checks; input operations have exact capture-ID reviews and release, and every operation records disconnect/mutex release. Native controller 41888 remains intentionally stopped. No guest mouse helper, keyboard, movement, cast, role switch, soul/point allocation, reset, purchase, settings change or addon deployment was requested. Opening the native menu cleared ordinary AFK state; no gameplay conclusion is drawn from that.

## Direct UI findings

The tooltip-bound **PLAYER** HUD menu exposed named **Soul Tree** and **Abilities** entries. One Soul Tree click produced an early unchanged frame; a separate settled capture then showed the actual panel. The allocation original is `artifacts/lab2-sc612-20261107-1026/soul-tree-settled/before.png`.

| Native field | Observed value | Limit |
| --- | --- | --- |
| Role label/style | Role 1 / CUSTOM | Consistent with saved role slot 1 and label Role 1; no UI-exposed exact role object ID |
| Ranger / Marksman / Bard | 43 / 14 / 0 | Current displayed allocation; no allocation change was made |
| Points spent / remaining | 57 / 0 | 43 + 14 + 0 = 57 |
| Max Legendary counters | Ranger **0/2**, Marksman **0/1**, Bard **0/1** | Displayed counters only; no unlock threshold, eligibility or selected Legendary ID |

A magnified diagnostic crop was used to read the small counter labels and correct the initial Ranger transcription from 0/1 to **0/2**. The original image remains authoritative. Historical Atank/Warrior allocations are not transferred to this Rogue.

The native Abilities panel showed categories **General, Marksman, Ranger, Bard, Role, Guild Perks, Ascended Powers and Patron Abilities**. Clicking Ranger's text had no verified effect in immediate or settled frames; a distinct click on its icon selected **RANGER**. Do not assume the whole text row is a working hotspot. The accepted Ranger original is `select-ranger-icon/after.png` in the same evidence directory.

| Native group | Visible names, each uniquely matched in SC-610 sequence 2 |
| --- | --- |
| Builder | Ace Shot; Piercing Shot; Quick Shot; Shadow Fire; Splinter Shot; Trick Shot |
| Finisher | Head Shot |
| Damage | Rain of Arrows |

These are **unique exact-name joins** to the saved API IDs, not IDs exposed by the native UI. No claim of all Ranger entries is made: lower content is off-page and was not swept. The prior General page visibly included Rejuvenate, Dismiss Pet, Legacy of the Shade, Motivational Roar, Ranged Weapon Mastery, Recycle, Soul Recall and Toggle Auto Attack, plus profession labels Fishing and Survival. Profession labels are not automatically expected in the API ability enumeration.

## Inconclusive tooltip route and preserved invariants

Two bounded Soul Tree hovers produced transient **Pin Down** and **Diffuse** tooltip frames. A later capture did not retain a future-root tooltip. These frames do **not** bind a name, threshold or exact ID to the intended future-root location. No future unlock or locked-spell claim is accepted, and no allocation/cast was used to force evidence. This is a reason to qualify tooltip settling before a later tooltip-dependent experiment, not to repeat speculative root clicks.

Soul Tree and Abilities were closed through their actual visible close controls. A read-only copy of the character SavedVariables after the UI work is **byte-identical** to SC-610: **21,670 bytes**, SHA-256 **5e2f8bab564fb4916dc87ba929fc3c1d022bab913bb7b4896cd2923197aae7fb**, v0.4.11 / sequence 2. There was no recapture or UI reload. Original files remain local; raw player/target identifiers are not published. Owned temporary guest diagnostic JSON cleanup was exact-path/hash-guarded and confirmed.

## Gate and next useful work

The repository now has source-bound current Lab-2 soul context and eight native UI group observations. **SC-612 completes only that bounded question.** SC-103's Warrior Legendary/Protector's Fury identity gap, SC-306 queue enum, broader SC-604, RC-26/30/31/32 and NAV-002 retain their gates. The Warrior static 96-ID list remains inapplicable to this Rogue. No new native mechanism is inferred from UI group names.

Validate original/action hashes, exact-name uniqueness, build/save invariants, unchanged unrelated task records, JSON/links, roadmap and diff before a scoped local commit. Documentation-only integration does not require the historical full research suite. Preserve the nine pre-existing untracked paths and independent work. No Ollama or new model execution occurred. The [timestamped handoff](REA-RIFT-SPELLCASTING-SESSION-HANDOFF-2026-11-07.md) carries the active three-hour goal; this milestone does not satisfy its duration requirement.
