# Click-to-move lane - 2026-10-18

**Result:** exact-build native code links a C2M-like event branch to segment querying, a destination setter, and a destination consumer. This exceeds UI-only evidence, but is not a qualified callable interface or recorded navigation success.

## Identity and method

- Worktree `C:\work\rre-worker-c2m`, branch `research/nav-c2m`.
- Read-only target `C:\Program Files (x86)\Glyph\Games\RIFT\Live\rift_x64.exe`; verified SHA-256 `7c356c9dde9e12fcbff3c08d953b0630b48b1510a0ffb36e4ec164606e7b17bd`, preferred base `0x140000000`. All addresses below are RVAs. Manifest `STABLE-1-1169-a-1256556` is baseline documentation, not independently re-read here.
- Reused `tools/inspect-navigation-static.py`, saved results of `tools/inspect-navigation-names.py`, original RiftReader `postupdate_static_access_chain.py`, Capstone 5.0.9 and pefile 2024.8.26 in the existing RRE venv. No environment changes or REA/Ghidra import.
- Lane helper searches common RIP MOV root references and byte operands with disp32 `0x146`/`0x1A8`; Capstone verifies candidates from PE unwind-range starts. This is bounded static inspection, not full control-flow/alias analysis.
- `c2m.json` retains selected instruction bytes, whole-window hashes, source hashes, scan counts, coverage and unresolved anchors. Window hashes cover the original full captured ranges even where fewer instructions are retained.

## Directly observed native code

| Stage | Location | Observation and limit |
| --- | --- | --- |
| Setting update | `0xBBB98E-0xBBB9EC`, root `0xBBA1F0` | References `Misc_EnableClickToMove` at `0x26851F8`; after string checks loads `[module+0x33136F0]`, compares/stores `dil` at `+0x146`, and sets bit 3 of byte `+0x18`. Input boolean normalization, dirty-bit handling and persistence remain unqualified. |
| UI value | `0xBC1D71-0xBC1DA6` | Reads the same `+0x146` byte and passes its stack copy and setting name to `0xBB5160`. That callee packages a boolean-like value and calls `0xA73FA0`; this alone is not gameplay control. |
| Event dispatch | root `0x6942A0`, branch `0x694381` | For `[event+0] == 2`, checks `[event+0x120] == 1`. Event type/button/press-or-release meanings are not established. |
| Settings gate | `0x6943A8-0x6943C9` | Calls `0x786C80` with an output handle at stack `+0x50`, then tests byte `[handle.firstPointer+0x146]`. Zero skips the segment/query path. |
| Settings accessor | `0x786C80-0x786D3D` | Can obtain a component-associated handle via `0x53CED0`, a selector, and `+0x20/+0x260`; otherwise calls `0xE60C60 -> 0xBB9D00`. The latter returns handle address `module+0x33136F0`. The fallback links to the UI root; the component-associated object is not proven identical to the global object. |
| Input to segment | `0x694404-0x69458E` | Loads event integers at `+0x128/+0x12C`, passes them through `0x809600` (AL success gate), converts to float for `0xF7A870`. On success builds `end = origin + direction * 100.0`. Float bytes at `0x263C5E8` equal 100.0. Pixel-to-world/ray semantics are inference. |
| Query/result | `0x694638-0x694692` | Calls `0xF671C0` with origin/end pointers, output buffer and stack arguments including `4`/nulls. On nonzero AL, passes the first 12 result bytes to `0x562BC0`, receiver `[inputOwner+0x10]`, then writes `[event+0x18]=1`. Last write is consistent with event consumption, not proof of movement. |
| Query internals | `0xF671C0-0xF673E6` | Packs input vectors via `0x13D2BD0`, calls `0x13D44D0`, gates success on collector `+0x60`, and writes a 12-byte output via `0x13D3180 -> 0x13D2BA0`. A segment-hit/query interpretation is supported; exact geometry, filters and job linkage remain unknown. |
| Destination setter | `0x562BC0-0x562C17` | Calls baseline follow-stop routine `0x534200`, then `0x534990`; copies 12 supplied bytes to `state=[receiver+0xB90]`, offsets `+0x60/+0x68`; sets bit 0 of byte `[state+0x1A8]`. Cached `+0xD8` is not involved in this observed write. |
| Destination clearing | `0x534990-0x534A38` | Processes/releases handles at `[state+0x70/+0x78]` when present and clears bit 0 of `[state+0x1A8]`. This is state-clearing evidence, not an externally validated cancellation gesture. |
| Destination consumer | root `0x5765D0`; `0x5768E0-0x576BCF` | Tests the same bit; copies `+0x60/+0x68`; when `+0x70` is null passes a structure containing the vector through `0x852100 -> 0x52DD60` to fill a handle at `+0x70`. Forms target-minus-position components, zeros the middle delta for this mode, computes squared distance and reaches orientation-like calls `0x686E10/0x686F30`. A near-distance branch calls `0x534990` at `0x576BCF`. Path/route semantics and thresholds remain unresolved. |

