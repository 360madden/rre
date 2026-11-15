# RC-59 — Native event-7 state clearing and 2D-to-3D projection (LEGION, November 11, 2026)

**New verified static result:** A second branch of the same RIFT callback rooted at RVA `0x6A6120` uses the **same receiver field `[callbackThis+0x10]`** as the RC-58 destination-setter path, but conditionally invokes the native follow-clear and destination-clear functions. Independently, the event-coordinate projection call now has a qualified 2D-bound-check/3D-transform implementation. These are actionable reverse-engineering anchors, **not live cancellation or input-device proof**.

## Host and source qualification

- Verified **LEGION** via Workbridge `hostname.exe` job `rre-rc59-verify-legion-20261111-01`, exit 0. All targets here refer solely to LEGION's physical RIFT executable. No VMware, AMD-DESKTOP or RR2 process was contacted.
- Original installed PE: `C:\Program Files (x86)\Glyph\Games\RIFT\Live\rift_x64.exe`, 60,493,640 bytes; SHA-256 **`1935a05c9db6d468e34e0055014a4a99c1b5afceb1695884e24600f5c20a4be8`**. Static preferred image base `0x140000000`. All below are original **RVAs**, not runtime pointers.
- Manager independently decoded and SHA-checked the three original PE `.pdata` windows **596/596 instructions**, `rre-rc59-manager-three-window-independent-20261111-01` exit 0. Additional targeted event-7 prologue verification `rre-rc59-event7-prologue-alias-20261111-01` exit 0.
- No debugger, process attachment, memory write, code patch, game input, installation, UI reload, broad Ghidra import, or network push.

## Event 7 — verified same-receiver clear route

The existing RC-58 callback entry `0x6A6120` copies its first argument `rcx` to `r14` and its event argument `rdx` to `rsi`. Its original-byte type-7 dispatch at `0x6A6167/0x6A616A/0x6A616F` passes the **original callback first argument** into `0x6A8870` (compare event-2 path at `0x6A615C`).

| Event-7 handler RVA | Original bytes | Directly observed |
|---|---|---|
| `0x6A8891` | `4c8bea` | `mov r13,rdx` — preserves the event argument |
| `0x6A8894` | `488bf1` | `mov rsi,rcx` — preserves the callback first argument |
| `0x6A8899` | `e822100000` | Calls prerequisite `0x6A98C0` |
| `0x6A88A6` | `e815070000` | Calls an additional helper `0x6A8FC0` |
| `0x6A88AB–AD` | `84db 7419` | Tests previous AL-derived `bl`; zero **skips this clear sequence** |
| `0x6A88AF` | `488b5e10` | Loads receiver `rbx=[rsi+0x10]`, same callback field used by destination setter |
| **`0x6A88B6`** | **`e8e5d7e9ff`** | Calls `0x5460A0` (previously qualified follow-clear) |
| **`0x6A88BE`** | **`e86ddfe9ff`** | Calls `0x546830` (previously qualified destination-clear) |
| `0x6A88C3` | `41c6451801` | Writes event field `+0x18=1` on the preserved second argument |

The event-7 handler spans `[0x6A8870,0x6A8FB2)`, **1,858 original bytes / 453 complete instructions**, SHA-256 `92213304d979200d6b95f7fff890070d337e629c7220d601a667610060e4c491`. Independent worker discovery job `rre-rc59-owner-type7-sibling-complete-20261111-01` exit 0; manager reverified the full window and highlighted bytes.

**Meaning:** Event type **2** can establish destination state under its own gates; type **7** contains a conditional same-receiver state-clearing path. This makes event 7 a strong **cancellation candidate**. Its physical input meaning, exact prerequisite result, actual character ownership, movement or observed stopping remain unknown. The numeric event value **7 is not** the earlier type-7 `TtPathfinding` dispatcher index; these unrelated uses of 7 must not be conflated.

## Native coordinate projection — current-build 3D transform

The RC-58 event handler reads two event coordinates, converts them to floats and calls `0xF903D0`. RC-59 qualified the two original target functions:

