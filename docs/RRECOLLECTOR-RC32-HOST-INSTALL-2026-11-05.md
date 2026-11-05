# RRECollector RC-32 physical-host installation receipt — November 5, 2026

**Status:** RRECollector v0.4.11 installed and hash-verified on the **physical Windows PC**. In-game v0.4.11 load/functionality remains unverified until Joey separately authorizes UI reload/restart and fresh runtime evidence.

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

## Pending runtime gate

1. Ask Joey before any `/reloadui`, restart, or reboot.
2. On approved normal addon load, obtain fresh physical RIFT v0.4.11 toolbar screenshot.
3. Read a version-matched character SavedVariables receipt without editing it.
4. Only then consider RC-32 live functional acceptance. RC-30's archival gap remains independently pending.

One RRE manager owned deployment; a separate read-only review identified no blocker.