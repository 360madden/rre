# Ghidra lane: two startup timeouts and supported next routes

Research date: 2026-10-18. Branch: `research/nav-ghidra`. Base commit:
`c7815b762dbdfe4d681a96cd14a69f658668595c`. Scope: retained evidence and installed
source read-only; no REA/Ghidra launch, import, process inspection/control, game
input, installation/configuration change, or network operation in this pass.

## Finding

Both first analysis requests exhausted REA's **450,000 ms startup deadline before
the post-analysis bridge became ready**. Ghidra had imported the PE, applied seeds
and analyzer options, and entered whole-program auto-analysis. The precise slow
task, elapsed time per phase, CPU use, heap pressure and eventual completion time
are unknown. Neither log proves a deadlock, out-of-memory condition, or specific
analyzer defect. Changing the query address or requesting fewer results cannot
make this startup selective.

There is **no persisted project to resume from these two runs**: both recorded
runtime/project paths are absent on this inspection, and the installed launcher
uses `-import -readOnly -deleteProject` in a private temporary root. Ghidra's own
documentation says `-readOnly` imports are not saved. The exported REA snapshots
contain zero query entries and zero evidence records, not a Ghidra database.

Machine-readable evidence IDs, source SHA-256 values, ZIP entry hashes, methods,
uncertainties and the proposed test are in [ghidra.json](ghidra.json). IDs below
resolve there; installed-source line numbers refer to the inspected package.

## Identity and method

- Executable: `C:\Program Files (x86)\Glyph\Games\RIFT\Live\rift_x64.exe`.
  SHA-256 remeasured:
  `7c356c9dde9e12fcbff3c08d953b0630b48b1510a0ffb36e4ec164606e7b17bd`;
  size 59,963,840; preferred base `0x140000000`; x64 PE. [S01]
- Installed `rea-agents/package.json`: **6.5.0**. Installed Ghidra
  `application.properties`: **12.1.2**; saved profiles select Temurin 21.0.11.
  Saved diagnostics independently report provider 12.1.2. [S02, S03, S06, S07]
- Parsed the full nested JSON tool responses, compared their SHA-256 values with
  the tracked attempt records, and read installed JavaScript/Java and Ghidra
  source ZIP entries without extraction. No analysis engine was started. [S04-S19]
- Used existing saved static-helper output and preexisting `pefile` only to verify
  a proposed byte slice. No replacement instruction decoder was built or run.
  Baselines read: `docs/navigation-research-2026-10-18.md`,
  `docs/navigation-findings.json`, `docs/navigation-workflow.md`.

## Recorded execution evidence

| Attempt | First analysis operation | Query elapsed | Disabled analyzers | Outcome |
| --- | --- | --- | --- | --- |
| navigation-20261018-01 | `resolve_containing_procedure(0x1406873ef)`; RVA `0x6873ef` | 450,729 ms in response/status | Stack; Decompiler Parameter ID | `provider_timeout` |
| navigation-20261018-02 | `xrefs(0x142d51598)`; RVA `0x2d51598` | 450,717 ms | Same plus Decompiler Switch Analysis | `provider_timeout` |

For each nested response, `error.details.diagnostics` reports
`failure_kind=timeout`, `failure_message=Ghidra startup deadline elapsed`,
`diagnostic_truncated=false`, and null exit code/signal. Null fields do not prove
that the JVM exited normally. Full stdout was retained: 31,574 / 31,677 bytes;
stderr: 1,232 bytes each. [S06, S07]

In **both** stdout streams, line 12 reports headless startup (2,166 / 1,880 ms),
line 348 reports zero additional imported files, line 351 reports three seeds
(one function created, two existing), lines 352-353 run analyzer options, and
line 354 says `ANALYZING all memory and code`. No analysis-success report or bridge
script execution appears afterward. DLL export scanning occurred during loading;
zero additional imported files does not mean zero loader work. There are no
phase timestamps to quantify loading versus analysis. [S06, S07]

Attempt 1 ends with a decompiler-switch restart message. Attempt 2, with that
analyzer disabled, ends with two `Unprocessed TypeDescriptor` messages. Both also
log `Invalid PNG data at 1427560e8` (RVA `0x27560e8`). These messages identify work
encountered, not where the remaining seconds were spent. Ghidra's
`TypeDescriptorModel.isPermittedType()` logs the TypeDescriptor message at INFO
and returns false for a demangled type that is neither class nor struct; the
message itself is not an exception or evidence of an infinite loop. [S18]

Both exports and closes succeeded, with zero analysis records. The first tracked
attempt summary says 450,728 ms; its raw response/status say 450,729 ms. This
one-millisecond bookkeeping difference does not change the diagnosis. [S04-S07]

## What the installed code supports

