# RRE modular host reader

**Host routing (November 9, 2026):** RRE is one cross-computer application: **LEGION → its physical local RIFT**, **AMD-DESKTOP → its authorized VMware RIFT labs**. Joey reports VMware is not installed on LEGION. All game-facing RRE work on LEGION targets only its physical local RIFT. `capture --source lab2` is now rejected on LEGION *before* any acquisition preflight, irrespective of supplied files. Offline `saved`, `memory-scan`, `native-snapshot`, and `publication` inputs remain supported; replaying an existing artifact is not live VM access. Do not contact VMware labs from LEGION.

One C# entry point normalizes RRECollector data for physical-host PowerShell, C# and other JSON consumers. Version0.2.3 includes file adapters plus an explicit bounded read-only Lab2 acquisition source. File sources remain offline; only `capture --source lab2` invokes existing guest memory-read tools. The reader issues no game input, starts no controller/service, deploys no addon and changes no other repository.

## Build and use

Requires the existing .NET10 SDK and Node runtime; no NuGet package dependencies. The saved adapter reuses `tools/read-rrecollector-saved.mjs` through a bounded data-only wrapper. Run from the RRE repository:

```powershell
dotnet build reader/Rre.Reader/Rre.Reader.csproj --ignore-failed-sources
$reader = 'reader/Rre.Reader/bin/Debug/net10.0/Rre.Reader.dll'
dotnet $reader doctor --repo C:\work\rre
dotnet $reader capture --source saved --input C:\path\RRECollector.lua --repo C:\work\rre
```

The last command emits one compact JSON document. PowerShell can pipe it to `ConvertFrom-Json`; C# consumers can parse the same contract or reference the assembly's `IObservationSource`/`ObservationModules` APIs. Add `--module abilities` or `--module context` to select output. `validate` performs the same parsing checks and emits a compact validation receipt. `--output NEW_FILE` publishes without overwriting existing evidence; its parent must exist. There is no shell command interpolation.

### LEGION physical RIFT: first supported data path

1. Verify that the **physical** RIFT client actually loaded the matching RRECollector addon; an offline package check is not installed/runtime proof. Any in-game `/rre capture`, `/reloadui`, or game shutdown must be separately authorized before execution.
2. After an authorized capture and normal SavedVariables flush, locate the *actual* per-character `RRECollector.lua` under the active RIFT documents/SavedVariables tree. Windows Documents may be redirected (including OneDrive); **do not assume an account/path or silently use a stale copy**.
3. Read a retained copy without replacing the original: `dotnet $reader validate --source saved --input 'FULL_PATH_TO_RRECollector.lua' --repo C:\work\rre`. Use `capture` instead of `validate` for normalized JSON. A Workbridge connector limited to `C:\work` cannot access Documents directly; use an explicitly admitted root or an authorized copy inside the allowed workspace, never a path-rule bypass.

This is a **file-backed physical workflow**, not continuous live memory acquisition. Its reader qualification remains offline and does not prove current game-process identity, freshness, or runtime acceptance. No VMware tools are involved on LEGION.

For an explicit **SC618 fixture replay**, obtain its32hex session from the retained scan's SearchText:

```powershell
dotnet $reader capture --source memory-scan --input C:\path\scan.json --session HEX32 --sequence 1
```

This adapter intentionally accepts only the experimental `RRE-feasibility-fixture` producer. It is not a decoder for an installed/live RRE memory producer. `memory-scan` names an input format, not a live acquisition command. Both adapters can be used behind the same core without adding separate semantic readers.

Version0.1.1 also consumes the standard snapshot/request pair emitted by the existing F414/B8 RR2 tools, without needing the original Reader scan format:

```powershell
dotnet $reader capture --source native-snapshot --input C:\path\snapshot.json --request C:\path\request.json --session HEX32 --sequence 1
```

The adapter verifies exact schema/key/type boundaries, request raw-byte SHA, declared PID/start/executable SHA agreement, known producer bundle declaration, ordered source clocks, complete chunks, canonical Base64 and per-chunk hashes, and the exact contiguous4KiB partition of≤16nonoverlapping≤8KiB absolute ranges. It dispatches one exact frame family: RREC1 fixture or RREC2 production contract; mixed families fail. Missing, partial, duplicate, overlapping, misaligned, unrequested or hash-inconsistent bytes fail. Process-start ticks are emitted as a string to preserve precision for JSON consumers. Artifact consistency is not current target/authenticity proof; all live qualifications remain false. RREC1 has no context; RREC2 preserves validated context.

Version0.1.2 adds the [RREC2 production contract](contract-rrec2.md) and a direct offline publication-export adapter:

