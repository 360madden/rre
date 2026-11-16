# WA-006 — source-qualified query-wrapper parent indirection (offline only)

**Checkpoint:** 2026-11-16 ~12:46 EST. **Host:** AMD-DESKTOP independently verified by Workbridge 0.16.5-dev and `hostname.exe` job `rre_20261116_continue_host_01`, exit 0. **Owner:** single RRE manager. **Scope:** archived original PE bytes and existing RRE files only; no live game, VM, debugger, input, installed addon, SavedVariables or other project modifications.

## Exact source and complementary methods

- Offline saved PE: `artifacts/lab2-live-20261107-0922/guest-rift_x64.exe`, 60,493,640 bytes, SHA-256 `1935a05c9db6d468e34e0055014a4a99c1b5afceb1695884e24600f5c20a4be8`, image base `0x140000000`. The filename denotes a **historical saved artifact**, not a VM session or proof of the current physical process.
- Independent worker: original-byte Capstone disassembly, corrected full-function alignment after an initial discarded unaligned subwindow. Jobs `rre_20261116_wa006_worker_wrapper_aligned_02`, `rre_20261116_wa006_worker_callargs_03`, `rre_20261116_wa006_worker_outer_caller_04`, `rre_20261116_wa006_worker_ctorarg_05`, `rre_20261116_wa006_worker_base_ctor_06` all exit **0**. Original wrapper `0xF7CD20–0xF7CF47` is 551 bytes, SHA `ae78a6ae1c6bed37d01a2173c43a265a91c0d8c3c0bc28fd6f585e65c8d33564`.
- Manager independent crosscheck: standard-library-only PE section mapper/direct-call displacement and opcode-byte inspection, job `rre_20261116_continue_wrapper_bytes_fix_02` exit **0**, same executable SHA/window hashes. A first exploratory one-off command `rre_20261116_continue_wrapper_bytes_01` failed exit **1** due to its own incorrectly escaped Python PE-signature literal, not a source mismatch; the corrected job passed.
- Durable independent verifier: [`verify_wa006_wrapper_parent_route.py`](../tools/agents/collision/verify_wa006_wrapper_parent_route.py). Initial job `rre_20261116_wa006_wrapper_verifier_first_01` and independently reviewed, strengthened job `rre_20261116_wa006_wrapper_verifier_pivots_02`, both exit **0**; the latter adds explicit `0x6A649B` (RAX→RDI) and `0x78B2E` (RCX→RBX) pointer-transfer guards after peer-review identified those missing semantic controls: **six SHA-pinned original windows, eleven exact instruction/operand anchors, seven independently recomputed direct-call targets, eleven RAM-only semantic corruption controls rejected**. This does not rely on Capstone, Ghidra or a new import.

## Narrow static result

| RVA | Source-qualified operation | Inference boundary |
| --- | --- | --- |
| `0x6A6484/0x6A6489` | Requests a 0x68-byte query wrapper allocation | Allocation success not observed |
| `0x6A6496/0x6A649B/0x6A64BC/0x6A64EC` | Calls constructor `0xF7CC50`; passes resulting wrapper in RCX to `0xF7CD20` | Conditional caller branches retained |
| `0xF7CC59→0x13E9A60` | Base constructor sets EDI=0 then writes zero to `[wrapper+0x08]` at `0x13E9A7B` | **Who later populates +0x08 is unknown** |
| `0xF7CD57/0xF7CD9C/0xF7CDFE` | Preserves wrapper RCX in RSI, restores it, then directly calls `0x13E9FE0` | Local static argument flow only |
| `0x13E9FE6/0x13E9FED` | Loads `RCX=[wrapper+0x08]`, then directly calls `0x78B1C` | No proven non-null stored value or runtime invocation |
| `0x78B2E/0x78B6E/0x78B7C/0x78B8E` | Reads `[parent+0x88]`, tests WorldManager readiness byte `+0x30`, then conditionally calls `0x8E744` | Query parent not proved to be the constructor's parent |

**Accepted static refinement:** The callback's query wrapper supplies an **indirect receiver slot `wrapper+0x08`** to the previously sourced WorldManager parent-field query path. This narrows the gap between [WorldManager lifecycle](RRE-WA006-WORLDMANAGER-LIFECYCLE-2026-11-16.md) and the known query wrapper, but **does not establish that the two parent receivers are identical or that `0x8F230` is actually dispatched**. No player/shape/gameplay owner, real hit/miss or collision clearance follows.

