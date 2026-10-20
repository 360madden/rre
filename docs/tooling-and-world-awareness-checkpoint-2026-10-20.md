# RRE toolchain and world-awareness checkpoint — October 20, 2026

Starting main commit: `67c0a3bf1afce3992a5605e8311ccd296382b214`. Joey expanded the assignment to identify and resolve tooling gaps across RRE as well as Workbridge. The current ChatGPT session is the sole Manager/source writer. Model self-report: GPT-6 Astra Pro; reasoning level unavailable. The implementation commit is recorded in `docs/roadmap-tasks.json` after integration.

## Outcome and boundaries

Five concrete RRE tooling improvements are implemented and validated: the independent-review adapter, compact evidence summaries, retained raw native-key index, unified validation gate, and verified two-file report publication. The saved-data inspector is now version 1.1.0. These improvements do not prove current nearby-object enumeration, actual gameplay-entity ownership, live camera calibration, or navigation.

The final unified command passed **357 tests**, no failures or skips, with tools-source hashes unchanged during the run. This is broader test selection than the previous 80-test slice: it explicitly includes every lane Python filename matching `*test*.py`, including the earlier M4A files, plus the new Node adapter tests. Do not describe all additional coverage as newly authored tests.

| Group | Actual tests | Result |
|---|---:|---|
| Validation lane | 144 | exit 0 |
| C2M geometry lane | 30 | exit 0 |
| Follow guards lane | 73 | exit 0 |
| Collision lane | 47 | exit 0 |
| Pathfinding lane | 46 | exit 0 |
| Review-adapter Node tests | 17 | exit 0 |
| Roadmap validator | Not a unit-test count | exit 0, consistency passed |

Job: `rre-tools-20261020-unified-gate-02`. Durable result and per-group logs: `artifacts/research-gate-20261020-tools-02/validation.json`. Every test ID, command, exit code, source hash and log hash is retained. This does not include tests from other repositories, live gameplay, model quality, or installed Workbridge runtime acceptance.

## TG-001: review orchestration and semantic completion

`tools/agent-review-runner.mjs` consumes a bounded request file and a source-hashed review packet. It launches the installed executable with literal arguments, not a giant shell command. Each run retains the exact request/configuration, raw stdout/stderr, independent session ID, requested model, timeout/output-limit state, source hashes and a structured result. Existing outputs are never reused or overwritten.

The adapter separates **process exit**, **review response structure/coverage**, and **Manager acceptance**. Empty replies, permission/step-limit summaries, provider errors, malformed JSON, wrong source hashes, missing coverage, schema-example echoes, and missing source-specific checks cannot automatically pass. Even a well-formed response keeps `managerAccepted=false` until its claims are checked. A failing regression exposed acceptance of JSON null; the object-type guard now rejects it. Seventeen adapter tests passed in the unified gate.

The prior `steps:1` configuration produced maximum-step summaries rather than useful reviews. The adapter omits that setting. File/custom-agent requests remained unreliable in observed runs; bounded inline packets with the built-in plan agent produced real responses. These observations do not prove a universal provider diagnosis. Per-process permissions deny modifications/commands; a review tool event disqualifies automatic acceptance. No global settings, dependencies or provider credentials were changed. Only explicitly requested free models were used.

Actual reviewer quality remained a separate limitation. Initial inline A/C replies copied the schema's example summary. The revised classifier rejects those responses; the old raw logs are preserved rather than rewritten. The current-source A review violated the no-tool/format requirements and made numerous counterfactual claims. B omitted required coverage and made false matrix/viewport claims. C returned a complete structured presentation/IO review, but its four alleged defects were rejected after source and test checks. C's delivered review is preserved for the pre-final-guard source. The subsequent publication-schema amendment has no independent delta review, so **WA-005A/B/C and overall WA-005 are not fully accepted**.

### Reviewer claim dispositions

