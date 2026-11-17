# RRE modular host reader

**CURRENT physical-only routing (November 10, 2026):** Both AMD-DESKTOP and LEGION may use only their respective physical RIFT clients as potential future live targets. The historical `capture --source lab2` acquisition command is **disabled on every host before file/path or helper preflight**. Its implementation and archived artifacts remain available for offline source checks and replay; `saved`, `memory-scan`, `native-snapshot`, and `publication` file adapters are unaffected. New physical-client actions still require verified host/process/build/owner and task-specific authority. This note supersedes the older Lab-2 routing passages retained below as history.

**Reader0.2.6: compare retained quest captures and read RIFT shared tables.** Add `--previous` to the existing quest command:

```powershell
dotnet reader/Rre.Reader/bin/Debug/net10.0/Rre.Reader.dll quests --input 'CURRENT_FOLDER/RRECollector.lua' --previous 'PREVIOUS_FOLDER/RRECollector.lua' --repo C:\work\rre --output 'NEW_quest_changes.json'
```

Both originals retain their SHA/length, sequence and clocks. Complete captures with the same typed player identity and advancing sequence/clocks can report count advances, counter decreases and observed presence changes. An objective must have the same typed key, exact unique nonempty description and required quantity. Partial coverage, ambiguous/reordered definitions, stale inputs and identity mismatches stay unqualified. Missing quests do not imply completion; reported completion/failure flags stay separate from quantities. Neither clock is interpreted as UTC, and comparison grants no game-session continuity, action execution or causation proof. `--previous` is rejected by `combat`.

The data parser now accepts RIFT's exact shared-table declaration/allocation/field encoding without executing Lua. It resolves references after all writes, rejects cycles, duplicate fields, altered loop bodies, arbitrary expressions and trailing code, and bounds expanded depth, nodes and UTF-8 string/key bytes. Ordinary literal inputs remain supported. Quest CLI serialization is capped at4,000,000 UTF-8 bytes before stdout/file publication; exceptional escape-heavy reports fail with `quest-output-limit`, preserving original data and existing child-process limits.

Physical LEGION v0.4.20 validation on November11 produced one complete53-record Rogue ability capture plus a partial27-quest/43-objective journal with15 remaining goals. All persisted and were decoded by this reader. The40 unsupported indicator entries yielded no map reads or locations; their actual representation needs a separate bounded capture. No movement or combat occurred. These are bounded observed receipts; file outputs still keep their general live/freshness qualifications false.

**Reader0.2.5: quest goals from the existing collector journal.** After an authorized `/rre quests` capture and normal SavedVariables persistence, run:

```powershell
dotnet reader/Rre.Reader/bin/Debug/net10.0/Rre.Reader.dll quests --input 'FULL_PATH_TO_RRECollector.lua' --repo C:\work\rre --output 'NEW_quests.json'
```

Omit `--output` to print JSON. The `rre-quest-journal/1` report includes source SHA/length, retained journal status, the last recorded attempt status, remaining quantities and exact-ID map locations. A later failed capture preserves the journal and is reported separately; it does not establish present freshness. Quest goals remain separate from ability `SourceCapture` and RREC2. Live freshness, coordinate frame, travel feasibility and completion actions remain unverified. This command reads files and issues no game input.

The actual nine-module addon startup and manual quest handler can be checked offline with the existing Fengari0.1.5 dependency, without installing packages:

```powershell
dotnet run --project reader/Rre.Reader.Checks -- --quest-only C:\work\rre C:\work\LuaPadModern\node_modules\fengari
node tools/run-collector-lua.mjs C:\work\LuaPadModern\node_modules\fengari tools/agents/quest_journal/verify_quest_capture.lua
```

Fengari implements Lua5.3.4; these mocked logic checks are not RIFT's Lua5.1 or current-client acceptance. The runner propagates Lua errors as failure exits and limits fixture file reads to an in-memory addon snapshot. It is intended for trusted repository fixtures, not as a sandbox for untrusted code.

**Reader0.2.4: combat feedback from the existing casting observer.** After a genuine recording and normal SavedVariables persistence, run:

```powershell
dotnet reader/Rre.Reader/bin/Debug/net10.0/Rre.Reader.dll combat --input 'FULL_PATH_TO_RiftReader2Casting.lua' --repo C:\work\rre
```

