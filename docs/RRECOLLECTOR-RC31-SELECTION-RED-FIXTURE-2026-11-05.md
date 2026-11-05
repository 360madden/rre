# RC-31 selection draw-state regression — November 5, 2026

**Task:** RC-31 / M7-UI. **State:** offline expected-red preparation only. Physical RRECollector v0.4.10 source/install remain frozen pending the strict RC-30 evidence gate or separate source-change authorization.

## Evidence and test result

- Fixture: tools/verify-rrecollector-rc31-selection-state.lua, SHA-256 35faa6e482100d4c6b116f79bc3553c57b003726b7282884f7dcf3b345f304b3.
- Frozen source: addons/RRECollector/ui.lua, SHA-256 36889ec1d848b723f602d0bf873250a5ef59b6e5e66d5288fc5608a96c6143aa.
- Real source fragments exercised: draw() selection/action-state rendering, Prev/Next callbacks, and runtime.ui.refresh(true). The mock UI contains synthetic records and in-memory button state; no RIFT process or live API was used.
- Job rre-rc31-selection-refresh-red-20261105-j6: exit 0, EXPECTED_RED_RC31_SELECTION 9/12 named scenarios; 3 PASS controls. Supervisor job rre-rc31-selection-final-failclosed-20261105-j7: exit 0 only after the later-fixed mode Lua child returned exit 1 with its expected unfixed-source diagnostic.
- The first local test invocation failed due to concatenated Lua long-bracket newline handling in the fixture; this was corrected before the recorded passing run. This is not a defect observed in the addon.

## Frozen-source findings

| Case | Count | Outcome |
| --- | ---: | --- |
| No selection should disable Pin and Check | 2 | RED |
| Existing known selection on another page should disable both | 2 | RED |
| Accepted Capture moves known selection off-page; disable both | 2 | RED |
| Prev/Next should clear selected ID and kind | 2 | RED |
| Real Check button must be stored as a redraw-accessible handle | 1 | RED |
| Valid visible known selection + Undo baseline controls | 3 | PASS |

**Coverage boundary:** The current fixture proves draw/navigation/control-handle defects, NOT complete action-guard acceptance. It does not execute actual Pin/Check click handlers. Current pinSelected() guards only by selectedKind and knownMap; the Check selected callback only checks selectedKind and selectedId, not visible page membership. A later click-handler regression must assert zero SavedVariables mutation or Detail call for a hidden known selection. The Check-handle source guard currently expects direct pinControls.check assignment; equivalent future wiring requires review rather than automatic green.

## Repeat offline

Run in Windows PowerShell, working directory C:\work\rre:

~~~powershell
$luaDir = 'C:\work\tools\cheat-engine-master\Cheat Engine\bin'
$priorPath = $env:Path
try {
  $env:Path = "$luaDir;$priorPath"
  & "$luaDir\lua_extra\lua.exe" .\tools\verify-rrecollector-rc31-selection-state.lua --expect-red
} finally {
  $env:Path = $priorPath
}
~~~

After separately authorized source edits, use --require-fixed and demand zero red cases, then independently test real Pin/Check click paths, package and source/installed parity, and physical version-matched UI behavior.

## Three priorities

1. P1: Build offline extracted Pin/Check handler test for an API-known ID hidden on another page; require no persisted change and no Detail call, plus visible-selection positive control.
2. P1: Later source fix uses one visible API-known predicate in both handlers and redraw; clear ID/kind on page navigation, retain Check handle, preserve original Undo baseline.
3. P2: Fix two-line captions and browser row fitting, followed by separately authorized physical UI visual checks.

No addon edits, deployment, RIFT input/process operations, SavedVariables writes, or desktop-capture quarantine changes occurred.
