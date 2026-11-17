# WA-006 — RR2 native-reader managed source provenance (offline)

- **Date:** Monday, 2026-11-16, ~20:29 EST
- **Host:** verified **AMD-DESKTOP**, Workbridge 0.16.5-dev, `C:\work`
- **Scope:** read-only inspection of RR2 sister-repository build outputs and source, solely to qualify WA-006's proposed native `unit-positions` evidence path. No RR2 or game changes, build, binary execution, runtime attachment, process-memory read, UI action, or VMware access.
- **Decision:** **PASS for the stated managed DLL/PDB/current-source provenance checks**; **NOT a WA-006 G2/live acceptance**.

## 1. Exact observed artifacts

All paths below are under
`C:\work\riftreader2\src\RiftReader2.Live\bin\Debug\net10.0-windows\win-x64\`.

| Artifact | Bytes | Original SHA-256 | Interpretation |
|---|---:|---|---|
| `RiftReader2.Live.exe` | 162,304 | `59f7241db21edc92df416f77087c9fec4250a359c321a6acda334476e4476911` | Native .NET apphost; has its own generic Microsoft apphost CodeView, not the project source PDB |
| `RiftReader2.Live.dll` | 2,068,992 | `a79ffeddf8d680cbc46ef2453cb7b7945307e56c6759a39db647c2f8cb5d7c05` | Managed project assembly with project RSDS CodeView |
| `RiftReader2.Live.pdb` | 380,392 | `4752a0787ee728fd46fbfea130be1407bf50589e89ec46b78db1740075340508` | Portable PDB with source-document checksums |

Managed DLL RSDS GUID `b030556f-6fb5-4f3e-b021-b584728ea08e`, age 1, matches the Portable PDB `#Pdb` identity GUID. The apphost contains the ASCII target name `RiftReader2.Live.dll` at byte offset **151,904**; adjacent dependency/runtime configuration reports .NET 10 and Windows x64. **The apphost name is not a content hash and does not prove which DLL will load at runtime.**

## 2. Source-checksum result and independent reproduction

The Portable PDB document-checksum algorithm GUID is
`8829d00f-11b8-4213-878b-770e8597ac16` (SHA-256).
A bounded original-file comparison checked document-row SHA-256 blobs against the **current file bytes** at their decoded checkout paths.

| Managed project PDB | Document rows | Checked current files | Matching SHA-256 | Mismatches |
|---|---:|---:|---:|---:|
| `RiftReader2.Live.pdb` | 107 | 106 | **106** | **0** |
| `RiftReader2.Infrastructure.pdb` | 28 | 28 | **28** | **0** |

The one unexamined Live document row is **not counted as a pass**, and the result is not a universal claim about every application component. The Infrastructure DLL's own RSDS GUID also independently matches its PDB (`f63dbe7c-ac59-43c9-8347-572aa9e295a9`).

An independent read-only reviewer used a **separate Python standard-library ECMA metadata parser** to check `#~` Document rows, `#Blob` hash contents, `#GUID` hash-algorithm identities, and actual SHA-256 of two critical source files:

| Live PDB document row | Current source | Independently matching document/file SHA-256 |
|---:|---|---|
| 71 | `CurrentBuildUnitPositionsCandidateReader.cs` | `5f2927879b3f09ff259026e445c4f5b250a3ac9dc5aaecb8752d941390040c3f` |
| 102 | `WindowsNativeMemorySession.cs` | `d1dce81644909c901f8c5b8da52968788ef77de3144119537246250ddb47796d` |

The reviewer separately decoded Infrastructure's different metadata row width, matched its DLL/PDB identity, and reproduced **28/28** present-file hashes. This rules out the initial parser merely misinterpreting a fixed Live-specific row layout. The wider 106/106 Live comparison was made by the first investigator; the second reviewer independently confirmed the key native-reader files, **not independently every one of those 106 rows**.

Other positive managed current-source matches include
`CurrentBuildUnitPositionsSampleCommand.cs`,
`NativeReadFileLease.cs`, `CurrentBuildPlayerLookup.cs`,
`JsonReportWriter.cs` and `JsonFormat.cs`.
All evidence came from existing files; no rebuild invalidated these artifacts.

**Bounded receipt IDs:** `rre_wa006_proofwave_siblings_20261116_01`,
`rre_wa006_proofwave_allpdb_20261116_02`,
`rre_wa006_proofwave_apphost_20261116_03` (all exit 0; each below one second); independent peer QA three subsecond probes also exit 0.

## 3. What this does and does not prove

1. **Established:** The observed managed Live DLL matches its Portable PDB identity. The PDB's SHA-256 document records match the 106 current-source files examined; the native unit-reader's two most relevant source files were independently reverified. The Infrastructure DLL/PDB/source chain independently passes all 28 rows.
2. **Not established:** A cryptographic `Live.exe` → exact DLL-content binding; exact modules loaded by a running reader; the current running game's PID, scene, start time or memory contents; runtime success of the proposed read; RIFT Lua unit IDs corresponding to native unit keys.
3. **G2 trap:** RR2's `unitIdCandidate` is a `u%016X` **representation derived from the native key**, not an independent `Inspect.Unit.List()` observation. Historical raw unit fixture belongs to PID 18092; it cannot be paired with any newer physical-RIFT process. `worldIdentityStatus='unavailable'` requires an independent scene witness.
4. **Process discipline:** RR2 native `unit-positions` source is read/query/sync-only, bounded, and creates a local JSON/lease lock; **do not run without the exclusive live session owner's coordination**, current PID/start/PE check and output-ownership agreement. Static provenance alone does not authorize live execution.

## 4. Next smallest evidence-producing jobs

- **P0 — Live owner/epoch qualification:** Coordinate the sole physical RIFT owner, confirm the current AMD-DESKTOP PID/start/PE, scene witness and whether this exact reader binary is to be used.
- **P1 — Independently captured Lua packet:** One bounded `Inspect.Unit.List()`/optional XYZ observation with a complete original LuaPad BEGIN/END transcript, source checksum, owner/time receipt, and no movement, target changes or reload. Reuse `verify_wa006_g2_packet.mjs` (24/24 structural cases), which explicitly cannot accept WA-006 by itself.
- **P2 — Native correlation:** One bounded same-epoch native unit-position JSON under the owner's lease; hash original bytes and reuse RRE's historical `verify_wa006_evidence_matrix.mjs` precision/identity patterns and RR2's native join. Add only a narrow RRE Lua↔native gate **after** raw receipts exist; demand two distinct nonself ID+XYZ matches plus scene/timing identity. Preserve `nativeCorrelationDone=false` and `wa006Accepted=false` until demonstrated.

**Current WA-006 status:** G1–G5 **BLOCKED**; RC-30/RC-88 remain operator-stopped. This is an offline provenance milestone, not collision or gameplay proof.
