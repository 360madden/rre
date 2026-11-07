# SC-622 — RRECollector memory publisher and one host reader

**Accepted scope:** offline source, package and interoperability only. RRECollector0.4.12 is not installed or loaded. The initial OneDrive deployment hold was resolved by the later explicit RRECollector-only synchronization authorization recorded below; fresh install/load/transfer gates remain pending. Physical-PC and Lab1 remain excluded from live testing. [Machine-readable source/package/test receipt](REA-RIFT-RRECOLLECTOR-MEMORY-PRODUCER-2026-11-07.json).

## Result

The same RRECollector manual Capture now builds a retained, bounded RREC2 generation from its already-acquired API snapshot. The same RRE host reader0.1.2 decodes it through either a saved native snapshot/request pair or an explicit offline publication artifact. No new addon, scanner, guest helper, process injection, memory write, event polling or inbound command channel was added.

The retained SC614 capture of Bolinao's54 API-listed abilities round-tripped through the actual new Lua serializer, independent Python Base64/zlib verification, and the release C# decoder: **five frames,18201 decoded bytes**, all54 records/fields, capture counts and populated context values equal. One empty Lua context table has no array/map distinction in SavedVariables; comparison explicitly normalizes that empty table to a map. Original saved data is untouched. Its producer version0.4.11 is deliberately retagged0.4.12 only in safe generated offline fixture data. This is not a fresh game capture or evidence that0.4.12 ran in RIFT.

The synthetic two-part case preserves multibyte `Éclair 水 😀`, target IDs, false and zero. Source/hash receipts distinguish these fixtures from game execution.

## Contract and lifecycle

[Contract v1](../reader/contract-rrec2.md) defines≤8192ASCII-byte frames, exact per-load32hex session and16hex capture sequence,≤16 canonical Base64 parts/4096raw bytes, a whole≤65536-byte UTF8 document, Adler32 and consumer SHA256. Header, part metadata and decoded document repeat the exact version/session/sequence. Complete list counts and allowed scalar context maps are checked; no learnability/usability/binding semantics follow from API-list membership.

Load clears retained frames. Each manual Capture clears the previous wire before API acquisition. API/incomplete failure preserves a prior complete SavedVariables snapshot and leaves no current wire. Wire encoding failure preserves the newly accepted API snapshot, reports a bounded failure, and leaves no retained frames. All strings and parts are built before the final retained table assignment. This is not cross-process atomic publication: temporary/old strings may be visible in memory and survive GC. A complete exact generation plus separately bound current identity/UI receipt is still required.

The session token is correlation data, not authentication or a host nonce. No inbound delivery capability is assumed. RREC1 remains a separate feasibility-only contract. Reader fixture=false for RREC2 denotes contract type, not verified origin; runtimeProducer/sourceAuthenticity and live/freshness/build/atomic/restart flags remain false.

## Validation

- **130 package-free C# checks pass**, covering production Unicode/parts/checksum/schema/count/context guards, native production carrier, prior adapters and malformed/coherence cases. Release build succeeds without warnings.
- **20 Node checks pass**, retaining literal-only SavedVariables parsing and target/false/zero/version behavior.
- Existing SHA-pinned host Lua5.3 executes the producer:39 recorded synthetic checks plus final reload-clear assertion;13 actual source-extracted manual Capture/wire lifecycle assertions;10 existing RC27 preservation assertions. Independent Python checks canonical Base64 and zlib Adler32, then compares C# output. This does not prove RIFT Lua5.1 load, locale or memory-global visibility.
- All four prior retained evidence inputs still decode54 IDs each through release0.1.2; stale sequence and output overwrite are rejected.
- Strict TOC/version/order gate passes11files. Independent recognized BotDsBridge0.3.3 TOC reference confirms required metadata including Email/environment. The reviewable ZIP contains only RRECollector files, TOC last in archive, exact per-file hashes; no installation occurred.
- Legacy full gate ran once:500tests/exit1, same historical exact-executable SHA guard failures in collision/pathfinding, seven other groups pass, inventoried sources unchanged. Pins are not rebaselined. It does not cover the new .NET/Lua suites; those have independent receipts. Later source-version comment corrections were followed by focused interoperability/package checks, not another legacy run.

