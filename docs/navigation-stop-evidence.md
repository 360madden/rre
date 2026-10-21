# NAV-003 — Recorded request and physical-stop evidence evaluator

Date: October 21, 2026. Manager implementation and review: GPT-6 Astra Pro; reasoning-level metadata unavailable. Scope: RRE files and disposable offline tests only. No game input, capture, process access, worker launch, environment change or RR2 source edit.

## Delivered behavior

`tools/navigation_stop_evidence.py` is a standard-library Python module/CLI for the specific missing interpretation step identified by [NAV-001](navigation-capability-audit.md) and [NAV-002](navigation-first-behavior-test.md). It is not a recorder, controller, queue, pathfinder or automatic T0 acceptance mechanism. Existing M4A source/fixtures and the screenshot pipeline remain unchanged.

The evaluator checks a normalized trace containing one reviewed ground-request record, one cancellation record and player observations. It validates the entire retained observation stream before making a positive predicate. Unlike the synthetic intention state machine, it continues checking after cancellation. Resumed motion, cumulative drift, vertical motion and an out-and-back excursion cannot be hidden by a stationary final endpoint. It does not evaluate distance-to-goal, so an initially outward detour is not automatically classified as routing failure.

The result separates:

- `movement-then-stationary`: at least two pre-cancel samples displaced from a stable baseline, followed by a sufficiently long sampled stationary interval after the declared settling allowance;
- `post-cancel-motion`: the maximum pairwise distance among post-settling observations exceeds the explicitly supplied tolerance;
- `no-pre-cancel-movement-observed`: adequate coverage but insufficient pre-cancel displacement; this is not a successful cancellation;
- `inconclusive`, `aborted`, or `invalid`: insufficient or contradictory evidence, identity/clock change, or malformed input respectively.

**Every result retains `t0Accepted=false`, `nativeRoutingVerified=false`, `provenanceAuthenticated=false`, and `imageBytesVerified=false`.** A positive telemetry predicate cannot establish that cancellation caused stopping or that arrival/contact did not cause it. It cannot exclude movement between samples. Calling a source `recorded-normalized` does not authenticate it. A downstream reviewer must check the original images, raw records, actual bindings, context, clock mapping, and live authority. These qualifications are not silently waived.

## Input contract, version 1

Top-level members are exactly `schemaVersion`, `kind`, `binding`, `policy`, `frame`, `actions`, `samples`, and `observationEndMs`. Unknown/duplicate properties, unsupported versions, booleans masquerading as numbers, invalid scalars, nonfinite/out-of-range numbers and oversized inputs are rejected. Input is limited to 2 MiB and 2,048 samples. These are implementation budgets, not measured RIFT performance limits.

`kind` is `synthetic-fixture` or `recorded-normalized`. The latter requires a separate, reviewed normalization step; the program does not silently convert a historical RR2 delivery receipt into a current experiment.

Every frame, action and sample repeats the same exact binding: `vm`, `epoch`, `buildSha256`, `scene`, `player`, `clock`, `window`, and `sourceEpoch`. The build hash is lowercase SHA-256. Labels are caller-supplied bounded strings, not runtime attestations. `sourceEpoch` identifies the reader/producer session, while `epoch` identifies the game process lifetime. All timestamps are integer milliseconds in the stated common monotonic domain. An adapter may use a conservatively verified mapping; it may not merely relabel host receipt times as guest times.

`frame` records `captureId`, `imageSha256`, `startMs`, `endMs`, `width`, `height`, and `point=[clientX,clientY]`, plus binding. The activation must match the capture ID, client point and dimensions exactly. A mismatch or stale frame prevents a positive result. This verifies metadata consistency only; actual pixel delivery and click placement remain separate evidence.

`actions` contains exactly one `activate` then one `cancel`. Each has binding, `startMs`, `endMs`, `delivery` (`confirmed`, `unknown`, or `failed`), and boolean `released`. Activation also has the frame's capture ID, point, width and height. One-to-250 ms recorded action intervals are accepted as this evaluator's bounded scope. No actual gesture/key is guessed or sent. Unknown delivery, failed release, extra activation, or missing cancel cannot pass.

Each sample has binding, integer `seq`, `startMs`, `endMs`, `receivedMs`, `status` (`ok`, `unavailable`, or `invalid`), and `xyz` as three finite coordinate values. Unavailable samples may have null XYZ and never supply position evidence. Source sequence must advance; acquisition intervals must not overlap or reverse. All retained samples, including those after apparent stopping, are checked. Raw coordinate units are not labelled metres.

`policy` requires all values explicitly: `positionTolerance`, `minimumMovement`, `maxAgeMs`, `maxGapMs`, `baselineSpanMs`, `postSpanMs`, `settleMs`, `budgetMs`, `frozenAtMs`. There are no implicit noise/timing defaults. Positive movement threshold must exceed twice the position tolerance. The current bounds retain at most 1,000 ms source age/gap, baseline span at least 1,500 ms, post-cancel span at least 2,000 ms, and at most a 10-second post-activation observation budget. Settling allowance is explicitly 0–2,000 ms; the existing draft uses 1,000 ms. These are declared experimental policies, not game measurements.

