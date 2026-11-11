# RC-67 — Additional Win32 keyboard-state record types 5/6/7 (LEGION)

**Accepted static extension of RC-66:** Two distinct original RIFT producer fragments call `USER32!GetKeyboardState`, create typed native records with the 256-byte snapshot, and send them through the same receiver writer (`0x7C1AC0` -> `0x7C1AD0` -> `receiver+0xA41`). The selected paths establish numeric record types **5, 6 and 7**. Type 5 and type 7 also call `USER32!MapVirtualKeyW` with mode 2 (`MAPVK_VK_TO_CHAR`); type 6 has no such translation in the selected branches. **Do not label these numeric types key-down/up/movement/stop events without separate proof.**

## Source and exact selected windows

- Independently verified host `LEGION`, physical original `C:\Program Files (x86)\Glyph\Games\RIFT\Live\rift_x64.exe`, 60,493,640B SHA-256 `1935a05c9db6d468e34e0055014a4a99c1b5afceb1695884e24600f5c20a4be8`, base 0x140000000; read-only .pdata disassembly and PE imports. RRE `C:\work\rre` clean main starting HEAD `d866db5b7306a6441a220fceaf9a9e52d5862f30` (22 ahead).
- Source A `[0xFB6D6D,0xFB6E9C)` **303 bytes/56 complete instructions**, SHA `91a114412e6a22966ae438c906274d7fe0f2a6a680ac0d4946349f5f47751da2`, job `rre-rc67-osvk-second-caller-selected-pdata-20261111-01` exit0.
- Source B `[0xFB51BF,0xFB5309)` **330 bytes/69 complete instructions**, SHA `6a252cb8f8999db41ea32ff484a75b1d5ce2f0331175a8ba8138aa165f34f39d`, job `rre-rc67-b-keyboardstates-three-calls-20261111-01` exit0.
- Original PE IAT `USER32.dll!GetKeyboardState=0x25EFD68`, `USER32.dll!MapVirtualKeyW=0x25EFC68`, `VCRUNTIME140.dll!memcpy=0x25EFDF8`. All addresses below are RVAs; mode-2 semantics: [Microsoft MapVirtualKeyW documentation](https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-mapvirtualkeyw).

## What the original code actually establishes

| Numeric record type | Proven producer(s) | State payload and dispatch | Additional translation |
|---|---|---|---|
| **5** | A `0xFB6D9B`, B `0xFB51E2` | GetKeyboardState; copy helper `0x7C21F0` (and, in selected B branch, explicit `memcpy`); `0x7C1AC0` wrapper to writer. | `MapVirtualKeyW(...,2)`; A stores EAX at `rsp+0x140` = record+0x120; B stores EAX at `[rbp+0x40]` (frame alias unqualified). |
| **6** | B `0xFB5255`; RC-66 `0xFB6CA6` | GetKeyboardState; copy helper `0x7C21F0`; same writer. | No MapVirtualKeyW seen in selected type-6 branches. |
| **7** | A `0xFB6E2B`, B `0xFB52B1` | GetKeyboardState; copy helper `0x7C21F0`; same writer. | `MapVirtualKeyW(...,2)`; return written at record+0x120 in selected A region. |

- In A, `0xFB6D8A` calls GetKeyboardState; `0xFB6D9B` chooses type5; `0xFB6DB2` copies 256B through helper; `0xFB6DCD` translates code with MapVirtualKeyW mode2; `0xFB6DED` copies the same 256B buffer again; `0xFB6DFF` writes via native receiver wrapper. Later `0xFB6E16` calls GetKeyboardState; `0xFB6E2B` chooses type7; `0xFB6E42` copies; `0xFB6E55` translates mode2; `0xFB6E6F` dispatches to wrapper. The observed type5 branch loops when its local count permits, but triggering predicate/real key meaning remain unknown.
- In B, three source calls `0xFB51D4`, `0xFB5247`, `0xFB52AB` populate a stack buffer. Typed branches 5/6/7 send records via `0x7C1AC0` at `0xFB523E`, `0xFB528E`, `0xFB5302`. The first type5 path has an explicit 256-byte `memcpy` at `0xFB522C` to `[rsp+0x39]` = record+0x19; type6/7 use the source-verified helper from RC66. Constructor parameter `R8D=8` in this B fragment is an observed numeric field, **not proof of VK_BACK or gameplay semantics**.
- The wrapper+handler are directly proven in RC-66, not newly guessed: `0x7C1AC0` sets R8b=1 and tail-jumps to `0x7C1AD0`; handler copies record+0x19, 256B, into receiver+0xA41. For record types5/6/7 it does not copy record+0x124 to receiver+0x38.

## Independent QA and limits

- Independent manager job `rre-rc67-manager-two-producers-independent-20261111-01` exit0 rechecked all 125 original instructions, both SHA-256 window hashes and call sites; `rre-rc67-manager-record-code-mask-precision-20261111-01` exit0 rechecked type values, mode2 argument and record+0x120 write. Additional original handler-tail list traversal `[0x7C1B7F,0x7C1C53)` was read-only examined, without assigning a subscriber identity.
- Independent RC-66 audit `rre-rc67-qa-all-original-windows-20261111-01`, `rre-rc67-qa-original-win32-imports-20261111-01` exit0: **10/10** original code windows, 683 instructions, 4 IAT slots, no material defect found. Refinements: modifier OR bits first enter **record+0x04**, not receiver+0x38; a reset type7 record is snapshotted after its selected table byte is cleared.
- No observed physical input, keyboard focus behavior, synthetic-key acceptance, movement, turning, stop or active player receiver ownership is proven. No game process/input/UI/reload, AMD/VM, installs, other repo writes, remote push, or model calls.

**Next ranked:** (1) compare one current passive physical-game keyboard snapshot with RRECollector SavedVariables only if separately authorized and current source identity confirmed; (2) source-qualify one active-player receiver/subscriber to connect input record to a movement predicate; (3) park broad `+0x350` owner and `+0xA40` writer searches pending a discriminating source alias.

