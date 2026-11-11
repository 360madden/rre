# RC-58 — Current-build click-to-move event, query and distance clear (LEGION, 2026-11-11)

**Result (read-only native discovery):** The present LEGION `rift_x64.exe` contains an instruction-verified event-type-2 branch, a click-to-move setting gate, a coordinate-bearing query, a destination-state setter, and a later distance-dependent state-clear branch. This is the strongest **static** C2M chain qualified on this build. **No actual player movement, physical button mapping or caller ownership is proved.**

## Exact source and method

- Operating machine: **LEGION**, independently verified by Workbridge `hostname.exe` (manager job `rre-rc58-host-legion-20261111-01`, exit 0). No access to AMD-DESKTOP or VMware.
- Original installed file: `C:\Program Files (x86)\Glyph\Games\RIFT\Live\rift_x64.exe`, 60,493,640 bytes, SHA-256 **`1935a05c9db6d468e34e0055014a4a99c1b5afceb1695884e24600f5c20a4be8`**.
- RVAs are relative to preferred static PE image base `0x140000000`, never live absolute addresses.
- Three independent **read-only** agent investigations used bounded `.pdata` unwind windows and Capstone, plus a separate manager pass re-reading original bytes and verifying **9/9 full-window hashes and 671/671 decoded instructions** (`rre-rc58-manager-nine-window-crosscheck-20261111-01`, exit 0). The source hash matches RC-55–57.
- No Ghidra import, full-binary call graph, live process memory, executable patch, game input, UI reload, addon installation or remote push.

## Native event-to-destination chain

| Step | Current RVA, verified original bytes | Observation and limit |
|---|---|---|
| Callback root and arguments | `0x6A6140 4c8bf1` `mov r14,rcx`; `0x6A6143 488bf2` `mov rsi,rdx` | The eventual setter receiver is derived from the callback's **first** argument; consumed-event flag belongs to its **second** argument. That first argument is **not proved to be a player**. |
| Type-2 branch | `0x6A6146 8b0a` `mov ecx,[rdx]`; `0x6A6159 83e901`; `0x6A615C 0f849f000000` | After decrement/test dispatch, numeric event discriminator **2** jumps to `0x6A6201`. This does **not** identify a Windows button or press/release. Other dispatch values also exist. |
| Event subcondition | `0x6A6201 8b8a20010000`; `0x6A6207 83f901`; `0x6A620A 0f852d030000` | `[event+0x120]` must equal **1** to remain on the candidate path. Its application meaning is unknown. |
| Settings gate | `0x6A6238 call 0x798B80`; `0x6A6242 80b84601000000`; `0x6A6249 0f84df020000` | An accessor yields a handle; `[handle+0x146]==0` branches away. Consistent with the independently qualified `Misc_EnableClickToMove` setting, without proving present runtime value. |
| Coordinate projection | `0x6A6375`, `0x6A6382`, `0x6A6393/9B`, `0x6A639E` | Reads two 32-bit event coordinate fields `+0x128/+0x12C`, converts to floats and gates a subsequent projection-like call `0xF903D0`; screen-pixel mapping is not proven. |
| Native spatial query | `0x6A64EC e82f688d00` call `0xF7CD20`; `0x6A64F1 84c0`; `0x6A64F3 7421` | Query result in `AL` gates whether a 12-byte output is forwarded. The query wrapper has original-byte verified optional **three-component coordinate** outputs and a result-record `+0x60` check; ground/hit identity is unknown. |
| Destination setter | `0x6A6501 498b4e10`; `0x6A650D e8aee4ecff`; `0x6A6512 c6461801` | Loads receiver `[r14+0x10]`, calls setter **`0x5749C0`**, marks event field `+0x18=1`. Setter (RC-56) copies 12 bytes to `[receiver+0xB90]+0x60/+0x68` and sets activation bit `+0x1A8.0`. |
| Destination consumer | `0x588420` entry, `0x58845B` activation test | Existing RC-56 read confirmed matching state. RC-58 extended its original-byte dataflow into the distance-clear branches below. |

**Callback boundary correction:** The RC-57 selected range `[0x6A62B1,0x6A652E)` is a chained unwind **subregion**, not the function entry. Root `[0x6A6120,0x6A6195)` preserves the first/second argument aliases. No native callback registration/vtable owner or local-player resolver has been qualified.

## New consumer-distance observation

