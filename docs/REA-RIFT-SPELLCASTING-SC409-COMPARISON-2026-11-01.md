# SC-409 — Native `/cast` and `/use` command-structure comparison

**Date:** November 1, 2026. **Status: completed at source-backed structural comparison scope; SC4 still active.** REA offline physical-PC RIFT reverse engineering only, no input or live process attachment.

## Build and provenance

Physical installed RIFT `rift_x64.exe` original SHA-256 `1935a05c9db6d468e34e0055014a4a99c1b5afceb1695884e24600f5c20a4be8`, size 60,493,640 bytes. Command callback pointers previously established by SC-407: **`cast` RVA `0x6c7450`** and **`use` RVA `0x6c7b90`**. These are native **new-build** RVAs, not absolute runtime addresses.

[Machine-readable comparative code census](REA-RIFT-SPELLCASTING-SC409-COMMAND-COMPARISON-2026-11-01.json), SHA-256 `35795cd9963d6ac43284d00389a1bf01653b8ef2fe3a86e43469af5b9c04489e`. It retains each source interval hash, all bounded direct-call sites and targets, indirect-call sites, literal references, and overlapping/shared/direct-difference sets.

The original PE `.pdata` verifies three contiguous unwind records for each of the two **investigative code regions**:

| Native command | Source RVA interval, end-exclusive | Source bytes | Source SHA-256 | Direct calls / indirect calls |
| --- | --- | ---: | --- | ---: |
| `/cast` | `0x6c7450–0x6c7b75` | 1,829 | `13c27e22dd45d0c3251efe145fb39887db4bf4461d73599a983132f418122731` | **39 / 5** |
| `/use` | `0x6c7b90–0x6c892d` | 3,485 | `a57d0ee6234c49cb4321c8b34e258416d8189341257e9c0c314d9302d717d513` | **75 / 10** |

Both Capstone x64 linear decoded regions reached their last `.pdata` boundary in the record. Adjacent unwind intervals do **not** themselves prove one semantic source-language function; the regions are curated source-code slices, not claimed decompiled interfaces.

## New discriminating result: shared helpers versus command-specific helpers

Comparing sets of direct call **targets** (not total sites):

- **17 target RVAs appear in both command regions**, including `0x7de6f0`, `0x7078e0` and `0x7ddd00`. This makes a cast-only interpretation of those generic helpers **less plausible**, independent of the earlier 192-byte `0x7de6f0` wrapper finding.
- **7 target RVAs appear in only the cast slice**: `0x126edc4`, `0x1272c18`, `0x4cb3d0`, `0x54ed40`, `0x57cda0`, `0x5a5ff0` and `0x5affe0`.
- **18 target RVAs appear in only the use slice**, including `0x57db60`, `0x54eca0`, `0x54ee30`, `0x62f650` and `0x8ee040`. This difference is a **source scope** statement; it does not establish that a unique helper itself accepts a game/server cast request.

**Key interpretation:** an argument-forwarding thunk shared by `/cast` and `/use` is unlikely to be a uniquely spell-specific dispatcher merely because `/cast` calls it. The new comparison is an independent discriminator for parked SC-408 findings, but it does **not** retroactively qualify the ability resolver.

Source-backed diagnostic divergence:

- `/cast` reads UTF-16LE `ABILITY` at RVA `0x26b6030` and error text `Could not cast unknown ability: [%ABILITY]` at RVA `0x26b6040` (three machine instruction references to the error string).
- `/use` reads error text `Could not use unknown item: [%ITEM]` at RVA `0x26b65e0` (three machine instruction references).
- These are **literal reporting paths**; no actual target game response, GCD rule, spellbook listing, cooldown lock, or server packet is established from the strings.

## Specific next offline hypothesis

**SC-411 candidate pair:** source compare cast-specific helper `0x57cda0` (callsite `0x6c75a8`) with use-specific `0x57db60` (callsites `0x6c7f98` and `0x6c8063`), perhaps identifying what the command-specific paths prepare. The two RVAs are close in the same original executable, but nearby placement is not proof of related semantics. A valid next step needs bounded `.pdata` function ranges, original bytes, distinct data references and a **discriminating result**; if no direct ability/item identity difference is observed, park after the source-bounded probe instead of opening an unbounded graph.

**Milestone SC-409 is complete only as a reproducible structural comparison.** Native ability list, actual `/cast` submission, GCD, queue and server acknowledgement remain open. This contributes to SC4 but does not complete that entire major phase.

## Receipts

Original byte/X64 source-comparison jobs `rea_cast_use_differential_20261101`, `rea_cast_use_pdata_inventory_20261101`, `rea_cast_use_closest_errors_20261101`, `rea_sc409_comparison_machine_20261101` and `rea_sc409_comparison_review_20261101` passed. No executable modification, game input, guest access or RR2/Workbridge source changes.