```powershell
dotnet $reader capture --source publication --input C:\path\publication.json --session HEX32 --sequence 4
```

The export has exactly schemaVersion=1, evidenceKind=`rrec2-publication-artifact/1`, origin (bounded declared/unverified description), and frames (1..16 ASCII strings). RREC2 carries one complete≤64KiB UTF8 document in≤16 canonical Base64 parts, each≤4096raw bytes/≤8192ASCII carrier bytes. It preserves context, exact API-list accounting and ability records, verifies whole-payload Adler32, and records SHA256. The consumer enforces version/session/sequence in header/body/document, complete unique parts and exact scalar-map context shapes. No highest-sequence selection, inbound commands, arbitrary dispatch or game action exists. The reader accepts exactly RRECollector0.4.12,0.4.13,0.4.14,0.4.15,0.4.16,0.4.17,0.4.18 and0.4.19, with identical version required across all parts and the decoded document. Version0.4.12 retains its original20-field unit maps;0.4.13,0.4.14,0.4.15,0.4.16,0.4.17,0.4.18 and0.4.19 permit optional `race`, `raceName`, and `zone` in player/target maps (maximum23 fields). Versions0.4.14,0.4.15,0.4.16,0.4.17,0.4.18 and0.4.19 permit `capabilities.experience` and an optional finite numeric `experience` map with `accumulated`, `needed`, `rested` (including zero and empty map); missing/false and contradictory bindings fail closed. The v0.4.19 reader contract is regression-verified offline; a version-matched physical-game load/capture acceptance receipt for v0.4.18 or v0.4.19 remains outstanding. Missing values remain unknown. Existing raw scalars are retained; non-string or empty metadata is semantically unqualified. Undocumented `decoration` is excluded. SC622 accepted one bounded Lab2 transfer from0.4.12;SC628 subsequently accepted a bounded0.4.13 Lab2 install/load/manual transfer with all three metadata strings also persisted; see the [live report](../docs/REA-RIFT-UNIT-CONTEXT-EXPANSION-2026-11-07.md). Continuous/passive acquisition remains unimplemented.

## Contract and truth boundaries

The output has schemaVersion1, reader/version, host observedAtUtc, sequence, source hashes/provenance, modules and qualification. `abilities` contains validated unique API-listed IDs and bounded scalar Detail fields; this does not establish learnability, current usability or game bindings. `context` is available only when provided by the source. Optional missing fields remain unknown; false/zero survive. Root SavedVariables addon version is separate from the version that produced a retained capture. The new local data adapter preserves ability targets; the older research crosswalk remains unchanged and deliberately omits private target IDs.

`qualification.complete` means all **requested modules** are available and the ability publication was validated. Thus RREC1 replay with `--module all` or `context` has complete=false; its ability module remains complete. RREC2 can provide both modules. It does not mean every optional game field is known. All outputs set live/freshness/processBuild/atomic/restart/runtimeProducer/sourceAuthenticity qualification false. Host observation time is not game capture time. `fixture` identifies the feasibility-only RREC1 contract; false for RREC2/SavedVariables does not prove a non-fixture origin or game execution. Explicit offline fixture origin and independent test provenance remain separately recorded.

The saved path caps input at2,000,000bytes, uses the existing literal-only parser and structure gate, retains exact raw SHA/length and helper/parser source hashes, and rejects input/source drift across the helper call. Only a fixed Node helper is launched with structured argv, bounded output and10second timeout; its owned child is cleaned on failure.

The memory replay contract is the exact SC618 experimental frame: ASCII `RREC1|<32lowerhex>|<8uppercasehex payload bytes>|<JSON>|ENDRREC1`, total≤8192bytes. JSON has exactly schemaVersion=1, producer=`RRE-feasibility-fixture`, session, sequence, part, parts and records. Parts≤16, aggregate IDs≤512, sequence positive and≤2^53−1. Unknown/duplicate JSON fields, nonfinite numbers, wrong identity/sequence, malformed/cross-publication/duplicate/missing parts and duplicate IDs fail. No highest-sequence guessing occurs. Original Reader scan contexts must use canonical uppercase hex byte pairs, exact window length and a matched address within that window. A saturated hit budget is ambiguous and rejected. Trailing context bytes are allowed only at the scan-context boundary; a standalone frame rejects trailing data.

SC622 accepted a manually triggered0.4.12 Lab2 publication acquired through existing tools and decoded by this host reader. No supported live acquisition adapter or passive freshness is established. Further acceptance requires a new coordinated Lab2 window and current version/source/install/load, process/build/player/session receipts. The user explicitly allowed only RRECollector addon files to synchronize through the observed OneDrive root; other files and sync settings remain outside that exception. Advancing observations, stale/GC/relocation handling, restart qualification and full transfer latency remain open. SavedVariables remains the durable fallback.

