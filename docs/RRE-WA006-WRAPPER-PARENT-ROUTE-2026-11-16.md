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

## ~16:02 EST addendum — two constructor-owned adapter backreferences (new bounded source lead)

Re-entry on independently verified **AMD-DESKTOP** (Workbridge 0.16.5-dev; `hostname.exe` job `RRE1616_1602_hostverify`, exit 0) and a tracked-clean RRE `main` at `52e7721` established no active RRE registered owner and no running Workbridge jobs. All twelve RRE worktrees were checked; historical untracked material (nine main entries, two pathfinding entries, two wire-contract entries) is preserved. FreeBuff/Ollama remain prohibited by the current provider hold; Workbridge code-verification jobs are **not** independent model agents.

A previously unexplored, concrete backreference path in the **same archived** 60,493,640-byte PE SHA-256 `1935a05c9db6d468e34e0055014a4a99c1b5afceb1695884e24600f5c20a4be8` was followed with an original-byte Capstone disassembly and independent standard-library PE/parser checks:

- Base constructor `0x13E9A60` **initializes** `[wrapper+0x08]=0` at `0x13E9A7B`. It conditionally allocates two small adapter objects, stores the same incoming wrapper receiver in each **adapter+0x08** at `0x13E9AB2` and `0x13E9AD8`, and retains the adapter pointers at **wrapper+0x50** (`0x13E9AC3`) and **wrapper+0x58** (`0x13E9AE4`). These are **different +0x08 fields**: a nonzero adapter backreference is **not** a nonzero setter of `wrapper+0x08`.
- Distinct RIP-relative LEAs `0x13E9AAB`/`0x13E9AD1` set adapter vptr addresses `0x2793FE8` and `0x2793FF0`. The original SHA-pinned table points respectively to **method** `0x13EA010` and **method** `0x13EA060`. These are two constructor-installed entrypoints, not proof of any dynamic invocation or complete vtable classification.
- Both methods load their **own adapter+0x08** (`0x13EA025`, `0x13EA075`) and call shared helper `0x13EA0B0` at `0x13EA037`/`0x13EA087`; their separate output paths copy two DWORDs to caller-provided destinations. In that helper, `0x13EA16E` reads **wrapper+0x08** and `0x13EA1BA` reads `[that pointer+0xC0]` before direct callee `0x7D3E4` at `0x13EA1C1`. This establishes **a second, callback-mediated static consumer** of the unresolved wrapper slot, not a producer, a successful raycast or a gameplay owner.

**Original-byte SHA-256 windows:** base constructor `0x13E9A60` 154 bytes `7b34a14cc98573af4d0382f5486178081cf70c2990d5bcab1b72134e0bcabeaf`; adapter A `0x13EA010` 67 bytes `795ed0774017d43101c5145c6466a60a0d1b6c8b0fdc13f26b73ac937a037b9c`; adapter B `0x13EA060` 67 bytes `f61ff24636763b2d41a08acfaa395f9cd58b8abfaa0cf9dc93fa59dd66eaeaab`; helper `0x13EA0B0` 527 bytes `305ca293f882dc55390d552579b2b6ba7c003d5e3904994e7202ce6bfe5640cb`; table `0x2793F58` 160 bytes `2dfc91e5709f35b7cca3ec7afa86a18b117f342286a2c620b091f5c1c4ff85a2`.

**Verification:** Capstone original-byte jobs `RRE1616_1553_wrappersource`, `RRE1616_1553_callbackvptr`, `RRE1616_1553_callbackmethods`, `RRE1616_1553_callbackhelper`, `RRE1616_1553_callbackhelperbody` all exit 0. Independent no-Capstone byte, RIP/branch and direct-E8 check `RRE1616_1553_callbackindependent` exit 0. The **existing** [WA-006 verifier](../tools/agents/collision/verify_wa006_wrapper_parent_route.py) was extended (no replacement tooling): `RRE1616_1602_extendedgate` exit **0**, **10 original SHA windows / 27 opcode anchors / 11 E8 targets / 3 branch targets / 33 in-memory negative controls rejected**; source syntax `RRE1616_1602_ast` exit 0. No runtime event, adapter invocation, nonzero wrapper setter, same-instance WorldManager dispatch, two nonself player identities, physics hit/miss or camera/scene invalidation is qualified. **WA-006/WA-007 and ROOT-001 remain blocked.** RC-30/RC-88 operator-stopped; SC-103/SC-306 blocked; SC-604 interim-complete; no RR2 feed promotion.

