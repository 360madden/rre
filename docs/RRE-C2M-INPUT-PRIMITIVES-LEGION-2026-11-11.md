# RC-62 — Native indexed-flag primitives and condition accumulator (LEGION, November 11, 2026)

**Practical static breakthrough:** We can now describe the *primitive* condition checks beneath RC-61's three-field records: one reads specified bits from an object at `+0x38`, another reads bit 7 of a byte indexed at `+0xA41`. Their receiver provenance is partially traced. Separately, the RC-61 stateful evaluator uses an exact **0.99 / 0.01 exponential-update formula** on a float initialized by its constructor. None of these static facts identifies physical keys, local-player ownership or real RIFT movement.

## Source and verification

- Independently verified **LEGION** via `rre-rc62-verify-legion-20261111-01` exit0; RRE only at `C:\work\rre`. Original installed physical PE `C:\Program Files (x86)\Glyph\Games\RIFT\Live\rift_x64.exe`, 60,493,640 bytes, SHA256 `1935a05c9db6d468e34e0055014a4a99c1b5afceb1695884e24600f5c20a4be8`. All RVAs relative preferred image base `0x140000000`.
- Three independent read-only agent lanes; sole manager writes. Manager independently verified the exact special bit test, constructor, general indexed-byte reader and accessor (**55/55 complete instructions**) in `rre-rc62-manager-bitfield-ctor-verify-20261111-01` and `rre-rc62-manager-tableaccessor-independent-20261111-01`, both exit0.
- Manager further checked original-window SHA and both float literal RVAs/opcodes in `rre-rc62-manager-verify-smoothing-constants-20261111-01` exit0. No game/process memory access, input, reload, install, VM, AMD-DESKTOP, other repo edit, new native tool import, or network push.

## 1. Specialized mask primitive `0x7C19D0`

No `.pdata` unwind entry: this is a small **leaf** function qualified by exact instruction boundaries. Region `[0x7C19D0,0x7C19D7)`, **7 bytes / 3 instructions**, SHA `2ae2064520604b6cb477c16276b9ceaf8e9555e8d53a10a9edd32ad9fb60689d`.

| RVA | Original bytes | Operation |
|---|---|---|
| `0x7C19D0` | `855138` | `test dword ptr [rcx+0x38],edx` |
| `0x7C19D3` | `0f95c0` | `setne al` |
| `0x7C19D6` | `c3` | `ret` |

The RC-61 first-field codes `4/5/6` pass respective masks **`0x04/0x08/0x10`** into this checker. This proves *specified-mask bits are set on its receiver*, not that the bits are keyboard or mouse buttons. Agent `rre-rc62-lanea-specialflag-leaf-20261111-01` exit0. An earlier `.pdata`-only query returned no unwind record as expected for this leaf; exact-byte decoding resolved it.

## 2. General indexed-byte primitive `0x7C1A00`

Another unwind-free leaf, original region `[0x7C1A00,0x7C1A0F)`, **15 bytes / 4 instructions**, SHA `d8fd27add70c646095b670a6b3af33adc5c101827a9a2b73dd0a53c89837ef51`.

| RVA | Original bytes | Operation |
|---|---|---|
| `0x7C1A00` | `0fb6c2` | `movzx eax,dl` (8-bit condition index) |
| `0x7C1A03` | `0fb68408410a0000` | `movzx eax,byte ptr [rcx+rax+0xA41]` |
| `0x7C1A0B` | `c0e807` | `shr al,7` (extract high bit) |
| `0x7C1A0E` | `c3` | `ret` |

Its exact return is **`(byte_at(receiver + 0xA41 + (index & 0xFF)) >> 7) & 1`**. Its 8-bit index could be an internal condition ID; **not proven** Win32 VK, scan code or user-visible binding.

