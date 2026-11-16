# WA-006: Split candidate-handle construction and virtual selector input (static only)

**Verified:** 2026-11-16, ~03:56 EST, independently identified **AMD-DESKTOP** via `hostname.exe` (Workbridge job `rre_20261116_0348_host`, exit 0). **Owner:** the sole RRE Manager. **Status:** source-qualified *local data flow only*; WA-006 remains **blocked**. No RIFT process attach/control, game input, VM, UI, installed addon, SavedVariables, RR2 source or network interaction.

## Exact source boundary

- RIFT x64 **on-disk executable**, 60,493,640 bytes, SHA-256 `1935a05c9db6d468e34e0055014a4a99c1b5afceb1695884e24600f5c20a4be8`, image base `0x140000000`.
- The original **producer** `0xD0944..0xD1074`, 1,840 bytes SHA-256 `2f37be6b71b566885610faa92f6bf0c1a210dc821a4c459ce985cf39d2b566fe`.
- The original **selector** `0xA2514..0xA26D2`, 446 bytes SHA-256 `ea78e0b39823e7ae154144f11e0d31a9acb794f8acfbfb9a4087e83255bba973`.
- Source `.rdata` descriptor table `0x278C980`, 64-byte SHA-256 `dea4f646f9944c1acf36b364687f96ff2e5476e2414c19197247067f08d9606f`; its slot `+0x08` points at selector `0xA2514`. A matching static slot is **not** proof that this particular virtual dispatch occurred at runtime.
- New persistent verifier: `tools/agents/collision/verify_wa006_candidate_pointer.py`, source SHA-256 `33393cca4b98673f72e2fe092755fd7c49a8680b2b9f827aa8a38e77876310d8` (at this verification). Reuse instead of another broad scan.

## Newly verified 32-byte record → selector path

The producer uses a masked index and stride to form a record field address: `0xD0CBF` masks `EBX`, `0xD0CC9` multiplies it by `0x20`, and `0xD0CE0` computes `RBX = R15 + index*0x20 + 0x14`. `R15` was originally read from `[RDX+0x20]` at `0xD09A6`; this is a **candidate buffer source**, not a proven physics or gameplay owner.

Two **nonadjacent** 32-bit candidate-record fields form a temporary 64-bit value:

| Original RVA | Verified instruction | Meaning relative to the 32-byte record |
| --- | --- | --- |
| `0xD0D4B` / `0xD0D55` | `mov eax,[rbx-0xC]` then `mov [rsp+0x1B8],eax` | low 32 bits from record `+0x08` |
| `0xD0D5C` / `0xD0D65` | `mov eax,[rbx]` then `mov [rsp+0x1BC],eax` | high 32 bits from record `+0x14` |
| `0xD0E90` / `0xD0EA3` | `mov r8,[rsp+0x1B8]` then `call [rax+0x08]` | combined value supplied as an argument to a conditional virtual dispatch |
| `0xA2527` / `0xA252A` | `mov rdi,[r8]`, `mov rsi,r8` | selector interprets `R8` as a pointer to an object-pointer slot; retains original `R8` |
| `0xA2646` / `0xA2684` | `mov rax,[rdi]`, `call [rax+0x40]` | zero-`R9` selector branch calls an **unresolved concrete** virtual method |
| `0xA2687` / `0xA2695` / `0xA2699` | stack-flag check, status `1`, `mov [rax+0x50],rsi` | on the conditional success path, scratch `+0x50` stores the original combined `R8` |

The other `R9 != 0` branch uses `[rax+0x48]` at `0xA2656` and follows the status-`0` return at `0xA2659`. The current finding therefore narrows the concrete-owner question to the **split source fields** and the dynamic object/vptr loaded through `R8`; it does **not** identify a player ID, geometry collision owner, raycast hit, or the wrapper's output `+0x60`.

## Independent checks and limitations

- `rre_20261116_0348_pointer_chain_negative_controls`: **exit 0**, independently decoded **21 original opcode+semantic anchors**, checked the 32-byte stride and the two half-stores, and rejected two **RAM-only** instruction mutations (producer low-half store and selector `+0x40` call). The mutations were evaluated by anchor checks independent of the whole-PE SHA gate.
- `rre_20261116_0348_new_pointer_verifier`: **exit 0**, persistent verifier reproduces the same 21 anchors and two negative controls, with both window hashes, descriptor hash and PE guard.
- `rre_20261116_0348_prev_query_crosscheck`: **exit 0**, previously accepted separate exact-build verifier still qualifies 9 windows/1,036 instructions/19 prior anchors/5 direct calls and explicitly rejects gameplay/world ownership.
- **No live observation or class RTTI/vptr proof.** The 64-bit value is treated as a pointer-like handle in this static selector path, but its actual runtime validity, concrete method implementation, downstream `result+0x60` binding, same-epoch player/scene identity, collision hit/miss and RR2 live qualification are **unknown**.

## Next bounded decision

Investigate whether an **existing exact-build** constructor, assignment or local vptr source proves the concrete object reached via `[R8]` and the `+0x40` callee. Prefer narrowly source-hashed candidate record producers/consumers; do **not** repeat broad PE imports/scans or promote this into `docs/RR2-DISCOVERY-HANDOFF.md` as ROOT-001. Only a *new, independently qualified current-player owner chain* should alter that feed. Preserve RC-30/RC-88 and all game-input stops.