- The exact check `type(value) is int` rejects booleans; the claim that it accepts True was false.
- A missing actual ID reaches a deliberate ValueError. `dict.get` does not raise the claimed KeyError.
- Partial XYZ is rejected. A typed unavailable coordinate produces no position, not a fabricated coordinate.
- Unit specifiers such as `player` are deliberately not accepted as persistent entity IDs. Unknown names are allowed and are not substituted for IDs.
- `nonsingular` works on sliced rows, preserves the caller's matrix, and returns False for zero-scale rows before division.
- Zero viewport width/height is rejected before projection. Internal projection helpers expect already validated camera data.
- Zone sorting has an explicit deterministic key. Missing zone and the literal zone name `unknown` are now distinct groups.
- Simultaneous publication to the same directory intentionally allows only one creator; a second request fails without clobbering the first report.
- Publication verification reads at most `MAX_BYTES + 1`; it does not read an arbitrarily large file into memory.
- SVG projection rendering explicitly skips a null screen position.

Concrete Manager replay: `artifacts/wa2-review-counterexamples-20261020-01.json`, job `rre-tools-20261020-review-counterexamples-01`. Original reviews remain under `artifacts/wa2-final-WA-005A-20261020-01/`, B and C equivalents. Current classifier replay of prior immutable logs is `artifacts/wa2-review-reclassification-20261020-01.json`. No reviewer-suggested unsafe cleanup code was applied.

## TG-002: recording completion is not complete disassembly

`tools/evidence-summary.py` verifies the saved artifact/manifest hashes and distinguishes a completed recording from fully decoded requested anchors. It reads saved JSON only; no binary scan or live process access occurs. It retains unresolved and unaccounted anchors, fully decoded/partial regions, row counts, original source identity and parser-warning counts.

The actual original WA capture requested **five** anchors. Its V7 recording completed, but only **two** anchors have decoded PE-unwind regions; **three** are explicitly unresolved. The new summary reports `recordingCompleted=true` and `allRequestedAnchorsDecoded=false`, retaining all 825 existing parser warnings. Job `rre-tools-20261020-coverage-summary-acceptance-01`, output `artifacts/wa2-initial-hit-coverage-summary-20261020-01.json`, exit 0. Original V7 manifests were not changed.

## TG-003: retain the complete bounded raw-key index

`tools/agents/collision/wa_backlink_literal_index.py` retains every raw `ffff0000` match from the bounded original `.text` scan, not just the nearest 24 regions. The saved index contains **777 raw matches**, **479 selected containing regions**, and **64 raw matches without a selected containing unwind region**. Raw byte flags help prioritize already saved candidates but are not disassembly, pointer ownership or proof of absence elsewhere.

One corrective acquisition was performed because the earlier ad-hoc top-24 result discarded the rest of the candidate set; further identical rescans are unnecessary. Source: `artifacts/wa2-complete-key-index-20261020-01.json`, SHA256 `75b5742fd6d486fc44bffbc849d2a479fc8c2c2971e9c1d59a8cdc412f9874d9`. Job `rre-tools-20261020-complete-native-index-01`, exit 0. The old partial output remains unchanged.

## TG-004: one durable validation entrypoint

`tools/validate-research.py` executes explicitly enumerated groups, records actual unittest IDs/counts instead of guessing from filenames, retains each group's stdout/stderr and exit code, updates a run-local checkpoint, and verifies tools-source hashes stayed unchanged. A fresh output directory is required. The validator performs no dependency installation or model calls. It does not represent all possible RRE behavior or any other repository's acceptance.

## TG-005: complete versus partial report publication

Inspector 1.1.0 writes `complete.json` **after** `report.json` and `report.html`. The receipt records both files' sizes and SHA256 hashes. `--verify-output` checks the fixed file set and source identity. A failed second write leaves an inspectable partial directory without a valid completion receipt; it does not delete prior user files or pretend rollback was atomic. Older version-1.0 reports are retained and are not retroactively assigned completion receipts.

New tests cover the completion marker, an injected second-write failure, tampering, zone-sentinel separation and historical-metadata type validation. A final negative pass also demonstrated a missing source-hash check and missing published-report schema check in the new verifier. Both were fixed and retained as regression tests; the prior 355-test run is preserved separately from the final 357-test run. Existing-output replay returns exit 2 and preserves all three files byte-for-byte. Actual historical and synthetic outputs both passed publication verification:

- `artifacts/world-inspector-v11-final-20261020-recorded/`: one historical RR2 player ID/XYZ; not current scene truth.
- `artifacts/world-inspector-v11-final-20261020-demo/`: six synthetic records, five IDs, four known positions; no real objects or collision shapes inferred.

Job `rre-tools-20261020-final-v11-reports-02`, exit 0. Completion verification means file-set integrity, not live-world validity.

## WA-007: bounded native progress and a remaining blocker

Before the next tool-blocked request, three completed original-build V7 captures retained **seven PE-unwind regions / 469 instruction rows**. Original executable SHA256 remains `7c356c9dde9e12fcbff3c08d953b0630b48b1510a0ffb36e4ec164606e7b17bd`. The saved-only verifier `tools/agents/collision/wa_backlink_saved_verify.py` now rechecks those immutable captures and exact instruction pins without new native acquisition.

A useful helper at RVA `0xF674E0` clears its output first, reads the 16-byte keyed records at receiver `+0xB0`/count `+0xB8`, finds key `0xFFFF`, and passes its associated value through `0x491320` into lookup `0x68E150` with index zero. The latter selects the receiver's `+0x50` container, calls an unexpanded lookup and can return a node's `+0x10` value. This is a stronger ownership lead than a matching offset, but the property's writer, key/value meaning, returned class and logical entity ID remain unknown.

The apparent nearby writer at `0x13D1960` was rejected: it uses `0xFFFF` as a 16-bit decrement value rather than demonstrated property insertion. Other scanned candidates contained masks or constructor sentinels. Only an initial four-instruction region of `0x491320` was captured; **do not call that a complete function or return-value proof**.

The requested next capture was blocked by the tool's safeguards. It was not retried through another tool or path. WA-007 remains blocked with a preserved partial checkpoint rather than falsely completed. Saved verification: `artifacts/wa2-backlink-saved-verification-20261020-01.json`, SHA256 `01573023f103dbe7c1c1346fb362f674b99b7ff3315fb4ea61d40a10e5eb0c4c`; job `rre-wa2-20261020-save-bounded-backlink-checkpoint-01`, exit 0. Six new saved-evidence regression tests are included in the collision group above.

## Workbridge findings

The active Workbridge 0.6.1 service successfully ran the source operations, bounded processes and test commands. Its `passed` job status denotes process completion, not semantic model review acceptance; fixing that distinction belongs in RRE's adapter. No confirmed core Workbridge defect was responsible for these review failures.

A general paged job-ID listing is an interface gap: the exposed tools provide known-ID status/output and diagnostic counts, not a catalog of job IDs. Durable RRE run receipts now preserve this workflow's identities and results. They are not a global Workbridge job listing. The Workbridge source repository has substantial pre-existing uncommitted changes, including jobs.ts and server.ts. They were not overwritten, committed or deployed. No runtime restart, command-host rebuild, permission escalation or user-setting change occurred.

## Reproduce and resume

From PowerShell in `C:\work\rre`:

```powershell
& .\.venv\Scripts\python.exe -B tools/validate-research.py --output-dir artifacts/research-gate-next
& .\.venv\Scripts\python.exe -B tools/world-inspector.py --verify-output artifacts/world-inspector-v11-final-20261020-recorded
Start-Process 'C:\work\rre\artifacts\world-inspector-v11-final-20261020-recorded\report.html'
```

Use a new validation output directory every run. Read `TOOLING_GAP_REGISTER.md`, `WORLD_AWARENESS_COMPLETION_PLAN.md` and the current machine board before resuming. TG-001..005 can be accepted after the validated source commit; incomplete review quality and the blocked native expansion are not silently removed from the roadmap. WA-006 still needs actual simultaneous non-self entities, a qualified physical hit/owner, scene identity and independent camera landmarks. M3-001 and the M4/M5/M6 gates are unchanged. No game input, process attachment or native function invocation occurred.