The fixed independent-review findings were malformed UTF8 publication, contradictory list counts, overly permissive context shapes, inconsistent fixture-contract classification, and a failure-reason parser omitting numeric characters. Secure Reload UI source is unchanged. Actual slash/UI/event binding and comma-decimal RIFT locale remain live acceptance limits; number serialization fails explicitly on comma decimal output.

## Reviewable artifacts and remaining gate

- [Addon package manifest](../artifacts/RRECollector-0.4.12-accepted-package-20261107/manifest.json) and [ZIP](../artifacts/RRECollector-0.4.12-accepted-package-20261107/RRECollector-0.4.12.zip).
- [Release reader](../artifacts/Rre.Reader-0.1.2-accepted-20261107/Rre.Reader.exe) and [commands](../reader/README.md).
- [Accepted Lua/Python/C# receipt](../artifacts/sc622-wire-accepted-20261107-1406/receipt.json), [prior-adapter integration](../artifacts/sc622-old-adapters-release-20261107-1404/integration.json), [C# checks](../artifacts/reader-checks-d92acdbc25114e98bf0eb2b0ffae1d2b/checks.json), [legacy gate](../artifacts/sc622-fullgate-20261107-1403/validation.json).
- [Isolation metadata](../artifacts/sc622-isolation-preflight-20261107-1328/metadata.json) and [read-only receipt](../artifacts/sc622-isolation-preflight-20261107-1328/receipt.json).

The currently qualified addon load root is `C:\Users\mrkoo\OneDrive\Documents\RIFT\Interface\AddOns\RRECollector`. A registered OneDrive sync root contains it and OneDrive was running at the metadata preflight. Normal directories do not imply isolation. No documented RIFT alternate-root flag was found in the bounded read-only investigation. A local staging folder is not a proved load root; temporarily pausing sync is not durable isolation.

A Windows Documents Known Folder Move change is a broader system-profile migration, not an evidenced RIFT option. Microsoft's [folder-backup documentation](https://support.microsoft.com/en-us/onedrive/back-up-your-folders-with-onedrive?country=us&culture=en-us) describes stopping backup and choosing PC-only files; [Known Folder Move documentation](https://learn.microsoft.com/en-us/sharepoint/redirect-known-folders) describes Documents redirection. RIFT's resolution after such a change remains an inference requiring fresh current-client proof. No OneDrive, Documents, profile, symlink or excluded-machine setting was changed.

Next live step therefore needs either a proved isolated Lab2 load root or an explicit informed exception to the [no silent propagation target policy](REA-RIFT-LAB2-LIVE-TARGET-2026-11-07.md). Then require source/install/load receipts and fresh process/build/scene before existing external mouse Capture. Acquire exact current frames using already pinned native tools and compare advancing wire/SavedVariables observations; no new backend is needed unless reuse actually fails. Until this gate resolves, controlled host-memory acquisition and bounded native/API research can continue independently.

## Later operator authorization and reused Lua5.1 validation

The operator explicitly answered: **“Allow only RRECollector addon files to sync; keep all testing in Lab2.”** This resolves the no-silent-propagation gate only for this addon folder; it does not change Windows/OneDrive settings or permit physical/Lab1 live interaction. Fresh install/load/transfer gates remain pending.

The repository's existing hash-pinned Lua5.1.4 double-int64 interpreter was reused without rebuilding/installing it. All9 current modules parse;40 synthetic publisher assertions,13 actual Capture/wire assertions and10 prior preservation assertions pass. Both the synthetic Unicode2part and historical54record5part frames are byte-for-byte identical to Lua5.3 output and decode through release0.1.2. [Exact compatibility receipt](../artifacts/sc622-lua51-qualification-20261107-1418/receipt.json). This is stronger offline compatibility evidence, not equivalence to RIFT's embedded Lua/API/locale/global-memory behavior.
