# RRE / Workbridge GUI-turn repair handoff — November 5, 2026

**Purpose:** Durable pause/resume checkpoint created at Joey's request **before** beginning Workbridge desktop-lock repair. Preserve current RRECollector v0.4.11 runtime progress, the outstanding GUI quarantine, cross-repository ownership and the exact safe recovery route. This document does **not** authorize removing the current lock, changing Workbridge service state, sending game input, or another UI reload.

## Verified RRE state

- Repository `C:\work\rre` on `main`; fresh HEAD `4cff3cc3713e18645c35f629d78f715587efa957` (Nov 5, 12:59:25 EST). Fresh `git status`: **no tracked changes**, nine untracked entries (eight pre-existing user-owned items and one deliberate v0.4.10 rollback backup). Do not clean or overwrite them.
- **RRECollector physical-host installation:** v0.4.11 copied to `C:\Users\mrkoo\OneDrive\Documents\RIFT\Interface\AddOns\RRECollector`, 10/10 strict source/host SHA-256 parity, TOC copied last. Source-only RC-32 fixes previously passed 167/167 Lua assertions; package and six candidate checks freshly passed on install. Installation receipt: [RC32 HOST INSTALL](RRECOLLECTOR-RC32-HOST-INSTALL-2026-11-05.md). Documentation commits `8f38e8b` and `4cff3cc`.
- **Rollback:** `docs/rc32-v0410-host-backup-20261105/` has all ten original installed v0.4.10 files and SHA manifest; manifest SHA-256 `ce16383991e7fb196f2289d827ba3e77d25f36140c70f7ab440988f03d3e809c`. It is intentionally untracked; preserve intact.
- **Live UI evidence:** Joey's original screenshot `image(20261105-175633).png`, attachment `libfile_61f0ca0d4c6c8191854cd414fc3da841`, SHA-256 `a039bec9745ea7d596de3254fb7664a561a2cdaf060414e5aa44bfada470b19e`, 1910×1071, visibly shows physical RIFT/Atank in Sanguine Shores and addon title `RRE v0.4.11 research`, eight toolbar icons, Known 69 / Static 96, browser buttons. **Loaded-v0.4.11 UI PASS; live RC-32 behavior not fully tested.**
- **SavedVariables evidence:** read-only SHA-bound receipt `rre_rc32_postreload_saved_receipt_20261105_01` exit 0 on original character file modified 2026-11-05T17:56:02.585Z; source SHA `773b6f1a67b06cca1051bcf5ed69ba505b9c37b99f0014aee8963831bc320528`. Saved `addonVersion=0.4.10` (expected possibility when old session flushes before new load), Known 69, Candidate 96, eight valid distinct pins, original fingerprint unchanged `b592926bdeaf9af039393efe956f32ee69cbdf9e7f13b9b0892d9c5333d9c160`.
- **Gates:** v0.4.11 live UI load verified; a new v0.4.11 SavedVariables flush and specific RC-32 failure/retry behavior remain pending. RC-30 strict archival evidence remains separately pending. RC-31 button-affordance fixes not deployed. Do not repeat old RC-30 Pin→Undo merely to recreate the missing pre-reload screenshot.
- **Game boundary:** Joey authorized one `/reloadui`; Workbridge did not send it. The user supplied post-transition screenshot. Do **not** issue any further UI reload, game restart or Windows reboot without asking. No automated game input has occurred in this recovery work.

## Workbridge desktop-turn incident

