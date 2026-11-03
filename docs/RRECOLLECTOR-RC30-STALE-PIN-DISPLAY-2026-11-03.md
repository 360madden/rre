# RC-30 — Correct stale toolbar pins without deleting SavedVariables IDs

**November 3, 2026 UTC.** Physical RIFT research addon only, host deployment with no in-game input or process control. **RRECollector v0.4.10 source and installation accepted; runtime NOT verified.**

## Narrow defect and fix

In v0.4.9, a saved `toolbarSlots[i]` string absent from the latest 69-ID current API-known snapshot was shown as **“Empty”**, even though the slot retained a real historical ID. A previous per-ID check could also lend stale positive status color to that display. This is misleading and must not be corrected by deleting user preferences.

v0.4.10 adds one pure, source-extracted `slotDisplayLabels` helper in `addons/RRECollector/ui.lua`:

| Slot condition | Tile | Tooltip/status | Saved state |
| --- | --- | --- | --- |
| No pinned ID (`nil`) | Empty | Empty slot / no ID | Unchanged |
| Saved ID absent from snapshot | **Not in list** | Exact ID; **NOT IN SNAPSHOT**; neutral gray | **Original ID retained** |
| Saved ID in current known snapshot | Existing ability name | Existing per-ID manual check, if any | Unchanged |
| Known record, missing name | Unnamed ability | Unnamed ability | Unchanged |

The new helper is called by **both** caption/tint rendering and hover tooltip construction. Stale IDs cannot inherit an earlier cyan or red check; icon stays hidden if no current known record exists. No changes to `loadSlots`, `pinSelected`, `undoPins`, the save schema, API collection, secure Reload UI, macro registration, drag, browser catalog, or game input.

## Source acceptance

- Reviewed UI source SHA-256: `36889ec1d848b723f602d0bf873250a5ef59b6e5e66d5288fc5608a96c6143aa` (v0.4.10 header only changed since independent Extra High approval of the functional diff).
- New `tools/verify-rrecollector-ui-slot-display.lua` extracts the **production** helper and tests both actual wiring sites. **14 assertions PASS**, including retained sparse pins/table identity, UTF-8 names, stale prior status suppression and true empty/known distinctions.
- Five existing source-extracted suites remain **10 capture + 9 captions + 25 controls + 26 lifecycle + 23 pin/Undo assertions PASS**. Total **107 assertions across 6 suites**.
- `luac64 -p` passed on all eight addon Lua source files.
- Strict manifest/source package verifier passed `Version=0.4.10` with ten source files. Independent Extra High reviewer **APPROVE** for the UI function and mock-test scope.

## Host installation and rollback

- **Before any host change:** read-only SHA guard verified **10/10** physical installed v0.4.9 files against their baselines; each was copied and SHA-verified to `artifacts/rc30-v049-host-backup-20261103` (10/10).
- Changed only **four** physical `Interface/AddOns/RRECollector` files: `core.lua`, `ui.lua`, `README.md`, and **`RiftAddon.toc` last**. Each source and installed file was SHA-checked immediately after copy.
- **After installation:** `node tools/verify-rrecollector-package.mjs --installed <physical AddOns/RRECollector>` returned `manifest=strict-pass`, `sources=10`, **`installedShaMatches=10`**, `runtimeUiVerified=false`.
- Full v0.4.9 rollback bytes remain available under the backup folder. No unrelated addon/game files or private SavedVariables were modified.

## Critical runtime proof boundary

This release **explicitly supersedes the installed v0.4.9 without ever achieving a version-matched v0.4.9 runtime receipt**. The last qualified live toolbar/save remains v0.4.8. The physical RIFT PID17412/HWND1382178 is responding, visible and not minimized, currently 974×523 and not foreground; the Workbridge screenshot adapter did not yield rendered game pixels. The latest Atank SavedVariables remains v0.4.8 (SHA-256 `bf6f34adac5256f2875ee787d549f7f93d7f5942959bf1c4c8dedfa4979bf276`, modified 2026-11-03 03:30:08 UTC) and predates the v0.4.10 install.

**RC-26 and RC-27 are still open for in-game validation.** Next when the operator has a visible, stable RIFT client: confirm a v0.4.10 title and one normal SavedVariables flush, manually Pin → Undo an API-known ability while recording the exact original eight slots, and check one stale saved-ID case if available. Stop if original slots cannot be restored in-session; never restore a running game's old saved file on disk as a substitute for UI Undo.
