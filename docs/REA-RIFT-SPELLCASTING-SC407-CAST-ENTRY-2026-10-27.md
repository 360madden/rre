# SC-407 — Native RIFT /cast command entry on physical PC

**October 27, 2026. SC-407 completed, SC4 overall still active.** Source-backed native command table and local process code bytes verified. No VMware, game input, process writes, injection, or full-PE Ghidra import.

## Pinned original executable

Physical-PC RIFT binary `C:\Program Files (x86)\Glyph\Games\RIFT\Live\rift_x64.exe`, SHA-256 `1935a05c9db6d468e34e0055014a4a99c1b5afceb1695884e24600f5c20a4be8`. All RVAs below belong only to this build. Original .rdata table pairs **function pointers before each short command name**. Earlier labels based on the *following* pointers were WRONG and are explicitly superseded here.

| Command | Name RVA | Specialized callback pointer location | New-build callback |
| --- | --- | --- | --- |
| `stopattack` | `0x26B6550` | preceding pointer block | `0x6C73F0` |
| **`cast`** | **`0x26B6598`** | **`0x26B6570`** | **`0x6C7450`** |
| `use` | `0x26B65D8` | `0x26B65B0` | `0x6C7B90` |

Companion cast pointer slot `0x26B6578` points to auxiliary short stub `0x6C7440`.

**Independent discriminator:** the error string "Could not cast unknown ability: [%ABILITY]" at RVA `0x26B6040` is referenced from native cast code at RVAs `0x6C78B2`, `0x6C78DD` and `0x6C7922`. The distinct string "Could not use unknown item: [%ITEM]" at RVA `0x26B65E0` is referenced from **use** code at `0x6C86A7`, `0x6C86D2` and `0x6C8716`. Separate original xrefs confirm that cast vs use labels are not swapped.

## Native cast command code region

One bounded original-.text decode: RVA **`0x6C7450–0x6C7B71`** (1,825 bytes), SHA-256 **`31c02f4e68ac0c8157ad4e8fd1f813fe724b02f607d9c67649bcd777d0890d85`**, 429 linearly decoded instructions, 39 direct calls and five indirect callsites.

PE `.pdata` contains adjacent/chained unwind intervals `0x6C7450–0x6C74D7`, `0x6C74D7–0x6C7B54`, `0x6C7B54–0x6C7B75`. The selected code range is an **offline investigative slice**, not a decompiled C/C++ function contract.

Source-backed direct calls in the cast-entry code include:

| Site RVA | Target RVA | Current interpretation |
| --- | --- | --- |
| `0x6C7519` | `0x6E7550` | Early argument/parse helper, precise semantics unknown |
| `0x6C752C` | `0x5A5FF0` | Result-producing helper and conditional branch, unknown actual ID lookup semantics |
| `0x6C75A8` | `0x57CDA0` | Bounded call amid argument/object preparation |
| `0x6C7958` | `0x7DDD00` | Near user-facing unknown-ability error handling |
| `0x6C7A10` | `0x7DE6F0` | Downstream call candidate; may be string/action preparation |
| `0x6C7A29` | `0x7078E0` | Later helper; not yet qualified as cast request transmit |

The two strings, their actual machine instruction references, and the table pointer assignments are verified code-source facts. **Server acceptance, actual ability invocation, modern ability-ID mapping, GCD and queue behavior remain unproven.**

## Live physical-PC corroboration

The running local executable PID **66436**, image base **`0x7FF720420000`** (both volatile), was checked using standard **PROCESS_QUERY_LIMITED_INFORMATION | PROCESS_VM_READ**. Nine bounded reads from the local process matched the installed original source: command literal, rebased cast pointer slots targeting moduleBase + `0x6C7450` and `0x6C7440`, adjacent use pointer targeting moduleBase + `0x6C7B90`, and selected cast/use error branch instruction bytes. No target input or memory write. The validated process association is from one recorded observation and must not be assumed current in a future session.

## Completion boundary and next question

**SC-407 accepted as a narrow native cast-command entry finding. SC4 major phase is NOT yet complete.**

The next REA task is to follow **one** downstream callee from `0x6C7450` (start with `0x5A5FF0` or `0x7DE6F0`) to determine whether code actually resolves a character's ability or submits a cast request. Stop after two materially different non-decisive probes rather than chasing generic allocators. No return to previously parked SC-401 API-schema branch without new evidence. Continue on physical PC, not VMware.

Source and validation records: [machine-readable SC-407 finding](REA-RIFT-SPELLCASTING-SC407-CAST-ENTRY-2026-10-27.json). Workbridge jobs `rea-localpc-cast-command-native-leads-20261027-01`, `rea-localpc-cast-command-table-20261027-01`, `rea-localpc-cast-dispatch-pointers-20261027-01`, `rea-localpc-cast-handler-errors-xrefs-20261027-01`, `rea-localpc-cast-handler-trace-20261027-01` and `rea-localpc-cast-command-runtime-code-20261027-01` completed exit 0. The preliminary pointer labels in `rea-localpc-cast-dispatch-pointers-20261027-01` must not be reused without this correction.
