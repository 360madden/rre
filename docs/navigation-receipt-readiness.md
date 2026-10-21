# NAV-004 — Saved RR2 receipt readiness checker

October 21, 2026. This is a small file-only follow-up to NAV-003. It does not normalize incomplete historical receipts into navigation traces or touch a live game.

`tools/navigation_receipt_readiness.py` reads one bounded JSON RR2 delivery receipt and publishes a deterministic readiness assessment. It distinguishes **historical** player ID/XYZ, game process identity and executable hash from **current** scene/freshness, C2M settings, reviewed ground click, actual movement/stop observation and live ownership/approval. All current capabilities remain false unless separately qualified: this tool never treats the historical `fresh` flag as a present-time guarantee. The RR2 receipt's `target` is a game **process target**, not a selected in-game entity.

From PowerShell in `C:\work\rre`:

```powershell
& .\.venv\Scripts\python.exe -B tools/navigation_receipt_readiness.py --receipt C:\work\riftreader2\artifacts\live-validation\live-fresh-receipt.json
```

An optional `--output artifacts/some-new-name.json` publishes a new JSON file without overwriting existing data. Keep publication under the RRE artifacts directory for retained reports. The input is limited to 2 MiB, duplicate JSON keys and nonstandard numbers are rejected, and no source files are modified.

This is a **readiness gap audit**, not the future normalizer. It does not fabricate a reviewed screenshot, click point, clock alignment or missing samples. Use it to avoid wasting work on old receipts and to request only the specific evidence the existing RR2 execution workflow needs to supply. When real, fully associated source records exist, NAV-003 can inspect a separately reviewed normalized trace. NAV-002 remains blocked on the four documented prerequisites.

Verification: `tools/tests_navigation/test_navigation_receipt_readiness.py` contains 12 focused tests, including actual historical receipt shape, malformed evidence, no overwrite, and rejection of unsupported present-time conclusions. No live inputs or control were issued.
