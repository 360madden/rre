# RRE — Lab-2 sole live-testing target and readiness

**Later SC-622 live observation:** [RRECollector0.4.12 manual outbound memory prototype](REA-RIFT-RRECOLLECTOR-LIVE-BRIDGE-2026-11-07.md) passed source/install/load/Saved gates and one complete54-record/five-part transfer through the existing native tools to the one host reader. The RRE window ended14:49EST; control was explicitly returned, with no controller restart or queue reset. Fresh coordination is required before any further Lab2 operation. The earlier readiness table below is historical, not current ownership or permission.

**Later explicit operator exception — November7 14:17 EST:** “Allow only RRECollector addon files to sync; keep all testing in Lab2.” The manager may additively deploy the reviewed RRECollector package to Lab2’s existing OneDrive Documents AddOns/RRECollector load root, accepting synchronization of only those RRECollector addon files. This resolves the no-silent-propagation gate for that folder only; no other addon, OneDrive/Windows setting, physical-PC/Lab1 live interaction or process is included. Keep source/package/install/load evidence, backups and TOC-last deployment. No further generic permission question is required for this authorized route.


**Decision:** November 7, 2026, America/New_York. **Task:** SC-607, sole RRE manager, documentation/read-only-readiness lane. The user replaced physical-PC live testing with **VMware RIFT-Lab-2 only**. This policy supersedes the October 27 physical-PC target policy and physical-host testing/deployment directions in older RRE instructions, roadmaps and handoffs. Their observations remain valid only at their recorded scope and time.

## Target and operational ownership

- VMX: `C:\rift modding\VMs\RIFT-Lab-2\RIFT-Lab.vmx`; guest machine: `RIFT-LAB-2`.
- Physical-PC RIFT and Lab-1 are excluded from RRE live testing. Do not shut down or alter them to enforce this scope; they may belong to independent workflows.
- Static/offline evidence from a previously qualified executable may be reused when it matches Lab-2's freshly checked bytes. Matching code does not transfer runtime addresses, character/role, loaded addon version, snapshots, freshness, input authority or gameplay acceptance.
- RR2 owns the existing per-lab controller and authenticated guest agent. RRE may consume their guarded read-only observations and generated runtime evidence without editing RR2/Workbridge source, starting another controller, releasing another owner's lease, or overriding a quarantine. Existing per-VM cached-login checks apply if a later authorized operation needs VMware Tools; never use Lab-1 credentials for Lab-2 or expose secrets.
- The switch does not authorize gameplay input, VM/game/helper process control, memory writes, injection/debugger attach, addon installation or reload. The former physical-PC RRECollector deployment exception is suspended. Any future deployment must first establish a scoped Lab-2 guest destination and package/install/load evidence; shared OneDrive folders must not silently propagate changes to excluded machines.

## Existing interaction route

**Current external mouse mode (later November 7, SC-609):** the user requires mouse tooling outside Lab-2, with positioning and left clicks first, preferring GitHub/third-party reuse. The installed host **vncdotool1.4.2** supplies the actual capture/move/click implementation through the small RRE entry point `tools/external-lab2-mouse.py`. See the [external mouse procedure and live evidence](REA-RIFT-LAB2-EXTERNAL-MOUSE-2026-11-07.md). No guest mouse software/helper was installed. Native controller PID41888 was STOPped, gracefully exited and independently released the shared console mutex; it is intentionally stopped while external mode is selected. Do not invoke the native inspection driver's automatic dependency startup during an external operation, or restart a competing controller. Use a separately coordinated mode handoff when native-agent telemetry/control is needed again. The native inspection route below records the earlier read-only observation and remains available after that handoff.

**Later same-session authorization:** the user approved the operations needed for reliable Lab-2 mouse interaction and made that the immediate priority (SC-608), with **no Ollama**. Bounded screenshot-reviewed mouse positioning/clicks through the existing controller are authorized. Begin with reversible addon UI controls; retain per-action identity/foreground/geometry checks, one queue owner, release/STOP and cleanup, and direct visual response evidence. The no-new-input statement above describes the target switch itself; this later authorization permits the stated mouse-qualification task without another permission question. It does not authorize unrelated gameplay or weaken process/memory protections.

