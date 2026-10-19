# Rift native-navigation research workflow

## Purpose and current status

This workflow continues the existing RiftReader investigation while keeping lasting
research in C:\work\rre. Its first objective is to reuse Rift's native movement,
pathfinding, route and collision facilities. It does not implement a new pathfinder.

The completed pass found a type-7 TtPathfinding job-dispatch category, a separate ray-cast
category, a follow-state clearing routine, a click-to-move settings mapping and collision
name anchors. It has not demonstrated player pathfinding or a usable native call contract.

Read these entry points first:

- C:\work\rre\docs\navigation-research-2026-10-18.md — findings and interpretation.
- C:\work\rre\docs\navigation-findings.json — exact evidence, hashes and unresolved claims.
- C:\work\rre\docs\navigation-investigation.json — investigation questions and current status.
- C:\work\rre\docs\native-navigation-experiment.json — prepared behavior experiment.
- C:\work\rre\docs\rea-import-attempt-2026-10-18.json and
  C:\work\rre\docs\rea-import-attempt-2026-10-18-02.json — failed import profiles and diagnostics.

## Ownership and input qualification

Use the native installation's executable for offline analysis. Its measured SHA-256
matches the existing RIFT-Lab build qualification. Keep later behavior experiments in the
already configured VM with fresh identity and observation checks.

The commands below are for this exact build:

~~~text
Binary: C:\Program Files (x86)\Glyph\Games\RIFT\Live\rift_x64.exe
Manifest: STABLE-1-1169-a-1256556
SHA256: 7c356c9dde9e12fcbff3c08d953b0630b48b1510a0ffb36e4ec164606e7b17bd
Preferred image base: 0x140000000
~~~

RVAs belong to that file. Static virtual addresses in REA request examples use its
preferred image base. A live process can load elsewhere and must be qualified separately.
If the executable or an imported helper changes, review the change and requalify it;
do not edit an expected hash merely to silence a mismatch.

RRE owns new tools and notes. Existing RiftReader files are read-only inputs to this pass.
C:\work\riftreader2 belongs to other work and is outside this workflow.

## Local Python environment

The completed run created C:\work\rre\.venv with C:\Python314\python.exe and installed the
two pinned wheels listed in C:\work\rre\requirements-static.txt:

- Capstone 5.0.9
- pefile 2024.8.26

Reuse that interpreter. No existing global or RiftReader environment was changed.
If reconstructing a missing environment, the setup used was:

~~~powershell
& 'C:\Python314\python.exe' -m venv 'C:\work\rre\.venv'
& 'C:\work\rre\.venv\Scripts\python.exe' -m pip install --only-binary=:all: -r 'C:\work\rre\requirements-static.txt'
~~~

These are dependency installation steps, not prerequisites to repeat on every query.
Package references: https://pypi.org/project/capstone/5.0.9/ and
https://pypi.org/project/pefile/2024.8.26/.

## Reproduce the focused offline research

The following PowerShell examples use literal argument arrays. Run the shared setup once
in the same PowerShell session, then choose the relevant query. The examples are for a new
output directory so the original evidence is preserved.

~~~powershell
$riftNavPython = 'C:\work\rre\.venv\Scripts\python.exe'
$riftNavOutput = Join-Path 'C:\work\rre\artifacts' ('navigation-replay-' + [DateTime]::UtcNow.ToString('yyyyMMddTHHmmssfffZ'))
New-Item -ItemType Directory -Path $riftNavOutput -ErrorAction Stop | Out-Null
$riftNavCommonArgs = @(
    '--binary'
    'C:\Program Files (x86)\Glyph\Games\RIFT\Live\rift_x64.exe'
    '--expected-sha256'
    '7c356c9dde9e12fcbff3c08d953b0630b48b1510a0ffb36e4ec164606e7b17bd'
)
~~~

### Names and known string references

This imports the existing RiftReader RTTI-name matcher. The wrapper adds a bounded text
search and qualifies common RIP-relative LEA references using Capstone and PE metadata.

~~~powershell
$riftNavNamesArgs = @('C:\work\rre\tools\inspect-navigation-names.py') + $riftNavCommonArgs + @(
    '--helper'
    'C:\rift modding\RiftReader\scripts\anti-re\rtti_class_scanner.py'
    '--expected-helper-sha256'
    '3636e5ca9c39318c27a7c5fdbccfd01e3258ef079139a0d9df64f49961448331'
    '--reference-rva'
    '0x2D51598'
    '--reference-rva'
    '0x2D51560'
    '--reference-rva'
    '0x26851F8'
    '--reference-rva'
    '0x2646388'
    '--reference-rva'
    '0x2665D08'
    '--output'
    (Join-Path $riftNavOutput 'names-and-string-references.json')
)
& $riftNavPython @riftNavNamesArgs
if ($LASTEXITCODE -ne 0) { throw 'Navigation name/reference query failed.' }
~~~

