# RC-85 - quest reader and actual-package Lua execution

**November 11, 2026, LEGION. Reader v0.2.5, verified offline.** RRE now exposes the collector's retained quest journal through the same host CLI used for combat and ability evidence:

```powershell
dotnet reader/Rre.Reader/bin/Debug/net10.0/Rre.Reader.dll quests --input 'FULL_PATH_TO_RRECollector.lua' --repo C:\work\rre --output 'NEW_quests.json'
```

Omit `--output` to print JSON. The `rre-quest-journal/1` report includes remaining quantities, tracked/watch priority, exact-ID map locations, original-file SHA/length and retained journal status. `lastRecordedAttempt` and `journalRetainedAfterFailure` expose a later recorded failure separately from the preserved journal. Neither the last recorded attempt nor filesystem modification time establishes present freshness. Missing journals fail rather than inventing goals. Quest data remains separate from ability SourceCapture and RREC2.

The C# adapter verifies the original bytes against the Node consumer, hashes all three helper dependencies before/after execution, preserves the existing 2MB collector input limit, and uses exclusive output publication. Invalid modern data does not acquire gameplay authority. All five live/freshness/coordinate/travel/completion qualifications remain false.

## Executable evidence

The already-installed `C:/work/LuaPadModern/node_modules/fengari` dependency (0.1.5) provides Lua5.3.4 semantics without installing or changing anything. Its CLI reports native exit0 even after a Lua exception and lacks `io.open`. The new `tools/run-collector-lua.mjs` uses the actual Fengari API and `lua_pcall` status, returns exit1 for Lua errors, and reads a frozen in-memory snapshot of the eleven addon files and selected trusted fixture. Unsupported writes, external modules and OS execution are unavailable. This is a fixture runner, not an untrusted-code security sandbox. The dependency repository stayed clean.

The new `verify_quest_command.lua` loads all nine actual startup modules, executes the actual SavedVariables and `/rre quests` handlers against synthetic APIs, and checks version/sequence binding, API reads, quantities and map projection. API/player failure preserves the good journal; unrelated ability/probe/profession/navigation snapshots stay intact. Startup performs no quest polling. Its sixteen assertions pass. The UI module is loaded with construction disabled; this does not test a real toolbar.

The seven C# integration checks execute that Lua fixture, serialize its actual captured report, parse the literal SavedVariables, export goals through Node and consume them through the real C# adapter/CLI. They verify original SHA, remaining quantity2, a matched map location, retained-journal diagnostics, false qualifications, missing-journal rejection, exclusive publication and rejection of gameplay-acquisition options.

## Verification and review

- **261 Lua assertions across fourteen fixtures passed:** quest capture56, UI controls25, context11+23, nine existing fixtures130 and the full-package quest command16. Source snapshots stayed unchanged. Fengari is Lua5.3 rather than the game's Lua5.1; these checks prove mocked logic only.
- **Eleven legacy Lua fixtures failed:** stale extracted-helper dependencies (including `savedSnapshotComplete`, `visibleKnownSelection`, `nextSequence` and `short`), old positive context/catalog fixtures, and an old caption expectation. No product defect was established by those failures. Original fixtures and production addon code were not changed to force a pass. There is no full-Lua-suite pass claim.
- **98 final Node checks passed**, including sixteen quest regressions. Peer review found text amplification and unexpected metadata echo in the consumer. The fix enforces the producer's 2048-byte UTF-8 text and 131072-byte aggregate content bounds before goal duplication, projects row status to a controlled enum/null, and limits context to scalars/null. Exact UTF-8/global-budget boundaries and false/zero preservation pass.
- **99 C# production checks, eight combat adapter checks and seven quest integration checks passed.** Warnings-as-errors build passed with zero warnings/errors. Strict eleven-file collector manifest passed.
- The full historical research gate ran once: **507 tests, FAILED**, source inventory unchanged. Its ten validation helper errors, two collision errors, nine pathfinding errors/one failure and two navigation skips match the earlier gate. Receipt: `artifacts/rc85-research-gate-20261111-2300/validation.json`; the directory suffix is a label, not execution time (actual start22:55:50EST). The final narrow text/metadata fix followed that gate and passed the final98 Node/seven quest checks. Historical source hashes were not rebaselined.

Independent Codex reviewers accepted the Lua runner/fixture and the final quest adapter after the bounds fix. [Source hashes and machine receipt](RRE-RC85-QUEST-READER-LUA-LEGION-2026-11-11.json). [CLI usage](../reader/README.md).

RRECollector source remains byte-identical to v0.4.20 at `a2d9660`. No deployment, reload, game input, process attach, VM access, dependency installation, REA import or Workbridge action occurred. The21:29EST request for bounded deployment/reload/read-only captures remains unanswered. Current RIFT load, Lua5.1 compatibility, persistence and actual quest/combat results remain unverified. The seven-hour goal remains active; this is a functional offline milestone.
