# Native pathfinding dispatch investigation — offline

**Lane:** `pathfinding` · **Branch:** `research/nav-pathfinding` · **Base commit:** `c7815b762dbdfe4d681a96cd14a69f658668595c` · **Research date:** October 18, 2026 (EDT)

## Verdict

The current Rift x64 build has a **type-7 dispatcher category labeled `TtPathfinding`**. We traced the generic queue/enqueue path and both currently known direct call sites into the dispatcher. Their producers are **type 1 and type 3**, not type 7. **Type-7 handler registration, non-null entries, job producers, and use for player navigation remain unverified.** This is neither proof of a reusable route interface nor proof the feature is absent.

This Markdown handoff was completed by the manager from the worker's saved JSON after the bounded Codex worker job timed out. The original worker's evidence verifier passed independently. No live game input, debugger, process attachment, game modification, REA/Ghidra import, or new navigation algorithm was involved.

## Exact executable and evidence

- Native file: `C:\Program Files (x86)\Glyph\Games\RIFT\Live\rift_x64.exe`
- SHA-256: `7c356c9dde9e12fcbff3c08d953b0630b48b1510a0ffb36e4ec164606e7b17bd`
- Preferred static image base: `0x140000000`; **all numbers below are RVAs**.
- Evidence: [pathfinding.json](pathfinding.json), with 17 exact native windows, 294 byte-verified instruction excerpts, seven qualified direct call sites, six hashed sources and documented rejected matches.
- Method: reused existing `tools/inspect-navigation-static.py`, original RiftReader `postupdate_static_access_chain.py`, pefile and Capstone. All analysis was offline.

Independent check:
`C:\work\rre\.venv\Scripts\python.exe -B tools/agents/pathfinding/verify.py`

The test returned `PASS` with 17 windows, 294 instruction excerpts and seven qualified call sites. This verifies bytes and extraction provenance, **not** control-flow reachability or game behavior.

## Confirmed native-code observations

| ID | Location | Observation |
| --- | --- | --- |
| PF1 | `0xF3FA4..0xF41FF` | Dispatcher obtains a job and maps type **7** to the profiling label `TtPathfinding` (reference `0xF4089`). The handler pointer is fetched using type-indexed `queue+0x130 + type*0x20`; for type 7 that is `queue+0x210`. |
| PF2 | `0xF4184..0xF41E2` | Indirect call receives queue in RCX, a pointer to the local job buffer in RDX and subtype in R8d. This is observed register flow, not a complete externally callable ABI. |
| PF3 | `0xF39A4`, `0xF38B8`, `0xF3664` | A generic enqueue wrapper invokes classification and copies a 0x100-byte job into a bucket selected through `state+0x38`. The classification helper examines job type/subtype and a mapping table or falls back to a type-based index. |
| PF4 | `0x8ECB4`, call site `0x8EFD0` | One dispatcher caller constructs job type **3**, subtype **7**, length **0x80**; enqueues through `0xF39A4` at `0x8EF77`. Subtype 7 must not be mistaken for **type** 7. |
| PF5 | `0x8A8D8`, call site `0x8A9E6` | Another dispatcher caller constructs job type **1**, subtype **0x0F**, length **0x70**; submits through `0xF3A08` at `0x8A9DA`. |
| PF6 | `0x89ABC` and `0x8A8D8` | A constructor-shaped region clears receiver field `+0x160`; that field is subsequently used as a queue pointer by a caller. Object ownership and non-null assignment remain unresolved. |
| PF7 | `0xF3A4C`, `0xF3DC0` | Generic callback offsets `queue+0x48/+0x50` are possible registration anchors. They are distinct from the per-type table; no writer or callback target is established. |

The profiling labels and RDTSC stores show named job categories, but a category may exist without populated handlers or submissions in this client. Do not call a function pointer, write an offset, or build a replacement pathfinder based on these results.

## Rejected shortcuts and limits

Offset-only scans did **not** establish queue writers: candidate stores at `0xAF85FD`, `0xB18D9C`, `0x4C3859`, `0x16384D5` and `0x953DE` belonged to different byte-copy/array contexts or lacked receiver/type-stride linkage. Each rejection, with neighboring instructions, is preserved in the JSON report.

Unwind regions do not guarantee source-level function boundaries. Linear disassembly and a direct-call cap of 64 candidates per target do not establish complete reachability. Direct/indirect/tail/leaf paths can be missed. Some leaf addresses have no PE unwind entry; enclosing boundaries were not guessed. The worker completed five focused wrapper queries covering 30 region records (with repeats), not a full-program code audit.

**No type-7 handler table entries have been observed.** Equally, no observation establishes that the table is null or unused. Existing game movement tests and historical custom A* / proximity meshes do not fill that evidence gap.

## Next bounded, reuse-first investigation

First identify where the queue provided to `0x8ECB4` or held at owner `+0x160` is constructed and populated. Qualify direct callers and address-taken references of `0x8ECB4` and `0x8A8D8`; cap the next pass at 12 additional unwind regions. Seek **the same receiver** receiving callback writes at `+0x48/+0x50` and typed handler record writes under `+0x130 + type*0x20`; an isolated matching offset is not enough.

Only after establishing a valid type-7 record writer should the analysis follow the pointer at `queue+0x210`, enumerate populated callbacks, and look for a producer whose job **type** is 7. Then determine whether a destination/route appears at the caller or output and whether it connects to player click-to-move, NPC movement or another service.

The scope remains **offline** until live-input and debugger boundaries are separately satisfied.
