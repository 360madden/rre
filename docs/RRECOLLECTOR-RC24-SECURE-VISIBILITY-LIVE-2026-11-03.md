# RC-24 — Secure visibility, physical UI capture and autonomous reload

**Date:** November 3, 2026 (UTC). **Target:** physical Windows PC RIFT Live x64, Atank. **Addon:** RRECollector v0.4.7. **Scope:** one addon; no VM or other addon edits.

## Problem and source-backed correction

RRECollector v0.4.6 had two independent visibility hazards. Its Hide handler concealed the ordinary bar first, then silently ignored a denied SetVisible on the separate restricted Reload UI frame. Its macro initializer also published the protected frame before registration succeeded. Under RIFT's secure environment a failed registration can prohibit its cleanup, leaving a topmost orphan.

The independently reviewed v0.4.7 correction:

1. Keeps the separate restricted parent and click macro that Joey confirmed working in v0.4.5.
2. Checks Inspect.System.Secure when supported before creating the control.
3. Constructs the reload frame hidden while it is normal, restricts its parent/child, registers/readbacks reloadui, and shows/publishes the frame only after success.
4. Changes the restricted sibling first when toggling visibility. Denial leaves the normal bar and browser unchanged; normal-frame errors trigger guarded rollback and a visible console message.
5. Places an icon hover card above a bottom-docked bar when the card would fall outside the viewport.
6. Keeps the existing normal rectangular buttons and un-stretched Text measurement layout.

Published historical API references: https://www.seebs.net/rift/pts/frame_setvisible.html ; https://www.seebs.net/rift/pts/frame_setsecuremode.html ; https://www.seebs.net/rift/pts/frame_eventmacroset.html ; https://www.seebs.net/rift/pts/inspect_system_secure.html .

## Verification

| Gate | Result |
| --- | --- |
| Candidate/source structural checks | 6/6 PASS after removing hard-coded 0.4.6 test version expectations |
| Existing shared-control behavior | 25 assertions PASS in container texlua, with simulated RIFT frames |
| New source-extracted lifecycle/geometry behavior | 26 assertions PASS in container texlua; exact source and fixture SHA hashes verified |
| Independent Extra High reviewer | APPROVE; final ui.lua SHA-256 `5fa95597ec103602257b12ef833be919897fb229cc7f547dc429701d5530eadc` |
| Strict TOC | PASS; Email, environment 4.4, all eight ordered Lua scripts |
| Physical-PC installation | 10/10 source-host SHA matches, TOC copied last; changed-file backup in `artifacts/rc24-v047-host-backup-20261103` |
| Current-game visual | Exact RIFT window captured at 2576x1408 with v0.4.7 title and normal button captions visible |
| Current-game persisted version | Atank root `0.4.7`, macro version `0.4.7`, status `registered`, reason `readback-matched` |
| Autonomous reload | Scoped physical window keyboard command submitted and followed by a new v0.4.7 save |

## Direct runtime evidence

- Physical process/window: `rift_x64` PID **17412**, HWND **1382178**, class `TWNClientFramework`, verified before desktop operations. PID/HWND are volatile and must be rediscovered next time.
- Ordinary WinApp capture returned `UI_TURN_BUSY`. A guarded Windows-native fallback restored only the verified RIFT window, captured the foreground window, and returned it to the previous minimized state.
- Full original: `artifacts/rc24-physical-rift-window-20261103.png` (SHA-256 `d8c2e37c0be32ea7737cf9a3e8b4b305d3305f125514c05f825951dc940399c2`).
- Exact toolbar crop: `artifacts/rc24-physical-rift-toolbar-crop-20261103.jpg` (SHA-256 `c8308bc7a77ee9cefbf287c2634c71c624df8658cf7cdff0db0ce4ea082825ba`).
- Guarded physical reload job: `rre-rc24-physical-ui-reload-guarded-20261103-a1`, exit 0. It verified process and foreground HWND before sending Enter, `/reloadui`, Enter, then restored minimized state. This command itself is not proof of in-game execution; the subsequent saved record supplies that evidence.
- New Atank save modified **2026-11-03T01:48:03.8924359Z**, SHA-256 `d990c5b3e057f0891d1070c6cff1cc24fa7b38fc2848312f8d6a79ea481d8413`; safe literal decoder confirms 69 known abilities, preserved probe and 50 returned unlisted candidate details.
- The UI screenshot shows legible command button text and normal borders. Several tile names remain abbreviated to one line, despite the two-line design goal. This specific defect is RC-25.

## Limits and next action

The source-extracted Lua tests use mock frames; they do not prove native hit testing. The direct screenshot proves v0.4.7 rendering and the external /reloadui command's success, but the secure **Reload UI toolbar button** was not independently clicked in this revision. Captured candidate metadata still does not prove learned/unlocked/castable states.

**Next:** RC-25 should use this exact screenshot to improve two-line ability labels and study title dragging beyond the 165x36 handle. Reuse the physical screenshot/reload route with fresh PID/HWND and full source/TOC/runtime gates.
