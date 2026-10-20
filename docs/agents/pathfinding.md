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

## Historical query recovery — 2026-10-19 (M3-001 preflight)

The five previously untracked `tools/agents/pathfinding/_query1.json` through `_query5.json` files have been **preserved and verified**, not reinterpreted as new pathfinding functionality. They are original offline exact-build scans made before V7 standardized complete run manifests. Their raw SHA-256s are pinned in `tools/agents/pathfinding/verify_legacy_queries.py`, which does not edit them.

Independent exact-file verification (job `rre-pathfinding-historical-verify-20261019-01`, exit 0) confirmed **30 saved code-region records / 28 distinct regions**, **2,739 decoded instruction rows**, **five instruction-boundary-qualified call sites**, two explicitly unresolved anchors (`0xF3F94`, `0x74490`), zero truncated code windows, and zero pending work queue. File and original helper hashes match the qualified executable `7c356c9dde9e12fcbff3c08d953b0630b48b1510a0ffb36e4ec164606e7b17bd`. A separate baseline report verifier (job `rre-pathfinding-baseline-verifier-20261019-01`, exit 0) rechecked 17 retained regions and 294 excerpt rows. pefile still reports 825 already-diagnosed duplicate-parent warnings.

These **historical** files have no complete invocation/recorder source manifest, so V7 cannot retroactively certify those run arguments or exhaustive coverage. The previous finding is unchanged: type-7 `TtPathfinding` label and queue slot `+0x210` exist, but registration, populated handlers, actual job producers and player navigation use remain **unknown**.

**Next bounded independent research:** use the current hardened offline caller/reference scanners to identify code or stored pointers referencing the generic dispatcher producers (`0x8ECB4`, `0x8A8D8`). Do not infer that matching a local field displacement proves ownership of `queue+0x210`. New evidence must be captured under a fresh V7 manifest, and any reported runtime/navigation capability must remain unverified without a later separately authorized behavior test.

## M3-001 continuation — 2026-10-19: job queue owner and simulation vtable

**Outcome:** This bounded exact-build continuation found a **concrete Havok simulation owner** for the previously known type-1 job producer, and an additional direct caller of the type-3 producer. It has **not** established a populated type-7 `TtPathfinding` table, a route request/output, or player navigation.

### Independently qualified native evidence

- **PF8 / RTTI-backed table:** Stored code pointer at `.rdata` RVA `0x27255F8` equals preferred VA `0x14008A8D8`. That pointer is slot **18** (zero-based) in a table starting `0x2725568`. At table-8 (`0x2725560`), a valid MSVC Complete Object Locator at RVA `0x2D75A80` identifies `.?AVhkpMultiThreadedSimulation@@`. The next table's locator at `0x2725620` is associated with `hkpReportContactMgr`; the boundary is not guessed from a coincidental offset.
- **PF9 / table installation:** Code at `0x89AE1` and `0x89CB7` loads that same table address; the following stores at `0x89AEC` and `0x89CC1` install it into a receiver. Constructor-shaped code `0x89ABC` initializes receiver `+0x160` to **zero** at `0x89BD7`. A qualified direct caller `0x7B0A3` reaches `0x89ABC`. Neither the constructor nor this scan identifies a non-null queue-pointer writer.
- **PF10 / type-1 producer:** Method `0x8A8D8` reads a queue pointer from receiver `+0x160` at `0x8A9DF` and invokes dispatcher `0xF3FA4` at `0x8A9E6`. This qualifies the earlier type-1 job as associated with Havok's multithreaded simulation. It is not a type-7 job.
- **PF11 / type-3 caller:** A new verified direct caller at `0x8F21C` invokes `0x8ECB4`. The small caller region at `0x8F204` selects that branch when argument gates pass, otherwise calls `0x8EA08` at `0x8F223`. An individual wrapper path is not a general gameplay call contract.
- **PF12 / narrow negative result:** Restricted static LEA/stored-pointer search finds two aligned references to the simulation vtable at `0x89AE1` and `0x89CB7`, but zero under that encoding coverage for `0x8F204` and `0x8EA08`. Other indirections, table encodings and dynamic call sites remain unknown.

The evidence consists of **six** new bounded V7 queries, each with its own write-once original schema-1 capture and schema-2 run/source manifest under `tools/agents/pathfinding/m3-001-*-20261019*.json`. The manifest records original binary/helper hashes, complete command args, Capstone/pefile versions and 825 unfiltered parser warnings. Full pinned SHA256s and evidence class/limits are in `tools/agents/pathfinding/m3-001-followup-summary.json`. The corresponding `verify_m3_001_followup.py` validated original PE bytes, decoded instruction bounds, RTTI locator, virtual-method position, simulator initialization and qualified caller sites. Real job `rre-resume3-vtable-followup-verification-20261019-01` **passed (exit 0)**.

