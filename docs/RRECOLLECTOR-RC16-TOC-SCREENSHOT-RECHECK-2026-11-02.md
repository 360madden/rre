# RC-16 — RRECollector TOC and physical-PC screenshot recheck; mandatory release gates

**Date:** November 2, 2026 (Eastern). **Owner:** RRE/REA manager. **Scope:** read-only installed-addon/screenshot diagnosis plus source-only packaging policy and verifier; no game input, addon reinstall, or VM changes.

## Observed result

The installed physical-PC RRECollector v0.4.0 **TOC is complete**, SHA-256 `82a18451d54992b98fd98ff3d24888dc038f64e555d5c28ad47fad7b9760e3b3`, matching the Git source. It contains all ten contract fields: `Identifier`, `Name`, `NameShort`, `Description`, `Author`, `Email`, `Version`, `Environment`, character `SavedVariables` and ordered `RunOnStartup` (eight existing Lua scripts). Syntax and relevant metadata were independently compared read-only against installed BotDsBridge, RiftReader2Casting, RiftReader2 and JAB TOCs. **No missing required field or bad dependency order was found.**

The configured physical-PC folder `C:\Users\mrkoo\OneDrive\Documents\RIFT\Screenshots` contained **162 JPG screenshots** at the bounded `2026-11-02T16:27Z` inventory; the most recent `2026-11-01_210700.jpg`, mtime `2026-11-02T02:07:00.452Z`, size 1,483,076 bytes. There is **no November 2 screenshot** in this folder. The RRECollector v0.4 install completed at `2026-11-02T16:06:43.771Z` (11:06 a.m. Eastern). Therefore the screenshot folder **cannot show whether the newly installed toolbar appears**. Absence of a current image is not evidence the TOC failed.

Historical v0.3 SavedVariables root `addonVersion="0.3.0"` was written at 15:18 UTC, *before* v0.4 installation; it preserved the 69 known-ability capture and v0.2 probe but had no `candidateLookup`. Installing new files under a running client does not itself reload Lua. **Fresh host check at 16:36 UTC:** the only Atank RRECollector saved file remains that same 15:18 UTC v0.3/31,081-byte SHA, job `rc16-current-collector-save-gate-20261102-a1` exit 0 (48 directories bounded, one match). Read-only process query `rc16-physical-rift-session-age-20261102-a1` exit 0 still observes physical RIFT PID 17412, started about 04:36 UTC, before installation. An in-game `/reloadui` would not change the PID, so the process start time alone cannot exclude a reload. **No post-install SavedVariables flush or screenshot evidence exists.** v0.4 remains **installed and not independently verified as loaded or visible**.

## Stronger durable addon checks implemented

New source-only `tools/verify-rrecollector-package.mjs` performs a strict, dependency-free read of the real TOC: rejects missing, duplicate or unexpected fields, unexpected/unclosed table syntax and BOM; requires matching addon folder/Identifier, `Environment="4.4"`, character SavedVariables, exact eight-script order and real module files; cross-checks Version with `core.lua` and README. Optional `--installed <RRECollector path>` compares source and physical installed **SHA-256 for all ten files**. The machine output deliberately reports `runtimeUiVerified:false`.

Two read-only jobs passed with exit code 0:

- `rc16-strict-toc-source-20261102-a1`: `manifest=strict-pass`, source files 10, version 0.4.0.
- `rc16-strict-toc-installed-20261102-a1`: `manifest=strict-pass`, installed SHA matches **10/10**, version 0.4.0.

Also updated `AGENTS.md` and the durable [SC-605 custom-addon playbook](REA-RIFT-SPELLCASTING-SC605-CUSTOM-ADDON-PLAYBOOK-2026-11-01.md) to enforce **three distinct gates**:

1. **Manifest:** strict syntax/fields/order/version and recognized local-addon comparison.
2. **Install:** narrow RRECollector-only copy with TOC last, then complete source/host hash equality.
3. **Runtime:** fresh version-matched SavedVariables and visually observed toolbar/direct equivalent before marking functional.

Gates 1 and 2 pass for current v0.4. **Gate 3 is open.** Do not change the manifest merely because a toolbar is absent. A future v0.4 saved root with hidden UI would justify a small `uiAttempt` initialization-reason diagnostic; absent v0.4 persisted root would instead prioritize addon load/enablement or lack of reload. No game commands were issued.

## Next discriminator

The operator controls normal RIFT `/reloadui`/logout. When the installed addon is next loaded, check for a v0.4 startup chat message and the top-left research strip; optionally `/rre ui` toggles it. A **new** screenshot saved under the configured physical-PC folder and a subsequent normal SavedVariables flush permit a source-qualified visual/runtime assessment. Do not request simultaneous soul/trainer/spellbook windows or recapture the original 69 abilities.

This RC-16 source/policy work does not change the installed addon bytes or the blocked RC-08 lookup/runtime verification scope.
