# RC-32 pre-gate regression fixtures — November 5, 2026

**Current source-only status (11:31 EST):** RC-32 reliability guards are **IMPLEMENTED AND VERIFIED OFFLINE** in staged RRECollector **v0.4.11** repo source. The physical RIFT installation remains **v0.4.10**; no install, UI reload/input, SavedVariables write or live v0.4.11 claim. **RC-30 strict archival PENDING; RC-32 deployment/runtime pending**.

**Historical pre-gate status (superseded for repository source only):** Offline test preparation expanded; candidate replacement, startup retention and Detail batch safeguards were unimplemented on frozen v0.4.10. No earlier physical game or SavedVariables change occurred.

## November 5, 11:31 EST — source-integrated fixed-version evidence

- **Production change:** `abilities.lua` permits raw List batch Detail only when enumeration is complete and duplicate-free; `main.lua` preserves a prior candidate report and sequence for malformed/zero-query, any explicit Detail errors, or all-inconclusive tables, with bounded failed/incomplete diagnostics; startup rejects all-error, all-inconclusive and zero-query cache placeholders while retaining legacy nil-inconclusive-counter and valid no-detail negatives. No changes to `candidates.lua`, `ui.lua` or toolbar pins.
- **Verifications with real exits:** Workbridge `rre_rc32_full_offline_20261105_1129_v1` exit **0**, ten source-extracted Lua suites **167/167** synthetic checks, including RC-32 candidate **9/9**, startup **8/8** (two new scenarios: all-inconclusive cache refresh, legacy missing counter retain), batch **7/7** and previously green RC-30 interleaved Undo **36/36**. All eight addon Lua sources pass syntax-only loadfile checks. `rre_rc32_pkg_source_1125_v1` exit **0**, strict source manifest/version v0.4.11 with ten files, explicitly no installed parity/runtime proof. `rre_rc32_candidates_node_1125_v1` exit **0**, six catalog checks; `rre_rc32_code_board_1125_v1` exit **0**. Original expected-red 12/22 historical receipt has not been retroactively rewritten.
- **One fixture correction:** Original RC-30 mock claimed 57 successful queries but represented one listed control plus 57 unlisted queries, and omitted actual producer counters. The first post-fix prior-suite run failed at its 'successful candidate retry' assertion. The manager adjusted only its synthetic report to 58 queries, 51 returned, seven no-detail, zero errors and zero inconclusive, with 1/57 listed/unlisted query split. Re-run preserved its original 36/36 Undo checks. This was a mock-compatibility issue, not a proven RIFT defect.
- **Hashes/source scope:** `abilities.lua` 8536f486753899ba168f2368ec6be1e8e8bb6ade3979e1b34d4eae9cb9eb26bd, `main.lua` 7770b8a08b45ea91d750946bd4bbdb00e14178bcaf7dbd24c53e026a6edda34e, `core.lua` d1d40245e8056260dddb0b2ef8fab1fa495dd91d2da982c9cfa739de1d5b807f, `RiftAddon.toc` 83f9f1492b430f80a4a481569eab8649039d474827adddb12570b81497be756a; startup fixture 1ded37095ad97916a8268740e2e4fbe63f11bb5b8d3699265110830bc456a20d and RC-30 interleaved fixture 6233d0c4bc1ee127e18bd63741702795687ce201608a9518fc4a1a92dc53dfde.

**Still blocked:** No v0.4.11 host deployment, source/installed ten-file parity, version-matched screenshot, or new SavedVariables receipt; they require separate approval. RC-30 operator-functional exception authorizes offline source only, while strict archival remains open.


## November 5, 11:17 EST — offline source-only implementation authorized

**Joey-approved alternate dependency tier:** The completed operator-attested RC-30 Pin → Undo → Reload, A/B/D images and preserved eight-slot postreload SavedVariables support **RC-32 source edits and source-extracted tests on the RRE repository only**. Missing historical C/pre-Pin evidence remains unresolved; **RC-30 strict archival acceptance is not granted**. No installed addon updates, RIFT interaction or Reload UI, private SavedVariables changes, or RC-31 release. This section supersedes previous RC-32 source-hold language for offline repository changes alone.

