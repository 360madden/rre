# Collision and obstacle-query reuse - 2026-10-18

The exact build contains concrete native ray and linear-cast implementations,
not just Havok name strings. This pass links the requested names to candidate
RTTI/vtables and aligned table-installation code, identifies endpoint-like inputs,
filter calls and native callers. **No query is yet qualified as player clearance,
and no callable integration contract or in-game navigation success is established.**

## Scope and provenance

- Lane/worktree/branch: `collision`, `C:\work\rre-worker-collision`, `research/nav-collision`.
- Starting commit: `c7815b762dbdfe4d681a96cd14a69f658668595c`.
- Read instructions and baseline: `AGENTS.md`, `docs/agent-coordination.md`,
  `docs/navigation-research-2026-10-18.md`, `docs/navigation-findings.json`,
  `docs/navigation-workflow.md`.
- Source executable: `C:\Program Files (x86)\Glyph\Games\RIFT\Live\rift_x64.exe`.
- Rechecked SHA-256: `7c356c9dde9e12fcbff3c08d953b0630b48b1510a0ffb36e4ec164606e7b17bd`;
  59,963,840 bytes; preferred base `0x140000000`. All addresses below are **RVAs**.
- Baseline manifest version: `STABLE-1-1169-a-1256556`; version metadata was not
  independently re-read. Exact file identity was verified by hash.
- Methods: original RiftReader RTTI-name/section helpers, existing
  `tools/inspect-navigation-names.py` and `tools/inspect-navigation-static.py`,
  pefile 2024.8.26 and Capstone 5.0.9 in the preexisting RRE environment.
- No target execution, process attach, live input, memory write, VM control,
  REA/Ghidra import, dependency installation or network operation.

[collision.json](collision.json) contains 12 hashed source paths, 25 byte-verified
strings, 28 complete captured unwind regions (7,216 bytes / 1,666 decoded instruction
rows), references and bounded RTTI records. Evidence is retained there rather than
in the shared main-worktree artifacts. Its `findings` IDs C1-C8 map to this report;
`evidence.nativeRegions` is keyed by each region's `beginRva` for lookup.

## Directly observed code and data

### Type-3 work is a dispatch category, not a clearance contract (C1)

At `0xF3FD7`, the dispatcher reads job byte 1. Its decrement/branch sequence selects
`TtRayCast Query` (string `0x2D51560`, LEA `0xF4123`) for **type 3**. Type 2 selects
`TtCollision Query` (string `0x2D51548`, LEA `0xF4148`). The label is written to a
buffer followed by an RDTSC timing value; this is profiling-like machinery.

At `0xF4184..0xF41A3`, native code reads type and subtype, then calls:

```text
handler_table = *(queue + 0x130 + (job[1] << 5))
handler = *(handler_table + 8 * job[0])
// rcx = queue; rdx = &job; other call-contract details unqualified
```

Type 3 therefore reaches **queue+0x190**; type 2 reaches **queue+0x170**.
This pass does not resolve either table's registration, entries or producers.
It does not connect these jobs to the synchronous query implementations below.

### Havok names have concrete metadata/code associations (C2, C6)

The original name matcher is reused. A small lane helper additionally tests
name-minus-16 descriptor candidates, six-dword locator records with signature 1
and a matching self-RVA, and stored preferred-base pointers to those records.
It reads at most eight executable-pointer slots, stopping at the first non-code
pointer. These are **RTTI/vtable interpretations of observed bytes**, not a full
hierarchy or class-layout recovery.

| Name | Name RVA | Locator candidate RVA | Table candidate RVA | Aligned code association |
| --- | --- | --- | --- | --- |
| hkpWorldRayCaster | 0x2F18FD0 | 0x2D75000 | 0x2723BC8 | LEA 0x78BAB; stack store 0x78BCB; callback pointer 0x9FC24 |
| hkpWorldLinearCaster | 0x2F190F8 | 0x2D75520 | 0x2723D50 | LEA 0x798E1; stack store 0x798E8; callback pointer 0xA1B48 |
| hkpKdTreeWorldLinearCaster | 0x2F196C0 | 0x2D76248 | 0x27259F8 | LEA 0x8EBB7; stack store 0x8EBBE; callback pointer 0xA2700 |
| hkpCharacterProxy | 0x2F1B1A8 | 0x2D78880 | 0x272B7D8 | stores at 0xCCE01 and 0xCCEC8 |

