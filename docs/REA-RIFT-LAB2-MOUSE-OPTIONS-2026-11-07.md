# SC-615 — External Lab-2 mouse options and measured capture costs

Observed November 7, 2026, 11:57 EST. **Best fit for RRE now: direct host-to-VMware VNC with the installed vncdotool 1.4.2.** Reuse the existing backend; optimize its session and observation workflow before replacing it. This is a contextual recommendation, not a claim that it is the fastest VNC implementation universally.

The current [adapter](../tools/external-lab2-mouse.py) already has live-qualified capture, absolute positioning/hover, and reviewed left clicks. All input remains external to Lab2. See the [SC-609 procedure](REA-RIFT-LAB2-EXTERNAL-MOUSE-2026-11-07.md) and this investigation's [source/timing receipt](REA-RIFT-LAB2-MOUSE-OPTIONS-2026-11-07.json). No input was sent for this benchmark; no software was installed and no backend changed.

## Options compared using primary sources

| Option | Toolset and fit | Decision |
| --- | --- | --- |
| [vncdotool](https://github.com/sibson/vncdotool) | Existing tested VMware path; move/button down/up, screenshots, region crops/expectations; synchronous API can reuse one connection | Keep as production research backend |
| [AsyncVNC](https://github.com/barneygale/asyncvnc) | Asyncio API, mouse buttons/wheel/hold, screenshots; could suit a future async service | Credible alternative if measured Twisted integration/lifecycle costs become a real blocker; no speed or Lab2 reliability proof yet |
| [noVNC](https://github.com/novnc/noVNC) | Rich human browser console; requires WebSocket transport, usually websockify for a raw TCP endpoint | Good if a browser console is itself needed; extra layer for current headless Python workflow, no demonstrated latency advantage |
| [LibVNCClient](https://libvnc.github.io/doc/html/group__libvncclient__api.html) | Native C library; framebuffer-relative pointer/button events and frame-update callbacks | Suitable for an existing native client; new integration/build cost is not justified by this sample |
| [VNC Agent Bridge](https://github.com/Ganzzi/vnc-agent-bridge) | Advertises move/click/drag/scroll/capture/recording and TCP/WebSocket facades | Feature-rich candidate, but advertised performance/coverage is not independently tested VMware evidence; do not add another layer merely for its feature list |
| [PyAutoGUI](https://pyautogui.readthedocs.io/en/latest/) / [PyDirectInput](https://github.com/learncodebygaming/pydirectinput) | Control the Windows desktop where they execute; PyDirectInput uses SendInput and scan codes | Could operate the VMware viewer from the host, but would depend on viewer focus, scaling, occlusion and coordinate mapping; direct VNC avoids those host-viewer dependencies |

Correction to an overbroad statement in the earlier SC-609 comparison: desktop-input tools do **not inherently have to run in the guest**. They can drive the host VMware viewer. The practical disadvantage is the extra viewer/focus/coordinate dependency; running them directly against guest applications would require guest execution. Neither route was newly tested here.

## Local measurement, not a library race

The capture-only experiment reused RR2's existing identity/authentication/console-mutex/connection/image helpers. It took nine full-desktop PNG captures: three reconnect sessions with one frame each, then one connection with six frames. VM epoch and1211x757 geometry matched throughout; connections closed, mutex released, reactor shut down; a fresh host check found zero established connections to5962 and zero benchmark/mouse Python processes.

| Measurement | Samples | Median | Range |
| --- | --- | --- | --- |
| Connection call plus first full verified/saved frame | 4 | 88.326 ms | 81.644–367.736 ms |
| Later full verified/saved frame on one connection | 5 | 72.654 ms | 65.473–1019.693 ms |

These durations include framebuffer delivery, PNG encoding/file I/O and validation. Connection creation returns before authentication, so the first frame includes lazy connection setup. They exclude Python process startup, model image interpretation, review/tool round trips, mouse events and visible game response. The1.02-second outlier remains in the evidence. No sustained frame rate, percentile latency, click latency or performance superiority over an untested library follows from nine samples. The whole measured script completed in2.407seconds.

## Highest-value optimization order

1. **Use a bounded persistent connection for one owned interaction session.** Keep absolute move and click on that same client. Preserve fresh per-action scene/geometry review and VM-epoch validation; expire/release the session on idle, drift or ownership handoff. This is a proposed adapter improvement, not implemented by this research. The library supports reuse, but its synchronous compatibility layer requires one application caller thread and one reactor thread; sharing the client across application threads is unsupported. See the [versioned library documentation](https://github.com/sibson/vncdotool/blob/v1.4.2/docs/library.rst).
2. **Measure and reduce observation/review round trips.** The current adapter deliberately spends100ms holding left click and350ms before its afterimage:450ms of configured waiting, plus captures/review. Improve feedback with bounded repeated observation of the expected UI change rather than blind replay or arbitrarily shorter waits. Any gains here remain unmeasured. Keep original full frames; useful crops reduce reviewer payload. In this [vncdotool version](https://github.com/sibson/vncdotool/blob/v1.4.2/vncdotool/client.py), captureRegion crops after refresh, so it must not be sold as a wire-bandwidth optimization.
3. **Expose existing primitives when a research task needs them.** Right/middle click, wheel button events and down/move/up can reuse the backend; each still needs Lab2 qualification and release-on-error checks. Do not use default mouseDrag blindly: the versioned implementation pauses0.2seconds per interpolation step, making step1 extremely slow for long paths. A duration-bounded drag would require an explicitly reviewed implementation and live test.
4. **Consider a replacement only against an unmet requirement.** Compare identical scene/resolution, the same click hold/response criterion, acquisition/visible-response medians and tails, cleanup, reconnection, CPU and full evidence cost. Absolute UI clicking and continuous relative camera control are different qualification problems. Neither native code nor an async API is inherently proof of better end-to-end game interaction.

Current reliable scope stays capture/move/hover/left click. No wheel/drag/right-click/relative camera/unattended-gameplay qualification was added. No Ollama or FreeBuff was used. The native controller remains intentionally stopped; do not start a competing console owner.
