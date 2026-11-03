# SC-401 — bounded physical-PE review of Lab1's shared manager constructor and distinct globals

**Date:** 2026-11-03. **RRE claim:** `M1-XP-002` in [cross-project evidence index](REA-RIFT-SPELLCASTING-CROSS-PROJECT-EVIDENCE-INDEX-2026-11-03.json).
**Scope:** accepted as a **static architecture lead**, not a live spellbook, current Legendary selection, or validated runtime pointer. SC-401 stays parked; SC-103 stays blocked.

## Provenance and source identity

- Committed Lab1 report `C:\work\REA-Lab1\NATIVE-L1-026.md`, original commit `5774d02408a945f352745306be16652cc544abbb`, 3,055 bytes, SHA-256 `722c91c71c19a3d94219461b879aba57280a92fdaee93f78220983a86a7a222c`. Git blob and physical report content were verified byte-identical.
- Physical on-disk RIFT Live x64: 60,493,640 bytes, SHA-256 `1935a05c9db6d468e34e0055014a4a99c1b5afceb1695884e24600f5c20a4be8`, same original static PE identity as Lab1's qualified source copy. Current runtime pointers/process state were not inspected.

## Accepted static claim

The physical PE contains **two lazy initialization paths**, each requesting a **0x50-byte (80-byte) allocation** through RVA `0x78E110`, then invoking **the same initializer RVA `0x12746C8`**. Their on-disk code refers to **different cached global storage RVAs**:

| Site | Path A | Path B |
| --- | --- | --- |
| Global load | `0x1339EC4` | `0x54EB0E` |
| Allocate 0x50 bytes | `0x1339F56` | `0x54EBA3` |
| Allocator call to `0x78E110` | `0x1339F5B` | `0x54EBA8` |
| Common initializer call to `0x12746C8` | `0x1339F86` | `0x54EBD3` |
| Global stores | `0x1339F8F`, `0x1339FA6` | `0x54EBDC` |
| **Global storage RVA** | **`0x33E0BE0`** | **`0x33624C8`** |

Independent original PE section parsing found file-backed .data ends at RVA `0x3361C00`, while the virtual .data section ends at `0x35EB660`. Both globals reside in the **virtual-only tail**. They are address references on disk, **not initialized runtime pointer contents**.

**Limit:** The same initializer and allocation size demonstrate common construction code, not pointer aliasing. These distinct slots might contain identical runtime pointers or different pointers; neither outcome is proved. Neither class ownership, underlying ability object, spellbook producer nor Legendary-state consumer has been established.

## Verified bounded Workbridge jobs

| Job ID | Exit | Evidence |
| --- | --- | --- |
| `rre-nativemgr-lab1-verifier-20261103-a1` | 0 | 20 exact-byte, call and virtual-tail checks |
| `rre-nativemgr-lab1-tests-20261103-a1` | 0 | 8 synthetic checks |
| `rre-nativemgr-physical-raw-20261103-a1` | 0 | Independent Node PE section mapper checked 4 calls, 5 global references |
| `rre-nativemgr-physical-capstone-corrected-20261103-a2` | 0 | Independent Capstone/pefile decode of 11 sites, 4 calls and 5 global accesses on physical PE |
| `rre-nativemgr-report-git-20261103-a1` | 0 | Original Lab1 report matches historical committed blob |

**Test defect recorded:** The initial Capstone verification job `rre-nativemgr-physical-capstone-20261103-a1` exited **1** because the audit script incorrectly expected RIP-relative memory to always be operand #2. For store instructions, memory is operand #1. The corrected script identifies the memory operand on either side, asserts its RIP base and independently verifies computed targets; the corrected job exited **0**. This is a corrected **test assumption**, not evidence of PE or source drift.

These are concurrent read-only **command jobs**, not separate spawned LLM reasoning agents. There was no RIFT game input, memory attachment, guest action, desktop capture, provider setup, Lab1 write or installed-addon change.

## Next discriminator and stop

Record `M1-XP-002` as source-qualified static research relevant to parked `SC-401`. Do not infer that Path A and B operate on the same object merely from shared constructor RVA, or that native fields `+0x848` and `+0x88` belong to one live class. A new dataflow/pointer-alias source lead is needed before advancing those hypotheses. Neither this result nor the historic normal/Legendary tooltips resolve the blocked `SC-103` role/Legendary identity.

Future in-game verification still requires a current role-bound native Soul Tree/Legendary selection view. RRECollector v0.4.10 and RC-30 Pin→Undo/Reload UI remain frozen behind their separate live gates.