## Verification

```powershell
dotnet run --project reader/Rre.Reader.Checks/Rre.Reader.Checks.csproj -- C:\work\rre
# Isolated RREC2 contract checks (no Lab2 child tests):
dotnet run --project reader/Rre.Reader.Checks/Rre.Reader.Checks.csproj -- --production-only
node --test tools/tests_reader/test_saved_adapter.mjs tools/verify-rrecollector-saved.mjs
```

The package-free C# check executable covers both contracts' frame/assembly failures, source limits, target/version preservation, context/freshness boundaries, native request/chunk coherence and evidence publication. Node tests cover the adapter and legacy literal parser. To verify the actual retained trial, run `tools/tests_reader/verify-reader-evidence.py` with explicit `--repo`, `--saved`, `--scan1`, `--scan2`, and fresh `--output` directory. Add `--native-snapshot`, `--native-request` and `--native-session` for the SC620fixture pair. It compares all54 IDs and every historical fixture field, verifies preserved saved targets and false live qualifications, rejects stale sequence, and confirms no overwrite. It performs no VM access.

`tools/tests_reader/verify-wire-publisher.py --output NEW_DIR --saved SAVED_LUA --reader READER_DLL` additionally runs the existing SHA-pinned host Lua5.3 runtime (or `--lua-runtime lua51` for the retained Lua5.1 runtime) (no install), synthetic malformed/lifecycle cases and prior-good capture preservation, then an independently audited Python Base64/zlib roundtrip through the C# reader. The retained0.4.11 capture is safely literal-parsed, converted to byte-escaped Lua fixture data, and explicitly retagged to the current source version only offline. Empty Lua context tables are normalized to object maps for comparison; no populated values are changed. These are host interoperability checks, not RIFT runtime acceptance. Retagging is not proof of exact historical0.4.12 carrier compatibility; the separate SC628 regression replays the original SC622 snapshot/request. The historical repository gate remains separate and has older-build-pinned failures; do not change those pins for this reader.


## Lab2 acquisition on supported hosts (SC625; never from LEGION)

First coordinate a new exclusive Lab2 window with its current owner and manually Capture a fresh collector generation using the existing reviewed external mouse setup. Create exact binding/window JSON under the [contract](contract-lab2-acquisition.md); they record context, not permission. Then use the same entry point:

```powershell
dotnet $reader capture --source lab2 --input C:\work\rre\artifacts\binding.json --window C:\work\rre\artifacts\window.json --evidence C:\work\rre\artifacts\new-lab2-trial --repo C:\work\rre --output C:\work\rre\artifacts\observation.json
```

The evidence directory and observation file must not exist; the output file must be outside the evidence directory. `--module context` or `abilities` selects the same canonical modules. `validate --source lab2` is deliberately rejected. The helper pins the fixed Lab2/1935build/F414/native/runtime dependencies and performs at most three bounded scouts plus one complete frame snapshot. C# reuses its strict decoder and publishes `acceptance.json` only after hash/identity/version/parts/bytes, source/image, native-exit journals and guest cleanup pass. Unknown process/data state quarantines the run; inspect `failure.json`/`guest-scope.json`, never auto-retry or assume cleanup. A parent timeout cannot clean the guest by itself. See the [source gate](../docs/REA-RIFT-LAB2-READER-ADAPTER-2026-11-07.md). The adapter passed one bounded live CLI trial as recorded below; all publication qualification flags remain false even when an active read is recorded.

Historical first0.2.1 live trial failed a prelaunch identity/output filename collision and was independently recovered/returned. Fixed0.2.2 separates namespaces and binds native timestamps to the acquisition interval. The second0.2.2 trial acquired/cleaned but failed on journal BOM parsing; the third0.2.3 trial passed below. See the source report for preserved failure/recovery evidence.


**November7 live CLI acceptance:** reader0.2.3 completed one fresh Lab2 acquisition at17:15:34–17:16:15EST, exit0/40.476s, seq10/fiveparts54records, acceptance and canonical observation published. Independent scoped cleanup and explicit return17:16:50EST passed. This accepts one bounded manual generation, while continuous freshness/authenticity/atomicity/inbound/restart remain unqualified. Prior failure narratives above are historical. A new coordinated owner grant is required for another run. See the [SC625 report](../docs/REA-RIFT-LAB2-READER-ADAPTER-2026-11-07.md).