| Route | Verified support | Consequence / limit |
| --- | --- | --- |
| Keep one successful REA session open | Provider client starts Ghidra once and routes subsequent operations through that client; `GhidraProviderClient.js:459-505`. | Reuses a warm **live analysis session**, once one exists. These failed sessions never reached readiness and were closed. |
| Resume these two imports | Launcher `GhidraLauncher.js:315-438` always constructs import/read-only/delete-project arguments; client cleanup removes private runtime roots at `GhidraClient.js:638-668`. Both recorded roots are absent. | No database from these runs is available. No persisted-project parameter or `-process` path was found in this launch/config contract. |
| Ghidra persisted project / no analysis | Installed `support/analyzeHeadlessREADME.html:175-194,274-287,324-332` documents `-process`, `-readOnly`, `-noanalysis`, per-file timeout; `HeadlessAnalyzer.java:1045-1098` shows analysis before post-scripts. | Supported by standalone Ghidra. It would need a separately authorized project workflow. It is not an exposed REA 6.5.0 launcher option; do not patch the installed launcher or relabel a JSON snapshot as a database. [S08, S10, S14, S16] |
| Disable named analyzers | `REA_GHIDRA_DISABLED_ANALYZERS`; options script checks analyzer existence, sets false, and reads false back. Profile commits the selected names. [S09, S11, S12] | Supported session-specific coverage tradeoff. The second run's options script completed with the third name. Seeds still precede default whole-program analysis. |
| RTTI ablation | Installed `RttiAnalyzer.java:41-70` names **Windows x86 PE RTTI Analyzer**, default enabled, applicable to Visual Studio/Clang PE. [S17] | A future profile could add exactly this name to the existing three. It removes useful RTTI/vtable metadata. The TypeDescriptor tail does **not** establish that this analyzer caused the timeout or was its only caller. |
| More time / heap | `REA_GHIDRA_STARTUP_TIMEOUT_MS` is the outer deadline; Windows `analyzeHeadless.bat` defaults to 2G and accepts `GHIDRA_HEADLESS_MAXMEM`. REA preserves selected environment but clears generic Java option variables. [S12, S13, S20, S21] | Exact effective historical heap and GC behavior were not recorded. More heap/time is speculative, not a diagnosed fix; do not increase contention across six workers. The existing runner also has a 550-second lifetime and separate request budgets. [S22] |
| Per-file timeout as partial-result escape | Ghidra supports `-analysisTimeoutPerFile`, but REA's launcher does not pass it; its handshake explicitly rejects `analysis_timed_out`. [S08, S15] | Adding that flag manually would not make partial analysis an accepted REA session. |
| Small raw input | `open_binary` accepts `format=raw-binary`, `architecture`, `entry_point`; `BinaryLoader` maps file offset zero there, and the pre-script disassembles/creates an entry before analysis. [S23-S26] | Supported smaller **input**, not function-only analysis of a PE. Raw x64 selects generic `gcc` compiler spec. It loses PE mappings, imports, unwind metadata, RTTI, distant bytes and Windows ABI assumptions. |

## Smallest recommended next test (proposed, not executed)

Keep the current offline helper route for navigation research. If the manager
wants to test REA recovery, use **one 603-byte raw dispatcher window**, not another
whole-program import or a third unchanged profile. This tests small-input bridge
readiness and basic procedure recovery; it does not diagnose the full PE's slow
analyzer or establish navigation behavior.

1. Recheck the original executable hash. Reuse the existing section reader / PE
   mapping to copy RVA `[0xf3fa4,0xf41ff)` into a new isolated scratch `.bin`,
   with lineage to the original SHA. File offset is `0xf33a4`; length 603;
   slice SHA-256 is
   `6f31c492e5028ed20758e711746dc3152406e6db9b0273336f2b5224d6636e8b`.
   This pass recomputed it from the PE and matched the saved static artifact. [S19]
2. Use the existing installed REA MCP client/session pattern and these canonical
   input fields (the proposed scratch path is deliberately not created here):

   ```json
   {"path":"C:\\work\\rre-worker-ghidra\\tools\\agents\\ghidra\\probe-f3fa4.bin","format":"raw-binary","architecture":"x86_64","entry_point":"0x1400f3fa4","provider_id":"ghidra"}
   ```

3. In that same session issue one
   `resolve_containing_procedure` request at `0x1400f3fa4`. Set the child-only
   startup budget to 60,000 ms, use a larger client request budget (75,000 ms),
   and a 120-second overall supervisor limit including cleanup. Clear the old
   PE seed file and analyzer-disable override for this raw probe; PE-specific
   names need not exist for a raw program. Do not change installation/settings.
   The existing `rea-session.mjs` rejects non-PE inputs, so it cannot run this
   request unchanged. A future lane-owned adaptation must retain its export,
   close and error-stop behavior rather than change the shared runner. [S22-S26]
4. Pass: readiness and a procedure result within budget, correct raw target hash,
   language/load address and nonempty evidence. Failure: preserve full diagnostic
   JSON and stop once; no automatic retry. Do not score external xref or route
   recovery as a requirement: those bytes are absent from this input.
5. Rollback: export diagnostics/evidence, call `close_binary`, close the owning
   stdio session, and verify the REA-owned temporary runtime is removed. Keep the
   scratch bytes and provenance locally until review; any later deletion must
   target only that exact scratch directory. No manual process termination or
   deletion of historical/shared projects. Escalate incomplete cleanup to the
   manager instead of starting another session.

Successful raw recovery would justify planning a separately approved, measured
PE analyzer-ablation or persistent standalone-Ghidra workflow. It would not prove
that removing RTTI, increasing heap, or waiting longer fixes full analysis.

## Validation and unanswered questions

Validated full-response hashes, exact executable hash/PE identity, slice lineage,
two empty snapshots/evidence bundles, source/ZIP entry hashes and report JSON.
`git diff --check` and lane-path review passed. No new import or runtime
performance test was performed, so the cause remains unresolved.

Local commit was attempted but staging failed before any commit: Git could not
create `C:/work/rre/.git/worktrees/rre-worker-ghidra/index.lock` (permission denied).
That metadata is outside this worktree's writable boundary. No permission
escalation, Git identity change, integration or push was attempted; both lane
files remain unstaged for the manager to stage and commit.

Unanswered: which analysis task consumes the budget; whether it is CPU work,
GC or blocking; how long full analysis would take; whether RTTI ablation helps;
whether the raw probe succeeds on this installation. No new native semantics,
game-world test, runnable pathfinding interface or in-game navigation success is
claimed. Historical custom proximity graphs, cached `+0xD8`, and rejected
player-centered bounds remain outside this diagnosis.
