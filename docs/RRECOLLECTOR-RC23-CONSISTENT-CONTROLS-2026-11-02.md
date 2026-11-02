# RC-23 — Consistent plain controls and measured text

Date: November 2, 2026. Target: physical-PC RIFT only. Installed version: RRECollector 0.4.6.

## Evidence and diagnosis

Joey supplied a cropped physical-RIFT screenshot showing v0.4.5 and explicitly reported that Reload UI works. Accept RC-22 at operator-attested click scope, with the screenshot proving the rendered version. Uploaded image SHA-256: e2d2b2aeec70814a79311c672bbc0be3a955500ab8e2a0a1caf727bbb158f49d. The conversation image is not copied into the repository.

The screenshot and source show different presentation paths: ordinary controls had a bottom line and varying caption sizes, while Reload UI had its own fixed 11-point caption and no matching border or visual handlers. Ability names were reduced to seven-character previews. The ordinary text fitting also called GetFullWidth through pcall, potentially swallowing failure and retaining a character-count font estimate.

Research: the generated RIFT API reference marks Text:GetFullWidth hard-deprecated/disabled (https://www.seebs.net/rift/pts/text_getfullwidth.html). Text:GetWidth remains documented (https://www.seebs.net/rift/pts/text_getwidth.html). The StarTip author independently records replacing GetFullWidth with GetWidth (https://www.riftui.com/downloads/info44.html). Historical custom-button discussion at https://riftui.com/forums/showthread.php?nojs=1&p=102 supports normal Frame/Text presentation, but its obsolete measurement/event examples were not copied. The security reference explicitly permits normal children under restricted frames (https://www.seebs.net/rift/pts/frame_setsecuremode.html). Historical documentation guides implementation; it is not a current game-render observation.

## Implementation

A shared buttonVisual helper now provides four-sided borders, a uniform 13-point starting font, measured width/height fitting, hover tint, pressed border reversal and a one-pixel caption depression, release-outside reset, disabled states and separate selected-tab styling. Visuals are normal child frames. The working restricted reload context, restricted click surface and single reloadui macro registration remain intact; only its normal visual children and visual-only pointer callbacks changed. No ordinary Lua click handler is attached to the secure Reload UI surface.

Ability icons remain square (40x40), with larger 52x74 tiles, two-line bounded labels, full-name/ID/status hover cards, four-sided state borders and visible press offset. Texture assignments are cached between pointer events. The toolbar is 18 pixels taller; browser offset and expanded-view clamping follow its actual height. No casting, ability discovery, SavedVariables snapshots, other addon or VM was changed.

## Validation and deployment

Source commit: 85c102d674e041eeb8cd5be91ec4c38916d170dd.

Six existing source checks, strict complete-TOC validation and git diff --check passed in Workbridge job rre_rc23_final_source_gates_20261102_a1. Twenty-five control-behavior assertions passed in an isolated Lua 5.4 interpreter with mocked RIFT frames, including ordinary activation, disabled behavior, cancellation, long-caption fitting, UTF-8 truncation and protected-host/macro preservation. Tested shared-helper SHA-256: 8bc6ecde234ac4e87621a9190cb737fd300bea787807fab1dc596df04931b8a3; the source gate verifies that exact block. Reusable fixture: tools/verify-rrecollector-ui-controls.lua. No Lua interpreter was found on the host command PATH; the behavioral test was executed in the assistant container, not inside RIFT.

Deployment job rre_rc23_v046_deploy_20261102_a1 exited 0. Previous v0.4.5 installed bytes were hash-checked and backed up to docs/rc23-v046-host-backup-20261102. Only ui.lua, core.lua, README.md and RiftAddon.toc were updated; TOC was copied last. The strict installed verifier returned version 0.4.6 and 10/10 matching source/installed hashes. All required TOC fields, including Email, and script order are unchanged.

No independent AI agents were launched: exposed Workbridge agent tools only track assignments, and the existing local model service was unreachable. Source/package/diff checks ran concurrently as command jobs, not reasoning agents.

## Remaining boundary

The new v0.4.6 visual behavior has not yet been observed inside the game. The supplied screenshot and successful reload report apply to v0.4.5. Use its working Reload UI control to load the already-installed revision. Do not claim that mocked behavior or hash parity proves current in-game rendering. RC-08's accepted 50 unlisted ability responses remain intact and are unrelated to this UI-only revision.