- Consumer forms a **sum of squared coordinate differences** in `xmm7` at `0x588889–0x5888C6`. In one guarded mode the middle delta is zeroed, so not every mode is full 3D distance.
- At `0x5885E0` and `0x5885F5`, default values enter `xmm8=9.0` (constant RVA `0x26AE500`, bytes `00001041`) and `xmm9=20.25` (RVA `0x26AE50C`, bytes `0000a241`).
- A separate branch reads two floats from a runtime object `[rax+0x18]` and `[rax+0x1C]` at `0x588688/0x58868E`, **squares them** at `0x588694/0x588699`, and substitutes them for `xmm9/xmm8`. Another branch substitutes both with **0.0625** from RVA `0x26AE4D8` (bytes `0000803d`) at `0x588747/0x588750`. Therefore those default values are **not globally fixed arrival tolerances**.
- The finite-value branch at `0x5889A7` compares squared delta `xmm7` with `xmm9`; `0x5889C6` enters the near branch on `<=`. At `0x588A16` it compares `xmm7` with `xmm8`; `0x588A1A` skips the clear on `>=`. The path that passes both tests directly calls state-clear **`0x546830`** at **`0x588A1F`** (bytes `e80cdefbff`).
- The square roots of the three **static literal squared values** are 3, 4.5 and 0.25, **conditional** distance magnitudes if the deltas use compatible units. Their runtime mode, physical units, and whether clearing constitutes actual arrival or a stop command are unverified. Another branch invokes follow-clear `0x5460A0` at `0x5889FA`, but cannot be labeled user cancellation from these bytes alone.

## Original-byte provenance (manager independently verified)

| Unwind window, RVA half-open | Bytes | Instructions | SHA-256 |
|---|---:|---:|---|
| `[0x6A6120,0x6A6195)` callback root | 117 | 33 | `fa13477ee8c8c9967efc334fe04cc29dadf3f2c1e38b633bc00569664790346f` |
| `[0x6A6195,0x6A62B1)` event/settings | 284 | 65 | `51b4bf0cda4354f0684026a1d2c679647b57e10a3b3154e31f7c2d5cfee3d50a` |
| `[0x6A62B1,0x6A652E)` projection/setter | 637 | 142 | `e820bb56a8d8b4ed6f21d61314d40ce003e01ec4a17e3c5d795da0f2a1e1fa09` |
| `[0xF7CD20,0xF7CF47)` spatial query | 551 | 144 | `ae78a6ae1c6bed37d01a2173c43a265a91c0d8c3c0bc28fd6f585e65c8d33564` |
| `[0x13E9FE0,0x13EA007)` query helper | 39 | 11 | `03d9b554e958d1e590ec3e9ecc4f87df18d60ed3dd009a8b42e584197901ab12` |
| `[0x588420,0x5884A7)` consumer entry | 135 | 32 | `2b57dcbdb4c7a84f243a5ba8ad35f5b1988f4135c1401158a8e9b7cee8e3ec26` |
| `[0x5885D4,0x588809)` threshold inputs | 565 | 121 | `fa9b16fb3647bf203e3e0ff5ad28db95fbff3ed9a4dffa2ba3357838d9b9db30` |
| `[0x588819,0x5889C8)` distance accumulation | 431 | 89 | `639f064bb66bfefb7c83b96fc1f4a3bcd38daa0201f468e5b52cf8a71391d3c7` |
| `[0x5889C8,0x588A51)` near-clear | 137 | 34 | `ec9c755ad12b9a99f9e0188a0217143373a59bf12b1b0da39a8790a4b95bd770` |

**Independent agent jobs (all exit 0):** `rre-rc58-owner-unwind-r14-ancestry-20261111`, `rre-rc58-owner-chain-root-continuation-20261111`, `rre-rc58-event-venv-142insn-20261111`, `rre-rc58-event-preceding-unwind-20261111`, `rre-rc58-query-original-pdata-20261111-c`, `rre-rc58-query-helper-pdata-20261111-a`. **Manager jobs (all exit 0):** `rre-rc58-consumer-continuation-bounded-20261111-01`, `rre-rc58-consumer-near-clear-window-20261111-01`, `rre-rc58-consumer-threshold-origins-20261111-01`, `rre-rc58-consumer-literal-thresholds-20261111-01`, `rre-rc58-manager-nine-window-crosscheck-20261111-01`.

## Verification status and next decisions

1. **P1 — Callback owner:** Locate a bounded registration/vtable/field-initialization relationship for the callback first argument and `+0x10` setter receiver; do not equate it to the player without evidence.
2. **P2 — Source-bound runtime observation:** Obtain separate scope-approved v0.4.19 RRECollector installation, manual `/rre navigation`, and genuine version-/session-bound SavedVariables source; no synthetic API export as game fact.
3. **P3 — Behavior acceptance:** Only under separate physical-client input authorization, compare the destination and actual motion/stop across one controlled ground gesture; static near-clear code is not a passed navigation trial.

Blocked: actual input device semantics; callback registration; local-player ownership; current in-game settings value; vector-world mapping; dynamic thresholds; genuine game motion/cancel; and any linkage to type-7 native pathfinding. The code has **not** been invoked.
