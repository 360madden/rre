# Navigation research integration checkpoint — 2026-10-19

**Repository:** `C:\work\rre`  
**Purpose:** accept the preceding four independent Codex worker research lanes into `main` with exact evidence, explicit limitations, and a recoverable roadmap state. All game activities in this checkpoint were **offline analysis only**; no live Rift input, memory modification, debugger attach, process control, installed-tool patching or remote publication.

## Worker outcomes and integration

Four real Codex CLI 0.163.0 agents were launched into the preexisting exclusive Git worktrees, under the parent ChatGPT Manager and the M0/M1/M2/M3 roadmap gates. Each completed significant lane-owned evidence before **all four Codex runs ended exit 1 due to the same usage-limit message**. No nested subagents were spawned, and no worker wrote to `main`. The Manager independently reviewed and verified the saved results, then committed each worker's owned changes within its branch and cherry-picked sequentially to main.

| Task | Worker branch commit | Integrated main commit | Independent evidence result |
| --- | --- | --- | --- |
| M1-002 / V6 pefile warnings | `d1668fd72ece9a571cf1922ed39056c1c24b1f97` | **`a4fac10`** | Five synthetic checks passed; exact-build audit exit 0 |
| M2-001 / Click-to-Move | `40554843379ea937321c13f115554ec950fbd759` | **`a7d2c4e`** | 25 regions, 971 instructions, 55 selected assembly rows verified |
| M2-002 / Follow and cancellation | `2042ebc592a533b5bdf463e5e8e0ff49270481d6` | **`37a244a`** | 25 regions, 3,217 rows and seven call sequences verified |
| M3-002 / Collision | `21a1d204dc7560adcba2276d381caf9767779097` | **`b023d66`** | 12 regions, 613 rows, two leaf windows and ten data reads verified |

The original worker reports remain in `docs/agents/`. The Manager completed the Collision Markdown handoff after its worker stopped. No out-of-lane changes were accepted. Git `diff --check` passed for all owned diffs after one trailing blank line was removed.

## Meaningful findings

**V6 warnings:** The exact executable has **302,344 runtime function entries**, **52,424 chain entries**, and **51,599 unique chain-info objects**. There are **631 reused chain objects** across **1,456 runtime entries**: the **825 extra references** exactly account for the 825 pefile duplicate-parent warnings. Observed reassignment targets were the same parent, with **zero conflicts in this build**. This diagnoses the warnings but does **not** prove every raw unwind chain's full 12-byte parent triple or global CFG coverage. Original pefile was not modified.

**C2M:** The earlier candidate destination data flow is stronger: the separate `state+0x70/+0x78` pair is populated through a **resource-backed auxiliary object factory** and reference-counted assignment, rather than an observed route array. The existing destination vector `state+0x60/+0x68` remains the directly observed steering input. The resource object's actual role and current-player ownership remain unresolved. **Do not call +0x70 a recovered navmesh route.**

**Follow:** Selected normal-input action IDs pass through follow-state clearing (`0x534200`) and separate C2M-state clearing (`0x534990`), which can also clean up an associated object/child callback range. Bit clearing, message emission or cleanup alone do **not** prove in-game movement has stopped. Physical key/gesture mappings remain unqualified.

**Collision:** A native phantom-cast path uses filtering and two collector implementations. An all-hit collector stores **0x40-byte records** sorted on a scalar at `+0x1C`; a closest-contact collector retains a smaller scalar and copies two vectors. Output behavior differs between all-hit and external collector branches. Treating every caller scalar as a uniform hit fraction is rejected. Player walkability/clearance, coordinate frame, cast layer values and native route linkage remain unresolved.

All addresses above refer to the same qualified native executable SHA-256 `7c356c9dde9e12fcbff3c08d953b0630b48b1510a0ffb36e4ec164606e7b17bd`, preferred static base `0x140000000`.

## Post-merge verification and provenance

A normal rerun on integrated `main` of the source-worker C2M verifier failed because the worker snapshot intentionally pins **older** versions of `AGENTS.md`, coordination docs, and the pre-hardening static helper; current `main` changed those files legitimately. The normal integrated Follow verifier failed a historical prefix hash due to **Git checkout LF/CRLF conversion**. **These two failures were not hidden or altered in original evidence.**

The Manager created `tools/verify-integrated-navigation.mjs`, which **passes** by:
- Comparing all **19 accepted lane-owned files** in the four original worker commits with their cherry-picked `main` blobs and the local checkout, using only documented LF/CRLF content equivalence.
- Verifying C2M's **13 recorded source hashes** against their **pinned historical Git versions** (or unchanged outside source files), including explicit raw/CRLF representation instead of silently replacing expected hashes.
- Checking the three C2M saved query artifacts and reconstructing the **original Follow JSON and Markdown historical prefixes** against their original hashes, with documented EOL handling.
- Rechecking the original qualified game executable SHA-256.

The independent lane verifiers all passed on their original worktrees **before** integration. `main` also independently passed the integrated Collision verifier and V6 synthetic checks, and the original shared synthetic regression suite passed **13/13**. The new integration verifier is for **provenance/payload**, not substitute proof of native semantic execution.

Run:
```powershell
& 'C:\Program Files\nodejs\node.exe' 'C:\work\rre\tools\verify-integrated-navigation.mjs'
& 'C:\work\rre\.venv\Scripts\python.exe' -B -m unittest discover -s 'C:\work\rre\tools\agents\validation' -p 'test_*.py' -v
```

## REA/Ghidra discovery

The 603-byte headerless x64 raw probe was rejected by REA Windows Ghidra P0 at admission (`capability_unavailable`, `target_format_unsupported`), confirming its contract supports native x64 PE but not raw x64. The Manager then re-used existing synthetic PE fixture-building code to create an isolated **2,560-byte PE** containing the validated 603-byte Rift dispatcher slice. Real REA 6.5.0/Ghidra 12.1.2 completed `resolve_containing_procedure` in about **19.6 seconds total**, exported **one evidence record**, and closed successfully. Provenance and limitations are in `docs/rea-small-pe-probe-2026-10-19.md`. A repeated preparation using a new isolated `--run-id` produced the same synthetic PE hash without modifying the original run.

**The full 60MB Rift executable still has not completed its prior whole-program Ghidra imports**; these small-PE results are not a working native pathfinding call.

## Remaining roadmap gates

- **M1-003 V7 provenance/versioning:** scheduled for a future narrow offline pass; the new integration verifier already illustrates immutable historical source recovery but does not yet provide a complete standardized per-run manifest.
- **M3-001 Pathfinding:** the dedicated pathfinding worktree retains **five preexisting untracked query JSON files**. Inspect and preserve those before any further pathfinding assignment. Type-7 handler registration/producer/player use remain unknown.
- **M4 Offline prototype harness:** blocked until further native interface qualification under M3 and the roadmap's selected gates.
- **M5 Live game trials:** require separate approval, identity-bound scene observation and a verified cancellation action; **T0 before T1 before T2**. No live trial took place.
- **M6 Target approach, M7 optimization:** deferred until preceding gates.

Codex CLI 0.163.0 reported the same quota exhaustion to every agent; no additional agents were respawned or promised to run asynchronously. The saved worktrees and exact Git history provide recoverable checkpoints for future eligible runs.
