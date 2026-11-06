# SC-604 — exact-build channel byte and castbar zero-source crosscheck (2026-11-06, 18:53 EST)

**Owner:** single RRE manager; static, source-only examination. **Gate:** SC-604 remains *interim*. This note refines two explicit uncertainties in [the November 6 field-key crosscheck](REA-RIFT-SPELLCASTING-SC604-LUA-FIELD-KEYS-2026-11-06.md); it does not establish runtime Lua behavior or successful casting.

## Source qualification and method

- Read-only original physical PC executable: `C:\Program Files (x86)\Glyph\Games\RIFT\Live\rift_x64.exe`; size **60,493,640 bytes**, SHA-256 **`1935a05c9db6d468e34e0055014a4a99c1b5afceb1695884e24600f5c20a4be8`**, freshly computed and asserted.
- Existing RRE virtual-environment Capstone/pefile decoded exactly two known PE unwind-bounded regions: producer `[0x91DED0,0x91E2B6)` (**253 continuous instructions**) and consumer B `[0x9B84F0,0x9B88CD)` (**218 continuous instructions**). No game process or memory was opened; no broad native scan.
- A separate **stdlib PE-section RVA→raw-offset** mapper independently asserted exact bytes for four anchors, without using pefile mapping: `0x91E066: 88 47 39`; `0x9B85C5: 0F 57 FF`; `0x9B86BD: F3 0F 5F C7`; `0x9B86E6: 0F 2F C7`. All four passed.
- Read-only Workbridge job receipts: `rre_20261106_1859_sc604_field_origins_ro` (exit 0; no truncated output), `rre_20261106_1900_sc604_local_branch_ro` (exit 0; untruncated), `rre_20261106_1905_sc604_xmm7_cfg_ro` (exit 0; untruncated).

## Finding A — channel-associated byte has a direct producer write

The producer hot region contains **`0x91E066: mov byte ptr [rdi+0x39], al`**; its recorded bytes `88 47 39` independently match the original PE. The nearby straight-line sequence includes `0x91E053 movzx r14d,r14b`, `0x91E05C cmovne r14d,eax`, `0x91E060 movzx eax,r14b` and `0x91E064 xor al,1`. Thus the stored byte is a branch-dependent transformed boolean-like value, not an assumed literal RIFT `channeled` API truth value.

The earlier two castbar consumers read output `+0x39` in the conditional `channeled` field-setting pattern. **New delta:** a direct producer-side write to the same buffer-relative byte now exists in a qualified hot instruction span; previously its source was uncertain. This is a static local producer→consumer correspondence, not an exhaustive proof that this write executes on every path. Producer output `+0x40` was **not** directly written through `rdi` or `r8` within this examined hot span; indirect writes, calls and other producer unwind regions remain possible, so `abilityNew` origin stays unresolved.

## Finding B — the consumer-B zero register has a dominating definition

The full qualified consumer-B region contains `0x9B85C5 xorps xmm7,xmm7`, preceding the `0x9B86BD maxss xmm0,xmm7` and `0x9B86E6 comiss xmm0,xmm7` uses. A bounded instruction-level intraprocedural control-flow graph of all **218** decoded instructions contained **234 edges**, zero unresolved jump destinations, and established both uses reachable from region entry but **neither reachable if `0x9B85C5` is excluded**. The backward jump from `0x9B886A` to `0x9B85D0` bypasses initialization only on re-entry; it does not create an entry-to-use path avoiding initial zeroing.

Only five instructions within this region explicitly mention `xmm7`: prologue save, zeroing, the two uses and epilogue restore. No intervening instruction in the region explicitly overwrites the register. **Subject to ordinary Windows x64 nonvolatile XMM7 preservation by called functions and no unmodeled exceptional/external entry into the middle of the function**, consumer B compares the `+0x2C` value against zero and `maxss` uses zero as its other source. For ordinary finite values, the latter bounds the float at a zero floor. No timebase, expiry semantics, NaN policy or runtime condition has been established. The prior note's `XMM7 source unqualified` caveat is narrowed for *this consumer B region*, not for other functions.

## Limits and gate

The graph does not model exceptions, indirect native call side effects, external jumps into the middle of the owner, or interprocedural source identity. Neither a local byte write nor CFG dominance proves a complete live casting chain, standard Lua helper identity, reliable external telemetry, current Legendary ID, queue enum or server behavior. `abilityNew +0x40` producer origin remains open. **SC-604 stays interim; SC-103/SC-306 blocked; RC-30 strict same-trial receipt incomplete; RC-32 physical operation unverified.** No native navigation, RR2, REA-Lab1, installed addon, SavedVariables or live RIFT state was changed.

**Next discriminating research:** source-qualify where producer `+0x40` is initialized across its separate unwind/call paths, or independently prove the remaining `+0x39` control dependencies. Avoid repeating exact-key scans or treating static labels as validated game values.
