# SC-604 — Selector-gated helper at RVA 0x128D198 (November 7, 2026, ~09:18 EST)

**Lane:** sole RRE manager, bounded read-only native inspection. **Scope:** original executable static code, not live cast behavior. This extends [the 0x1290768 / 0x128D020 selector handoff](REA-RIFT-SPELLCASTING-SC604-SELECTOR-THUNK-1290768-2026-11-07.md). SC-604 remains an **interim** cast-state mechanism; neither an ability identity nor a queue or server-cast contract is proved.

## Source and independent verification

- Physical RIFT Live x64 original: `C:\Program Files (x86)\Glyph\Games\RIFT\Live\rift_x64.exe`; **60,493,640 bytes**, SHA-256 **`1935a05c9db6d468e34e0055014a4a99c1b5afceb1695884e24600f5c20a4be8`**, independently rehashed by each successful bounded verifier.
- The **Lab-2 guest executable was separately rehashed to this SHA earlier on November 7 at approximately 08:00 EST**, before the native-controller-to-external-VNC handoff. This permits reuse of identical *static bytes* only; there is **no fresh post-handoff guest/process/loaded-memory or runtime call attestation**.
- Primary existing-pefile/Capstone job `rre_20261107_0917_sc604_128d198_disasm_ro` exited 0 and decoded a bounded window from RVA `0x128D198` (file offset `0x128C598`). Complementary job `rre_20261107_0920_sc604_128d198_tail_ro` exited 0, ending at the verified function `ret` at `0x128D303`; both outputs untruncated.
- Independent **Python 3.14 standard-library-only** original-PE/byte/relative-target verifier `rre_20261107_0924_sc604_128d198_stdlib_fixed_ro` exited 0: **38/38 assertions**, including two negative controls. The first draft `rre_20261107_0922_sc604_128d198_stdlib_ro` exited 1 because its *verifier code* compared the DOS PE marker using wrongly escaped null-byte text. The corrected parser passed without changing the RIFT executable or claiming the earlier draft as a source failure.

## Direct static findings

| Original image RVA | Disassembly evidence | Bounded interpretation |
| --- | --- | --- |
| `0x128D1A7`, `0x128D1BE` | `mov word [rax+0x10],dx`; `movzx r15d,dx` | Incoming **16-bit selector** is retained in a stack home and in R15; actual selector identity unknown. |
| `0x128D1B4`, `0x128D1C2–1CA` | `mov rbx,[rcx+0x98]`; nonnull branch calls `0x3C310` | Reads an optional object-associated pointer; helper behavior unproven. |
| `0x128D1D1–1D8` | `cmp byte [rsi+0x83],0`; `je 0x128D2DA` | A **zero byte bypasses** the selector-processing region and reaches the cleanup/return path. Field meaning unknown. |
| `0x128D1DE–0x128D234` | `lea r14,[rsi+0xA0]`; call `0x1277164`; compare its three returned words against null/end/container | A three-part **range/end sentinel test** gates the next call. Only equality/branch control flow is established, not container type. |
| `0x128D234–0x128D24F` | `lea edx,[rcx+1]` on the zero-`rcx` path; `mov r8d,r15d`; calls `0x12E6F1C`, `0x12E8534`; `cmp eax,0x64` | A selector-preserving call receives `R8D`; a later result is compared to **100**. No success, ability, cooldown or percentage semantics are established. |
| `0x128D2AA–0x128D2BD` | `mov word [rsp+0x20],r15w`; call `0x128E884` using `R8=&[rsp+0x20]` | The selector is also passed **by pointer** in a later branch; this does not identify its data model. |
| `0x128D2D6–0x128D303` | Selected `rdi=[rcx+0x10]` or preserved zero; optional `0x3C320`; `mov rax,rdi`; `ret` | The helper returns a pointer-like value or zero in those branches. Not proof of accepted cast execution. |

The key new connection is that `0x128D020`'s call to **`0x128D198`** enters a **flag-gated, range-sentinel-tested path** that can forward the *same word selector* to `0x12E6F1C` and by address to `0x128E884`. A static callsite does **not** establish that a live RIFT session traversed it. The branch on `0x64` is only a comparison, not a decoded status code.

## Stop conditions and next useful question

Do **not** promote this to Legendary / Protector's Fury identity, SC-306 queue mapping, server acceptance, or RC-30 SavedVariables operator acceptance. Keep SC-103 and SC-306 blocked, SC-604 interim, RC-30/RC-32 unverified. No new model inference was performed: FreeBuff `--check` (job `rre_20261107_0913_freebuff_capability`, exit 0) confirms only fixed previously exercised modes; **zero genuine new model agents**, separate from Workbridge verification commands.

One possible *later* bounded next question is what `0x128E884` does with the pointer to the 16-bit selector, if it would distinguish the mechanism from an already documented lookup. Avoid wide caller graph walks or unqualified post-handoff game state.

No RIFT/VM input, UI reload, controller launch, process manipulation, installed addon/SavedVariables edit, desktop lease action, cross-repository edit, dependency install, or push occurred.
