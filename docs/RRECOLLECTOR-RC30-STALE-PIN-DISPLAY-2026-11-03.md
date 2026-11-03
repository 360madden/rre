# RC-30 — Correct stale toolbar pins without deleting SavedVariables IDs

**November 3, 2026 UTC.** Physical RIFT research addon only, host deployment with no in-game input or process control. **RRECollector v0.4.10 source and installation accepted; operator screenshot now confirms version-matched visual load. v0.4.10 SavedVariables persistence is subsequently verified; Pin/Undo and stale saved-slot appearance remain NOT verified.**

**Later November 3 correction:** [Source-hashed RC-30 eight-slot finding](RRECOLLECTOR-RC30-EIGHT-SLOT-CORRECTION-2026-11-03.md) supersedes older **seven pins / empty eighth slot** interpretations for the original 18:11 UTC v0.4.10 SavedVariables SHA `2c3bd03d...`. That file uses an implicit Lua array: **eight distinct valid IDs, slot eight populated**, confirmed against the raw table. Earlier 06:24 and 17:33 pin counts are **unverified** under corrected indexing until their old original bytes are available. No in-game Pin→Undo has been proven.

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

This release **explicitly supersedes v0.4.9 without ever achieving a version-matched v0.4.9 visual receipt**. Joey supplied a 646×612 original PNG screenshot (SHA-256 `6d4060ede113ad1f055419a80193ba561bee313d8895f540901e7846ea6c1dfb`) showing **RRE v0.4.10 research**, normal buttons, eight ability tiles, browser Known page 1/9, **Known 69**, **Static 96**, Pin to #1 and disabled Undo pins prior to any observed pin. This proves the v0.4.10 UI loaded visibly; it does **not** prove pin mutation/restoration or that any stale saved ID has been exercised. Physical RIFT remains PID17412/HWND1382178 responding and visible; separate read-only desktop metadata now shows 1936×1048 and not foreground. The newest collector SavedVariables file was written at `2026-11-03T04:12:44.514Z`, SHA-256 `0303d1cde261cf7096c1a65651c9e07a725eb9c99c43889a02793ad9214b94d3`, and still identifies root **v0.4.9**, possibly a prior UI instance flushed during transition. It cannot serve as a v0.4.10 persistence receipt. Historical v0.4.8 visual checks remain separately qualified; screenshot supplied here supersedes that version only for the visual-load criterion.

**Later 06:24:32 UTC persistence receipt (supersedes the earlier last-save statement above):** A fresh Atank `RRECollector.lua`, 74,216 bytes, SHA-256 `bdf78a8811cc9fa58fcf649bfd8fec98aa3bc93c9d02ec6c01398cc5582da8ac`, was decoded using the existing literal-only parser with read-only Workbridge jobs `rre-rc30-fresh-saved-receipt-20261103-a1` and `rre-rc30-fresh-save-candidate-integrity-20261103-a1` (**both exit 0**). Root `addonVersion=0.4.10`; the prior complete 69 known entries are intact; current candidateLookup is API-ready, 96 entries, 51 Detail returns, seven no-detail, zero errors, sequence 5. An earlier decoder **reported** seven saved toolbar IDs, Shield of the Chosen in slot #1 and slot #8 nil, but those counts/identities are **UNVERIFIED** because the implicit Lua-array indexing method was later corrected and the exact earlier 06:24 original bytes are unavailable for a new parse. The independently requalified **18:11 UTC original** contains eight distinct populated saved slots; do not transfer its count backward to this file. This **confirms v0.4.10 persistence** and preserved saved data, not the manual Pin→Undo sequence, an Undo-restored in-memory baseline, secure Reload UI click or actual stale-ID tile rendering. RC-26/27/30 live interaction gates remain pending. No game input, addon file edit, SavedVariables write or desktop capture was performed by RRE.

**Later physical session identity (2026-11-03 08:04 UTC):** Read-only Windows window inventory now shows `rift_x64` PID **13584**, HWND **19596868**, title `RIFT`, window dimensions reported as 1936×1048, not foreground. Independent read-only `Get-Process` returns the same PID/HWND, `Responding=true`, process start `2026-11-03T06:25:03.233Z`. The earlier PID17412/HWND1382178 above is historical. The verified v0.4.10 SavedVariables file was written **31.186 seconds before** this current process started, and its SHA remains unchanged at the 08:04 check. The earlier version-matching screenshot is **not bound to the new PID/HWND**; current-process addon load, in-memory eight-slot baseline, Pin→Undo, secure Reload UI click and post-Undo persistence are **not verified**. Operator must first confirm the visible **v0.4.10 title and exact current slots**, then follow the in-session Pin→Undo sequence. No game input, desktop capture retry, or quarantine-lease mutation was performed.

**RC-26 and RC-27 are still open for in-game validation.** Next when the operator has a visible, stable RIFT client: confirm a v0.4.10 title and one normal SavedVariables flush, manually Pin → Undo an API-known ability while recording the exact original eight slots, and check one stale saved-ID case if available. Stop if original slots cannot be restored in-session; never restore a running game's old saved file on disk as a substitute for UI Undo.