The manager must record source/test hashes and real --require-fixed exits after editing; all pre-approval expected-red receipts below remain valid historical evidence, not post-fix results.

## November 5, 10:52 EST — Joey-approved all-inconclusive reliability requirement

**Decision:** Joey explicitly approved the additional RC-32 requirement. This resolves the **policy decision**, not the source implementation, RC-30 gating, or runtime verification. The previous requirement covered explicit Detail errors; this extends it to all-inconclusive Detail-table attempts. Treat it as a newly approved reliability behavior, **not retroactive evidence of a production defect**.

- **All-inconclusive definition:** at least one Detail was queried (`counts.queried > 0`) and **every queried Detail** resulted in `inconclusive-table` (`counts.inconclusiveTables == counts.queried`), e.g. `{}` lacking usable fields. Do not infer this solely from zero returned records.
- **With a valid prior:** preserve the entire successful `candidateLookup` (including its sequence) when a new attempt has explicit errors or is all-inconclusive. Keep unrelated `latest`, `probe`, and saved toolbar slots untouched.
- **Without a valid prior:** retain bounded attempt/error diagnostics, but do not label an all-inconclusive attempt `recorded` or advance a successful-report sequence.
- **Truthful negative control:** error-free `nil` / no-detail API results remain valid negative evidence and may replace the prior according to the existing contract. Distinguish these from empty/inconclusive tables and actual exceptions.
- **Evidence/gates:** existing source-extracted expected-red fixtures cover these new cases (candidate 6/9, startup 2/6, batch 4/7; combined **12/22 expected red, 10 controls green**). The nine-query all-inconclusive aggregate is synthetic. No source fix, independent live RIFT fault, installed addon change, or RC-30 acceptance is claimed; v0.4.10 remains frozen.

## November 5, 11:08 EST — source-qualified implementation map (design only; no addon edit)

The manager and independent read-only reviewer matched the approved contract to unchanged frozen v0.4.10 source hashes: `abilities.lua` `d181ba0061a5959474dd3487b41c114f631122375a8b67421817fd54fdc1c510`, `main.lua` `3aca63c501686fca5ab6bef8a72d81e3b4fe9fdca4ca3558d379e0cf24a1e5c6`, `candidates.lua` `f558b68cab4804f78bbff4d5d1c4a234a6973fbdce60c76d93be77b487c38e85`. Implement the following **only after the RC-30 dependency is separately resolved**:

1. **Bound batch Detail** (`abilities.lua:57–69`): gate `Detail(rawList)` behind `enumeration.apiAvailable and enumeration.enumerationComplete and enumeration.duplicates == 0`. Existing 1,024 raw / 512 accepted-ID caps make truncation fail `enumerationComplete`; the already-bounded scalar Detail loop handles duplicates, ignored, and oversize inputs. **Do not** redefine duplicate enumeration as incomplete: a fully recovered deduplicated scalar capture can still be complete.
2. **Protect candidate snapshot** (`main.lua:97–138`): before incrementing `candidateSequence` or replacing `candidateLookup`, validate numeric nonnegative producer counters and at least one query. `counts.errors > 0` is an explicit-error attempt; `counts.queried > 0 and counts.inconclusiveTables == counts.queried` is all-inconclusive. On either condition, retain any existing good report object and sequence, set a bounded `candidateAttempt` with `failed/detail-all-error` or `incomplete/detail-partial-error` or `incomplete/detail-all-inconclusive`, refresh UI, and return without `recorded` success. Also fail closed for zero-query/malformed counters. Keep `latest`, `probe`, and `toolbarSlots` unchanged. Genuine error-free nil/no-detail API negatives remain recordable.
3. **Reject invalid startup cache** (`main.lua:300–305`): retain a matching-catalog saved candidate report only if `apiReady`, positive valid queried count, fewer errors than queries, and fewer inconclusive tables than queries; otherwise retry with the existing bounded startup mechanism. Treat a missing historical `inconclusiveTables` counter as zero only when otherwise valid for backward compatibility. Do not delete the prior persisted report during a failed retry.

