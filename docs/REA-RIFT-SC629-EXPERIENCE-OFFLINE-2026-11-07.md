# SC-629 — RRECollector v0.4.14 Experience integration (offline source gate)

**Status:** ✅ Offline source/test gate passed on November 7, 2026. ⚠️ **No v0.4.14 game deployment, loaded proof, live Experience data or acceptance**. Base RRE main commit was `5f284a1`. The 0.4.13 Lab-2 trial remains the latest live collector evidence.

## What changed

The existing single manual `abilities.collect()` Capture opts in to `snapshotContext(true)`; candidate lookup and API capability probes call `snapshotContext()` and never look up Experience. One independently protected `Inspect.Experience()` lookup/invocation reads only `accumulated`, `needed`, and `rested` via individually protected access. Finite numbers (including zero) survive; missing, wrong type, nonfinite and throwing members are omitted as unknown. Missing/thrown/non-table API returns `capabilities.experience=false` and no map; successful empty/partial tables set true. Existing `Inspect.Stat()` is not duplicated.

RREC2 v0.4.14 now strictly requires the ninth boolean capability with an optional bounded numerical map. v0.4.12 and v0.4.13 contracts and v0.4.13 race/raceName/zone metadata stay compatible. The JavaScript SavedVariables adapter enforces the same version/flag/map binding; it recognizes a literal Lua `{}` as an empty Experience object **only** for v0.4.14 and true capability. The Lab-2 decoder permits a *declared* v0.4.14 version, but this does not grant permission to acquire memory.

## Focused verification

| Check | Observed result |
| --- | --- |
| Real SHA-pinned host Lua 5.1.4 context/call/failure fixture | ✅ 16 assertions |
| Host Lua 5.1 wire publisher, malformed cases, lifetime | ✅ 46 assertions |
| Node saved-data parser and version/capability regression | ✅ 12/12 |
| .NET 10 production RREC2 contract-only checks | ✅ 79/79 |
| Lua producer → Python partition/hash → .NET reader | ✅ 1 synthetic Experience publication, 2 frames, exact decoded context |
| Historical saved fixture, explicitly retagged .13 → .14 with `experience=false` | ✅ 54 records, 5 frames, exact decoded context/counts |
| Strict addon TOC/package source gate | ✅ 11 source files; **not** installed-copy parity |
| Roadmap validator | ✅ 47 tasks / 11 milestones / 0 failures |

**Provenance:** `artifacts/sc629-v014-lua51-20261107-2246/receipt.json` (SHA-256 `29aebb683b4362ceb4083e5b48743fd8967e448791fc7a0b4c09eecb0126b6d2`), source hashes, actual Lua executable/DLL hashes and test outputs. Machine-readable summary: [SC629 offline report JSON](REA-RIFT-SC629-EXPERIENCE-OFFLINE-2026-11-07.json). No external model agents were launched under the current FreeBuff/Ollama hold.

**Known limitation:** The full C# suite reached 152 checks, then an independent Lab-2 controlled-child exercise failed `lab2-capture-only`; the production-only contract suite independently passed 79/79. No claim is made that the entire C# integration suite passed. The latest matching-build `Inspect.Experience` reference names the three members without explicit member-type annotations; numerical types are a strongly supported migration inference, not observed live types.

## November 8, 2026 — saved-version acceptance discriminator (offline only)

A new bounded, read-only three-case test reused the existing SavedVariables adapter fixture and production `exportSavedSnapshot` code. **All 3/3 assertions passed** (Workbridge job `rre-run11-sc629-version-triage-20261108`, Node exit 0). The adapter intentionally returns **both** the root `savedAddonVersion` and the `latest` capture's `addonVersion` without imposing equality:

| Synthetic source | Adapter parse | Strict v0.4.14 acceptance gate |
| --- | --- | --- |
| Root `0.4.14`, latest `0.4.14` with `experience=false` | Passed | **Version pair qualifies** |
| Root `0.4.14`, stale latest `0.4.13` | Passed | **Reject as v0.4.14 Capture evidence** |
| Root `0.4.11`, latest `0.4.14` with `experience=false` | Passed | **Reject as version-inconsistent receipt** |

This is deliberate archival compatibility, **not an adapter defect**. Independently, `main.lua` sets root `RRECollectorData.addonVersion` at SavedVariables load but preserves an older complete `latest` until a successful manual Capture, so a root-only version check is insufficient. For the future authorized Lab-2 SC-629 trial, compare **both fields** to `0.4.14` and separately verify installed/loaded source hashes, current UI-bound Capture, RREC2 session/sequence and current process/build identity. Equality alone does not prove fresh capture or gameplay semantics. No game/VM/install/other-repository operation, source modification or live qualification occurred.

## November 8, 2026 — same-version capture can lack a live wire generation (offline negative control)

A new **source-extracted** Windows Lua 5.1.4 trial executed the actual v0.4.14 `recordCapture` function and `wire.lua` without RIFT or a SavedVariables file. Eight assertions passed (Workbridge job `rre_20261108_1148_sc629_pair_wire_neg_lua51_02`, exit 0):

