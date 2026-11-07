# SC-614 — Lab2 native typed-definition filter agrees with both54-ID API captures

**Accepted scope: bounded observational agreement, November7,2026, not continuous-state or restart qualification.** Two native map samples contained the same134 unique keys in player context+0x1C0 and zero in+0x240. Existing typed-definition lookups resolved all134. The54 records with nonzero byte+0xC9 reconstructed to exactly the54 full IDs in both fresh RRECollector API captures; the80 zero-flag records were absent from both lists. No filtered extras or misses occurred. This makes a bare134-key map unsuitable as a substitute for the API-listed catalog in this observation.

The [machine/source/action receipt](REA-RIFT-SPELLCASTING-SC614-NATIVE-API-LIST-2026-11-07.json) retains exact IDs/names, source/reader/report hashes, acquisition clocks, cleanup and original image paths. [SC610](REA-RIFT-LAB2-CATALOG-2026-11-07.md) and [SC612](REA-RIFT-SPELLCASTING-SC612-ROGUE-UI-2026-11-07.md) establish the prior catalog/context work; this task independently sampled the larger native cohort.

## Method and source separation

Only Lab2 was live-tested: RIFT-LAB-2, VMX `C:\rift modding\VMs\RIFT-Lab-2\RIFT-Lab.vmx`, VNC5962, RIFT PID9752/start639294897826627677, `C:\RIFT_TRANSFER\RIFT\rift_x64.exe`,60,493,640bytes, SHA1935a05c9db6d468e34e0055014a4a99c1b5afceb1695884e24600f5c20a4be8. Fresh preflight16:21:33.9878227Z and post-interruption observation16:46:04.2956434Z agreed. No whole-module mapped hash or uninterrupted identity/role guarantee follows.

Reused three already installed, hash-matched RR2 Live publications: BF3EFA65 map sampler, F4148B83 typed-record sampler and B8A725E6 generic byte snapshot. No reader/backend/dependency was built or deployed; no external source changed. Source snapshots pin the published-record route at RR2 commit01bea03039549a901ce21aa7a9facf1602f5ac8a, file SHA349162b6a11f347a9470c0f301e403ac90e5375f234817bf11001ddb343a8a25. Later c7a39ed1 sources are separately labeled and not silently attributed to the older binary. Output/published hash equality is not reproducible-build attestation.

The native discovery/input distinction is explicit: the map enumerated134 keys; those keys, not the API54, supplied two67-key record lookups. A supplied lookup is not itself enumeration. Both map endpoints bound the complete key cohort. Existing source/type profiles qualify the definition route: registry0x3372C18, selector context0x33624C8/+0x40, type0x0051 with record vtable0x28A08C0/getter0x1899BF0 and descriptor0x344A6B0; primary/secondary children+0x8E0/+0x958 use type0x1E17 and localization DWORD+0x18. These are build-bound source profiles, not newly proven callable game interfaces.

Full ID reconstruction uses the map key as the high32bits and the modulo32 sum of the two child localization-key hashes as the low32bits. The hash uses signed32 interpretation, division by127773 truncated toward zero, multipliers16807/2836, signed overflow and the2147483647 correction. Independent Python stdlib code reproduced **all134 full IDs**, rather than comparing prefixes alone.

## Bracket, observations and interruption

| Stage | Observation |
| --- | --- |
| API-before | Reviewed Capture11:23EST, observed normal reload/save11:25; v0.4.11 sequence3, BolinaoL43Rogue role1,54raw/unique/details,0gaps |
| Map-before |16:28:42.7588897Z;134/0 entries;13.826ms acquisition |
| Record batches |16:31:30Z and following;67+67 records;33.347/32.097ms acquisition |
| Map-after |16:31Z; same134/0 keys;12.226ms acquisition |
| Scene interruption | Fresh image11:39:24EST showed Dimension:SanguineShores instead of SilverCoast; no RRE travel requested. Planned Hide rejected. User confirmed Lab2 free; fresh identity requalified. Second planned Hide rejected after scene/panel geometry changed again. |
| API-after | Reviewed Capture11:48EST, tooltip-bound normal reload/save11:49; v0.4.11 sequence4, same character/level/calling/role and exact54ID/name set |
| Settled image |11:53:45EST original shows in-world SilverCoast, RREv0.4.11/Known54; idle RR2 panel NOT RECORDING |

Both API files pass the existing literal-only structure gate. Its freshness/process-build/event-delivery flags remain false; composite acquisition evidence is separate. Endpoint agreement does not prove that role/world state never changed in between. The independent raw spotcheck occurred after the visible chat transition time and cannot restore uninterrupted trial control.

## Independent checks and recovery

The retained-data audit passed **1783 concrete assertions including five negative controls**: raw map24-byte key/float slices and0/-1 values, counts/unique cohort, exact native identity/player binding, requested CSV hashes/order, typed statuses, all134 public-ID calculations, exact before/after API IDs/names, distinct sequences, source-report hashes and owned guest cleanup. Negative mutations omit one flag-positive, retain the unfiltered map, alter a low ID word, drop a cohort key and change player identity. These counts are byte/data consistency checks, not1783 gameplay trials.

A different existing generic reader independently captured22ranges/146bytes for one positive QuickShot record and one typed zero-flag record. **44checks** verified raw+C9, vtable/getter/initialized descriptors and child localization values. It checks two records, not a separate raw reread of all134.

The initial native wrapper failed locally after successful map acquisition because its frozen-validator namespace omitted GAME_SHA. The successful map was retained/revalidated, not replayed; continuation v2 exited0. Independent audit drafts exposed verifier assumptions about overflow-node alignment and two artifact field shapes; those were corrected against actual source/data before the passing audit. No expected executable/tool hash, captured report or game state was changed to make checks pass.

All approved clicks released/disconnected/released the console mutex. Both rejected Hide reviews sent no input. A rejected-path result left consoleMutexReleased=false due to flag placement after the context manager; a separate nonabandoned acquire/release plus0establishedVNC/0mouse processes established actual cleanup. This task records the receipt limitation and does not repair the shared tool.

## What remains unknown

Nonzero+C9 and full-ID agreement identify the **API-listed subset in this sampled character/role**, not all learned, learnable, future/locked, currently usable or action-bound spells. The80 excluded entries have no such classifications. Static candidate absence, definition existence and a zero flag do not prove locks. Map float0/-1 pairs do not establish cooldown meaning. Sequential reads cannot exclude ABA or prove atomicity/passive freshness. There was no restart, cast, queue/GCD measurement, role/point/settings change, native callback, memory write or server-outcome test. SC103/SC306 and broader SC/RC/NAV gates remain unchanged. No Ollama/FreeBuff was used.
