# SC-103 — source-qualified ability-change event payload contract

**Date:** 2026-11-03. **Owner:** physical-PC RRE spellcasting manager. **Evidence tier:** source-qualified historical/generated API documentation and independently corroborating installed addon source only. **State:** accepted as an offline payload-shape lead; **current-client callback delivery, role/Legendary selection and modern Protector's Fury ID remain unverified**.

## Original sources and exact provenance

All paths below are relative to the **physical-PC RIFT Interface/AddOns root**, accessed read-only through the configured Workbridge root. The `RIFT_API_Docs` files are 18-line *generated Markdown references to older HTML documentation*, marked `Priority tier: Secondary`. Their presence on disk is not proof that a documentation addon loaded or that the 2026 client implements the same runtime semantics.

| Documented event | Source path under AddOns | SHA-256 (exact local file) | Documented `abilities` variant |
| --- | --- | --- | --- |
| `Event.Ability.New.Add` | `RIFT_API_Docs/LLM_RIFT_API/Ability/event_ability_new_add.md` | `83ef445348a383aa934d629be38776ed6df10b9172e45dbe20f151081bd321e0` | Map: ability ID → value documented as “true” (Lua scalar type unverified) |
| `Event.Ability.New.Remove` | `RIFT_API_Docs/LLM_RIFT_API/Ability/event_ability_new_remove.md` | `e5588a1af69b781272983f81403c6c654a3a4a7fc19cc85e8632608354c0776a` | Map: ability ID → value documented as “false” (Lua scalar type unverified) |
| `Event.Ability.New.Usable.True` | `RIFT_API_Docs/LLM_RIFT_API/Ability/event_ability_new_usable_true.md` | `8adf6e1bb46999162fc8637bd8ae29c7add337b7b315277d383276749de19578` | Map: ability ID → new usability value |
| `Event.Ability.New.Usable.False` | `RIFT_API_Docs/LLM_RIFT_API/Ability/event_ability_new_usable_false.md` | `f9ca81a3753239008b64945125305dbd7eb43a73dde6cb060ec7c5126b466dd6` | Map: ability ID → new usability value |

Each generated page names a single usage parameter `abilities` with datatype `variant`; **none of the four pages independently establishes the exact runtime Lua scalar type**. Add/Remove describe values as quoted “true”/“false”; Usable.True/False describe a new usability value. The four names were also present in the previously saved RIFT API-name index ([selection evidence](REA-RIFT-SPELLCASTING-SC103-LEGENDARY-SELECTION-2026-11-03.md)), but that index established **names**, not live callback invocations or payload values.

## Independent implementation corroboration (installed JAB source, no edits)

- `JAB/Main.lua` exact SHA-256 `7cb9a877f7d8f2e45bb43e580248ae03e9bb5101efd39bb131d306dbeb69249b`: lines **283–309** register `.Usable.True/False` handlers `function(_, abilities)`, iterate `abilityID, usable` and update matching slotted action-button usability. Lines **349–389** register `.Add/.Remove` handlers with the same callback form, iterate ability-ID keys; Add re-queries `Inspect.Ability.New.Detail(abilityID)` for matching slots, Remove clears matching slots.
- `JAB/Events.lua` exact SHA-256 `012c89f1ff3f87f3da61530051371446587acf610fff9b53ac2867abfbaa2a90`: lines **12–24** call `pcall(Command.Event.Attach, event, handler, label)`. The wrapper checks `pcall` success only, so an explicit `false` return could be misreported as attached. Its source is corroboration of intended handler shape, **not proof of registration**.
- **Signature interpretation boundary:** the generated pages display `Event.Ability.New.Add(abilities)` while JAB callbacks accept `function(_, abilities)`; the extra callback argument is observed only in the addon source, not independently qualified as a runtime API signature. Do not silently treat the documentation and callback invocation convention as identical.

## What this finding changes—and what it does not

**Now source-qualified:** four historical event payload shapes and an existing addon implementation that expects ability-ID-keyed maps. This narrows an SC-103 open *documentation* question, without introducing any new listener or game operation.

**Still unresolved:** Whether these events fire in the current physical RIFT client; role/character/build binding of any emitted IDs; Add/Remove relation to permanent learning versus role availability; Usable True/False relation to transient target/resource/cooldown readiness; and selected Normal/Legendary identity. A role switch could change event membership without permanently learning or forgetting a spell. A usability change does **not** demonstrate that an ability became unlocked. The Atank native Soul Tree screenshot already shows **0/3, 0/2 and 0/1** Legendary counters; another generic screenshot would not resolve a nonzero selection.

## Offline pre/post event-delta acceptance matrix (no new listener or parser)

**Decision:** Defer a standalone synthetic event-delta harness: RRE has no current `Event.Ability.New.*` consumer or measured live event trace to regress. A simulator would test its own assumed callback shape. Reuse the existing collector's bounded snapshots if future role-bound event observation is separately authorized, and keep event kind and ability-ID keys distinct from opaque values.

