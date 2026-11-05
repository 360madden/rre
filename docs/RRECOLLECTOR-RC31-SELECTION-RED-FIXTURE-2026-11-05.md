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

**Coverage boundary:** The draw-state fixture proves draw/navigation/control-handle defects, NOT complete action-guard acceptance. It does not itself execute actual Pin/Check click handlers; the companion handler fixture described below now does so offline. Current pinSelected() guards only by selectedKind and knownMap; the Check selected callback only checks selectedKind and selectedId, not visible page membership. The companion extracted-handler regression below now asserts unchanged synthetic saved slots and zero apiCheck dispatch for a hidden known selection. The Check-handle source guard currently expects direct pinControls.check assignment; equivalent future wiring requires review rather than automatic green.

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

1. P1: Source-extracted Pin/Check hidden-selection regression is added offline (see below); keep its gate fail-closed through source revisions.
2. P1: Later source fix uses one visible API-known predicate in both handlers and redraw; clear ID/kind on page navigation, retain Check handle, preserve original Undo baseline.
3. P2: Fix two-line captions and browser row fitting, followed by separately authorized physical UI visual checks.

No addon edits, deployment, RIFT input/process operations, SavedVariables writes, or desktop-capture quarantine changes occurred.

## Companion real-handler offline regression (02:27 EST)

- Fixture: tools/verify-rrecollector-rc31-hidden-clicks.lua, SHA-256 d0c91c086490e15bf2ccf11d7c2215a7ef1257b9d7aecdc1d9a836fd19fa90d6. It extracts the actual pinSelected() and Check selected callback bodies from the frozen ui.lua into one mock with 16 known records, page 2, eight original saved slots, related research receipts, and a counted mock apiCheck() call.
- A01 known but hidden on page 2: source Pin changes saved storage/pin baseline (RED) and source Check calls Detail-style apiCheck for A01 (RED). A09 visible on page 2: Pin updates intended slot and Check makes exactly one API check with unrelated receipts preserved (PASS). No claim is made about a physical RIFT click or real API return.
- Final reviewed job rre-rc31-hidden-clicks-reviewed-20261105-m6: exit 0, EXPECTED_RED_RC31_HIDDEN_CLICKS 2/3 and a --require-fixed child exit 1 with the expected diagnostic. It also validates all eight saved-slot contents and references, the complete original in-session pin baseline, exact visible-slot persistence, and captures the chosen ID before invoking a handler. The earlier l1/l2/l7 jobs are historical baseline checks. Senior review further required visible-Pin in-memory/original-slot integrity and Check Undo-state invariants; those are now asserted. The combined RC-31 offline tests now expose 11 expected-red assertions over 15 scenarios, with four green controls; multiple assertions can reflect the same underlying defect.
- Production fix remains on hold behind RC-30. Future corrected handlers must prevent stored-slot mutation, pin-baseline creation and Detail calls from an off-page known selection while allowing visible known IDs. The fixed-version source-extraction fixture may need review if helper definitions are factored outside the captured callbacks.
