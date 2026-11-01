# SC-416 — RIFT installed addon inventory and spellbook-source triage

**November 1, 2026 EST. Status: source inventory COMPLETE; SC-102 remains blocked on a current same-character/role local-PC API + spellbook/soul comparison.** Scope: read-only installed addon inventory on the physical PC and both running VMware labs (VM evidence supplementary; no guest native build assumed equivalent). No game input, addon enablement, source edits, or process modification. Guest Public Documents held a temporary JSON report for file transfer only; all report temp files were removed from the guests.

## Exact inventory

- Physical PC, `C:\Users\mrkoo\OneDrive\Documents\RIFT\Interface\AddOns`: **47 top-level directories**, **45 root `RiftAddon.toc` manifests**, **19 folder names ending in `.disabled`**, two non-addons (`RIFT_API_Docs`, `zip`). Disk listing and hash of each host root manifest saved in [machine-readable inventory](REA-RIFT-SPELLCASTING-SC416-ADDON-INVENTORY-2026-11-01.json).
- RIFT-Lab-1: **47/47 same folder names**. **42 root manifests readable and version-matched** to host; **three manifests unreadable** (`ApiAtlas`, `ApiAtlasConsumer`, `RiftApiCollector`); two absent as expected. Bounded guest metadata returned file attribute mask `4199968` (`0x401620`): the three unreadable manifests each have Windows **Offline**, **ReparsePoint**, **RecallOnDataAccess** bits. This is consistent with OneDrive cloud placeholders, not proof that every dependent `.lua` is locally readable. The guest source was not hydrated.
- RIFT-Lab-2: **47/47 same folder names and declared versions**, with 45 readable root manifests and the two expected non-addon folders. Equality of the manifest metadata **does not prove full byte-for-byte source equality or active load state**.
- Windows GUI screenshot captures independently identify Lab 1 **Atank, level 45 Warrior** and Lab 2 **Bolinao, level 43 Rogue**, with General Abilities and Stats windows visible. They are separate characters/roles; no cross-VM catalog merge.
- All inventories are **files on disk**, not an `AddonSettings.lua` enabled-state audit, a successful addon-load test, or a current ability API capture.

## Full top-level addon inventory

In the Lab columns, “Matches” means the local root TOC was read and its **declared version** matched host. This is weaker than hash equality.