**Freshness hazard grounded in existing source:** RRE-owned `addons/RRECollector/abilities.lua` (SHA-256 `d181ba0061a5959474dd3487b41c114f631122375a8b67421817fd54fdc1c510`, lines 18–49, 52–99) sets `captureComplete` only when List is available, bounded enumeration has no ignored/truncated entries, all Detail lookups succeed and player context is present. This is **collector-level completion of the returned current API set**, not a claim that all learnable/future spells were enumerated. `addons/RRECollector/main.lua` (SHA-256 `3aca63c501686fca5ab6bef8a72d81e3b4fe9fdca4ca3558d379e0cf24a1e5c6`, lines 156–180) deliberately **preserves an older complete `latest` and sequence after a later unavailable/incomplete capture**. Therefore a saved `latest.captureComplete == true` alone does **not** qualify a fresh *after* snapshot. The installed generated `Inspect.Ability.New.List` reference (SHA-256 `a07009634f63ab97a81f3d21678312ad050e5eb4a59941484d6da5ab846f37d5`, line 17) calls the result IDs of **available** abilities, not a permanent learned/Legendary set.

**Minimum acceptance gates for a future comparison (none executed):**

1. Preserve separately source-hashed *before* and *after* collector records with `captureComplete=true`, `abilityList.apiAvailable=true`, `abilityList.enumerationComplete=true`, `abilityList.detailFailures=0` and valid player context. Record the **new capture sequence** and bounded frame/real time; do not mistake an old preserved `latest` for a new observation. Require a demonstrably advancing after-sequence and evidence of its creation in the intended session.
2. Bind both records to the same qualified physical process/client executable, character and operator-controlled trial. Record the exact **before and after role slots** (which may intentionally differ), character/effective level and event time interval. A matching `clientVersion` text field alone is not an executable hash.
3. Independently qualify current-client event registration, callback argument placement, each event-kind identifier and time ordering; flag failed/false Attach, unconfirmed Detach, dropped samples or interrupted frame stream. The generated `abilities` values are `variant`; do **not** coerce the historical quoted `true`/`false` into assumed Lua booleans or infer membership from usability.
4. Compare only qualified ability-ID keys against before/after **available-ID** sets, with no unrelated unit/buff payload export. A chosen Legendary variant still needs direct native Soul Tree selection/role evidence or a distinct verified selection-state interface.

| Future observation (if all relevant gates pass) | Narrow permissible result | Forbidden shortcut |
| --- | --- | --- |
| ID absent before, present after; same ID in **Add** | Corroborated available-ID addition for the bound transition | Permanently learned, unlocked or selected Legendary |
| ID present before, absent after; same ID in **Remove** | Corroborated available-ID removal for the bound transition | Permanently unlearned, role lost forever |
| **Usable.True/False** ID without a matching membership delta | Usability-event observation only | Addition/removal or unlock/lock |
| **Add** and **Usable.False** for the same ID (or **Remove** and **Usable.True**) | Preserve independent event channels; inspect final List set | Treat the pair as contradictory or collapse into one state |
| Add and Remove name the same ID; no qualified final List | Intermediate event-key observations only | Stable final ownership or Legendary choice |
| List delta without matching event, or event without matching List delta | Unreconciled sample/timing/signature relationship | Invent a missing event or conclude no change occurred |
| Failed/partial capture, stale sequence, unknown role/build, attach failure or dropped callback | **INCONCLUSIVE**—stop and retain only qualified metadata | Interpret missing IDs/events as negative proof |

These are **future evidence-classification rules**, not synthetic tests or observed 2026 event behavior. RC-30 visual Pin→Undo acceptance, current callback signature qualification, a separate event-observation authorization and current role-bound identity evidence remain blockers.

**Offline-only structural preflight added (2026-11-03):** `tools/read-rrecollector-saved.mjs` (SHA-256 `1d552c0354bc090e12105c2281b5b84fd5e82c7308615a93fc603eab082bc81d`) now emits a diagnostic-only `knownSnapshotReadiness` with fixed reason codes for partial List/Detail data, inconsistent record counts/shapes, zero-based/gapped/extra-key Lua rows, missing player identity/role/clocks/version, or nonpositive/mismatched saved sequence. Its `offlineStructureQualified` flag is **not** live-event or freshness approval: `freshnessVerified`, `processBuildVerified`, `eventDeliveryVerified` and `eventComparisonReady` remain `false` even on a structurally valid single file. Legacy `buildAbilityCrosswalk` rows/counts are unchanged. Tests `tools/verify-rrecollector-saved.mjs` (SHA-256 `7720567da92ef40eda1dd617d58a2273487647d5f59d8e721f841aaca33bf57e`) plus atlas-consumer checks passed **14/14** offline. No two independently flushed captures, event consumer, or current live proof exists.

## Future discriminator (not authorized or performed here)

1. **Preflight first:** complete the separately blocked RC-30 current-toolbar/Pin→Undo acceptance, establish current process/build/role ownership and obtain separate authorization for any event observation. Do not alter another addon or deploy an RRE event listener on this report alone.
2. If later approved, compare a **before/after `Inspect.Ability.New.List()` snapshot** and narrowly captured Add/Remove keys from one *operator-controlled* role-state transition. Keep usability event deltas distinct, label lost samples and failed attachment, and bind every observation to role/time/build. An ID keyed in Add/Remove is a lead to investigate, not a Legendary proof.
3. Do not export unrelated unit/buff identifiers, arbitrary payloads, a full private catalog, or unqualified volatile process state. If source and live event behavior disagree, stop and document the divergence; never infer missing IDs from silence.

**Stop state:** `SC-103` remains blocked on a current role-bound exact identity/selected-state discriminator; `RC-30` remains blocked on live operator Pin→Undo and the quarantined GUI lease. Installed RRECollector **v0.4.10 stays frozen**. No PE analysis, RIFT input/capture, event callback execution, SavedVariables read/write, other-repository edit or installed-addon modification was performed by this source-contract milestone.
