# RC-86 - recorded quest changes and RIFT shared-table input

**November11, 2026. RRE.Reader0.2.6.** The existing `quests` command now compares two retained originals:

```powershell
dotnet reader/Rre.Reader/bin/Debug/net10.0/Rre.Reader.dll quests --input 'CURRENT_FOLDER/RRECollector.lua' --previous 'PREVIOUS_FOLDER/RRECollector.lua' --repo C:\work\rre --output 'NEW_changes.json'
```

Both files are independently bounded, read and source-hashed. C# binds both hashes/lengths and all three helper hashes. Comparison requires complete captures, the same typed player, advancing sequence and independently advancing Frame/Real clocks. Neither clock is UTC and the check does not prove a shared process epoch. Quest source-ID qualification is preserved. Matching objectives require the same typed key, exact unique nonempty description, known equal required quantity and known done quantities.

The result reports signed recorded count differences, counter decreases, added/absent rows and explicit completion/failure flags. A missing quest is never completed by inference; reaching a quantity never manufactures an explicit completion flag. Ambiguous/reordered definitions, partial captures, identity mismatch and stale inputs remain diagnostic. All action/causation/session/authenticity qualifications stay false. `--previous` is quest-only, rejects duplicates/unknown options, and validates both inputs before exclusive publication. This consumer does not move, fight or complete quests.

## Actual integration defect fixed

The approved physical capture in [RC87](RRE-RC87-PHYSICAL-CAPTURE-LEGION-2026-11-11.md) exposed RIFT's real shared-table serialization. The saved quest snapshot and its attempt share one counter table, so the original begins with `local ref = {}`, a fixed allocation declaration, and scalar assignments before the expected root. The old literal-only parser rejected this at offset5.

The data parser now recognizes that exact encoding declaratively. It never executes the loop or original Lua. Only positive declared reference slots and literal/reference-valued fields are accepted; resolution follows all assignments. Null-prototype dictionaries avoid prototype mutation. Cycles, duplicate fields, modified allocation bodies, member reads, expressions/calls and trailing statements fail. Maximum16384 reference slots, expanded depth48, per-occurrence100k/4M nodes and2MB/32MB UTF-8 string/key budgets prevent DAG/string amplification. Ordinary literal contracts and collector/casting input ceilings remain unchanged.

Quest output also enforces2048-byte text fields,131072-byte projected content and the actual producer's fixed counter names. A4,000,000 UTF-8-byte serialized transport cap applies before stdout or file creation. An escape-heavy accepted source can exceed that transport capacity; it fails explicitly with `quest-output-limit` instead of truncating data or emitting partial JSON. Ordinary512-objective maximum-content fixtures fit. Existing shared child-process limits are unchanged.

## Verification

- **124 Node checks passed:**31 quest cases, nine new reference grammar/expansion cases, two new shared-table consumer cases and the existing saved/navigation/profession/combat regressions. Receipt: `artifacts/rc86-87-focused-node.log`.
- **99 C# production, eight combat and eleven quest adapter checks passed.** The actual nine-module Lua command fixture emits two captures and passes19 assertions; the reader checks both original hashes and a recorded count delta of1. Build passed with zero warnings/errors under warnings-as-errors.
- Both actual RRECollector originals and the existing casting observer file passed the real C#/Node CLI adapters. The actual journal is partial and is not promoted into a qualified progress comparison.
- The historical full gate ran once after final source changes: **507 tests, FAILED**, unchanged source inventory, with the same historical helper/source/old-build errors and two skips. Receipt: `artifacts/rc86-87-research-gate-20261111/validation.json`. No source pins were rebaselined and no full-suite pass is claimed.
- Independent read-only Codex reviews accepted comparison semantics, output transport limits and the reference parser. No worker wrote main or operated the game.

[Source hashes and validation](RRE-RC86-QUEST-COMPARISON-LEGION-2026-11-11.json). Addon source is unchanged at v0.4.20/a2d9660. The goal remains active; actual travel, objective completion and combat remain open.
