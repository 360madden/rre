# Inspector QA resumption — October 20, 2026

## Scope and ownership

Continue WA-005A/B/C and WA-005 from main `a442cd2174f5a4baae9b898fbeb4e1764fb4cfaf`. The current ChatGPT session is the sole Manager and source writer. Model self-report: GPT-6 Astra Pro. Reasoning level: unavailable (machine records leave it blank).

Fresh preflight job `rre-wa3-20261020-preflight-01` exited 0: all six research worktrees are clean; main retains only the two historical raw-probe files. Workbridge 0.6.1 initially reported zero managed running jobs. Other Codex processes exist on the machine; they are not counted as available RRE workers or stopped. No OpenCode process was present in the process inventory. The installed OpenCode version is 1.18.10. A model catalog entry does not prove successful inference.

The preserved input source is `tools/world-inspector.py`, SHA256 `7f0473230020e9103a0956d2e974cca754cf13f4cc76cd0f30b43cbb5a287acc`. No new native capture, live game observation/input, process attachment, binary invocation, external-repository edit, dependency installation, paid-model selection, publishing, or Workbridge runtime change is part of this slice. In particular, the blocked WA-007 native capture will not be retried through another route. A new game-build hash is not claimed for this file-only consumer review.

## Ordered work

1. Prepare bounded, line-numbered source packets for the three existing review lanes. Pin exact source and packet hashes and archive copies under main's ignored artifacts. The Manager may create immutable review packets under each lane's ignored `artifacts/wa3-packets-20261020/`; reviewers have no writable source ownership.
2. Request three independent no-tool reviews with the existing runner and free models already listed by the installed runtime. Parsing/identity uses the C2M lane, numerical/projection semantics uses Follow, and HTML/publication/CLI uses Validation. Each packet carries complete functions for its scope. Include imports/constants and the applicable contract. The combined scopes cover every top-level function. This differs from the prior unsuccessful north-mini-code attempts: different model selection and refreshed complete, bounded source packets. Do not repeat identical failed launches.
3. Independently inspect the code and test concrete counterexamples. Distinguish actual source defects from reviewer errors. Preserve original model output even when invalid. Process exit, structured response, substantive review and Manager acceptance are separate outcomes.
4. For any confirmed defects, first retain a failing regression, apply a narrow fix, run targeted tests, and obtain a bounded independent delta review of the changed functions. Do not modify the pinned inspector while its initial reviewers run.
5. Run the full existing `tools/validate-research.py` gate on the final source, regenerate recorded and synthetic reports into fresh directories, verify publication receipts, validate the roadmap, review diffs, and make scoped local commits. Preserve baseline files and all prior outputs.
6. Update the task register with real jobs, independent session IDs, source hashes, tests, acceptance dispositions and exact remaining gates. Do not declare WA-005 complete without acceptable full coverage and resolution of final-source changes. WA-006 and the native navigation milestones do not complete from this QA slice.

## Stop and recovery rules

At most three reviewer processes run together; keep capacity for supervision/tests. Each reviewer has a finite deadline. On failure, inspect its actual result and do not relabel it successful or loop on an unchanged configuration. Only the Manager edits shared code/board. Use expected hashes for edits and expected HEAD plus explicit file lists for commits. Keep worker source trees clean. Do not interrupt unrelated Codex sessions.

## Execution results

### Implemented and locally committed

Implementation commit: `c651fb99619c345bdf910e2abd81f6b606de3bb1`. Inspector version: **1.1.1**. Executed source SHA256: `77e487b942e58731a961ca9af79c8badf46e8843101ce7df0ddfcd8953146e02`. The Manager authored the two fixes and nine new regression tests; no independent worker implementation or completed independent QA is claimed.

**QA-P01 — publication size mismatch.** A valid synthetic input of 2,443,627 bytes and 512 records generated a 14,881,038-byte JSON report, a 3,165,553-byte HTML report and a completion receipt. The inspector returned success, but its own verifier rejected the JSON because verification is bounded to 8,388,608 bytes per file. Version 1.1.1 measures actual encoded UTF-8 report sizes before creating the output directory and rejects expansion beyond that same cap. It does not increase memory/file limits or publish an unusable receipt. Exactly-at-limit output remains accepted; 512 ordinary short-ID records remain supported. The contract now documents the output cap separately from input validity.

**QA-U01 — invalid Unicode in ignored fields.** The JSON decoder accepted escaped lone surrogates in ignored legacy fields and camera extras, contrary to the scalar-validity contract. The loader now checks all decoded string keys and values, including nested arrays. Iterator-based traversal adds storage proportional to nesting rather than array width. Valid supplementary Unicode characters, ignored newline/tab strings and ordinary unknown legacy fields remain supported. Both fixes reject before creating output and preserve inputs.

Original positive reproductions are retained under `artifacts/wa3-boundary-repro-20261020/`, including the old invalid publications and `reproduction.json`. They were not overwritten after the fix.

