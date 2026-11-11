# RRE RC-76 — Current-build click-to-move chain and native input pump (LEGION)

**Date:** 2026-11-11 · **Evidence class:** original installed RIFT x64 executable, offline disassembly · **Milestone:** native click-to-move event → query → destination writer → destination consumer → distance-gated clear **statically source-linked on this build**. Actual player ownership, physical execution and navigation success **not yet proven**.

## 1. Exact binary and host qualification

- Independent LEGION hostname + original installed `C:\Program Files (x86)\Glyph\Games\RIFT\Live\rift_x64.exe`; 60,493,640 bytes, SHA-256 **`1935a05c9db6d468e34e0055014a4a99c1b5afceb1695884e24600f5c20a4be8`**, preferred image base `0x140000000`; **all addresses are RVAs**. Manager and three read-only agents separately verified the source. No running process, UI/input, VM/AMD, other repositories, provider change, installation, reload or push.
- Historical October C2M PE was **different**: 59,963,840 bytes, SHA `7c356c9dde9e12fcbff3c08d953b0630b48b1510a0ffb36e4ec164606e7b17bd`; prior RVAs `0x562BC0` (setter), `0x6942A0` (callback), `0x5765D0` (consumer) cannot be used on LEGION's currently installed binary. The exact field/layout agreement below was re-established from **new native instruction bytes**, not by blindly shifting old RVAs.

## 2. Current `Misc_EnableClickToMove` setting — accepted static

Exact ASCII setting string `Misc_EnableClickToMove` at `0x26EC228`; three actual aligned RIP-relative LEA references: `0xBD10FE`, `0xBD1126`, `0xBD74E8`. Both current native settings paths load the same **module-global pointer slot RVA `0x33958C0`**:

- `0xBD1136` loads the pointer; `0xBD113D` compares the proposed value to byte `[settingObject+0x146]`, `0xBD114A` writes it, and `0xBD1155` sets dirty bit 3 in `[settingObject+0x18]`. This is a setting-update route, **not** proof of its runtime value.
- `0xBD74E1` loads the same global pointer; `0xBD74FD` reads `[settingObject+0x146]` for a UI/settings-output path. The C2M event handler below reads a similarly offset byte from its **accessor-returned handle**; handle identity with this global object has **not** been proved.
- Manager original-source windows `[0xBD106E,0xBD11BE)` SHA `239064228779b4a973acb78df4a787853a17dfbc3926ca857254a8782238b730`; `[0xBD7458,0xBD75A8)` SHA `2da948f37e48b88c238c7b9495cad851fdbfa9be7d317495a53e9a6a0d336384`. Source alignment, all five RIP target calculations, byte-offset write/read independently passed job `rre-20261111-rc76-mgr-current-c2m-setting-root-independent-qa-001`.

## 3. Native event handler → geometric hit query → setter — accepted static

The current executable’s compiled native callback includes this conditional branch:

| RVA | Source-proven action |
|---|---|
| `0x6A6146`, `0x6A6159`, `0x6A6201` | Type-2 event and event+0x120 subcode **1** conditional branch. Matches the type/subcode *shape* of left-button release, but its concrete Win32-to-callback attachment is not proved. |
| `0x6A6238→0x798B80` | Obtains a component/settings handle. |
| `0x6A6242` | `cmp byte ptr [rax+0x146],0`; gate exits when click-to-move setting is disabled. Actual runtime setting unknown. |
| `0x6A6284`, `0x6A628A`, `0x6A629D` | Reads record `+0x12C/+0x128` integer coordinates and validates through `0x81B510`. |
| `0x6A639E` | Calls `0xF903D0` in the coordinate-to-projected-segment route. Exact 3D ray semantics are **inferred**, not all geometry parameters qualified. |
| `0x6A64EC` | Calls `0xF7CD20` with a candidate segment/hit query; successful return gates later write. Query semantic details and world-coordinate frame remain unqualified. |
| `0x6A6501`, `0x6A650D` | Loads receiver `[r14+0x10]` and makes an exact **direct CALL to `0x5749C0`** (new destination setter). `0x6A6512` marks record+0x18 as consumed. |

