# WA-006 — bounded physical G2 API-list feasibility (2026-11-16, AMD-DESKTOP)

**Status:** Offline API contract verified; proposed Lua probe **NOT EXECUTED**; WA-006 G2 **BLOCKED**. RRE single-manager research only. No gameplay, process attachment, screenshot, movement, casting, targeting, /reloadui, addon deployment, VMware, RR2 mutation or remote publication was performed for this research slice.

## Original current-client-family API evidence

An original saved RIFT API atlas at `artifacts/addon-investigation-20261107-1209/sources/08-live-snapshot.json` is 1,388,851 bytes, SHA-256 `6aee10589341c7462539d15adb726e1fddf14af31d936505195020370b954ec0`. Its producer metadata describes an October 28, 2026 capture, client build `Oct 23 2026 11:32:27 RIFT-BUILD-12` / `STABLE-1-1178-A-1256632`, 1,939 API entries, zero collection errors. This is a recorded API inventory, **not** a successful current-game invocation.

The archived exact client documentation records:
- `Inspect.Unit.List()` as a function returning a **map of unit ID (key) to unit specifier (value)** for units the client can see. A unit with multiple valid specifiers may have one chosen at random.
- `Inspect.Unit.Detail(unit)` as a function accepting one unit ID/specifier (or a batch); returned detail can include `id`, `coordX`, `coordY`, `coordZ`, which may be absent.
- `Inspect.Unit.Lookup(unit)` as a function that may resolve an ID/specifier or return nil.

**Do not reverse key/value roles**, treat specifiers as native keys, assume the map is an exhaustive nearby census, or fabricate Lua `uHEX` IDs from native decimal keys.

## Current persisted RRE evidence

The original AMD-DESKTOP Atank SavedVariables `RRECollector.lua` read on November 16 at approximately 19:25 EST was 68,044 bytes, SHA-256 `503885ef5387a7c4d07e9a31a5bbc716fcf39233892e48752441f89d9a2ddf6d`, modified 2026-11-17 00:09:01.942 UTC. Existing .NET 10 reader `validate --source saved --module context` and `capture --source saved --module context` both exited 0; the retained snapshot is RRECollector 0.4.20, sequence 2, player API ID `u035400012FA2D207`, XYZ (7143.8198242188, 871.76995849609, 3054.2800292969), zone candidate `z487C9102D2EA79BE`, and **empty target** with `capabilities.target=false`. The recent file modification is not proof of capture UTC, current PID, atomicity or authentic current-process publication.

Existing RRECollector only calls `Inspect.Unit.Lookup('player.target')` for **one** target in `context.lua`. Its `wire.lua` discards/replaces prior RREC2 frames for each publication. The physical RRE reader has no independently qualified live multi-generation acquisition; memory-scan/native-snapshot/publication sources are offline replay modes. Two captures followed by only one SavedVariables flush would retain only the latter. Neither `/rre navigation` nor `/rre capture` invokes `Inspect.Unit.List`.

Source RRECollector package version 0.4.21 validates offline; AMD-DESKTOP's physically installed package is a distinct 0.4.20 build. Seven of ten raw installed files differ from source (three byte-matched), but independent text comparison shows G2-relevant `context.lua` and `wire.lua` are semantically unchanged after line-ending normalization. **Deploying 0.4.21 alone does not add nonself enumeration or multi-generation retention**. Installed runtime load is unverified. Keep current RC-30/RC-88 stop gates.

## Reuse rather than rebuild

RR2 already has a bounded physical `unit-positions` native sampler at `C:\work\riftreader2\scripts\physical_rift.py`, and a source-wrapped route-view producer at `scripts/save_physical_route_view.py`. Historical nonself candidates are **not** independent API IDs. RR2's ongoing work owns 23 reserved paths/12 queued assignments at inspection; zero running jobs does not grant the RIFT client to RRE. Request an explicit exclusive read-only observation window with fresh PID/start/executable SHA/window/scene and per-sample clocks before any native sample. Do not create a duplicate native scanner or alter RR2 source.

## One-shot *read-only* LuaPad probe (10-case offline mock; never run in-game)

This candidate script is strictly exploratory until its output path, syntax, and source attribution are independently validated. It never targets, moves, casts, reloads or modifies SavedVariables. A cap applies to **Lua iteration and details**, not the game's internal List implementation.

The canonical source is [`tools/agents/collision/wa006_g2_one_shot.lua`](../tools/agents/collision/wa006_g2_one_shot.lua), SHA-256 `990c91a06cb0398cbc3e495c59169b43b11bd0c29d132319c30607d39f448b5e`. It validates RIFT-format unit IDs, rejects mismatched `Detail.id`, marks missing `Detail.id` as `idBinding=missing` and **does not count its coordinates as verified `validXYZ`**, preserves explicit sampling caps, records begin/end game clocks, and always marks output `exploratory-only`. It remains **UNTESTED IN LIVE RIFT**.