**Focused acceptance:** The existing *source-extracted* three Lua suites provide candidate 6/9, startup 2/6, batch 4/7 expected RED (12/22 total, ten controls green) on frozen source. After authorization and a scoped source fix, require each `--require-fixed` test to exit **0 with zero RED**, then run strict TOC/source checks, controlled RRECollector-only deployment (backup and TOC last), full source/host 10/10 parity, and fresh version-matched runtime evidence. `--expect-red` exit 0 alone is **not** a fixed-version pass.

**Gate review:** A bounded search of RRE artifacts and the authorized physical SavedVariables directory did not locate historical RC-30 screenshot C or same-trial pre-Pin receipt; the operator-attested A/B/D + postreload G1 evidence remains useful but **strict RC-30 is pending**. A future *two-tier* operator-functional-versus-strict-archival gate could unblock offline source integration **only with Joey’s explicit separate approval**. No dependency was changed in this design checkpoint. No source edit, deployment, game input or temporary shadow-patch run occurred.

## Source-extracted tests

| Fixture | Executed scenario count | Expected red on frozen source | Passing unchanged controls |
| --- | ---: | ---: | ---: |
| `tools/verify-rrecollector-rc32-candidate-preservation.lua` | 9 | 6 | 3 |
| `tools/verify-rrecollector-rc32-startup-retention.lua` | 6 | 2 | 4 |
| `tools/verify-rrecollector-rc32-batch-bounds.lua` | 7 | 4 | 3 |

All three run against the original source through the already-installed Windows Lua 5.3 executable with the companion DLL directory added **only to the child environment**. Each returned exit **0** in `--expect-red` mode because the exact named known defects reproduced. This is an expected-red receipt, **not** a passing fixed-version gate.

- Candidate: producer-shaped 39-listed/57-unlisted fixture with eight actual canaries, deep prior-preservation comparison and exact named-red checks. A useful prior is overwritten by all-error, partial-error and all-inconclusive Detail attempts; no-prior error/inconclusive attempts are misclassified as recorded. Error-free positives/negatives and deferral remain green. A no-prior partial report may be retained as explicitly incomplete evidence or discarded, but never labeled successful.
- Startup: source-extracted SavedVariables branch incorrectly retains all-error and zero-query saved reports for a matching catalog, suppressing refresh. Healthy positive, all-no-detail, listed-control-only and catalog-mismatch controls pass. It does not imply the game's SavedVariables are corrupt.
- Batch: real-source offline fixture now checks named failures, exact scalar call IDs/record sets, original batch argument identity, clean 512-ID inclusive boundary and clean mixed map/array input. Original raw List table is still sent to Detail for duplicate, invalid, 513-ID and 1,025-entry inputs despite normalized bounds. Three clean batch controls pass.
- Source code was **not modified** in `addons/RRECollector`; two existing offline fixtures were retained/hardened and a new startup fixture added. This documentation records the updated state.

### Additional bounded source-extracted all-inconclusive qualification (03:58 EST)

Workbridge job `rre_rc32_inconclusive_readonly_fixed_20261105_0353` exited **0** under Windows Lua 5.3. The experiment extracted the **real** `query(item, phase)` from `candidates.lua` SHA-256 `f558b68cab4804f78bbff4d5d1c4a234a6973fbdce60c76d93be77b487c38e85` and the **real** `runCandidateLookup(trigger)` from `main.lua` SHA-256 `3aca63c501686fca5ab6bef8a72d81e3b4fe9fdca4ca3558d379e0cf24a1e5c6`.

An empty table returned by mocked `Detail(id)` produced `inconclusive-table` with no exception. A synthetic nine-query `apiReady=true`, all-inconclusive candidate report then **overwrote a prior successful candidate report**, incremented its sequence from 7 to 8 and labeled the attempt `recorded`. Green controls showed error-free `no-detail` remains accepted and `apiReady=false` still preserves the prior report. The initial ad hoc run had a test-string concatenation error and was corrected before the passing run.