This source-hashed report distinguishes exact-target damage/heal, overheal-only, matched failures and inconclusive observations. It preserves an earlier observed result separately from an aborted/incomplete trial, honors modern ability-ID precedence, and handles capped event lists plus retained last-hit evidence. Archived trials retain unknown producer-version provenance. The `rre-casting-evidence/1` contract is separate from ability `SourceCapture`; it invents no inventory or sequence. It grants no live freshness or action authority. `--output NEW_FILE` uses exclusive publication. The casting consumer has a practical32MB/4M-literal-value ceiling; ordinary RRECollector inputs retain their2MB/100k-value limits. Unknown/unreadable files are not empty trials.

Focused adapter checks: `dotnet run --project reader/Rre.Reader.Checks -- --combat-only C:\work\rre`. Existing production-only and historical full checks remain separate.

RRECollector v0.4.20 retains the existing ability/context/Experience wire contract and v0.4.19 compatibility. Its separate quest journal stays outside RREC2; use `tools/export-rrecollector-quests.mjs` for source-hashed offline quest goals. Package/reader checks do not establish current client load or gameplay results.

**Historical host routing (November 9; superseded November 10):** Earlier RRE policy assigned LEGION to its physical game and AMD-DESKTOP to VMware. That authorization has ended. The current physical-only rule applies to both machines, and `capture --source lab2` now fails closed on every host. Existing source and retained Lab-2 evidence remain available for **offline** analysis only.

One C# entry point normalizes RRECollector data for physical-host PowerShell, C# and other JSON consumers. Version0.2.3 historically introduced a bounded read-only Lab2 acquisition source; that source remains in the tree for offline provenance and tests. The `capture --source lab2` CLI now rejects before launching any guest memory-read helper. File-backed sources remain offline, and the reader issues no game input, controller/service start or addon deployment.

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

The export has exactly schemaVersion=1, evidenceKind=`rrec2-publication-artifact/1`, origin (bounded declared/unverified description), and frames (1..16 ASCII strings). RREC2 carries one complete≤64KiB UTF8 document in≤16 canonical Base64 parts, each≤4096raw bytes/≤8192ASCII carrier bytes. It preserves context, exact API-list accounting and ability records, verifies whole-payload Adler32, and records SHA256. The consumer enforces version/session/sequence in header/body/document, complete unique parts and exact scalar-map context shapes. No highest-sequence selection, inbound commands, arbitrary dispatch or game action exists. The reader accepts exactly RRECollector0.4.12 through0.4.21, with identical version required across all parts and the decoded document. Version0.4.12 retains its original20-field unit maps; versions0.4.13 through0.4.21 permit optional `race`, `raceName`, and `zone` in player/target maps (maximum23 fields). Versions0.4.14 through0.4.21 require boolean `capabilities.experience` and permit an optional finite numeric `experience` map with `accumulated`, `needed`, `rested` (including zero and empty map); the capability flag must be present, with a missing map permitted only when it is false, and contradictory bindings fail closed. The v0.4.21 reader contract passed offline Lua5.1.4/5.3 producer-to-.NET round trips for a synthetic publication and a 54-ability historical fixture. Version-matched physical-game load/Capture acceptance for v0.4.21 remains outstanding. Missing values remain unknown. Existing raw scalars are retained; non-string or empty metadata is semantically unqualified. Undocumented `decoration` is excluded. SC622 accepted one bounded Lab2 transfer from0.4.12;SC628 subsequently accepted a bounded0.4.13 Lab2 install/load/manual transfer with all three metadata strings also persisted; see the [live report](../docs/REA-RIFT-UNIT-CONTEXT-EXPANSION-2026-11-07.md). Continuous/passive acquisition remains unimplemented.

## Contract and truth boundaries

The output has schemaVersion1, reader/version, host observedAtUtc, sequence, source hashes/provenance, modules and qualification. `abilities` contains validated unique API-listed IDs and bounded scalar Detail fields; this does not establish learnability, current usability or game bindings. `context` is available only when provided by the source. Optional missing fields remain unknown; false/zero survive. Root SavedVariables addon version is separate from the version that produced a retained capture. The new local data adapter preserves ability targets; the older research crosswalk remains unchanged and deliberately omits private target IDs.

