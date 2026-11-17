# RIFT Update Analyzer v1 — offline game-update helper (2026-11-17)

Implemented and offline-tested on AMD-DESKTOP. Actual post-patch compatibility remains UNKNOWN until the Glyph/RIFT updater finishes. The source lives in RRE but can compare any two explicitly supplied local AMD64 RIFT PE files; other repositories remain untouched.

## One-command launcher (AMD-DESKTOP)

After the updater has fully finished, open PowerShell and run:

    & 'C:\work\rre\tools\Run-RiftUpdateAnalyzer.ps1'
    $LASTEXITCODE

The launcher prints its machine name and a unique report path. It creates report.json and report.md inside a NEW directory under C:\work\rre\artifacts\rift-update-analyzer-*. Existing reports cannot be overwritten; executable inputs are never written.

Exit codes:
- 0 MATCH — executable SHA is identical. Running process, addon, player ownership and gameplay remain unqualified.
- 2 CHANGED — executable SHA differs, even if only headers/overlay changed. BLOCK reuse of old-build native RVAs, pointer chains, vtables and signatures until requalified.
- 3 ERROR — missing/unstable file, unexpected baseline SHA, malformed or non-AMD64 PE, ambiguous sections, invalid command or unsafe report destination. Compatibility UNKNOWN.

PowerShell execution policy or Python failures must be resolved through normal approved setup; the helper does not change system policy or install packages.

## Portable Python CLI

Run on a machine with Python 3.9+ and separately verified local files:

    & 'C:\Python314\python.exe' -B 'C:\work\rre\tools\rift_update_analyzer.py' --before 'C:\work\RIFT-Build-Baselines\1935a05c9db6d468e34e0055014a4a99c1b5afceb1695884e24600f5c20a4be8\rift_x64.exe' --after 'C:\Program Files (x86)\Glyph\Games\RIFT\Live\rift_x64.exe' --anchors 'C:\work\rre\tools\rift_update_anchors.json' --output-dir 'C:\work\rre\artifacts\rift-update-CHOOSE-UNIQUE'

Override --expected-before-sha only for a separately verified *different* baseline; use a corresponding SHA-pinned manifest. Report controls: --block-bytes 64..1048576 (default 65536), --max-blocks 1..256 (default 128).

## Evidence produced

1. Whole-file SHA-256 and size, plus rehash and restat at completion to detect possible updater races.
2. Strict PE32+ AMD64 header, file-backed/virtual section table and overlap validation.
3. Per-section old/new RVA, file offset, sizes, executable flag and SHA-256. Changed mapped sections include bounded changed-byte-block ranges with old and new RVAs. This is **not** automatic function/semantic matching.
4. Four SHA-bound ROOT-001 instruction-byte canaries from tools/rift_update_anchors.json. The original must match its expected bytes. Identical bytes at the same RVA in the new file do not prove callback reachability, player identity or live validity.
5. JSON schemaVersion 1 and a Markdown summary. Changed whole-file SHA always returns CHANGED, even when section bytes match (e.g. header/overlay edits).

This helper neither launches/controls/modifies RIFT nor accesses VMware or a live process. It does not change old evidence, installed addons, Git pins or external repositories. The existing Soldier script C:\work\Soldier\scripts\Test-RiftClientBuild.ps1 remains the fast SHA-only gate.

## Verified starting position (November 17)

- Native host: AMD-DESKTOP; RRE at C:\work\rre.
- Preserved baseline: SHA-256 1935a05c9db6d468e34e0055014a4a99c1b5afceb1695884e24600f5c20a4be8, 60,493,640 bytes. Saved outside Git under C:\work\RIFT-Build-Baselines.
- First real-file run: MATCH, zero changed sections, four anchor checks, exit 0; job rre-1117-update-analyzer-real-before-after-1.
- Synthetic regression suite: 12/12 tests passed, exit0, job rre-update-analyzer-synthetic-final-green-1117-1. Includes header/overlay-only changes that must return CHANGED, invalid CLI returning ERROR, malformed/overlapping PE, changed/added sections, bounded output, anchor pin validation and report overwrite refusal.
- Actual one-command PowerShell launcher: HOST=AMD-DESKTOP, MATCH, zero changed sections, four pinned anchors, exit0; job rre-update-analyzer-powershell-launcher-real-1117-1. Independent generated report directory: artifacts/rift-update-analyzer-20261117-121811-10e9fbe2 (report.json and report.md). No game/UI/VM operations or installed-file edits.
- Generated reports under ignored artifacts are disposable; *never delete the preserved pre-update executable or the verified RRECollector v0.4.20 rollback*.

## Follow-ups

P0 — After update finishes, run the helper. Result: MATCH / CHANGED / ERROR and two reproducible reports. Joey indicates update completion; coordinator executes.

P1 — If changed, preserve the new file separately by its SHA, then rederive only impacted WA-006/ROOT-001/C2M locations offline using existing RRE analyzers. Do not reuse old pointers, change source pins or trigger full imports. Coordinator can proceed.

P2 — If separately authorized, physically verify the active client, current addon loaded version and RREC2/SavedVariables, then revalidate affected gameplay observations. RRECollector 0.4.21 is on disk but last directly observed UI/save were 0.4.20. SC-629 pending; RC-30/RC-88 stopped. Requires Joey and live-owner coordination.
