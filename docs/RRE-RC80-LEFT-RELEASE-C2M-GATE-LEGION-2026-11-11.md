# RC-80 — concrete left-release producer and C2M callback gate

**November 11, 2026, LEGION. Original-byte source findings only.** Following [actual C2M enrollment in RC-78](RRE-RC78-C2M-ENROLLMENT-LEGION-2026-11-11.md), two missing input semantics are now source-qualified: Windows left-button release produces a type2/subcode1 record; the selected callback predicate returns false for that record and therefore does not skip the C2M handler on that predicate alone.

The original installed physical PE is 60,493,640 bytes, SHA256 `1935a05c9db6d468e34e0055014a4a99c1b5afceb1695884e24600f5c20a4be8`, preferred image base `0x140000000`. All addresses are RVAs. Independent Codex agent research and manager rehash/aligned-instruction assertions passed for all ten windows in the [machine evidence](RRE-RC80-LEFT-RELEASE-C2M-GATE-LEGION-2026-11-11.json). No Workbridge, game input, attachment, import or VM was used.

## Callback predicate on this exact record

`0x6A663A` reads the record type. Two decrements select numeric type2 and jump `0x6A6648→0x6A69EF`. The latter reads record+0x120. For subcode1, the comparison against4 does not match; `0x6A69FA` computes `subcode-8`; `0x6A69FD test eax,0xFFFFFFF7` is nonzero; `0x6A6A02→0x6A6AAA` clears AL and returns false.

This selected path calls no registry/gameplay helper and performs no object-state update. At RC-77's callback gate `0x6A5FB4`, this predicate result does not take the skip branch. **The whole predicate is not pure:** other record branches call helpers and mutate state.

## Windows left-button release produces the consumed record shape

Win32 `WM_LBUTTONUP` (`0x202`) selects entry1 through `0x7C1928`; destination entry1 at `0x7C18FC` is `0x7C105B`. Prologue `0x7C0BB9 lea rbp,[rsp-0x88]` followed by `0x7C0BC1 sub rsp,0x188` establishes RBP = working RSP+0x100. The local record starts at RSP+0x30, so `[rbp+0x50]` is record+0x120.

- `0x7C109A` sets EDI=1; `0x7C10A2` writes record type2.
- Both modifier branches write subcode1: `0x7C1120 jge 0x7C104E` uses the shared `[rbp+0x50]=edi`, and the other branch writes it at `0x7C1129`.
- Coordinate fields record+0x128/+0x12C derive from the receiver's saved +0x30/+0x34 values. This alone does not prove a world-space destination.
- Both paths reach `0x7C17F2 call 0x7C0480`, the existing buffering/dispatch route.

**This is one proven producer, not a unique meaning of every type2/subcode1 record.** The existing native reset path also emits that record combination; a record observation alone cannot identify an actual physical release.

## Practical consequence and limits

The coherent static path now has a specific ordinary mouse-release source, a real enrolled listener, known virtual dispatch, and a selected predicate that permits the C2M continuation. Native actuation should reuse this existing mechanism when runtime-qualified, rather than invoke a setter or invent a parallel controller.

Earlier callback eligibility (`0x54ECA0` and context+0x358), consumed-record handling, actual `Misc_EnableClickToMove` value, later handler/query gates, active-player identity, and observed movement/stop are still unresolved. This research neither enables the setting nor sends a click. The practical RC-79 quest feature's deployment/read-only capture authorization remains pending independently.
