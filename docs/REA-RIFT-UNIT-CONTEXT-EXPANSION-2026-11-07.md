# SC628 — Versioned unit context accepted in bounded Lab2 transfer

RRECollector0.4.13 adds optional `race`, `raceName`, and `zone` to the existing player/target Unit.Detail projection, reusing the same API results. No extra lookup, polling, event, inbound command or gameplay action is introduced. [SC626 source research](agents/rre-context-api-reference-2026-11-07.md) establishes the documented field meanings; no race enum, zone display name or undocumented decoration field is invented. Missing values remain unknown; retained non-string/empty raw scalars remain semantically unqualified.

Reader0.1.3 accepts exactly collector0.4.12 and0.4.13. It binds identical versions across all frame parts and the document, preserves the original20-field0.4.12 unit maps, and permits the three extra fields only in0.4.13 (23-field bound). Source evidence reports the actual decoded producer version. The [wire contract](../reader/contract-rrec2.md) records these rules.

Validation passed140C# checks and20Node tests. SHA-pinned existing Lua5.1 and5.3 runtimes each passed11actual-context-module checks (including target projection and exact existing call counts),13Capture lifecycle checks,10prior-snapshot preservation checks and the synthetic publisher checks. Both runtimes produced byte-identical synthetic and historical54-record carrier frames. Explicit assertions verify new metadata and decoration exclusion. Historical fixture retagging remains offline-only.

Separately, the exact original SC6220.4.12 snapshot/request replayed through reader0.1.3 with all modules exactly equal to the accepted prior output and producerVersion still0.4.12. This is compatibility evidence, not a new live acquisition. The strict11-file package gate passed; required TOC fields/environment were independently compared with the retained recognized BotDsBridge TOC. Neither that comparison nor source parsing establishes installation/load.

The coherent-source legacy gate ran once:500tests, exit1, the same older-build collision/pathfinding SHA guards; seven other groups passed and sourcesUnchanged=true. Old pins were not changed. [Machine-readable source/evidence hashes](REA-RIFT-UNIT-CONTEXT-EXPANSION-2026-11-07.json) retain exact receipts and limitations.

Two built-in read-only reviewers examined Lua/package and C# compatibility independently. Their concrete documentation and coverage findings were addressed. No Ollama, FreeBuff or dependency install occurred. The source/offline gate preceded the separately coordinated live phase below. SC625 remains a separate incomplete acquisition-adapter task.


## Bounded live acceptance — November7,15:36–15:43EST

RR2 granted an exclusive Lab2 window20:36:32.953019Z–20:51:32Z with RR2 reporting controller absent, queue holder null/BLOCKED and no active RR2 Lab2 native jobs; its original handoff receipt is retained as `peer-grant-before.json`. Existing user authorization permitted only RRECollector files to synchronize through the observed OneDrive root. Fresh parent-chain/root, exact VM epoch, unique RIFT process/path/build, all11installed0.4.12 hashes and all11rollback backups passed. The full reviewed0.4.13 package copied with TOC last; postcopy guest inventory and host readback passed11/11. This RRE workflow deployed only those11RRECollector files and did not invoke settings, other-addon, Lab1 or physical-client routes.

Three fresh original-screenshot-reviewed external vncdotool clicks performed Reload UI, Capture and Reload UI to persist. The visible toolbar changed0.4.12→0.4.13; the final scene remained playable Silver Coast with Bolinao L43 Rogue/role1. All three button releases/connections/mutex releases passed. There was no travel, cast, text command or new API call beyond the existing Capture/startup paths. Last guest identity remained PID9752/start639294897826627677,60493640-byte executable SHA1935a05c9db6d468e34e0055014a4a99c1b5afceb1695884e24600f5c20a4be8.

Fresh Capture reported session`0b6399207d0e277158ee6c11c3af1bd4`,sequence7,fiveparts,18295bytes,54API-listed records. One bounded F414 scout attempted770723840bytes, returned partial/time-budget with six candidates and five exact full-prefix starts. The standard snapshot copied those complete frames; the pinned host reader0.1.3 validated and preserved all records/context/counts exactly. Payload SHA589ac1afffe7026ad7055d90211c504db1c6248af63da5b7638b9a50cd73a774. Partial scan coverage establishes no whole-process absence or uniqueness outside inspected memory.

| Player field | Observed API/wire/persisted value |
| --- | --- |
| race | `mathosian` |
| raceName | `Mathosian` |
| zone | `z0000000CB7B53FD7` |

The subsequent normal reload produced a fresh21972-byte SavedVariables file, SHAa21e5c429173b3e3414f8eb54d07b0cb9c6ebcb2864ac3dc30906b357160a459. Root/capture0.4.13,sequence7,session,parts,length and Adler2fcd6fa3 agree with the captured publication. All three metadata strings agree exactly. Full comparison covered545scalars:150/164numbers exact,14equal to wire values formatted to14significant digits and the samefloat32bits;381other scalars exact. One empty target-table ambiguity was normalized. These are explicit observed representation differences, not bit-exact double equality or proof of RIFT's serializer.

Original images, scripts, native request/snapshot, decoded document, strict-reader output, SavedVariables and comparison are retained under `artifacts/sc628-live-context-20261107-1533/`; [the machine report](REA-RIFT-UNIT-CONTEXT-EXPANSION-2026-11-07.json) hashes every artifact. The package README remains its frozen source-time predeployment record; this later report records observed acceptance.

Last guest operation completed20:43:03.011514Z. After final scene review, a host-only nonabandoned console-mutex acquire/release passed and control was explicitly returned20:43:52.595787Z, before the deadline. Scout/snapshot/Saved temporary guest artifacts were removed, no RRE live job remains, and neither controller nor queue was changed. No further Lab2 operation is authorized by that expired/returned window. Passive freshness, continuous acquisition, inbound commands, source authentication, atomicity and restart qualification remain open.