The character-proxy name also has locator offsets `0x10` and `0x18`, with table
candidates `0x272B7A0` and `0x272B770`. At `0xCCDE8`, code installs all three tables
at receiver offsets `+0`, `+0x10`, `+0x18`, initializes array-like fields and calls
`0xCBE18`. At `0xCCE9C`, code reinstalls the tables, releases references/arrays and
replaces the tables again. Initialization/destruction roles are inferred from
these operations. The receiver's ownership by the player is unknown.

The initial name-address reference scan found no direct references to the three
requested RTTI strings under its LEA/absolute-pointer coverage. The relative-dword
metadata walk recovered the associations above. Zero name xrefs was not absence
of native implementation. Complete vtable extents/method names remain unproven.

### Ray implementation: two vectors, filter and shape callback (C3)

- `0x78B1C` references `TtworldCastRayCollector` at `0x78B50`; its fallback branch
  constructs the table-bearing object and calls `0x9FD68` at `0x78BD0`.
  An alternate path calls `0x8E744` at `0x78B8E` and is not followed here.
- `0x9FD68` preserves the input pointer at receiver `+8`, an output-like pointer
  at `+0x18`, and an optional filter-like subobject pointer at `+0x10`.
  At `0x9FE36`, it calls another object's virtual slot `+0xB8` with the callback object.
- Callback `0x9FC24` invokes filter virtual `+8` at `0x9FC7C`. If accepted, it
  subtracts a collidable transform's translation (`+0x30`) and applies rotation-like
  SIMD arithmetic to two vectors, storing them at callback receiver `+0x30/+0x40`.
  The second vector is input `+0x10`; the input record indexing uses stride `0x30`.
- `0x9FD41..0x9FD44` copies input dword `+0x24` to callback receiver `+0x50`;
  `0x9FD4B` calls shape virtual `+0x48`.

**Inference:** input `+0/+0x10` are ray endpoints; the arithmetic is consistent
with world-to-local transformation; `+0x24` is filter-info-like. Native axes,
units, output layout and bit meanings are not qualified. An output scalar at
`+8` is read back (`0x9FD4E`); treating it as a hit fraction requires further proof.

### Linear casts and phantom cast: existing obstacle-query leads (C4-C5)

`0x79820` references `TtworldLinCast` at `0x7985C`. Its fallback branch constructs
the linear-caster object and calls `0xA1BE8` at `0x7994F`; the alternate branch calls
`0x8EBA8`, which installs the Kd-tree caster table and calls `0xA27A8`.

`0xA1BE8` subtracts the collidable transform translation from input vector `+0`
(`0xA1CA1..0xA1CAF`), stores the difference at receiver `+0xA0` and its XYZ length
at `+0xB4` (`0xA1CD8..0xA1CE8`). It calls a shape virtual method at `+0x38`, then
another object's virtual `+0xD8` at `0xA1D91`. The input is destination-like;
shape/radius and the owning object's identity remain unknown.

Callback `0xA1B48` rejects its own collidable (`0xA1B6A..0xA1B71`), invokes filter
virtual `+8` (`0xA1B82`), then chooses a callback using a 32-stride type-pair table
at dispatcher `+0x2B0` and calls it at `0xA1BC5`. The Kd-tree callback `0xA2700`
shows a similar filter/type-pair dispatch pattern. **This dispatch table is not
an established gameplay layer mask.**

`0x986AC` references `TthkpAabbPhantom::linearCast` at `0x986E8`. It computes a
similar vector difference and XYZ length, loops pointers at receiver `+0x110`
using count `+0x118`, applies filter virtual `+8` at `0x98831`, rejects self and
uses a type-pair-selected callback at `0x9887D`. This is a useful bounded sweep
lead. It does not establish player capsule clearance or route walkability.

### Collision filters/layers remain partly unresolved (C7)