At least three baseline and three post-cancel samples are required, with time spans measured conservatively from the first acquisition END to the last START. At least two pre-cancel observations must show displacement. Baseline samples must have been received by the policy-freeze time, before input. The baseline's maximum pairwise spread must fit the tolerance. The evaluator cannot prove that the supplied tolerance itself was calibrated honestly; calibration remains a reviewed prerequisite.

Age uses the earliest possible measurement/capture time. Maximum inter-sample gap uses the next acquisition END minus the previous START. A long scan therefore cannot conceal stale observations by reporting only its completion time. Observation-end coverage is checked, so a short favorable interval cannot hide an unobserved tail. All post-settling positions are compared pairwise in 3D, bounded by the sample limit.

## Usage on Joey's PC

Run in PowerShell at `C:\work\rre`, using the existing RRE interpreter. The saved positive sample below is explicitly synthetic:

```powershell
Set-Location C:\work\rre
& .\.venv\Scripts\python.exe -B tools/navigation_stop_evidence.py `
  --input artifacts/nav003-stop-evidence-20261021-01/stopped.input.json `
  --require-stop
```

Add `--output-dir artifacts/my-unique-stop-review` only for a new directory. The parent must already exist. The CLI refuses paths outside RRE artifacts and never overwrites an output directory. `report.json` is followed by a last-written `complete.json` carrying its byte count and SHA-256. Missing completion marker means incomplete publication. The marker proves publication consistency, not a successful game trial. The report records the exact input and tool hashes.

Without `--require-stop`, exit 0 means a structurally valid analysis completed, including a negative or inconclusive result. With it, exit 4 means the conditional telemetry-stop predicate did not pass. Exit 2 indicates malformed input, unsupported shape, or IO/publication failure. Never infer navigation success from process exit alone.

The deterministic fixture constructor is retained in `tools/tests_navigation/test_navigation_stop_evidence.py`. Original M4A fixtures are not repurposed to pretend their synthetic goal IDs or terminal cancelled state are live evidence.

## Validation and observed limitations

The initial red run failed because the evaluator did not yet exist. The first implementation passed 59 tests. A subsequent adversarial review added four genuine failing timing cases: baseline received after policy freeze, aged frames hidden by a late capture end, delayed observations hidden by scan completion, and wide scan intervals hiding sample gaps. The fixes use conservative acquisition bounds. The positive synthetic fixture was adjusted from a 1,001 ms worst-case gap to exactly 1,000 ms by moving one sample one millisecond earlier; no policy threshold was weakened. The failure runs remain in Workbridge history.

Final focused job `rre-nav003-focused-20261021-03` passed **67 tests**, exit 0. The tests include identity/window/reader/clock mismatch, duplicate sequences, stale/unavailable data, insufficient coverage, baseline drift, resumed/out-and-back/vertical motion, point/capture/geometry mismatch, input bounds, malformed JSON, no-overwrite publication, and failed publication without a completion marker. They are Manager-authored tests, not independent reviewer acceptance.

CLI/publication job `rre-nav003-cli-acceptance-20261021-01` passed exit 0, checking child outcomes separately: synthetic stop returned 0, resumed motion and wrong point returned 4, clock mismatch returned 4, and the original historical player-only receipt returned 2 (invalid for this schema). All four published receipts matched actual report bytes. The historical receipt retained SHA-256 `a7cddc62cd66a14f943e0bc2de82666fcd7de0013c5e6db12780518e726329d5`. A single 2,048-sample synthetic evaluation took about 0.255 seconds locally; that is not a latency guarantee.

Full gate `rre-nav003-full-gate-20261021-01` passed exit 0: **502 tests**, including 67 navigation-evidence tests and all 435 prior tests, roadmap consistency passed, no duplicate Python test IDs and tools-source hashes unchanged during the run. This is an offline gate, not live-game acceptance. Evidence root: `artifacts/nav003-stop-evidence-20261021-01/`; full inventory, actual group exits and retained logs are in `full-gate/validation.json`.

## Next integration boundary

This closes a preparatory analysis implementation gap, not NAV-B01 through NAV-B04 or full M4/M5. The existing RR2 workflow is independently evolving control admission/watchdog code and remains the control/capture owner. Do not overwrite its uncommitted work or infer it is deployed.

The next useful deliverable is a reviewed producer/normalizer mapping one actual request and the original time/identity-bound observations into this contract, together with the existing screenshot-evidence package. Missing inputs must remain missing; do not generate samples or cast old receipts as fresh. Then the existing owner can resolve the reviewed-point delivery and current binding requirements for the separately authorized T0 experiment. No new engine scan, world model, queue or capture framework is required by this evaluator.
