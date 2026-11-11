# RRE RC-73 — `Event Mouse_Move` event identified; typed reset record linked

**Host:** LEGION · **Time:** 2026-11-11 ~12:45 EST · **Source:** original RIFT x64 PE, static/read-only · **Accepted result:** concrete mouse-move event identification, precise type-3 state normalization and type-2 producer-to-listener subcode linkage. **Not established:** player/world movement, camera turning, runtime key-button identity or a live game response.

## 1. Native type-3 callback reaches a named mouse-move event

The source-qualified RC-72 callback at `0x93B710` handles type3, compares two record values against its owner's state, then passes two scaled `float` arguments to `0x4BD9A0`. New complete code windows show the downstream event path:

- `[0x4BD9A0,0x4BD9D0)` begins the callee; subsequent `[0x4BD9D0,0x4BDAC3)` contains at `0x4BDA00` `lea r8,[rip+0x21E89C1]`. The target `0x4BDA07 + 0x21E89C1 = RVA **0x26A63C8**` is exact ASCII **`Event Mouse_Move`** in the original `.rdata`.
- At `0x4BDA07`, a second RIP-relative `lea rdx,[rip+0x21E7EE2]` targets **`0x26A58F0`**, exact ASCII **`Rift`**. The routine uses these names with `0x981720` at `0x4BDA1B` to construct/prepare the event context.
- `0x4BDA44` and `0x4BDA5D` convert two `float` values to `double`; each is supplied through `0x16893D0` (`0x4BDA52`, `0x4BDA61`) into the event-argument path.

**Strong source conclusion:** This previously unclassified two-value flow is RIFT's named **`Event Mouse_Move`** path. **Boundary:** Selected source proves event-name use and argument preparation; it does not establish that a Lua subscriber ran, nor any actor/camera/world movement. The native label supports *mouse event*, not *player navigation*.

## 2. Type-3 receiver fields are normalized, not originally populated here

The fully decoded producer `[0x7C0780,0x7C0909)` treats `RDI` as the receiver. It reads preexisting 32-bit fields `[receiver+0x30]` (`0x7C07DD`) and `[receiver+0x34]` (`0x7C07D6`), extracts/sign-extends 16-bit values, and at `0x7C0863` and `0x7C0852` writes the canonicalized dwords back to the **same** fields. The type-3 record receives them at offsets `+0x128/+0x12C` (proven RBP/RSP frame alias in RC-72). The concrete listener compares and consumes those exact fields.

**Important negative:** Those same-function writes are **normalization of existing state**, not a source-qualified OS message / mouse coordinate producer. The earlier upstream origin remains unknown.

## 3. Type-2 record producer matches listener subcodes

Adjacent original native windows `[0x7C0940,0x7C0A40)` and `[0x7C0A40,0x7C0BAA)` prove a receiver-state reset process. With `RDI=receiver` and `RBP=RSP+0x100`, the record base `RSP+0x20` makes `[RBP+0x40]` exactly **record+0x120**:

| Native condition on receiver+0x38 | Emitted type/subcode | Native call to dispatcher | Listener effect (RC-72) |
|---|---|---|---|
| Mask bit `1` set | Type `2`, subcode `1` | `0x7C0A9E` | Clears `owner+0x1C0` |
| Mask bit `2` set | Type `2`, subcode `2` | `0x7C0B07` | Clears `owner+0x1C1` |
| Mask bit `4` set | Type `2`, subcode `4` | `0x7C0B70` | Clears `owner+0x1C2` |

The mask tests are at `0x7C0A22` (bit1), `0x7C0AA3` (bit2) and `0x7C0B0C` (bit4). The record type write sites are `0x7C0A84`, `0x7C0AED`, `0x7C0B56` and the corresponding subcode writes are `0x7C0A96`, `0x7C0AFF`, `0x7C0B68`. The routine subsequently clears the receiver's 256-byte keyboard-state buffer using the previously qualified memset and resets receiver+0x38.

