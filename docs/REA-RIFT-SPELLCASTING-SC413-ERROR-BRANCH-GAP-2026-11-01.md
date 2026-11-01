# SC-413 — Native `/cast` diagnostic predecessor: bounded negative result

**November 1, 2026 (EDT). Status: BLOCKED/PARKED after two bounded source comparisons.** Exact original physical-PC RIFT `rift_x64.exe` SHA-256: `1935a05c9db6d468e34e0055014a4a99c1b5afceb1695884e24600f5c20a4be8` (60,493,640 bytes). No VMware, game input, process attach, memory modification, or executable write.

## Narrow question

Can the original `/cast` unknown-ability message path establish a **native ability-lookup failure predicate**, when compared with the `/use` unknown-item message path as a negative control? The earlier [SC-407](REA-RIFT-SPELLCASTING-SC407-CAST-ENTRY-2026-10-27.md) and [SC-409](REA-RIFT-SPELLCASTING-SC409-COMPARISON-2026-11-01.md) established command entries and message xrefs, not the successful ability resolver. This task did not repeat SC-408 generic helpers or SC-412 `+0x358` field scans.

## Original regions and direct evidence

| Original command slice, end-exclusive | Bytes; SHA-256 | Linear decoded instructions | Three direct UTF-16 error-data references |
| --- | --- | ---: | --- |
| `/cast` RVA `0x6C7450–0x6C7B75` | 1,829; `13c27e22dd45d0c3251efe145fb39887db4bf4461d73599a983132f418122731` | 431 | `0x6C78B2`, `0x6C78DD`, `0x6C7922` |
| `/use` RVA `0x6C7B90–0x6C892D` | 3,485; `a57d0ee6234c49cb4321c8b34e258416d8189341257e9c0c314d9302d717d513` | 817 | `0x6C86A7`, `0x6C86D2`, `0x6C8716` |

The exact source file hash was freshly rechecked in Workbridge job `rre-sc413-source-rehash-20261101-manager-a1`. The original code-slice bytes match SC-409's pinned source hashes; see [machine-readable instruction and command receipts](REA-RIFT-SPELLCASTING-SC413-ERROR-BRANCH-GAP-2026-11-01.json).

### Probe 1 — Six error data references

Source instruction windows around all six RVAs were decoded from the **original executable**. They display closely mirrored sequences for string data construction, length/capacity tests, buffer copying and conditional allocation. Representative verified points:

- Cast: `0x6C78B2 lea rcx,[rip+0x1FEE787]`, then `0x6C78BE call 0x142504857`, length comparisons at `0x6C78C6` and `0x6C78CF`, source literal `lea` at `0x6C78DD` and `0x6C7922`.
- Use: `0x6C86A7 lea rcx,[rip+0x1FEDF32]`, then `0x6C86B3 call 0x142504857`, length comparisons at `0x6C86BB` and `0x6C86C4`, source literal `lea` at `0x6C86D2` and `0x6C8716`.
- Both code regions use matching helper targets `0x142504857` and `0x1425047A9` in these source windows. This makes these literal references **consistent with generic error-text formatting**, not with direct proof that one helper is a cast-specific ability lookup.

This is a source-backed **negative discriminator for the six literal-reference sites**, not proof that no ability resolver exists elsewhere in the command path.

### Probe 2 — Immediate predecessor and negative-control comparison

The bounded predecessor-source windows were decoded and compared without following a whole-image call graph:

- Cast `0x6C7792 cmp rax,rcx`; `0x6C7795 je 0x1406C77B3`; nearby buffer-copy call at `0x6C77AE`. Subsequent branches around `0x6C783B` and `0x6C7864` choose alternative string-storage paths.
- Use `0x6C8593 cmp rbx,rax`; `0x6C8596 je 0x1406C85B2`; nearby matching buffer-copy call at `0x6C85AD`. Subsequent branches around `0x6C862E` and `0x6C8657` choose matching string-storage paths.
- These **local formatting-predecessor branches** compare pointers or string lengths; their visible source instructions do not identify an ability-ID resolver or a server request. The true earlier reason the program reached its unknown-ability diagnostic remains unqualified.

The original command slices do not provide a source-backed link from the observed message-formatting sequences to a proven ability lookup result, spellbook storage, current-cast admission, GCD or server acknowledgement. No broader absence claim is warranted.

## Decision and limits

**Park SC-413 after two distinct bounded comparisons.** The six error-data xrefs and their nearest visible predecessor chains are not a discriminating native ability resolver. Reopen only if a newly verified, narrowly localized producer or branch status, same-build runtime observation, or typed call-site argument supplies a falsifiable ability-identity dependency. Do not broaden into a full-image source sweep.

**Workbridge receipts (all exit 0):**

- `rre-sc413-source-rehash-20261101-manager-a1` — SHA and file length.
- `rre-sc413-manager-diag-xref-blocks-20261101-a1` — both exact source slices and all six immediate error-data xref windows.
- `rre-sc413-branch-predecessors-20261101-manager-a1` — bounded 60-instruction predecessor and incoming local branch compare.
- `rre-sc413-errorblock-entry-20261101-manager-a1` — predecessor pointer/length control windows.

A separate worker request `rre_sc4_errorbranch_sourceprobe_20261101_agent_native` returned **aborted without a job receipt or source output**, and is **not counted** as successful research. Only the manager's verified terminal-job receipts support this checkpoint.

**Next independent evidence route:** review **already-saved local physical-PC RIFT screenshots** for spellbook/soul/role or queue-setting labels with reliable build/character/time provenance. Do not claim a screenshot proves ability eligibility or mode without actually observing the relevant UI and binding it to the recorded API/session. SC1, SC3, SC4, SC5 and SC6 remain open; SC0/SC2 remain the only completed major phases.
