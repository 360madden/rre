# FreeBuff RRE reviews — SC-103 and RC-30 (2026-11-03)

**Outcome:** Two genuine FreeBuff model review sessions completed through the pre-existing Windows-native ConPTY adapter. Single RRE manager reviewed the conclusions; original game/addons, VMware, SavedVariables and Workbridge code were unchanged.

## Transport and actual receipts

- Original proven helper (read-only dependency): `C:\work\workbridge-mcp\scripts\freebuff-conpty-probe.py`, SHA `c29fbfd898c5fe54e86e34403a79ef4d1107761f4828deed153be4be3de3c07f`.
- New RRE-owned specialization: `tools/freebuff-rre-review.py`, SHA `6167b76902b68bfc8df7904a1d8150e951e535cf1552ecc5dae72866c40d73b4`. It pins the trusted helper hash, makes fixed in-memory replacements for RRE source copies and prompts, uses exclusive disposable Windows TEMP folders, and requires positive completion marker, owned process stop and folder cleanup. It never edits the Workbridge helper. Source copies are not an OS-enforced sandbox.
- Native FreeBuff CLI version **0.2.35** (global npm wrapper package 0.0.128); Desktop 0.0.198 is installed but not driven here. FreeBuff, **not Ollama**, performed the inference. Its actual internal model was not independently attested.

| Review | Workbridge job | Verified status and duration |
| --- | --- | --- |
| SC-103 | `rre-freebuff-sc103-real-review-20261103-a1` | Exit 0; final `REVIEW_END_41`; **59.3 s**, 15:38:24.926–15:39:30.010 UTC; owned process stopped and temp copy deleted |
| RC-30 | `rre-freebuff-rc30-real-review-20261103-a1` | Exit 0; final `LIFECYCLE_DONE_53`; **50.3 s**, 15:40:36.437–15:41:32.312 UTC; owned process stopped and temp copy deleted |

Both were requested together but **recorded execution times did not overlap**. Do not claim simultaneous inference or equate Workbridge's 36 command slots with 36 AI agents. A future single supervisor may be useful to test actual overlap.

## SC-103 — accepted narrow bug

The FreeBuff reviewer located a source defect in the pre-existing staged `tools/sc103_luapad_hover_probe.lua` at original lines 75–79: if `pcall(Inspect.Tooltip)` failed transiently after two matching ability reads, it incremented `failures` without clearing `state.stable` / `state.lastId`. The next matching ability could erroneously count as the third **consecutive** valid sample. The RRE manager inspected source and reproduced that state transition in a source-extracted **expected-red** Lua 5.4 mock.

**Fix:** In the failure branch reset both `state.lastId = nil` and `state.stable = 0`. The source-extracted **green** Lua 5.4 check passed, and an intermittent fault test was added to `tools/test_sc103_luapad_hover_probe.lua`. No game or installed addon files were changed.

**Important testing limit:** The prior full fixture had **110 passing Lua 5.4 assertions** under its previous exact SHA. The modified source and fixture **have not yet been rerun as one complete exact Lua suite**. The source-extracted red/green check does not replace the full-suite receipt. Current native RIFT/LuaPad compatibility and modern Legendary ability ID are still unverified.

## RC-30 — conditional leads only, no collector edit

1. **Baseline generation replacement:** At the first pin, `pinSelected` stores the then-current `storage.toolbarSlots` reference. `undoPins` restores it into the presently active `RRECollectorData.toolbarSlots`. A contrived external replacement of the *whole* RRECollectorData table between pins can resurrect an earlier table. This sequence was independently reproduced with source-extracted Lua 5.4 logic; no evidence yet that the physical client performs such a replacement.
2. **Malformed persisted entries:** `loadSlots` copies only strings of at most 128 bytes. A numeric/oversized entry omitted in memory will not be included in a later persisted pin table. This is a **validation boundary for unsupported data**, not demonstrated loss of a valid historical ability ID. Do not alter the frozen source on this hypothesis.

Physical RRECollector **v0.4.10 remains frozen** pending current in-memory eight-slot baseline, Pin→Undo before Reload UI, full restoration and a new matching SavedVariables proof. Workbridge's desktop-capture quarantine is not bypassed.

## Future work

Use the proven FreeBuff ConPTY path (not Ollama) for isolated bounded source review, independent acceptance and one RRE writer. Verify revised Lua suite when a compatible interpreter is available. Preserve SC-103 rank/variant and RC-30 live acceptance blockers. Do not repeat the parked native Ability List trace.