Use the existing `C:\work\riftreader2\scripts\inspect_lab2_tool.py` through its reviewed `scripts/lab2_tool_handoff.js` overview handler. The driver is fixed to Lab-2 and sends no gameplay input. It reuses the existing controller, fresh executable-byte identity, persistent native candidate reads, queue-owned capture, watchdog release and final VM/game inventory. Its canonical artifacts are under `C:\work\riftreader2\artifacts\e2e-latency-20261106`; these runtime receipts are distinct from source development. Inspect the returned original image after cleanup before describing the scene.

The runtime resource is `vm:rift-lab-2`; the controller configuration is `artifacts/control-fleet-live/lab2/host.json`, with loopback API port 49921. Do not print private configuration/managed-plan contents or tokens. Do not use Workbridge's `desktop_capture_vmware_host`: it is fixed to Lab-1. Direct unleased VMware/VNC input is not a substitute for the existing controller. Future separately authorized input must retain current screenshot review, foreground/window/geometry, sole owner, lease, bounded action, STOP/release and cleanup gates.

## Fresh observation — November 7, approximately 08:00–08:01 EST

The existing read-only inspection completed with exit 0 in 3.803 seconds; its screenshot and native sample were reviewed after release. [Machine-readable receipt](REA-RIFT-LAB2-READINESS-2026-11-07.json) records original artifact paths and SHA-256 hashes.

| Check | Observation and limit |
| --- | --- |
| VMware | Lab-2 running; exact VMX independently inventoried. VMX PID 17848, start ticks `134383662779267832`, log epoch `2026-11-05T15:31:17.951Z`, console listener 5962. Lab-1 was also running but was not operated. |
| Guest RIFT | `RIFT-LAB-2`, `C:\RIFT_TRANSFER\RIFT\rift_x64.exe`, PID 9752, process-start ticks `639294897826627677`, HWND `0x401BC`, foreground; client 1211 x 702. Identities are observation-specific. |
| Actual executable build | Fresh-byte authenticated identity checks returned SHA-256 `1935a05c9db6d468e34e0055014a4a99c1b5afceb1695884e24600f5c20a4be8`. A separate VM-bracketed fresh-byte query also exited 0. This matches the recent SC-604 static source; no expected hash or native offset was changed. File length/product/API build string were not independently returned by this check. |
| Scene | Original image reviewed: Bolinao level 43, AFK, visibly in the Silver Coast game world with HUD/action bars, without a loading/disconnect modal. This is a current scene observation, not casting or movement acceptance. No role allocation or exact ability inventory was established. |
| Controller and cleanup | Connected to Lab-2; resource ready; guest disarmed, not busy, no sampled desktop inputs down, no recovery required. Capture receipt says `captured-and-released`, watchdog `stopVerified=true`. The persistent controller's lifetime console reservation remains held by its owner; do not clear it. `nativeTextEntryState=unknown` and `responseVerified=false` remain explicit. |
| Native candidate baseline | Health 10635/10635 and Energy 100/100, visually consistent with the HUD. Mana unavailable (`not-mana-kind-three`). These remain candidate observations; passive freshness, changed-state behavior and restart qualification are not established. |
| RRECollector | UI visibly v0.4.10, Known 0 / Static 96, no saved candidate receipt, empty research slots. Source/guest parity, current saved version and functional captures are unverified. Physical-PC v0.4.11/Atank L45/69-known receipts must not be applied to Bolinao. No install, capture command or reload was performed. |

**Readiness verdict:** Lab-2 is available for guarded read-only observation. The actual RIFT executable matches the current static research build. Gameplay experiments and RRECollector acceptance are not qualified by these checks; no pending SC/RC/NAV gate is closed except the bounded SC-607 target-switch/readiness task.

## Exact restart

1. Read the latest dated RRE handoff, this policy, SC/RC registers and coordination instructions. Reconcile Git/index, worktrees, owners, jobs and journals before mutations.
2. Recheck the existing Lab-2 owner/controller and run a new guarded overview into a fresh canonical output directory. Do not reuse PID/start/HWND/VM epoch or an old screenshot as current.
3. For SC-103/collector work, establish Lab-2 character/calling/role and source/install/load/saved-data evidence before choosing a relevant bounded test. Existing Warrior-specific static candidates and physical-PC Pin/Undo history do not qualify this character.
4. Preserve SC-103/SC-306 blocked, SC-604 interim, RC-26/30/31/32 pending, and NAV-002 blocked until their own evidence exists. Do not recreate missing physical-PC historical receipts using Lab-2.
5. Use a separately scoped and authorized operation for any input, installation or dependency recovery; keep one live owner. No broad import or repeated parked probe is needed for this readiness result.
