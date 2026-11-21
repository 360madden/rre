# RRECollector v0.4.23 — AMD-DESKTOP physical addon installation

**Saturday, November 21, 2026, 12:14–12:15 PM EST.** RRE repository `C:\work\rre`, Git `main` baseline `3617fd0f4b94f39e25a31d335ee4684861f84664`. Only installed **RRECollector** files were changed; the physical game process remained running but was not controlled or reloaded.

## Verified identity

- Host: `AMD-DESKTOP` (Workbridge `0.16.5-dev`).
- Physical RIFT window: PID `37676`, HWND `3541956`, not foreground before/after package copy; neither game nor OS was restarted.
- Source folder: `C:\work\rre\addons\RRECollector`.
- Installed folder: `C:\Users\mrkoo\OneDrive\Documents\RIFT\Interface\AddOns\RRECollector`.
- Installed preflight: TOC `0.4.21`, exactly eleven expected files. Source TOC `0.4.23` and twelve files, including new `units.lua`. No unexpected top-level installed files.
- Executable identity from earlier independent read-only audit: on-disk `rift_x64.exe` size 60,574,536, SHA-256 `df954b798331e18359be62a31cc74b49fc3f50b87385ebb080a5448256322c01`. This does not prove mapped-memory identity.

## Backup and deployment

1. Backed up the original eleven files to **`C:\work\rre\artifacts\rrecollector-v0421-backup-20261121-1214-est`**. Operation `rre20261121_collector_backup_1214_01`: exit 0, each original/backup SHA-256 matched **11/11**. A local `backup-manifest.json` records hashes. No overwrite of an existing backup.
2. Preserved the original destination directory and copied only RRECollector source files, with **`RiftAddon.toc` copied last**. Operation `rre20261121_collector_diskdeploy_1215_01`: exit 0, **12/12** source/install file hashes agree.
3. Independently ran the project's strict package verifier, operation `rre20261121_collector_parity_final_01`: exit 0; `{"package":"RRECollector","version":"0.4.23","manifest":"strict-pass","sources":12,"installedShaMatches":12,"runtimeUiVerified":false}`.
4. Ran `tools/audit-rrecollector-readiness.mjs` against original installed addon and original character SavedVariables; operation `rre20261121_collector_readiness_postdeploy_01`: exit 0, `sourceInstalledByteIdentical=true`, `installedVersionMatchesSource=true`, but `savedRootMatchesSource=false`. No source tree modifications or other addon copy.
5. Reopened installed TOC: version `0.4.23`; `Email` present; `RunOnStartup` has all ten modules in required order. Physical RIFT still visible via read-only window inventory (PID `37676`).

## Evidence boundaries

**Installed** is verified. **Loaded/executing v0.4.23** is **NOT** verified. No `/reloadui` or other game input was issued. The observed SavedVariables root remains `0.4.21`, latest accepted ability producer `0.4.20` seq 2 with 55 abilities, `memoryPublication.status=not-published`, with no `captureAttempt`/unit snapshots; these are old retained data, not failed v0.4.23 captures.

RC-30 Pin/Undo/Reload and RC-88 quest investigation remain user-stopped; the physical game's built-in `/reloadui` is not the RRECollector Pin/Undo/Reload investigation. No other RRE controls, input, native process memory, network datastream or VMware target were used.

## Operator acceptance steps (separate game action)

After confirming game ownership, when Joey wishes to load the new addon, a normal in-game `/reloadui` is sufficient (no full game or Windows restart). Check toolbar/startup console for `RRECollector v0.4.23`, then manually run `/rre status`, `/rre capture`, `/rre units` in a suitable playable scene. Save via a normal UI reload/logout, then compare original character SavedVariables: root and new captured versions, `captureAttempt`, unit receipt and sequence; `tools/export-rrecollector-units.mjs` is available for strict original-file export. Same-session native correlation requires a separately coordinated source/owner/UTC receipt; WA-006 remains blocked.

Rollback, if needed, requires a new deliberate operation: compare the backup manifest SHA-256 against all eleven originals and restore the eleven backed-up files to the same installed addon directory. Since v0.4.23 added `units.lua`, remove only that known new module during rollback (without touching other addons). Reload RIFT UI after restoration. **No rollback was performed.**

## Next priorities

- **P0** Verify in-game v0.4.23 startup and one successful manual `/rre units` response, preserving the old accepted ability snapshot.
- **P1** Verify persisted original SavedVariables, output complete and partial/error reasons through strict offline exporter; retain source hashes.
- **P2** Continue WA-006 matching against independently timestamped native evidence only after two genuine nonself Lua/API IDs are available.
