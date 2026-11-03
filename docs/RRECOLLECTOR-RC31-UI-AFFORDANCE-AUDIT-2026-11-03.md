# RC-31 — Screenshot-guided UI affordance audit (plan; no addon edits)

**2026-11-03 UTC.** Read-only review of Joey's physical RIFT v0.4.10 screenshot (646×612 PNG, SHA-256 `6d4060ede113ad1f055419a80193ba561bee313d8895f540901e7846ea6c1dfb`) and `addons/RRECollector/ui.lua` (SHA-256 `36889ec1d848b723f602d0bf873250a5ef59b6e5e66d5288fc5608a96c6143aa`). The screenshot confirms a visible eight-icon toolbar and Known69/Static96 browser, **not** mouse interactions, castability, saved-state persistence, or Pin→Undo.

## Prioritized findings

1. **P1 — Misleading enabled-looking actions with no selected ability.** `draw()` lines 594–595 only set Pin text and Undo disabled state, and `RRECheckSelected` lines 870–876 is not retained as a button handle. The screenshot shows `Select a row` while `Pin to #1` and `Check selected` look enabled. Preserve the existing handler guards, retain the Check handle, and call `setEnabled(false)` for both controls until `selectedKind == "known"` and the exact ID is in `knownMap()`. Static candidates must remain ineligible for those manual known-ability actions.
2. **P1 — Abbreviated ability captions lose distinguishing words.** Actual examples include `Shield of the Ch...`, `Patron's Artifac...`, and `Summon Primali...`. `layoutTileCaption` lines 509–525 greedily consumes the first line then trims the remaining line. Explore a measured UTF-8-safe first/last-significant-word fallback, retaining each full name in the hover tooltip and preserving exact saved IDs.
3. **P2 — Crowded browser rows.** At lines 596 and 604–607, the page heading already says `API-known` but every Known row repeats `[API]`. Name trimming uses `short(...,43)`, not natural RIFT Text metrics. Remove redundant row mode prefixes, fit the entire label to width, and preserve soul suffixes to distinguish same-name abilities.

## Source-level regression plan

- Add source-extracted fixture tests for disabled/no selection, valid known, unknown known, static selection and filter changes. Keep in-handler guards.
- Extend existing two-line caption tests with screenshot names and UTF-8; enforce measured 46px line bounds and full hover names.
- Test long browser names and duplicate-name/different-soul rows against actual measured width.
- Re-run existing six Lua suites, strict package manifest, eight `luac64 -p` checks and independent code review. The visual button code at lines 124–160 already implements hover and pressed states; do **not** label these broken without a real mouse hover/down/up image pair.

## Deployment gate

Keep physical RRECollector **v0.4.10 unchanged** until RC-30 runtime validation: operator selects an API-known row, pins, clicks Undo, confirms original eight slots and produces a normal saved-state flush. Most recent read-only 04:29:43Z check still found collector SavedVariables root v0.4.9 (SHA-256 `0303d1cde261cf7096c1a65651c9e07a725eb9c99c43889a02793ad9214b94d3`). In-session Undo baseline is not separately persisted. Only then version/deploy RC-31 with rollback backup and 10/10 SHA parity.

No new game input, code changes or installed-addon changes were made as part of RC-31.