The `hkpGroupCollisionFilter` name (`0x32DBBF0`) links to multiple locator/table
candidates. Its secondary table `0x2D686D8` (subobject offset `0x18`) contains
`0x146BC0` and `0x146B60`. These obtain filter-info-like words through virtual
`+0x20` or collidable `+0x2C`, adjust the receiver by `-0x18` and call `0x146898`.

The existing static wrapper reports **no containing PE unwind entry** for
`0x146898`; it is left undecoded rather than assigned a guessed boundary.
Strings `collisionFilterInfo` (`0x2D5DF98`), `defaultCollisionFilterInfo`
(`0x2D5DCE0`) and `collisionLookupTable` (`0x2D5DDE8`) are additional data leads.
No Rift-specific layer names, bit allocation or player filter values are established.
The reference at `0x14044A` to table `0x2D686D8` has no unwind boundary verification
and is retained only as an unqualified candidate, not a confirmed constructor.

## Caller coverage and camera/display distinction (C8)

All seven direct caller candidates below were instruction-boundary verified by
the existing wrapper. These are bounded direct-call results, not an exhaustive
call graph or proof of execution.

| Callee | Caller site RVAs | Role established? |
| --- | --- | --- |
| 0x78B1C ray wrapper | 0x1460FF, 0x817B1B, 0x13D44DD | Unclassified |
| 0x79820 linear wrapper | 0x145D4D | Unclassified |
| 0x986AC phantom cast | 0x13D2590, 0x13D26FD, 0x13D276F | Shared unwind-chain root 0x13D2400; unclassified |

The ray caller `0x13D44D0` compares an output-like `+8` scalar with a constant and
returns a Boolean; that alone does not identify clearance. The phantom caller
contains collector/count checks and copies scalar/vector results to optional
outputs (`0x13D2595..0x13D25DD`, `0x13D27B9..0x13D281A`); these do not yet prove
hit point/normal meanings. All unwind-chain regions for roots `0x8178B0` and
`0x13D2400` were captured, without a gameplay ownership conclusion.

`Camera_WaterCollision` (`0x2685040`) has aligned settings references at `0xBBB487`,
`0xBBB4AF`, `0xBC11B5`; it was not connected to these casts. Camera collision,
screen picking and player clearance cannot be treated as interchangeable.
The existing RiftReader `scripts/world-to-screen.py:220-269` explicitly describes
`screen_to_world_ground` as approximate C2M math, intersecting a horizontal plane.
It was read, never imported/executed. Its ray is not native obstacle evidence.

## Evidence classes, validation and limits

- **Direct observations:** exact file/strings, decoded instructions, pointer values,
  table stores, filter/indirect calls and qualified direct callers retained in JSON.
- **Inferences:** RTTI/COL/vtable interpretation, constructor/destructor roles,
  endpoint/destination-like vectors, world/local conversion and filter-info meaning.
- **Existing documented runtime evidence:** no new runtime data. Baseline wall-slide
  evidence rejects projected-target minus current position as actual velocity; it
  does not qualify any cast found here. No player-centered volume, custom proximity
  graph, or cached component `+0xD8` is promoted to a native goal/navmesh.
- **Unresolved:** type-3 registration/payload; caller ownership; shape/radius;
  layer bits; coordinate units; hit semantics; lifetime/thread/lock contracts.
- Every retained window decoded to its end; each run exhausted its pending queue.
  Linear decoding and unwind chains still do not establish a complete reachable CFG.
  Direct callers are capped at 64 per target; indirect/tail callers can be missed.
  The string/reference search has the baseline's restricted encoding/LEA coverage.
- The metadata helper is bounded to five names/eight code-pointer slots per table.
  It is not a new instruction decoder or collision engine.

Validation command (read-only, no bytecode output):

```powershell
& C:\work\rre\.venv\Scripts\python.exe -B tools/agents/collision/verify.py --verify docs/agents/collision.json
if ($LASTEXITCODE -ne 0) { throw 'Collision evidence verification failed' }
```

Validation passed: Python AST/JSON parsing, all seven caller qualifications, the
exact-build verifier, and rejection of deliberately altered instruction bytes and
RTTI links. Temporary collection/negative-test files were removed.

