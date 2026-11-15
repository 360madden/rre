# RC-81 — correct callback-state address and actual C2M eligibility bases

**November 11, 2026, LEGION. Two concrete static advances:** the callback-state global address and writer are corrected/source-proven, and the remaining direct callback eligibility tests are mapped to their actual objects. The active player and runtime motion remain unverified.

All RVAs refer to the original installed 60,493,640-byte RIFT PE, SHA256 `1935a05c9db6d468e34e0055014a4a99c1b5afceb1695884e24600f5c20a4be8`, preferred base `0x140000000`. Two independent Codex agents researched disjoint questions; the manager independently rehashed and completely decoded all **19 original windows**, with decisive pointer/instruction assertions. [Machine evidence](RRE-RC81-CALLBACK-STATE-AND-ELIGIBILITY-LEGION-2026-11-11.json). No Workbridge, full import, game input, process attachment or VM operation.

## Address correction and exact object identity

**Reject RC-77's `0x337FD20`. Correct slot: `0x336FD20`.** Instruction `0x6A9B10` is `lea rcx,[rip+0x2CC6209]`: next RIP `0x6A9B17` plus displacement equals `0x336FD20`. The getter then jumps through `0x6A3EE0→0x58B20`, whose leaf reads `[rcx]`. A zero-hit scan of the wrong address was not evidence of missing functionality.

The root constructor `0x53DC70` requests a **0x20-byte allocation** at `0x53E53A/0x53E549`. It passes the root in RDX and the new object in RCX to `0x6A3E80` at `0x53E559`. That constructor writes the root into **state+0x10** at `0x6A3E97`; then `0x6A3E9B` passes the state as RDX, `0x6A3EA2` addresses the corrected slot, and `0x6A3EA9→0x6A3E60→0x589D0` writes it. The definitive leaf is `mov [rcx],rdx; ret`.

Thus the callback receives a **small callback-state object whose +0x10 references the same 0xF40 root**. The global is not evidence of a direct player singleton or a native class name. Clear/initialization routes at `0x6A3ED0`, `0x16A930`, and `0x2551DA0` were source-qualified; indirect writers were not exhaustively excluded.

## Direct callback route and the correct field bases

At `0x6A5E1F`, RSI holds callback state and RDI holds the incoming record. The direct C2M continuation requires:

1. `0x6A5E25` reads **root = [state+0x10]**; `0x6A5E29` calls `0x54ECA0(root)`. The result must be nonnull.
2. `0x6A5E37` obtains that root again; `0x6A5E3B` requires **byte[root+0x358] != 0**.
3. `0x6A5E48` requires **byte[record+0x18] == 0**, reaching `0x6A5FA7`.
4. Predicate `0x6A6620` returns false, permitting `0x6A5FCF→0x6A6120`. RC-80 established this selected predicate result for type2/subcode1.

**Do not put +0x358/+0x400 on the 0x20-byte state object.** They belong to the referenced root. If either early eligibility condition fails, the callback takes alternate handling at `0x6A5FD4`. For already-consumed type2/subcode1, `0x6A5F2B` clears state byte+0x0C bit1 and `0x6A5F44` tail-jumps to `0x6A8FC0` with DL=1, bypassing this callback's direct C2M jump. The tail helper was not characterized by this milestone.

`0x54ECA0(root)` is a **lazy/cache-mutating resolver**, not a pure predicate. It reads root+0x400; on a miss it may call `0x6A0040` with root+0x360/+0x3F8, use a byte index with 0xFF sentinel into a container's +0x78 table, and cache the selected pointer at root+0x400. Its resolved type is still unknown. The root constructor initializes byte+0x358 to zero at `0x53DDF1`; later setters are a fresh bounded follow-up.

## Practical consequence

The current source map now separates callback state, application root, incoming record and lazy resolved object. This prevents using a wrongly decoded global as an actor pointer or treating a mutating getter as a passive predicate. The next grounded questions are later root+0x358 writers and the resolved object behind root+0x400. Existing setting/query gates, active actor ownership, physical delivery and actual movement/stop still need their own evidence.

RRECollector quest capture/export is already published as RC-79 `a2d9660`. Its physical deployment/read-only capture approval remains pending independently; no native finding authorizes that action.