## Separately completed record-writer falsification

Another independent read-only worker used two exact-build Capstone probes to test a pre-existing candidate-element writer lead:

1. `rre_wa006_recwriter_20261116_allocator_pdata_probe_01`, exit **0**: `0x723CC–0x7247F` (callee reached from `0xD0926`) performs size-scaled array allocation/copy and pointer replacement; not an observed 32-byte record-element `+0x08/+0x14` writer.
2. `rre_wa006_recwriter_20261116_copy_callees_probe_02`, exit **0**: `0x25047A9` resolves to an import thunk; `0x7128C–0x7131D` performs pool deallocation/recycling, not element initialization.

Neither test supports promotion of earlier container-header writes `0xD0828` or `0xD0904` to per-record producers. **Park this lead after two non-decision-changing probes**; do not broad-scan or import the full executable.

## ~15:00 EST addendum — exact dual-path guard in the query caller

A separate read-only Capstone disassembly (`rre_1116_1452_wa006_gate_branches`) and independent standard-library branch/call decoder (`rre_1116_1452_wa006_gate_stdlib_qa`) both passed against the **same archived** 60,493,640-byte PE SHA-256 `1935a05c9db6d468e34e0055014a4a99c1b5afceb1695884e24600f5c20a4be8`. The original 261-byte query window at RVA `0x78B1C` has SHA-256 `3d24fd605664f325b6e1006b6ec75a82efa426e0e13bd746e81974077024c088`.

- At `0x78B6E`, the query receiver's `parent+0x88` pointer is loaded. `0x78B77/0x78B7A` compare it to zero and branch to fallback `0x78B95` when null.
- A nonnull `parent+0x88` whose byte `+0x30` is **zero** passes `0x78B7C/0x78B7F` into direct call `0x78B8E → 0x8E744`; byte **nonzero** branches to the fallback. The byte is an observed gate, not an independently proven gameplay readiness state.
- Fallback starts at `0x78B95`, reads `parent+0xC8` for R9 and `parent+0x80` for RDX (`0x78BBC`), then directly calls descriptor helper `0x78BD0 → 0x9FD68`. The WorldManager path jumps at `0x78B93 → 0x78BD5`, skipping that fallback; both paths rejoin at `0x78BD5`.

This source-level **either/or** relationship connects the already known descriptor fallback to the same guarded caller, rather than treating `0x9FD68` as an unrelated unconditional operation. It does **not** identify the fallback receiver, nonzero `wrapper+0x08` writer, actual virtual dispatch, selected candidate, hit/miss, gameplay object, player, live process or running scene.

The existing RRE verifier was strengthened in place (no broad scan): **6 SHA-pinned source windows, 17 operand/opcode anchors, 8 verified direct calls, 3 branch destinations and 20 RAM-only mutation rejects**, `wa006Accepted=false`. Job `rre_1116_1452_wa006_extended_verifier` exited 0. The independent standard-library check separately rejected 9 branch/call mutation controls. All analysis remained in memory on the archived source; no game, VM, addon, external repository or process manipulation.

## Status and next exact discriminator

- 🟢 **Verified static path:** constructed wrapper → preserved receiver → `[wrapper+0x08]` dereference → guarded parent `+0x88` WorldManager query.
- 🟡 **Unverified P0:** source-backed nonzero setter of `wrapper+0x08`, identity of assigned parent relative to constructor `0x7A248`, actual virtual `0x8F230` dispatch.
- 🔴 **Still blocked:** WA-006 G1–G5, WA-007, ROOT-001 live player/physics owner; RC-30/RC-88 are operator-stopped. No RRE/RR2 discovery-feed promotion.
- **P0:** Follow only a concrete existing class-path reference to `wrapper+0x08` setter; stop after bounded unproductive probes.
- **P1:** When separately approved and coordinated with the current physical RIFT owner, capture **two independently verified nonself API IDs in one native/appearance epoch** and known hit/miss/owner/camera/invalidation receipts. Current historical self-only PID 18092 and nonself PID 51524 must never be joined.
- **P2:** Reuse accepted observations in the file-only inspector, preserving unknowns. No autonomous movement test from static source alone.

**No changes to RIFT client, VM, other repositories, installed addon or private original recordings.** This report and verifier are manager-owned RRE-only continuation evidence.
