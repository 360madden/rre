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

## Next gate

Keep the release **source-only** until reviewed version-matched v0.4.14 installation/load proof and one newly authorized, peer-coordinated Lab-2 manual Capture with RREC2 and SavedVariables parity. **Do not use the returned Lab-2 lease**. RC-30's original physical v0.4.10 Pin → Undo → Reload strict same-trial gate remains historically incomplete. SC-103 Legendary/Protector's Fury identity, SC-306 remaining queue values and SC-604 extended native semantics are not resolved by this work.
