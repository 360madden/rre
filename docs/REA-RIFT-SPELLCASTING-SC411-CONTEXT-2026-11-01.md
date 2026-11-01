# SC-411 — Shared native command context offsets in physical-PC RIFT

**November 1, 2026. Status: completed as bounded native context-data discovery.** This is an original-binary source result, **not** a qualified meaning for the flag or a complete SC4/GCD/request implementation.

## Original new-build evidence

Physical PC installed RIFT executable SHA-256 `1935a05c9db6d468e34e0055014a4a99c1b5afceb1695884e24600f5c20a4be8`. The comparisons came from the **cast-only** source helper called from native `/cast` at code RVA `0x6c75a8` and the **use-only** helper called from native `/use` at RVA `0x6c7f98`.

[Machine-readable source-instruction and unwind evidence](REA-RIFT-SPELLCASTING-SC411-CONTEXT-OFFSETS-2026-11-01.json), SHA-256 `751b800b730c3e5b57ff5d772eaad8d05c5c31e101d4d39cfe84220ce8fef211`.

| Verified original helper | Exact original RVA region | Byte length and SHA-256 | Decoded source evidence |
| --- | --- | --- | --- |
| Cast-specific call target `0x57cda0` | `0x57cda0–0x57d028` | **648** bytes, `ceae85fe884756bf1897e7cf4ab3cca026d3373cca7bbd43940a83370286023b` | 169 instructions, three contiguous `.pdata` spans, **12** direct calls |
| Use-specific call target `0x57db60` | `0x57db60–0x57dbd7` | **119** bytes, `7f581827f1c97db0e5c600f3d436bc76b07c5bc65fcaf0073e0057afa2e2da24` | 32 instructions, one `.pdata` span, **4** direct calls |

Original byte-bound Capstone decode completed at each final `.pdata` end; the larger exploratory cast-window that crossed into the next unrelated interval was not used as this milestone's authoritative function range.

## Specifically observed shared offset

~~~asm
; Native RVA 0x57CDC4 inside the cast-only source helper
cmp byte ptr [rcx + 0x358], 0

; Native RVA 0x57DB7E inside the use-only source helper
mov rbx, rcx

; Native RVA 0x57DBA3 inside the use-only helper
cmp byte ptr [rbx + 0x358], 0

; Native RVA 0x57DBAC in the use-only helper
mov rcx, qword ptr [rbx + 0x340]
~~~

The cast helper explicitly tests byte **`+0x358`** from its first pointer input (Windows x64 `RCX`). The use helper copies that first pointer argument from `RCX` to `RBX`, then tests byte **`+0x358`** from the same argument pointer, and subsequently reads a pointer from **`+0x340`** before further work.

This **proves two separately identified command code paths access the same numeric context offsets** of their respective first pointer inputs. It motivates a shared **data-layout hypothesis**, but not yet a claim that the same runtime object/class/instance is passed to each command. The `+0x358` byte could be a mode, gate, initialization state or unrelated flag; without code/dataflow or observed behavior **its meaning is unknown**. It does **not** establish GCD, spell acceptance, transport, resource eligibility or queue state.

## The next meaningful REA question

**SC-412 hypothesis:** find one source-backed producer/writer of the `+0x358` field on this command-context type, or a source-instruction/test linking a named gameplay state to its branches. Start from the current **verified caller/parameter flow**, not a broad full-PE search for byte displacement `0x358`. Do not guess the flag is `isCasting`, `inCombat` or `canUseAbility` from the offset alone. If no discriminating write/caller appears after two distinct bounded probes, park this hypothesis with a source hash.

SC-411's **single milestone result is complete** as evidence of native dataflow. The wider SC4 phase is **still open**, and the actual internal spellbook, native ability submission and GCD clock remain unresolved.

**Execution records:** `rea_sc411_helper_pair_pdata_20261101`, `rea_sc411_cast_helper_context_20261101` and `rea_sc411_exact_context_machine_20261101` passed. No live game process was running at the earlier November 1 host status check. No game input, process attach, VM, file replacement, RR2/Workbridge modification or full Ghidra import.