The five string targets are TtPathfinding, TtRayCast Query, Misc_EnableClickToMove,
the stopped-following message, and setFollowMode. Omitting the reference options retains
the names/text search alone.

A match is a lead. Zero matches do not establish absence. Coverage is printable ASCII and
ASCII-range UTF-16LE in non-executable sections, a restricted MSVC RTTI-name pattern,
common x64 RIP-relative LEA encodings, and stored absolute pointers. Check each reference's
instructionBoundaryVerifiedFromPeRange field before treating it as an aligned instruction.

### Native dispatch, follow clearing and their callers

This imports the existing RiftReader executable-section reader, summary helper and direct
call candidate generator. Capstone and pefile supply established decoding and PE metadata.

~~~powershell
$riftNavStaticBase = @('C:\work\rre\tools\inspect-navigation-static.py') + $riftNavCommonArgs + @(
    '--helper'
    'C:\rift modding\RiftReader\scripts\postupdate_static_access_chain.py'
    '--expected-helper-sha256'
    'c62d729ea027c271c8b4113c927ab039ae760d6db20f479166e7769dd4891319'
    '--follow-unwind-chains'
)
$riftNavCallersArgs = $riftNavStaticBase + @(
    '--rva'
    '0xF3FA4'
    '--rva'
    '0x534200'
    '--caller-rva'
    '0xF3FA4'
    '--caller-rva'
    '0x534200'
    '--depth'
    '0'
    '--output'
    (Join-Path $riftNavOutput 'dispatch-and-follow-callers.json')
)
& $riftNavPython @riftNavCallersArgs
if ($LASTEXITCODE -ne 0) { throw 'Navigation caller query failed.' }
~~~

For focused pose/transform and settings inspection:

~~~powershell
$riftNavPoseArgs = $riftNavStaticBase + @(
    '--rva'
    '0x6865E0'
    '--rva'
    '0x687840'
    '--rva'
    '0x687250'
    '--rva'
    '0xBC1D71'
    '--depth'
    '0'
    '--output'
    (Join-Path $riftNavOutput 'pose-and-c2m-settings.json')
)
& $riftNavPython @riftNavPoseArgs
if ($LASTEXITCODE -ne 0) { throw 'Navigation pose/settings query failed.' }
~~~

Use depth 1 or 2 only when the next direct callees answer a specific question. The wrapper
limits each run to 40 unwind regions and 16 KiB per region and records queueRemaining,
unresolvedAnchors, windowTruncated and instructionDecodingCoversWindow. Direct-call
candidate generation is capped at 64 per requested target.

PE exception entries describe unwind regions, not guaranteed complete source functions.
Following UNW_FLAG_CHAININFO improves coverage of split routines but does not recover a
complete control-flow graph. Linear instruction alignment is not proof of runtime reachability.
Leaf functions without exception entries remain unresolved. The reused helper's field
labels are candidates because its register tracking is not full data-flow analysis.

Both tools suppress bytecode writes before importing the existing helpers. They read the
game file without launching it, attaching to a process, invoking game functions or sending input.
They refuse to replace an existing output file.

## REA session workflow

C:\work\rre\tools\rea-session.mjs uses the official MCP client already installed with REA.
One local Node process keeps one REA stdio session, reads a sorted request queue, saves full
tool responses, exports the evidence bundle, requests a snapshot and closes the binary.
It verifies the target hash, x64 PE identity and installed REA version first.

The saved REA 6.5.0 profiles are historical failed attempts:

| Profile | Disabled analyzers | Outcome |
| --- | --- | --- |
| rea-session-options.json | Stack; Decompiler Parameter ID | First analysis query exceeded 450 seconds |
| rea-session-options-navigation2.json | Same two; Decompiler Switch Analysis | First analysis query exceeded 450 seconds |

Both reached whole-program analysis and returned provider_timeout. Both exported and
closed successfully with zero analysis evidence records. The exact switch analyzer name
was verified from the installed Ghidra source ZIP before the second attempt. Its removal
did not establish or solve the startup bottleneck.