- Workbridge 0.16.4-dev service/tunnel was recently healthy; `desktop_windows` and exact `desktop_inspect` worked read-only. The Nov 5 exact-window screenshot requests for physical RIFT PID 32156/HWND 462734 returned `UI_TURN_BUSY`; UIA inspection confirmed RIFT window existence, not in-game content.
- Lock path: `C:\work\workbridge-mcp\.tools\desktop-evidence\desktop-input-turn.lock`; matching quarantine sidecar for lease `8aed4916-1cf3-4100-bc1b-d56f2308585f`. Original request ID `rc18-physical-rift-screenshot-20261102-postinstall-b1`, acquired 2026-11-02T20:46:12.574Z, targeted old physical RIFT PID 17412. Source `src/desktop-registration.ts:36–140` uses exclusive `open('wx')` and rejects a present lock as `UI_TURN_BUSY`; it preserves lock + sidecar on uncertain screenshot worker-tree settlement.
- November 4 documented historical lock SHA `635a367e41b80f9ad76fa1097c2ca8ece090315dc05dbf65deb4ebbfb28636b0` and sidecar SHA `f1b37ebbeca97b4351d719786beb8c93dc678b76170f7e1a32b04bdecf0750a0`. **These are historical reference hashes, not fresh November 5 hash verification.** Quarantine reason `DESKTOP_TREE_UNSETTLED`, processTreeSettlement unknown, automaticRetryAllowed false.
- The latest reports found no proven surviving old capture worker, but neither an original request-specific completion receipt nor historic private Job Object settlement. This is an *unknown historical outcome*, not proof of a live stuck worker or bad RIFT UI.
- Authoritative Workbridge documents:
  - `investigations/windows-desktop-automation/reports/desktopprobe-host-ops-preflight-2026-11-04.md`
  - `investigations/windows-desktop-automation/reports/gui-turn-live-classification-2026-11-04.md`
  - `investigations/windows-desktop-automation/reports/manual-gui-turn-archive-protocol-2026-11-04.md` (design only)
- **Safety stop:** Do not delete/rename the lock or sidecar, invent a release receipt, retry the unknown old screenshot, or bypass the lease with SendKeys/another GUI producer. The existing recovery design requires an enforceable cross-producer GUI admission freeze (not implemented), exact current owner/lease/hash reconciliation, durable byte-exact archive, sidecar-first then guard-last controlled release, independent postchecks and a new explicit Joey decision. The original screenshot outcome must remain UNKNOWN.

## Next resumption — after this handoff is safely saved

1. **Read-only Workbridge preflight:** Read `C:\work\workbridge-mcp\AGENTS.md`; verify actual Git HEAD/status, worker owners, active jobs and scope. Check for other concurrent Workbridge development. Read the three incident reports and current source/tests without touching protected runtime state.
2. **Safe tooling repair lane:** Determine the smallest permanent cross-producer desktop admission/recovery improvement, with synthetic race/failure tests in a separate owned worktree or exclusive lane. Implement only if it can be isolated and verified; preserve all unrelated untracked material. Do not change service version, register a boot helper, or deploy a new input producer without explicit approval.
3. **Live lock release is a separate decision:** Before archival/unlock, present to Joey exactly what will be changed and the unresolved historical screenshot outcome. Obtain new approval and satisfy the reviewed technical gates. If current architecture cannot enforce the shared freeze, keep quarantine intact and report blocker.
4. **After tool recovery:** Verify harmless screenshot/focus capture on an exact current window under fresh ownership. RRE visual automation is not considered repaired from tests alone. Keep current RIFT game state and no-restart requirement.

## Machine-readable checkpoint

```json
{
  "schemaVersion": 1,
  "dateEastern": "2026-11-05",
  "project": "C:/work/rre",
  "rreHeadBeforeThisHandoff": "4cff3cc3713e18645c35f629d78f715587efa957",
  "trackedDirtyBeforeHandoff": false,
  "historicalUntrackedPreserve": 8,
  "newRollbackBackupUntracked": 1,
  "physicalInstalledAddon": "RRECollector 0.4.11",
  "installedPackageShaMatches": 10,
  "liveUiVersionScreenshot": "0.4.11",
  "liveUiProof": true,
  "savedVariablesVersion": "0.4.10",
  "savedV0411Receipt": false,
  "rc32RuntimeComplete": false,
  "workbridgeVersionLastObserved": "0.16.4-dev",
  "workbridgeGuiLock": "quarantined",
  "workbridgeGuiError": "UI_TURN_BUSY",
  "oldScreenshotOutcome": "unknown_outcome",
  "guiLockReleaseAuthorized": false,
  "gameReloadOrRestartAuthorizedNow": false,
  "nextTask": "read_only_workbridge_preflight_then_safe_repair_tests"
}
```

