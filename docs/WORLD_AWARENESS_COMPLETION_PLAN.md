# World-awareness completion plan — October 20, 2026

Goal: finish the existing file-only inspector acceptance, then advance the collision-hit-to-object identity chain. The full objective remains actual small-scene object/physics/camera qualification (WA-006); offline deliverables do not substitute for that evidence. This plan supplements, not replaces, WORLD_AWARENESS_ROADMAP.md and the main task board.

## Current execution checkpoint

**Latest follow-up:** Inspector 1.1.1, commit `c651fb9`, fixes output-size expansion and invalid Unicode in ignored fields. Nine new regression tests, 66 inspector tests and the 377-test unified gate passed; both new reports verified and old reports stayed unchanged. Independent QA is still blocked: A/C timed out, B attempted tools and returned rejected claims, and the proposed Codex launcher was tool-blocked before creation. Do not repeat these unchanged failed attempts or retry the blocked launcher through another route. See [the exact resumption checkpoint](inspector-qa-resumption-2026-10-20.md) and the task board. No native capture or game action was added.

**Earlier tooling checkpoint:**

Joey clarified that tooling gaps across the entire RRE workflow must be identified and resolved. The five TG fixes in [the tooling register](TOOLING_GAP_REGISTER.md) are implemented and the unified gate passed 357 tests (144 validation, 30 C2M, 73 follow, 47 collision, 46 pathfinding, 17 adapter) with unchanged source hashes. Both new inspector 1.1 reports passed publication verification. The 357 count includes existing suites selected more completely, not 357 newly written tests.

R0 preflight and the local tooling/acceptance work completed. Independent review C produced a structured response; its incorrect claims were checked and rejected. A/B responses remain inadequate, and C has no independent delta review of the final publication-schema guard, so overall independent QA is not claimed complete. WA-007 retained seven native regions/469 rows and a stronger property-to-lookup link before the next capture was tool-blocked; it was not retried. Real-scene WA-006 is still unqualified. All eleven review packets were archived byte-identically under `artifacts/wa2-review-packets-20261020/`; the six worker worktrees are clean.

See [the detailed checkpoint](tooling-and-world-awareness-checkpoint-2026-10-20.md) and current task board for tests, review dispositions, evidence and commits. Do not repeat unchanged unsuccessful model/attachment workflows or silently weaken the full-world qualification gate.

## Execution order and exit criteria

1. **R0 / fresh preflight.** Inspect main and all six worktrees, command jobs, existing source hashes and original game build. Preserve unrelated changes. Reuse the accepted inspector rather than rebuilding it.
2. **WA-005A/B/C / independent review.** Three narrow read-only reviews jointly cover the complete inspector: parsing and identity (C2M lane), numerical/projection/report semantics (Follow lane), presentation/file IO/CLI and cross-module integration (Validation lane). Supply pinned source and contract directly in bounded packets. Reviews must use supplied evidence without tool calls, file writes, subprocesses, live-game access, or nested workers. File-mode initially denied all tools; the later inline built-in-plan path used per-process write/command restrictions, and any observed review tool event disqualified the response. Each must return findings, exact locations, concrete counterexamples and limitations. Record actual model/session/job IDs. A process exit alone is not review completion.
3. **WA-005 / reproduce and resolve.** Manager checks every reported issue against current source, records accepted/rejected findings, writes failing regressions for actual bugs, implements only necessary fixes, reruns the entire relevant inspector/validation/collision suite, and obtains a bounded final delta review. Reviewer output is untrusted until checked. Preserve old reports; generate fresh outputs.
4. **WA-007 / collision backlink producer.** In parallel with review, use original PE and the existing V7 capture tools to locate the writer/caller for the 0xFFFF-keyed record and trace pointer ownership. Prefer verified call boundaries/RTTI over offset coincidence. Maximum one targeted byte-prefilter pass with explicit bounds and at most twelve new fully decoded native regions in this slice; no unchanged full imports or broad repeated displacement scans. Deliver source-pinned verifier, positive/negative evidence, regression tests and an exact next target even when gameplay identity remains unresolved.
5. **R4 / acceptance and resumption checkpoint.** Review diffs, verify input/output hashes and full test counts, validate task dependency DAG and changed links, make scoped local commits, check all session jobs stopped and worktrees clean except preserved baseline files. Finish every unblocked item above; leave a precise evidence/authorization blocker for genuinely unavailable WA-006 inputs.

## No conflict or wasted-worker policy

This ChatGPT session is the sole Manager and source writer. Independent model sessions are reviewers, not competing implementers. Workbridge's six command slots do not imply six AI workers. Use up to three useful reviewer sessions plus a bounded research/test command, leaving supervisory capacity. Each reviewer gets one question, complete relevant code, exact source hash, and a short response cap. Restrict permissions through per-process OpenCode inline configuration; no global permission/configuration changes. Do not repeat the previous external-directory or oversized-command failure mode. No infinite retry or idle agents.

Source packages and raw model results are immutable local artifacts. Record partial/error/timeout outcomes accurately. No review may mark a test passed without actual run evidence. No new paid-model selection, installation, runtime update, public publishing, or permission escalation.

## Review requirements

- A missing unit is not empty scenery; no live freshness derived from an old file.
- IDs merge only inside a qualified source scope; conflicting coordinates/roles remain explicit.
- All JSON values used in rendering and metadata must have bounded, valid types; output failures must be honest and recoverable.
- Projection uses only an explicit matrix convention and binds the exact input; no inferred occlusion or walkability.
- Output commits must not overwrite reports or inputs. Both portable tests and exact-build verifiers are required, with separate historical/synthetic labels.
- Full review coverage and all dispositions must be recorded before WA-005 is accepted.

## Full world-recognition gate remains unchanged

WA-006 requires actual simultaneously identified non-self units, a qualified physical hit/owner, a common scene/coordinate binding and independent camera landmarks. Existing saved player-only data, synthetic fixtures, static pointer candidates, and a screenshot-looking plot do not satisfy that gate. Existing authorization covers offline source/saved-evidence work, not game input, debugger/process attachment, native execution, or external-repository edits. Complete independent work without requesting optional clarification; never erase the remaining gate to label the overall project finished.

Model self-report: GPT-6 Astra Pro. Reasoning level: unavailable; machine records leave it blank.
