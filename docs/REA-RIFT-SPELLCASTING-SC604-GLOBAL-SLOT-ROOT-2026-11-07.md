# SC-604 — global pointer-slot provenance of six guarded reference sources (November 7, 2026, ~03:08 EST)

**Owner:** single RRE manager. **Verdict:** the native helper `0x1333200` returns the address of one global pointer *slot*, not the pointed-to object. Its nonzero fast path and initialization-like cold path converge on **RVA `0x33E0AB0`**. This newly qualifies the first indirection shared by the six previously observed initializer paths; it does **not** prove one stable runtime object instance, ability ID, Legendary state, or cast acceptance.

## Exact source and methods

- Original physical RIFT executable: `C:\Program Files (x86)\Glyph\Games\RIFT\Live\rift_x64.exe`, length **60,493,640 bytes**, SHA-256 **`1935a05c9db6d468e34e0055014a4a99c1b5afceb1695884e24600f5c20a4be8`**. Hash rechecked independently by both methods. These RVAs apply to **this file build only**, not an unqualified VMware guest or live process.
- First bounded method: `rre_20261107_0305_decode_ro` (exit 0), offline PE/Capstone decode from the existing RRE Python environment. It decoded `0x1333200–0x133329A` and the first cold initializer `0x49FD2B–0x49FD6C`. No imports, files or processes changed.
- Independent verification: `rre_20261107_0318_sc604_slot_stdlib_final_ro` (exit 0), Python 3.14 **standard library only**, independently parsed the PE header, section ranges, original byte anchors and RIP/rel32 targets. **21/21 checks passed**, including a misaligned-opcode negative control and detection of a zero-filled PE virtual tail. The two earlier verifier drafts failed due to an incorrectly escaped PE signature and an attempted on-disk read of a **virtual-only** address; neither was a RIFT-code failure. Their job IDs were `rre_20261107_0314_sc604_slot_stdlib_ro` and `rre_20261107_0316_sc604_slot_stdlib_corrected` (exit 1); do not count them as passes.

## Fresh byte-qualified facts

| RVA | Instruction / observation | Narrow inference |
| --- | --- | --- |
| `0x1333206` | `cmp qword ptr [rip+0x20AD8A2], 0` | Tests eight-byte global slot at `0x33E0AB0` for zero. |
| `0x133320E` | `jne 0x133328E` | Nonzero value skips the slower initialization-like sequence. |
| `0x1333210` | `call 0x1339EC0` | Slow sequence obtains an upstream value; semantic type unresolved. |
| `0x1333234`, `0x133326B` | Each `call 0x2030EF0` | Helper invoked with slot-address-related arguments, but side effects are **not** yet proven. |
| `0x133325E` | `lea rbx, [rip+0x20AD84B]` | RBX holds **address of the same global slot** `0x33E0AB0`. |
| `0x1333285` | `mov rax, rbx` then return | Slow path returns the **slot address**. |
| `0x133328E` | `lea rax, [rip+0x20AD81B]` then return | Fast path returns the **same slot address**. |
| `0x49FD44` | `call 0x1333200` | Cold initializer obtains this slot address. |
| `0x49FD4D` | `mov rdx, [rax]` | Caller then loads the **pointer value** from the slot. |
| `0x49FD50` | `add rdx, 0x960` | Supplies an interior address to `0x171BFF0`; object type and `+0x960` meaning remain unknown. |

**PE-section nuance:** The slot `0x33E0AB0` lies in the **virtual-only tail** of `.data` (section RVA `0x2F56000`, virtual size `0x695660`, raw size `0x40BC00`). It has **no corresponding file-initialized eight-byte value**. Standard PE image loading zero-fills such virtual space; this is **not a reading of the current game memory** and does not establish lifetime ownership, synchronization, subsequent writes or value persistence.

The [six verified cold cache initializers](REA-RIFT-SPELLCASTING-SC604-SIX-REFERENCE-INITIALIZERS-2026-11-07.md) each call `0x1333200` before the `0x171BFF0` wrapper and load from six distinct downstream DWORD offsets. This step qualifies that they call a **common slot-address getter**. It does not establish that the calls ran, that they observed identical pointer contents, that the wrapper returned the same object, or that the six DWORDs are abilities.

## Proof limitations and next discriminator

This is static code/PE evidence, not native runtime tracing. The effects of `0x2030EF0`, the identity of the pointed-to object, meaning of `+0x960`, real cache mutations, any GCD/queue mapping and game-side results are **unverified**. **SC-604 remains an accepted interim mechanism; SC-103 and SC-306 remain blocked.** RC-30 strict same-trial A/B/C/D/pre-Pin persistence remains incomplete; a later v0.4.11 UI/SavedVariables receipt cannot close the historical v0.4.10 acceptance gap.

**Next optional owner-cleared work:** narrowly trace `0x2030EF0`'s storage effect or the value originating from `0x1339EC0`, only after checking for overlap with active REA/RR2. Do **not** relaunch broad imports or infer live object identity. No RIFT input, UI reload, process action, installed addon or SavedVariables write, desktop lease/quarantine override, cross-repository modification or push was performed.
