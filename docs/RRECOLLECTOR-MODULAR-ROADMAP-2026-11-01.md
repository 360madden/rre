# RRECollector modular research addon — implementation roadmap

**Planned:** November 1, 2026  
**Status (November 2, after operator probe):** RC-00/01/02 complete; v0.2.0 installed files 7/7 hashes, **live `/rre probe` SavedVariables captured and source-hashed**. RC-03 closed by explicit no-qualified-soul/eligibility/bar-API decision; RC-05 v0.2 acceptance complete. **RC-04 / SC-102 physical-PC UI reconciliation remains blocked.**
**Owner:** RRE/REA manager, `C:\work\rre\addons\RRECollector` only.  
**Companion task register:** [RRECOLLECTOR-MODULAR-TASKS-2026-11-01.json](RRECOLLECTOR-MODULAR-TASKS-2026-11-01.json).  
**Research link:** [SC-605 proven-addon playbook](REA-RIFT-SPELLCASTING-SC605-CUSTOM-ADDON-PLAYBOOK-2026-11-01.md) and [SC-418 saved live catalog](REA-RIFT-SPELLCASTING-SC418-FIRST-CAPTURE-2026-11-01.md).

## Outcome and design decision

Grow **one** independent, read-only `RRECollector` research addon into a small collection of focused Lua modules. Reuse the original collector, not a second installed addon or a full production telemetry framework. Only build modules when a verified RIFT API can supply decision-changing observations; when the API cannot expose an answer, record the gap and use operator-provided game UI or targeted native research.

**Important:** This is an addon-development roadmap. It does not authorize gameplay automation or claim the SC-102 spellbook blocker is solved. The November 1 Atank physical-PC user-attested capture already contains **69 unique current API-listed abilities and 69 Details**, no detail/duplicate/truncation errors. A new export is **not** needed solely to regain those records. The blocking part of SC-102 is still matching physical-PC same-character/role spellbook, soul/trainer and action-bar UI.

## Baseline contract to preserve

- `RiftAddon.toc` is a **working corrected manifest**, with `Identifier`, `Name`, `NameShort`, `Description`, `Author`, `Email`, `Version`, `Environment`, `SavedVariables` and `RunOnStartup`. Any Lua split must list scripts in dependency order; no assumed `require` mechanism.
- `main.lua` v0.1.0 already implements `/rre help`, `status`, `capture`, `page N` and `export`, saves `RRECollectorData.latest` per character after normal game UI reload/logout, batches `Inspect.Ability.New.Detail` with per-ID fallback, and records player/target/stats, optional role slot/names, client version and clocks. Current caps are 1,024 raw list entries, 512 unique IDs, 256 stats.
- Preserve exact ability IDs, finite/scalar limits, false/zero vs missing, null/unknown semantics, capability flags, diagnostics, completeness counts, role identity and source clocks. Never convert “not in API List” into “locked” or “unlearnable.”
- Keep v0.1 `RRECollectorData.latest` readable. Add optional fields only when ready; advance schema version only for an actual incompatible change with explicit migration/backup. Do not discard a good saved snapshot on a failed capture.
- Source of truth: user-operated physical-PC RIFT; Lab1/Lab2 data remain distinct and supplementary. The operator enters game slash commands; RRE tooling does not issue game input or modify RR2/Workbridge, the executable, other addons or game settings.

## Capability / ownership matrix

