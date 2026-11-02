# RC-20 — Reload UI plain-frame binding repair

Date: November 2, 2026. Physical-PC RIFT. Addon version 0.4.4.

User reported that the v0.4.3 Reload UI button did not work. Its binding was set on a plain Frame after attaching ordinary Mouse.Left.Down/Up handlers. The installed Gadgets wtDataTextBar.lua provides a directly relevant working plain Frame with SetSecureMode('restricted') and EventMacroSet(Mouse.Left.Click,'reloadui'), but no ordinary Down/Up handlers. Therefore the extra handlers were a plausible cause, not a proven one; no v0.4.3 runtime error transcript is available.

Repair: avoid registering Down/Up (including Upoutside) on the macro frame while preserving their behavior on all ordinary buttons. Keep the working Gadget-style cursor hover and secure registration. Handle explicit false returns and exceptions from SetSecureMode/EventMacroSet. Save a small character-scoped uiReloadMacro registration receipt (registered/failed, version, short reason). Registration is not execution; an actual hardware click and runtime observation are required.

Source commit 34fc84693b5976ef82153f176143d4fff3982bc0. Six focused checks, strict TOC, Git diff check pass. Physical-PC RRECollector installation updated only four files after verifying the prior hashes and backing them up in docs/rc20-v044-host-backup-20261102; manifest last. Strict install verification rc20_reloadsecure_installedgate_20261102 exited 0: version 0.4.4, source files 10, installed hash matches 10. All other addons untouched. In-game functional gate remains pending.