### Verified tests and reports

- `rre-wa3-20261020-boundaries-red-01`: **exit 1**, nine test methods with seven failure records (including two subtest failures in one method), confirming the old behavior.
- `rre-wa3-20261020-inspector-green-01`: **exit 0**, all **66 inspector tests** passed, including the nine new regressions.
- `rre-wa3-20261020-unified-gate-01`: **exit 0**, **377 tests** passed. Groups: Validation 153, C2M 30, Follow 73, Collision 47, Pathfinding 57, review adapter 17. Roadmap consistency also passed. Tools-source hashes stayed unchanged; the durable gate retains each group, actual IDs/counts, stdout/stderr and exit codes in `artifacts/research-gate-wa3-20261020-01/validation.json`.
- `rre-wa3-20261020-release-verification-01`: **exit 0**. Both fresh 1.1.1 reports passed receipt verification, both original bug inputs now fail before directory creation, recorded input hashes stayed unchanged, and all six prior 1.1 report/receipt files remained byte-identical. Saved result: `artifacts/wa3-release-verification-20261020-01.json`.

The total increased from the historical 357-test gate by **nine newly added tests and eleven previously integrated Pathfinding tests**. It is not twenty newly authored tests and is not a live-game test count.

New outputs are `artifacts/world-inspector-v111-20261020-recorded/` and `artifacts/world-inspector-v111-20261020-demo/`. The recorded report still contains only the historical player (one ID/position), and the demo still contains six synthetic records, five IDs and four positions. Both remain explicitly non-live. The source receipt hash is still `a7cddc62cd66a14f943e0bc2de82666fcd7de0013c5e6db12780518e726329d5`.

### Independent review outcomes — not accepted

Three refreshed, hash-bound packets collectively contained every top-level inspector function. Main's immutable packet archive is `artifacts/wa3-packets-20261020/manifest.json`; matching ignored worktree copies are preserved. No reviewer changed source.

| Task / Workbridge job | Independent session | Actual outcome |
| --- | --- | --- |
| WA-005A / `rre-wa3-20261020-review-A-01` | `ses_ea6057b66ffeK01RmIP1R0kqgW` | Requested MiniMax M3.1 Flash free; 180-second deadline, child exit 1, adapter exit 2; no completed assessment |
| WA-005B / `rre-wa3-20261020-review-B-01` | `ses_ea60565b7ffe4gI70W47dSJyEj` | Requested Nemotron 3 Ultra free; child exit 0, adapter exit 2; one tool event disqualified the response and its four alleged defects were checked rather than adopted |
| WA-005C / `rre-wa3-20261020-review-C-01` | `ses_ea605404fffem5j6LR7zM02jll` | Requested MiniMax M3.1 Flash free; 180-second deadline, child exit 1, adapter exit 2; no completed assessment |

B1 was rejected because the public camera-validation path already rejects a 12-element matrix before calling the internal helper. B2 describes retained whitespace in display labels, not accepted whitespace-only entity IDs; the latter are rejected. B3's overflowing-ratio example is outside the frustum and returns before division; replay also confirmed a valid tiny-W case, and 1e208 is finite. B4 is a numerical precision limitation, not the claimed pixel error: the replay produced the exact expected coordinate, and spacing at 1e12 is about 0.000122 pixels. The actual replay values and review-result hashes are retained in the release-verification JSON. None of these claims warranted a source change.

The installed Codex CLI reports 0.163.0 and a ChatGPT login. The initial PowerShell capability wrapper exited 1 because normal auth-status stderr was treated as a PowerShell error; the direct CLI help command exited 0. These observations do not establish model availability or quota. A proposed final-source reviewer-launcher file was then blocked by the tool before creation. `change_status` returned `UNKNOWN_CHANGE` for operation `rre-wa3-20261020-codex-review-driver`. No Codex review was launched, and the blocked action was not retried through another route. No new driver is claimed as an implemented tool.

### Remaining gates and next resumption

**WA-005A/B/C and WA-005 remain blocked on acceptable independent final-source review.** Local test success and the Manager's source review do not satisfy that gate. Do not repeat today's failed free-model launches unchanged or retry the blocked Codex launcher by another route. No available AI-worker capacity is inferred from Workbridge's six command slots or from unrelated Codex processes.

WA-006 still lacks actual bound multi-object/physics/camera observations. WA-007's separately blocked native capture was not retried. M3-001's type-7 registration/producer and native player routing remain unresolved; M4/M5/M6 boundaries are unchanged. Permitted saved-evidence work remains separate from blocked capture/review actions. Do not rerun completed movement baselines or declare live world recognition from these report fixes.

Next session: refresh main/worktree/job state, use commit `c651fb9` plus the final documentation checkpoint, preserve the two baseline probe files and all evidence, and choose a genuinely unblocked task from the authoritative board. No work is promised after this session ends.
