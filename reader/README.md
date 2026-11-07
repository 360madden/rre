# RRE modular host reader

One C# entry point normalizes RRECollector data for physical-host PowerShell, C# and other JSON consumers. Version0.1.2 is **offline**: it reads persisted SavedVariables or replays saved memory-scan/native-snapshot/publication artifacts. It does not open a game/VM process, acquire live memory, issue input, start a service, deploy addons or change another repository.

## Build and use

Requires the existing .NET10 SDK and Node runtime; no NuGet package dependencies. The saved adapter reuses `tools/read-rrecollector-saved.mjs` through a bounded data-only wrapper. Run from the RRE repository:

```powershell
dotnet build reader/Rre.Reader/Rre.Reader.csproj --ignore-failed-sources
$reader = 'reader/Rre.Reader/bin/Debug/net10.0/Rre.Reader.dll'
dotnet $reader doctor --repo C:\work\rre
dotnet $reader capture --source saved --input C:\path\RRECollector.lua --repo C:\work\rre
```

The last command emits one compact JSON document. PowerShell can pipe it to `ConvertFrom-Json`; C# consumers can parse the same contract or reference the assembly's `IObservationSource`/`ObservationModules` APIs. Add `--module abilities` or `--module context` to select output. `validate` performs the same parsing checks and emits a compact validation receipt. `--output NEW_FILE` publishes without overwriting existing evidence; its parent must exist. There is no shell command interpolation.

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

The export has exactly schemaVersion=1, evidenceKind=`rrec2-publication-artifact/1`, origin (bounded declared/unverified description), and frames (1..16 ASCII strings). RREC2 carries one complete≤64KiB UTF8 document in≤16 canonical Base64 parts, each≤4096raw bytes/≤8192ASCII carrier bytes. It preserves context, exact API-list accounting and ability records, verifies whole-payload Adler32, and records SHA256. The consumer enforces version/session/sequence in header/body/document, complete unique parts and exact scalar-map context shapes. No highest-sequence selection, inbound commands, arbitrary dispatch or game action exists. RRECollector0.4.12 is source/offline-tested only; installation/load/live transfer remains gated.

## Contract and truth boundaries

The output has schemaVersion1, reader/version, host observedAtUtc, sequence, source hashes/provenance, modules and qualification. `abilities` contains validated unique API-listed IDs and bounded scalar Detail fields; this does not establish learnability, current usability or game bindings. `context` is available only when provided by the source. Optional missing fields remain unknown; false/zero survive. Root SavedVariables addon version is separate from the version that produced a retained capture. The new local data adapter preserves ability targets; the older research crosswalk remains unchanged and deliberately omits private target IDs.

`qualification.complete` means all **requested modules** are available and the ability publication was validated. Thus RREC1 replay with `--module all` or `context` has complete=false; its ability module remains complete. RREC2 can provide both modules. It does not mean every optional game field is known. All outputs set live/freshness/processBuild/atomic/restart/runtimeProducer/sourceAuthenticity qualification false. Host observation time is not game capture time. `fixture` identifies the feasibility-only RREC1 contract; false for RREC2/SavedVariables does not prove a non-fixture origin or game execution. Explicit offline fixture origin and independent test provenance remain separately recorded.

The saved path caps input at2,000,000bytes, uses the existing literal-only parser and structure gate, retains exact raw SHA/length and helper/parser source hashes, and rejects input/source drift across the helper call. Only a fixed Node helper is launched with structured argv, bounded output and10second timeout; its owned child is cleaned on failure.

The memory replay contract is the exact SC618 experimental frame: ASCII `RREC1|<32lowerhex>|<8uppercasehex payload bytes>|<JSON>|ENDRREC1`, total≤8192bytes. JSON has exactly schemaVersion=1, producer=`RRE-feasibility-fixture`, session, sequence, part, parts and records. Parts≤16, aggregate IDs≤512, sequence positive and≤2^53−1. Unknown/duplicate JSON fields, nonfinite numbers, wrong identity/sequence, malformed/cross-publication/duplicate/missing parts and duplicate IDs fail. No highest-sequence guessing occurs. Original Reader scan contexts must use canonical uppercase hex byte pairs, exact window length and a matched address within that window. A saturated hit budget is ambiguous and rejected. Trailing context bytes are allowed only at the scan-context boundary; a standalone frame rejects trailing data.

The production contract and source publisher now exist, but no live acquisition adapter or loaded production bridge is claimed. The next live gate requires a Lab2-isolated destination, version/source/install/load receipts, exact Lab2 process/build/player/session, complete advancing observations, stale/GC/relocation handling and full guest-to-host latency measurement. The current Lab2 addon root is under an active OneDrive sync root; do not silently deploy there. SavedVariables remains the proven durable fallback.

## Verification

```powershell
dotnet run --project reader/Rre.Reader.Checks/Rre.Reader.Checks.csproj -- C:\work\rre
node --test tools/tests_reader/test_saved_adapter.mjs tools/verify-rrecollector-saved.mjs
```

The package-free C# check executable covers both contracts' frame/assembly failures, source limits, target/version preservation, context/freshness boundaries, native request/chunk coherence and evidence publication. Node tests cover the adapter and legacy literal parser. To verify the actual retained trial, run `tools/tests_reader/verify-reader-evidence.py` with explicit `--repo`, `--saved`, `--scan1`, `--scan2`, and fresh `--output` directory. Add `--native-snapshot`, `--native-request` and `--native-session` for the SC620fixture pair. It compares all54 IDs and every historical fixture field, verifies preserved saved targets and false live qualifications, rejects stale sequence, and confirms no overwrite. It performs no VM access.

`tools/tests_reader/verify-wire-publisher.py --output NEW_DIR --saved SAVED_LUA --reader READER_DLL` additionally runs the existing SHA-pinned host Lua5.3 runtime (no install), synthetic malformed/lifecycle cases and prior-good capture preservation, then an independently audited Python Base64/zlib roundtrip through the C# reader. The retained0.4.11 capture is safely literal-parsed, converted to byte-escaped Lua fixture data, and explicitly retagged0.4.12 only offline. Empty Lua context tables are normalized to object maps for comparison; no populated values are changed. These are host interoperability checks, not RIFT Lua5.1/runtime acceptance. The historical repository gate remains separate and has older-build-pinned failures; do not change those pins for this reader.
