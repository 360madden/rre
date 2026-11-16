# WA-006 — source-qualified WorldManager lifecycle and parent-field query linkage

**Date:** 2026-11-16 ~09:25 EST. **Host:** independently verified AMD-DESKTOP via Workbridge 0.16.5-dev and `hostname.exe`, exit 0, job `rre_20261116_0918_host`. **Owner:** sole RRE manager. **Scope:** bounded offline analysis of preserved executable bytes; no physical client, VM, process, debugger, game input, addon, SavedVariables or other repository touched.

## Source identity

Original saved `artifacts/lab2-live-20261107-0922/guest-rift_x64.exe`: 60,493,640 bytes, SHA-256 `1935a05c9db6d468e34e0055014a4a99c1b5afceb1695884e24600f5c20a4be8`, image base `0x140000000`. This is exact-build static evidence, **not** current physical process or live-owner qualification.

## New independently checked static chain

1. **Conditional parent-field producer:** In a bounded excerpt of original function `0x7A248–0x7B5A9`, `0x7B4C9/0x7B4CD` may bypass WorldManager construction and `0x7B512` stores **zero-valued `R15`** at `[RDI+0x88]` (the parent constructor independently sets `R15D=0` at `0x7A261` and preserves its incoming receiver as `RDI` at `0x7A272`). On the construction branch, `0x7B4F1` supplies the parent pointer `RDI` as `RDX`; `0x7B4F4` supplies the prospective object pointer as `RCX`; `0x7B4FB` directly calls constructor `0x8E670`; `0x7B500` then stores the returned pointer at **`[parent+0x88]`**. Do not infer a live successful allocation or branch from this code alone.
2. **Concrete WorldManager constructor:** `0x8E670–0x8E6E3` zeroes **`[object+0x28]`** at `0x8E686`, stores the incoming parent pointer at **`[object+0x20]`** at `0x8E694`, installs primary vptr `0x278CA10` at `0x8E698/0x8E69F`, and initializes **`object+0x30=1`** at `0x8E6B7`. Prior independent RTTI proof resolves `0x278CA10` as `hkpKdTreeWorldManager`, with virtual slot `+0x18 → 0x8F230`; see `RRE-WA006-WORLDMANAGER-VTABLE-2026-11-16.md`.
3. **Conditional candidate-container publication:** On entry `0x8F230` saves its receiver, passes address **`[same receiver+0x28]`** to wrapper `0x8F204` at `0x8F2E2/0x8F2F6`, then resets **`[same receiver+0x30]=0`** at `0x8F2FB`. The wrapper's conditional arms may publish the candidate-container pointer **or zero**; `0x8F230` remains a virtual method with **no proven runtime dispatch**.
4. **Parent-field consumer and readiness gate:** Independent caller `0x78B1C–0x78C21` saves its own incoming parent receiver in `RBX`, loads **`RCX=[RBX+0x88]`** at `0x78B6E`, checks non-null and **`byte [RCX+0x30]==0`** at `0x78B77–0x78B7F`, and only then invokes `0x8E744` directly at `0x78B8E`. The query wrapper uses **`RDX=[RCX+0x28]`** at `0x8E7C5` and invokes geometry-candidate producer `0xD0944` at `0x8E7E0`. Otherwise, the outer caller uses a separate `0x9FD68` fallback. This establishes a concrete **parent+0x88 producer/read path and WorldManager field+0x28/+0x30 lifecycle compatibility**; it does not prove both parent invocations act on the same runtime instance.
5. **Cleanup corroboration:** The WorldManager deleting-destructor-style slot `0x8F1B8` calls `0x8EC24` at `0x8F1C7`. That function conditionally passes its receiver's `+0x28` pointer to `0x8E7F0`, and restores other vptrs. Precise allocation/free semantics beyond the displayed calls remain unqualified.

**What changed relative to the previous checkpoint:** Previous reports had the class/vptr for `0x8F230` and its output-slot pointer, but had not tied the class constructor and the **parent-field `+0x88` publication** to the **parent-field `+0x88` query reader and `+0x30` readiness predicate**. Source-level reuse is now materially stronger; live collision, player identity, and actual dispatch are **still unproven**. A bounded parent-constructor vptr check found `0x7A28E/0x7A295` installs `0x278B078`, but there was no `.rdata` function-pointer match for query caller `0x78B1C`. Thus the producer's parent class and the query caller's receiver class/instance are **not** proven identical.

