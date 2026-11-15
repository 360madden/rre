# RRE RC-70 — queue-drain caller, receiver destruction and corrected listener layout

**Host:** LEGION · **Time:** November 11, 2026 ~12:09 EST · **Status:** accepted exact original-PE static input-receiver lifecycle extension; physical gameplay movement/stop remains unverified.

## Breakthrough A: the receiver's queued records have a native invocation site

An exact `.text` E8-rel32 scan for queue drainer `0x7C1D40` returned **one raw direct caller**, `0xFCA473`. The complete containing function `[0xFCA0D0,0xFCAE98)` has 3,528 bytes and 865 fully decoded instructions. Its source-level object/argument chain:

1. `0xFCA2D1 call 0x49A020` obtains the same lazy global root getter proved in RC-63; `0xFCA2D6 mov r14,rax` retains that root across the selected path.
2. `0xFCA45B mov rcx,r14`, `0xFCA45E call 0x54F7C0`, and `0xFCA463 test rax,rax` check for an available native receiver; zero branches around the drain at `0xFCA466`.
3. On the nonzero path `0xFCA468 mov rcx,r14`, `0xFCA46B call 0x54F7C0`, `0xFCA470 mov rcx,rax`, then `0xFCA473 call 0x7C1D40` submits that receiver for buffered-record draining.
4. The complete tiny getter `[0x54F7C0,0x54F7D1)` reads `rax=[rcx+0x350]`, checks it, then (if nonzero) reads `rax=[rax]`, returning the *same* `root+0x350 -> owner+0 -> receiver` established in RC-68. When owner is zero, it returns zero. Thus the drain is directly reached through the proven native input receiver chain.

**Boundary:** The function is a real native caller, but we have not qualified its gameplay timing or linked the buffered records to a particular real movement/stop event. The two queue strides and `0x7C1AD0` sink remain RC-64/RC-69's separately proven behavior.

## Breakthrough B: receiver object teardown, not only global pointer clear

The outer cleanup `[0x779140,0x779607)` calls owner cleanup `0x7933C0` using `[outer+0x1B8]` before the already proven `globalRoot+0x350=NULL` write. Inside complete owner cleanup `[0x7933C0,0x793751)`, `0x7936CC mov rdi,[rbx]` loads the owner's receiver field. The nonnull path passes it in RCX to `0x7C0340` at `0x7936D7`, then passes its same pointer to a deallocation-like helper with RDX=`0xB48` (`0x7936DC`–`0x7936E4`) and clears owner+0 at `0x7936E9` with RSI previously zeroed at `0x793400`.

The entire receiver destruction helper `[0x7C0340,0x7C047D)` is source-decoded. It cleans both buffered-record allocations, unlinks/frees nodes in the two 0x18-byte sentinel lists at receiver+0x18 and receiver+0x08, and frees the sentinel allocations. The exact allocator implementation is not separately qualified, so these are deallocation-like calls rather than a claim about allocator internals.

## Important RC-68/69 field correction

The earlier phrase **`receiver+0x10 callback-root pointer` was incorrect**. The original receiver initializer `[0x7C00A0,0x7C016A)` sets up two circular 0x18-byte list sentinels: one installed at **receiver+0x08**, the other at **receiver+0x18**. It zeros adjacent `receiver+0x10` and `receiver+0x20`. The callback fanout traverses nodes from the **+0x08 sentinel** and only dispatches when the +0x10 value is nonzero. The adjacent zero field is strongly consistent with an MSVC list **size/count**, but a source-qualified increment/decrement writer has not been found, so its numeric semantics remain *probable* rather than definitively proven. The exact listener insertion site and player movement callback remain open.

## Exact source evidence

- Original physical RIFT executable: `C:\Program Files (x86)\Glyph\Games\RIFT\Live\rift_x64.exe`, 60,493,640 bytes, SHA-256 `1935a05c9db6d468e34e0055014a4a99c1b5afceb1695884e24600f5c20a4be8`, preferred image base `0x140000000`; the source addresses below are RVAs.
- Drain caller `[0xFCA0D0,0xFCAE98)` 3,528B/865 instructions, SHA `35e7e89ce4795d13eec2de00b64d2b7ce9e23f772bbf5582e60a83e2d3d72cd6`.
- Receiver getter leaf `[0x54F7C0,0x54F7D1)` 17B/6 instructions (no `.pdata` record), SHA `66a56a6b070f8087cdd68637f4dab49dbd8fbdd6b6107b0599340b36f2d93d64`.
- Owner cleanup `[0x7933C0,0x793751)` 913B/218 instructions, SHA `0c58476387a692b289ecc057fe8ee894c234fe6613b10f10c0758e7321d145fe`.
- Receiver destruction `[0x7C0340,0x7C047D)` 317B/79 instructions, SHA `b0b48f625094ce1d69595973c827797942df8ba6293b3af523dae33dc876bd7e`.
- Receiver initializer `[0x7C00A0,0x7C016A)` 202B/48 instructions, SHA `91dd527b1562b535ed21c3675fde7a711f04b40f30416a55e894d4979b7cee2a`.
- Independent manager verification of all five complete windows and the exact source registers: `rre-rc70-manager-independent-five-window-qa-20261111-01` exit 0, including `0xFCA2D1`, `0xFCA45E`, `0xFCA473`, getter leaf, list sentinel initialization and receiver destruction. Exact direct caller search: `rre-rc70-manager-drain-direct-caller-scan-20261111-01` exit 0, one syntactic E8 hit (indirect calls not excluded).
- Manager intermediary jobs `rre-rc70-manager-drain-one-caller-full-source-20261111-01`, `rre-rc70-manager-drain-root-register-trace-20261111-01`, `rre-rc70-manager-receiver-dtor-drain-getter-20261111-01` exit 0.
- Three independent LEGION agents: constructor/list initialization `rre-rc70-lane-a-receiver-constructor-owner-source-20261111-01` exit 0; listener sentinel/count correction `rre-rc70-b-ctor-list-sentinel-and-size-20261111-01` exit 0; owner teardown `rre-rc70-lane-c-owner-teardown-callee-7933c0-20261111-01` and zero-value proof `rre-rc70-lane-c-owner-zero-value-proof-20261111-01` exit 0. Each worked read-only; manager performed all repository edits.

## Unresolved and priority order

1. **List insertion and count:** Find a source-qualified routine that inserts into the receiver+0x08 list and updates its +0x10 companion field; confirm whether it is a count and identify the registration object.
2. **Actual listener:** Trace an anchored listener object's vtable+0x08 to a specific gameplay consumer; do not interpret the callback path as player turning/stopping without that evidence.
3. **Physical result:** After separate live authorization and exact current RRECollector load/version receipts, compare timestamped position snapshots with a separately recorded physical-key timeline; source linkage alone cannot certify movement.

**No** physical game input, UI, process attachment, VM/AMD access, installer, additional repo edits or remote push took place in this RC-70 discovery.