| Area | Existing capability | Proposed module | Truth boundary |
| --- | --- | --- | --- |
| Known/current abilities and detail | **Proved** with SC-418, 69/69 | `abilities.lua` extracted from current `main.lua` | Does **not** enumerate all future or unlearned spells |
| Player, target, resources, stats, role slot/name | **Implemented**, optional fields conditional | `context.lua` | Soul point allocation or name-to-slot mapping not yet qualified |
| API presence and documentation | Safe feature guards already in v0.1 | `capabilities.lua` | Must discover and report unknown/missing; no speculative API calls |
| Soul allocations and prerequisites | **Unproven** for the current API | `souls.lua` **only if verified** | Do not claim this is exposed merely because the UI exists |
| Spellbook, trainer, locked/learnable | **UI evidence pending** | `eligibility.lua` **only for supported API fields** | Manual same-role UI may remain mandatory |
| Action-bar bindings | **Not captured by RRECollector** | `bars.lua` **only if supported** | Bound-to-bar does not mean known/usable/learnable |
| Operator commands, persistence and reports | **Working v0.1** | `main.lua` bootstrap, `diagnostics.lua` as needed | No gameplay input; no autonomous background polling |

**API discovery rule:** inspect current client-generated `Inspect.Documentation`/local API references and at most two relevant installed-addon examples. Historical API documentation is a lead, not proof of support on the current game build. Record observed `present/absent/returned/error/unknown` with character/role/build and small sample output. A visible Soul UI window is not evidence of an enumerable soul-tree API.

## Milestone sequence

| Phase / task | Work (smallest useful increment) | Deliverable / exit gate |
| --- | --- | --- |
| **M0 / RC-00 — API feasibility** | Pin v0.1 source/TOC and the SC-418 saved-catalog record. List exact desired missing fields and map them to existing or verified RIFT addon API calls, or mark “UI-only/unknown”. Do not re-inventory 47 addon directories. | Short capability matrix and the **first one** API observation worth coding; explicit “no API” outcome is acceptable. |
| **M1 / RC-01 — Modular skeleton** | Refactor only the proven capture path into ordered `core.lua`, `context.lua`, `abilities.lua` and `main.lua` if M0 establishes a reason for change. Keep one addon identifier, one slash prefix, old SavedVariables key, exact command behavior and existing data schema. | Focused static/manifest check, predictable TOC load order, no output contract regression; commit before host installation. |
| **M2 / RC-02 — Focused capability probe** | Add one guarded manual `/rre probe` (or similarly small command) for the specific missing APIs from M0. Use bounded, read-only requests; store source/version, capability flags, returns/errors and reasons for unavailable fields. No wholesale documentation dump. | Operator can run once, `/reloadui`, and produce a source-hashed capability receipt. Stop immediately if target APIs are absent. |
| **M3 / RC-03 — Useful conditional producers** | Add `souls.lua`, `eligibility.lua`, `bars.lua` only for discovered supported APIs; otherwise leave them **unimplemented** and record exactly which UI/native evidence is required. Extend existing `abilities`/`context` data if that already answers the question. | One complete-or-explicitly-partial character/role-bound SavedVariables record; no fabricated locked/learnable flags. |
| **M4 / RC-04 — SC-102 UI reconciliation** | In parallel with M0–M3, use existing SC-418 Atank role-slot-1 catalog and operator-provided physical-PC spellbook/souls/trainer/action-bar screenshots. Pair exact character/role/build/time as far as source supports; refresh capture only if incompatible. | A source-qualified known/learnable/locked/usable/bound table or exact blocker report. This task is **not gated** on modular refactor completion. |
| **M5 / RC-05 — Deliver, verify, hand off** | Bump version only for actual implementation, check complete TOC fields, compare source/installed SHA files, use one operator-driven load/capture/reload/save smoke check, document failures and rollback path, update taskboard and handoff. | One accepted coherent addon increment committed with source and saved-output proof level; existing addons untouched. |
| **Later / RC-06 — Optional probes** | Only if a concrete SC3/SC5 question needs it, consider bounded readiness/castbar/resource/event snapshots. Define exact event/timing questions before implementing any listener or sampling loop. | Deferred until demanded; no all-purpose live telemetry or infinite polling by default. |

**Critical path:** M0 → (M1 if justified) → M2 → M3 → M5. **SC-102 UI evidence (M4) is independent and can unblock research immediately**, without waiting on addon modularity. If M0 finds no actionable API for souls/spellbook, pause M2–M3 rather than making an empty implementation; prioritize M4.