### Original byte windows

| Context | RVA range | Bytes | SHA-256 |
| --- | --- | ---: | --- |
| Parent query caller | `0x78B1C–0x78C21` | 261 | `3d24fd605664f325b6e1006b6ec75a82efa426e0e13bd746e81974077024c088` |
| Conditional parent constructor excerpt | `0x7B4B0–0x7B530` | 128 | `45a45bf4658da3e853f06bba850841e18f15eec4cba0bb8b660e1551a63a9cbc` |
| WorldManager constructor | `0x8E670–0x8E6E3` | 115 | `f5b9f4f8843909deff70d0edc7ce902a144aabd114c6ab10d642f073c2abf03d` |
| Inner query wrapper | `0x8E744–0x8E7ED` | 169 | `84493c16cc018b254698dd8a1d37406f6e7ee3150d1e407bc232cd5608014274` |
| WorldManager virtual candidate initializer | `0x8F230–0x8F37A` | 330 | `a97f396a877d5a35db5b39bb0d723ecb599c8f11e716bd6752bb98ba2e52a732` |
| Cleanup method | `0x8EC24–0x8ECB3` | 143 | `3caeb02524c0adc8004e0f78700ba64969d41342fa8ae7655e14e19972700914` |

## Verification receipts

- Original exact-PE SHA and bounded `.text`/unwind-aware `LEA` cross-reference search, `rre_20261116_0918_worldmgr_vptr_xref`, exit **0**: `0x8E698` and `0x8EC33` reference WorldManager vptr `0x278CA10`; independent positive control `0x8E74B` references visitor vptr `0x278C980`. Xrefs are instruction-decoded, not arbitrary raw-byte matches.
- Capstone original function decoding `rre_20261116_0918_worldmgr_fn_disasm` and bounded caller-context decoding `rre_20261116_0918_worldmgr_context`, both exit **0**.
- Bounded direct-call and pointer Xrefs `rre_20261116_0918_worldmgr_caller_xref`, exit **0**: `0x7B4FB→0x8E670`, `0x78B8E→0x8E744`, `0x8F1C7→0x8EC24`; zero direct `E8` to `0x8F230` (does not rule out virtual dispatch).
- Independent **standard-library-only** PE parser `rre_20261116_0918_worldmgr_stdlib_proof`, exit **0**: checks exact whole-file SHA, **17 opcode anchors**, **4 recomputed direct-call destinations**, vtable reference and six original window hashes; **4/4 in-memory changes rejected** at `0x7B503`, `0x78B71`, `0x8F2FD`, `0x8E69B`. Does not modify the source PE.
- Worktree/register inventory `rre_20261116_0918_repo_registers`, exit **0**: 12 RRE worktrees; only earlier unrelated untracked artifacts on main, historical pathfinding and wire-contract worktrees.

## Confidence boundary and decision

**Source-proven:** WorldManager vptr constructor; object `+0x20` parent association; initial `+0x28` null; parent `+0x88` store and later conditional read; virtual method's `+0x28` output-slot address; `+0x30` readiness transition; eventual query wrapper's `+0x28` consumption. **Not established:** same *live* parent, `0x8F230` dispatch in a real session, success branch, concrete `+0x40` candidate implementation, gameplay or shape owner, valid raycast/collision, physical hit/miss, two same-epoch nonself API IDs, camera/restart qualification, current-player ownership. **WA-006 and WA-007 remain blocked; ROOT-001 is not qualified.** No RR2 discovery-feed entry is justified.

**Next bounded step:** if a new source-backed caller/dispatch proves that the WorldManager `+0x18` method executes before the parent `+0x88` query on an instance, inspect that one dispatch. Otherwise **park static expansion** and await separately authorized passive physical-game evidence; do not scan unrelated Havok classes or run broad imports. RC-30/RC-88 remain operator-stopped; SC-103/SC-306 blocked; SC-604 interim-complete.

**Safety/ownership:** No game input, reload, VM, process attachment, desktop lease override, debugger, installed-addon or other-repository changes. Independent Workbridge commands are *not* reasoning agents; FreeBuff/Ollama hold remains in force.
