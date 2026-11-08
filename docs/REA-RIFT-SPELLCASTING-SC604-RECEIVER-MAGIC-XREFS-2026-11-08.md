# SC-604 — Exact-build receiver-magic cross-reference check (November 8, 2026, 09:08 EST)

**Scope:** One new, bounded, read-only source-code discriminator following the previously accepted `0x12EA3BC` selector preflight. **SC-604 remains interim.** No table owner, selector meaning, cast lifecycle or server behavior is assigned.

## Pinned source and method

- Original physical-host `C:\Program Files (x86)\Glyph\Games\RIFT\Live\rift_x64.exe`, **60,493,640 bytes**, SHA-256 **`1935a05c9db6d468e34e0055014a4a99c1b5afceb1695884e24600f5c20a4be8`**. This is a *disk-source* check and does not freshly attest the Lab-2 guest/process.
- Exact little-endian DWORD `A3 0D F2 BD` (value `0xBDF20DA3`) was counted with **two separately invoked byte-search methods** over the matching executable. They agreed on **eight** file offsets, each mapping into `.text` by direct PE section-header parsing. The **full 7-byte containing instruction** at every site was independently decoded with pre-existing Capstone, not inferred solely from a 4-byte hit.
- Verified eight sites: **five comparisons** and **three writes** to the same relative structure offset `+0x78` (register differs by site). This is a bounded exact-file literal census, **not** an exhaustive list of all runtime writes or aliases.

| Instruction RVA | Decoded operation | Qualification |
| --- | --- | --- |
| `0x12E0EE0` | `cmp dword ptr [rcx+0x78], 0xBDF20DA3` | Comparison only |
| `0x12E278B` | `cmp dword ptr [rcx+0x78], 0xBDF20DA3` | Comparison only |
| `0x12E2A31` | `cmp dword ptr [rbx+0x78], 0xBDF20DA3` | Comparison only |
| **`0x12E301E`** | **`mov dword ptr [rcx+0x78], 0xBDF20DA3`** | Literal writer; nearby code preserves input registers and conditionally branches |
| **`0x12E328F`** | **`mov dword ptr [rbx+0x78], 0xBDF20DA3`** | Literal writer; following instructions also write `+0xAC`, `+0x88`, `+0xA4`, `+0x148` |
| **`0x12E832D`** | **`mov dword ptr [rbx+0x78], 0xBDF20DA3`** | Literal writer; following instructions put `0` at `+0xAC`, `1` at `+0x88`, `0xFF` at `+0xA4`, `0` at `+0x148` |
| `0x12E85B1` | `cmp dword ptr [rbx+0x78], 0xBDF20DA3` | Comparison only |
| `0x12EA41D` | `cmp dword ptr [rdi+0x78], 0xBDF20DA3` | Previously qualified selector-preflight comparison |

## Independent checks / retained command receipts

1. `rre_20261108_0910_sc604_magic_xref_bounded_01`: **exit 0**. SHA/length matched; regex and direct byte searches found the same eight hits; PE section RVA mapping printed. This first pass is a search/census, not instruction semantics.
2. `rre_20261108_0914_sc604_magic_writers_decode_ro_01`: **exit 0**. Pre-existing Capstone decoded three exact writer instructions; raw immediate comparisons and **two negative controls** passed at each site. The 64-byte writer-window SHA-256 values, respectively: `bf90a9c02ab1015c0ea3297780ded64f253cb03112e6e14c4a15b0a70cce56b1`, `7e4e4ef8543c6a63ea5f2d10880707eb4ff8dbeff0735a7dfad5f4400634c21e`, `ffea52d3516d93701af824ddcb35b559f64e7e6c2f50ec4f93deac41e98b7b64`.
3. `rre_20261108_0917_sc604_magic_eight_instruction_ro_01`: **exit 0**. All **8/8** seven-byte instructions matched decoded comparison/write class, `+0x78` displacement, literal value and complete eight-hit census.

**Interpretation:** The previously unidentified preflight magic at receiver `+0x78` is initialized at three original-code sites. In particular, two stores share nearby `+0xAC/+0x88/+0xA4/+0x148` writes, providing a **specific structure-layout lead** for independent receiver provenance. These may be different branches of related code; **do not claim three distinct constructors, object types or live instances**. The literal could be a sentinel; its precise meaning and the owning subsystem are unproved. No direct link to ability identity, Legendary Protector's Fury, Ability Queue modes, spellcasts or server acceptance is established.

**Stop/next discriminator:** Reuse these exact RVAs only when an independent receiver type/owner or source-qualified runtime artifact appears. Do **not** widen into `0x12CCA58`, perform a broad callgraph sweep/full Ghidra import, or treat static stores as live behavior. Physical RC-30, SC-103, SC-306, Lab-2 SC-629 and NAV-002 gates are unchanged. No game input, UI reload, process control, addon/install, external repository or SavedVariables change occurred.
