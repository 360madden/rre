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