| Folder | Host version | Lab 1 manifest | Lab 2 manifest | Purpose / code-checked distinction |
| --- | --- | --- | --- | --- |
| `ActionStrip.disabled` | 0.2.0 | Matches | Matches | Pixel telemetry bridge: player/target name, HP, resources, casting (8 color rows). |
| `ApiAtlas` | 0.3.0 | **Unreadable** | Matches | API documentation browser/export |
| `ApiAtlasConsumer` | 1.0.0 | **Unreadable** | Matches | Atlas example consumer |
| `ApiBrowser` | 1.1 | Matches | Matches | API wiki browser |
| `ApiDumper` | 0.1.0 | Matches | Matches | Action.Get slot 1–12 probe (manifest misleading) |
| `ApiProbe` | 0.1.0 | Matches | Matches | Action API probe |
| `BarCode.disabled` | 0.4.1 | Matches | Matches | Live BC-Strip/1 telemetry bridge for RIFT. |
| `BotDsBridge` | 0.3.3 | Matches | Matches | Known-ability List/Detail to character SavedVariables |
| `BotFight` | 0.2.0-beta | Matches | Matches | Combat data probe / ability API consumer |
| `ChromaLink.disabled` | 0.1.0-dev | Matches | Matches | Ability export / telemetry bridge (suffix .disabled) |
| `Gadgets` | v0.10.19 | Matches | Matches | Unit Frames and Other Stuff for RIFT |
| `JAB` | 1.4.2 | Matches | Matches | Custom action bar |
| `Leader.disabled` | 1.0.0 | Matches | Matches | Unclassified |
| `LibSimpleWidgets` | 1.14.5 | Matches | Matches | Unclassified |
| `LibWiki` | 1.1.1 | Matches | Matches | A library for creating and navigating Wiki-like pages. |
| `luapad` | 1.8 | Matches | Matches | Lua runtime scratchpad |
| `MemoryScannerHelper` | 1.0.0 | Matches | Matches | API / native discovery helper |
| `MereHealingFrames` | 0.4.38 | Matches | Matches | A set of healing frames |
| `Merisioux` | 0.30-151128-15:56:24 | Matches | Matches | Unclassified |
| `MessageViewer` | 1.0 | Matches | Matches | A tool to view, send and filter the inter-Addon messages. |
| `MinionSender.disabled` | 1.6.9 | Matches | Matches |  |
| `MultiFollow.disabled` | 0.2.0 | Matches | Matches | Multiboxing engine for Rift. Leader-driven follow and assist for up to 5 characters. |
| `nkDebug` | 1.3.3 | Matches | Matches | Helpfull tools for debugging Rift addons |
| `nkTextureViewer` | 1.1.0 | Matches | Matches | Record all the textures |
| `player.coord.disabled` | 1.1 | Matches | Matches | A minimal, draggable coordinate overlay showing player position and zone. |
| `PlayerCoords.disabled` | — | Matches | Matches | Unclassified |
| `projectabilitybook.disabled` | 1.1 | Matches | Matches | Static soul ability IDs/icons for five callings |
| `ReaderBridge` | 0.3.2 | Matches | Matches | Player data marker bridge |
| `ReaderBridgeExport.disabled` | 0.1.0 | Matches | Matches | Export layer that mirrors ReaderBridge telemetry into saved variables for RiftReader |
| `RiftApiCollector` | 0.5.0 | **Unreadable** | Matches | Manual paged known-ability ID export, no SavedVariables |
| `RiftBridge.disabled` | 0.1.0 | Matches | Matches | Personal-use coordinate HUD for RIFT. |
| `RiftMeter` | 1.2 | Matches | Matches | Combat log outcome tracker |
| `RiftMeter.disabled` | 1.2 | Matches | Matches | Alternate folder copy; same identifier as RiftMeter |
| `RiftReader2` | 0.1.0 | Matches | Matches | API/reader bridge |
| `RiftReader2Casting` | 0.4.0 | Matches | Matches | Full List/Detail metadata to character SavedVariables |
| `RiftReaderApiProbe` | 0.6.0 | Matches | Matches | API capability/ability probe |
| `RiftReaderValidator.disabled` | 0.1.0 | Matches | Matches | Helper addon for validating RiftReader memory captures. |
| `RIFT_API_Docs` | — | — | — | Documentation folder, not an addon |
| `Rustys_Action_Bars` | 3.0.4 | Matches | Matches | Unclassified |
| `SignalStrip.disabled` | — | Matches | Matches | Unclassified |
| `SpellDump.disabled` | 2.1.0 | Matches | Matches | Known-ability copyable names/IDs/cooldowns |
| `spelldump2.disabled` | — | Matches | Matches | Known-ability display/filter, missing IDs in raw export |
| `TargetCoords.disabled` | — | Matches | Matches | Unclassified |
| `TextureViewer` | 1.2.1 | Matches | Matches | A tool to view the textures which are present inside the game client. |
| `Walker.disabled` | 0.4.0 | Matches | Matches | Rift telemetry bridge - exposes in-game API state via SavedVariables. |
| `WalkerCoords.disabled` | 0.1.1 | Matches | Matches | Draggable window showing live player coordinates from the Rift API. |
| `zip` | — | — | — | Archive folder, not an addon |

## Decision-changing source findings

1. **BotDsBridge 0.3.3 — most direct explicit character catalog export.** `ability_catalog.lua` (`SHA256 3a2c4a7b5a6fa2e091e3b7846187973cf1344a16cdffba191cf00236fea8d300`) exposes `/botds catalog`; it calls `Inspect.Ability.New.List()`, iterates candidate IDs and `Inspect.Ability.New.Detail(id)`, captures name, cooldown, cast time, passive, channel, approximate combined resources, and writes `BotDsDebug.catalog` with player level/calling to character SavedVariables. A UI reload/save is needed for disk persistence; no command was sent in this audit. The exporter drops fields and may skip invalid detail records, so do not call it the entire game's unlearned spell universe.
2. **RiftReader2Casting 0.4.0 — richer retained details.** Existing `model.lua` (`SHA256 dbd689b9f47140e95153a583e47a445ae3ac35794d293cf58c5d58e1143ce2bc`) batches `List/Detail` with lookup IDs, rank/variant-related IDs, passive/cost/range/status fields; `main.lua` (`SHA256 7e24d78eeaf589bf76a7e4d59b4f6be5242d8c8d4947448995c33a60da945213`) places `evidence.abilities` into character-scoped `RiftReader2CastingEvidence` on SavedVariables load. Verify actual addon load, save freshness, character, active role and build before reuse.
3. **RiftApiCollector 0.5.0 — exact paged ID export, not detail bulk export.** `main.lua` (`SHA256 47755e48c8616a423eb69c2d4b1adf74c560a8d49d96e5b3f9a446fe0ec880be`) exposes `/rac abilities`, `/rac export abilities prepare` and paged copy/view operations, with completion/truncation status and page fingerprint. It does **not** declare SavedVariables and its bulk export carries IDs, not the complete `Detail` set. **Lab 1's root TOC is currently an unreadable OneDrive placeholder**, so do not assume it can load there.
4. **ProjectAbilityBook 1.1 — complementary static reference.** Its `Callings` directory contains **five callings**, including 11 Warrior and 11 Rogue soul files. `Paladin.lua` (`SHA256 e4af04464201adbc5cbae9d07cab0e36a9da616b5b30abd466f8ca44c8f92f28`) includes exact IDs for Aggressive Block and Light's Decree; `Marksman.lua` (`SHA256 fd5b52925e6d20215f93014de283d06cd069a287489e88df59afb27c36cff8b9`) contains Barbed Shot and other exact IDs. This may supply unlearned/static candidates, **not current soul eligibility or proof a character can cast them**.
5. **SpellDump 2.1.0 / SpellDump2 — in-game known-ability viewers.** Both folders end in `.disabled`. SpellDump's `/spells` offers copyable names/IDs/cooldowns, but its TOC persists only settings and logs. SpellDump2 calls `List/Detail`, but its export discards IDs and its offensive filter is heuristic. Initialization in an older screenshot did not prove an exported file.
6. **ApiAtlas 0.3.0 versus ApiDumper 0.1.0.** ApiAtlas's `Collector.lua` (`SHA256 64c591c27caa861d43879b8fdbb50c408c51f9549eb80e7c1e3e2597ad5ac71a`) gathers `Inspect.Documentation`—API documentation, **not** current learned spells. ApiDumper's manifest claims a documentation dump, but its actual `main.lua` (`SHA256 8ae15f28fb964932e397e22f019911a0c5c0bf403ebc1b39cdd48da70c4d84ed`) samples `Action.Get` slots 1–12 instead. Treat the manifest description as stale.
7. **ChromaLink** has a substantial `List/Detail` ability exporter but its folder ends in `.disabled`; **RiftReaderApiProbe** probes ability API availability and broader live state. Neither is substituted for a same-session character-role catalog without saved output and build/identity binding.

