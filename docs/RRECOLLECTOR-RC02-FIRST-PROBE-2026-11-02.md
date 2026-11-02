# RC-02 — First physical-PC runtime capability probe (2026-11-02)

**Result:** ACCEPTED as one operator-attested `/rre probe` SavedVariables receipt from RRECollector **v0.2.0**, schema **1**. The original `RRECollectorData.latest` known-ability catalog remains separately present and complete. **SC-102 remains BLOCKED** on matching physical-PC spellbook/soul/trainer/action-bar UI; no enumerated future/learnable/locked spell set was produced.

## Provenance and source qualification

- The game operator reported **“probe done”** in this conversation after the requested physical-PC in-game `/rre probe`/`/reloadui` workflow. Origin is **operator-attested**: no contemporaneous process-ID or executable-SHA binding was obtained, and file mtime is a persistence time rather than the in-game invocation instant.
- Saved file (raw/private, **not committed**): `C:\Users\mrkoo\OneDrive\Documents\RIFT\Interface\Saved\<account>\Deepwood\Atank\SavedVariables\RRECollector.lua`. One matching file found under the bounded character path.
- Current SavedVariables file: **31,081 bytes**, SHA-256 **`242259d4f20709574b45676ed6a6ebdaef64e5a8d99b22341abb5291bccdfb12`**, last modified **`2026-11-02T00:33:34.850Z`**.
- Captured player: **Atank**, level **45**, `warrior`, combat role `tank`, role slot **1**. API client internal **`STABLE-1-1178-A-1256632`**, external `1.0.0`, build label **`Oct 23 2026 11:32:27 RIFT-BUILD-12`**.
- `probe.addonVersion="0.2.0"`, `probe.schemaVersion=1`, `probe.sequence=1`, `probeSequence=1`, scope explicitly `api-capability-only-not-learnability-or-actionbar-contents`.
- Installed v0.2 source/host hash parity was already **7/7** before this operator run; see [RC-02 installation receipt](RRECOLLECTOR-RC02-PROBE-INSTALL-2026-11-02.md) and code commit `8d41ed8`. This saved receipt establishes runtime execution/persistence at the user's stated origin, not a new PE hash claim.

## Actual in-client documentation and type results

`Inspect.Documentation()` reported **`index-available`**: **1,910** entries inspected (below the 2,048 cap), **22** relevant names matched and retained, **1,888** ignored, **0** truncated, `scanLimitReached=false`, **0 documentation errors**. These are count/provenance checks, not a comprehensive guarantee that no other API could expose the desired facts.

| Current-client path | Direct type / documentation | Decision |
| --- | --- | --- |
| `Inspect.Documentation` | `function`; index returned | Current-runtime API documentation access **proven** |
| `Inspect.Ability.New.List`, `Inspect.Ability.New.Detail` | Both `function`; existing old `latest` has 69/69 output | Preserve known-ability producer; not future unlock catalog |
| `Inspect.Role.List`, `Inspect.TEMPORARY.Role` | Both `function`; List description returned | Role context supported, already available in collector |
| `Inspect.Setting.List`, `Inspect.Setting.Detail` | Both `function`; descriptions returned | Generic settings enumeration/detail documented, **not called**; exact queue-mode key unknown |
| `Inspect.Queue.Status` | `function`; description returned, excerpt truncated | Documentation describes queues such as `global` and `auctionfullscan`, **not proved** as the player's spellcast queue or `Full/Short/None` setting |
| `Inspect.Queue.Handler` | `function` | No game-queue semantics inferred |
| `Inspect.Soul.List`, `Inspect.Soul.Detail` | Both `nil`; named documentation status `other`/return type `nil` | **Absent at these exact paths**, no justified soul-points producer |
| `Inspect.Action.List`, `Inspect.Action.Detail` | Both `nil`; named documentation status `other`/return type `nil` | **Absent at these exact paths**, no justified action-binding producer |
| `UI.Native.Soul`, `UI.Native.BarMain`, `UI.Native.Ability` | All `table` | Native UI frames exist; **no proof** of enumerated tree points, action slots, or eligibility |

The 22 retained names additionally include the native BarBottom1–6, BarSide1–4, BarPet and BarTemporary identifiers. Name presence is a frame/API index observation, **not** slot-content access. No arbitrary `Inspect.Setting`, `Inspect.Action`, `Inspect.Soul`, or game-control functions were invoked by this probe.

## Existing catalog integrity

The same new saved file contains a separate `latest` table still marked addon v**0.1.0** and client build **`STABLE-1-1178-A-1256632`**. A bounded read counted **69** `lookupId` ability records with **69** unique IDs. Its stored `abilityList` says `rawEntries=69`, `uniqueCount=69`, `detailCount=69`, `detailFailures=0`, `duplicates=0`, `ignored=0`, `truncated=0`, `enumerationComplete=true`, and `captureComplete=true`. The original November 1 file hash `abbf08e8108faa2a9c85d1a61f9c4ab63070ee5ac9a29a041ebd83c058090482` is a **previous full-file SHA**, not the expected current SHA after adding `probe`; byte-for-byte comparison of the entire old `latest` table was not attempted.

## RC-03 decision and next evidence gate

**No `souls.lua`, `eligibility.lua`, or `bars.lua` should be implemented from this probe alone.** None of the tested direct soul/action functions exists, and native frame tables do not expose evidenced point allocations, trainer locks, or action-bar entries. A generic settings API exists, but it does not close SC-102; a later **separately justified** read-only query for one documented `ActionBars_AbilityQueue` setting could be considered for SC-3 if its exact exposed key and relevance are established. Do not broadly dump all settings merely because List/Detail exists.

**Primary next action (RC-04 / SC-102):** operator-provided **same physical PC, Atank, role slot 1** screenshots of spellbook, selected souls/point allocation, class trainer, and action bars; keep source-time/build/role caveats and classify known, learnable, locked, usable, and bound separately. A fresh 69-ability API capture is unnecessary solely to recover already-preserved records. Until qualifying UI arrives, SC-102 and SC1 remain blocked; no UI-derived eligibility has been inferred.

## Evidence jobs (all exited 0)

- `rre-rc02-operator-savedvar-discovery-20261102-a1`: one character SavedVariables file, size/hash/mtime, `latest` and `probe` detected.
- `rre-rc02-savedvar-probe-structure-20261102-a1`: v0.2 probe, client version and exact function documentation.
- `rre-rc02-savedvar-probe-tail-20261102-a1`: exact index counts, path types, role and scope.
- `rre-rc02-savedvar-original-catalog-20261102-a1` and `rre-rc02-savedvar-catalog-integrity-20261102-a1`: 69/69 prior catalog fields, unique IDs, current SavedVariable SHA.
