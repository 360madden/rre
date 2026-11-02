# SC-102 — Physical-PC spellbook/soul screenshots and SpellDump v2.1.0 reconciliation (2026-11-02)

**Status:** **MEANINGFUL PARTIAL UI EVIDENCE ACCEPTED.** Physical-PC host screenshot filenames, visual Atank level 45 ability tabs and soul-tree allocation now exist. Independent user-pasted SpellDump **v2.1.0** yields an exact 69/69 ID/name/positive-cooldown match to the preserved RRECollector v0.1 `latest` catalog. **SC-102 still BLOCKED** on identifiable learnable/locked trainer entries and exact action-bar slot bindings; the UI photos do not themselves prove such classifications.

## Sources, build and evidence strength

1. **14 user-uploaded screenshots** labeled `2026-11-01_194717.jpg` through `2026-11-01_194912.jpg` (selected entries, not a continuous recording). A bounded **read-only physical-PC** directory/hash check found **all 14 same filenames** under `C:\Users\mrkoo\OneDrive\Documents\RIFT\Screenshots\`. Their visible content is consistent with the attached RIFT images. The uploaded derivatives have different byte hashes/sizes (for example uploaded soul `194839` SHA `a2e7f931...` vs host original `b0613f01...`), so they are **not asserted byte-identical**. Host original file names and hashes below provide the reproducible source anchors. A file on the host is not contemporaneous process-ID/executable-SHA proof.
2. **User-pasted SpellDump v2.1.0** lines in the November 2 conversation: 69 ability-name, `id`, and `cd` records. Version/source are **operator-reported**; no separate raw SpellDump file or executable/source hash was supplied. Exact ID comparison job `rre-sc102-spelldump-exact-id-audit-20261102-a1` exited 0.
3. **RRECollector API-known baseline:** `latest` 69 unique current-list IDs / 69 Details, Atank level 45 Warrior, tank, role slot 1, internal build `STABLE-1-1178-A-1256632` (original [SC-418 report](REA-RIFT-SPELLCASTING-SC418-FIRST-CAPTURE-2026-11-01.md); current preserved file SHA `242259d4f20709574b45676ed6a6ebdaef64e5a8d99b22341abb5291bccdfb12` including later separate RC-02 `probe`).
4. **Same character/role/time caveat:** screenshots visibly show `Atank` level 45 and the soul tree labeled **Righteous Defender**, with the same PC's host originals found. This is a matching-character **host-local visual** snapshot and a consistent role name, but not a simultaneous API+UI frame or a new process-bound PE record; exact numeric role-slot/name equivalence still needs care. Lab1/Lab2 images were **not** mixed into this result.

## Original physical-PC screenshot source manifest

Source directory: `C:\Users\mrkoo\OneDrive\Documents\RIFT\Screenshots\`. The report commits **only filenames and hashes**, not raw screenshots.

| Host JPG filename | SHA-256 of host original | Observed screen |
| --- | --- | --- |
| `2026-11-01_194717.jpg` | `bf6112e247498280e7a30e370819e146cce0afcfa5c7afa7707d63891ef09a97` | Abilities: General |
| `2026-11-01_194724.jpg` | `6d9c7446e62322b549d89bd8fca6cc147ba0484c3b955312aaef43fc637695c7` | Abilities: Paladin upper section |
| `2026-11-01_194729.jpg` | `f325f06dc29134e769e1d85762ce1ccb8864f572f30b67c1c5b87ef70b45f4da` | Abilities: Paladin middle section |
| `2026-11-01_194733.jpg` | `3389997f0abb2e563c80258ab77250de686454368e9bc10768b54eee8b9a9102` | Abilities: Paladin lower section |
| `2026-11-01_194738.jpg` | `559a5828e9fe81cf39e8cc6045ddf32abbc532e407da51cc1bed892a41414363` | Abilities: Void Knight upper section |
| `2026-11-01_194740.jpg` | `e6871177c3b587e19632306d87784269dd8458c6db6b96798bd4d824fa2ea91e` | Abilities: Void Knight lower section |
| `2026-11-01_194742.jpg` | `b3ff81cde9064447ac9b2af2fa4d6af2cd16290ccf89d84fca263248a17b86e5` | Abilities: Paragon |
| `2026-11-01_194747.jpg` | `b83df11be25c5b5dedab89364efabb1ba25cc59012b57abffd0cf6a327703db1` | Abilities: Role names |
| `2026-11-01_194748.jpg` | `fc3c25be59c87bb154b6892b433f6cc5e389ab9bfd0bf9080c421019657f0905` | Abilities: Ascended Powers |
| `2026-11-01_194756.jpg` | `ad3c26302cb9a7765762d00fa2709693fe3cbbd4397d2cbc30a6634e94a85ff5` | Abilities: Patron services |
| `2026-11-01_194801.jpg` | `a855f2d5b184532e68d27b82df8c8d85cf800c87e732f4c88358df3ff2ae40e6` | Abilities: Patron service/passive overlap |
| `2026-11-01_194803.jpg` | `15e1ef5fc4fdb6cb68f2375372a426a80209ce495eaa6fcde06beed2457ee22c` | Abilities: Patron passives |
| `2026-11-01_194839.jpg` | `b0613f012118c744be5aa220c45d67b0d8b78da2a20632331e0dbf18a83da592` | **Soul Tree: selected Righteous Defender** |
| `2026-11-01_194912.jpg` | `071834c4c9fb98d79326613e804f099f0577af529e9bd032074fdafb97812db6` | World scene and action bars, no menu |

## Exact API/SpellDump v2.1.0 comparison

- SpellDump: **69 entries / 69 distinct exact IDs**; saved RRECollector `latest.abilities`: **69 records / 69 distinct `lookupId` values**. **0** IDs missing from either set, **0** same-ID name mismatches.
- **39** positive cooldowns from SpellDump match **39** explicitly populated RRECollector cooldown fields (tolerance `0.002s` for Lua floating-point representation). **0** conflicting positive values and **0** positive-vs-missing cases.
- The remaining **30 SpellDump `cd:0`** entries correspond to **30 missing/omitted `cooldown` fields** in RRECollector. Treat SpellDump's numeric zero as **its own exporter convention** and the absent RRECollector member as **unknown/not returned**; do not rewrite the latter as known zero.
- Duplicate names are legitimate distinct IDs, **not duplicate records**: `Building Fury` occurs for three IDs, `Changing Role` for four. Join on exact ID and retain name variants.
- The screen-visible `Righteous Charge` (`A01BB8C035B6A96DD`), `Shield of the Chosen` (`A03F53003A62FFD1E`), `Spark` (`A05213A7D60B13F6B`), `Amnesty` (`A0CB1772899B72707`), `Interfere` (`A05E934712DEB9B9F`), `Swift Strike` (`A388AC2A3092B4DB9`), and `Summon Warrior Trainer` (`A72F1082A8F6DD4C5`) all have **same-name exact-ID known catalog records** in both API and SpellDump. The screenshot alone labels names/icons, **not stable IDs**; the ID association is from the other two sources.

## New source-qualified UI observations

- `2026-11-01_194839.jpg` displays **Paladin 45 / Void Knight 15 / Paragon 0**, **60 points spent, 0 remaining**, with role label **Righteous Defender**. It shows allocated (bright) and unallocated/grey soul nodes and unlock-tier icons. Without individually labeled tooltips/trainer offers, **no exact unlearned/locked ability IDs** can be assigned from grey icons alone.
- The same images display baseline `Paragon` tab abilities (`Swift Strike`, `Building Fury`, `Follow Up Attacks`, `Way of the River`) despite **0 Paragon points** allocated. This cautions against equating `0 points` with no current known abilities; does **not** by itself prove future eligibility.
- `General` shows `Fishing` and `Survival` with **Novice** UI labels; those two names are **not** among the 69 current API `lookupId` entries. They are visible profession/skill UI entries, **not proven unlearned combat spells**.
- `Patron Abilities` visually lists `Bonus Currency`, `Bonus Daily Quests`, `Bonus Rewards`, `Marvelous Luck`, `Mounted Command`, `Overlord`, and `Patron's Focus` as **Patron Passive** entries; these seven labels are **not** among the 69 RRECollector/SpellDump IDs. They are **UI-visible/API-not-listed at this observation**, not proof of locked or trainable abilities.
- A `Summon Warrior Trainer` **spell** appears in the Patron book and in both 69-ID catalogs. **No trainer dialogue/offer window** is among these 14 screenshots; a summon ability is not a trainer list.
- Action bars are visible on screen edges, but no exact **slot → stable ability ID** is shown. Do not infer bound state from icon resemblance or equate a bar icon with learned/usable status.

