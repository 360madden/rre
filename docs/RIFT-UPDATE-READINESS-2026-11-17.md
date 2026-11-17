# RRE physical-client update readiness — November 17, 2026 (AMD-DESKTOP)

Status at 06:56 EST: **PRE-UPDATE BUILD UNCHANGED; POST-UPDATE NOT YET QUALIFIED.** This document is a compatibility and rollback checkpoint, not authorization to update, launch, reload, control or inspect live RIFT. The only active potential live target is physical RIFT on its independently verified local computer; VMware access is excluded by AGENTS.md:3 and ROADMAP.md:1.

## Fresh pre-update evidence

- Host: machine-local Windows PowerShell verified `AMD-DESKTOP`; repository `C:\work\rre`; Workbridge 0.16.5-dev. Identity job `rre-nov17-update-host-identity-v1`, exit 0.
- Installed physical executable: `C:\Program Files (x86)\Glyph\Games\RIFT\Live\rift_x64.exe`; **60,493,640 bytes**, last-write UTC `2026-10-27T10:56:49.6396025Z`, SHA-256 **`1935a05c9db6d468e34e0055014a4a99c1b5afceb1695884e24600f5c20a4be8`**. Read-only hash job `rre-nov17-current-rift-pe-readonly-v1`, exit 0; it matches the current archived RRE static-source executable.
- Recoverable pre-update binary: `C:\work\RIFT-Build-Baselines\1935a05c9db6d468e34e0055014a4a99c1b5afceb1695884e24600f5c20a4be8\rift_x64.exe`; **60,493,640 bytes**, independently SHA-256-identical to the installed game executable. Read-only verification job `rre-nov17-baseline-rehash-v1`, exit 0. Preserve outside Git; do not overwrite or delete.
- Reuse the existing sibling project's read-only build guard: `C:\work\Soldier\scripts\Test-RiftClientBuild.ps1`. Independent reviewer executed it on AMD-DESKTOP at approximately 06:55 EST and observed **MATCH, exit 0**. Return codes documented by the existing script: **0 = same bytes; 2 = changed build; 3 = inspection/error**. Do not duplicate the script into RRE or modify Soldier.
- Source/installed `RRECollector`: v**0.4.21**, **11/11 source/installed-file hashes agree**, strict manifest pass; `node tools/verify-rrecollector-package.mjs --installed <physical AddOns/RRECollector path>`, job `rre-nov17-update-collector-parity-1`, exit 0. This proves **disk installation only**: last directly observed in-game toolbar and SavedVariables were **v0.4.20**; no v0.4.21 live load, capture or active RREC2 proof. Preserve verified **v0.4.20 rollback** at `artifacts/RRECollector-installed-v0420-AMD-DESKTOP-20261117-0015`; do not garbage-collect it. SC-629 remains pending, with no game input.
- Existing offline gates: `node tools/validate-roadmap.mjs` passed (47 tasks, 11 milestones, nine WA-006 pins, mutation negative control), job `rre-nov17-update-roadmap-validator-1`; `C:\Python314\python.exe -B tools\agents\collision\verify_wa006_wrapper_parent_route.py` passed 20 original-byte windows, 38 opcode anchors, 66 RAM-only negative controls, job `rre-nov17-update-wa006-source-gate-1`. **WA-006 acceptance remains false**; source success on the archived PE is not an updated-client/runtime assertion.

## Immediate post-update decision gate (no game interaction required)

1. Confirm the game updater has **finished**. Reverify actual computer and executable **path, length, last-write UTC and SHA-256**; do not assume the old process or file was replaced. From AMD-DESKTOP PowerShell, run:

   ```powershell
   & 'C:\work\Soldier\scripts\Test-RiftClientBuild.ps1'
   $LASTEXITCODE
   ```

2. **MATCH / exit 0:** the *executable bytes* still match the preserved baseline. Previously SHA-pinned static RVA/opcode evidence remains applicable only to those bytes, **not** proof of a still-valid running process epoch, in-game player identity, collision behavior, addon load, or server/asset compatibility. Recheck collector source/install hashes and offline test gates; obtain fresh live identity/scene evidence only under separate physical-client approval.
3. **CHANGED / exit 2:** **STOP reuse of all prior client-specific native RVAs, absolute pointers, pointer chains, vtables, offsets and source-byte signatures** in WA-006, WA-007, ROOT-001, C2M/spellcasting, RR2, Soldier or any live reader. Preserve the archived baseline and original evidence unchanged. Obtain a separately SHA-named read-only copy of the **new** executable outside Git, then use existing PE/Capstone/REA/Ghidra narrow analysis to requalify only the needed specific functions. Do not automatically change expected hashes or backfill old research to a new build; no broad Ghidra import.
4. **ERROR / exit 3 or missing file:** treat build identity as **unknown and blocked**. Diagnose file/path/permission without launching or modifying the game. No forced bypass, retry of side-effecting action, or old-offset fallback.
5. After **either** branch, check RRECollector's TOC/11 source hashes and physical installed files, and validate a fresh on-screen loaded version plus SavedVariables or active RREC2 only if an explicit owner-approved physical test becomes available. An update can reset, disable or change an addon despite an unchanged executable. RC-30/RC-88 remain stopped. Old v0.4.20 screenshots/save receipts are historical, not a current acceptance claim.

## Git, ownership and recovery

- At this checkpoint RRE `main` was four commits ahead of `origin/main`. A concurrent uncommitted ROOT-001 research edit and nine inherited untracked backup/probe entries were present; another independent read-only reviewer saw an additional RR2 discovery-handoff edit. **Preserve all these; do not stage or discard them as part of update preparation.** Stage only this new document after review and publish by normal non-force push; recheck working-tree/remote state immediately before and after.
- No RIFT updater, executable, UI, game input, process, VMware machine, installed addon or other repository was changed by this RRE update-preparation checkpoint.
- RRE/SC-629 physical acceptance and WA-006/ROOT-001 runtime conclusions remain explicitly **pending**. The decision-changing next fact is the **post-update physical executable SHA**.
