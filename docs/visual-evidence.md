# Screenshot evidence: architecture, contract and usage

## Scope

The RRE screenshot-evidence consumer is implemented at `tools/visual-evidence.py` with separate `visual_evidence/evidence.py` (identity/file checks), `matcher.py` (screen-space diagnostics), and `cli.py` (packaging/reporting). It reads saved RR2 client captures and optional context screenshots. It does not capture a live screen, send game input, open a game process, run a model, or alter VMware. Existing RR2 producers remain unchanged.

Architecture:

```text
RR2 client capture / recorded console screenshot + capture metadata
           + action results + host journal
                          |
               hash-pinned visual spec
                          |
         recorded VM/session/action association checks
                          + bounded scene-patch diagnostics
                          |
        portable originals + annotated PNG previews
        + report.json + report.html + review-packet.json
                          |
                  complete.json (last)
```

Screenshots are now an explicit evidence type in RRE validation, not a substitute for typed observations, original native bytes or code QA. The image checker observes pixels independently of controller delivery claims; it is Manager-authored software, not an independently authored reviewer. A generated review packet does not establish that a vision model received its images.

## Existing image runtime

Verified local runtime: `C:/work/riftreader2/artifacts/tools/control-python/Scripts/python.exe`, Python 3.14.6, Pillow 12.3.0. No package was installed or upgraded for this integration. RRE's own interpreter remains responsible for the other research suites. The unified gate runs a separate mandatory `visual-evidence` group, records the actual image runtime, test IDs and exits, and fails rather than skipping when the image runtime is missing.

In PowerShell:

```powershell
Set-Location C:\work\rre
$ImagePython = 'C:\work\riftreader2\artifacts\tools\control-python\Scripts\python.exe'
& .\.venv\Scripts\python.exe -B tools/validate-research.py `
  --image-python $ImagePython --output-dir artifacts/research-gate-my-visual-run
```

Use a new output directory every time. `--image-python` overrides the existing sibling RR2 runtime; without it the gate uses that runtime when present, otherwise its own interpreter. It never installs Pillow silently.

## Recipe and manifest

A recipe has integer `schemaVersion: 1`, `kind: rre-visual-evidence`, a bounded `experimentId`, declared `sourceKind: recorded|synthetic`, `expectedVm`, `journal`, `frames`, `actions`, `comparisons`, and optional `references`. Unsupported top-level fields are rejected. `sourceKind` is a declaration, not proof of authenticity.

Each file reference is `{ "path": "relative/path.png" }` before pinning, or `{ "path": "relative/path.png", "sha256": "64 hex characters" }` afterward. Paths are relative to the explicit source root; traversal, alternate streams and linked child paths are rejected. Existing hashes must match; `pin` never silently refreshes a mismatched hash. Original input files are never written.

`expectedVm` has `vmx`, integer VMware `pid`, and integer `startTicks`. Do not guess these from a VM display label. Use retained host connection evidence. The copied source data preserves full integer ticks; no JavaScript numeric conversion is involved.

A frame has `id`, `image` and `capture` references. Captures use the existing RR2 `capture.json`: `captureId`, `capturedAtUtc`, `captureBackend`, image SHA, `savedImage` SHA/byte count and target identity. Target identity includes guest name, game PID/start ticks, executable path/hash, HWND, foreground and client geometry. Two to eight frames are supported; PNG, BMP and JPEG decode through the existing image runtime. Animated images are rejected. Per-image limits: 4096 per dimension, 8,388,608 pixels and 32 MiB encoded bytes.

An action has an `id` and `result` reference to its existing RR2 action envelope. Each comparison has an `id`, `before` and `after` frame IDs, an ordered `actionIds` list, `expectation`, four to eight non-overlapping patch `points`, and optional matcher `settings`.

The journal is an existing RR2 JSONL host log. The checker binds capture IDs/hashes/targets and exact action payloads to a single recorded guest connection, the requested VM epoch and actual command IDs. It requires that the journal's action requests between the two captures match the supplied ordered action list; extra or missing actions invalidate the linkage. Missing connection evidence, reconnection, wrong VM, changed process/window/geometry, unsupported timing, or identical image bytes produces an **inconclusive** result, not an inferred match. A consistent log does not exclude unrecorded human input or prove authentic screenshots.

The observation interval is capped at 60 seconds, with at most 45 seconds from baseline capture to first action and 5 seconds from last action completion to the after capture. Actions must be bracketed by the images. These are bounded replay policies, not a claim of synchronized host/guest clocks. Image timestamps are parsed to Python's microsecond precision; original metadata bytes remain preserved.

An optional reference is `{ "id": "bindings", "image": {"path":"bindings.png"}, "note":"..." }`. It is displayed and included in the review packet as **context-only-unbound**. It cannot satisfy a missing VM/game/action binding. Use this for VMware console context or a settings screenshot, without relabeling it as a qualified client capture.

## Diagnostic predicates

`radial-in`: sampled textures move toward the image center; a possible zoom-out pattern, not a calibrated camera measurement. `radial-out`: the opposite pattern. `stationary`: sampled patches return to or remain at their baseline locations. No automated strafe/turn/world-object interpretation is supplied by this first version.

Defaults: 13x13 patch (radius 6), 2-pixel sample spacing, integer search within +/-12 pixels, variance >=16, mean squared grayscale error <=100, competing distinct-match gap >=5, stationary tolerance 1 pixel and radial-fit RMS residual <=1.5 pixels. The radial fit is diagnostic only. It requires consistent signed motion across separated patches on both sides of the image. Uniform translation does not automatically pass as zoom. Match-quality, repeated-pattern and search-boundary failures are inconclusive. A well-matched stationary scene fails an expected-motion predicate even when delivery succeeded.

Patch selection is explicit and manual. Avoid UI, animated vegetation, characters and occlusion. The checker does not automatically recognize suitable terrain. These thresholds are not universally calibrated; never relax them merely to force a historical trial to agree with its written note. Preserve every changed policy as a different spec/hash.

## Commands

Start from a small recipe with path-only references. Actual examples with all fields are retained under `artifacts/visual-evidence-20261020-01/`; these are private historical data, not generic live configurations.

```powershell
# 1. Pin the exact files; existing output/hash mismatches are errors.
& $ImagePython -B tools/visual-evidence.py pin `
  --recipe artifacts/my-visual-recipe.json `
  --source-root C:\work\riftreader2\artifacts `
  --output artifacts/my-visual-spec.json

# 2. Create a new standalone package. Normal exit 0 means publication succeeded,
#    not that every visual predicate passed. --require-pass gives CI result exits.
& $ImagePython -B tools/visual-evidence.py run `
  --spec artifacts/my-visual-spec.json `
  --source-root C:\work\riftreader2\artifacts `
  --output-dir artifacts/my-visual-package --require-pass

