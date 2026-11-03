# RC-25 — Measured two-row ability captions, global drag and physical secure-button proof

**Date:** November 3, 2026 (UTC). **Target:** physical Windows RIFT Live x64, Atank. **Addon:** RRECollector v0.4.8. **Scope:** isolated research UI and one tested protected Reload UI click; no VM or other addon edits.

## Source change

The physical v0.4.7 screenshot showed incomplete, often single-line icon titles in a 46x25 RIFT Text frame using automatic word wrap. The v0.4.8 correction creates two independent normal Text children per 52px tile with natural pixel metrics. `tileLineFits» measures RIFT's `GetWidth» for each line; words fill the first line and overflow moves to the second line. A bounded codepoint-safe ellipsis fits overflow within 46px. Short names clear the second line, and both lines follow the existing press offset. The tile becomes 77px tall with matching borders; toolbar and icon proportions stay unchanged.

Dragging formerly bound `Event.UI.Input.Mouse.Cursor.Move» to only the 165px title handle. v0.4.8 binds `Event.Mouse.Move» through `Command.Event.Attach», using guarded `Inspect.Mouse()» and the preexisting clamped movement logic. It retains the frame-local fallback if global registration is denied and Up/Upoutside cancellation. The protected Reload UI surface remains parented to its restricted context, independently anchored to the normal header; moving the header carries the anchor without reparenting or changing its secure macro.

Primary historical API references: https://www.seebs.net/rift/pts/text_getwidth.html ; https://www.seebs.net/rift/pts/text_setwordwrap.html ; https://www.seebs.net/rift/pts/event_mouse_move.html ; https://www.seebs.net/rift/pts/event_ui_input_mouse_cursor_move.html ; https://www.seebs.net/rift/pts/command_event_attach.html ; https://www.seebs.net/rift/pts/frame_setpoint.html .

## Verification and physical-client evidence

| Gate | Outcome |
| --- | --- |
| Focused source-extracted Lua captions fixture | 9/9 PASS on exact source mirror; source SHA `d1033871c1567399975a6ea63a8566a3f71e96673bb28dd67543891354b0dabf»; fixture SHA `2be9ade5989904e0ca33928db1cfce31c93181ea6bc3af36b10242c7d13d86a6» |
| Existing candidate/TOC structural Node tests | 6/6 PASS |
| Strict package check | PASS; Environment 4.4, eight ordered Lua modules and complete metadata including Email |
| Existing RC-24 secure lifecycle and shared-button logic | Source blocks unchanged; previous 26 lifecycle and 25 controls assertions remain applicable |
| Independent Extra High source reviewer | APPROVE exact v0.4.8 UI source; fixture issue corrected before execution |
| Guarded installed release | Four changed files backed up from installed v0.4.7 at `artifacts/rc25-v048-host-backup-20261103» and installed v0.4.8, TOC last. Final README refresh copied TOC last again; strict source/installed gate 10/10 passed |
| Physical current-window rendering | Full original 2576x1408 PNG `artifacts/rc25-physical-rift-window-20261103.png», SHA `0c5c31565ccff306683b8be6c9d5e5201ea0eb444ec71d7193c4857ce6f020a3» |
| Exact v0.4.8 toolbar detail | `artifacts/rc25-physical-rift-toolbar-actual-20261103.jpg», SHA `82cc578e79e281b35d99034df2c806a54edb56c20ce75d9bde8ce895ae00e5da»; visible two rows include Summon/Banker, Shield of/the Ch..., Patron's/Artifac..., Summon/Primall..., and normal command buttons |
| Global title drag | Held-drag full PNG `artifacts/rc25-global-drag-held-20261103.png», SHA `a0db28b85ee385d51ecec1cad11f620d2d2c89b05765856b4d1af6829caae024»; crop `artifacts/rc25-global-drag-held-crop-20261103.jpg», SHA `93fd710482fca2982271e621a1d37c54755732bd3da9db82853d7d2aab6e6690». Toolbar moved about 335px left and 54px down while the pointer had left the title, then the guarded test reversed the movement before releasing. |
| Actual protected Reload UI button | One guarded Win32 mouse click on the source-confirmed restricted control triggered an Atank save **2026-11-03T02:09:06.6997842Z**, SHA `f90620596f5d3a445d61cd8c3c9b9ad377f64ac03d429e0681b4c64a2f4d8532». Saved root and macro both reported `addonVersion=0.4.8»; macro `status=registered», `reason=readback-matched». |

The first guarded `/reloadui» loaded v0.4.8 and the screenshot confirmed the title. The save still held v0.4.7 immediately after this transition. The subsequent direct click on the **Reload UI toolbar button** forced a new save containing v0.4.8, confirming the protected control worked in this revision.

## Boundaries and next task

The 46px tile abbreviates names too long for two rows; the hover card provides the full name and ID. The live screenshot establishes native rendering and the drag-held screenshot establishes movement; the source-extracted fixture uses mock Text widths. The drag script reversed its cursor path before release, though no final post-release screenshot of its exact position was captured. API-known and historical static candidate records remain separate, and caption colors do not certify ability castability.

**Next RC-26:** inspect the actual hover tooltip, browser opening/closing, row selection and pinning on physical RIFT, with guarded mouse coordinates and before/after snapshots. Preserve SavedVariables, gameplay state and the independently protected reload surface.
