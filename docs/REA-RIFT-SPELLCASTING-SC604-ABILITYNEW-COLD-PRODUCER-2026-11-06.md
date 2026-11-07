# SC-604 — cold-path source of castbar `abilityNew` output +0x40 (November 6, 2026, 20:07 EST)

**Owner:** sole RRE manager. **Gate:** SC-604 remains interim; this is static exact-build evidence, not a runtime cast result. Follow-up to [the hot-region +0x39 note](REA-RIFT-SPELLCASTING-SC604-CHANNEL-ZERO-CFG-2026-11-06.md).

## Source and independent verification

- Physical original `C:\Program Files (x86)\Glyph\Games\RIFT\Live\rift_x64.exe`: 60,493,640 bytes; SHA-256 **`1935a05c9db6d468e34e0055014a4a99c1b5afceb1695884e24600f5c20a4be8`** freshly asserted; no process opened.
- Existing RRE .venv Capstone/pefile decoded all three qualified producer unwind ranges: `[0x91DED0,0x91E2B6)` (253 instructions), `[0x91E2B6,0x91E2F8)` (13), `[0x91E2F8,0x91E4D9)` (127): **393 contiguous instructions**. The prior hot-only scan ended before the new write.
- Independent Python 3.14 *stdlib-only* PE section mapper, without Capstone, pefile or RR2 code, asserted **6/6** raw encodings: `0x91DEF9: 44 89 6D AF`, `0x91E090: 89 45 AF`, `0x91E49F: 8B 45 AF`, `0x91E4BA: 89 47 40`, `0x9B8767: 8B 8C 24 A0 00 00 00`, `0x91E47F: 41 8B 87 08 03 00 00`.
- Read-only Workbridge receipts, **5/5 exit 0, no truncation:** `rre_20261106_2008_sc604_out40_triple_region_ro`, `rre_20261106_2010_sc604_cold_write_branch_ro`, `rre_20261106_2011_sc604_stack51_refs_ro`, `rre_20261106_2012_sc604_plus40_cfg_defs_ro`, `rre_20261106_2012_sc604_plus40_raw_bytes_ro`.

## Producer value path

| RVA | Instruction | Narrow observation |
| --- | --- | --- |
| `0x91DEF3` | `xor r13d,r13d` | Clears R13D before local initialization. |
| `0x91DEF9` | `mov dword ptr [rbp-0x51],r13d` | Initializes the stack local to zero. |
| `0x91DEFD` | `mov rdi,r8` | Saves third-argument output pointer in RDI (usual x64 nonvolatile convention). |
| `0x91E083` | `call 0x58B30` | Helper call with unknown semantic contract and side effects. |
| `0x91E090` | `mov dword ptr [rbp-0x51],eax` | Reachable optional replacement with call result. |
| `0x91E49F` | `mov eax,dword ptr [rbp-0x51]` | Cold epilogue reloads the local. |
| **`0x91E4BA`** | **`mov dword ptr [rdi+0x40],eax`** | **Direct producer write to output +0x40.** |
| `0x9B8767` | `mov ecx,dword ptr [rsp+0xA0]` | Consumer B reads output +0x40 relative to its qualified buffer base `rsp+0x60`. |

`0x91E47F` separately loads `[r15+0x308]` into EAX to classify nearby flags; **this is not the +0x40 source**, because `0x91E49F` overwrites EAX before the final store.

A bounded instruction CFG across the three ranges has **393 nodes, 446 direct edges, zero unresolved direct branch targets**. Modeled paths from producer entry to `0x91E49F/0x91E4BA` pass through the zero initialization at `0x91DEF9`; the optional overwrite at `0x91E090` is reachable but does not dominate. A forward two-definition analysis reaches the reload with `zero_init` or `helper_result`. This analysis treats calls as returning and all conditional branches as potentially feasible. It does **not** model indirect/exceptional flow, alias writes, callee side effects or live values; hence this is a candidate *static* provenance rather than a guaranteed runtime two-value classification.

**Finding:** A direct producer +0x40 write is now source-qualified in the *cold* unwind region, narrowing the prior `abilityNew` origin gap. The two castbar consumers' conditional key-setting patterns were established in the [field-key note](REA-RIFT-SPELLCASTING-SC604-LUA-FIELD-KEYS-2026-11-06.md). Neither the helper's meaning nor a current ability/Legendary ID, successful casting, queue enum, runtime truth of `abilityNew`, or telemetry correctness is proven.

## Gates and next discriminating step

`SC-604` **interim**; `SC-103` Legendary/Protector's Fury and `SC-306` queue enum **blocked**; `RC-30` strict same-trial Pin→Undo→Reload receipt **incomplete**; `RC-32` physical Retry/startup **unverified**; `NAV-002` remains RR2-owned. Only if nonoverlapping with RR2, a future narrow read-only check can qualify `0x58B30` result handling and the `0x49FA20` conditional consumer branch. Avoid repeated parked scans, broad imports and assumed live semantics.

No independent model agent launched: available fixed FreeBuff `sc103/rc30` reviewer prompts were exhausted on unchanged questions, and Workbridge command slots do not constitute reasoning agents. No game input, reload, process manipulation, addon/SavedVariables modification, quarantine override, external repository write, package install or native function invocation.
