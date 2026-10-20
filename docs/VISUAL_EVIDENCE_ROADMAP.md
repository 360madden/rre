# Screenshot evidence integration

Authorized by Joey on 2026-10-20: integrate in-game/VMware screenshots into validation. This is a reusable, saved-evidence implementation slice, not permission for new movement or native acquisition. Existing capture paths remain in RiftReader2; this slice does not modify that repository, Workbridge, VM settings or game bindings.

## Ownership and checkpoint

Manager/source writer: current ChatGPT session, GPT-6 Astra Pro; reasoning level unavailable (blank in machine records). Starting RRE HEAD: `a91bbb72fce81378117d036773babeb54c1e09f0`. Preflight `rre-ve-20261020-preflight-01` passed: all six worktrees and RR2 clean; main has only the two preserved historical probe files. Workbridge initially reported zero jobs. No independent AI worker is launched; prior blocked review/capture routes are not retried.

Task **VE-001**, Manager-owned paths: `tools/visual-evidence.py`, `tools/visual_evidence/`, `tools/tests_visual/`, `tools/validate-research.py`, `docs/VISUAL_EVIDENCE_ROADMAP.md`, `docs/visual-evidence.md`, and Manager roadmap/task-board/checkpoint files. Saved sources outside RRE are read-only. Test fixtures and published image bundles use fresh RRE artifact directories.

## Ordered implementation

1. Inspect actual saved image/capture/action envelopes, VM provenance and available image runtime. Reuse Pillow and RR2 capture outputs; do not introduce a new recorder or install dependencies. Record exact Python/Pillow versions used.
2. Implement a versioned screenshot-evidence bundle: original image/metadata hashes; capture IDs, timestamps, dimensions and backend; recorded VM and guest process/window identity; pinned action results. Verify same-session/frame/action association before accepting a visual result. Keep source provenance separate from current freshness.
3. Implement a bounded image-patch checker and human-readable report. Reject ambiguous, textureless, out-of-bounds and incompatible inputs. Distinguish diagnostic pass/fail/inconclusive from input-delivery success. A screenshot does not prove player displacement, object identity, collision ownership, visibility or native pathfinding. Thresholds are explicit diagnostic settings, not universally calibrated game semantics.
4. Replay existing old-wheel and reversible-zoom captures without new game input. Retain original frames, render derived PNG previews in a portable local report, and write a hash-bound completion receipt last. Never overwrite outputs. Provide reusable manifest/CLI entry points for later captured screenshots.
5. Add synthetic positive and negative tests, a separate image-runtime group in the unified RRE gate, saved-source integrity checks, CLI/report replay and a durable resumption checkpoint. Scope new tests separately from existing suites. Preserve current WA-005 independent-code-review blockers; machine image comparison is not independent source-code QA.

## Completion criteria

A working local CLI consumes existing screenshots and associated records, produces viewable images plus diagnostic results, verifies its complete bundle, handles missing/corrupt/mismatched/ambiguous evidence without false passes, and runs through the existing research validation gate. Actual saved-data outcomes and any provenance gaps must be reported honestly. New live captures, unattended recording, game input, vision-provider image delivery and numerical camera calibration are separate follow-up qualifications, not implied by this slice.

## Completed offline slice

Implementation commit `843c2f4b35dc166c4303a75a3a11564141819757`. The full gate passed **435 tests**, including **58 new visual-evidence tests**, with unchanged source hashes. Saved reversible-zoom predicates passed, a self-contained replay returned identical results, and all 15 original source files remained unchanged. The older wheel pair is **inconclusive** under the fixed match-quality policy; its displacement candidates do not corroborate a blanket no-motion claim, and the discrepancy is retained rather than hidden. Final package/CLI verification completed with the expected exit codes. See [the acceptance checkpoint](visual-evidence-checkpoint-2026-10-20.md) and [usage](visual-evidence.md).

This accepts the reusable offline consumer and workflow/test integration only. Automatic live capture orchestration, strafe/turn/object interpretation and an external vision-review transport remain unimplemented. WA-005 independent code QA is not satisfied by the pixel checker.

## Runtime discovery

RRE's virtual environment and global Python do not contain Pillow; the example `artifacts/native-vm-control/venv` directory is absent. Actual existing image runtime is `C:/work/riftreader2/artifacts/tools/control-python/Scripts/python.exe`, Python 3.14.6, Pillow 12.3.0. Verified by `rre-ve-20261020-pillow-and-identity-01`. Reuse it read-only; no installation or environment changes.
