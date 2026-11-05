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

## Six-name caption-identity collision regression (02:38 EST)

- Fixture: `tools/verify-rrecollector-rc31-caption-collisions.lua`, SHA-256 `1e2176768cdaec03b83967be69d53c261136b6afea9521ea666676280164cab6`. It source-extracts the actual `RC25-CAPTIONS` formatter from frozen `ui.lua` (SHA `36889ec1d848b723f602d0bf873250a5ef59b6e5e66d5288fc5608a96c6143aa`) and loads the intact 96-entry `candidate_catalog.lua` (SHA `10dddab8779fdb6253fa372ca47632c2396e1d3a15edddb40c17c495bd3adccd`) with unique-ID validation. All test captions are synthesized offline under the existing RC-25 **6px-per-glyph / 46px-line** mock, not observed RIFT pixels.
- The real distinct catalog entries **Shield of the Chosen / Hero / Vengeful** all produce `Shield | of t...`; **Way of the Mountain / River / Wind** all produce `Way of | the ...`. These are two named expected-RED *groups* (four duplicate comparisons), not six separate addon defects. Three controls pass: all six captions fit the mock width, a short word is preserved, and distinct short names remain distinct.
- Windows Lua 5.3 job `rre-rc31-caption-collision-reviewed-20261105-n7` passed `--expect-red` exactly **2/5**, and a supervised `--require-fixed` child failed with the correct 2-group collision diagnostic (exit 1). Existing green `tools/verify-rrecollector-ui-captions.lua` remains untouched and passed **9 RC-25 assertions** in job `rre-rc31-caption-rc25-green-20261105-n8`.
- **Coverage boundary:** A future RC-31 fix still needs omission markers, qualifier retention, UTF-8/word order, full hover identity, long browser-row measured fitting, and later physical visual acceptance. Do not require different captions for identical full names appearing under different souls (e.g., Building Fury). No addon source, deployment, RIFT input or SavedVariables changes occurred.

## Duplicate API-known browser labels versus underlying identity (06:45 EST)

- A prior bounded audit of 69 historically API-known records found **four distinct `Changing Role` IDs** with the same user-facing browser label `[API] Changing Role   [Other]`. This alone does not establish wrong-ID selection.
- New persistent fixture `tools/verify-rrecollector-rc31-browser-duplicate-identity.lua` (SHA-256 `7e95238ca3378a282defbddbca348630481afe2e2052aebae051b79bd2f51901`) source-extracts the frozen `ui.lua` browser-row rendering loop, `selectAt()`, `selectedText()`, `pinSelected()` and `undoPins()` at UI SHA-256 `36889ec1d848b723f602d0bf873250a5ef59b6e5e66d5288fc5608a96c6143aa`.
- Under four **synthetic, distinct IDs with the same Changing Role name and Other source**, all four rendered labels are identical, but choosing each row retains its particular ID in the detail panel and pinned slot. Undo restores all eight baseline positions, the original saved-slot **table reference**, the next Pin target and a cleared session Undo baseline. This confirms source-extracted **ID-keyed routing under the mock**, rather than a demonstrated identity swap. It does not validate any current saved record's exact ID or a live mouse event.
- Workbridge job `rre_rc31_dup_id_persist_tests_20261105_d1` exit **0**: `--expect-red` reported **1/5** label-ambiguity group expected RED and **4/4** independent ID/Detail/Pin/Undo controls PASS; `--require-fixed` independently exited **1** with its expected duplicate-label diagnostic. The first two *ephemeral harness* attempts had missing-local/mock-table errors and were corrected before this persistent fixture and test run. No source-code defect or crash in RIFT was observed from those harness errors.
- RC-31 documented offline inventory is now **14 expected-red groups / 25 scenarios** (11 PASS controls) across prior draw/handler/caption coverage plus this new identity discriminator. This is not a fixed-version gate PASS or proof of actual font metrics, current runtime identity, visual usability, or RC-30 operator acceptance.
- After explicit future production authorization, prefer **distinguishable user-visible row qualifiers** while preserving the existing ID-keyed selection contract. The mock fails closed if future source refactoring breaks extraction; review any such changes instead of declaring the behavior fixed automatically. Physical v0.4.10 source/install and SavedVariables remain untouched.