**Evidence limits:** The two real source functions ran offline but the nine-query report was constructed in memory; there is no observed RIFT outcome. This historical one-off did not prove real Detail calls return empty tables in this sequence or introduce a source fix. The later 04:38 EST test integrated the two new cases into the existing persisted candidate fixture; a separately reviewed fourth fixture is no longer necessary. Independent model review remains outstanding. Physical v0.4.10 source/install and SavedVariables were unchanged.

### 04:38 EST — permanent two-case all-inconclusive regression (source unchanged)

The pre-existing source-extracted candidate fixture now additionally extracts the **actual** `query(item, phase)` from frozen `candidates.lua` and checks that an empty `Detail(id)={}` classifies as `inconclusive-table` (one query, no exception, no `no-detail`). It then builds an explicit synthetic nine-query, all-inconclusive report and tests **two distinct failure cases**: overwrite of a useful prior report and false `recorded` success when no prior report exists. The 39-listed/57-unlisted, six-screenshot/two-soul canary shape and existing three clean controls remain intact. **The nine-query aggregate is synthetic**; the producer and consumer functions are source-extracted but their end-to-end live link was not observed.

The bounded Windows Lua 5.3 job `rre_rc32_persist_red_20261105_a1` exited **0**, reporting exactly **6/9 named expected-red scenarios**, 3 controls PASS and a separate successful producer classification assertion. The supervised fail-closed job `rre_rc32_persist_failclosed_20261105_a1` exited **0** only after the same fixture in `--require-fixed` mode returned exit **1** with `RC32 candidate protection not yet implemented (6 defects)`. The separate FreeBuff adapter preflight `rre_rc32_freebuff_check_20261105_a1` passed with `noModelExecution=true`; its eight reviewed fixed modes do not address this new RC-32 case, so no redundant or independent model review is claimed.

**Current source-tested scenario totals:** candidate 6 RED/9 (3 green), startup 2 RED/6 (4 green), batch 4 RED/7 (3 green): **12 known-red assertions / 22 scenarios, 10 controls green**. Frozen RRECollector source and physical installation remain unchanged. The new candidate test SHA-256 is `3ded35c2c428e83e1050f51ddd1f0b54fe9e2704d0ea9250168d55117ab20607`; the earlier 4/7 fixture/hash remains a historical receipt only. No live API observations or acceptance of RC-30/31/32 is implied.

## Exact Windows job receipts

- `rre-rc32-red-candidate-20261105-01`: exit 0, `EXPECTED_RED_RC32_CANDIDATES 4/7`.
- `rre-rc32-red-batch-20261105-01`: exit 0, `EXPECTED_RED_RC32_BATCH 4/6`.
- `rre-rc32-candidate-strong-red-20261105-b5`: exit 0, `EXPECTED_RED_RC32_CANDIDATES 4/7 named scenarios` (revised producer-shaped fixture).
- `rre-rc32-startup-six-red-20261105-c3`: exit 0, `EXPECTED_RED_RC32_STARTUP 2/6` (new startup branch fixture).
- `rre-rc32-strengthened-failclosed-20261105-c4`: supervising exit 0 confirms both strengthened candidate and startup `--require-fixed` child processes exited 1 with their distinct expected diagnostics.
- `rre-rc32-batch-strong-final-20261105-h1`: exit 0, `EXPECTED_RED_RC32_BATCH 4/7 named scenarios`; same supervisor confirmed strengthened batch `--require-fixed` child exit 1 with expected diagnostic.
- Direct `lua.exe -v` without the companion DLL search path exited `3221225781`; tests succeeded when the existing `C:\work\tools\cheat-engine-master\Cheat Engine\bin` folder was prepended only to the launched Lua process PATH. No installation or global PATH edit.

### 01:10 EST negative-control gate (verified November 5)

