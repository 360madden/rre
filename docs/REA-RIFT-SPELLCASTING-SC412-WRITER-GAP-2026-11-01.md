# SC-412 — Native command-context flag producer: bounded negative result

**November 1, 2026. Status: BLOCKED after two non-decisive bounded probes; keep SC4 active.** REA offline original physical-PC RIFT research only, no game input, process attachment or system modification.

## Source and question

The original local RIFT executable remains SHA-256 `1935a05c9db6d468e34e0055014a4a99c1b5afceb1695884e24600f5c20a4be8`. In [SC-411](REA-RIFT-SPELLCASTING-SC411-CONTEXT-2026-11-01.md), the separate `/cast` and `/use` code paths each read byte `+0x358` of their first pointer input. The `/use` path also reads pointer `+0x340`.

**Question:** can a source-backed producer, setter or constructor for the byte `+0x358` be found cheaply, to distinguish what it means without guessing?

[Source and probe receipt](REA-RIFT-SPELLCASTING-SC412-WRITER-GAP-2026-11-01.json), SHA-256 `efb0a49fc7186ffb0819b6dad5ed472157fb1d73c6eb5a50f632099aedd665ce`.

## Probe 1 — Nearby original-function disassembly

Searched only `.pdata` function starts in the already identified native helper neighborhood, original RVAs **`0x57c000–0x57e000`**. All **38** qualifying function intervals were examined with Capstone, totaling **8,507 original source bytes** (some intervals extend past the window). No function was skipped for excess size.

Exactly four memory operands in that bounded set accessed the nominated offsets:

| Instruction RVA | Source expression | Access |
| --- | --- | --- |
| `0x57cabe` | `mov rcx, qword ptr [rbx + 0x340]` | Read `+0x340`, in function interval `0x57ca20–0x57cb76` |
| `0x57cdc4` | `cmp byte ptr [rcx + 0x358], 0` | Read `+0x358` in cast helper |
| `0x57dba3` | `cmp byte ptr [rbx + 0x358], 0` | Read `+0x358` in use helper |
| `0x57dbac` | `mov rcx, qword ptr [rbx + 0x340]` | Read `+0x340` in use helper |

There were **zero writes to either exact displacement in this 38-interval bounded source region**. This is a *local scan result*, not proof that the field is never assigned elsewhere or that the program lacks a setter. Accesses via an alias pointer, different instruction offset/width, constructor or indirect function can also evade this kind of source search.

The extra `+0x340` read at `0x57cabe` is new structure evidence: a third nearby native routine accesses a related context offset, but still does not name or qualify the object.

## Probe 2 — Dispatcher call-site argument preparation

Verified original bytes from the two SHA-pinned `.pdata` command regions around the selected helper calls:

- Before `/cast` calls helper `0x57cda0` at `0x6c75a8`, **`0x6c7591` executes `mov rcx, rbx`**.
- Before `/use` calls helper `0x57db60` at `0x6c7f98`, **`0x6c7f95` executes `mov rcx, r15`**.

These are first-pointer-argument **source register preparations**, not yet proof that both pointers refer to the same runtime object. The earlier common offset therefore suggests a comparable layout but not a shared C++ class, field name or game-state meaning.

## Research decision

**Park SC-412.** Neither bounded probe supplies a writer, constructor, reliable runtime object type, or link to a spellbook/GCD state. A further indiscriminate full-image search for `0x358` is expressly *not* justified by this evidence. Reopen only on a new discriminator: a specific live observation tied to this byte, verified C++ vtable/class/constructor reference, or an original code path with a localized setter.

**Status boundaries:** SC-411's accepted fact (two context-offset reads) remains valid, but the meaning of `+0x358` and native cast acceptance are unknown. The major SC4 research phase remains **not complete**. SC1 current-level spellbook and SC3 GCD still lack current local-game evidence.

Read-only successful Workbridge jobs: `rea_sc412_local_context_writer_scan_20261101` and `rea_sc412_dispatch_argument_provenance_20261101`. No VM access, no game input, no RR2/Workbridge changes. **Next useful independent task:** compile the accepted client/API/event findings into an **interim source-pinned mechanism map** without treating blocked research as completed.
