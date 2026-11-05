# SC-103 — LuaPad preview20 installed-source compatibility addendum (2026-11-04)

**Status:** Read-only disk-source compatibility review, **NOT** in-game load or SC-103 execution proof. **Owner:** physical-PC RRE manager; independently owned LuaPad files were not modified.

## Source identity and supersession

- Installed physical-PC `luapad/RiftAddon.toc`: `Version = "2.0.0-preview20"`; SHA-256 `b3caba8124274cb744f693f727726edc5cbb3ff38733158eae511bed90a4d11b`.
- Installed `luapad/main.lua`: SHA-256 `34bf8d962c700862f655d5c60c58e5a76a01ca8c3c26eb4299e55a38ed5f6e59`; both installed source files were last modified on November 4 at approximately 14:05 UTC.
- RRE staged `tools/sc103_luapad_hover_probe.lua`: SHA-256 `fbf1199a7fc85f126157e477211044762dc3fbc0fcb943c05726941c70d1c816`. One-shot `tools/sc103_luapad_copy_result.lua`: SHA-256 `478e81c2d83d7406c7998f8f6ebe311c3785a2acf4b7ca37b7689ad338f06406`.
- The prior [pinned SC-103 hover guide](REA-RIFT-SPELLCASTING-SC103-LUAPAD-HOVER-PROBE-2026-11-03.md), SHA-256 `fec94cb5482c255489696606253de71e1cf645a40bbd4dccfb852aca798b7374`, correctly records historical preview14/preview16 **disk** observations. This addendum supersedes its *latest installed version* statement without changing the pinned guide, the six-source SC-604 supplement, or the immutable interim mechanism graph.

## Focused source-behavior matrix

| Preview20 source | Read-only observation | Operator consequence |
| --- | --- | --- |
| `main.lua:300–302` | Run invokes `LuaPad.doRun` | Existing operator-pasted one-shot probe path remains structurally available |
| `main.lua:502–531` | Run clears prior Output; `loadstring`/`load` compiles; protected synchronous execution temporarily substitutes global `print` then restores it | Initial `ARMED_12_SECONDS` appears in LuaPad Output; asynchronous frame-update result is expected in **RIFT chat** after Run returns |
| `main.lua:310–328` | Copy Output forwards current `lastOutput` to `Command.CopyToClipboard` | Copy helper's newly printed result **before another Run**, and verify actually pasted clipboard contents; a protected call is not proof the clipboard contained the intended text |
| `main.lua:175–203,675–683` | Output display is bounded and the retained printed tail has a separate limit | Short allowlisted SC-103 statuses fit source limits; no guarantee for arbitrarily long pasted output |
| `main.lua:491–497` | Nested synchronous Run is rejected | No conflict with the intended one-shot sequence |
| `main.lua:129–142` | Title/version derives from `Inspect.Addon.Detail("LuaPad").toc.Version` | An **actual live** title can qualify the loaded version, unlike matching installed files |
| `main.lua:466–488,704–709` | Startup may raise/show LuaPad window | Operator must keep LuaPad clear of the native Soul Tree tooltip during the 12-second hover observation |

**Compatibility verdict:** No source-level Run/Copy/Output contract change was found that requires modifying the staged RRE SC-103 Lua probe or one-shot helper. This does **not** establish that preview20 is loaded in the running client, that `Inspect.Tooltip` produces a modern Protector's Fury ID, or that a clipboard copy, callback, or event detach succeeds live.

## Required next game-session evidence (operator-controlled)

1. Establish a **new physical RIFT process/session** and visible LuaPad title `2.0.0-preview20` (or record the actual loaded version instead). On the November 4, approximately 19:00 EST read-only tasklist check, no physical `rift_x64.exe` was running; this is a point-in-time observation.
2. Capture the current Atank role, selected Legendary counters and **native** Protector's Fury Soul Tree tooltip without LuaPad obscuring it.
3. Operator may manually Run the already staged 12-second SC-103 hover probe once, preserve the initial LuaPad Output and the later RIFT-chat result, and only afterward use the optional copy helper if needed. Stop on Attach/Detach ambiguity or source/session mismatch; do not infer identity from an ability-shaped ID alone.

No RRE-controlled game input, reload, memory/process manipulation, installed addon change, source replacement, private SavedVariables access or GUI quarantine bypass occurred during this source review.
