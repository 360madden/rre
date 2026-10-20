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


## M3-001 additional bounded negative proof — October 19, 2026, 23:48 EDT

**PF21 verified:** The apparent queue+0x210 handler writer at RVA **0x79A9F** is a SECOND hkpWorld constructor zero-initialization, not a registered type-7 job callback. It is exactly *mov qword ptr [rbx + 0x210], rcx* (bytes 48898b10020000). Exact PE instructions within the complete unwind range 0x799A4..0x79B41 demonstrate: 0x799B9 aliases world this to RBX; 0x799BC derives VFT RVA 0x2724038 and 0x799C9 installs it; 0x799D1 zeros ECX with XOR; no intervening RCX overwrite or call occurs before 0x79A9F. The MSVC class locator 0x2D755A0 confirms the class as hkpWorld. All 79 instructions in the method decode to their complete PE boundary.

**V7 evidence:** Read-only job rre-m3-v7-second-hkpworld-ctor-capture-20261019-01 succeeded, output original artifact at artifacts/m3-001-second-world-ctor-20261019-01.json (29,983 bytes; SHA256 a79b857fbf997411a463ebcd6cad79119942ac1543ad7a2c664494d5c5f13443) and immutable manifest at artifacts/m3-001-second-world-ctor-20261019-01-manifest.json (SHA256 74bf45db06e6a04d4a88e4ba02a3011acb9e1a61bc531ae9186a371ac2495600; 825 parser warnings retained). The exact original native code/RTTI verifier wrote the unique, write-once artifacts/m3-001-second-world-ctor-qualified-20261019-01.json (1,279 bytes; SHA256 d95a802962f729f274580a15ad9e5f40a01ebb543017c2f85ddcd05d310432f7). Source is tools/agents/pathfinding/m3_001_verify_second_world_ctor.py. Four independent Manager-reviewed tests in m3_001_test_second_world_ctor.py passed exit 0, job rre-m3-second-ctor-four-verifier-regressions-20261019-01.

**Additional original PE-unwind-bounded band survey** of RVA 0x70000..0xF7000 (not the whole game) decoded 78 qualified ranges / 27,224 instructions and found seven qword *memory-first* operand references with +0x160 or +0x210. They are NOT all writes. Qualified observations: 0x79A9F and 0x7A384 are hkpWorld zero stores; 0x89BD7 initializes simulation+0x160 to zero; 0x8A576/0x8A904 compare/read qword simulation+0x160; 0x9377E/0x9A757 use RSP stack-local offsets. **No verified nonnull same-simulation queue writer or type-7 handler appears in this bounded band.** Original source raw-byte literal hits are not proof of valid instruction boundaries; the bounded scanner qualified PE regions. Indirect/leaf methods and other code outside this band remain unknown. Machine record: tools/agents/pathfinding/m3_001_second_world_ctor_findings.json.

**M3-001 remains READY/incomplete.** Its remaining gates are a nonnull write to the actual simulation+0x160 queue field, populated type-7 queue handler at the SAME queue+0x210, and a producer whose true job type is 7. World zero stores, virtual slot18, incidental literal7 and type3 subtype7 are not proof. No live inputs, game process attachment, memory modifications or custom pathfinder.


## M3-001 continuation — October 20, 2026: +0x160 allocation lifecycle vs simulation queue ownership

**PF22 / native allocator-returned store.** In PE-unwind region `0x89C4F0..0x89C746`, `0x89C50C mov rdi,rcx` retains the receiver, `0x89C600 call 0x14077C230` invokes an allocator and the immediately following `0x89C605 mov qword ptr [rdi+0x160],rax` stores its returned pointer. The stored result may be non-null, but actual successful allocation is not proven from a static call.

**PF23 / same-offset release and zero.** Another routine (`0x89C990..0x89CB27`) reads `[rdi+0x160]` at `0x89CA17`, calls release `0x77C240` at `0x89CA1E` and writes `[rdi+0x160]=rsi` at `0x89CA2A`. `0x89C9D5 xor esi,esi` establishes zero; RSI is nonvolatile on Win64, and no intervening local write redefines it.

**PF24 / exact direct-call chain.** V7 retained instruction-boundary-qualified `0x89EA8D → 0x89C4F0`, `0x89E89D → 0x89C990`, `0xFB524E → 0x89EA80` and `0x89EB20 → 0x89E6F0`. The wrapper at `0x89EA80` passes its own receiver to the allocator routine, and the cleanup wrapper at `0x89E6F0` reaches the release routine. This is a bounded direct-E8 call graph, **not** proof of all indirect callers or the receiver's C++ class.

**PF25 / crucial RVA and allocation distinction.** The wrapper receiver comes from a global factory `0x89E5D0` that requests **`0x1D8` bytes**, returning a pointer used at `0xFB5246..0xFB524E`. Separately, the already verified `hkpWorld` constructor requests **`0x200` bytes**, invokes `hkpMultiThreadedSimulation` constructor `0x089ABC` and stores the simulation pointer at `hkpWorld+0x10`. The addresses **`0x089ABC` and `0x89C605` differ by more than 8 MiB**; their similar names were an initial misleading impression and are explicitly corrected. The factory object's actual RTTI and any alias with the separately allocated simulation are **unknown**. **Do not promote `0x89C605` as a non-null simulation queue-pointer writer.**