Manager original-source QA passed full aligned block `[0x6A6120,0x6A617C)`, 92B/24 instructions, SHA `3e19e7aca762b0f67e6faa6e4921584ba46cf213ebc86687ec49201aefd74eef`; `[0x6A6195,0x6A62B1)`, 284B/65, SHA `51b4bf0cda4354f0684026a1d2c679647b57e10a3b3154e31f7c2d5cfee3d50a`; `[0x6A62B1,0x6A652E)`, 637B/142, SHA `e820bb56a8d8b4ed6f21d61314d40ce003e01ec4a17e3c5d795da0f2a1e1fa09`. Check `rre-20261111-rc76-mgr-current-c2m-event-setter-join-independent-qa-001` (exit0).

Bounded direct-E8 search found the aligned call at `0x6A650D` as the only direct call to this setter in original executable code. **Not a claim of no indirect callers.**

## 4. Exact destination writer, native consumer and stop/clear path — accepted static

- **Writer** `[0x5749C0,0x574A18)` is a complete 88-byte/21-instruction native function SHA **`e6427f87b5f3f2a407bd742142181cffe82125a2b9943b80a690b8aa374d6075`**. At `0x5749D0` it calls `0x5460A0` (not fully characterized), then `0x5749D8` calls the current clear routine **`0x546830`**, `0x5749E1` loads `state=[receiver+0xB90]`, `0x5749E8` copies the first eight destination bytes into state+0x60, `0x5749F6` writes the final four at state+0x68, `0x574A08/0x574A0C` sets bit 0 at state+0x1A8. Independent manager byte/disassembly checks passed `rre-20261111-rc76-mgr-current-build-c2m-setter-independent-qa-001`.
- **Consumer** `[0x5885D4,0x588809)`, 565B/121 aligned instructions SHA **`fa9b16fb3647bf203e3e0ff5ad28db95fbff3ed9a4dffa2ba3357838d9b9db30`**: at `0x588730` reads `[receiver+0xB90]`; `0x588737` tests active bit `[state+0x1A8]&1`; `0x588754/0x588759` reads exact same 12-byte destination `+0x60/+0x68`. If state+0x70 is absent, it builds a separate object through `0x867900` and stores a handle via `0x53FBF0`; **not** proof of a navmesh route.
- **Relative-position and distance**: source `[0x588809,0x5889C8)` SHA `35eb7a10708c540739f9dbc35551931c1b939020b170cc1e23abad8dfa66d09f` (alternative aligned start `[0x588819,0x5889C8)` SHA `639f064bb66bfefb7c83b96fc1f4a3bcd38daa0201f468e5b52cf8a71391d3c7`). `0x588889..0x588894` computes destination-relative 3D deltas from an externally retrieved position; `0x58889A..0x58889F` suppresses the middle component on the relevant mode path; `0x5888A3..0x5888C6` computes squared length; later native calls include `0x698C90` and `0x698DB0` (orientation-like, not motor actuation proof).
- **Conditional clearing**: `[0x5889C8,0x588A51)` SHA `ec9c755ad12b9a99f9e0188a0217143373a59bf12b1b0da39a8790a4b95bd770`. After comparison at `0x588A16` and branch at `0x588A1A`, `0x588A1F→0x546830` clears the active state on the qualifying near-distance path; thresholds and behavior not yet qualified.

Both independent consumer lane and manager original-byte recheck validated full relevant instruction ranges and field consistency: `rre-rc76-child-consumer-two-function-full-decode-20261111-03`, `rre-rc76-child-consumer-arrival-clear-continuation-20261111-04`, `rre-20261111-rc76-mgr-current-c2m-consumer-independent-qa-001`, all exit0. This links **writer → same state fields → consumer → distance check → clear** without assuming player identity.

## 5. Native callback object reference — **partial registration**