`qualification.complete` means all **requested modules** are available and the ability publication was validated. Thus RREC1 replay with `--module all` or `context` has complete=false; its ability module remains complete. RREC2 can provide both modules. It does not mean every optional game field is known. All outputs set live/freshness/processBuild/atomic/restart/runtimeProducer/sourceAuthenticity qualification false. Host observation time is not game capture time. `fixture` identifies the feasibility-only RREC1 contract; false for RREC2/SavedVariables does not prove a non-fixture origin or game execution. Explicit offline fixture origin and independent test provenance remain separately recorded.

The saved path caps input at2,000,000bytes, uses the existing literal-only parser and structure gate, retains exact raw SHA/length and helper/parser source hashes, and rejects input/source drift across the helper call. Only a fixed Node helper is launched with structured argv, bounded output and10second timeout; its owned child is cleaned on failure.

The memory replay contract is the exact SC618 experimental frame: ASCII `RREC1|<32lowerhex>|<8uppercasehex payload bytes>|<JSON>|ENDRREC1`, total≤8192bytes. JSON has exactly schemaVersion=1, producer=`RRE-feasibility-fixture`, session, sequence, part, parts and records. Parts≤16, aggregate IDs≤512, sequence positive and≤2^53−1. Unknown/duplicate JSON fields, nonfinite numbers, wrong identity/sequence, malformed/cross-publication/duplicate/missing parts and duplicate IDs fail. No highest-sequence guessing occurs. Original Reader scan contexts must use canonical uppercase hex byte pairs, exact window length and a matched address within that window. A saturated hit budget is ambiguous and rejected. Trailing context bytes are allowed only at the scan-context boundary; a standalone frame rejects trailing data.

SC622 accepted a manually triggered0.4.12 Lab2 publication acquired through existing tools and decoded by this host reader. No supported live acquisition adapter or passive freshness is established. Future SC-629 acceptance requires a separately authorized local **physical** RIFT session with current version/source/install/load, process/build/player/session receipts; no Lab-2 session is eligible. The user explicitly allowed only RRECollector addon files to synchronize through the observed OneDrive root; other files and sync settings remain outside that exception. Advancing observations, stale/GC/relocation handling, restart qualification and full transfer latency remain open. SavedVariables remains the durable fallback.

## Verification

Under the current physical-only policy, use `dotnet run --project reader/Rre.Reader.Checks/Rre.Reader.Checks.csproj -- --production-only` for the active, no-VM reader contract/host-routing gate. The historical all-checks mode also probes pinned **installed Lab-2 helper dependencies**; these can drift after the original trials and are not a physical-client acceptance gate. Do not rebaseline an old receipt, access a VM, or weaken the hash checks to force that legacy mode green.

```powershell
# Current physical-only source/reader checks:
dotnet run --project reader/Rre.Reader.Checks/Rre.Reader.Checks.csproj -- --production-only
# Historical full suite (includes archived Lab2 host dependency checks; may be blocked):
dotnet run --project reader/Rre.Reader.Checks/Rre.Reader.Checks.csproj -- C:\work\rre
node --test tools/tests_reader/test_saved_adapter.mjs tools/verify-rrecollector-saved.mjs
```

The package-free C# check executable covers both contracts' frame/assembly failures, source limits, target/version preservation, context/freshness boundaries, native request/chunk coherence and evidence publication. Node tests cover the adapter and legacy literal parser. To verify the actual retained trial, run `tools/tests_reader/verify-reader-evidence.py` with explicit `--repo`, `--saved`, `--scan1`, `--scan2`, and fresh `--output` directory. Add `--native-snapshot`, `--native-request` and `--native-session` for the SC620fixture pair. It compares all54 IDs and every historical fixture field, verifies preserved saved targets and false live qualifications, rejects stale sequence, and confirms no overwrite. It performs no VM access.

