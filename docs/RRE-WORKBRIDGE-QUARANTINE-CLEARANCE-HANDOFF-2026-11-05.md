# RRE → Workbridge GUI quarantine clearance handoff — 2026-11-05

**Status:** HANDOFF SAVED FOR FUTURE CONTROLLED RECOVERY. **Do not unlock now.**
**Scope:** Physical-PC RIFT and Workbridge desktop automation; no VMware/game input required to read or act on this document.
**Checkpoint date:** Thursday, November 5, 2026, America/New_York. This file is a newer supplement to [RC-32 / GUI-turn repair handoff](RRE-RC32-WORKBRIDGE-GUI-HANDOFF-2026-11-05.md), not a replacement for incident evidence.

## 1. Reconciled state before this write

- RRE Git `main` HEAD **`dc4e074ea471b2c53302edcf1fa00c09bb7cab19`**; no tracked modifications. Preserve nine pre-existing untracked entries: `docs/rc18-v042-host-backup-20261102/`, `docs/rc19-v043-host-backup-20261102/`, `docs/rc20-v044-host-backup-20261102/`, `docs/rc21-v045-host-backup-20261102/`, `docs/rc23-source-backup-20261102/`, `docs/rc23-v046-host-backup-20261102/`, `docs/rc32-v0410-host-backup-20261105/`, `docs/rea-raw-probe-profile-2026-10-18.json`, and `tools/agents/ghidra/prepare_raw_probe.py`.
- Workbridge Git `main` HEAD **`73366b3338253fb27c4e44aef9c822f586ffb34b`**. Sole tracked modification: unrelated, user/other-workstream-owned `scripts/freebuff-conpty-probe.py`; do not include it in a release, edit, stage, reset, or stash it.
- Fresh Workbridge diagnostics: `0.16.4-dev`, instance `8eeaffd2-4e11-4228-8bac-daa06449b08c`, PID **15064**, started `2026-11-05T15:27:35.161Z`, tunnel ready/control plane OK, **36/36 command slots available**, zero running jobs observed. Historical job inventory is **incomplete** at the 20,000-entry scan limit. These are command slots, not 36 AI reasoning agents.
- Physical RIFT/RRECollector **v0.4.11 source-to-installed SHA parity 10/10**, Joey's screenshot proves loaded `RRE v0.4.11 research` UI, subsequent character SavedVariables SHA `8321e9e3fa850c2b1500287cf72da4c0f4f29b47c1ad581b016a1de2a184c4ed` proves saved `addonVersion=0.4.11` and unchanged eight-slot fingerprint. **RC-32 real error/retry behavior remains pending**, as do RC-30 strict archival and RC-31 UI presentation. No new `/reloadui`, game restart, Windows reboot, or keyboard/mouse authorization is implied.

## 2. Exactly what remains quarantined

- Original guard: `C:\work\workbridge-mcp\.tools\desktop-evidence\desktop-input-turn.lock`.
- Matching sidecar: `C:\work\workbridge-mcp\.tools\desktop-evidence\desktop-turn-quarantine-8aed4916-1cf3-4100-bc1b-d56f2308585f.json`.
- Lease ID `8aed4916-1cf3-4100-bc1b-d56f2308585f`; request `rc18-physical-rift-screenshot-20261102-postinstall-b1`; acquired `2026-11-02T20:46:12.574Z`, old Workbridge owner PID **43508**, old physical-RIFT target PID **17412**.
- Nov 4 pinned historical SHA-256: guard `635a367e41b80f9ad76fa1097c2ca8ece090315dc05dbf65deb4ebbfb28636b0`; sidecar `f1b37ebbeca97b4351d719786beb8c93dc678b76170f7e1a32b04bdecf0750a0`. These are **reference pins**, not a future substitute for fresh file-identity/hash checks.
- Nov 5 read-only exact-pinned classifier `wb_gui_quarantine_live_readonly_20261105_01`: `OWNER_PID_NOT_PRESENT`, `releaseEligible:false`, `automaticRetryAllowed:false`, `priorActionOutcome:unknown`, `historicalTreeSettled:unverified`. It verified its expected guard pin and linked sidecar identity; absence of the old PID **does not prove screenshot success, child process-tree settlement, or safe removal**.
- **Both original files are untouched.** The old screenshot request must never be replayed or converted into a fabricated success receipt.

## 3. Source-only repairs completed (not deployed)

All six Workbridge code/report milestones were locally committed, with separate narrow tests:

| Commit | Verified repair |
| --- | --- |
| `c5676b9` | Quarantine sidecar independently vetoes three producers even if the original guard is missing; 38/38 targeted synthetic tests PASS. |
| `6ba12a8` | Fresh, read-only November 5 owner/lease classification documented. |
| `accee90` | Atomic `desktop-turn-admission.lock`: producer/maintenance exclusive entry and owner-checked release; 36/36 focused JS and 8/8 isolated compiled MCP tests PASS. |
| `74d50de` | Admission helper included in the **sealed staged runtime** and WB-001 closure checks; staging 55 pass/1 skip, updater 37/37, isolated MCP 8/8 PASS. |
| `b6dac1e` | C# DesktopProbe watchdog takes the same admission gate first; .NET 10 publish and normal/uncertain/foreign-lock synthetic checks PASS. |
| `d3e9851` | Standalone screenshot CLI requires current exact parent-owned admission and GUI-turn stamps; unowned launch denied, positive staged fake-backend child invoked once; combined 56 pass/1 skip. |