# 3. Verify without regenerating, then replay into a different directory.
& $ImagePython -B tools/visual-evidence.py verify --bundle artifacts/my-visual-package
& $ImagePython -B tools/visual-evidence.py replay `
  --bundle artifacts/my-visual-package --output-dir artifacts/my-visual-replay
```

Exit codes: 0 = valid publication/verification (or all predicates passed with `--require-pass`); 2 = invalid evidence, malformed configuration or I/O error; 3 = at least one failed predicate with `--require-pass`; 4 = inconclusive predicates with no failed predicate under that flag. `replay` recomputes evidence diagnostics and does not reuse a prior pass label.

The package contains unchanged copied source bytes, a portable pinned spec, original source spec, labeled PNG previews, a local script-free side-by-side HTML report, JSON metrics, a vision/human review packet, and a last-written completion receipt. Original frames are never annotated in place. Yellow boxes in derived previews mark baseline sample locations, not tracked object bounds. All file names, sizes and hashes are verified, including referenced images and required previews. File-set verification is not source authenticity or semantic recomputation. A partial write leaves an incomplete directory without a valid receipt; no output is overwritten or deleted.

## How future experiments use this

For a separately authorized visual-control experiment, use the existing RR2 capture path before/after the action and retain the action and host journal. Add a later settled frame when it answers the test question. Create the evidence spec, run the consumer, inspect its original images and diagnostics, and preserve the complete package with the experiment. A new observer does not authorize another movement attempt or a repeat of completed baselines.

For movement/turning, combine images with qualified position/heading observations; camera motion alone is not character movement. For object projection, compare independently observed landmarks and actual scene binding; a matched pixel is not a gameplay entity ID or collision owner. For parser and native ownership questions, continue their existing nonvisual evidence checks.

Before sending `review-packet.json` to another AI, verify that the available reviewer accepts actual image content and retain an image-delivery receipt with the image hashes and returned session/model identity. Passing filenames to a text-only reviewer is not image delivery. This integration creates the portable packet but launches no external reviewer; `visionReview` and `deliveryStatus` remain `not-attempted`. WA-005 independent final-source code QA remains separately blocked.