An additional **fail-closed check of the unfixed-source mode** ran under Workbridge job `rre-rc32-requirefixed-negative-20261105-01` (PowerShell supervisor exit **0** only if both Lua children fail with the specified diagnostic). With only the existing Lua DLL folder prepended to the child PATH, `--require-fixed` returned **exit 1** for the candidate test and **exit 1** for the batch test. Both required diagnostics were observed: `candidate protection not yet implemented` and `batch cap not yet implemented`. The supervisor reported `CANDIDATE_FAIL_CLOSED=True` and `BATCH_FAIL_CLOSED=True`; its output was not truncated.

The frozen RRE source still hashes to `ui.lua` SHA-256 `36889ec1d848b723f602d0bf873250a5ef59b6e5e66d5288fc5608a96c6143aa`, `abilities.lua` SHA-256 `d181ba0061a5959474dd3487b41c114f631122375a8b67421817fd54fdc1c510`, and `main.lua` SHA-256 `3aca63c501686fca5ab6bef8a72d81e3b4fe9fdca4ca3558d379e0cf24a1e5c6`. Current fixture SHA-256: candidate `3ded35c2c428e83e1050f51ddd1f0b54fe9e2704d0ea9250168d55117ab20607` (prior 4/7 fixture: `47166c7cadd8cb7e5fea1a4332a1b3dfdb9561e346c57809104bae44e83b9094`), startup `284c48d43a89799e569e4d351f9e6b3fdde7f7e83b872c64501e5f27692d4169`, and batch `d988b1f7947294266ac47878ef2e8809716347566bd36f2604740a33107303a2`. Original batch fixture SHA `5b46567f8b66b16ccc627a088f84f50717f2f46784f9b01828482b6fa2577bd3` and original candidate fixture SHA `c620daa011f9c928ae2d4cdf18606f39bf7c5e61c4c1582624a9b7d5b6d99868` remains historical.

**This proves** the proposed future fixed-version test mode rejects the known frozen defects; an expected-red harness exit 0 cannot masquerade as fixed-version success. It **does not prove** corrected collector behavior, complete scenario coverage, live-game faults, RC-30 acceptance, or independent model approval. No FreeBuff worker was re-launched for already-reviewed fixed-prompt questions, and the physical addon remains untouched.

To rerun from Windows PowerShell in `C:\work\rre`:

```powershell
$luaDir = 'C:\work\tools\cheat-engine-master\Cheat Engine\bin'
$priorPath = $env:Path
try {
  $env:Path = "$luaDir;$priorPath"
  & "$luaDir\lua_extra\lua.exe" .\tools\verify-rrecollector-rc32-candidate-preservation.lua --expect-red
  & "$luaDir\lua_extra\lua.exe" .\tools\verify-rrecollector-rc32-startup-retention.lua --expect-red
  & "$luaDir\lua_extra\lua.exe" .\tools\verify-rrecollector-rc32-batch-bounds.lua --expect-red
} finally {
  $env:Path = $priorPath
}
```

After an **authorized** source fix, replace `--expect-red` with `--require-fixed`; require **zero red cases**, then run existing Lua, TOC, source/hash and version-matched host gates. The command-line flag is read from `arg[1]`; non-red mode already requires zero failures.

## RC-30 next gate (not completed)

The November 5 physical `rift_x64` window was subsequently identified by read-only Workbridge detection, and Joey supplied live v0.4.10 screenshots and confirmed that Pin → Undo → Reload UI occurred. A redacted fresh post-reload SavedVariables receipt proves the original eight-slot fingerprint persisted. These later observations supersede the earlier negative window inventory, but do not establish the missing standalone pre-reload Undo screenshot or same-trial pre-Pin saved fingerprint. See `docs/RRECOLLECTOR-RC30-OPERATOR-ACCEPTANCE-2026-11-03.md` and `docs/RRECOLLECTOR-RC30-POSTRELOAD-SAVED-2026-11-05.json`.

**Strict RC-30 gate remains pending, with operator success supported and archival comparison incomplete.** Do not ask Joey to repeat the gameplay trial solely to repair the assistant's prior sequencing error. RC-31/32 addon source changes and a new deployment remain gated. `DESKTOP_TREE_UNSETTLED` remains owner-gated; no RRE-initiated game input occurred.