The five identified GUI-affecting entrypoints have source-level guards or verified parent-lease checking: MCP capture, VMware host capture, DesktopProbe action, C# watchdog, and standalone screenshot CLI. **The running Workbridge service still uses its previously installed runtime**. Git commits, synthetic tests, and a staged helper are not proof that every currently deployed process obeys the new gate.

Authoritative Workbridge report: `C:\work\workbridge-mcp\investigations\windows-desktop-automation\reports\gui-orphan-sidecar-veto-2026-11-05.md`.
Archival protocol (design, not executed): `...\reports\manual-gui-turn-archive-protocol-2026-11-04.md`.
Service upgrade/rollback instructions: `C:\work\workbridge-mcp\docs\updates.md` (WB-001).

## 4. Safe sequence to clear the quarantine — all gates mandatory

1. **Qualify a clean release first, without restarting:** Stage WB-001 from a clean, committed Workbridge source snapshot that excludes the dirty Freebuff script. Run all release gates, confirm the six-file sealed desktop closure and a recoverable prior-runtime backup/rollback path. Keep live `.local` owner and the November 2 artifacts unchanged.
2. **Get Joey's explicit approval for a controlled Workbridge runtime upgrade.** Coordinate a quiet maintenance window across chat/automation clients, avoid racing new jobs, apply the WB-001 updater and verify fresh hosted tools/service identity. It may stop/restart **Workbridge only**; it does **not** require RIFT or Windows restart. Do not silently issue even this service restart.
3. **Prove current admission coverage and quiescence:** Verify upgraded MCP + CLI producers, direct legacy scripts and C# watchdog all honor the same atomic gate; inventory present GUI turns, child processes, command jobs and ownership. A frozen chat instruction or a standalone `freeze.json` is not an adequate atomic gate. Abort on unknown running producer or unverified active GUI work.
4. **Ask Joey separately to authorize archival of this exact legacy lease** and acceptance that the original screenshot outcome stays **UNKNOWN**. Approval to update Workbridge is not approval to move or release the old guard/sidecar. Re-read the real files for present SHA-256, sizes, non-link identity, lease/request linkage, process inventory, and any extra quarantines; abort on any mismatch.
5. **Under an exclusive maintenance admission lease, archive reversibly.** Write durable byte-exact, checksum-verified backups and an append-only journal in a new same-volume recovery folder; rename **sidecar first while the original guard remains**, then rename the exact guard **last**, both without replacement; no deletion. On Windows, validate file-identity and no-replace rename behavior against disposable fixtures before live use. An interruption or ownership mismatch is **STOP**, not an automatic retry.
6. **Postcheck before dropping maintenance admission:** Confirm both originals are in the archive with their exact bytes/identities, original guard/sidecar names absent, no new claimant, no orphan sidecar or unexpected GUI action, and healthy Workbridge. Retain backups and history; record only archival success, never old screenshot success.
7. **Pilot later, separately:** Obtain authorization for a harmless, exact-target DesktopProbe/host screenshot; verify screenshot bytes, process/target identity and no unexpected focus/input. Only then consider a new RIFT-specific test. No additional RIFT `/reloadui` is currently authorized.

### Mandatory stop conditions

No validated WB-001 release; deployed legacy producer still bypasses admission; old/foreign active desktop turn; extra quarantine; hash/linkage/identity drift; owner PID reuse ambiguity; Win32 rename/archival failure; unexpected new claimant; or loss of maintenance admission: **stop, preserve evidence, and report**. Do not delete `.lock`, clear a sidecar by age, spoof an owner stamp, replay the old screenshot, use PowerShell SendKeys as a bypass, or restart RIFT/Windows.

## 5. Machine-readable resumption checkpoint

```json
{
  "schemaVersion": 1,
  "kind": "rre_workbridge_gui_quarantine_clearance_handoff",
  "asOfEasternDate": "2026-11-05",
  "rreHeadBeforeHandoff": "dc4e074ea471b2c53302edcf1fa00c09bb7cab19",
  "workbridgeSourceHead": "73366b3338253fb27c4e44aef9c822f586ffb34b",
  "workbridgeInstalledVersion": "0.16.4-dev",
  "workbridgeInstalledInstanceId": "8eeaffd2-4e11-4228-8bac-daa06449b08c",
  "workbridgeOwnerPidObserved": 15064,
  "workbridgeCommandSlotsAvailableObserved": 36,
  "quarantineLeaseId": "8aed4916-1cf3-4100-bc1b-d56f2308585f",
  "quarantineRequestId": "rc18-physical-rift-screenshot-20261102-postinstall-b1",
  "lastReadonlyClassification": "OWNER_PID_NOT_PRESENT",
  "lastReadonlyReleaseEligible": false,
  "originalScreenshotOutcome": "unknown",
  "originalGuardAndSidecarPreserved": true,
  "guiAdmissionSourceTests": "passed",
  "newGuiRuntimeDeployed": false,
  "wb001ReleaseQualified": false,
  "wb001UpgradeAuthorized": false,
  "exactLegacyQuarantineArchiveAuthorized": false,
  "gameReloadOrRestartAuthorizedNow": false,
  "rreCollectorLoadedVersion": "0.4.11",
  "rreCollectorPostLoadSavedVersion": "0.4.11",
  "rreRc32BehavioralAcceptance": "pending",
  "next": "clean_wb001_release_preparation_then_separate_operator_review"
}
```