**PF26 / stack-frame false positives.** The exact source windows at `0x892C41`, `0x868113` and `0x8DDA75` write `[rbp+0x160]` but their method prologues derive RBP directly from RSP, qualifying these as frame-local destinations (subject to no intervening RBP redefinition), not heap queue fields. The reusable `m3_001_displacement_index.py` records validated RBP-from-RSP ancestry rather than blindly rejecting all RBP offsets.

**PF27 / bounded source index, explicitly incomplete.** In separate source windows over RVA `0x1000..0x400000`, `0x400000..0x800000` and `0x800000..0xC00000`, the index counted **72,625 + 94,801 + 114,831 decoded instruction rows** (band totals, not unique code) and marked **all three bands incomplete** due unqualified/unwind decode gaps. A historical pre-RBP-filter artifact contained **52 syntactic non-RSP +0x160 write candidates**, reduced to **43** after the strict frame-alias filter (3, 28 and 12 by band). These are **not proven non-null writes to the simulation**, merely candidates for data-flow qualification. Output is pinned in `artifacts/m3-001-three-band-index-rbp-qualified-20261020-01.json`; prior write-once artifact `...-3band-displacement-index-20261020-01.json` preserves the pre-filter checkpoint.

**Reproducibility and validation:**
- Four exact-build V7 captures and immutable manifests for allocation, direct callers, wrapper callers and factory setup are pinned by SHA256 and rechecked by `tools/agents/pathfinding/m3_001_verify_field160_lifecycle.py`. All preserved original artifacts had completed/bounded V7 coverage; known pefile warnings were not suppressed.
- Exact-source and four-receipt verifier result at `artifacts/m3-001-field160-lifecycle-qualified-20261020-01.json`, SHA256 `b88f4a368db482cf4c90fb5ed72f26e40f10fd4a895ad89b8137fbadc48cdfaa`. `m3_001_test_field160_lifecycle.py`: **10/10 passed**, exit 0.
- Index improvement in `m3_001_displacement_index.py` and `m3_001_test_displacement_index.py`: **12/12 passed**, exit 0. One test originally used an invalid RVA band (`0x89A000` could not contain `0x089BD7`); the test was corrected *without skipping* and now explicitly verifies the distinct owner/source ranges.
- Additional isolated V7 evidence `artifacts/m3-001-nearby-other-field160-writers-20261020-01.json` distinguishes three RBP frame-local stores; earlier V7 wrapper captures also retain provenance.
- Full machine evidence and test jobs: `tools/agents/pathfinding/m3_001_field160_lifecycle_findings.json`. **This continuation was Manager-executed through Workbridge, with zero new independent AI workers**, so it must not be reported as another multi-agent worker success.

**M3-001 remains READY/incomplete.** Next qualify a non-null assignment to the **same hkpMultiThreadedSimulation+0x160 receiver** (not a separate global factory or stack), identify a nonnull callback for job type 7 at the same queue's `+0x210`, and verify a real type-7 job producer with route/player linkage. Synthetic M4A remains accepted but does not satisfy native M4, M5 live-trial or M6 navigation gates. No game input, process attach, memory modification, or replacement pathfinder was introduced.

## M3-001 continuation — October 20, 2026: adjacent zero-source disambiguation (PF28–PF30)

**PF28 / normal fall-through zero store.** In exact original PE unwind range `0x6BA30..0x6BC69`, instruction `0x6BB81 xor edx,edx` (bytes `33d2`) is immediately followed by `0x6BB83 mov qword ptr [rsi+0x160],rdx` (bytes `48899660010000`). All 133 instructions decode to the original range end. No **direct local** jump/call targeting that store was found by the bounded scanner. This is a **zero write on the qualified normal fall-through path**, *not* a non-null queue-pointer assignment. Unknown indirect/tail entries or other paths are not declared absent; receiver class remains unknown.

**PF29–PF30 / unqualified computed values.** RVA `0x1CEE6` stores computed `RAX` in `[RBX+0x160]` after a conditional pointer arithmetic/test sequence in fully decoded `0x1CE73..0x1CF07`. RVA `0x6B602` stores `RAX` similarly in fully decoded `0x6B500..0x6B626` after `0x6B515 mov rbx,rcx` and a lookup-derived computation. Neither receiver's RTTI/class identity nor its equivalence to the world-created `hkpMultiThreadedSimulation` is established. Neither is promoted as a queue assignment.

**Reusable scanner refinement.** `tools/agents/pathfinding/m3_001_displacement_index.py` now records `adjacentZeroSourceRva` only for a directly adjacent same-GPR `xor/sub reg,reg` source feeding a qword store, and only when a direct local branch/call does not target the store. This prevents the known `0x6BB83` zero-source false positive from being shortlisted as a potential *non-null* pointer write. It is not a general register data-flow proof or whole-program CFG. The historical write-once three-band artifact and its recorded **43** candidates remain unchanged; **no fresh aggregate candidate count is claimed** and no broad rescan was repeated. New machine evidence: `tools/agents/pathfinding/m3_001_adjacent_zero_source_findings.json`.

**Boundary:** Offline original executable only, matched SHA256. No new AI-worker result was accepted; the two attempted OpenCode sessions did not modify files (one model/tool error, one main-repository read permission rejection). This is Manager-directed Workbridge work. **M3-001 remains READY**; same-simulation non-null queue pointer, same-queue type-7 handler, true type-7 producer, and any player navigation linkage are unresolved.

