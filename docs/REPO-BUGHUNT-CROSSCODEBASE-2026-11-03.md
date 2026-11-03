# Cross-repository bug hunt — November 3, 2026

**Owner:** RRE integration manager. **Isolated repair branch:** `bughunt/freebuff-supervisor-20261103` in `C:\work\rre-bughunt-freebuff-20261103`. **Baseline:** RRE main `e5a060a6a3df9a2b8c3da54fdbabbedec1642cc0`. No installed addon, physical RIFT, VM, Workbridge service or other repositories' tracked source was changed.

## Confirmed bugs and branch repairs

| Priority | Defect | Before | Fix |
| --- | --- | --- | --- |
| P1 | FreeBuff `clean_summary([])` and one/duplicate-worker cases | Incorrectly returns `completed` because Python `all([])` is true | Require exactly two distinct worker modes before accepting aggregate completion |
| P1 | `completedReviewSessions` counter | Counts an exited/failed worker when its completion markers exist | Count only settled exit-zero workers with prompt, marker, adapter, stopped-child and temp-cleanup receipts |
| P1/P2 | Timeout after Windows `taskkill` fails | Second `communicate()` may raise uncaught `TimeoutExpired` and never attempt the exact-child fallback | Retry with `proc.kill()` on the owned child, use bounded waits, surface `cleanupFault`, fail closed if termination cannot be confirmed |

**Red-to-green evidence:** `rre-bughunt-freebuff-three-red-regressions-20261103-a1` exited 1 with **two assertion failures plus one uncaught timeout**; seven pre-existing supervisor checks passed. The repaired branch passed **10/10** in `rre-bughunt-freebuff-green-unit-20261103-a1` and **12/12** in `rre-bughunt-freebuff-12cases-20261103-a1`. Added coverage for Windows `taskkill` returning nonzero, throwing, and an unkillable child. The final diagnostic improvement records `TASKKILL_FAILED` even when the fallback succeeds. All simulations are **in-memory mocks**: no live process was killed.

Synthetic concurrency `rre-bughunt-freebuff-overlap-extra-20261103-a1` passed with **1.063s** harmless Python child overlap. Adapter preflight and source/diff checks passed.

**Remaining limit:** If Windows refuses both `taskkill` and a direct-child kill, the code reports `CHILD_STILL_RUNNING` and cannot mark the review complete; it cannot guarantee privileged cleanup.

## Other codebases examined with synthetic or read-only checks

| Repository | Tests and outcomes |
| --- | --- |
| ChatGPTGoals v1.3.7 | Node `tests/store.test.js` and `tests/runner.test.js` **both passed** |
| Agent_Reasoning | Release checks **17 passed, 0 failed, 1 skipped**; symbolic-link fixture unavailable because Windows lacks that test privilege |
| AutoFight | Core **149**, Windows/VM **141**, Guest **13** passed: **303 total, 0 failed** |
| Workbridge | FreeBuff VT-screen test **6 passed**; no service build/restart |
| RRE agent-review adapter | **17 passed** |
| RRE FreeBuff supervisor | Historical baseline **7 passed**; isolated fix **12 passed** |
| RRE roadmap | 47 tasks/11 milestones; **zero validation failures** |

Coverage is limited to these offline/synthetic checks; no actual GUI, VMware, RIFT casting or RC-30 Pin→Undo behavior was validated.

## Historical navigation build mismatch — not a new client update

The historical `tools/verify-integrated-navigation.mjs` gate exited 1 because it pins source SHA `7c356c9dde9e12fcbff3c08d953b0630b48b1510a0ffb36e4ec164606e7b17bd`. A fresh read-only original executable hash of the physical RIFT Live client remained `1935a05c9db6d468e34e0055014a4a99c1b5afceb1695884e24600f5c20a4be8`, 60,493,640 bytes, matching the qualified October 27 PC source. This is a **historical verifier versus current physical target** mismatch. Do not overwrite the historical expected hash merely to pass the old test.

## FreeBuff independent-review limitation

Two additional isolated FreeBuff code-review launches were attempted. The visible screen presented an interactive UI choice rather than a source-grounded completed review; the one-off prompt included a literal completion marker that might be echoed. Neither launch was accepted as an actual AI review. No consent/privacy choice was selected, and no review result was used as evidence. Future pilot markers must be calculated by the model rather than supplied verbatim in the prompt.

## Ownership / integration

RRE main was already dirty in three FreeBuff source/test files and later additional task records owned by another workflow. **Do not overwrite or stage those main files.** The fixes remain in this separate bug-hunt branch and must be integrated only after the main owner reconciles concurrent changes. Then rerun the bounded 12-case suite, synthetic overlap test and roadmap validator. Preserve RRECollector v0.4.10, SC-103 and RC-30 live gates, and all unrelated repository files.