## November 2 current-client capability verdict

[Source-hashed first v0.2 live probe](RRECOLLECTOR-RC02-FIRST-PROBE-2026-11-02.md): the operator-attested physical-PC Atank role-slot-1 SavedVariables file contains the separate `probe` plus intact v0.1 `latest` **69/69** ability records. The current `Inspect.Documentation` index scanned **1,910**, retained **22** relevant names with **0** documentation errors and no scan truncation. `Inspect.Role.List` and `Inspect.Setting.List/Detail` are current functions; tested `Inspect.Soul.List/Detail` and `Inspect.Action.List/Detail` are `nil`. `UI.Native.Soul` and `UI.Native.BarMain` are **UI tables**, not proof of points or bar slot inventories. `Inspect.Queue.Status` describes generic `global`/`auctionfullscan` queues, not a qualified spellcast mode. The full saved-file SHA-256 is `242259d4f20709574b45676ed6a6ebdaef64e5a8d99b22341abb5291bccdfb12` (31,081 bytes); no raw private file was committed.

**RC-03 no-code exit:** No supported direct soul, eligibility or action-content producer was demonstrated; do **not** add empty `souls.lua`, `eligibility.lua` or `bars.lua` just to fill the roadmap. A later narrow settings-key probe would require a separate decision-changing SC3 question and an actual documented key. **RC-04/SC-102 is the practical next gate:** same physical-PC character/role spellbook, soul/points, trainer and action-bar screenshots; a second ability capture is unnecessary solely to recover the 69 saved IDs. This is a scoped result, not a claim that no RIFT API anywhere could ever expose the missing fields.

## Implementation and acceptance rules

1. **One source owner and commit per meaningful milestone.** Only RRE `addons/RRECollector/` and its dedicated docs/task entries are in scope. No second addon, unrelated repo migration or framework rewrite.
2. **Minimal changes.** Keep v0.1 until a module has a concrete purpose. No UI widget, daemon, network server, auto-rotation or telemetry stream is required for this research scaffold.
3. **Failure isolation.** `pcall` guarded API calls, bounded entries/payload, explicit partial status and field omissions, no crashing slash handler. Source and saved-file failures must not silently count as success.
4. **Focused verification.** For a code milestone: manifest/source-load-order check and one relevant structural test; when the user operates the game, one physical-PC capture + normal SavedVariables flush + hash/provenance inspection. Do not run a redundant full navigation test suite. Record actual outcomes rather than optimistic test predictions.
5. **Version/rollback.** Preserve the pre-change Git commit and installed three-file v0.1 package receipt. Confirm changed files before copying only the RRE-owned addon; if new package fails, restore only its own versioned files after checking current installed hashes. Never overwrite operator edits or touch another addon.
6. **Documentation.** Update the dedicated board state, build/API evidence, one decision-changing finding, installation match, and resume handoff each accepted step. Do not mark SC1/SC3/SC6 finished merely because the collector loads.
7. **Stop rule.** Two distinct nondecisive probes of one API claim → document unknown/unavailable and switch to UI/native evidence. Do not expand scope to fill time.

## Current next action after RC-02 installation

[RC-00 feasibility](RRECOLLECTOR-RC00-API-FEASIBILITY-2026-11-02.md) and [RC-01 modular source split](RRECOLLECTOR-RC01-MODULAR-SCAFFOLD-2026-11-02.md) are accepted. [RC-02 `/rre probe` installation record](RRECOLLECTOR-RC02-PROBE-INSTALL-2026-11-02.md) confirms 7/7 source/host SHA parity but **no in-game load yet**. The physical-PC operator should run `/rre status`, `/rre probe`, `/reloadui`, then RRE can examine `RRECollectorData.probe` as the first current-build API capability receipt. Do not implement RC-03 soul/eligibility/action-bar producers until a usable supported API is established. The **SC-102 spellbook/soul/trainer/action-bar UI** remains independently pending; the existing 69 known abilities need not be recaptured merely to recover them.
