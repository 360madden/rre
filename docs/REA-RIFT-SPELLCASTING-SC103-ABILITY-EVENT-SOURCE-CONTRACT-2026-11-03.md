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

## Future discriminator (not authorized or performed here)

1. **Preflight first:** complete the separately blocked RC-30 current-toolbar/Pin→Undo acceptance, establish current process/build/role ownership and obtain separate authorization for any event observation. Do not alter another addon or deploy an RRE event listener on this report alone.
2. If later approved, compare a **before/after `Inspect.Ability.New.List()` snapshot** and narrowly captured Add/Remove keys from one *operator-controlled* role-state transition. Keep usability event deltas distinct, label lost samples and failed attachment, and bind every observation to role/time/build. An ID keyed in Add/Remove is a lead to investigate, not a Legendary proof.
3. Do not export unrelated unit/buff identifiers, arbitrary payloads, a full private catalog, or unqualified volatile process state. If source and live event behavior disagree, stop and document the divergence; never infer missing IDs from silence.

**Stop state:** `SC-103` remains blocked on a current role-bound exact identity/selected-state discriminator; `RC-30` remains blocked on live operator Pin→Undo and the quarantined GUI lease. Installed RRECollector **v0.4.10 stays frozen**. No PE analysis, RIFT input/capture, event callback execution, SavedVariables read/write, other-repository edit or installed-addon modification was performed by this source-contract milestone.
