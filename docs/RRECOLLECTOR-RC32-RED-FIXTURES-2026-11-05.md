# RC-32 pre-gate regression fixtures — November 5, 2026

**Status:** Offline test preparation expanded; **candidate replacement, startup retention and Detail batch safeguards remain UNIMPLEMENTED**. The physical-PC RRECollector addon **v0.4.10 is frozen and unchanged**. No RIFT inputs, addon deployment, game process access, SavedVariables writes, or quarantine release occurred.

## November 5, 10:52 EST — Joey-approved all-inconclusive reliability requirement

**Decision:** Joey explicitly approved the additional RC-32 requirement. This resolves the **policy decision**, not the source implementation, RC-30 gating, or runtime verification. The previous requirement covered explicit Detail errors; this extends it to all-inconclusive Detail-table attempts. Treat it as a newly approved reliability behavior, **not retroactive evidence of a production defect**.

- **All-inconclusive definition:** at least one Detail was queried (`counts.queried > 0`) and **every queried Detail** resulted in `inconclusive-table` (`counts.inconclusiveTables == counts.queried`), e.g. `{}` lacking usable fields. Do not infer this solely from zero returned records.
- **With a valid prior:** preserve the entire successful `candidateLookup` (including its sequence) when a new attempt has explicit errors or is all-inconclusive. Keep unrelated `latest`, `probe`, and saved toolbar slots untouched.
- **Without a valid prior:** retain bounded attempt/error diagnostics, but do not label an all-inconclusive attempt `recorded` or advance a successful-report sequence.
- **Truthful negative control:** error-free `nil` / no-detail API results remain valid negative evidence and may replace the prior according to the existing contract. Distinguish these from empty/inconclusive tables and actual exceptions.
- **Evidence/gates:** existing source-extracted expected-red fixtures cover these new cases (candidate 6/9, startup 2/6, batch 4/7; combined **12/22 expected red, 10 controls green**). The nine-query all-inconclusive aggregate is synthetic. No source fix, independent live RIFT fault, installed addon change, or RC-30 acceptance is claimed; v0.4.10 remains frozen.

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