## Next verified route for SC-102

1. Keep the two VM references separate: Atank/Warrior and Bolinao/Rogue, and requalify each guest executable if comparing native internals. **Physical-PC current role-specific evidence remains the acceptance target** under [the pinned local-PC policy](REA-RIFT-LOCAL-PC-TARGET-2026-10-27.md).
2. Prefer an already-loaded **RiftReader2Casting** `RiftReader2CastingEvidence.abilities` full-detail save for the same character/role as the open spellbook. Alternatively, a supervised `/botds catalog` plus a saved/exported `BotDsDebug.catalog` can produce a compact character-tagged baseline. These are proposed next actions, **not actions performed**.
3. Supplement known API IDs with ProjectAbilityBook static IDs; photograph the **selected soul/point allocations and an explicit locked/learnable ability UI**, not only General Abilities. Keep role and timestamps exact.
4. Resolve Lab 1's three **Offline/ReparsePoint/RecallOnDataAccess** manifests through its existing addon-sync/OneDrive file-availability owner before treating `RiftApiCollector` as usable there. No hydration or addon activation was attempted in SC-416.

## Reproducible receipts and provenance

- Host manifest scan: `rre-sc102-host-addon-manifest-inventory-20261101-manager-a1`, exit 0, `2026-11-01T20:28:31.3453533Z`.
- Lab 1 folder names: `rre-sc102-lab1-addon-names-readonly-20261101-manager-a1`, 47 names, original report SHA `bfb881a6b448139ea0b1946f768b7b94b4c5910944c00008f9313c4ba435ec6f`.
- Lab 1 tolerant manifests: `rre-sc102-lab1-addon-manifest-tolerant-20261101-manager-a1`, 42 readable/3 unreadable, report SHA `ae9007ce5690b26d526475d0d740cb9fbb3334c9329e7d1820bde54fca63adeb`. The first non-tolerant probe's exit 1 was **not counted** as evidence of absence; follow-up isolated the unreadable files. Windows attribute probe `rre-sc102-lab1-addon-unreadable-attributes-20261101-manager-a1`.
- Lab 2 manifest report: `rre-sc102-lab2-addon-disk-inventory-20261101-manager-a1`, report SHA `2290abb31ac092f5430a79a46c763ad17c9ee766eaa2d6018512f11194e017d0`.
- Lab 1 GUI: `rre-sc102-lab1-genericcapture-20261101-manager-a1`, image SHA `63d46a14e34b288f848bd74777fc5868794c03c6fdc1e134b47c0c9204777e2f`, `20:20:07.593Z`.
- Lab 2 GUI: `rre-sc102-lab2-genericcapture-20261101-manager-a1`, image SHA `07eb147f37de2ef475a825ea279c656cecdae340b587aba8b26ae267e32071d6`, `20:20:18.086Z`.
- Guest report files were copied into `C:\work\temp\` for inspection and original guest staging files cleaned. Those temporary paths are not an RRE Git source or a current live API record. Host root manifest hashes and per-lab statuses are in the JSON companion.

**Limits:** This inventory does not establish addon enabled/loaded state, full nested-dependency hashes, source file equality across guests, an updated game executable SHA inside guests, or any new same-role `Inspect.Ability.New.List/Detail` output. The SC-102 scientific evidence gate remains open.
