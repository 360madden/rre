# RRE session handoff — 2026-11-26 EST / 2026-11-27 PHT

## Scope and last verified baseline

- Host: LEGION, verified locally. Repository: `C:\work\rre`, branch `main`. Starting HEAD and remote main: `3dafd763cf30249ec5573c25296299f91bbd60e3`.
- Manager-only SC-103 offline follow-up, P1 from [November 21 consolidated handoff](RRE-CONSOLIDATED-HANDOFF-2026-11-21-1620-EST.md). No independent AI workers launched; no game input, live lookup, debugger, native capture, installation, process control, VMware access, or other repository edits.
- SC-103 remains blocked on live rank/variant/role evidence. P0 physical Collector acceptance and WA-006/007 runtime gates are not satisfied by this offline work.

## Implementation and observed validation

- `tools/plan-pab-static-candidates.mjs`: requires a canonical calling and 1–8 explicitly supplied, distinct exact IDs, pins original V2 catalog SHA-256, retains source-file hash, soul and source line, distinguishes duplicate-name context and cross-calling occurrences, rejects unknown or wrong-calling IDs, and labels all runtime qualification false. No game queries or catalog mutation.
- `tools/test-plan-pab-static-candidates.mjs`: six deterministic focused tests, including wrong calling, byte mutation, duplicate input and duplicate-name/cross-calling provenance.
- `.gitattributes`: pin the two published November 21 static catalog JSON files to LF. On LEGION a clean Git checkout previously held CRLF copies. V2 working-tree SHA was `5115b7ca27a3eef55e65956404d3726bbcba4608528c5bb6e27477a63d438dc6` (463,894 bytes); Git blob was the original `5685fa02b82b9802739f85348dcf1d0514a8b1b3e39353cf80f96135cc36908c` (449,055 bytes). Restored only exact newline-equivalent checkout copies after verifying the committed and index blobs matched; both V1 and V2 SHA pins now match the original committed blobs. No catalog content change.
- Initial combined run `rre_20261127_p1_test_01`: 9 pass / 6 fail, exit 1. Two source read failures were caused by observed OneDrive metadata changes on open (ctime only); opening cloud placeholders may hydrate them. No source file content edits or integrity-guard relaxation. Repeated the test only after the observed metadata change/hydration. Final combined run `rre_20261127_p1_test_02`: **15/15 passed**, exit 0, zero skips, including 56/56 original source files and exact V2 reproduction. Checkout repair `rre_20261127_catalog_canonical_01`: exit 0. Prior checkout-index attempt did not rewrite the file, exit 1; equivalent bytes were verified before the narrowly scoped canonical restoration.
- CLI smoke `rre_20261127_candidate_cli_01`: exit 0; both distinct Flame Lance IDs and shared Dismiss Pet ID retained, cross-calling and duplicate-name context observed, all live qualification false. V2 ordered source-manifest SHA `898f651e8fd272dc220fe0c32aecbb3e937dac750d6d9b912b1f94ab561eb5bb`.
- Decision: cap explicit requests at eight as in earlier RC-07 bounded canary scope. No automatic full-catalog sweep; no inferred learned/unlocked/castable state. This packet is offline preparation, not a request to execute a game lookup.
- Integration gate `rre_20261127_p1_integration_gate_01` initially exited 1: WA-006 matrix and static verifier working-tree SHA mismatches. `rre_20261127_wa006_pin_diagnose_01` verified committed/index blobs and exact CRLF-only differences. Added LF attributes for those two files and restored byte-identical committed copies, without changing evidence pins or file contents in Git.
- Final integration gate `rre_20261127_wa006_restore_gate_01`: exit 0, 11 milestones / 47 tasks, 9 WA-006 current source pins, negative control passed, `git diff --check` passed. Board counts remain 37 integrated, 8 blocked, 2 deferred. No WA-006 runtime acceptance implied.

## Exact restart commands

```powershell
node --test tools/test-plan-pab-static-candidates.mjs tools/test-inventory-pab-static-abilities.mjs
node tools/plan-pab-static-candidates.mjs Cleric A060ED54D21F2B259 A1A35B21D4891044E A40C51A65DBA71310
node tools/validate-roadmap.mjs
git status --short --branch
```

Next: first validate original local installed package and character SavedVariables if available under current physical-only policy; do not infer game acceptance from source parity or stale records. P0 requires operator-coordinated current version-matched UI and persisted unit/ability capture. WA-006 requires same-epoch independent nonself IDs and scene evidence; no new live probe without the task-specific authority and preflight. Git publication status is to be verified separately; this handoff is not a push receipt.

## P0 physical package readiness — November 27, 12:35 PHT (November 26 EST)

- Host verified LEGION. Physical RIFT process count 0 at preflight and deployment checks. No game launch, input, reload or runtime acceptance.
- Initial audit `rre_20261127_p0_audit_01`: installed/source v0.4.23; 7/12 raw hashes matched, no files missing. All 12 files were verified newline-equivalent to the corresponding source in `rre_20261127_p0_file_compare_01`; no Lua logic mismatch.
- `.gitattributes` now pins RRECollector Lua and TOC files to LF. `rre_20261127_p0_source_canonical_01` exit 0: all 12 source files match the unchanged Git blobs; index has no staged content changes.
- `rre_20261127_p0_install_parity_01` exit 0: verified backup of all 12 original installed files at `artifacts/rrecollector-v0423-precanonical-legion-20261127-1234-pht` with `backup-manifest.json`; copied only seven newline-different RRECollector files, TOC last, while physical client was stopped. Strict package gate 12/12, v0.4.23 unchanged. The install lives in OneDrive Documents; other hosts' current runtime/installation not verified.
- `rre_20261127_p0_postrepair_gate_01`: readiness audit proves source/install parity 12/12 and original Atank saved data SHA-256 `d2f6a94ec8de8d77bc4bceb86cc51a92785be12028bff6bc29e6f73593c73e34`, 68,045 bytes, modified 2026-11-27T03:47:41.248Z. Root v0.4.23; latest accepted ability producer v0.4.20, seq 2, 55 entries, complete; no capture attempt or unit attempt/snapshot. Saved timestamp does not prove current runtime capture.
- Combined regressions: 27/36 passed, nine failed because the exact pinned Lua 5.1 executable/DLL were absent on LEGION (`artifacts/sc103-lua51-msvc-20261104-1925-v1`). No substitute runtime or new dependency was installed. Node readiness and exporter tests all passed. Roadmap `rre_20261127_p0_runtime_dependency_01` exit 0, 47 tasks and 9 pins validated; no board state change.
- Remaining P0 gate: operator launches/logs into physical RIFT on LEGION, confirms version 0.4.23 UI in a playable scene and runs `/rre status`, `/rre capture`, `/rre units`, then normally reloads UI or logs out to flush original SavedVariables. Record direct UI evidence and re-audit persisted captures. Do not mark P0 accepted until these witnesses pass. Backup and prior saved evidence retained. No WA-006 acceptance or live agent launched.
