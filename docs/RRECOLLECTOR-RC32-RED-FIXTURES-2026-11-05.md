# RC-32 pre-gate regression fixtures — November 5, 2026

**Status:** Offline test preparation expanded; **candidate replacement, startup retention and Detail batch safeguards remain UNIMPLEMENTED**. The physical-PC RRECollector addon **v0.4.10 is frozen and unchanged**. No RIFT inputs, addon deployment, game process access, SavedVariables writes, or quarantine release occurred.

## Source-extracted tests

| Fixture | Executed scenario count | Expected red on frozen source | Passing unchanged controls |
| --- | ---: | ---: | ---: |
| `tools/verify-rrecollector-rc32-candidate-preservation.lua` | 7 | 4 | 3 |
| `tools/verify-rrecollector-rc32-startup-retention.lua` | 6 | 2 | 4 |
| `tools/verify-rrecollector-rc32-batch-bounds.lua` | 7 | 4 | 3 |

All three run against the original source through the already-installed Windows Lua 5.3 executable with the companion DLL directory added **only to the child environment**. Each returned exit **0** in `--expect-red` mode because the exact named known defects reproduced. This is an expected-red receipt, **not** a passing fixed-version gate.

- Candidate: producer-shaped 39-listed/57-unlisted fixture with eight actual canaries, deep prior-preservation comparison and exact named-red checks. A useful prior is overwritten by all-error and partial-error Detail attempts; no-prior error attempts are misclassified as recorded. Error-free positives/negatives and deferral remain green. A no-prior partial report may be retained as explicitly incomplete evidence or discarded, but never labeled successful.
- Startup: source-extracted SavedVariables branch incorrectly retains all-error and zero-query saved reports for a matching catalog, suppressing refresh. Healthy positive, all-no-detail, listed-control-only and catalog-mismatch controls pass. It does not imply the game's SavedVariables are corrupt.
- Batch: real-source offline fixture now checks named failures, exact scalar call IDs/record sets, original batch argument identity, clean 512-ID inclusive boundary and clean mixed map/array input. Original raw List table is still sent to Detail for duplicate, invalid, 513-ID and 1,025-entry inputs despite normalized bounds. Three clean batch controls pass.
- Source code was **not modified** in `addons/RRECollector`; two existing offline fixtures were retained/hardened and a new startup fixture added. This documentation records the updated state.

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

The frozen RRE source still hashes to `ui.lua` SHA-256 `36889ec1d848b723f602d0bf873250a5ef59b6e5e66d5288fc5608a96c6143aa`, `abilities.lua` SHA-256 `d181ba0061a5959474dd3487b41c114f631122375a8b67421817fd54fdc1c510`, and `main.lua` SHA-256 `3aca63c501686fca5ab6bef8a72d81e3b4fe9fdca4ca3558d379e0cf24a1e5c6`. Current fixture SHA-256: candidate `47166c7cadd8cb7e5fea1a4332a1b3dfdb9561e346c57809104bae44e83b9094`, startup `284c48d43a89799e569e4d351f9e6b3fdde7f7e83b872c64501e5f27692d4169`, and batch `d988b1f7947294266ac47878ef2e8809716347566bd36f2604740a33107303a2`. Original batch fixture SHA `5b46567f8b66b16ccc627a088f84f50717f2f46784f9b01828482b6fa2577bd3` and original candidate fixture SHA `c620daa011f9c928ae2d4cdf18606f39bf7c5e61c4c1582624a9b7d5b6d99868` remains historical.

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
