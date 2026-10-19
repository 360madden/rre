# Rift navigation research — 18 October 2026

## Outcome

The exact current Rift client contains a job-dispatch branch labeled **TtPathfinding**.
The branch selects job type 7, and the dispatcher reaches that type's handler table
through **queue + 0x210**. This is a concrete native-code lead for continued research.
It does not yet establish that the table is populated, what its handlers do, or whether
the player uses it.

The same pass located the click-to-move setting, a routine that emits the stopped-following
message and clears a state field, and existing Havok collision-related names. The research
workflow now produces repeatable, build-bound static evidence in seconds using existing
RiftReader helpers and established libraries. **A working in-game navigator has not been
demonstrated by this pass.**

The project decision remains: investigate and reuse the game's commands, handlers, route
data and collision queries before considering a new pathfinder.

## Exact build and environment

| Item | Value |
| --- | --- |
| Executable | C:\Program Files (x86)\Glyph\Games\RIFT\Live\rift_x64.exe |
| SHA-256 | 7c356c9dde9e12fcbff3c08d953b0630b48b1510a0ffb36e4ec164606e7b17bd |
| File size | 59,963,840 bytes |
| Manifest version | STABLE-1-1169-a-1256556 |
| Preferred static image base | 0x140000000 |
| Installed REA | rea-agents 6.5.0 |
| Ghidra / Java | 12.1.2 / Temurin 21.0.11 |
| Offline Python dependencies | Capstone 5.0.9; pefile 2024.8.26 |
| Isolated research interpreter | C:\work\rre\.venv\Scripts\python.exe |

The host executable's measured SHA-256 matches the RIFT-Lab qualification record.
That permits static analysis of the host file while retaining the VM for later behavior
experiments. An RVA in this report is relative to the module, not a reusable live absolute
address. The preferred image base is for static analysis; a running process can be rebased.

Build qualification source:
C:\rift modding\RiftReader\docs\recovery\player-yaw-build-2026-10-18.json.

## Native findings

### 1. Pathfinding and ray-cast jobs share a dispatcher

| Lead | Exact location | Observed behavior |
| --- | --- | --- |
| TtPathfinding | String RVA 0x2D51598; code reference 0xF4089 | Selected when the job type byte is 7 |
| TtRayCast Query | String RVA 0x2D51560; code reference 0xF4123 | Selected when the job type byte is 3 |
| Generic dispatcher | RVA 0xF3FA4 through 0xF41FF | Obtains a job, labels/times work, and calls a handler |
| Actual indirect dispatch | RVA 0xF41A3 | Selects a handler by job type and subtype |

The decoded data flow is equivalent to the following **analytical pseudocode**:

    type = job_bytes[1]
    subtype = job_bytes[0]
    handlers = read_pointer(queue + 0x130 + type * 0x20)
    handler = read_pointer(handlers + subtype * 8)
    indirect_call(handler, queue, job, other_contract_details_unknown)

For type 7, the table pointer is reached at queue + 0x210; for type 3, at queue + 0x190.
The code also writes a label and an RDTSC timing value into a per-thread-looking event buffer.
This is consistent with profiling of generic job categories. A category's presence can
survive even when a particular application's handlers or submissions are absent.

**What remains unknown:** the queue instance, registration code, non-null handler entries,
job payload layout, route representation, coordinate spaces and player/NPC usage. The first
next step is to resolve registration and submission for type 7. The string itself is not a
function to invoke.

Two aligned direct call sites to the dispatcher were found: 0x8A9E6 and 0x8EFD0.
Their surrounding regions are saved for following the queue's origin.

Evidence:
C:\work\rre\artifacts\navigation-20261018-01\static-navigation-string-references.json,
static-navigation-command-regions.json, and static-navigation-command-callers.json.
Their SHA-256 values are preserved in C:\work\rre\docs\navigation-findings.json.

### 2. Follow-state clearing is now a specific native lead

The routine rooted at **RVA 0x534200** references the message
"You have stopped following [%TARGET_TOKEN]". It initially checks a qword at
this + 0xB60 and clears that qword at RVA 0x53494F. Sixteen aligned direct call sites
were found, including several compact routines near 0x71B1F0–0x71B5F8.

This gives us a candidate for tracing the game's own cancellation behavior. It does not
identify the receiver object or prove that clearing this field alone stops movement.
The function has additional formatting, notification and state-processing calls.

