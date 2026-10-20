# World-awareness checkpoint — October 20, 2026

Repository: `C:/work/rre`. Contract/roadmap commit: `02fbcc127eec835e98c22943a4e89978a83ea541`. Scope: file-only inspector and bounded original-executable research. This is NOT completed live object recognition, a world map, a camera-calibrated overlay, or working navigation. All implementation and tests in this slice were authored/reviewed by the Manager through Workbridge. Model self-report: GPT-6 Astra Pro; reasoning level unavailable.

## Delivered consumer

`tools/world-inspector.py` reads saved JSON only and writes self-contained HTML/JSON into a new directory. No game process, network, Lua execution, keyboard/mouse or native function invocation path exists. It accepts observed ReaderBridgeExport DirectAPI/ReaderBridge shapes and the exact retained RiftReader2 delivery receipt shape. It groups exact IDs within one input, preserves source roles and conflicting observations, keeps unknown values unknown, and never equates nearby-list absence with complete empty scenery.

The table and raw X/Z diagnostic retain Y separately. The projection module accepts only an explicit hash-bound matrix/viewport sidecar with a named convention; it is tested with synthetic matrices, not calibrated against the current game camera. Frustum membership never implies visibility or walkability. The report does not generate obstacles, terrain, collision bounds, support classifications or routes from unit coordinates.

Actual recorded receipt: `C:/work/riftreader2/artifacts/live-validation/live-fresh-receipt.json`, SHA256 `a7cddc62cd66a14f943e0bc2de82666fcd7de0013c5e6db12780518e726329d5`, captured October 19 at 02:26:11 UTC. Output retains one player ID `u035400012FA2D207` and XYZ `(7308.330078125, 875.6599731445312, 3050.909912109375)`. It remains recorded/player-only/freshness-unverified despite historical bound/fresh flags. Its process `target` is not a selected game entity.

Saved outputs from final code:
- `artifacts/world-inspector-release-20261020-recorded/report.html` and `report.json`; 1 record, 1 ID, 1 position, 0 conflicts. JSON SHA256 `089f4b309dd1802226dd0ca5a13f6ae90eb9a7bfe26ad78412ae299db75a2d5a`.
- `artifacts/world-inspector-release-20261020-demo/report.html` and `report.json`; explicitly SYNTHETIC, 6 input records, 5 distinct IDs, 4 known positions. Self-target merges; same-name units and separate heights stay distinct. JSON SHA256 `13c89bd7c93c20d2f2c37d941813043cd68b41b74a12aab1c1497aea4a9d72cf`.
- Source code SHA256 at validation: `e0208f528d841aa8c0810c7ec86f8982933c0de7dab0e87b305d5d1d6384d79d`. Git checkout line endings can change raw source bytes; each report pins its actual executed checkout.

## Entity-source research — WA-002

Full machine record: `tools/agents/c2m/wa_entity_findings.json`. Read original `ReaderBridgeExport/main.lua`, SHA256 `45b5c820a9001cf2adfa963bfa0c24fe2bc41b476b49af9494c3d5aede8b91fa`. Both it and the saved RR2 receipt were rehashed after the final inspector runs.

Source constants cap nearby rows at 10 and party slots at 5. The DirectAPI nearby reader returns nil for unavailable lists AND zero retained rows, excludes player/target, and has no exhaustive/truncation/distance-sort guarantee. `Inspect.Unit.List` remains explicitly unverified. The alternate ReaderBridge mode sets nearbyUnits=nil without enumerating. Partial coordinates and ID fallback to a unit specifier require explicit handling. Current multi-object enumeration is not established by this source audit.

## Native collision result and backlink research — WA-003

Original executable SHA256 `7c356c9dde9e12fcbff3c08d953b0630b48b1510a0ffb36e4ec164606e7b17bd`; base `0x140000000`; all addresses below are RVAs. Native file was read only. Verification code: `tools/agents/collision/wa_hit_result_verify.py`.

**Observation A — collector identity.** Code at `0xF67254` references VFT `0x2D6A8A8`, installed in the local stack collector. The self-consistent MSVC locator at `0x2D800D8` identifies `.?AVhkpClosestRayHitCollector@@` (type descriptor `0x32DC460`). A nonnull caller-supplied collector can replace this local one, so that caller instance is not automatically assigned the local class.

**Observation B — geometric result conversion.** Direct-call-qualified entry `0x13D3180` computes `start + (end - start) * scalar`; in this caller its scalar comes from collector+0x20. Entries `0x13D2BA0` and `0x13D2BD0` unpack/pack the first three float lanes without a visible axis swap or scaling in these bounded entries. This supports a specific ray-hit interpolation interpretation, not a universal collision ABI, real world-unit calibration or player clearance.

**Observation C — optional hit-associated pointer output.** After a nonnull collector+0x60 hit-associated pointer, `0xF67314..0xF673BB` checks an optional output pointer in RBP; checks a type-like byte at hit+0x28; uses a signed byte at hit+0x20 as an object-relative adjustment; reads an array/count at adjusted+0xB0/+0xB8; searches 16-byte records for key `0xFFFF`; then follows the record value through two +8 dereferences and a -8 adjustment before writing the optional output. This is a concrete object-backlink research lead, NOT a confirmed gameplay entity ID or restart-stable pointer.

