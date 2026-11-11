# RRE RC-74 — Windows `WM_MOUSEMOVE` to native mouse-state result (LEGION)

**Date:** 2026-11-11 ~12:58 EST · **Mode:** offline, read-only PE inspection · **Outcome:** proved a Windows mouse-message coordinate writer and a five-button named-result reader. **Not proven:** player turning, camera yaw, physical mouse behavior on this LEGION session, exact Lua function registration or in-game movement/stop.

## 1. Original executable and scope

- Host independently returned `LEGION` through the LEGION-bound Workbridge command `rre-20261111-rc74-identity-001` (exit 0). Only `C:\Program Files (x86)\Glyph\Games\RIFT\Live\rift_x64.exe` was inspected; never accessed VMware, AMD-DESKTOP, running game memory, UI or another repository.
- Installed PE length **60,493,640** bytes; SHA-256 `1935a05c9db6d468e34e0055014a4a99c1b5afceb1695884e24600f5c20a4be8`; preferred image base `0x140000000`. Every address in this report is an RVA, not a process VA. Do not apply to a differently hashed build.
- Main baseline HEAD `143388b067ad1bd4ccfa183ecbc4c4ffaa8f6b15`, clean at start, `main...origin/main [ahead 29]`. No addon deployment, RIFT input, reload, installer, new provider or remote push.

## 2. Windows mouse-message → receiver coordinates: **source proven**

At entry RVA `0x7C0BB0`, the Windows-message dispatcher preserves original receiver `RCX` in `RSI` at `0x7C0BE3` and packed coordinate parameter `R9` in `R14` at `0x7C0BDD`. `0x7C0BE6` performs **`cmp edx,0x200`**; `0x7C0BF2` jumps for equality to `0x7C0E72`. `0x200` is the Win32 `WM_MOUSEMOVE` constant. This is an actual native branch, not a string/name guess.

Within that branch, `0x7C0E9A` sign-extends the low 16-bit coordinate from `R14`, `0x7C0EBA..0x7C0EC2` obtains the high 16-bit coordinate, and `0x7C0EAD` marks the stack record as numeric type **3**. At `0x7C0ECA..0x7C0ED8`, the native code passes `R9=R14`, `RCX=RSI` and record pointer `RDX` to helper `0x7C0680`.

The helper checks `[record]==3` at `0x7C0680`. On the matching path it sign-extends the low/high 16-bit components (`0x7C06A2`,`0x7C06B0`), stores them at **record+0x128/+0x12C** (`0x7C06A6`,`0x7C06B4`) and **receiver+0x30/+0x34** (`0x7C06BA`,`0x7C06C4`). It also saves the previous receiver values at record+0x130/+0x134. At `0x7C0F1E..0x7C0F37`, a changed-position or changed-mask path dispatches via the already qualified `0x7C0480` record dispatcher. This is conditional dispatch, not a claim that every message calls every callback.

**Cross-link to RC-72/73:** The saved type-3 record fields match the concrete callback `0x93B710` reading record+0x128/+0x12C and forwarding scaled values to `0x4BD9A0`, which builds the named `Event Mouse_Move` event and emits two double arguments through `0x98E8B0`. This is a coherent static source chain from a native `WM_MOUSEMOVE` case to a named game event, with conditional listener/registry gates. Whether any Lua subscriber executes on a current LEGION client was not tested.

**Do not merge distinct producers:** A separate branch at `0x7C1642..0x7C16F7` calls `USER32!ScreenToClient` at `0x7C16A6` (IAT RVA `0x25EFC60`), and conditionally writes the same receiver coordinate fields at `0x7C16E6/+0x7C16EC`. This is *not* the direct `EDX==0x200` branch above; its precise message selector is still unresolved.

## 3. Five native mouse flags → named result fields: **source proven**

Leaf getter `0x93B4B0` executes `movsxd rax,edx; movzx eax,byte ptr [rax+rcx+0x1C0]; ret`. It indexes five bytes belonging to the owning native input object. The complete result-construction routine `[0x9AC1D0,0x9AC832)` contains exact ASCII marker **`results@mouse`** (RVA `0x26D7DB8`), named keys and five direct calls to the getter:

| Index in getter | Record subcode from RC-72 | Owner byte | Named key | Getter call RVA |
|---:|---:|---|---|---|
| 0 | 1 | `+0x1C0` | `Left` | `0x9AC2D0` |
| 1 | 2 | `+0x1C1` | `Right` | `0x9AC3E4` |
| 2 | 4 | `+0x1C2` | `Middle` | `0x9AC4E8` |
| 3 | 8 | `+0x1C3` | `Mouse4` | `0x9AC5EC` |
| 4 | 16 | `+0x1C4` | `Mouse5` | `0x9AC6F0` |

The same native result builder calls `0x93B4C0` for **`x`** (`0x9AC26E`) and `0x93B500` for **`y`** (`0x9AC29E`). Those getters convert owner dwords +0x1B8/+0x1BC to float and divide by a common engine scale factor reached via `0xFB4860 → 0xFAFAB0`. Do not assert that divisor represents resolution, DPI, camera angle or world position without a separate source check.

Verified literal RVAs: `results@mouse`=`0x26D7DB8`; `x`=`0x26A65A0`; `y`=`0x26A7E3C`; `Left`=`0x26A3F98`; `Right`=`0x26A3FC8`; `Middle`=`0x26D7DC8`; `Mouse4`=`0x26D7DD0`; `Mouse5`=`0x26D7DD8`. This native result shape aligns with `Inspect.Mouse()`. The native name metadata is independently located below, although **the runtime dispatch/registration edge to this result-building function remains unproven**.

