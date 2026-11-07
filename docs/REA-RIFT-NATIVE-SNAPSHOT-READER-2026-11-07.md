# SC-621 — Standard native snapshots in the same RRE host reader

**Accepted offline, reader0.1.1.** The existing modular C# reader now consumes a standard RR2 native snapshot/request pair directly. It reconstructs the copied frame bytes, invokes the shared session/sequence/frame/part/ability validators, and emits the same observation contract. No original Reader scanner or second semantic reader is needed for this artifact path. The [usage guide](../reader/README.md) and [source/build/test receipt](REA-RIFT-NATIVE-SNAPSHOT-READER-2026-11-07.json) bind the result.

```text
Rre.Reader.exe capture --source native-snapshot
  --input full-frames.snapshot.json --request full-frames.request.json
  --session <expected32hex> --sequence <expected-positive-sequence>
```

The adapter reads only the two explicit local paths. It opens no process/VM, follows no filenames declared inside an artifact, and makes no live input or acquisition request. It verifies the exact raw request SHA, standard request/report schemas, required explicit-null fields, PID/start/executable SHA agreement, bounded module metadata, known producer-declared F414/B8 bundle hashes, and source clock order on/after process creation. Producer declarations remain declarations; file-pair coherence is not authenticity or current-target proof.

Requests are capped64KiB and reports8MiB. At most16nonoverlapping absolute ranges of≤8192bytes are accepted. Complete successful chunks must form the exact expected contiguous4KiB partition, with canonical Base64, exact byte counts and per-chunk SHA. Missing/partial/duplicate/misaligned/unrequested chunks, overlap and hash disagreement fail closed. Ticks are compared as exact64-bit integers and emitted as strings to avoid JSON-consumer precision loss. Heap ranges need not lie inside the executable module.

Each reconstructed range must begin with the exact experimental RREC1 fixture frame and explicit session/sequence. The same strict body/part/catalog validation used by the other adapter applies. Source kind is `native-snapshot-replay`, fixture=true, context unavailable; live/freshness/process-build/atomic/restart qualification remain false. An all/context request is incomplete when context is absent; an ability-only request can be complete. This is not yet a production RRECollector wire decoder or live acquisition adapter.

## Verification and review

- **73 package-free C# checks passed**, including24 native adapter checks and three subsequent hardening checks: exact-tick mismatch, malformed metadata, missing-vs-null schema fields, raw request SHA, per-chunk coverage/hash/status, overlap, canonical Base64, and acquisition-before-process-clock rejection. Strict .NET ID/session end anchors reject a final newline; saved adapter also enforces exact lookup-ID length.
- **20 Node checks passed**,9 new adapter checks plus11 unchanged legacy parser checks. One regression initially expected the new ID guard's error, but the earlier structure gate already rejected the malformed ID; the test now verifies the decoded newline and accepts either correct rejection boundary. No source acceptance was weakened.
- Published0.1.1 built without warnings. An explicit integration over SC614saved, SC618scan1/2 and SC620native snapshot returned54exact IDs each. Every fixture field compared equal; the newer saved adapter separately retained one producer target absent from the old sanitized fixture. Stale sequence was rejected; existing output was preserved; every live qualification stayed false.
- A read-only built-in reviewer identified schema/null, metadata-type and process-clock coherence gaps. They were fixed and regression-tested. No reviewer edited files or invoked any VM/process/provider. Final clock and newline guards were manager-reviewed and checked after the static review snapshot.
- The historical full gate ran once for this source integration:500tests, exit1, same collision/pathfinding old executable SHA failures, seven other groups passed, tool inventory unchanged during the run. It excludes the new .NET suite, whose checks and actual-evidence integration are separate. Later narrow guards/test expectations were validated by focused/release checks; no historical binary pins or unrelated tests changed.

No RIFT or guest process was accessed in this milestone. No addon source/install, controller, cross-repository source, dependency or service changed; no memory writes/injection/debugger, Ollama or FreeBuff. The next data-source gate is an RRE-owned serialized producer with source/package/load receipts and an actual Lab2 session/publication acquisition through the already-qualified numeric-scout/snapshot route. Current SavedVariables remains the durable fallback.