## Later continuation — Thursday, November 5, 2026, 13:49 EST

The above snapshot is a **historical checkpoint from before tooling repair**.
Do not reinterpret its earlier pending gates as the latest status.

- **RRE post-load evidence advanced independently:** commit `d3c26398566e88685ce4e5037aede3a72ea579c9` qualified a read-only `addonVersion=0.4.11` SavedVariables receipt (file SHA `8321e9e3fa850c2b1500287cf72da4c0f4f29b47c1ad581b016a1de2a184c4ed`) and reverified 10/10 source/physical package hashes. The visible loaded UI v0.4.11 and the post-load saved-version gate now **PASS**. Specific RC-32 retry/failure behavior and RC-30 strict archival gates remain **PENDING**; no additional reload authorized.
- **Workbridge first repaired orphan sidecar veto:** `c5676b990930c68ced6b175cd8ea307d6dfeb724`, synthetic 38/38 pass.
- **Fresh Nov 5 read-only live classification:** `6ba12a807b11e7d24ce9f712c8e10086f736fa5e`, exact historical lock hash/lease/request pinned; result `OWNER_PID_NOT_PRESENT`, `releaseEligible:false`, prior action `unknown`. Workbridge current owner PID 15064, instance `8eeaffd2-4e11-4228-8bac-daa06449b08c`, version 0.16.4-dev, diagnostics healthy at observation.
- **Source-only shared admission gate:** `accee90fe2fb4d129d6894d6cb21ebfbbed8a388`. Atomic maintenance/producer lease, ownership-checked release, cross-producer synthetic tests.
- **Sealed desktop runtime packaging:** `74d50de8bc1c43aa4084652cc922171ffe4b42d7`, staged helper included and checked in updater; stage/baseline 55 pass, 1 skip, updater 37/37 pass, isolated MCP 8/8 pass.
- **C# watchdog gate:** `b6dac1ee0b196a72fa034619729cff4e9238e859`, .NET 10 publish plus normal/uncertain/foreign-lock synthetic checks pass.
- **Standalone capture CLI contained:** `d3e98516becf24c2c3ad78afbf1c7c0f356ffd16`. Exact parent-owned admission/GUI stamps required; independent CLI refused. Positive staged child using fake screenshot backend invoked once; combined 56 pass / 1 skip / 0 fail.
- **LIVE IS STILL BLOCKED:** All changes are Git source/doc changes, not a WB-001 deployed runtime. The original Nov 2 `desktop-input-turn.lock` and matching quarantine remain untouched, old screenshot settlement still UNKNOWN, and no GUI input/restart was performed.

### Updated machine-readable continuation

```json
{
  "schemaVersion": 1,
  "kind": "rre_workbridge_handoff_continuation",
  "dateEastern": "2026-11-05",
  "rrePostLoadSavedVersion": "0.4.11",
  "rrePostLoadVersionGate": "passed",
  "rreLiveRc32FailureBehavior": "pending",
  "workbridgeGuiSourceHardeningHead": "d3e98516becf24c2c3ad78afbf1c7c0f356ffd16",
  "workbridgeRuntimeUpgraded": false,
  "nov2GuiQuarantineRetained": true,
  "nov2PriorCaptureOutcome": "unknown",
  "guiReleaseEligible": false,
  "nextTasks": [
    "stage_and_qualify_wb001_release_without_restarting_running_service",
    "review_cross_producer_quiescence_and_live_owner_evidence",
    "request_joey_approval_for_runtime_upgrade_and_separate_exact_lease_archive"
  ],
  "gameReloadOrRestartAuthorizedNow": false
}
```
