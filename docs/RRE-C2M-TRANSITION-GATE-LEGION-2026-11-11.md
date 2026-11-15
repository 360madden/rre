# RC-60 — Event-7 transition gate and indexed-state lookup (LEGION, November 11, 2026)

**New original-byte-qualified result:** Event type 7's conditional clear route is activated by a **tracked state transition / special side effect** returned from the callback's own state sampler, rather than an unconditional clear. This narrows the RC-59 cancellation candidate; it is **not evidence that event 7 means a physical keyboard or mouse release, nor that the local player stops moving**.

## Source and execution scope

- Host **LEGION** verified independently; original physical installed RIFT PE `C:\Program Files (x86)\Glyph\Games\RIFT\Live\rift_x64.exe`; size 60,493,640 bytes; SHA256 `1935a05c9db6d468e34e0055014a4a99c1b5afceb1695884e24600f5c20a4be8`; preferred base `0x140000000`. Addresses are **static RVAs**.
- Event-7 caller: `0x6A8897 xor edx,edx`, `0x6A8899 call 0x6A98C0` (with callback `this`), `0x6A88A3 movzx ebx,al`; the intervening `0x6A88A6 call 0x6A8FC0` does not overwrite saved `bl`; `0x6A88AB test bl,bl` skips both RC-59 clears when zero. Original event-7 window and same receiver `[this+0x10]` are documented in RC-59.
- Two bounded independent original-PE agent probes: `rre-rc60-gate-pdata-20261111-01` and `rre-rc60-gate-index-helper-20261111-01`, both **exit 0**. Manager independently verified all three selected window hashes and their full decodes in `rre-rc60-manager-two-helper-independent-20261111-01` (**exit 0**); focused byte/branch check `rre-rc60-manager-check-gate-selected-20261111-01` and indexed-bit slice `rre-rc60-manager-gate-bitfield-slices-20261111-01` also **exit 0**.
- No native process attachment, debugger, memory writes, game/OS input, UI reload, VMware, AMD-DESKTOP, addon deployment, install, network push, or other repository mutation.

## Decoded transition detector `0x6A98C0`

Complete function unwind **`[0x6A98C0,0x6A9B0E)`**, **590 bytes / 186 instructions**, original-window SHA256 `3f10a058b42ec0145fbf7de76fd8d42d3d367af1110be071bf9b13db711ffb32`.

1. `0x6A98DB xor bpl,bpl` initializes a per-call change accumulator to zero. `0x6A98DE call 0x6A9C10` obtains a condition-source object.
2. The function calls `0x7C97E0` eight times with **numeric indices 2, 3, 6, 7, 4, 5, 8, 16**, collecting boolean-like results.
3. Six indexed results are compared with a cached bitset at **`[callbackThis+0x0C]`**. When a bit differs, native `bts`/`btr` writes the new state and `mov bpl,1` records a transition. Index-to-bit correspondence is directly visible in this original code:

| Indexed condition | Cached bit mask |
|---|---:|
| `2` | `0x10` (bit 4) |
| `3` | `0x20` (bit 5) |
| `6` | `0x40` (bit 6) |
| `7` | `0x80` (bit 7) |
| `4` | `0x08` (bit 3) |
| `5` | `0x04` (bit 2) |

Representative exact sites: `0x6A997C test dil,dil`; `0x6A9985 bts ecx,4`; `0x6A9989 mov bpl,1`; `0x6A9995 btr ecx,4`; `0x6A9999 mov bpl,1`. Other transition sites include `0x6A99D1/0x6A99E1/0x6A9A23/0x6A9A51/0x6A9A79/0x6A9AA0`.
4. Indices **8 and 16** also feed special branches and flag byte **`[callbackThis+0x0D]`**. The path can call `0x6A5D00`, `0x6A6FD0`, or `0x6A6E70`. `0x6A9AF5 movzx eax,bpl` returns the accumulated bit-change flag; `0x6A9AF1 mov al,1` is another possible positive return after a special branch. The semantics of those helpers and bits are not yet qualified.
5. Thus, when the event-7 handler invokes `0x5460A0` (follow clear) and `0x546830` (destination clear), the conditional gate indicates a **change or special action in the callback's tracked conditions**, not simply that an event-7 packet arrived.

## Indexed-state evaluator `0x7C97E0`

Complete unwind **`[0x7C97E0,0x7C98CD)`**, **237 bytes / 74 instructions**, original-window SHA256 `0b2676dcc89d521b6795a826c851d6756c1e8157779acccd8ab314354ae94250`.

- `0x7C9801 cmp r8d,[rdx+0x20]` compares the requested index to an ordered-tree node key; `0x7C9807` and `0x7C980F` traverse child pointers `+0x10/+0x18`. Missing records return `AL=0` at `0x7C9818`.
- For a found record it evaluates associated fields with `0x7C3C90` and `0x7C98D0`; both are **unqualified callees**. No evidence here says the index numbers are Win32 virtual-key codes, scancodes, mouse buttons, or documented addon APIs.
- Separately examined only the **first unwind region** of companion helper `0x6A8FC0`: `[0x6A8FC0,0x6A9026)`, 102 bytes / 30 instructions, SHA `b14f1dfc92c259413990403af5df8c23b101b045b055bafc6fd0bb3b1f673441`. It accesses `[callbackThis+0x10]`, receiver `+0xB60`, and calls `0x574370` / `0x5739F0`; possible chained unwind beyond that region is **not fully decoded**. Its immediate effect on the event-7 clear gate remains unproven.

## Evidence boundary and practical next actions

**Static proof:** Indexed-state sampling → cached-bit changes / special flags → nonzero gate result → **same-receiver** follow + destination clear inside the event-7 handler.

**Not yet proved:** The indices' physical control identities, callback construction, local-player identity, the event producer, real-time delivery, world-coordinate meaning, navigation state changes in-game, or actual movement/cancellation.

1. **P1 — Indexed-condition ownership:** Narrowly trace the source object from `0x6A9C10` and provenance of one known tree key; stop on concrete identity evidence or ambiguity.
2. **P2 — Receiver identity:** Trace one chosen constructor/owner writer for callback `this+0x10` or bit cache `this+0x0C`, keeping RRE native RE evidence separate from RR2.
3. **P3 — Genuine runtime bridge:** With separate physical-RIFT approval, first obtain v0.4.19 RRECollector navigation SavedVariables and then observe input→destination→stop in an operator-controlled game session; do not infer live behavior from disassembly.