## SC-102 reason-coded decision

| Dimension | Qualified result | Remaining gap |
| --- | --- | --- |
| **K — API-known/current-listed** | **69 unique IDs**, twice cross-checked by RRECollector and SpellDump | Not all UI-visible professions/passives are in `Inspect.Ability.New.List` |
| **Soul/role context** | Host-local Atank visual, **45/15/0** souls, **60/0** points, **Righteous Defender** label | No simultaneous API/UI role-slot binding or tooltip IDs for grey nodes |
| **L — learnable/eligible** | **Unknown** for unlearned IDs | Need trainer offers or labeled soul prerequisites |
| **F — locked** | **Unknown** for specific ability IDs | Need explicit trainer/tooltip lock reasons |
| **U — usable now** | **Not established** by these static menus | Separate readiness/cooldown/range/resource evidence |
| **B — action-bar bound** | Bars visibly exist | No identified exact slot → ability ID map |

**Next narrow operator evidence:** open a **Warrior class trainer dialogue**, preferably on the physical PC, with its available and unavailable/unlearned entries visible; alternatively supply tooltips identifying one named grey soul node and its unlock requirements. The host screenshot capture tool can acquire the window once the operator opens it. Action-bar tooltips can be collected later only if needed. **No second RRECollector or 69-ID capture** is justified. SC-102/RC-04 remains blocked on the **eligibility discriminator**, with broad spellbook/soul screenshot absence now resolved.

## Reproducibility and read-only jobs

- `rre-sc102-attachments-host-origin-20261102-a1` exit **0**: all 14 same filenames in a bounded physical-PC RIFT Screenshots directory, original sizes/SHA-256; source originals not modified.
- `rre-sc102-known-ability-name-reconcile-20261102-a1` exit **0**: catalog's 69 names from original current SavedVariables `latest`.
- `rre-sc102-spelldump-exact-id-audit-20261102-a1` exit **0**: 69 exact-ID/name matches, 39 positive cooldown matches, 30 zero-vs-missing pairs and no other deltas.

No game input, game-file change, second addon, native attach, VM import, or raw private screenshot/SavedVariables commit was performed by this research turn.
