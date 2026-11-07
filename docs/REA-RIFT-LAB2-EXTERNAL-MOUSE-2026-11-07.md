# SC-609 — External Lab-2 mouse functions using vncdotool

**Current setup:** host-side **capture**, **absolute positioning**, and **left click**, using the already-installed third-party **vncdotool1.4.2**. The user selected positioning/left-clicking first, required the tool to remain external to Lab-2, and requested GitHub reuse. No mouse package, script, service or helper was installed inside the guest. No Ollama was used.

The previous SC-608 guest-agent click route was useful evidence, but did not fulfill the later external-tool requirement. This setup uses the VMware VNC endpoint directly from the physical host; it does not route mouse input through the guest RR2 control agent.

## Third-party choice

- [sibson/vncdotool](https://github.com/sibson/vncdotool) provides the actual VNC protocol, screenshots, absolute mouse positioning and mouse buttons. Existing host installation: `C:\work\riftreader2\artifacts\tools\control-python\Scripts\python.exe`, vncdotool version1.4.2. No download, global installation, environment change or replacement mouse backend was needed.
- Its [v1.4.2 usage documentation](https://github.com/sibson/vncdotool/blob/v1.4.2/docs/usage.rst) explicitly requires position initialization and click within the **same connection**; starting a separate CLI click can click at(0,0). The entry point always calls `mouseMove(x,y)` before any left-button down/up on that same client.
- PyAutoGUI and PyDirectInput were also inspected on GitHub. They operate a Windows desktop directly and would need to run inside the guest for this use, contrary to the external-tool requirement. They were not installed or used.

The RRE [entry point](../tools/external-lab2-mouse.py) is a small adapter around the installed library and existing RR2 VM identity/authentication/console-mutex helpers. It adds Lab-2-only routing, screenshot review, bounded button hold/release, retained hashes and connection cleanup; it does not implement a VNC or mouse backend. It does not modify those external source files.

## Explicit controller handoff

At approximately08:33EST on November7, the existing native Lab-2 controller was freshly checked against its managed owner, exact VM/game identity, idle queue and no held input. Its authenticated STOP returned stopped=true/recoveryRequired=false. The existing generation's own `stop.request` mechanism was used, and exact controller PID41888 exit plus `exited.json` were verified. The shared console mutex was independently acquired **without abandonment**. The game and VM were not restarted; guest software was not changed.

**Final mode:** native Lab-2 controller intentionally stopped; host VNC mouse tool active on demand, disconnecting and releasing its mutex after each command. The old controller's marker/receipt remain intact. Native inspection helpers that automatically start dependencies must not be run concurrently. Returning to native telemetry/control requires an owner-coordinated handoff, not clearing a stop marker, forcing a process or bypassing the mutex.

Original owner preflight, authenticated STOP/exit/mutex handoff and operation artifacts are hash-bound in the [machine receipt](REA-RIFT-LAB2-EXTERNAL-MOUSE-2026-11-07.json).

## Functions and coordinate system

All commands run **on the physical host**, using the existing host interpreter:

```powershell
$mousePython = 'C:\work\riftreader2\artifacts\tools\control-python\Scripts\python.exe'
$mouseTool = 'C:\work\rre\tools\external-lab2-mouse.py'
& $mousePython -B $mouseTool capture --output 'C:\work\rre\artifacts\my-new-capture'
```

For a standalone absolute move, use `move X Y --output <fresh RRE artifacts directory>`. For one left click, use `click X Y --output <fresh RRE artifacts directory>`. Choose X/Y from a **fresh full guest-desktop image**. The observed VNC desktop is1211x757, including the guest title bar and taskbar; the earlier guest-agent RIFT client images were1211x702 with origin(0,23). These coordinate systems must not be mixed.

Move/click commands capture and display a review request before input. Inspect its original `before.png`, target pixel and current scene, then send `approve CAPTURE_ID specific review note` to that process's stdin within40seconds. One command performs one reviewed movement or click. Click uses the existing library's absolute move, left down, bounded100ms hold, and left up. A separate image is captured after350ms for visual review; that delay is not a guaranteed game response time. Input is not automatically replayed.

Each command acquires the existing **Lab-2 console mutex**, refuses a busy or abandoned owner, brackets its operation with the exact VM process/log/listener identity, preserves image dimensions, keeps saved authentication in memory, releases the mouse button, disconnects the VNC connection and releases the mutex. Capture sends no input. Reports deliberately say `completed-awaiting-visual-review`: successful protocol execution is not itself proof of a UI response.

VMware endpoint: `127.0.0.1:5962`; VMX `C:\rift modding\VMs\RIFT-Lab-2\RIFT-Lab.vmx`. This is host-loopback access to the existing VMware service; no guest network service or new inbound port was installed. Do not place credentials on command lines or in reports.

## Fresh live verification

At approximately08:36–08:38EST, four operations completed through the host-only VNC route:

| Operation | Full desktop position | Direct original-image observation |
| --- | --- | --- |
| Standalone move | (914,335) | Pointer moved onto highlighted Browse; browser stayed closed. |
| Left click | (914,335) | Browser visibly opened. |
| Standalone move | (1162,431) | Pointer moved onto highlighted Close; browser stayed open. |
| Left click | (1162,431) | Browser visibly closed. |

Each operation used a fresh capture/review and a fresh VNC connection with same-connection position initialization. All exited0, sent release, disconnected and released their mutex. The original before/after images were visually inspected, and their hashes are retained. VNC capture-only also succeeded before the input trials. The final browser is closed, with no persistent RRE VNC process or connection.

These external frames show BolinaoL43 in the game world on the same VM epoch. The pre-handoff fresh guest executable SHA was `1935a05c9db6d468e34e0055014a4a99c1b5afceb1695884e24600f5c20a4be8`, PID9752/start ticks`639294897826627677`. External VNC identity checks authenticate the VM/console and original pixels; they do **not** independently attest the guest process/hash/foreground state after shutdown of the native controller. Do not promote the pre-handoff process receipt into a continuous post-handoff process attestation. Requalify builds/processes when needed through a separately authorized read-only route.

## Validation and completion scope

Ten focused host-only tests passed without VM access, covering capture without input, movement without button-down, move-before-click on one client, rejected review, invalid coordinates, busy/abandoned ownership, VM drift, release after button failure, and failure to claim completion on uncertain disconnect. Source tests are in [test_external_lab2_mouse.py](../tools/tests_mouse/test_external_lab2_mouse.py).

The setup fulfills the selected initial functions: capture, positioning and left clicks, external to Lab-2 using third-party software. No right-click, scrolling, dragging, gameplay automation, guest installation or backend rewrite is claimed. Preserve existing SC-103/SC-306/RC/NAV blockers. The current research gate's unrelated old-build failures, exact test exits and final cleanup checks are recorded in the machine receipt and dated handoff.
