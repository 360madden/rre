# SC-604 — 16-bit selector route through native thunk 0x1290768 (November 7, 2026, ~07:43 EST)

**Lane/owner:** single RRE manager; bounded, offline, read-only static verification. **Finding:** the previously unresolved selector consumer `0x1290768` is a small adjustment thunk that tail-jumps to executable RVA `0x128D020`. The latter retains the supplied 16-bit selector and output pointer for downstream operations. Neither target gives an ability ID, a Legendary flag, a proven live branch, or server-side cast acceptance.

## Original source and independent receipts

- Original **physical-PC RIFT Live x64 executable**: `C:\Program Files (x86)\Glyph\Games\RIFT\Live\rift_x64.exe`; **60,493,640 bytes**; SHA-256 `1935a05c9db6d468e34e0055014a4a99c1b5afceb1695884e24600f5c20a4be8`. Both independent bounded jobs rehashed the original file. These are **RVAs** on that exact image, not runtime addresses or guest-build offsets.
- Primary Workbridge job `rre_20261107_0740_sc604_1290768_disasm_ro` (exit 0) decoded a bounded 900-byte window from `.text` using existing RRE `.venv` pefile and Capstone. Separate job `rre_20261107_0741_sc604_128d020_disasm_ro` (exit 0) decoded a bounded 580-byte destination window. Both outputs were untruncated.
- Independent job `rre_20261107_0742_sc604_1290768_stdlib_ro` (exit 0) used **Python 3.14 standard library only**, a separate PE/section parser, exact original instruction bytes and signed rel32 destinations: **42/42 assertions passed**, including mutated-byte and incorrect-jump-target negative controls. It independently resolved thunk file offset `0x128FB68`, implementation file offset `0x128C420`, and the tail jump to `0x128D020`. No target execution occurred.
- FreeBuff capability check `rre_20261107_0738_freebuff_check_ro` exited 0, with `noModelExecution=true`: installed fixed modes remain `sc103/rc30`, `sc306/sc503`, `slots/file`, `operator/ability`. These are unchanged prior questions, not a novel thunk-review mode. **Independent new reasoning agents: 0**; Workbridge command slots/jobs are not model agents.

## Qualified observations (original byte offsets)

| RVA(s) | Direct static evidence | Qualified interpretation |
| --- | --- | --- |
| `0x1290768–0x129076F` | `mov r9,[rcx]`; `mov eax,[r9+4]`; `neg eax` | Reads a dereferenced source pointer and 32-bit value at offset `+4`; actual object and data type are not established. |
| `0x1290771–0x1290782` | `sbb rcx,rcx`; `add r9,0x110`; `and rcx,-0xF0`; `add rcx,r9` | Arithmetic selects `RCX = [original RCX]+0x110` when the `+4` DWORD is zero, or `RCX = [original RCX]+0x20` when nonzero, given x64 `NEG/SBB` carry semantics. It does not establish which route runs in a real game session. |
| `0x1290785` | `e9 96 c8 ff ff`, signed `rel32` | Unconditional **tail jump** to `0x128D020`, not a direct function body that computes an ability ID. The thunk does not overwrite the incoming `RDX` selector or `R8` output pointer. |
| `0x128D03B–0x128D042` | `mov r15,r8`; `movzx r14d,dx`; `mov rbp,rcx` | Common implementation preserves output-address argument in `R15`, zero-extends the **16-bit** selector from `DX`, and preserves the adjusted object pointer. |
| `0x128D052–0x128D06D` | `movzx edx,r14w`; call `0x128D198`; `mov r8d,r14d`; `mov edx,1`; call `0x12E6F1C` | The selector feeds at least two downstream paths. Called functions and meaning of the selector remain unresolved. |
| `0x128D0BE–0x128D0D1` | `movzx r8d,r14w`; `mov rcx,rbp`; call `0x128BD30` | Another 16-bit selector-preserving call from the common body. This is not runtime cast acceptance. |
| `0x128D10D–0x128D127` | `mov rcx,[r15]`; call `0x128749C` | Common body reads the pointer behind the supplied output address before a downstream call, consistent with an output-pointer interface; result semantics unverified. |
| `0x128D165–0x128D168` | `cmp eax,0x64`; `je 0x128D077` | Conditional backward branch on the returned integer. Do not label the constant as a number of abilities, progress percentage or runtime retries without additional proof. |

The upstream source-hashed note [SC-604 output selector 0x12748C8](REA-RIFT-SPELLCASTING-SC604-OUTPUT-SELECTOR-12748C8-2026-11-07.md) verified that `0x12748C8` supplies the word at `[RSI+0x40]` in `EDX`, alongside the output-pointer address in `R8`. The new exact-build chain is **`0x12748C8 → 0x1290768 → 0x128D020`**. In particular, the earlier “unresolved helper” is a **thunk**, not a final single-stage selector consumer.

## Uncertainty, ownership and next bounded check

- This is **static evidence**, not a live pointer value, selector identity, current Legendary/Protector's Fury ID, queue map, game input or server acknowledgement. A branch or call being present in instruction bytes does not prove execution.
- SC-604 remains an **accepted interim** mechanism; SC-103 and SC-306 remain blocked. RC-30 **historical v0.4.10 same-trial** Pin → Undo-before-Reload + matching saved archive is still incomplete. Later v0.4.11 host/runtime evidence does not reconstruct the missing same-trial receipt; RC-32 live Retry is also unverified. No task gate/status change is justified.
- If new evidence warrants more work, review one of `0x128D198` or `0x128BD30` to identify a concrete selector operation, with fresh repository ownership checks. Do not follow broad graphs, import the executable, assume object or ability semantics, or repeat parked probes.
- No game input, reload, process action/attach, desktop quarantine override, installed addon/SavedVariables mutation, cross-repo edit, dependency install or push was performed. Only RRE manager-owned documentation and dated handoff are authorized for local integration.
