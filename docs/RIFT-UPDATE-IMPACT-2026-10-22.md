# RIFT update impact and requalification gate — October 22, 2026

**Status: PATCH SCOPE UNVERIFIED IN GUEST; native offsets and live movement must not be promoted to the updated session.** The user reported a game update on October 22. This is a **read-only compatibility checkpoint**, not a declaration of changed native code or a newly tested game session. It does not authorize game input, code injection, debugger attachment, control-host restart, guest installation, queue deletion, or an update to RR2's expected executable hash.

## Actual observations

- **Physical-host RIFT executable**, `C:\Program Files (x86)\Glyph\Games\RIFT\Live\rift_x64.exe`: SHA-256 `7c356c9dde9e12fcbff3c08d953b0630b48b1510a0ffb36e4ec164606e7b17bd`, **59,963,840 bytes**, on-disk last-write UTC **2026-09-29T12:04:29.2915369Z**. This exactly matches the historical RRE static research pin; it is **not** proof that the VM's guest game has the same bytes.
- A metadata-only recursive check of the physical-host `Live` directory found **zero files** with last-write UTC on or after October 21 00:00. That scope covers **this installation only**, not another launcher folder or the VMware guest's virtual disk.
- VMware `vmrun list` returned **one running VM**, `C:\rift modding\VMs\RIFT-Lab\RIFT-Lab.vmx` (RIFT-Lab-1). The physical host had one `vmware-vmx.exe` process (PID **31884**) with listener **127.0.0.1:5905** at the observation time. This establishes a running VM, **not** a running/foreground/playable RIFT client or its hash. PIDs and listeners are volatile.
- RR2's existing, unleased **read-only** `scripts/control_client.py --config artifacts/native-usability-20261020/host.json status` returned **WinError 10061, actively refused**. No ARM, capture, action or STOP was sent. This means the configured status endpoint was unreachable for this request—not that game startup, receiver health, guest build or patch application failed. Do not restart/deploy a host to make the check pass from the RRE lane.
- At the same host observation, selected RR2 host ports **49712/49713/49714** were not listed as listening. Existing RR2 connected/lease receipts from earlier October 22 are historical. RR2's worktree has extensive **other-owner uncommitted control/receiver-recovery changes**; preserve them. RRE main carried only the two known historical untracked raw-probe files before this documentation change.

No fresh guest `rift_x64.exe` bytes, current game version, addon telemetry receipt or in-world image was collected. No ASLR/pointer-chain, plugin, Lua, or native C2M result can be requalified from the host-install hash alone.

## Immediate compatibility gate before resuming NAV-002 or M5-T0

1. **P0 — Identify the updated game instance.** Ask which environment was updated (currently running RIFT-Lab-1 guest versus physical host/another instance). The presently observed physical-host install is unchanged. Preserve active VM and current queue evidence; do not clone, restart, delete, replace or retarget either system merely to inspect a patch.
2. **P1 — Qualify the executable actually used by guest RIFT.** Use an authorized **guest-local read-only file hash** or an existing verified RR2 readback, when its receiver/host are available, including full path, bytes, SHA-256, timestamp, process lifetime, and exact guest machine/VM identity. Do **not** use a saved July/October process epoch or the host's older executable as a proxy. If interactive guest Windows is available, the local operator may run the following PowerShell with the **verified** actual game path:
   ```powershell
   Get-Item -LiteralPath 'C:\RIFT_TRANSFER\RIFT\rift_x64.exe' |
     Select-Object FullName, Length, LastWriteTimeUtc
   Get-FileHash -LiteralPath 'C:\RIFT_TRANSFER\RIFT\rift_x64.exe' -Algorithm SHA256
   ```
   The path above is taken from historical RR2 guest receipts, **not** asserted as today's running game's path. Confirm it before trusting output. If the game or launcher moved, discover its current executable first.
3. **P2 — Split based on byte identity, not on the word “update.”**
   - **Same SHA-256:** The exact executable's code-byte/RVA static findings remain candidates for that same file, subject to runtime build/session, native receiver identity, actual player ownership, scene, addon and click/cancel checks. Asset, UI, server or data-only updates can still change behavior.
   - **Different SHA-256:** Create a **new separate pinned-build research baseline**. Preserve old reports as old-build-only evidence; do not re-use native C2M/follow/collision RVAs, pointer chains, field locators, unwind boundaries or memory signatures as newly qualified. First compare the new original file with a saved original using existing bounded offline scanners and selected source-pinned anchors; rederive and retest only the player-facing features needed by the current bounded trial. Do **not** restart the deferred Havok type-7 search or a full-binary import by default.
   - **Unknown/inaccessible:** Leave updated-guest compatibility **blocked/unverified**; do not change expected hashes or force/bypass RR2's executable safety gate.
4. **P3 — Verify RR2 session safety independently.** The RR2 owner must diagnose the currently refused status endpoint through approved owner-specific status/preflight, without changing or deleting canonical queue/history or using old PID/token/grant. If a guest build changed, receiver expected-build identity and addon acquisition contracts require explicit review before any update; a new hash string alone does not prove compatibility. Recheck exactly one receiver, fresh advancing observation and proper cancellation/recovery state.
5. **P4 — Verify actual game behavior before movement.** Require a new source-hash-bound **visually reviewed playable in-world frame**, current C2M setting and actual key/mouse mappings, then sampled player XYZ/clock binding. Only under the existing separate live approval and single RR2 input owner can T0 activation/stop testing resume. T1/T2 remain sequenced after T0 and T1 respectively.

## Patch impact by subsystem

| Item | Current disposition |
| --- | --- |
| RRE M2 exact-build static RVAs (C2M event/query/setter/consumer, follow/clear paths), Havok findings | **Pinned to old SHA; updated guest unknown**. Keep accepted historical findings; do not claim address validity for an unverified guest build. |
| Native pointer chains, RRE/V1 raw probes, ASLR and process lifetime | **Session-volatile** even with identical disk bytes. Requalify resolver and ownership after guest/process change; never transplant absolute pointers. |
| RR2 process, native host/receiver, queue and SHA gates | **Current endpoint unreachable** by one benign status attempt. Coordinate recovery through RR2 owner; preserve protections and unfinished work. |
| RIFT Lua addon and selected player/target/nearby observations | **Unknown current version/source freshness**. Recheck read-only addon API/producer and scene source on the actual updated client, not only historical fixture correctness. |
| RRE NAV-003..006 offline evidence validators and visual tooling | **Reusable** with their previously accepted synthetic/file-only scope; not evidence that updated-game movement or native routing works. |
| Click-to-move activation, current binding/cancel, player motion, obstacle routing | **Unverified**; run only after guest/build/scene and supervised safety gates. |

## Fast resumption without extra framework work

**Next decision-changing fact:** the SHA-256 of the `rift_x64.exe` **actually executed inside RIFT-Lab-1 after the update**, or confirmation the update applied elsewhere. Until then do not invest in repairing offsets that may still be valid or blindly update all hashes.

Use Workbridge/RR2 existing read-only functionality and the current image review path. Do not install a new scanner, agent scheduler, screenshot service or patch watcher. First compare immutable bytes and restore an authorized read-only receiver/status channel through the current RR2 owner; then return to NAV-002 P0/P1.

**Validation performed:** host file SHA-256, on-disk metadata, host changed-file count, one VMware running-list query, benign RR2 status request, physical-host process/listener inventory, and Workbridge/Git preflight. These are runtime observations, not unit-test counts. No source code, user settings, game files, RR2 source, control grants or VM state was modified.