- A **complete** API capture with malformed UTF-8 in a Detail name replaced the saved `latest` at sequence 9, leaving **both** root and capture versions `0.4.14`. Wire serialization rejected the data (`memoryPublication.status=failed`, reason `utf8`) and left `RRECollector_WireFrames=nil`. Thus version-pair equality and a complete saved catalog do **not** prove any matching RREC2 publication.
- A corrected complete capture at sequence 10 published frames with a `complete` receipt. Re-executing the actual `wire.lua` as a synthetic addon reload cleared frames and set its **in-memory** receipt to `not-published/addon-load`; the retained synthetic saved root, `latest`, and prior saved `memoryPublication` receipt still looked complete **before** the real SavedVariables load callback. In production source, that callback refreshes the saved receipt from `wire.receipt()`. No real load callback or game reload was performed.
- An independently invoked, source-hash-pinned Node branch review passed **12/12** checks including two in-memory negative controls (job `rre_20261108_1150_sc629_source_branch_ro_01`, exit 0). The source SHA-256 values were `main.lua=72f84c09cd37fbdc97748af65458b59d73535d129b67afbbe2b92d2c3dbdf1fe` and `wire.lua=16a4cdcecb4f20bf4bc39eeb34b241fc5b7261a5b05b4c67be8827a44e95fd0d`. The first Lua test command (`rre_20261108_1144_sc629_pair_wire_neg_lua51_01`) exited 1 because the synthetic fixture omitted a local `root` variable; the corrected test passed. No product failure is inferred from that fixture error.

**Acceptance consequence:** For SC-629, matching root/latest version numbers are **necessary but insufficient**. Require a **current-load**, operator/UI-bound, full RREC2 generation with matching session/sequence and source/build identity; separately correlate SavedVariables. Neither an old `memoryPublication` receipt nor a higher saved sequence substitutes for observed active wire frames. This is an offline counterexample, **not** v0.4.14 live installation, RIFT behavior, or acceptance. No source, installed addon, VM, process, or other repository was changed.

## November 8, 2026 — distinct real-clock values can alias the RREC2 session token (offline negative control)

A bounded **read-only**, source-extracted Lua 5.1.4 check independently qualified an additional collision mode beyond repeating *identical* initial inputs. Original `hex`, `hash32` and `newSession` functions were extracted in memory from `addons/RRECollector/wire.lua` SHA-256 `16a4cdcecb4f20bf4bc39eeb34b241fc5b7261a5b05b4c67be8827a44e95fd0d`. Host interpreter was the existing SHA-256-pinned `artifacts/sc103-lua51-msvc-20261104-1925-v1/lua.exe` (SHA `6675a1c46671d8bbdfea2b94704c495a2cb9e7accaffbb309f85c025752c2c67`).

The exact Lua function generated the **same** token `009896800dfb38d2ab0d88ab3cb152f6` for two *synthetic* records with identical player, sequence, frame time and version but **different** `realTime` values of `10000` and `4304967.296` seconds. These differ by `4294967.296` seconds (one full `2^32`-millisecond modulus); the first token component explicitly uses `math.floor(realTime * 1000) % 4294967296`. Negative controls changing real time by one millisecond, frame time by one second or player ID each changed the token. Independent Node BigInt modulo/negative checks corroborated the arithmetic. Workbridge job `rre_nov8_1440_sc629_session_wrap_direct_ro_a1` exited **0**, untruncated.

**Limit:** This is a mathematical, **synthetic**, full-source-function counterexample, not a collision observed in RIFT or proof that the serialized frame payloads would be identical: `realTime` is separately present in the encoded context. It adds an explicit distinct-clock alias case to the existing warning that the 32-character token is not a fresh-load authenticator. **No new acceptance gate or task promotion:** SC-629 still requires separately verified current build/process, loaded addon, UI-bound Capture, complete active RREC2 generation and version-matched SavedVariables. No source/installed-addon/VM/process changes occurred.

## November 8, 2026, 22:49 EST — source-executed SavedVariables load callback, not live

Two **in-memory synthetic-event** trials executed the **unchanged real** `addons/RRECollector/main.lua` on the existing SHA-pinned Windows Lua 5.1.4 interpreter. The first used a mocked `wire.receipt()` and passed **24/24** assertions (job `rre_20261108_2251_sc629_source_load_event_ro_01`, exit 0). The second also executed the **real** `addons/RRECollector/wire.lua` alongside `main.lua` and passed **26/26** (job `rre_20261108_2254_sc629_realwire_load_event_ro_01`, exit 0). Original source SHA-256: main `72f84c09cd37fbdc97748af65458b59d73535d129b67afbbe2b92d2c3dbdf1fe`, wire `16a4cdcecb4f20bf4bc39eeb34b241fc5b7261a5b05b4c67be8827a44e95fd0d`; Lua executable SHA `6675a1c46671d8bbdfea2b94704c495a2cb9e7accaffbb309f85c025752c2c67`.

In both v0.4.13→v0.4.14 and v0.4.14→v0.4.14 simulated loads, the real SavedVariables callback accepts only identifier `RRECollector`, updates the **root** version, retains the prior `latest` object and its own historical version, and replaces an old **saved** `memoryPublication` receipt with the current `wire.receipt()` value (`not-published/addon-load`). Real `wire.lua` initialization separately cleared synthetic preexisting `RRECollector_WireFrames`. Wrong-addon and duplicate-event controls passed. This closes an *offline callback coverage gap* left by the earlier isolated wire-reload trial, not the possibility of stale saved catalogs or independently retained memory copies.

**Proof limits:** Event delivery and the surrounding runtime were mocked; no real RIFT load, SaveVariables flush, installed-file comparison, guest process observation, active memory acquisition or UI-bound Capture occurred. The test does not prove a fresh addon load from a saved receipt, a real full publication, or the absence of stale heap copies. SC-629 remains **source-only/pending**; the accepted live version remains v0.4.13. No source or installed files changed.

## Next gate

Keep the release **source-only** until reviewed version-matched v0.4.14 installation/load proof and one newly authorized, peer-coordinated Lab-2 manual Capture with RREC2 and SavedVariables parity. **Do not use the returned Lab-2 lease**. RC-30's original physical v0.4.10 Pin → Undo → Reload strict same-trial gate remains historically incomplete. SC-103 Legendary/Protector's Fury identity, SC-306 remaining queue values and SC-604 extended native semantics are not resolved by this work.
