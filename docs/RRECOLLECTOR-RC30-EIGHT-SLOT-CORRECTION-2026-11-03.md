# RC-30 — implicit Lua array indexing correction and read-only SavedVariables receipt

**November 3, 2026. Owner:** Physical-PC RRE research manager. **Accepted proof:** G1 original saved-state data, **not** a live Pin→Undo operation. The exact source-qualified save now proves **eight distinct populated toolbar slots**, correcting an earlier inspection error.

## Original source, method and result

- `RRECollector.lua` in physical character SavedVariables: modified **2026-11-03T18:11:04.712Z**, **74,215 bytes**, SHA-256 **`2c3bd03dc9e8a0018f23a6c8e2ca06acfd4d3f08dcfd12077a7a54c3c7aa72b0`**.
- `toolbarSlots` is serialized as a **Lua implicit array**. The existing literal-only RRE parser returns a JavaScript array whose keys **0–7** correspond to **Lua slots 1–8**. All eight elements are valid ability-shaped IDs. This was established independently by original Lua structure/key inspection and a tightly bounded original-source text read, without printing any IDs.
- The new `tools/rc30-saved-receipt.mjs` performs a single bounded read, original-file identity/SHA check, literal-only Lua parse, correct implicit/explicit slot normalization and sanitized receipt. For this source it reports **eight valid and eight distinct pinned IDs**, **all eight present in the saved Known list**, **slot #8 populated**, root **v0.4.10**, **69 known**, **96 candidates**, and lookup sequence **5**.
- Canonical SHA-256 of the eight-slot JSON array, verified independently against the raw source: **`b592926bdeaf9af039393efe956f32ee69cbdf9e7f13b9b0892d9c5333d9c160`**. This fingerprint proves identity of that saved array on that source; it is not an in-game Undo receipt.

## Correction of earlier findings

Two different one-off inspection methods were wrong for an implicit Lua array:

1. `toolbarSlots[String(i+1)]` accessed JavaScript keys 1–7 and incorrectly treated missing JS key 8 as an empty eighth *Lua* slot. This generated the false **seven valid / slot eight empty** conclusion and the invalid canonical fingerprint `c95f2b01...`.
2. A different `toolbarSlots[String(i+1)] ?? toolbarSlots[i]` fallback duplicated the seventh source item in some cases and omitted the first, making its apparent eight-count and fingerprint `278d3938...` invalid even when the count coincidentally matched.

**Neither prior fingerprint is accepted** for the 18:11 source SHA above. The valid original file has **eight**, not seven. Earlier **06:24** and **17:33** timestamped source hashes have been preserved, but their exact original bytes are not currently available for a corrected reparse; previously claimed seven/empty outcomes for those *older* files must be treated as **unverified**, not retroactively changed to eight. No in-game Pin/Undo action is inferred from changing file hashes or timestamps.

## Verification and FreeBuff worker receipts

| Workbridge job | Accepted scope |
| --- | --- |
| `rre-rc30-saved-toolbar-structure-only-20261103-a1` | Exit 0; confirms eight JS array keys 0–7 |
| `rre-rc30-implicit-array-raw-table-20261103-a1` | Exit 0; bounded original table contains eight ability-shaped entries |
| `rre-rc30-raw-eight-slot-fingerprint-independent-20261103-a1` | Exit 0; independent canonical fingerprint matches `b592...` |
| `rre-rc30-current-8slots-source-bound-20261103-a1` | Exit 0; read-once source receipt has eight valid and distinct IDs |
| `rre-rc30-readonce-implicit-table-9tests-20261103-a1` | Exit 0; nine initial synthetic tests |
| `rre-rc30-saved-receipt-11tests-20261103-a1` | Exit 0; **11/11** tests after file-change and redaction hardening |

A two-lane FreeBuff source-only review `rre-freebuff-rc30-readonce-dual-review-20261103-a1` was launched in disposable ConPTY folders. The two processes overlapped **103.894 seconds**, but only the **file/race reviewer** returned a qualified completion marker; the slot reviewer timed out/incomplete. Do **not** count this as two completed reviews. The completed reviewer highlighted a pathname check-to-open race; a new file-identity gate and a synthetic file-replacement-during-open test now pass. FreeBuff did not interact with the game.

## Limits and next action

**RC-30 remains pending.** G1 saved file bytes do not prove the current in-memory tile rendering, whether the game process PID 33936 wrote the file, actual Pin→Undo restoration, or a deliberately associated subsequent Reload UI and saved receipt. Preserve the installed v0.4.10 package, original SavedVariables and quarantined desktop capture lease.

For a future safe source check in Windows PowerShell, use the RRE-owned **read-only** command `node tools/rc30-saved-receipt.mjs <RRECollector.lua> [--expected-sha <64-hex-SHA>]`. Output is sanitized JSON with counts/slot states and a fingerprint; no raw IDs, filesystem paths or saved Lua text. There is no background monitor or installer. Only operator-supplied current in-game Pin→Undo evidence can close RC-30.
