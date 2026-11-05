# RC-32 pre-gate regression fixtures — November 5, 2026

**Status:** Offline test preparation complete; **both reliability fixes remain UNIMPLEMENTED**. The physical-PC RRECollector addon **v0.4.10 is frozen and unchanged**. No RIFT inputs, addon deployment, game process access, SavedVariables writes, or quarantine release occurred.

## Source-extracted tests

| Fixture | Executed scenario count | Expected red on frozen source | Passing unchanged controls |
| --- | ---: | ---: | ---: |
| `tools/verify-rrecollector-rc32-candidate-preservation.lua` | 7 | 4 | 3 |
| `tools/verify-rrecollector-rc32-batch-bounds.lua` | 6 | 4 | 2 |

Both ran against the original source through the already-installed Windows Lua 5.3 executable with the companion DLL directory added **only to the child environment**. Each returned exit **0** in `--expect-red` mode because the exact known defects reproduced. This is an expected-red receipt, **not** a passing fixed-version gate.

- Candidate: prior useful result overwritten by all-error and partial-error Detail attempts; no-prior all-error and partial-error attempts erroneously classified as recorded. Successful Detail, error-free no-detail, and deferred paths remained green.
- Batch: original raw List table sent to Detail for duplicate, invalid, 513-ID and 1,025-entry inputs despite normalized bounds. Clean 69-ID and clean mixed map/array inputs remained green.
- Source code was **not modified** in `addons/RRECollector`; only the two RRE-owned test files and this documentation were created.

## Exact Windows job receipts

- `rre-rc32-red-candidate-20261105-01`: exit 0, `EXPECTED_RED_RC32_CANDIDATES 4/7`.
- `rre-rc32-red-batch-20261105-01`: exit 0, `EXPECTED_RED_RC32_BATCH 4/6`.
- Direct `lua.exe -v` without the companion DLL search path exited `3221225781`; tests succeeded when the existing `C:\work\tools\cheat-engine-master\Cheat Engine\bin` folder was prepended only to the launched Lua process PATH. No installation or global PATH edit.

### 01:10 EST negative-control gate (verified November 5)

An additional **fail-closed check of the unfixed-source mode** ran under Workbridge job `rre-rc32-requirefixed-negative-20261105-01` (PowerShell supervisor exit **0** only if both Lua children fail with the specified diagnostic). With only the existing Lua DLL folder prepended to the child PATH, `--require-fixed` returned **exit 1** for the candidate test and **exit 1** for the batch test. Both required diagnostics were observed: `candidate protection not yet implemented` and `batch cap not yet implemented`. The supervisor reported `CANDIDATE_FAIL_CLOSED=True` and `BATCH_FAIL_CLOSED=True`; its output was not truncated.

The frozen RRE source still hashes to `ui.lua` SHA-256 `36889ec1d848b723f602d0bf873250a5ef59b6e5e66d5288fc5608a96c6143aa`, `abilities.lua` SHA-256 `d181ba0061a5959474dd3487b41c114f631122375a8b67421817fd54fdc1c510`, and `main.lua` SHA-256 `3aca63c501686fca5ab6bef8a72d81e3b4fe9fdca4ca3558d379e0cf24a1e5c6`. Fixture source hashes: candidate `c620daa011f9c928ae2d4cdf18606f39bf7c5e61c4c1582624a9b7d5b6d99868` and batch `5b46567f8b66b16ccc627a088f84f50717f2f46784f9b01828482b6fa2577bd3`.

**This proves** the proposed future fixed-version test mode rejects the known frozen defects; an expected-red harness exit 0 cannot masquerade as fixed-version success. It **does not prove** corrected collector behavior, complete scenario coverage, live-game faults, RC-30 acceptance, or independent model approval. No FreeBuff worker was re-launched for already-reviewed fixed-prompt questions, and the physical addon remains untouched.

To rerun from Windows PowerShell in `C:\work\rre`:

```powershell
$luaDir = 'C:\work\tools\cheat-engine-master\Cheat Engine\bin'
$priorPath = $env:Path
try {
  $env:Path = "$luaDir;$priorPath"
  & "$luaDir\lua_extra\lua.exe" .\tools\verify-rrecollector-rc32-candidate-preservation.lua --expect-red
  & "$luaDir\lua_extra\lua.exe" .\tools\verify-rrecollector-rc32-batch-bounds.lua --expect-red
} finally {
  $env:Path = $priorPath
}
```

After an **authorized** source fix, replace `--expect-red` with `--require-fixed`; require **zero red cases**, then run existing Lua, TOC, source/hash and version-matched host gates. The command-line flag is read from `arg[1]`; non-red mode already requires zero failures.

## RC-30 next gate (not completed)

A read-only fresh Workbridge desktop-window inventory listed two VMware Workstation windows titled RIFT-Lab-1 and RIFT-Lab-2, but **no visible physical `rift_x64.exe` window**. This does not prove the game process is absent; it means a current physical-game window was not verified from this inventory. No screenshots or input were attempted. The separate `DESKTOP_TREE_UNSETTLED` capture lease remains owner-gated.

Use `docs/RRECOLLECTOR-RC30-OPERATOR-ACCEPTANCE-2026-11-03.md` for the physical operator's A→B→C→D sequence: record all eight current slot labels and v0.4.10, Pin a known ability once, Undo before reload and compare all eight, then Reload UI and obtain a fresh version-matched saved receipt. **Do not claim acceptance from the historical eight-slot saved file alone.** RC-31/32 source changes and v0.4.11 deployment remain gated until this trial is confirmed.
