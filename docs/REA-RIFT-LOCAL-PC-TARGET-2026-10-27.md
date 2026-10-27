# REA RIFT spellcasting — Physical-PC target policy (October 27, 2026)

**Authorized target:** the RIFT client installed and running on this physical Windows PC, **not either VMware lab**. REA owns this research. RiftReader2 and Workbridge retain their own development/coordination roadmaps. User explicitly requested local-target research and authorized the work on October 27, 2026.

## Confirmed host target

- Physical local executable: `C:\Program Files (x86)\Glyph\Games\RIFT\Live\rift_x64.exe`
- SHA-256: `1935a05c9db6d468e34e0055014a4a99c1b5afceb1695884e24600f5c20a4be8`
- File size: **60,493,640 bytes**, last modified **2026-10-27T10:56:49.6396025Z**.
- At read-only check **2026-10-27T13:21:39.2796550Z**, Windows WMI showed **one running local `rift_x64.exe` process**, **PID 66436**, executablePath **exactly the same local installed path**; reported process start time 2026-10-27 07:10:10 local. Process identity and PID are volatile and MUST be refreshed for later runtime claims. An executablePath match plus disk SHA authenticates the file used as source; it does not independently attest all mapped memory bytes or gameplay state.
- The original October 27 PE section inventory and source hashes remain recorded in [build inventory](REA-RIFT-BUILD-INVENTORY-2026-10-27.json).
- Read-only observation job `rea-hostlocal-pc-binary-process-20261027-02` passed, exit 0. Earlier same-purpose `rea-hostlocal-pc-binary-process-20261027-01` failed because this Windows CIM client returned an already-converted CreationDate instead of DMTF text; fixed in second request, no target impact.

## Effective workflow

1. **REA:** analyze this local installed PE and, if needed, bounded read-only local process identity/observation for confirmed source-linked questions. Keep one worker/command owner, no repeated long whole-client Ghidra imports, and commit source-backed conclusions plus concise handoff each milestone.
2. **No VMware requirement:** do not query, start, modify, transfer into, or use either Lab-1/Lab-2 for REA spellcasting research. Previously collected RR2 VM observations may be cited only as **historical old-build evidence**; they do not establish current PC ability inventory, GCD, role or spellbook.
3. **No cross-project changes:** REA does not edit RR2 source, build new Workbridge orchestration, or alter either project's roadmap to achieve local analysis. Existing installed REA 6.5.0, Ghidra 12.1.2, Capstone and Workbridge read-only transport are sufficient now.
4. **Static first; observe when useful:** PE strings/RVA/.pdata/Capstone are source evidence; precise game mechanics and live spellbook require PC-only current game data tied to exact process, role and event times. Do not infer server authority or GCD from static names.
5. **Authorization/stop conditions:** user granted permission for this endeavor, but REA does not need to issue game input, modify process memory, deploy an addon, or attach a debugger to prove the currently selected native descriptor hypothesis. If an action requires destructive game/system modification or an active-game interruption, avoid it when a read-only method can answer. No game input occurred in the target switch.
6. **Every Chat-mode checkpoint:** record local PE SHA, method, source RVAs/function-byte SHA, exact Workbridge jobs and outcomes. Commit each bounded finding. Old RVA reports stay historically pinned.

**Next active task: SC-401**, now specifically an offline/native analysis of the **host-local PE** plus exact local process identity only if decision-changing. The previously confirmed `Inspect.Ability.New.List` registration-data function `0x9b0376–0x9b0776` and its callees are candidates; source-backed link to actual ability enumeration is not yet proven. SC1 level learnability and SC3 GCD remain unresolved.

**This note supersedes the earlier VM-only build-compatibility warning for THIS REA workstream.** It does not change the safety or deployment requirements inside independently owned RiftReader2 and Workbridge projects.