**Stop/next discriminator:** The two adapters are **consumers**, so do **not** search their already inspected projection output stores again as if they wrote `wrapper+0x08`. Pursue only a new source-backed **nonzero store to the actual wrapper+0x08**, with verified receiver identity, or a separately approved and owner-coordinated physical observation. No game/process/VM/desktop/input/reload, installed addon, cross-project edit, provider use or remote push occurred.

## ~18:59 EST addendum — false writer leads eliminated and receiver pivots guarded

**Scope:** Independently verified AMD-DESKTOP; archived original x64 PE 60,493,640 bytes SHA-256 `1935a05c9db6d468e34e0055014a4a99c1b5afceb1695884e24600f5c20a4be8`. The existing callback and wrapper source windows remain SHA-pinned. No live source or game/VM action.

| Original RVA | Exact instruction bytes and observed operation | Decision |
| --- | --- | --- |
| `0x6A646D` | `48 89 43 08` — `mov [rbx+8],rax` | Precedes wrapper allocation; **another object**, not proven wrapper+8 writer |
| `0x6A6480` | `48 89 5F 08` — `mov [rdi+8],rbx` | Also precedes `0x6A6484` wrapper allocation and `0x6A6496` constructor; **not** the wrapper field |
| `0xF7CE32` | `41 89 46 08` — `mov dword [r14+8],eax` | Four-byte output write; not saved wrapper receiver in RSI |
| `0xF7CE70` | `41 89 47 08` — `mov dword [r15+8],eax` | Another output write; not wrapper+8 |

Read-only worker jobs `rre_child_setter_bounded_window_xrefs_01` and `rre_child_setter_tight_dataflow_02` both exit **0**, followed by manager independent source-mapped Capstone job `rre_20261116_evening_p0_false_writer_independent_01` exit **0** (all six above RVAs, including allocation/call ordering). The two concrete candidate windows do **not** contain an established nonzero wrapper+8 setter. This is bounded falsification, **not** a whole-program absence proof; park these four false leads.

Separate read-only source check `rre_20261116_evening_wmid_postctor_01` exit **0** examined `0x7B4F1–0x7B5A9` (SHA-256 `1e710cbd785af14ff9538c4e1ed973d2835aae92ea35211099f2e3b7c1c57372`): the already reported `0x7B4FB→0x8E670` constructor and `0x7B500 [parent+0x88]=RAX` remain verified; no `0x8F230` virtual-slot dispatch was observed through the bounded parent-constructor return `0x7B5A8`. This does **not** exclude dispatch elsewhere or prove that the query receiver is the same parent.

**Independent verifier RED→GREEN:** Reviewer `rre_20261116_agentqa_pivot_mutation_witness_01` exit **0** showed that original `0x13E9A82:48 8B D9` (wrapper RCX→RBX) and `0x13EA0D0:4C 8B F1` (helper RCX→R14) were absent as explicit dataflow anchors: RAM-only register-operand mutations were incorrectly accepted by `semantic_check()` despite whole-PE hash safety. Manager added both exact opcode guards and their operand-byte mutations to the **existing** [verifier](../tools/agents/collision/verify_wa006_wrapper_parent_route.py). Manager run `rre_20261116_evening_p0_verifier_29x35_01` exit **0**; independent after-fix witness `rre_20261116_agentqa_pivot_rejection_retest_02` exit **0** now rejects both altered operands; reviewer full gate `rre_20261116_agentqa_fullgate_after_pivots_02` exit **0**: **10 exact source windows, 29 opcode anchors, 11 direct calls, 3 branch destinations, 35 RAM-only negative controls**. Verifier SHA-256 `8238e4f972c42d82f2c4edce7a261b7fdaa5052c14332e03304bc011ec5d5304`, `wa006Accepted=false`.

**Gate status:** WA-006 G1–G5, WA-007 and ROOT-001 remain blocked; source still lacks a nonzero actual wrapper+8 writer, same-runtime WorldManager identity, virtual dispatch, gameplay owner and physical hit/miss. Stop bounded negative routes; next pursue only a *new, source-qualified* writer/dispatch lead or separately approved owner-coordinated physical-RIFT receipt. Do not promote RR2 feed, start RRECollector RC-30/RC-88, use VMware, or repeat these failed writer candidates.