The prototype should reach cancellation through a demonstrated game input or command.
It should not write this field or call this native routine based on this evidence alone.
Whether click-to-move and follow share cancellation remains unresolved.

The separate string **setFollowMode** is weaker evidence for this purpose. One implementation
at RVA 0xDA8B00 accepts values 1 or 2, stores a field at +0x294 and invokes another routine.
Its object identity and connection to character following are unproven.

### 3. Click-to-move enablement has a static settings mapping

**Misc_EnableClickToMove**, string RVA 0x26851F8, is referenced by settings code.
At RVA 0xBC1D71–0xBC1DA6, the UI code reads a byte at:

    settings = read_pointer(module + 0x33136F0)
    candidate_enable_click_to_move_byte = read_byte(settings + 0x146)

This is a static association between a setting label and a byte supplied to the UI.
The current value was not read, and the correct setter/persistence contract was not examined.
Use the existing settings UI or independently qualified readback to confirm enablement
before interpreting a failed ground click as a pathfinding failure.

### 4. Collision support has exact-build name anchors

The existing RTTI-name matcher found names including hkpCharacterProxy,
hkpWorldRayCaster, hkpWorldLinearCaster, hkpKdTreeWorldLinearCaster and several
collision filters/dispatchers. Relevant name RVAs include:

| Name | RVA |
| --- | --- |
| hkpCharacterProxy | 0x2F1B1A8 |
| hkpWorldRayCaster | 0x2F18FD0 |
| hkpWorldLinearCaster | 0x2F190F8 |
| hkpKdTreeWorldLinearCaster | 0x2F196C0 |

These are **name-pattern matches**, not verified vtables or class layouts. They do not
establish which object controls the player. Follow a concrete active query to identify
endpoints, shape/radius, collision layers, hit point/normal, and result semantics.

The bounded text search found 147 matching strings. Zero matches for navmesh or hkai in
this particular search do not establish absence: the scan covers printable ASCII and
ASCII-range UTF-16LE in non-executable PE sections, with a restricted RTTI-name pattern.

## What the existing movement work already gives us

Current position and body yaw have qualified prior evidence. Player and selected-target
API telemetry, advancing-source checks, screenshots and bounded keyboard pulses already
exist in RiftReader. These should be reused.

The newly followed **0x6865E0 → 0x687840** chain performs coordinate and orientation
queries and copies values into several cached fields. The writer rooted at **0x687250**
applies source position/orientation data, including quaternion-to-matrix-like arithmetic.
These observations support a pose/transform synchronization hypothesis.

They do not identify the obstacle solver. In particular, **component +0xD8 is not established
as a persistent player-selected navigation goal**. The dispatcher can overwrite it with
the same queried position placed in +0x48 and +0x88.

Prior wall-slide evidence already rejects treating projected-target minus current-position
as actual velocity: the candidate had the wrong Z sign and about 62.5 degrees of directional
error while the player slid along a wall. Preserve this rejection. For a first behavior
prototype, observed displacement over qualified sample time can measure progress without
requiring discovery of a native velocity field.

Prior sources:

- C:\rift modding\RiftReader\docs\workflow\native-motion-recovery-result-2026-10-18.md
- C:\rift modding\RiftReader\docs\workflow\player-yaw-recovery-result-2026-10-18.md
- C:\rift modding\RiftReader\.riftreader-local\motion-recovery\20261018\analysis-static-native-motion.json

Other rejected shortcuts remain rejected: the old player-centered +/-40 bounds were not a
fixed destination; record-navmesh.py builds a custom proximity graph; nav8.py supplies
custom A*. Those artifacts do not prove that we have extracted Rift's own navigation mesh.

## Working research workflow

Three small local tools now support iteration:

| Tool | Role |
| --- | --- |
| C:\work\rre\tools\rea-session.mjs | One bounded official REA MCP session, queued static requests, saved responses, export and close |
| C:\work\rre\tools\inspect-navigation-static.py | Existing RiftReader section/summary helper, pefile unwind ranges/chains, Capstone listings and qualified direct-call candidates |
| C:\work\rre\tools\inspect-navigation-names.py | Existing RiftReader RTTI-name matcher, text leads and bounded string-reference qualification |

Both Python tools verify the exact binary and existing-helper hashes. Outputs use new
filenames instead of replacing existing evidence. The imports suppress bytecode writes
to the referenced RiftReader tree. Capstone and pefile were installed in the isolated RRE
environment because they were absent from the inspected existing environments.