`tools/tests_reader/verify-wire-publisher.py --output NEW_DIR --saved SAVED_LUA --reader READER_DLL` additionally runs the existing SHA-pinned host Lua5.3 runtime (or `--lua-runtime lua51` for the retained Lua5.1 runtime) (no install), synthetic malformed/lifecycle cases and prior-good capture preservation, then an independently audited Python Base64/zlib roundtrip through the C# reader. The retained0.4.11 capture is safely literal-parsed, converted to byte-escaped Lua fixture data, and explicitly retagged to the current source version only offline. Empty Lua context tables are normalized to object maps for comparison; no populated values are changed. These are host interoperability checks, not RIFT runtime acceptance. Retagging is not proof of exact historical0.4.12 carrier compatibility; the separate SC628 regression replays the original SC622 snapshot/request. The harness additionally wraps exact current Lua-emitted frames (two-part synthetic and five-part/54-ability saved-source retag) in **simulated F414-shaped native snapshot/request files** and checks native-snapshot versus publication ability/context/count/payload parity plus stale-sequence and missing-part rejection under both pinned Lua runtimes. This is a file-only decoder interoperability test: it does not execute F414, read a game process, verify real tool provenance, or qualify live acquisition. Older Experience-capable saved sources retain their actual captured Experience values when retagged; pre-Experience fixtures add only a false capability, never fabricated measurements. The historical repository gate remains separate and has older-build-pinned failures; do not change those pins for this reader.

For an **actual native-executable test against a disposable host fixture process only**, use `tools/tests_reader/probe-native-publication.py`. It still pins the F414 binary and defaults to its historical reader SHA and sequence 4; explicit `--expected-reader-sha256 CURRENT_DLL_SHA`, `--expected-sequence N` and `--expected-producer-version 0.4.21` allow a source-hash-bound current-format fixture without changing old receipt pins. The test runs the existing bounded native int32 scout and 8KiB snapshot against its *own* spawned Python fixture, then decodes the output through the existing file adapter. A November 17 v0.4.21 five-part/54-ability fixture passed current F414/native reader integration, stale-generation refusal and cleared-frame refusal. This does **not** qualify F414 against physical RIFT, load-state binding, source authenticity or live acquisition.

## Historical Lab2 acquisition (SC625; disabled on every host)

The following November 7 procedure is retained **only for historical provenance**. It is superseded by the November 10 physical-only directive and must not be executed against VMware. The current CLI rejects the command before any input/path preflight. The archived binding/window JSON under the [contract](contract-lab2-acquisition.md) records old context, not current permission:

```powershell
dotnet $reader capture --source lab2 --input C:\work\rre\artifacts\binding.json --window C:\work\rre\artifacts\window.json --evidence C:\work\rre\artifacts\new-lab2-trial --repo C:\work\rre --output C:\work\rre\artifacts\observation.json
```

The evidence directory and observation file must not exist; the output file must be outside the evidence directory. `--module context` or `abilities` selects the same canonical modules. `validate --source lab2` is deliberately rejected. The helper pins the fixed Lab2/1935build/F414/native/runtime dependencies and performs at most three bounded scouts plus one complete frame snapshot. C# reuses its strict decoder and publishes `acceptance.json` only after hash/identity/version/parts/bytes, source/image, native-exit journals and guest cleanup pass. Unknown process/data state quarantines the run; inspect `failure.json`/`guest-scope.json`, never auto-retry or assume cleanup. A parent timeout cannot clean the guest by itself. See the [source gate](../docs/REA-RIFT-LAB2-READER-ADAPTER-2026-11-07.md). The archived adapter passed one bounded live CLI trial as recorded below; no current Lab2 acquisition path is authorized and all historical publication qualification flags remain false.

Historical first0.2.1 live trial failed a prelaunch identity/output filename collision and was independently recovered/returned. Fixed0.2.2 separates namespaces and binds native timestamps to the acquisition interval. The second0.2.2 trial acquired/cleaned but failed on journal BOM parsing; the third0.2.3 trial passed below. See the source report for preserved failure/recovery evidence.


**November7 live CLI acceptance:** reader0.2.3 completed one fresh Lab2 acquisition at17:15:34–17:16:15EST, exit0/40.476s, seq10/fiveparts54records, acceptance and canonical observation published. Independent scoped cleanup and explicit return17:16:50EST passed. This accepts one bounded manual generation, while continuous freshness/authenticity/atomicity/inbound/restart remain unqualified. Prior failure narratives above are historical. This historical result grants no new Lab2 run; current work permits only a separately approved physical-client target. See the [SC625 report](../docs/REA-RIFT-LAB2-READER-ADAPTER-2026-11-07.md).