- Original constructor/registration-like source `[0x53DC70,0x53E773)`, 2,819B complete aligned, SHA `ad5de6f4c667efdb89b2b9d3d0445ae55e45fb7b9dc024f688e3e77b26ce8e75`, stages exact callback pointer **`0x6A5E10`** at `0x53E58B`/`0x53E597`, copies into constructed object at `0x53E5B3`, and writes object into owner+0x3F0 at `0x53E5BC`. Independent manager check `rre-20261111-rc76-mgr-c2m-native-callback-registration-independent-qa-001` passed.
- This **does not** on its own prove the object attaches to the Win32 button record stream, executes for the active player, or that `0x6A5E10` is an exported/directly invokable gameplay API. Native event handler `0x6A6120` and C2M branch `0x6A6201` are qualified by source; missing provenance is upstream caller/object→record delivery.

## 6. Mouse record pump: immediate-versus-deferred delivery — accepted static

A *separate* current-build input path (not automatically the C2M callback) explains buffered mouse event delivery:

1. `0x7C0480` queues types 1/2 as 0x140-byte records at receiver+0x40/+0x48; when receiver+0xA40 is zero it conditionally drains through `0x7C1AD0`. Source `[0x7C0480,0x7C0670)` SHA `dd34f629e839fa3297c0bd985bebcb1633591b7a47618efcd30bb84915a93669`.
2. `0x7C1D40` drains that and another 0x130-byte queue through `0x7C1AD0` (calls at `0x7C1D90/0x7C1DE0`) and resets cursors; `[0x7C1D40,0x7C1E1D)` SHA `acd9156d25be9ac21cd0bd2ef188f02b2777ed09a6c8355f69bf2ac5b0eaabef`.
3. A concrete external direct caller **`0xFCA473→0x7C1D40`** follows receiver getter `0x54F7C0`; `[0xFCA430,0xFCA4B0)` SHA `b96fd43836c809d79b2e02f9792117aa6618ff40af45276ee02f26d72b70c931`. Frame/tick frequency not established.
4. Listener delivery at `0x7C1CC9` invokes virtual `[vtable+8]`, gated by listener state; source `[0x7C1AD0,0x7C1E60)` SHA `d75676445a4c77bbb69c1e55c14d1b3784ce9e22fc8632ade54f9d8e5d69f23d`. Prior `0x93B710` listener updates five button flags for type1/type2; the named `Event Mouse_Move` callback is only for **type3** in this listener. Other native name strings `Mouse_Left_Down`/`Mouse_Right_Click` are **unlinked leads**, not proved Lua button events.

Manager checked all four exact original source hashes and deferred flush call: `rre-20261111-rc76-mgr-mouse-record-flush-independent-qa-001` exit0. Specialist source jobs `rre-rc76-button-native-dispatch-and-listener-20261111-01`, `rre-rc76-button-queue-drain-7c1ad0-20261111-01`, `rre-rc76-button-pump-sole-flush-caller-20261111-01` exit0.

## 7. Limits, operational impact, next discriminating tests

**Verified:** This source-matched build has a coherent conditional event/query/destination setter/consumer/clear chain, an exact setting update/get path, a concrete native callback pointer stored in an object, and mouse-record buffering/flush. **Not verified:** live event source and active player, Win32 message→callback object link, user setting on/off, click screen-to-world accuracy, obstacle avoidance, real movement, cancellation under operator input or native pathfinding.

**Practical rules:** Do not invoke native setter, write player memory, transplant old RVAs or call this a complete public movement API. Keep original PE SHA and source hashes as the entry gate. Historical C2M documentation remains useful only when interpreted against its original SHA; the current LEGION client uses the new chain above.

1. **P1:** prove the callback object at owner+0x3F0 receives the expected type2/subcode1 event from the Windows message pump and identify active-player ownership; then identify a concrete externally observable destination field.
2. **P2:** characterize segment query success, screen/world coordinate frame and *normal cancellation/arrival* thresholds with bounded native source; use offline captures before gameplay.
3. **P3:** when separately coordinated, one physical LEGION live test: confirm actual setting, capture operator ground request + timestamped destination/XYZ and a real stop; notify before any addon installation, UI reload or game restart. No live tests were performed for RC-76.
