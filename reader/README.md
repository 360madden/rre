# RRE modular host reader

One C# entry point normalizes RRECollector data for physical-host PowerShell, C# and other JSON consumers. This0.1.0 milestone is **offline**: it reads persisted SavedVariables or replays a saved memory-scan artifact. It does not open a game/VM process, acquire live memory, issue input, start a service, deploy addons or change another repository.

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

## Contract and truth boundaries

The output has schemaVersion1, reader/version, host observedAtUtc, sequence, source hashes/provenance, modules and qualification. `abilities` contains validated unique API-listed IDs and bounded scalar Detail fields; this does not establish learnability, current usability or game bindings. `context` is available only when provided by the source. Optional missing fields remain unknown; false/zero survive. Root SavedVariables addon version is separate from the version that produced a retained capture. The new local data adapter preserves ability targets; the older research crosswalk remains unchanged and deliberately omits private target IDs.

`qualification.complete` means all **requested modules** are available and the ability publication was validated. Thus memory replay with `--module all` or `context` has complete=false; its ability module remains complete. It does not mean every optional game field is known. All outputs set live/freshness/processBuild/atomic/restart qualification false. Host observation time is not game capture time. Fixture output is explicitly labeled and has unavailable context.

The saved path caps input at2,000,000bytes, uses the existing literal-only parser and structure gate, retains exact raw SHA/length and helper/parser source hashes, and rejects input/source drift across the helper call. Only a fixed Node helper is launched with structured argv, bounded output and10second timeout; its owned child is cleaned on failure.

The memory replay contract is the exact SC618 experimental frame: ASCII `RREC1|<32lowerhex>|<8uppercasehex payload bytes>|<JSON>|ENDRREC1`, total≤8192bytes. JSON has exactly schemaVersion=1, producer=`RRE-feasibility-fixture`, session, sequence, part, parts and records. Parts≤16, aggregate IDs≤512, sequence positive and≤2^53−1. Unknown/duplicate JSON fields, nonfinite numbers, wrong identity/sequence, malformed/cross-publication/duplicate/missing parts and duplicate IDs fail. No highest-sequence guessing occurs. Original Reader scan contexts must use canonical uppercase hex byte pairs, exact window length and a matched address within that window. A saturated hit budget is ambiguous and rejected. Trailing context bytes are allowed only at the scan-context boundary; a standalone frame rejects trailing data.

The core is ready for additional acquisition adapters and feature modules, but no live adapter or production addon frame contract is claimed. The next live gate requires an RRE-owned bounded producer, version/source/install/load receipts, exact Lab2 process/build/player/session, complete advancing observations, stale/GC/relocation handling and full guest-to-host latency measurement. SavedVariables remains the proven durable fallback.

## Verification

```powershell
dotnet run --project reader/Rre.Reader.Checks/Rre.Reader.Checks.csproj -- C:\work\rre
node --test tools/tests_reader/test_saved_adapter.mjs tools/verify-rrecollector-saved.mjs
```

The package-free C# check executable covers frame/assembly failures, source limits, target/version preservation, context/freshness boundaries and evidence publication. Node tests cover the adapter and legacy literal parser. To verify the actual retained trial, run `tools/tests_reader/verify-reader-evidence.py` with explicit `--repo`, `--saved`, `--scan1`, `--scan2`, and fresh `--output` directory. It compares all54 IDs and every historical fixture field, verifies preserved saved targets and false live qualifications, rejects stale sequence, and confirms no overwrite. It performs no VM access. The historical repository gate remains separate and has older-build-pinned failures; do not change those pins for this reader.
