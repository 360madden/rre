# SC-623 — Existing native tools transport actual RREC2 frames

**Accepted scope:** controlled host fixture only. The existing F414 native reader located and copied the actual SC622 Lua-produced54-record/five-frame publication; release RRE reader0.1.2 decoded exact records, context, counts and payload SHA. This does not establish a live Lab2 bridge, current game state, game-runtime memory visibility or source authenticity. [Machine-readable source/artifact receipt](REA-RIFT-RREC2-NATIVE-ACQUISITION-2026-11-07.json).

## Acquisition proof

`tools/tests_reader/probe-native-publication.py` uses the already installed base Python to create one disposable child and its own262144-byte allocation. Five unchanged frames occupy nonoverlapping8KiB slots spanning all four absolute byte alignments. A thousand fragment decoys precede them; a truncated same-session/wrong-header-sequence candidate tests exact-prefix discrimination. All native requests name only the exact created child PID/start/executable SHA. No RIFT/VM selection or game-input route exists in this helper. These route restrictions are not OS-wide handle auditing.

The same hash-pinned F414 `scout-values-native` and `snapshot-native` commands supply immediate contexts and then five8KiB ranges/ten4KiB chunks. The same accepted host-reader DLL checks the native request/snapshot schema, exact target/hash/chunk coverage, production frame assembly and all semantic fields. The known54-record payload SHA remains `1bb278780026d95ab104f86339afb99f93ecdd82e22768ff654c747256d3c86c`.

The first attempt rejected a Windows venv redirector/interpreter PID mismatch before any scout request. The corrected helper launches the existing base executable directly; it does not replace the expected PID with arbitrary child-reported metadata. The failed attempt exited cleanly and remains retained. Review also fixed failure-path cleanup to guard broken stdin and escalate graceful exit→terminate→kill, always returning explicit cleanup evidence. Four failure-path unit cases pass; the final real fixture exited0 with no cleanup errors.

## Locator improvement

| Controlled fixture strategy | Candidates | Exact current frame starts | Copied context bytes | Result |
| --- | ---: | ---: | ---: | --- |
| Generic prefix offsets0..3, cap8 |8|0|2072|candidate budget exhausted before real frames|
| Session-interior offsets10..13, cap64 |11|5|2959|256KiB partial scan|
| Session-boundary offsets34..37, cap64 |7|5|735|same256KiB partial scan|

Boundary anchors reduced immediate context bytes by about75% and candidates from11 to7 in this synthetic fixture. This is not a universal speed benchmark: process startup, file hashing, allocator layout and game memory differ. Final observed wall times were approximately414ms generic,437ms interior,418ms boundary,325ms full-copy and208ms decode; the unusable generic result cannot be called faster successful acquisition.

For known expected prefix `RREC2|<session32>|<sequence16>|`, use four little-endian int32 references from offsets34,35,36,37. These cover all residues modulo4 and mostly cross the session/sequence separator; avoid offset38's common `|000`. Regenerate signed-decimal DWORD values for each expected prefix. With contextBefore37/contextAfter64, each candidate's prospective frame start is `S=M-o`, at context offset3/2/1/0. Try every returned reference name and validate exact prefix at that computed address. A match elsewhere in the context is insufficient. Whole-frame/session/sequence/parts/checksum validation remains mandatory.

The existing pinned scout source OR-matches references, scans absolute4-byte alignment, supports1..8 references,≤2048bytes each before/after with total+8≤4096, and at most128matches. Its byte/time resume overlaps7bytes; dedupe process epoch+address. Candidate-budget NextAddress is the first unretained candidate: resume exactly there. Read holes are different: ordinary forward continuation does not repair earlier unread ranges. Retry holes explicitly in the same epoch or keep coverage incomplete. MEM_PRIVATE scope, region caps and any holes/partial budget forbid a whole-process absence conclusion.

## Validation and limits

The final proof verifies exact five original frame byte strings after native copying, all54 records and complete producer context/counts after C# decoding, exact payload SHA, all four alignments, expected-sequence mismatch rejection, and rejection of the five known addresses after clearing only the fixture's own allocation. The latter does not prove old copies disappeared elsewhere; the stale test does not prove arbitrary stale whole-generation discovery.

The native binary and accepted reader DLL are SHA-pinned; the base Python and resolved .NET host are SHA-recorded and unchanged during the run. Pinned source copies come from RR2 commit01bea030, not active RR2 uncommitted code. Runtime declarations/artifact consistency do not establish game authenticity or live freshness; all reader live/runtime/build/atomic/restart qualifications remain false.

A scoped fullgate ran once:500tests, same historical collision/pathfinding exact-executable SHA guard failures, seven other groups pass and inventoried sources unchanged. Later cleanup and runtime-pinning fixes passed four focused unit tests and a fresh complete host acquisition; no second legacy run. No dependency install, new native backend, original Reader dependency, guest operation, OneDrive change, external source edit, Ollama or FreeBuff was used.

[Final receipt](../artifacts/sc623-native-accepted-20261107-1420/receipt.json), [native snapshot](../artifacts/sc623-native-accepted-20261107-1420/frames.snapshot.json), [request](../artifacts/sc623-native-accepted-20261107-1420/frames.request.json), [reader output](../artifacts/sc623-native-accepted-20261107-1420/reader.json), [legacy gate](../artifacts/sc623-fullgate-20261107-1417/validation.json).

Next live step is SC622's operator-authorized RRECollector-only synchronized deployment, fresh Lab2 source/install/load/identity receipts, manual Capture, then the same exact-prefix acquisition. The operator explicitly permits only RRECollector addon-file synchronization; all live testing remains Lab2-only.