**Distinct neighboring type-7 path:** The earlier fragment `[0x7C0940,0x7C0A40)` also emits type-7 records from high-bit entries of receiver+0xA41. At `0x7C09E4` it calls named **`USER32.dll!MapVirtualKeyW`** (IAT RVA `0x25EFC68`) with a map-type argument 2, supplying the result to record+0x120 and dispatching at `0x7C0A0C`. **This Windows import belongs to type7; do not misattribute it as type1/2 provenance.**

**Still unresolved:** The source of type1 records, what physical key/mouse inputs numeric subcodes represent, and whether any of these flags control character locomotion. Typed record names are numeric only except the independently named `Event Mouse_Move` downstream.

## 4. Source-hash evidence and corrections

Installed original executable `C:\Program Files (x86)\Glyph\Games\RIFT\Live\rift_x64.exe`, 60,493,640 bytes, SHA-256 `1935a05c9db6d468e34e0055014a4a99c1b5afceb1695884e24600f5c20a4be8`; image base `0x140000000`, all addresses below RVA.

| Half-open source window | Size / decoded instructions | SHA-256 |
|---|---:|---|
| `[0x4BD9A0,0x4BD9D0)` | 48B / 11 | `8f7dad264f178a720f37adb26cbbf759d77d05e727cc66d33403b56d73ac5f54` |
| `[0x4BD9D0,0x4BDAC3)` | 243B / 53 | `57ac23f3a6b19a9f6787285295f91a5f8a8f2c42ef92067e024934f5d5cb5bbe` |
| **Data** `[0x26A63C8,0x26A6428)` (`Event Mouse_Move`) | 96B | `3756c3c8789071c5a515fc68534bd20d6791160c07d3f0451e1a4e8d082b9247` |
| **Data** `[0x26A58F0,0x26A5950)` (`Rift`) | 96B | `e445771d9a2daed1ed120885e6fae7acbaa787fbe3bfb29c0de2b6a47b7a2749` |
| `[0x7C0780,0x7C0909)` | 393B / 106 | `a6fb7de6365dd92fd4f474fb7345391221f0a00881cea0d1f3d9986c873a60de` |
| `[0x7C0940,0x7C0A40)` | 256B / 57 | `3dff7574010a45e934bc05814988f235f2d57c3ddb7cba8b74aa25c2c62f9f7f` |
| `[0x7C0A40,0x7C0BAA)` | 362B / 82 | `d10dd985a73f7e52f18352ad9362d397b65753f93fe69511b81be0fd512e41ee` |
| `[0x93B710,0x93B755)` | 69B / 17 | `cc90debb4fd97122c9a16643272eddc42150e2a92e476b60765c3f7c974d5c06` |
| `[0x93B7BA,0x93B8A3)` | 233B / 78 | `fca35ef7ad9ec79d61382490c59cd24d5e0430b877b554da5a7bfb2f63eefebe` |

Manager independently verified literal/code references in `rre-rc73-manager-mousemove-original-call-and-literal-20261111-01` and typed source windows in `rre-rc73-manager-type2-type7-producer-independent-20261111-01` (both exit0). Three read-only agent lanes: downstream `rre-rc73-b-downstream-contiguous-dynamic-dispatch-20261111-01`, identifier `rre-rc73-b-downstream-anchored-ascii-correction-20261111-01`, receiver-normalization `rre-rc73-lane-a-type3-status-writes-detailed-20261111-01`, type2 reset `rre-rc73-lane-c-type2-reset-entire-selected-original-20261111-01`, adjacent type7 `rre-rc73-lane-c-type2-upstream-adjacent-funclets-20261111-01`; exact producer/consumer cross-check is in RC72 reports.

## 5. Prioritized next work

1. **True OS origin of receiver+0x30/+0x34:** Trace one anchored upstream input message setter, not the already known normalization loop.
2. **Event delivery to addons:** Follow exact `Event Mouse_Move` dispatcher/source API route and correlate to RIFT Lua if evidence supports it.
3. **Separate locomotion track:** Discover a source-qualified player actor/camera consumer or conduct separately approved physical XYZ versus manual input checks; mouse event handling alone cannot prove character turns.

**Scope:** Source-only LEGION. No physical game input, process attachment, VM/AMD access, installs, other project edits or remote push.
