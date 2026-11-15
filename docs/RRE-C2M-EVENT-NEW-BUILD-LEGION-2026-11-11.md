# RC-57 — Current-build event/query → destination-setter call (LEGION, November 11, 2026)

**New static bridge:** On the currently installed physical RIFT executable, a bounded exact-build direct-call search found a verified caller of the RC-56 destination setter at `0x5749C0`. The source window shows **query result → successful-result gate → receiver/vector preparation → setter call → event-consumed flag**. It is a strong static C2M candidate, **not observed player movement**.

## Exact evidence

- Source: `C:\Program Files (x86)\Glyph\Games\RIFT\Live\rift_x64.exe`, SHA-256 `1935a05c9db6d468e34e0055014a4a99c1b5afceb1695884e24600f5c20a4be8`.
- One candidate in a selected raw `E8` direct-call search, **one instruction-boundary-qualified call** inside PE unwind interval `[0x6A62B1,0x6A652E)`. This does not establish all possible callers; indirect/tail calls are not covered.
- Entire 637-byte original source window SHA-256 `e820bb56a8d8b4ed6f21d61314d40ce003e01ec4a17e3c5d795da0f2a1e1fa09`. The manager independently rehashed the full original executable and full selected region and decoded all **142 instructions**, job `rre-rc57-manager-original-byte-confirm-20261111` exit0.
- Discovery job `rre-rc57-native-newbuild-c2m-direct-call-20261111` exit0. Only this one focused callback path was probed; no broad scan or Ghidra import.

| New-build RVA | Original bytes | Verified instruction / role |
|---:|---|---|
| `0x6A64EC` | `e82f688d00` | Direct `call 0xF7CD20` (query candidate) |
| `0x6A64F1` | `84c0` | `test al,al` (query success) |
| `0x6A64F3` | `7421` | `je 0x6A6516` (skip setter on failure) |
| `0x6A6501` | `498b4e10` | `mov rcx,[r14+0x10]` (setter receiver) |
| **`0x6A650D`** | **`e8aee4ecff`** | **Direct `call 0x5749C0`** (RC-56 setter) |
| `0x6A6512` | `c6461801` | `mov byte ptr [rsi+0x18],1` (event consumption) |

The original-byte region also prepares an output vector from the query's result near `0x6A64F5/0x6A64FE` and `0x6A6505/0x6A650A`. The setter's separate byte-verified region copies that 12-byte value to state `+0x60/+0x68` and sets the `+0x1A8` activation bit, as recorded in [RC-56](RRE-C2M-NEW-BUILD-LEGION-2026-11-11.md).

This extends the independently requalified current-build native sequence:

`input/event-shaped callback region → query + success test → C2M setter → destination activation state → consumer entry bit test`.

**Boundaries:** The event's physical input/button/type meanings, callback registration, relation to the local player, runtime vector correctness, live destination, movement, stopping and pathfinding use are still unverified. Do not call a function, write memory or interpret the event-consumed flag alone as a working C2M command.

## Practical follow-up

1. Identify current-build callback registration and owner provenance, using one bounded evidence-driven path; do **not** equate receiver `[r14+0x10]` with the player without proof.
2. Qualify type/button fields of this same region before any claim about mouse or hardware input.
3. Compare a genuine game-bound destination sample to live movement only under a separately approved physical-client test and single input owner.

Machine-readable original-byte hashes, selected instructions, limits and Workbridge job IDs: [RC-57 JSON](RRE-C2M-EVENT-NEW-BUILD-LEGION-2026-11-11.json).
