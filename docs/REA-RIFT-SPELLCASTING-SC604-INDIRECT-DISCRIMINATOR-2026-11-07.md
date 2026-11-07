# SC-604 — indirect discriminator dispatch behind the shared-slot setter (November 7, 2026, ~04:38 EST)

**Owner:** single RRE manager. **Scope:** one bounded, offline investigation of the physical RIFT executable; read-only sources and no live process access. **Verdict:** helper `0x127303C` is a **two-stage indirect dispatch trampoline**, not a direct literal/type-field reader. Its caller `0x2030EF0` compares **the low 16 bits of the dynamically returned result** against `0x0E89` before allowing a candidate pointer assignment. What the returned code signifies is **not established**.

## Exact source and two methods

- **Original source:** `C:\Program Files (x86)\Glyph\Games\RIFT\Live\rift_x64.exe`, 60,493,640 bytes; SHA-256 `1935a05c9db6d468e34e0055014a4a99c1b5afceb1695884e24600f5c20a4be8`. Both independent jobs rechecked this hash. RVAs refer only to this exact physical file, not the live process or VMware guests.
- **Primary disassembly:** Workbridge jobs `rre_20261107_0435_sc604_type_helper_disasm_ro` and `rre_20261107_0438_sc604_dispatch_caller_ro`, both exit **0** and untruncated, used the existing RRE environment's `pefile`/Capstone to decode the caller and `0x127303C–0x1273057`.
- **Independent byte verification:** `rre_20261107_0442_sc604_dispatch_stdlib_fixed_ro`, exit **0**, used Python 3.14 standard-library PE/section parsing, direct byte assertions and signed `rel32` arithmetic; **29/29** checks including `.pdata` function boundary (`0x127303C–0x1273057`) and two negative controls (misalignment, in-memory modified byte). A first verifier draft `rre_20261107_0440_sc604_type_helper_stdlib_ro` exited **1** because its helper incorrectly sliced by the length of a *hex string*, not decoded bytes. Diagnostic job `rre_20261107_0441_pe_mapping_diagnose_ro` confirmed original bytes and PE mapping; the fixed verifier passed. The failed draft is **not** a target-code failure.

## Byte-qualified native sequence

| RVA | Exact instruction or conditional | What it supports |
| --- | --- | --- |
| `0x2030F28–0x2030F30` | `mov rcx,[rdi]`; null test; `call 0x127303C` | Caller supplies candidate pointer to discriminator helper only when non-null. The direct call's signed relative destination was independently checked. |
| `0x127303C–0x1273043` | `sub rsp,0x28`; `mov rax,[rcx]`; `call qword ptr [rax+0x40]` | First dynamic dispatch through a pointer-derived function slot; the target is **not resolved**. |
| `0x1273046–0x127304D` | `mov rcx,[rax]`; `mov rdx,[rcx+8]`; `mov rcx,rax` | Uses the first dispatch's returned pointer to select a second indirect target at offset `+8`. |
| `0x1273050–0x1273057` | `add rsp,0x28`; `jmp rdx`; `int3` padding | Tail-dispatches to that second target rather than returning locally. The `.pdata` record ends at `0x1273057`. |
| `0x2030F35–0x2030F3D` | `mov ecx,0xE89`; `cmp ax,cx`; `jne 0x2030F4D` | Assignment requires the **downstream result's low 16 bits** to equal `0x0E89`. |
| `0x2030F47–0x2030F4A` | `mov [rbx],rax`; `inc dword ptr [rax+8]` | Candidate assignment and count-like increment are on the permitted path; not proof the branch ran. |

**Interpretation boundary:** `0x0E89` is a verified *comparison constant* for the indirect dispatch's result, not a statically proven class ID, ability ID, legendary flag, or a demonstrated runtime object type. The second indirect callee, concrete table instances, semantics of its return and whether it ever returns `0x0E89` are unknown. Static instructions do not establish executed runtime paths, queue/GCD modes, cast success or server acceptance.

This extends the [guarded setter report](REA-RIFT-SPELLCASTING-SC604-REFERENCE-SLOT-SETTER-2026-11-07.md) and preserves its shared `0x33E0AB0` slot boundary. **SC-604 remains interim; SC-103 / SC-306 blocked. RC-30 historical v0.4.10 same-trial Pin→Undo→Reload evidence remains incomplete; RC-32 specific live Retry unverified.** No task-register state change is justified.

**Optional next discriminator:** only if owner-cleared and newly evidenced, locate one concrete second-dispatch target/table tied to this exact build. Do not infer it from the numeric constant or launch a broad code import. No game input, UI reload, process manipulation, desktop lease intervention, installed addon/SavedVariables modification, other repository edit, dependency installation or remote push occurred.