Observed job durations on this PC were approximately 0.7 seconds for the initial name
search, 5.2 seconds for the initial region pass, 5.5 seconds for linked regions, 6.4 seconds
for string references, and 6.8 seconds for direct callers. These are individual run timings,
not performance guarantees or warmed-cache benchmarks.

A reproducible command set and request profile are in C:\work\rre\docs\navigation-workflow.md.
Keep original binaries and generated outputs out of Git; keep code, profiles, findings,
rejections and artifact hashes in Git.

### REA result and limitation

Two REA 6.5.0 sessions successfully admitted the exact file and reached Ghidra whole-program
analysis. Each first analysis query then hit the configured **450-second startup deadline**.

The first profile disabled Stack and Decompiler Parameter ID. Its diagnostic included a
Decompiler Switch Analyzer restart message. The second additionally disabled **Decompiler
Switch Analysis**, whose exact name/default were verified from the installed Ghidra source ZIP.
That second profile also timed out. The log does not identify a proven root cause.

Both sessions exported and closed successfully, with **zero REA analysis evidence records**.
The successful instruction and string findings in this report came from the explicitly
identified offline libraries/helpers, not REA decompilation. No third automatic import was run.
Seeds run before whole-program analysis; they do not limit it to the seeded functions.
Exported REA query snapshots do not preserve a warm Ghidra database.

### Static coverage limits

PE exception entries describe unwind regions. The first pass exposed only pieces of some
larger routines; the second followed actual UNW_FLAG_CHAININFO links. Complete linked-region
traversal is still not proof of a complete control-flow graph.

All selected regions in the linked-position and command-region reports were decoded through
their captured windows. One broader caller, rooted at 0x695810, contains data-like bytes near
a switch table; linear decoding stopped at 0x696921 before the unwind-region end 0x6969EC.
Its broader control flow remains unresolved. The aligned call-site prefixes used in that
region occur earlier.

The direct-call candidate search is capped at 64 candidates per target. String references
cover common x64 RIP-relative LEA encodings and stored absolute pointers, not all possible
reference encodings. Existing helper register/field labels are candidates, not full data-flow
analysis. Leaf functions without unwind entries are left unresolved rather than assigned
guessed boundaries.

## Next prototype experiment

C:\work\rre\docs\native-navigation-experiment.json contains the prepared experiment:

1. Verify a nearby ground destination activates native movement and establish actual
   cancellation in an uncluttered scene.
2. Observe a single native destination request on clear ground.
3. Observe a single native destination request whose direct route crosses a wall with
   a visible accessible opening.

The trajectory must be observed without the old C2M runner's re-aiming, keyboard presteps
or custom detours, so any route through the opening can be attributed to the game's behavior.

The existing guest entry point is
C:\rift modding\RiftReader\tools\riftreader_workflow\game_session.py.
Its observe path provides reviewed screenshots and advancing, identity-bound readback.
Its live run path currently supports only short W/A/S/D pulses.

The existing VNC mouse leaf demonstrates transport, but explicitly limits itself to UI
actions and says never to use it for game movement. A supervised gameplay mouse action must
reuse that transport within the current game freshness/recovery flow. Controller pause,
mouse-up, key-up and a script timeout do not by themselves cancel latched C2M or follow.

Selected-target coordinates are already represented by
observation.readback.typedApi.snapshot.target, with entity and per-field statuses.
They are optional current-session API telemetry, not proof of a native target object.
Target radius/name are not in the current typed guest contract. Approach-point selection
will need valid surface/height and a practical stopping distance once basic travel is working.

RiftReader's AGENTS.md explicitly requires approval for live game input and states that
autonomy alone is not live-input approval. This pass performed offline research only.
No in-game navigation success, stopping success, or route validity is claimed.

## Priority for the next research pass

1. Resolve registration and submission for job type 7 and the queue +0x210 handler table.
2. Trace gameplay consumers of the C2M settings byte into destination formation and any
   ray-cast or pathfinding job submission.
3. Trace the qualified callers of 0x534200 to an actual game cancellation gesture and
   establish separately whether it also stops C2M.
4. Qualify the C2M setting and one native behavior experiment using existing telemetry.
5. Identify a useful native ray/sweep query and any reusable route representation.
6. Resolve the Ghidra startup bottleneck with a documented change or supported persistent
   analysis workflow before another full import.

A new pathfinder is not the default outcome of an import timeout or an inconclusive
behavior test.
