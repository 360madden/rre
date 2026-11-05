# RRECollector RC-32 physical-host installation receipt — November 5, 2026

**Status (updated 13:08 EST):** RRECollector v0.4.11 installed and 10/10 hash-verified on the physical PC, visibly loaded in Joey's operator screenshot, and now confirmed in a subsequent **v0.4.11 character SavedVariables receipt**. Specific RC-32 retry/startup behavior remains unverified in-game; do not infer fresh ability capture or RC-30 strict archival acceptance.

## Scope and source

- Repository: `C:\work\rre`, branch `main`, source HEAD `e883a0c689c6d945d3d7a41e72b08852e74e07b0`.
- Source: `addons/RRECollector/`; ten package files (eight Lua, README, TOC).
- Destination: `C:\Users\mrkoo\OneDrive\Documents\RIFT\Interface\AddOns\RRECollector`.
- Prior installed version: `0.4.10`; installed files version: `0.4.11`.
- Only the ten named RRECollector files were overwritten; `RiftAddon.toc` was copied last. No other addons, VMware guests, game executable, SavedVariables, settings, game input, UI reload, process restart, or reboot.

## Observed gate receipts

| Gate | Workbridge job ID | Result |
| --- | --- | --- |
| Strict source package | `rre_rc32_source_gate_20261105_01` | Exit 0; v0.4.11; 10 files |
| Candidate catalog tests | `rre_rc32_candidates_check_20261105_01` | Exit 0; 6/6 |
| V0.4.10 physical backup | `rre_rc32_host_backup_v0410_20261105_01` | Exit 0; 10 copies, hashes verified |
| Preinstall backup/source verification | `rre_rc32_preinstall_verify_20261105_01` | Exit 0; 10/10 host-to-backup, four pinned source hashes |
| File copy, TOC last | `rre_rc32_install_v0411_20261105_01` | Exit 0; ten installed, no runtime reload |
| Strict installed package verifier | `rre_rc32_host_parity_v0411_20261105_01` | Exit 0; **10/10 source-host SHA-256 matches**, v0.4.11 |

**Rollback backup:** `docs/rc32-v0410-host-backup-20261105/` contains ten original installed files and `backup-manifest.json`. Manifest SHA-256: `ce16383991e7fb196f2289d827ba3e77d25f36140c70f7ab440988f03d3e809c`. The backup is intact and intentionally untracked. Rollback must restore exactly these ten files with TOC last, verify original hashes from manifest, and ask before any reload.

Historical source validation from `b28fceb`: 167/167 Lua assertions passed; not rerun today. Today's package and candidate checks were freshly run.

## Runtime evidence — November 5, approximately 12:56 EST

- **Operator-submitted original PNG:** `image(20261105-175633).png`, 1910 × 1071, SHA-256 `a039bec9745ea7d596de3254fb7664a561a2cdaf060414e5aa44bfada470b19e` (ChatGPT attachment `libfile_61f0ca0d4c6c8191854cd414fc3da841`). Screenshot visibly shows the physical RIFT client in Sanguine Shores with Atank, addon title `RRE v0.4.11 research`, toolbar and eight icons, Known 69 / Static 96, browser and controls. No visible Lua error in the displayed chat. This is **direct UI-load evidence**, not a full RC-32 behavior test or process-hash receipt.
- **Fresh postreload SavedVariables read:** original character `RRECollector.lua` modified `2026-11-05T17:56:02.585Z`, 74,216 bytes, SHA-256 `773b6f1a67b06cca1051bcf5ed69ba505b9c37b99f0014aee8963831bc320528`. Read-only, expected-hash-pinned sanitized receipt job `rre_rc32_postreload_saved_receipt_20261105_01` exit 0: `addonVersion=0.4.10`, 69 known, 96 candidate entries (51 returned, 38 listed-not-queried, seven no-detail), eight valid distinct stored toolbar IDs, zero duplicates, fingerprint `b592926bdeaf9af039393efe956f32ee69cbdf9e7f13b9b0892d9c5333d9c160` unchanged.
- The persisted `0.4.10` is **consistent with the old session flushing before the newly loaded 0.4.11**. The screenshot proves v0.4.11 UI loaded, but a fresh `addonVersion=0.4.11` saved-file receipt remains pending. Do not rerun `/reloadui` without Joey's new approval; one previously approved reload has already occurred. No automated keyboard/mouse input, game process restart or OS reboot was performed.
- Workbridge desktop screenshot acquisition is still blocked by the pre-existing November 2 quarantined GUI turn (`UI_TURN_BUSY`), investigated separately under `workbridge-mcp/investigations/windows-desktop-automation/reports/`. Do not bypass or remove that lock as part of RRE deployment. This operator-provided PNG is the current visual evidence.

## Fresh post-load SavedVariables qualification — 13:07 EST

A previously unseen saved-file revision modified **2026-11-05 17:58:19.181Z** was SHA-bound and parsed **read-only** with `--expected-sha 8321e9e3fa850c2b1500287cf72da4c0f4f29b47c1ad581b016a1de2a184c4ed --require-version 0.4.11`. Workbridge job `rre_rc32_saved_v0411_20261105_1305_a1` exited **0**. The 74,216-byte file reports addonVersion **0.4.11**, 69 retained Known entries, 96 retained candidates (51 returned / 38 listed-not-queried / 7 no-detail), sequence 5 and **8/8 distinct, valid slots**. The eight-slot fingerprint still equals the earlier qualified baseline `b592926bdeaf9af039393efe956f32ee69cbdf9e7f13b9b0892d9c5333d9c160`. An independent Workbridge `file_info(hash=true)` recheck showed identical SHA and mtime after the read. A fresh read-only strict package check `rre_rc32_postload_pkg_parity_20261105_1309_a1` exited **0**, confirming source/host **10/10 SHA parity** on the installed v0.4.11 package.

The saved-file version now passes its **post-load version gate**, complementing Joey's already qualified v0.4.11 UI screenshot. It does **not** establish new Known/candidate capture freshness, writer PID, same-session association to the screenshot, or the RC-32 error/inconclusive behavior. No RIFT input, reload, process control, desktop lease alteration, SavedVariables modification or additional deployment occurred. Source-hashed sanitized details and limits: [v0.4.11 post-load receipt](RRECOLLECTOR-RC32-POSTLOAD-SAVED-2026-11-05.json).

## Remaining runtime and archival gates

- **PASS:** installed/source v0.4.11 hash parity, operator-visible loaded UI v0.4.11, and subsequent saved-file `addonVersion=0.4.11` with intact eight-slot fingerprint.
- **PENDING:** specific RC-32 failure/retry/startup behavior under real RIFT API responses; no freshness or event-delivery claim from retained saved records.
- **PENDING separately:** RC-30 strict A/B/C/D plus comparable same-trial pre-Pin evidence. Do not repeat Joey's completed Pin/Undo sequence for paperwork.
- **Authorization:** no further `/reloadui`, process restart, reboot, game input or desktop lease override without a new, separate Joey decision.

One RRE manager owned deployment; a separate read-only review identified no blocker.