Upstream accessor `0x7A3500`, `[0x7A3500,0x7A3515)`, **21 bytes / 5 instructions**, SHA `0378fdba4c8a06aac40d9c2c896ad095c2885e8e1421ab1402d17f9c270b322e`: `0x7A3504 call 0x49A020`; `0x7A3509 mov rax,[rax+0x350]`. RC-61 `0x7C3CAC–B1` then calls this accessor and dereferences its result before passing the receiver to `0x7C1A00` or `0x7C19D0`. `0x49A020` identity, pointer lifetime, and table writers are unqualified. Agent jobs `rre-rc62-general-leaf-discriminator-20261111-01` and `rre-rc62-general-object-accessor-20261111-01` exit0; an initial .pdata query failed only because the leaf lacked unwind metadata.

## 3. Constructed subobject and precise floating-point update

Constructor `0x7C3920`, original `.pdata [0x7C3920,0x7C39D1)`, **177 bytes / 43 instructions**, SHA `f0829d2d8dfab7a96feabc2d1c005ba7d229a172255f4c8148d4b1e99e4a2ae0`.

- Calls allocator `0x78E110` requesting `0x70` bytes for a subobject at `0x7C395D/0x7C3962`; stores pointer at **`[owner+0x58]`** at `0x7C39AD` (zero under a failure branch at `0x7C39BF`).
- Initializes **`[subobject+0x68]=1.0f`** at `0x7C39A2`; **`[subobject+0x40]=0.75f`** at `0x7C398F`; **`[owner+0x38]=0.75f`** at `0x7C3956`.
- The RC-61 evaluator `0x7C98D0` reads the subobject via `[owner+0x58]` at `0x7C991E` and writes its float `+0x68` on these two code paths:

| RVAs in evaluator | Verified formula |
|---|---|
| `0x7C9984–0x7C9991` | `new_value = 0.99f * old_value` |
| `0x7C99DC–0x7C99F1` | `new_value = 0.99f * old_value + 0.01f` |

Exact PE constants: **0.99f** at RVA `0x26A4488`, bytes `a4707d3f` = 0.9900000095367432; **0.01f** at RVA `0x26A33CC`, bytes `0ad7233c` = 0.009999999776482582. Both `mulss` at `0x7C9989/0x7C99E1` point to the same 0.99 literal; `addss` at `0x7C99E9` uses the 0.01 literal. The complete reused evaluator region `[0x7C98D0,0x7C9BD6)` remains RC-61 qualified (774 bytes/207 instructions, SHA `6b7058cff85b3acb859e04139739c7f9a4191e63cc55e8652ff2f3fb9b8a6988`).

**Interpretation limited:** This is an exponential-style update of a bounded-looking accumulator; call cadence, whether the signal is input, time, focus or navigation, and actual player/game effects are **not qualified**. Repeated 0.99-only updates would halve a value after about 69 calls, **not necessarily 69 frames or seconds**.

**Object identity safeguard:** The constructor owner's `+0x38` initialized float and the primitive's `[rcx+0x38]` bitmask read are not equated. Their receivers arrive through **different call paths**, and aliasing has not been proven.

Constructor and float jobs `rre-rc62-constructor-pdata-full-20261111-01`, `rre-rc62-constructor-evaluator-float-slices-20261111-01`, `rre-rc62-constructor-float-literals-20261111-01` exit0.

## Result and next discriminators

The verified original-PE chain now includes a global condition source, indexed composite record lookup, **primitive bitmask/table tests**, stateful float updates, changed-bit detection, and conditional event-7 follow/destination clear. Every link is static behavior, **not a verified end-to-end player input or movement event**.

1. **P1 — Flag/table producer:** Find one bounded writer of the indexed high-bit table at the primitive's `receiver+0xA41`, then evaluate if table entries match any actual input control. A code reader alone does not name producer.
2. **P2 — Receiver ownership:** Trace `0x49A020` to qualify the owner supplying `+0x350`, and separately qualify one `0x7C3920` record registration site; keep object identities distinct.
3. **P3 — Physical proof:** Separately authorized operator-controlled physical LEGION RIFT, genuine RRECollector v0.4.19 navigation SavedVariables, and an exact session-bound movement/stop observation. No code-level finding is live acceptance.