The verifier checks the executable hash, hashed sources, all retained window hashes
and instruction bytes, reference/string bytes, and freshly reconstructed metadata
links. This validates provenance/bytes, not semantic or runtime correctness.
The JSON records wrapper paths, reference targets and anchor sets needed to rerun
the existing tools with `--depth 0 --follow-unwind-chains` and the baseline hashes.

## Concrete next validation

1. Offline: trace callers above `0x13D2400`, `0x8178B0` and `0x13D44D0`; identify
   owner/type, input construction and output consumers before classifying clearance.
2. Offline: resolve type-3 registration at queue `+0x190` and a producer/payload;
   keep that connection separate from the synchronous cast implementations.
3. Offline: qualify leaf `0x146898` with boundary-aware analysis and trace the actual
   filter instance/values. Do not infer gameplay layers from the type-pair dispatch.
4. Only in a separately authorized future game-world experiment: compare a qualified
   player-owned query on clear ground/wall/camera-only changes, recording endpoints,
   shape/radius, layers, self-exclusion, coordinate space and hit outputs.

The most useful next offline target is **the phantom-cast caller at 0x13D2400**:
it reaches a concrete cast and consumes results, making it a better starting point
for ownership/contract tracing than a Havok class name alone.

## Completion and local-commit blocker

The three owned files are complete and validated. `git add` was attempted with
only those paths, but Git could not create
`C:/work/rre/.git/worktrees/rre-worker-collision/index.lock`: **Permission denied**.
Linked-worktree metadata is outside this worker's writable root. No commit SHA
exists, the staged diff check was not reached, and no permission escalation,
Git-identity change or alternative index/worktree workaround was attempted.
The manager can stage/commit the three files from its authorized context.
Temporary collection and negative-test files were removed; no persistent jobs
were started. No outside source files were changed.

## Follow-up 2026-10-19 — M3-002 (manager-verified worker evidence)

The assigned Codex worker stopped with exit code 1 when its usage allowance was exhausted. It saved a dated `followUps` evidence record in [collision.json](collision.json), and the manager independently ran [m3_002.py](../../tools/agents/collision/m3_002.py) successfully (job `rre-resume-qa-collision-new-20261019-01`, exit 0). The historical report above is unchanged.

**Exact build:** SHA-256 `7c356c9dde9e12fcbff3c08d953b0630b48b1510a0ffb36e4ec164606e7b17bd`, base `0x140000000`; addresses below are RVAs. Evidence covers **12 PE unwind regions / 613 instruction rows**, **two 96-byte fixed leaf windows** without asserted function boundaries, and **ten data reads**. The two captured queries and all source/byte hashes are retained under `tools/agents/collision/_m3_002_query1.json`, `_m3_002_query2.json` and the JSON report.

### Qualified findings and limits

- The phantom-cast caller around RVA `0x13D2400` stages a destination-like vector, tolerances and a filtered cast. Caller ownership, world frame and applicability to player movement are unknown.
- Candidate filtering includes a virtual callback and rejection of null shapes or the source object. The observed shape-type dispatch is **not** a qualified Rift walkability-layer mask.
- The all-hit collector appends **0x40-byte records** and sorts by a scalar at `+0x1C`; a separate closest-contact collector retains a smaller scalar and copies two vectors. Point/normal identities, direction and scalar units remain hypothetical.
- The all-hit and external-collector caller branches expose **different scalar behavior**. A universal hit-fraction result contract is rejected by these code paths.
- No complete route, player-owned clearance query, native navigation invocation or in-game success was established.

**Independent verification:** `C:\work\rre\.venv\Scripts\python.exe -B tools/agents/collision/m3_002.py --verify docs/agents/collision.json` returned `verified: true`, 12 regions, 613 rows, two leaves and ten reads. It validates the exact saved bytes and provenance, not active game behavior.

**Next focused task:** identify the actual caller/object owner for `0x13D2400`, then qualify filter implementation, layer values and output consumers. Do not connect this cast to type-3 job dispatch without evidence; do not build a replacement pathfinder as an automatic fallback.