The offline mock harness is [`tools/agents/collision/test_wa006_g2_one_shot.mjs`](../tools/agents/collision/test_wa006_g2_one_shot.mjs). Using the already-installed, SHA-pinned Windows Lua 5.3 interpreter (not a RIFT Lua 5.1 runtime), job `rre_wa006_g2_mock_10cases_20261116_01` exited 0 with **10/10** scenarios, including invalid IDs/coordinates, API errors, 128/8 caps, missing `Detail.id` and explicit `Detail.id` mismatch rejection. `rre_wa006_g2_roadmap_10cases_20261116_01` also passed (47 tasks, 11 milestones, zero failures). Lua 5.1 runtime compatibility remains untested.

**LuaPad integration (offline source proof):** Installed OneDrive LuaPadModern `v2.0.0-preview22` has a 31,498-byte `main.lua` byte-matching the repo source. Its Run action captures `print()` but ignores the chunk's return value; our probe explicitly calls `print(report)`. Copy Output copies the currently retained `lastOutput`, which `LuaPad.print` caps to the last 12,000 bytes. The offline source-derived **worst-case canonical packet is 10,284 bytes**, leaving **1,716 bytes** under the 12,000-byte retained-history cap (see detailed bound below). **Complete actual live copy and loaded-version proof are not yet verified**. Validate BEGIN, END, counters, no truncation notice and host SHA/time once a game owner approves a test window.

**Offline transcript gate:** The dedicated parser [`verify_wa006_g2_packet.mjs`](../tools/agents/collision/verify_wa006_g2_packet.mjs) parses a copied report, computes its raw-byte SHA-256, checks complete BEGIN/END, strict counts, two distinct ID-bound finite XYZ rows, clocks, errors, enumeration caps and LuaPad's 12,000-byte tail limit; it returns `packetStructurallyReady` separately from **always-false** `nativeCorrelationDone` and `wa006Accepted`. Invoke as `node tools/agents/collision/verify_wa006_g2_packet.mjs <copied-report.txt>` from the RRE root. [`test_verify_wa006_g2_packet.mjs`](../tools/agents/collision/test_verify_wa006_g2_packet.mjs) job `rre_wa006_g2_packet_validator_24cases_20261116_01` passed **24/24** offline cases. A fabricated transcript can pass these structural checks; source/PID/time and independent native correlation remain mandatory. Installed PUC-Rio `luac32.exe -p` also accepted Lua syntax (Lua 5.3), but no actual Lua 5.1 interpreter was found in the bounded path inventory.

## ~20:32 EST — exact LuaPad copy-output byte budget (independent offline QA)

An independent AMD-DESKTOP reviewer checked original `LuaPadModern/main.lua` Run/Clear, `LuaPad.print` append/tail, Copy Output, and the canonical one-shot source's ID, specifier and finite-coordinate formatting. The probe prints a single report; at most eight `ROW` lines; unit IDs are 17 ASCII bytes; specifiers capped at 80 **bytes**; each finite coordinate uses `%.6f`. Under these actual source bounds:

| Packet component | Calculated maximum bytes |
|---|---:|
| `BEGIN` | 687 |
| 8 × `ROW` (1,105 bytes each) | 8,840 |
| `END` | 748 |
| 9 newline separators | 9 |
| **Total** | **10,284** |
| **Below 12,000-byte retained output cap** | **1,716** |

LuaPad clears its output before Run and its Copy Output retrieves `lastOutput`, not the visually rendered preview; its 12,100-byte/300-newline *render* bound is distinct. The structural verifier rejects copied bytes >=12,000 and missing `BEGIN/END`. **No fragmentation or packet size-reduction code is justified**. The bound assumes finite ordinary Lua IEEE-754 values and a successful canonical one-shot; unrelated diagnostics/errors are a different output that must fail the validator unless separately validated. It is **not a live RIFT execution proof**. Three read-only bounded source checks; no file/game/UI mutation.

## Exact next micro-slices (ranked)

1. **Offline QA largely complete:** Lua 5.3 mock 10/10, packet structural negatives 24/24, installed LuaPad source copy path and 10,284-byte worst-case bound are verified. A true RIFT Lua 5.1 execution and actual loaded LuaPad version are **not** verified; no successful live RIFT API invocation may be claimed.
2. **Physical observation only after owner coordination:** independently verify AMD-DESKTOP, current RIFT PID/start/window/executable SHA and actual playable scene plus current LuaPad loaded/version and an exclusive game-control window. One scripted `Inspect.Unit.List` invocation with no movement/click targeting and a complete source-hashed output/UTC bracket; abort on missing APIs, truncated output, mismatched build or ownership uncertainty.
3. **Native correlation:** obtain bounded RR2 native `unit-positions` before/after through its owner. Compare **two genuine distinct nonself API IDs** and independently sourced XYZ to native decimal keys on one process epoch, with predeclared tolerance, scene proof and negative controls. Treat missing identity/clock/calibration as UNKNOWN. No G2 or ROOT-001 acceptance by assumption.

**Hard stop:** WA-006 G1–G5, WA-007 and ROOT-001 remain BLOCKED. No RIFT movement, targeting, casting, reload, process attachment, VM operation, installed addon change, other-repository edit or push is authorized merely by this offline report.
