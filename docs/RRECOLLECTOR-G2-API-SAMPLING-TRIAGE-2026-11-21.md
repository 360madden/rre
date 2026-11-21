# RRECollector v0.4.23 ↔ WA-006 G2 Lua API sampling triage
November 21, 2026 · AMD-DESKTOP · source-only, offline

## Verified finding

The pre-existing G2 LuaPad one-shot (`tools/agents/collision/wa006_g2_one_shot.lua`) examines up to 128 `Inspect.Unit.List()` table entries and invokes `Detail()` for the first eight eligible nonself units encountered by `pairs()`. RRECollector's `units.lua` examines the same maximum entry count but sorts eligible unit IDs before selecting the eight Detail calls. Two valid same-scene collections therefore need **not** contain the same eight nonself IDs. Absence of a shared key is not sufficient to infer an entity's disappearance.

The two Lua collections are **not independent native evidence**. Neither SavedVariables nor the copied LuaPad transcript provides an authenticated shared process/scene/UTC execution bracket. The exporter retains source-byte SHA-256, but a hash is not source-authenticity proof or proof of current live-game execution.

## Offline triage tools

1. `node tools/export-rrecollector-units.mjs "FULL_PATH_TO_RRECollector.lua" --output "NEW_unit_witness.json"` parses original SavedVariables without executing Lua, validates counters and producer status, and records source SHA-256.
2. `node tools/agents/collision/triage_collector_g2_units.mjs "FULL_PATH_TO_RRECollector.lua" "ORIGINAL_LUAPAD_G2_COPY.txt"` compares the **latest** validated Collector snapshot against the original G2 transcript after the existing canonical G2 packet verifier succeeds. It reports self-ID agreement, shared nonself API IDs, count, observed coordinate deltas, and exact source-byte hashes.
3. The existing independent native preflight remains `tools/agents/collision/verify_wa006_g2_cross_source_preflight.mjs`. This new triage tool does not convert a Collector snapshot into a canonical LuaPad occurrence, does not bypass the external owner/scene/UTC receipt, and does not weaken any G2 source SHA pin.

## Interpretation and acceptance boundaries

- A result `API-ID-overlap-unqualified` only means two Lua/API snapshots contain two common nonself IDs under valid source structures. It does **not** establish a shared time, same scene, same process, accurate coordinates at one instant, or a native match.
- An observed nonzero coordinate delta can arise from movement, serial capture timing, or differences in API precision. The tool reports the maximum difference numerically **without guessing tolerance**.
- `rejected` is returned for malformed canonical G2 packets, different self IDs, incomplete Collector sampling, or fewer than two shared nonself IDs. It does not prove a gameplay entity was absent.
- All outputs explicitly set `sameSceneVerified=false`, `sameEpochVerified=false`, `nativeCorrelationDone=false`, and `wa006Accepted=false`.
- Field-provenance and process-build correlation still require independently acquired, contemporaneous physical-game evidence and a separately verified exact running image. The November 17 on-disk build-1179 SHA does not prove the older PID's mapped image.

## November 21 verification (synthetic, source-only)

- `node --test tools/test-export-rrecollector-units.mjs`: **14/14 pass**, including new producer status-reason, monotonic clock, sorted IDs and case-folded numeric-key rejection controls.
- `node --test tools/agents/collision/test_triage_collector_g2_units.mjs`: **9/9 pass**, including swapped IDs, mismatched self IDs, coordinate drift, incomplete sampling, command-line use with source-hashed original Lua, and 12,000-byte G2 input rejection.
- `node tools/agents/collision/test_verify_wa006_g2_cross_source_preflight.mjs`: **67/67 pass**; native acceptance remains false.
- No installed-addon copy, game input, process memory read/write, or sibling-repository mutation was part of this milestone.

## Follow-up

**P0**: Use a real physical-client capture window to obtain version-matched Collector and LuaPad records, independently timestamped by a host observer, after confirming running-process build and source provenance. **P1**: Preserve original native unit-positions JSON in a separate owner-coordinated observation and use the existing G2 preflight. **P2**: Add verified selection-order and process-epoch metadata in a future Collector release only if actual samples show the present limits hinder correlation. Avoid inventing a live success from synthetic tests.