**Important distinction:** The shared worker dispatcher contains the profiling category `TtPathfinding` type 7, but the **specific producer now associated with `hkpMultiThreadedSimulation` constructs type 1**. Its vtable slot number 18 is not a job type. Those numbers must not be conflated. No evidence in this pass proves type 7 is absent or unused elsewhere.

**Next gate:** identify what assigns the simulation's `+0x160` queue pointer, then locate a same-queue typed handler-table write at `queue+0x210` and an actual producer whose **job type** is 7. Only then inspect route inputs/outputs and any relationship to player movement. Do not build a custom pathfinder from this result.

## M3-001 bounded continuation — October 19, 2026: exact RTTI rejects misleading offsets

**Result: qualified offline disproof, not a working native pathfinder.** V7 target capture `artifacts/m3-001-owner-caller-20261019-01.json` (259,174 bytes; SHA-256 `445c8025bceb6f639847c1170e09161c9c0d8eca362e3475b11e73c2fc0d3046`) and its immutable manifest (`99872594de03085c316ed966965c6cc21b3fe8020fc8d13b21cdbab93240d54c`) covered two PE-unwind regions. It found one qualified direct call to `0x89ABC` at `0x7B0A3` and no direct E8 caller for `0x8A54C` within that method's bounded search. There were no truncated regions; 825 original pefile warnings were retained. Absence of direct calls is NOT absence of virtual/indirect calls.

**New exact native owner evidence:**

- **PF13:** At `0x7A28E`, a RIP-relative LEA resolves to VFT `0x2724038`. MSVC RTTI Complete Object Locator `0x2D755A0` has valid signature and self-RVA and names `.?AVhkpWorld@@`. World-this is copied to RDI at `0x7A272` and VFT installed at `0x7A295`.
- **PF14 — false handler:** `0x7A384 mov qword ptr [rcx+0x210],r15` stores **zero**, established by `0x7A261 xor r15d,r15d` without intervening calls or register overwrites. This is **hkpWorld+0x210**, not a proven queue type-7 handler registration.
- **PF15 — false queue setter:** `0x7AF8D mov dword ptr [rdi+0x160],ecx` copies an integer derived from `0x7AF81 movsx ecx,byte ptr [rsi+0xD9]` to the *world* object, not to the separate simulation's pointer field.
- **PF16 — two distinct objects:** At `0x7B0A3` world construction calls Havok simulation ctor `0x89ABC` and at `0x7B0A8` saves its pointer at `hkpWorld+0x10`. The resulting `hkpMultiThreadedSimulation` VFT is `0x2725568`; MSVC RTTI names that distinct class.
- **PF17 — simulation field:** At `0x89BD7` the simulation's own `+0x160` is zero-initialized; its type-1 job method reads that field at `0x8A9DF` and calls dispatcher `0xF3FA4` at `0x8A9E6`. A nonnull same-object assignment is **not yet identified**.

**Bounded archive triage:** The recovered `tools/agents/pathfinding/m3_001_offset_triage.py` deterministically scans **eleven existing local schema-1 artifacts**, with original binary SHA checks and read/write classification. Among **3,890 distinct decoded instruction RVAs**, it found **91 distinct offset references**, including nine `+0x160` and three `+0x210`. The latter are the hkpWorld zero initialization (`0x7A384`), stack-local `movss [rsp+0x210]` (`0x8AC30`), and a repeated initialization at `0xAF8485` with unqualified receiver; nearby immediate `7` values are not a job type. Other `+0x160` stores at `0xAF8396` (vector initializer) and `0x1638115` (32-bit scalar) are not established simulation queue writers. These are **only already-captured windows**; no native global coverage is claimed.

**Validation:** The exact original PE-byte/RTTI verifier `tools/agents/pathfinding/m3_001_verify_world_owner.py` passed (job `rre-m3-world-owner-independent-byte-verifier-20261019-01`, exit 0); `m3_001_test_offset_triage.py` passed **18 tests**, exit 0; the old five-file native-window verifier passed, exit 0. Full machine-readable findings are preserved in `m3_001_world_owner_findings.json`.

**Agent recovery:** A genuine independent Pathfinding OpenCode session `rre-m3-type7-independent-offset-triage-agent-20261019-01` timed out, leaving only an inaccurate prototype parser and no tests. That prototype was **rejected**. The Manager subsequently rewrote its code, authored the tests/verifier and validated them. Do not attribute the corrected implementation to the timed-out worker.

**M3-001 remains READY / incomplete.** Next qualify a **nonnull assignment to the same hkpMultiThreadedSimulation object +0x160**, then a populated handler at the same queue's `+0x210` and a producer whose actual **job type == 7**. Neither a vtable slot 18, literal 7, type-3 subtype 7 nor matching displacement suffices. No input, debugger, game process, memory write or custom pathfinding was performed.