The setter has one qualified direct call (`0x69468D`) in the helper's capped search; do not infer uniqueness because indirect calls are not covered. No direct caller of `0x6942A0` was found; callback registration remains open.

The root scan found 319 common MOV references, all prefix-aligned, but local `+0x146` hits were settings code only. An independent byte-operand search found five aligned `+0x146` instructions, including accessor-based gameplay gate `0x6943C2`. The byte-array store at `0x8AFBC8` is not associated with settings just because its displacement matches. Following only the global root missed the candidate gameplay gate.

## Inference and unknowns

**Inference:** event coordinates -> projected segment -> successful query result -> `[receiver+0xB90]+0x60` with active bit `+0x1A8.0` is the strongest exact-build C2M destination-creation candidate here. The matching consumer strengthens destination semantics. It does not prove current-player ownership, the component-specific setting's current value, or an ordinary ground-left-click-release event.

**Unknown:** callback registration/event schema; player ownership and stable resolver; vector frame; query filters/hits; `+0x70` handle contents; native routing and type-7 `TtPathfinding`/type-3 raycast linkage; obstacles, arrival tolerance and cancellation input. Static orientation/distance code does not establish route validity or a supported native call contract. Do not call setters, write fields or promote offsets from this report.

## Existing documented runtime evidence (historical)

Read-only RiftReader sources: `docs/recovery/c2m-destination-discovery-status-2026-07-18.md`, `progress-2026-07-18-post-patch-root-and-c2m.md`, `c2m-truth-bind-and-static-chain-restart-survival.md`, and `scripts/c2m_run_to_goal.py`. July results are not an independently qualified runtime test of this October hash. Referenced capture files were not re-audited.

- The July destination report initially proposed a goal-related paired +/-40 box, then rejected it when its center tracked the player before/after clicking. Its fixed-goal scan found zero qualifying goals. Preserve the later correction.
- Current runner source uses W2S/center fallback and foreground C# SendInput (`click_client_sendinput`, line 823), repeated re-aiming/lateral detours (`drive_to_goal`, lines 1277 onward), and A/D presteps (lines 1326 onward; default enabled). Arrival checks planned-goal distance; it does not read the native destination candidate identified here.
- Historical multi-waypoint arrival therefore does not isolate native obstacle routing. The old `0x32E07C0` root/camera offsets are not promoted here. A custom proximity graph is not a native navmesh; cached component `+0xD8` remains unqualified as a destination.

## Validation, limitations and next step

Five wrapper passes captured 35 regions / 28 unique ranges, all decoded through their windows, without truncation or queued work. Anchor `0x809600` has no PE unwind entry; no function boundary was guessed. Linear decode completeness is not complete control-flow recovery. Two local helper-development failures (initialization order; shell quoting) were corrected without touching external sources. The patch tool could not create the Markdown file; the same owned path was written successfully through PowerShell.

Run `C:\work\rre\.venv\Scripts\python.exe -B tools/agents/c2m/validate_report.py` to verify JSON, retained instruction bytes/decoding, full captured-window hashes, source hashes and the scalar against the exact executable. Reproduce candidate scanning with `inspect_settings.py` (stdout JSON). Wrapper pass anchors/options are retained in JSON.

**Next offline validation:** trace `0x852100` and `0x52DD60` from `0x576994/0x5769A0` to characterize `state+0x70`; resolve stored pointers/registration for callback `0x6942A0`. Establish event meanings and player ownership first. A later separately authorized behavior test should issue one native ground request without runner detours/presteps/re-aims, compare the candidate vector to the destination while walking, and demonstrate ordinary cancellation before obstacle testing.

No live input, live memory read, attach, VM/process control, target modification, publishing or persistent job occurred.



## Local commit blocker

Git staging failed: sandbox cannot create C:/work/rre/.git/worktrees/rre-worker-c2m/index.lock (Permission denied). Parent: c7815b762dbdfe4d681a96cd14a69f658668595c. No staging or commit completed; no escalation, identity change, integration or push attempted. Manager can commit the four owned files with Git metadata write access.
