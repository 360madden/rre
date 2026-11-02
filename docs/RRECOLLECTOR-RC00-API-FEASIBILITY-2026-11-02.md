# RC-00 — RRECollector API-feasibility checkpoint (2026-11-02)

**Status:** COMPLETE at **offline source and historical API-reference scope**; current-client soul/setting/action-bar capabilities remain **unverified**, not “absent.”  
**Decision:** the next useful addon instrument is a **small guarded `/rre probe` capability receipt**, not a second addon or a broad 47-folder rescan. Proceed to RC-01 compatible module extraction, then RC-02 probe.

## Source-bound baseline

| Source | SHA-256 | Qualified statement |
| --- | --- | --- |
| `addons/RRECollector/main.lua` v0.1.0 | `93fd9d3147c1b467c5d937b500d95eb2b5c9567f20c13d069ed2cddfa67532c5` | `Inspect.Ability.New.List/Detail` plus `Inspect.Unit.Detail`, `Inspect.Role.List`, `Inspect.TEMPORARY.Role`, `Inspect.Stat`; manual commands and character SavedVariables |
| `addons/RRECollector/RiftAddon.toc` | `885527d8d007c6b785cbeeeb52fef73ccf1962abe4ab6c04400b285f2d24789f` | Corrected `Email`/`NameShort` manifest; one script, version 0.1.0, character-scoped saved data |
| Installed `BotDsBridge/ability_catalog.lua` | `3a2c4a7b5a6fa2e091e3b7846187973cf1344a16cdffba191cf00236fea8d300` | Read-only reference reproduces API List/Detail → character/clock context and SavedVariables; **not** soul eligibility |
| Installed `RiftReader2Casting/main.lua` | `7e24d78eeaf589bf76a7e4d59b4f6be5242d8c8d4947448995c33a60da945213` | Lines 357–379 contain guarded `Inspect.Documentation(name)` and `Inspect.Documentation()` index usage for runtime API descriptions. **This is source-code evidence, not a current runtime return.** |
| [SC-418 saved physical-PC catalog](REA-RIFT-SPELLCASTING-SC418-FIRST-CAPTURE-2026-11-01.md) | Original SavedVariables `abbf08e8108faa2a9c85d1a61f9c4ab63070ee5ac9a29a041ebd83c058090482` | User-attested Atank L45 Warrior role slot 1; 69/69 unique current known API ability details, 0 failures. No unlearned/locked proof. |

Historical client-generated [RIFT addon API index](https://www.seebs.net/rift/pts/index.html) documents `Inspect.Role.List`, `Inspect.Setting.List/Detail`, `Inspect.Queue.Status` and `UI.Native.Soul`/action-bar frame identifiers, but it is an **old PTS snapshot**. It lists no obvious `Inspect.Soul` or `Inspect.Action` entries in the bounded top-level index; this **cannot establish absence in the 2026 client**. `UI.Native.Soul` means a UI element is named, **not** that point allocations or future trainer abilities are enumerable. `Inspect.Queue.Status` cannot be assumed to represent the game's cast queue/`Full/Short/None` setting; inspect documentation before interpreting.

## Decision-focused capability matrix

| Desired fact | Established source now | Status and next discriminator |
| --- | --- | --- |
| Known/current ability IDs, detail, cooldown flags | SC-418 and collector v0.1 | **Proved** for 69 API-listed records; preserve code/old output |
| Player identity, level/calling, target/stats | Collector `snapshotContext`; saved SC-418 | **Implemented**, some optional values conditional |
| Role slot/name list | `Inspect.TEMPORARY.Role` and `Inspect.Role.List` | **Captured**, but soul points and exact role-slot↔name mapping not established |
| Current soul/point allocation and unmet prerequisites | No qualified API record | **Unknown**; inspect runtime docs for direct API before building `souls.lua` |
| Trainer-only, learnable and locked spell list | Only in-game UI/static candidate references so far | **UI evidence needed**, unless a current exposed API proves otherwise; API List absence is not a locked flag |
| Bound action-bar slots | Historical `UI.Native.Bar...` frame names, no RRE source producer | **Unknown**; native frame metadata is not slot contents |
| Ability queue Full/Short/None option | Historical `Inspect.Setting.List/Detail` lead and separate native `ActionBars_AbilityQueue` field | **Unmapped**; if runtime settings API exposes the exact key, correlate with an operator-visible UI label; never infer enum from raw 1 |
| `Inspect.Documentation` on current build | Existing installed RR2 source checks for it | **Code-supported candidate**, not yet current-runtime verified |

## One bounded RC-02 probe specification

- Keep existing `/rre capture` output and schema 1 untouched. Add one manual `/rre probe` (no automatic polling) that first checks `type(Inspect.Documentation)`. If present, safely enumerate the in-client index and retain **only relevant names** under `Inspect.Role`, `Inspect.Setting`, `Inspect.Soul`, `Inspect.Action`, `Inspect.Ability`, `Inspect.Queue`, and `UI.Native`. Cap records and string lengths; count ignored/truncated entries.
- Request short documentation for explicit names: `Inspect.Role.List`, `Inspect.Setting.List`, `Inspect.Setting.Detail`, `Inspect.Ability.New.List`, and any actually returned direct soul/action paths. Record `present/absent/error/unknown` separately.
- Do **not** indiscriminately call functions from the index: signatures may require arguments or have side effects. Only if a documented read-only settings API and its signature are confirmed should a subsequent targeted call examine the exact `ActionBars_AbilityQueue` key. Avoid dumping all personal settings.
- Attach the existing player, role, source version and frame/real-time context to the result; save under a separate optional `RRECollectorData.probe` so the accepted `latest` known-catalog record survives a probe failure. Normal `/reloadui`/logout flush, with user-operated commands.
- Acceptance requires source/installed hash parity and one operator-attested saved probe receipt. No current-client positive/negative capability result is claimed until that happens.

## Stop and handoff

No live game input, process manipulation, RR2/Workbridge edit, installed game change or capture was performed during RC-00. Existing SC-418 catalog is enough for the current-known dimension. **SC-102's same-role physical-PC spellbook/soul/trainer/action-bar UI comparison can proceed independently.**

**Next:** RC-01 minimal compatible module split (source only, dedicated small validation), then RC-02 targeted capability probe; no new second addon.
