# WA-005A/B/C independent inspector QA — 2026-11-15 EST

**State:** Independent, no-tool static source reviews complete; final WA-005 acceptance **still blocked** by the historical original-executable hash gate in the broader research suite. This document does not qualify live game behavior, a current scene, collision ownership, or navigation.

## Source and machine identity

- Host: independently verified **AMD-DESKTOP** via named Workbridge 0.16.5-dev and `hostname.exe` (exit 0); repo `C:\work\rre`. No LEGION/VMware/game UI/process operations.
- Final file-only inspector: `tools/world-inspector.py` **v1.1.2**, SHA-256 `fdbc066c2da4a929fc8219a839ba8c02d72aad741f8157c8584cac5933347eb6`.
- Final test: `tools/agents/validation/test_world_inspector.py`, SHA-256 `fce86d3672d4fe9f1bc0df17a64520ca2d3ebd801a2af301ff2b9a986cdff25e`.
- Final contract: `docs/world-awareness-contract.md`, SHA-256 `1ecfdbc7d3d06140a7101db10e519b39a64d5ac170aa3d8f93c2ba24e1bd5aa4`.
- Review started from inspector 1.1.1 SHA-256 `77e487b942e58731a961ca9af79c8badf46e8843101ce7df0ddfcd8953146e02`. Historical October 20 v1.1.0 packet SHA `7f047323…` is **stale** and was not reused as final-source proof.

## Independent reviewers and source coverage

Three **separate ChatGPT subagent model turns**, not Workbridge command slots or tool-assisted preparatory audits, reviewed the source supplied in parent-history line-numbered Workbridge results, together with the full contract. Each was explicitly prohibited from tools, process/file access, code execution, nested workers and mutation. Their response self-reported zero tool calls; separate raw event-trace/model-runtime IDs are not exposed here, so they are **not invented**. Their actual reviewer paths are preserved below.

| Task | Actual independent reviewer | Source coverage | Completed verdict |
| --- | --- | --- | --- |
| WA-005A | `/root/wa005a_no_tool_review` | Helpers/parsing/identity lines 26–260; public `inspect_data` entry and file path | Identified A1/A2; manager disposed both; reviewed each code/contract delta to the final SHA |
| WA-005B | `/root/wa005b_no_tool_review` | Numeric, camera, frustum, projection and report lines 36–44, 122–129, 261–348, file path | No actionable source-demonstrable defect; earlier B1–B4 allegations remain rejected; reviewed final deltas |
| WA-005C | `/root/wa005c_no_tool_review` | HTML, plotting, publication, receipt verifier, CLI lines 349–503 and shared helpers | No actionable source-demonstrable defect; independently checked source-delta continuity |

Original inspector 1.1.1 source was provided in bounded, line-numbered ranges `1–105`, `100–262`, `261–350`, `349–407`, `408–503`. Full contract lines `1–34` were supplied. No reviewer read the Windows filesystem; later source changes were supplied in exact before/after terms and corresponding SHA-256 values for no-tool delta reviews. The manager separately rechecked final file hashes and diffs. This is **independent static code QA**, not an external-provider or live test; no external reviewer session ID is claimed. Historical failed MiniMax/Nemotron attempts and blocked Codex launcher were **not** retried.

## Manager dispositions and implementation

1. **UC-01 — accepted and fixed.** `text()` rejected only C0 (`ord<32`) and surrogates, allowing Unicode Cc DEL `U+007F` and C1 `U+0085/U+009F` inside consumed IDs/names/zones. Before the patch, `rre_20261116_0532_wa_unicode_red_01` exited **1**, 67 tests with **nine failing subtests** across these three consumed fields. Source now uses Python-standard-library `unicodedata.category(c) == "Cc"`, preserving the lone-surrogate guard and permitting ignored extension-field controls. Static allowlist updated. Final targeted test exits **0**.
2. **A1 — accepted as an ambiguity guard, fixed conservatively.** The old ID exclusion rejected `group01` but accepted dotted `group01.target`/ `raid01.target`/`raid20.focus`. `rre_20261116_0549_wa_group_alias_red_01` exited **1**, three new failing cases. Regex now excludes `(?:group|raid)\d+(?:\..*)?`; ordinary `u...` IDs remain accepted. This does **not** claim those exact dotted strings resolve in the actual RIFT API. Separate read-only architecture QA confirmed rejection of three specifier-shaped inputs and acceptance of six ordinary opaque-ID examples.
3. **A2 — intentional behavior, documented.** Partial ReaderBridge coordinate objects are errors. RR2 typed fields with incomplete `ok` status triplets deliberately produce unknown position, retain individual status metadata and do **not** fabricate XYZ. Contract now makes the distinction explicit; no source modification was warranted.
4. **B and C — no actionable changes.** Camera frustum/math/HTML/receipt/CLI semantics were reviewed against actual functions. Prior B1–B4 allegations had been rejected with counterexamples; no reopening or code change from those allegations.
5. Version advanced from **1.1.1 to 1.1.2** to distinguish the tightened accepted-input policy. New reports and receipts both advertise 1.1.2; old publications were not rewritten.

