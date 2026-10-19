# Navigation research tools: five regression fixes

Local date: 2026-10-18 (EDT); validation job UTC date 2026-10-19. Source repo `C:\work\rre`.

This document **supersedes only the unresolved status of V1–V5** in the historical independent report `docs/agents/validation.md`. The original worker report remains intact as the evidence of what failed. **No game movement or live attachment was performed.**

## Source changes

| ID | Previous regression | Corrected behavior |
| --- | --- | --- |
| V1 (P1) | Original helper returned the first 64 raw `E8` patterns, potentially all embedded in other instructions, hiding a real later `CALL`. | `inspect-navigation-static.py` traverses common x64 direct relative-CALL candidates in executable section buffers, qualifies each against Capstone decoding from the PE unwind region, retains up to 64 verified sites **after** qualification, and records per-target `callerSearchSummary` including scan/retention counts and truncation. |
| V2 (P2) | Empty/unmapped decode window marked `instructionDecodingCoversWindow=true`. | Decoding completeness now requires a nonempty window. `windowTruncated` remains separately recorded. |
| V3 (P1) | REA `open_binary` could admit an unexpected file/hash and still allow queries. | `rea-session.mjs` rejects mismatch/absence in provider-returned path, SHA256, `x86_64`, or `pe` before analysis. If opened, it still attempts evidence export and close. |
| V4 (P2) | A job ending `time-budget-reached` returned OS exit 0. | Exit 0 now requires `state=completed` and zero recorded failures; non-completion exits nonzero. |
| V5 (P2) | An existing `identity.json` could be overwritten when `status.json` was missing. | Preflight blocks old evidence even with missing status; all receipts and responses are created with exclusive-write, with only mutable `status.json` rewritten. |

Historical artifacts are not modified. The newly accepted source code does **not** establish complete static coverage: leaf functions without unwind data, indirect calls, tail transfers, alternative encodings, mid-range decode breaks, and runtime reachability remain separate questions. Caller scanning records a qualified-result truncation signal, but the current scan is still a targeted x64 direct `E8 rel32` pattern search rather than a complete xref index.

## Validation completed

- Initial V1–V5 synthetic suite: **12 passed, 0 expected failures, 0 skipped**. On 2026-10-19 EDT, a fresh run of the expanded suite (including a synthetic raw-probe contract check) reported **13 passed, 0 expected failures, 0 skipped**; job `rre-resume-m1-regressions-20261019-01`, exit 0. Prior to repair, the original suite reported seven passes and five expected failures; strict reproduction demonstrated those failures.
- Node source syntax: `node --check tools/rea-session.mjs` **exit 0**.
- Exact-build static query: `tools/inspect-navigation-static.py --rva 0xF3FA4 --caller-rva 0xF3FA4 --depth 0`, using the pinned Rift executable and original RiftReader helper hashes, **exit 0** in about 5.7 seconds.
- The new direct caller search found **2 raw candidates, 2 boundary-qualified**, at RVAs `0x8A9E6` and `0x8EFD0`; no qualified truncation. Three PE windows decoded to their captured ends; queue remaining zero.
- New output retained outside Git at `C:\work\rre\artifacts\navigation-hardening-20261018-01.json`, SHA256 `0f9c473da29319c03ceb7bc6045a4dfa2fa9756446def9627b563fe5e5db7430` (126,475 bytes).
- The selected exact binary SHA256 remains `7c356c9dde9e12fcbff3c08d953b0630b48b1510a0ffb36e4ec164606e7b17bd`.
- V3–V5 and the raw-probe contract test use a **synthetic fake MCP client**; no actual REA/Ghidra import was run to test these fixes. A fake provider's wrong hash is rejected before any analysis query. Small raw-binary admission is driver support only, not evidence of real Ghidra readiness.

## Still open (nonblocking)

- **V6:** native PE parsing emitted 825 pefile warnings in the previous audit, some referencing chained-function-entry bookkeeping. Investigate root cause before asserting global unwind-chain coverage. Selected saved chain roots were independently byte-checked; no known corruption in those selected results.
- **V7:** improve immutable exact-run input/source manifest and consistent Capstone version labeling (`dist 5.0.9`, module `5.0.7`). Original artifact schema versions and line endings differ; preserve original hashes.
- A fresh exact-build static query on 2026-10-19 (job `rre-resume-m1-exact-pe-query-20261019-01`, exit 0) read three unwind regions and requalified direct dispatcher callers at `0x8A9E6` and `0x8EFD0`. Saved result: `artifacts/navigation-m1-resume-20261019-0148.json` (126,475 bytes, SHA-256 `d72c03ae46c63adda16cb96bcfceed72270c4999a4fad044d6c9a638a567b7af`). This is offline instruction evidence, not runtime navigation.
- The input/job type `7` pathfinding handler population and player ownership remain unknown. The C2M destination and Havok collision leads are still hypotheses requiring their own qualified validation.

## Reproduce

Run in `C:\work\rre`:

```powershell
& 'C:\work\rre\.venv\Scripts\python.exe' -B -m unittest discover -s tools/agents/validation -p 'test_*.py' -v
& 'C:\work\rre\.venv\Scripts\python.exe' -B tools/agents/validation/audit_saved_evidence.py
& 'C:\Program Files\nodejs\node.exe' --check tools/rea-session.mjs
```

The test scripts use temporary synthetic PE/fake-MCP fixtures, remove them afterward, and do not launch the Rift game or Ghidra. The evidence audit inspects the existing saved artifacts read-only.