**Important limitation:** Several AL=1 exits occur before the optional output is cleared at `0xF67332`. Therefore a successful geometric query does not guarantee a freshly written/nonnull object pointer. No invocation is authorized or supplied by this research.

**Coverage:** The V7 capture accounts for five requested anchors but has only TWO complete PE-unwind regions: `0xF671C0..0xF673E7` (144 rows) and `0x13D44D0..0x13D44F7` (11 rows). The other three anchors have no PE-unwind entries. Supplemental original-file reads are bounded to 96 bytes per direct-call-qualified entry and retain 24 instructions through the first return; these are not promoted to full function-boundary or exhaustive CFG evidence. All 825 existing parser warnings remain recorded. V7 recording completion must not be described as five fully recovered functions.

V7 original artifact: `artifacts/wa-hit-result-20261020-01.json`, SHA256 `388ce76ffb959dc5da0f9b4f938edaf1502baf58e0e951b9238d6dbc875f877d`. Manifest: `artifacts/wa-hit-result-20261020-01-manifest.json`, SHA256 `0b77c1dd0b24df35507ba888ab30857a6b163a588318e3d6d7361506ad1a733b`. Final source verifier output: `artifacts/wa-hit-result-qualified-20261020-01.json`, SHA256 `0b5a00097e3fc2bbcd8b33d62edc5cad46d9f4c5ae14ae26bcc84882c3c822ba`.

## Validation and agent outcomes

Final job `rre-wa-20261020-final-validation-reports-02` passed exit 0: **71 validation tests** (50 new inspector tests plus 21 existing tests in this discovery pattern), **9 new exact-build collision verifier tests**, both report CLI runs, and the roadmap validator. These are **80 distinct tests**, not 80 live-game trials. The tests under this pattern do not represent every test in other repositories or every older RRE test filename pattern.

Source/report integrity job `rre-wa-20261020-source-report-integrity-01` passed exit 0 and checked input hashes, exact retained player ID/XYZ, record counts and output source labels. Native byte verifier `rre-wa-20261020-hit-native-proof-01` passed exit 0. Initial negative-regression job `rre-wa-20261020-negative-regressions-red-01` intentionally exposed exponent-overflow acceptance, Unicode validation occurring after output directory creation, and a non-object schema error; all three were fixed and retained in passing tests. Additional source audit corrected the draft's unobserved JSHUD mode to actual ReaderBridge mode.

Independent review was attempted through installed OpenCode 1.18.10 / Cohere north-mini-code:free:
- `rre-wa-20261020-entity-review-agent-01`: process exit 0 but external-directory read rejected; NO review accepted. No permission changes.
- `rre-wa-20261020-hit-review-agent-01`: independent excerpt review completed exit 0. Accepted cautions: backlink remains unqualified and early successful paths may leave output untouched. Rejected reviewer errors: it incorrectly said `0x13D44D0` lacked unwind metadata (it is the second captured region); it misplaced the output clear (actual `0xF67332`, before the count/record search); and it oversimplified the final pointer dereferences. The Manager checked native bytes rather than repeating these errors. This was not an independent PE verification.
- `rre-wa-20261020-inspector-review-agent-01`: failed at command parsing, exit 1, no review.
- `rre-wa-20261020-inspector-review-agent-02`: bounded attached-source review timed out after tool/command missteps; no final code-review findings. The immutable reviewed input was preserved as `artifacts/wa-review-source-20261020.txt` (SHA256 `7f5950e5f291d55857ffa792db97b65101b3b0b4732db05941af41f3c9627daa`). No independent full-code QA completion is claimed. WA-005 therefore remains blocked/pending that review despite passing Manager regression tests.

## Run and inspect

In PowerShell on Joey's PC, existing generated reports can be opened without game interaction:

```powershell
Start-Process 'C:\work\rre\artifacts\world-inspector-release-20261020-recorded\report.html'
Start-Process 'C:\work\rre\artifacts\world-inspector-release-20261020-demo\report.html'
```

To generate a new demo report, choose an output directory that does not already exist:

```powershell
Set-Location C:\work\rre
& .\.venv\Scripts\python.exe -B tools/world-inspector.py --input docs/world-awareness-demo.json --input-format readerbridge --output-dir artifacts/world-inspector-my-demo
```

## Exact next research gate

After independent consumer review, qualify real simultaneous non-self entity observations and scene identity. For native ownership, prioritize the producer/writer of the `0xFFFF` keyed record and the class behind the final backlink, then correlate against an independently observed unit ID. Do not return to broad +0x160 displacement scanning as a substitute. Camera calibration still needs independent landmarks and camera-only changes; current shape/owner, visibility, clearance, support and reachability are unqualified. WA-006 remains blocked, M3-001 stays open, and M4/M5/M6 gates are unchanged. No game input, native function call, game-process attachment or external-source modification occurred in this slice.