## Actual test and publication receipts

| Evidence | Actual result |
| --- | --- |
| Baseline inspector `rre_20261116_0528_inspector_baseline_01` | 66/66 passed before edits |
| UC-01 red `rre_20261116_0532_wa_unicode_red_01` | exit 1, nine subtest failures, expected |
| UC-01 green interim | First run found a **test allowlist** failure for new stdlib `unicodedata`; allowlist corrected, next run 67/67 passed |
| A1 red `rre_20261116_0549_wa_group_alias_red_01` | exit 1, three subtest failures, expected |
| Final focused `rre_20261116_0552_wa_inspector_final_01` | **67/67 passed**, exit 0 |
| Full Node `rre_20261116_0540_wa_node_suite_01` | **358/358 passed**, exit 0 |
| Final research gate `rre_20261116_0552_wa_full_research_final_01` | **FAILED** overall; 514 tests executed across groups, source hashes unchanged, 7/9 groups passed (counting roadmap), collision and pathfinding blocked by exact-PE mismatch |
| Final publication `rre_20261116_0555_wa_final_pub_01` | exit 0, synthetic six records/five IDs, version 1.1.2, remains `live:false` |
| `rre_20261116_0557_verify_publication_0/1/2` | exit 0 each: final 1.1.2 synthetic, untouched prior 1.1.1 synthetic, untouched prior 1.1.1 recorded |

The immutable final demo resides at `artifacts/world-inspector-v112-20261116-demo-final/`. Its `complete.json` advertises version 1.1.2 and source hash `df156fdf4ab5b0b2b8a20eb18736a4327b474b8bbb7813bfbbb9ae6c03bdc77d`; the input itself is synthetic, not live. Original saved reports remain preserved.

**Full-gate blocker:** The historical `tools/agents/collision/wa_hit_result_verify.py` and multiple `tools/agents/pathfinding/m3_001_*` tests require original executable SHA-256 `7c356c9dde9e12fcbff3c08d953b0630b48b1510a0ffb36e4ec164606e7b17bd`. The actual installed `C:\Program Files (x86)\Glyph\Games\RIFT\Live\rift_x64.exe` on independently verified AMD-DESKTOP is **60,493,640 bytes**, SHA-256 `1935a05c9db6d468e34e0055014a4a99c1b5afceb1695884e24600f5c20a4be8` (read-only hash job `rre_20261116_0545_wa_pe_identity_01`, exit 0). The earlier source-build tests correctly **fail closed**. No RVA substitution, bypass, rewrite, process attachment, game input, VM access or speculative pass claim was made. Logs retained under `artifacts/research-gate-wa005-20261116-0439/`.

## Acceptance boundary / next actions

- **WA-005A/B/C:** No-tool source reviews and manager dispositions complete for final inspector SHA; can be recorded as individual independent **static QA** integrations.
- **WA-005 overall:** Remains **blocked** on reproducible whole-research validation against an explicitly preserved, source-hash-matched original PE or an approved revision of the historical-fixture test architecture that retains exact-build checks. Do not change hashes just to force green.
- **WA-006:** Requires real, simultaneously bound non-self units, collision/owner and camera/scene evidence; no such evidence is supplied by this file-only result.
- **WA-007:** Native capture remains separately blocked and was not retried.

Recommended next work, in order:

1. Locate and qualify an **archived exact old PE** for offline legacy test fixtures, preserving current installed RIFT and refusing hash mismatch; otherwise keep the two groups transparently blocked.
2. Record these three independent reviewer outcomes against task IDs with exact hashes, task paths, test jobs and the real whole-gate blocker. Preserve historical failed reviews instead of rewriting them.
3. Advance WA-006 only after separately authorized current physical RIFT scene/source evidence; do not infer a live-world map from synthetic/recorded reports.
