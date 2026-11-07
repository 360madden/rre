# SC-608 — Guarded Lab-2 mouse positioning and reversible clicks

**Accepted scope, November 7, 2026, approximately 08:12–08:16 EST:** six individually reviewed left clicks produced three RRECollector browser open/close round trips in the same Lab-2 session. Every click has guest cursor-position verification, button-down/up receipts, exact-build/window binding, lease release and watchdog cleanup. All six UI outcomes were visually reviewed from retained original images. This establishes a usable bounded positioning/left-click route for current live testing, not a statistical reliability rate or restart/resize/drag/right-click/wheel qualification.

The user explicitly authorized the operations needed for mouse qualification and prohibited Ollama. RRE remained the sole task/input manager, using one lease per click. No Ollama or alternative paid model provider ran. No casting, movement, keyboard command, addon installation, reload, game/helper restart or external source edit was performed. Mouse activity cleared the character's AFK flag; opening the browser shifted the toolbar upward, and closing it left the compact toolbar at that new position.

## Existing route and smallest repair

The existing legacy RR2 `run_targeted_click.py` workflow configuration points at an old controller plan. A read-only preflight refused it with **Controller shutdown requested**. That guard and the old stop marker remain intact. The actual current managed Lab-2 owner passed admission and advertised `targetedClickVersion=1`.

The RRE-only [mouse adapter](../tools/qualify-lab2-mouse.py) reuses the existing RR2 `ManagedPinnedHost`, fresh-byte game identity, queue/fence, screenshot validation, capture-ID review, one-use arm, targeted-click action, STOP and cleanup primitives. It introduces no new input backend, service, controller or external source dependency. Its first attempt failed before any capture/input because local capture parents were absent; STOP and exact-generation cleanup still passed. The adapter now creates those parents before acquisition.

Current guest target was `RIFT-LAB-2`, `C:\RIFT_TRANSFER\RIFT\rift_x64.exe`, PID 9752/start ticks `639294897826627677`, HWND `0x401BC`, foreground client 1211 x 702 with screen origin (0,23). Fresh-byte identity remained SHA-256 `1935a05c9db6d468e34e0055014a4a99c1b5afceb1695884e24600f5c20a4be8`. These identities and positions require rechecking before reuse.

## Live evidence

The [machine-readable receipt](REA-RIFT-LAB2-MOUSE-2026-11-07.json) records all original file paths/hashes, action/cursor events, cleanup generations, source versions, validation results and qualification limits. Private arm tokens are excluded.

| Trial | Reviewed client rectangle x/y/w/h | Visual result | Release and watchdog cleanup |
| --- | --- | --- | --- |
| browse-02 | 890 / 522 / 48 / 19 | Browser opened | Verified |
| close-01 | 1124 / 399 / 76 / 19 | Browser closed | Verified |
| browse-03 | 890 / 303 / 48 / 19 | Browser opened at the moved toolbar | Verified |
| close-02 | 1124 / 399 / 76 / 19 | Immediate image inconclusive; later independent image shows closed | Verified |
| browse-04 | 890 / 303 / 48 / 19 | Distinct settled image shows open | Verified |
| close-03 | 1124 / 399 / 76 / 19 | Distinct settled image shows closed | Verified |

All six guest-side verified screen positions equal the reviewed client rectangle's center plus client screen origin. For example, the first Browse rectangle centered at client (914,531) produced verified guest-screen (914,554). Every action contained no keys, no relative mouse delta and no wheel motion. OS delivery receipts deliberately retain `responseVerified=false`; the separate original-image review establishes the bounded UI response.

**Two practical findings:**

1. Expanding the browser moved its toolbar from y522 to y303. Reuse visual targets, not stale coordinates; the second Browse click was selected from a fresh capture at the new location.
2. The close-02 immediate screenshot, captured approximately 141 ms after button-up, still showed the open panel. A separate guarded observation at 08:14:49 EST showed it closed. This supports an early-frame/UI-update timing ambiguity, not a failed click. No repeat input was sent to resolve it. The adapter now preserves the immediate image and adds a separate capture after 350 ms; the final open/close round trip visually passed on those settled images. That delay is not claimed as a universal response bound, and visual review remains mandatory.

## Repeatable use

1. Use the [Lab-2 target policy](REA-RIFT-LAB2-LIVE-TARGET-2026-11-07.md) and existing RR2 overview handler to obtain a fresh managed inspection plan and current original image. Preserve the current controller owner, queue, source/build checks and cleanup gates.
2. Select a current reversible UI rectangle from those pixels. Run `C:\Python314\python.exe -B C:\work\rre\tools\qualify-lab2-mouse.py` interactively with `--plan` pointing to that run's `managed-host-plan.json`, a fresh `--output` under `C:\work\rre\artifacts`, the matching `--purpose open-browser|close-browser`, and `--target X Y WIDTH HEIGHT`. The tool only accepts the managed Lab-2 resource and rectangles fully inside the current client (width/height 4–128).
3. Inspect the newly returned **before** image and its exact target rectangle. Only after visual review, send `approve CAPTURE_ID specific review note` to the process's stdin within its 40-second review window. This is the model/operator's screenshot-review record, not a bypass of an application approval dialog. One arm permits one click; timeout or admission failure does not authorize retry.
4. Require process exit 0, released/disarmed/idle final state, exact-generation watchdog cleanup and visual review of the returned settled image. Retain the immediate image as well. Do not automatically replay an input because an early frame is unchanged. A new click requires a new capture, review and lease.

The adapter's JSON intentionally returns `visualResponseVerified=false`; only a subsequent independent pixel review can accept the UI effect. Its purposes are restricted to this reversible browser qualification. Other control classes require their own scoped implementation/evidence, not a relabeled arbitrary click.

## Validation and remaining limitations

- Adapter syntax/help checks passed. Six offline admission-negative cases passed: output outside RRE artifacts, reused output, Lab-1 plan, negative rectangle position, oversized rectangle, and out-of-client rectangle. None performed live I/O. The live pre-input capture-parent failure separately demonstrated STOP/watchdog cleanup on failure.
- Six actual guarded click trials exited 0, with all cursor positions, button releases, final disarmed/idle/no-input state, exact cleanup generations and visual outcomes checked. Original screenshots remain unchanged and hash-bound.
- The full research gate was attempted, then correctly rerun with the preexisting RRE `.venv` after the first system-Python attempt lacked pefile/Capstone. The `.venv` run reported **500 tests**, source inventory unchanged: validation, C2M, follow, navigation-evidence, visual-evidence, review-adapter and roadmap groups passed; collision/pathfinding groups failed their **historical executable SHA** requirements. Full gate exit **1**, not green. No old test, source pin, executable or environment was modified to make this pass. Both gate receipts/logs are linked by the machine report.
- The bounded click result does not qualify dragging, hover timing, right click, wheel input, resize/DPI changes, full-game restart, spell-button semantics, casting, or gameplay success. Lab-2 collector still visibly reports v0.4.10 with no known catalog or saved candidate result; this mouse milestone does not repair SC-103/SC-306 or RC live-data gates.

The final browser is closed, all six click leases are released, and the existing managed controller retains its own lifetime console reservation. Resume with a fresh identity/scene review, not the recorded coordinates or process epoch.