**Exact native API metadata association (new):** the original executable also contains exact ASCII **`Inspect.Mouse`** at RVA `0x26D7D98`, 32 bytes before `results@mouse` at `0x26D7DB8`. Its global `.data` descriptor-like triple at RVA `0x2F63F48` (file offset `0x2F62548`) holds 64-bit image pointers **`0x1426D7D98`** (`Inspect.Mouse`), **`0x1426D7DB8`** (`results@mouse`), then **zero**. Adjacent entries pair other named APIs and results. This directly establishes the native API name/result metadata association; it does **not** independently establish the indirect runtime call or registration edge to function `0x9AC1D0`. A bounded `.text` E8 scan found no direct call to that exact function entry (negative, not evidence of nonuse). Original table and string-window SHA values are below.

## 4. Practical reuse in existing RRECollector (no new addon)

- Current RRE source `addons/RRECollector/ui.lua` lines **997–1039** already calls guarded `Inspect.Mouse()` to consume `m.x`, `m.y`, and `m.Left`, and conditionally registers `Command.Event.Attach(Event.Mouse.Move, moveDrag, ...)` with a frame-local cursor event fallback. No new mouse observer is necessary just to demonstrate that this API path is available in source.
- Historical [RC-25](RRECOLLECTOR-RC25-TWO-LINE-TILES-LIVE-2026-11-03.md) records physical-client v0.4.8 dragging outside the title handle; this supports the addon use case but is **not a test of the current LEGION build, currently installed RRECollector or current subscriber execution**.
- A separately approved and timestamped physical LEGION test can cross-correlate native `Inspect.Mouse` fields with passive RRECollector state and an independent operator gesture. This turn performed no such test.

## 5. Exact source-window evidence

| Half-open RVA window | Bytes | SHA-256 |
|---|---:|---|
| `[0x7C0BAA,0x7C0CA0)` | 246 | `c029d0a258fe75fbfcb5fb460522e10e6793e1ba29fb7e6616bcfbf094b96d6c` |
| `[0x7C0E72,0x7C0F68)` | 246 | `b9213f64e06e82e5849a5ca0dc060672d266eb9f8bb8326a6f84bd650972f448` |
| `[0x7C0580,0x7C0750)` | 464 | `20fd7114a1bf8939731de5fdea185943c785af856204882b79de1779c45910cd` |
| `[0x7C1600,0x7C1740)` | 320 | `75f53621949975c0aa2d0214fa19f371fb46723ab129f2822475afb568a62731` |
| `[0x93B4B0,0x93B4BC)` | 12 | `a6a26820e48ad17a8d3b0bcbd4feda1e8773c54cae8e58251079a2dc9d1504bd` |
| `[0x93B4C0,0x93B4F2)` | 50 | `43f9f655aff92d513a768bd841ff5d7572ba18a4340f1fc005ac0b3cfd6fa2eb` |
| `[0x93B500,0x93B532)` | 50 | `98eacdb0162a0230ac686be864f1c8e7ab96af85bdcf39a3aaecada6494b8015` |
| `[0x9AC1D0,0x9AC832)` | 1634 | `190f28cba5e450196bb81eaee56e67a0b98886754d305e685b9b0657e194856a` |
| `[0x94CDD0,0x94CDFB)` | 43 | `62c9248ef6d76e9445e19f12918f6f4c63521fb2e68ab13a81096734c54ae044` |
| `[0x4BD9A0,0x4BDAC3)` | 291 | `c2261226ca4d3b35efaceaaefee0f9b36e71930555a7c9e31f1c4be53639415d` |
| **Data** `[0x2F63F40,0x2F63F60)` | 32 | `ae323324706e2d78f60cfe5288c7a5469eb793f640934293ab0ce2413610b181` |
| **Data** `[0x26D7D90,0x26D7DD0)` | 64 | `0f541e4263de98733260a84474fc13efae430310b05a86517d6139724cc64fa6` |

Manager checked all four Windows-branch window hashes and eight decisive instructions in `rre-rc74-mgr-wm-mousemove-final-independent-qa-20261111-01` (exit 0); independently checked seven direct getter/coordinate calls, eight exact ASCII literals and 1634-byte builder SHA in `rre-rc74-mgr-five-button-table-final-independent-qa-20261111-01` (exit 0); source fragment hash receipt `rre-rc74-mgr-final-source-fragment-hashes-20261111-01` (exit 0). Exact `Inspect.Mouse` metadata triple and two data-window SHA checks passed in `rre-rc74-mgr-inspect-mouse-metadata-triple-qa-20261111-01` (exit 0); explicit string search, descriptor-table read, and bounded direct-call scan also passed as read-only inspection jobs. Three genuine read-only source agents independently traced upstream Windows, downstream native event/no camera writes, and native result keys. No agent or manager changed a file outside these scoped RRE report/handoff files.

## 6. Next results-first work

1. **Close dynamic Lua dispatch:** the exact `Inspect.Mouse`/`results@mouse` metadata pair is found; trace the remaining registration/call edge to native builder `0x9AC1D0` rather than guessing it from adjacent strings. Reuse existing RRECollector implementation.
2. **Pursue movement-specific evidence:** identify a separate native key-action → controlled player/camera yaw or actor XYZ consumer. The mouse-UI event path is not proof of locomotion.
3. **Controlled physical validation when authorized:** verify current LEGION RRECollector package/load and compare timestamped mouse/XYZ snapshots with a bounded operator action; never transfer historical physical-PC/VM acceptance automatically.

**Exit boundary:** All original-PE evidence here is static/read-only. No actor turn, camera rotation, movement/stop, current Lua callback or real mouse event was observed this turn.