1. **Outer conversion `[0xF903D0,0xF9044F)`:** 127 bytes/31 instructions, SHA `7906a185a07ea33b722b9c843dccce8a5523db47f4e2e9b54e2b4e49d0624300`. `0xF903E6` and `0xF903F9` convert floats to 32-bit integers; `0xF903FD` calls `0x1154840`; `0xF90405/07` gate on its success. On success `0xF90416–0xF9043F` add three floats from a separate position-like accessor into the supplied output vector. The accessor's object identity is unqualified.
2. **Projector `[0x1154840,0x1154A87)`:** 583 bytes/112 instructions, SHA `ffe16977f0c9ef1b07371fbd0d7fbf7b8b54a6f16e3df02bec81402aa840b162`. It requires a nonnull context pointer and a successful call `0x114BF00`. Values are checked against 2D lower/upper bounds at receiver offsets **`+0x19C/+0x1A0`** and **`+0x1A8/+0x1A4`**. It divides coordinate differences by their ranges at `0x1154912/0x1154922`, remaps to another rectangle at `+0x178…+0x184`, then combines the normalized components with a 3D coefficient block at roughly `+0xD4…+0x100`. On successful branches, three float outputs are written at `0x11549D1/0x11549D5/0x11549DA` or `0x1154A44/0x1154A48/0x1154A4D`.
3. **Practical interpretation:** This is an exact-build **2D input → bounded spatial transform → three-component coordinate output** candidate, supporting the RC-58 event-to-native-query route. Whether coordinates are framebuffer pixels, which camera/view owns the transform, and which world-space frame/units the result uses have **not** been runtime calibrated. Do not promote this to a supported external API.

Manager source-only jobs `rre-rc59-projection-current-pdata-20261111-01` and `rre-rc59-projection-helper-bounded-20261111-01` both exit 0. Original hashes, full instruction counts and selected disassembly were independently rechecked in the 596-instruction job.

## Negative callback registration probe

An independent read-only exact 8-byte search for preferred-address callback pointer `0x1406A6120` (little endian `20616a4001000000`) found **zero direct matches** in the current PE `.rdata` (9,855,488 bytes, RVA `0x25EF000`) and `.data` (4,242,432 bytes, RVA `0x2F56000`). Source SHA matches; job `rre-rc59-vtable-directptr-data-20261111-01` exit 0.

**Boundary:** This excludes only that exact absolute pointer encoding in those two sections, **not** callback registration through relative/thunk/dynamic pointers or other sections. Do not infer absence of a vtable, player ownership, or a complete code Xref inventory.

## Independent review and acceptance

- Separate read-only QA agent `rre-rc59-quality-branch-byte-audit-20261111-01` exit 0 rechecked **28** RC-58 selected event/threshold/clear-site instructions and three original floats; no material defect found.
- Historical consumer entry `0x5765D0` and near-clear call `0x576BCF` both map to current `0x588420` and `0x588A1F` with **identical RVA shift `+0x11E50`** (independent report). Static cross-build continuity does **not** prove in-game arrival.
- Sole manager writes the RRE main branch; all three delegated agent lanes were read-only. No modifications outside `C:\work\rre` and no live game intervention.
- Prior RC-58 report, SHA ledger and test results remain authoritative for the event-2 setter, squared-distance literals `9.0/20.25/0.0625`, and near clear. RC-59 extends rather than replaces that evidence.

## Next practical discriminators

1. **P1 — Event 7 prerequisite:** Identify what `0x6A98C0` actually checks (one bounded original-byte probe). It gates whether clearing occurs; interpret it before proposing a real cancellation button.
2. **P2 — Player ownership:** Find a selected constructor/receiver resolver for callback `this+0x10`; the absence of direct `.rdata/.data` pointer is not a negative player-owner proof.
3. **P3 — Controlled runtime verification:** Under separate physical-client authorization and a current session-bound data capture, correlate event types, projected destination and actual movement/stop. Genuine v0.4.19 RRECollector navigation SavedVariables still await deployment and manual capture.

**Explicitly unverified:** physical mouse/keyboard mapping; event semantics; current player identity; runtime 2D/3D transform; use of native routing; actual movement, arrival or cancellation. No static discovery substitutes for a game-observed result.
