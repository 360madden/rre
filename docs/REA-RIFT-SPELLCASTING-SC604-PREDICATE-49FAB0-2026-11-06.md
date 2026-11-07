# SC-604 — exact-build predicate gates for conditional castbar `abilityNew` (November 6, 2026, ~23:30 EST)

**Owner:** sole RRE manager. **Scope:** independent, bounded offline read of the *physical* RIFT executable; no game, process, installed addon, SavedVariables or other repository changes. **Status:** SC-604 remains an accepted **interim** static mechanism.

## Provenance and methods

- Original physical `C:\Program Files (x86)\Glyph\Games\RIFT\Live\rift_x64.exe`: **60,493,640 bytes**, freshly verified SHA-256 `1935a05c9db6d468e34e0055014a4a99c1b5afceb1695884e24600f5c20a4be8`. Addresses here are **RVAs** for only this exact executable, not VM offsets.
- Reused the previously qualified `0x49FA20 -> 0x49FAB0` call and [consumer-gate analysis](REA-RIFT-SPELLCASTING-SC604-ABILITYNEW-CONSUMER-GATES-2026-11-06.md). This step resolves a *new* question about the second predicate; it does not redo the proven `0x58B30` leaf.
- Workbridge read-only Capstone/pefile jobs `rre_20261106_2327_sc604_49fab0_disasm_ro`, `rre_20261106_2330_sc604_predicate_cfg_ro`, `rre_20261106_2333_sc604_predicate_core_ro`: **3/3 passed, exit 0, untruncated**. Decodes entered at instruction-aligned `0x49FAB0` and the independently traced continuation at `0x49FB4B`. Nearby exception-unwind entries include `[0x49FAB0,0x49FAD7)`, `[0x49FAD7,0x49FC78)`, `[0x49FC78,0x49FCD4)`, and the separate cold/initialization range `[0x49FCD4,0x49FEDE)`. These are **unwind regions**, not necessarily four independent functions.
- Independent Python 3.14 **standard-library only** verifier `rre_20261106_2335_sc604_predicate_stdlib_ro`: **21/21 exact RVA byte anchors, 6/6 direct rel32 call targets, 10/10 conditional branch targets**, plus a deliberate misaligned-anchor negative control, **exit 0**. It parsed raw PE section headers itself; no Capstone/pefile/RR2, running process or live memory. Negative control only checks exact-address anchoring, not all possible false positives.

## New static branch/value findings

| Code RVA | Directly decoded instruction sequence | Narrow result |
| --- | --- | --- |
| `0x49FAD7–0x49FB45` | Preserves second argument in `RDI`, first DWORD in `R15D`; reads `GS:[0x58]` thread-local pointer and tests six separately addressed DWORD globals against its DWORD; greater-than branches enter cold initialization paths. | Guarded initialization / global values occur; their source meaning and live initialization state are not established. |
| `0x49FB4B–0x49FB81` | From `[rdi]` + `0x588`, calls `0x49A8D0`, optionally `0x49AC90`, yielding a candidate begin/end pair at `[rbp-0x49]` / `[rbp-0x41]`. | Candidate DWORD sequence boundaries, not a certified list type or ability taxonomy. |
| `0x49FBD0–0x49FBF5` | Iterates DWORDs in 4-byte steps and compares each element to **six** values read from RIP-relative globals. Each equal branch targets **`0x49FC45`**. | **One positive-result route is a match against one of six reference values**, subject to valid pointers and reached branch. |
| `0x49FBF7–0x49FC3F` | On no equality match, calls `0x49A020`, uses `0x54ED40`, reads a byte at `[rcx+rax+0x18]`, tests against `0xFF`, optionally follows an `[rax+0x78]` indexed pointer, and calls `0x5AF690` with `R15D` as the second argument. Null paths and zero result branch to `0x49FC49`. | **A separate fallback success route depends on pointer/table resolution and nonzero return from `0x5AF690`**. No semantics are assigned to the index, helper, or object. |
| `0x49FC41` / `0x49FC45` / `0x49FC49` | Both success routes set `BL=1`; fallback failure clears `BL=0`. | Two statically distinct candidate paths to positive and one to negative result. |
| `0x49FCBB–0x49FCD3` | `movzx eax,bl`, stack-cookie check `0x24E11C0`, epilogue, `ret`. | On ordinary return, output is **0 or 1**, barring unmodeled exception/error behavior. |
| `0x49FCD4–0x49FEDE` | Six cold branches use repeated initialization helpers and jump back into the earlier compare/loop paths. | A hot-only decode misses part of the predicate's reachable code. |

**Consequence for `abilityNew`:** Previous exact-build research established that consumer B forwards producer output `+0x40` to `0x49FA20`, which requires a nonnull intermediate and a positive `0x49FAB0` response before subsequent conversion/field-setting. We now have two *static* routes to that predicate's positive result: **six-way equality over a candidate DWORD sequence, or an object/table predicate via `0x5AF690`**. This is substantially more specific than a generic “unknown boolean gate,” but **does not** establish a Legendary ability identity, a known/learned spell, accepted cast, Lua field value, numeric queue mode or GCD.

## Proof limitations / no-go

No runtime path feasibility, pointer ownership, all exceptional branches, callee side effects or data types were proven. The six RIP-relative reference values are not yet semantically classified, and `0x5AF690` is not characterized. Even exact code cannot establish whether the current RIFT session traverses either positive path. SC-604 remains **interim**; **SC-103/SC-306 blocked**, **RC-30 strict same-trial archival evidence incomplete**, **RC-32 physical v0.4.11 Retry behavior unverified**, NAV-002 with the separate RR2 owner. Do not retry the resolved `0x58B30` or literal-ID scans. Any next offline step should select **one** previously unqualified `0x5AF690` or six-reference origin discriminator and independently source-hash it; stop if it overlaps active RR2/REA research or repeats an existing probe.

No new reasoning-model agents were launched: available RRE FreeBuff modes had been used on their fixed unchanged review questions; Workbridge commands are *not* model agents. No game input, RIFT reload, process manipulation, installed addon/SavedVariables edit, desktop lease override, other repository write, package installation or remote push was performed.
