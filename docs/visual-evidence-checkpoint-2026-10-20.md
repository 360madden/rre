# Screenshot evidence integration checkpoint — 2026-10-20

Implementation commit: `843c2f4b35dc166c4303a75a3a11564141819757`. Task: **VE-001**. Manager/implementation model: GPT-6 Astra Pro; reasoning level unavailable, blank in machine records. This is a completed **offline screenshot-evidence integration slice**, not a live-capture deployment or independent AI review.

## Delivered

`tools/visual-evidence.py` provides `pin`, `run`, `verify`, and `replay`. It reuses existing RR2 capture/action/journal files and the installed Python 3.14.6 / Pillow 12.3.0 interpreter. No new dependency or runtime was installed. Modules separate source/identity validation, bounded pixel matching and report publication. The [contract and usage](visual-evidence.md) explains the schema, limits, commands and interpretation. The [integration roadmap](VISUAL_EVIDENCE_ROADMAP.md) preserves scope and resumption.

Packages retain original image and metadata bytes, portable hash-pinned references, annotated PNG previews, side-by-side local HTML, JSON results, a review packet and a last-written complete receipt. Optional keybindings/VMware screenshots are context-only unless independently bound. The receipt validates the full referenced file set, not merely files still named in a truncated receipt.

Recorded VM identity is checked using actual VMX path, VMware process/start identity and host connection records. Game process/start identity, executable hash, HWND, client geometry and capture backend must agree. Capture IDs/image hashes and exact action result payloads are matched to command journal entries. Extra/missing actions, reconnection, wrong VM, timing gaps and unbound images cannot produce an accepted diagnostic pass. Successful input delivery remains a separate field from the visual result.

The implemented predicates are radial-in, radial-out and stationary scene-patch patterns. Weak/repeated textures, poor matches, search-boundary hits and non-radial motion remain inconclusive. A successful radial fit is not numerical camera calibration, character movement, gameplay object identity, physics ownership or navigation proof. Manually selected patches still require scene-appropriateness review.

## Actual validation

`rre-ve-20261020-unified-gate-01` completed **exit 0**, **435 tests** with unchanged tool-source hashes and no duplicate Python test IDs. The actual groups were Validation 153, C2M 30, Follow 73, Collision 47, Pathfinding 57, **Visual evidence 58**, and review adapter 17. Roadmap consistency also passed. The 58 new visual tests are included in 435, not in addition. Durable results, complete test IDs, runtime identity and stdout/stderr are under `artifacts/research-gate-visual-20261020-01/validation.json`.

Negative runs were preserved rather than relabeled:

- `rre-ve-20261020-tests-01`: exit 1, 49 tests, one failure. Repeated textures were already rejected but the reason selected search-boundary instead of ambiguity; classification priority was corrected.
- `rre-ve-20261020-tests-red-closure-02`: exit 1, 58 tests, two failures. Removing a referenced image or preview and also removing it from the receipt could incorrectly pass file-set verification. The verifier now checks transitive manifest references and required preview names. Both regressions pass in the final gate.

`rre-ve-20261020-release-acceptance-01` completed **exit 0**, inspecting actual child exits. Final zoom generation with `--require-pass` exited 0; the old-wheel baseline exited **4, inconclusive**, as expected. Both package-verification calls and a standalone portable replay exited 0. Replay results were identical. All 15 referenced original source files remained byte-identical. Every image referenced by the generated HTML was decoded and checked at 1211x686. This checks image links/decodability, not a human browser-layout review. Exact commands, exits, source hashes and report hashes: `artifacts/visual-evidence-release-20261020/acceptance.json`.

The precommit check `rre-ve-20261020-precommit-check-01` exited 0 and rechecked all 64 tool-source hashes from the completed gate, both preserved baseline probe hashes, Git HEAD and whitespace checks. Git emitted existing LF/CRLF conversion advisories, not validation failures.

## Results on existing game captures

**Final reversible zoom:** recorded linkage to the same VM/game session and the exact action IDs passed. The zoom-out diagnostic measured four patch offsets `(4,0)`, `(-4,0)`, `(5,-6)`, `(-5,-6)` with radial-fit residual approximately **0.992 pixels**, under the explicit 1.5-pixel diagnostic threshold. After the opposite action, all four patches matched their baseline pixel positions. Both predicates passed. Actual command IDs: `43f904693de545eeaf4f3ba990945806` and `8a55b1ef18bf4581bf91a542c34f2843`.

**Older wheel baseline:** recorded linkage passed, but the image diagnosis is **inconclusive**, not a confirmed no-motion result. Three patches produced qualified displacements `(+3,0)`, `(-5,+6)`, `(+5,+6)`; the fourth candidate was `(-4,0)` with mean squared error approximately **144.286**, exceeding the fixed limit of 100. This is a discrepancy with the older written no-visible-zoom note, not proof that the old path worked. Do not tune the threshold to force agreement with either narrative. The saved pair and command `dcd42a68c5104226b0530efd8b4b0c98` need direct visual/context review before revising that historical conclusion. The original RR2 documentation and images were not changed.

Report directories:

- `artifacts/visual-evidence-release-20261020/recorded-final-reversible-zoom/`
- `artifacts/visual-evidence-release-20261020/recorded-old-wheel-baseline/`
- `artifacts/visual-evidence-release-20261020/portable-replay/`

Each contains `report.html`, `report.json`, copied originals, derived previews and `complete.json`. The initial packages under `artifacts/visual-evidence-20261020-01/` are also preserved.

## Boundaries and remaining work

No live screenshots, new game input, process attachment, native acquisition, VM/settings changes, external-repository edits, dependency installation or Workbridge deployment occurred. There were no new independent AI reviewers or worker agents; the source writer was the Manager. Existing six worker worktrees were clean at preflight and remain reserved against conflicting writers.

`review-packet.json` is ready for a human or image-capable review transport, but **no external vision reviewer was invoked**. Passing an image filename as text is still not image delivery. Independent code review and WA-005 remain uncompleted. WA-006 actual multi-object/physics/camera evidence and the M3/M4/M5/M6 gates are not relaxed.

Next useful work is to inspect the flagged historical baseline pair and then connect this consumer to future separately authorized capture sequences. Automatic live capture orchestration and automatic strafe/turn/object interpretation are not part of this accepted slice. Do not rerun already completed basic controls or retry the previously blocked Codex/native-capture actions through another route.
