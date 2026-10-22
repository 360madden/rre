# RRE toolchain gap register — October 20, 2026

Scope expanded by Joey: tooling gaps across RRE, not just Workbridge. Fix the narrowest responsible layer, validate the fix with a failing/passing regression, and return to world-awareness research. Do not install a new framework or rebuild a functioning tool merely because a downstream task is unresolved.

## Priority and dispositions

| ID | Layer | Observed gap | Resolution/acceptance |
|---|---|---|---|
| TG-001 | RRE agent coordination | Several OpenCode processes exited zero with permission-denied/max-step summaries and no review; large shell/array arguments also misparsed. | `tools/agent-review-runner.mjs`: direct literal argv, bounded file request/packet, pinned hashes, isolated inline config, no steps:1 trap, separate raw logs/session IDs/process and semantic outcomes. A produced review is never automatically Manager-accepted. Test empty output, primitive JSON, wrong hash/coverage, provider/tool errors, timeout and truncation. |
| TG-002 | RRE evidence interpretation | V7 recording completion accounted for unresolved anchors, but could be mistaken for complete function recovery. Large raw JSON consumed review context. | `tools/evidence-summary.py` independently labels recordingCompleted vs allRequestedAnchorsDecoded and retains unresolved/missing anchors, exact hashes and counts. Validate against the actual 5-anchor/2-region capture and synthetic negative cases. Original V7 semantics remain unchanged. |
| TG-003 | RRE native search | An ad-hoc raw-key search retained only 24 proximity-ranked regions, requiring repeat acquisition for a different question. | `tools/agents/collision/wa_backlink_literal_index.py` preserves every bounded raw match, nearest unwind metadata range and source-byte relevance flags. Reuse immutable index offline. Raw flags are NOT disassembly or object identity. One corrective full index capture is justified; do not repeat it unchanged. |
| TG-004 | RRE acceptance/test workflow | Prior commands selected different filename patterns and reported partial suite counts; no single resumable validation entrypoint covered all changed tools. | `tools/validate-research.py` supplies a bounded validation command with explicit suite inventory, exit codes and durable logs. Keep portable/tooling/exact-native groups separate; count actual results, not expected tests. |
| TG-005 | RRE report publication | Two-file output had no durable completion marker; interruption after JSON could leave a plausible partial report. | Add a last-written SHA-bound publication receipt and regression for failed second write. Do not overwrite/clean existing reports; retained partial output is explicitly incomplete. |
| WB-G01 | Workbridge interface | HISTORICAL: original release lacked a paged job-ID listing. | **Resolved in observed 0.16.3-dev runtime:** `command_list` supports filtered paging and `diagnostics` provides live owner jobs, with 0 running at October 22 preflight. Incomplete bounded scans still require continuation. Six command-job slots are not six AI agents. Stop rebuilding job enumeration. |
| WB-G02 | Workbridge source/runtime separation | The original source and active 0.6.1 runtime differed. Current active Workbridge reports 0.16.3-dev. | Continue treating source checkout and runtime separately; preserve unrelated dirty edits. No blind service restart or in-place rebuild. No observed Workbridge core defect currently blocks the first navigation trial. |
| DATA-G01 | RRE/RiftReader observation boundary | Saved RR2 receipt is player-only; current multi-entity enumeration, physical owner correlation and real camera calibration absent. | This is a data/qualification gap, not solved by more unit tests or another synthetic map. Keep WA-006 blocked until actual bound observations exist. Do not invent terrain or authorize live actions by editing a roadmap. |

## October 22 workflow and imaging update

The current [execution optimization](NAVIGATION-WORKFLOW-OPTIMIZATION-2026-10-22.md) identifies **no required new framework or installation**. Existing RR2 Python/Pillow plus Workbridge's bounded command output now permits source-hash-pinned saved screenshot previews and native-resolution crops to be inspected by the model (tool capability verified this session). Visual inspection of the saved October 22 coordinated capture found a disconnected/loading game screen despite successful screenshot and host-ownership checks. Do not promote that historical observation to current disconnection, and do not retry blocked guest setup via a different route. Prioritize fresh playable-scene evidence and real one-click/movement-stop telemetry over additional converters or offline-only test-count increases.

## Verified implementation checkpoint

TG-001..005 are implemented. The final unified run `rre-tools-20261020-unified-gate-02` passed **357 tests**, with unchanged source hashes, and both final inspector 1.1 reports passed receipt verification. The compact summary was checked against the actual five-anchor capture: recording complete, two anchors decoded, three unresolved. All 777 raw key matches are retained in the reusable index. The source commit and exact evidence paths are recorded in the task board and [acceptance report](tooling-and-world-awareness-checkpoint-2026-10-20.md).

This acceptance covers the five bounded tooling fixes, not every possible toolchain feature. Independent A/B review quality, a C delta review, actual multi-object/physics/camera observations, and the blocked next native capture remain explicit open gates. The global Workbridge job-list API is not implemented; RRE-specific run receipts mitigate this workflow's resumption gap. No Workbridge runtime or pre-existing dirty source was changed.

## Inspector QA boundary follow-up

Commit `c651fb9` adds two verified fixes to the existing consumer: pre-publication UTF-8 byte limits that agree with TG-005's bounded verifier, and rejection of invalid Unicode scalars throughout decoded JSON, including ignored fields. Nine new regression tests were added. The current unified gate passed **377 tests**, including eleven Pathfinding tests integrated after the earlier 357-test tooling checkpoint. Both 1.1.1 report receipts verified, while old reports and original inputs stayed unchanged. Details: [inspector QA resumption](inspector-qa-resumption-2026-10-20.md).

Review quality/availability remains unresolved. The refreshed A/C model requests timed out, B attempted a tool and produced rejected counterexamples, and a proposed Codex review-launcher write was tool-blocked before creation. No Codex review ran, no blocked action was retried, and no new review driver is claimed implemented. These outcomes do not establish a Workbridge core defect or current Codex quota. Existing Workbridge source/runtime and native-capture boundaries remain unchanged.

## Current implementation model

The current ChatGPT session is the sole Manager and source writer. Independent reviewers return bounded assessments only; all their findings are checked. Tooling fixes stay in RRE unless a reproducible Workbridge defect requires a core change. No game process/input, external repo overwrite, dependency installation, public publishing, or silent permission change.

OpenCode reference checked on October 20: official Agents documentation describes the steps limit injecting a summary prompt; CLI/config docs define file arguments and inline configuration. Those are reference facts, not proof a model is available. Actual successful model output is required. Official source: https://opencode.ai/docs/agents/#max-steps ; https://opencode.ai/docs/cli/ ; https://opencode.ai/docs/config/ .

## Completion rule

For each TG item retain reproducer, source hash, tests/job exits, output receipts, integration commit and remaining limits. The full toolchain is not declared perfect: solved execution/diagnostic gaps remain distinct from unqualified native semantics and current provider availability. This register supplements WORLD_AWARENESS_COMPLETION_PLAN.md and docs/roadmap-tasks.json.
