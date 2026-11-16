# WA-006 — exact-build caller passes its own +0x28 field as container output slot (static only)

**Verified:** November 16, 2026, ~07:11 EST on independently confirmed AMD-DESKTOP (Workbridge `0.16.5-dev`, `hostname.exe` exit 0). **Owner:** sole RRE manager. **State:** accepted *static caller/slot-provenance finding*; WA-006 and WA-007 remain **blocked**. No game, VM, process, debugger, input, reload, installed-addon, SavedVariables, RR2/REA, or remote operation.

## Original executable qualification

- Archived original: `artifacts/lab2-live-20261107-0922/guest-rift_x64.exe`, 60,493,640 bytes, SHA-256 `1935a05c9db6d468e34e0055014a4a99c1b5afceb1695884e24600f5c20a4be8`; image base `0x140000000`. It is an **offline file**, not current process/scene evidence.
- **Newly qualified caller**: RVA `0x8F230–0x8F37A`, 330 bytes, SHA-256 `a97f396a877d5a35db5b39bb0d723ecb599c8f11e716bd6752bb98ba2e52a732`. Original `.pdata` matches this function extent; Capstone decoded all **81/81** instructions to the end.
- Previously qualified callee wrapper: `0x8F204–0x8F22D`, 41 bytes, SHA-256 `67f197e75d675474765f891519b36ea5f4f7c73368b32fac0a7d73b6a2741943`. The two prior arms at `0x8EA08–0x8EBA6` and `0x8ECB4–0x8F1B6` retain original SHA-verified bodies, as reported in [WA-006 alternate constructor](RRE-WA006-ALTERNATE-CONSTRUCTOR-2026-11-16.md).

## New source-qualified argument relationship

| Original RVA | Original instruction | Narrow proof |
| --- | --- | --- |
| `0x8F23F` | `mov rbx,rcx` | Saves the function's incoming receiver in nonvolatile RBX |
| `0x8F2E2` | `lea rdx,[rbx+0x28]` | Supplies the address of that receiver's `+0x28` field as an **output slot** |
| `0x8F2E6` | `lea r8,[rsp+0x30]` | Supplies a distinct stack descriptor |
| `0x8F2EB` | `mov r9,rsi` | Supplies a preserved argument |
| `0x8F2EE` | `mov rcx,rbx` | Passes the **same caller receiver** as callee RCX |
| `0x8F2F6` | `call 0x8F204` | Direct `E8 09 FF FF FF` call; target calculation independently checked |
| `0x8F2FB` | `mov byte ptr [rbx+0x30],0` | Writes a separate receiver-local byte *after* the call; purpose not inferred |

The full source function contains no intervening reassignment of RBX between `0x8F23F` and the call. The prior exact-build proof established that `0x8F204` preserves incoming RDX into either branch; the `0x8ECB4` branch stores its initialized container pointer through that slot at `0x8EDA4`, while the `0x8EA08` branch stores a pointer **or zero** at `0x8EAE3`. **New conclusion:** the caller at `0x8F230` supplies its **own receiver+0x28** as the output field for both conditional branches.

**Crucial non-equivalence:** The other static *query* wrapper at `0x8E7C5` reads `[its incoming RCX+0x28]` before the producer `0xD0944`. There is **no source proof** that the query wrapper's incoming receiver equals the receiver supplied by this `0x8F230` caller, even though the offsets and container layouts are compatible. Do not promote this to an end-to-end producer→query object, a collision owner, or a ROOT-001 player pointer.

## Independent evidence and negative controls

- `rre_20261116_0713_8f204_direct_xrefs`, exit **0**: full original PE hash verified; searched executable PE sections for **only** direct `E8` references to RVA `0x8F204`; found **one raw candidate**, callsite `0x8F2F6`. Capstone confirmed it on an instruction boundary within the `.pdata` function.
- `rre_20261116_0715_8f230_full_disasm`, exit **0**: original 330-byte function SHA and complete 81-instruction disassembly independently checked argument setup and preserved RBX. The raw match does not exclude **indirect** callers or other invocation forms.
- `rre_20261116_0716_receiver_slot_stdlib`, exit **0**: a separate **standard-library-only** PE section and `.pdata` parser verified four original SHA windows, eight exact instruction anchors, unique direct `E8` target, and rejected **2/2 RAM-only mutation controls** (changing the field displacement `+0x28→+0x20` and the direct-call displacement). No source PE was changed or written.

## Gate and follow-up

**WA-006 / WA-007 remain BLOCKED.** Need a *different source-proven connection* showing the query receiver and constructor caller refer to the same actual object, or an independently identified per-record low/high writer; otherwise stop this static route. Physical nonself same-epoch identities, collision hit/miss and restart/scene invalidation still require separate authority and evidence. **ROOT-001 live player ownership remains unqualified.** RC-30/RC-88 remain operator-stopped; SC-103/SC-306 blocked; SC-604 interim complete.

**One concrete next offline action:** inspect a genuinely new, pre-existing source-backed constructor/callsite reference for `0x8F230` that could establish receiver identity, bounded and without broad import. If no discriminator emerges, park the lead rather than repeat scans. The RR2 discovery feed is deliberately unchanged because this is not a live or player-owner result.