Do not rerun either profile unchanged. A further import needs a documented material setup
change, such as a verified supported persistent analysis workflow or a specifically diagnosed
startup fix. More memory is an untested possibility, not a demonstrated remedy.
The installed launcher does not expose a verified function-only/no-analysis option.
Seed functions do not restrict whole-program analysis, and an exported query snapshot is
not a warm Ghidra database.

After a justified setup change, copy a profile to a new file, choose a new outputDirectory,
and record the reason for the change. The runner refuses an existing status.json.
Its executable invocation is:

~~~text
Executable: C:\Program Files\nodejs\node.exe
Arguments: C:\work\rre\tools\rea-session.mjs <absolute-new-options.json>
Working directory: C:\work\rre
Workbridge timeout: 600 seconds
~~~

The process's configured lifetime is at most 550 seconds; queries and export/close have
individual budgets. It stops the queue on a tool error so that a failed import cannot
silently start another one.

Place request files under the new outputDirectory\requests before starting the runner.
The tracked C:\work\rre\docs\rea-navigation2-requests.json supplies filenames and payloads
for the second attempt; remove its file property when writing each request's JSON body.
That list is a historical request set, not evidence that every request executed.

A request has this shape:

~~~json
{
  "tool": "xrefs",
  "arguments": { "address": "0x142d51598" }
}
~~~

Optional timeoutMs is per request. The first analysis operation may trigger full import;
a short request timeout does not make the import selective. After the useful requests,
a lexically last file such as 99-finish.json containing {"finish": true} closes the session
without waiting for the overall time budget.

Review status.json, responses, analysis-profile.json, export-receipt.json and
close-receipt.json. A connected session or admitted file is not a successful analysis query.
The runner's method and provenance must remain distinguishable from the separate Python
offline results.

Official REA reference:
https://github.com/morluto/rea/blob/main/docs/native-investigation.md

## Concrete next investigation

1. Follow queue construction and table population from the dispatcher at RVA 0xF3FA4.
   Resolve queue+0x210 for type 7, then find producers and the actual job payload/output.
   The two currently qualified dispatcher call sites are 0x8A9E6 and 0x8EFD0.
2. Follow gameplay consumers of the settings byte at the object obtained from
   [moduleBase+0x33136F0], offset +0x146. Determine how an enabled ground click forms
   a destination and whether that path reaches the ray-cast or pathfinding job system.
3. Trace the qualified callers of 0x534200 to a normal input action that cancels
   following; establish separately whether it cancels C2M.
4. Once an active collision query is identified, record coordinate space, endpoints,
   sweep shape/radius, collision layers, hit point/normal and return semantics.
5. Connect an observed native behavior or handler to player travel before proposing
   an integration. Preserve negative and inconclusive results.

The component +0xD8 vector is not a verified navigation goal. Existing wall-slide evidence
also rejects treating projected-target minus current-position as actual velocity.
Use qualified position differences over advancing sample time to measure prototype progress.

## Prepared behavior experiment and execution boundary

The experiment JSON starts with movement activation and genuine in-game cancellation in
an uncluttered scene, then a clear-ground baseline, then a wall with an accessible opening.
Each observation uses one native destination request without the old runner's custom
re-aiming, keyboard presteps or detours.

Reuse the existing RiftReader game-session screenshots, process binding, advancing player
readback and optional selected-target telemetry. The current supervised input path supports
short W/A/S/D pulses. Its UI-only VNC mouse leaf is transport to reuse within a supervised
gameplay flow; it is not already a qualified gameplay-click action.

A controller pause, key release, mouse release or script deadline does not by itself cancel
latched native movement. The experiment's observation budget is not a movement-duration bound.
The cancellation mechanism and fresh scene review must exist before an obstacle run.

C:\rift modding\RiftReader\AGENTS.md requires explicit approval for live game input and
states that autonomy alone does not provide that approval. No live-input or debugger
experiment was performed in this pass. This restriction does not block the static steps above.

## What is already verified

The Python wrappers completed real queries against the exact binary and produced six saved
static artifacts. The core linked-position and command-region windows decoded through
their captured ends. One broader caller region stops before its exception-range end and
is explicitly recorded as incomplete. See the findings manifest for hashes and coverage.

REA connected, admitted the target, attempted import twice, preserved its diagnostics,
exported and closed. It did not produce usable decompilation or pathfinding analysis.

ChatGPT used Workbridge to save and execute these local tools on this PC. This demonstrates
the local orchestration route discussed earlier. Tight execution and repeated sampling
belong in the local process; individual browser-chat turns are not the movement control loop.

Track source, profiles, interpretations and artifact hashes in Git. Generated listings and
game binaries remain local inputs/outputs under the repository's existing ignore rules.

