# SC-604 — Selector preflight at RVA 0x12EA3BC (November 8, 2026, 08:07 EST)

**Scope:** one bounded, read-only original-PE inspection and an independent byte-level verifier. Extends [indexed selector entry](REA-RIFT-SPELLCASTING-SC604-SELECTOR-ENTRY-12E39D8-2026-11-08.md) and [preparation helper](REA-RIFT-SPELLCASTING-SC604-ENTRY-PREP-12E38E0-2026-11-08.md). **SC-604 remains interim; this is static structure, not a qualified cast or gameplay action.**

## Verified exact-build provenance

- Source: original physical-host `C:\Program Files (x86)\Glyph\Games\RIFT\Live\rift_x64.exe`, length **60,493,640**, SHA-256 **`1935a05c9db6d468e34e0055014a4a99c1b5afceb1695884e24600f5c20a4be8`**. The source was rehashed by each native-inspection verifier. This does **not** requalify the currently running Lab-2 process.
- RVA `0x12EA3BC`, 384-byte `.text` window SHA-256 **`f61bbc48366f7e4ae265fdd363b423cbd86359b3dc484e6ea5ba0b8c15ce5cad`**.
- Existing RRE virtual-environment Capstone decode: job `rre_20261108_0805_sc604_gate12EA3BC_decode_ro_01`, exit **0**.
- Independently implemented Python 3.14 standard-library PE section mapper and exact opcode/rel32 verifier: job `rre_20261108_0806_sc604_gate12EA3BC_stdlib_ro_01`, exit **0**, **31/31 assertions**, including two deliberately wrong-byte negative controls (stride `0x40` and altered magic constant).
- Separate exact-build direct-call verification: job `rre_20261108_0807_wt_caller_verify_ro_01`, exit **0**; `0x12E6F40 → 0x12EA3BC` and `0x12E6F5C → 0x12E39D8` via original rel32 bytes.

## Newly qualified native operations

| RVA | Direct machine-code observation | Bound on interpretation |
| --- | --- | --- |
| `0x12EA3D1–0x12EA3DA` | Sign-extends `EDX` index into `RSI`; saves the `RCX` receiver to `RDI` and tests for null. | Index appears signed; receiver's actual type is not established. |
| `0x12EA3E8–0x12EA412` | Checks receiver's first qword for zero; branches and optionally obtains a `+0x58` subordinate pointer. | The first qword is not proven to be a vtable or game owner. |
| `0x12EA41D–0x12EA431` | Requires `[RDI+0x78] == 0xBDF20DA3` and signed `[RDI+0x8C] < 0` to reach the indexed path. | These constants/fields are **not** classified as spellcasting fields. |
| `0x12EA437–0x12EA448` | Checks index `>=1` and `<=` the sign-extended word at `[RDI+0x62]`. | Conditional, 1-based signed-range guard; table count's semantic meaning unknown. |
| `0x12EA44A–0x12EA459` | Computes `index*0x38`, adds base `[RDI+0x68]`, takes `entry = base+(index-1)*0x38`, calls preparation helper `0x12E38E0(entry)`. | Receiver is confirmed as an indexed, 56-byte-stride structure on this branch; table type/owner unknown. |
| `0x12EA45E` | Writes **word 1** at `entry+0x24` (`[RBX-0x14]`). | This is an observed static write, not an observed runtime state. |
| `0x12EA466–0x12EA46B` | Invokes `0x12CCA58` with receiver's first-qword value and zeroed second/third arguments. | Side effects and receiver lifetime unknown. |
| `0x12EA470–0x12EA499` | Checks flag byte `[RDI+0xA8]`, index limit `0x20`, bitmap-like `[RDI+0x15C]`, and may set byte `[RDI+0xA2]=1`; the in-range branch returns zero. | Bitmap-like interpretation is tentative; no ability, queue or server semantics. |
| `0x12EA49D–0x12EA4C2` | Out-of-range branch includes `0x19` literal and a call to `0x12CCA58`; another failure branch at `0x12EA4C4` uses literal `0x15`. | They are observed code literals/path results, **not decoded error names**. |

**New connection and correction:** the `0x12EA3BC` callee previously described as an unclassified gate is **not merely a read-only predicate** in the static code: on its guarded in-range branch it calls the previously verified entry-preparation helper, writes `entry+0x24 = 1`, calls another unclassified helper, and returns zero. The direct caller `0x12E6F1C` tests that return and can subsequently pass the same 1-based index to `0x12E39D8`, which performs its own preparation and writes `entry+0x24 = 4`. This establishes two ordered source-code preparation/write sites on one conditional path, **not** that either executed live, that the table remains the same across calls, or that an actual cast succeeds. The intervening helper may have unknown side effects.

## Open decisions and stop condition

This narrows the receiver structure and control-flow constraints but **does not identify the table owner, selector identity, a Legendary ability, an Ability Queue enum value, network dispatch, server admission or observed spellcasting**. In particular, the meaning of `0xBDF20DA3`, `[RDI+0x62]` and the flags must not be guessed. Do not recursively trace `0x12CCA58`, the callback, or wider caller graphs without an independent table-owner discriminator.

SC-103, SC-306 and physical historical RC-30 remain blocked as before; SC-629 v0.4.14 remains offline-only awaiting a new Lab-2 control window. No model agents were launched due to the active FreeBuff/Ollama hold. These Workbridge jobs were **read-only command slots, not AI reasoning agents**. No game input, reload, process manipulation, installed addon/SavedVariables edit, cross-repository modification, dependency installation or remote push occurred.
