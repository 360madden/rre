# RC-30 — post-start SavedVariables provenance (November 3, 2026)

**Outcome:** New saved-file hashes and timestamps verified. Collector v0.4.10 data integrity accepted as a bounded G1 source receipt; **RC-30 Pin → Undo remains PENDING**.

## Original local-file evidence

Read-only Windows inventory still identifies the physical game window at PID **33936**, HWND **16585300**. Its previously verified process start was **2026-11-03T11:09:52.813Z**. A later file modification does not independently prove that this exact process wrote the bytes.

| Original Atank SavedVariables | Modified UTC | Bytes | SHA-256 |
| --- | --- | ---: | --- |
| `RRECollector.lua` | **2026-11-03T17:33:57.499Z** | 74,216 | `4da64665b3bbc69ca5b6b2faa94dd6ed9b31e2508aca60c2af56748fe20ad056` |
| `RiftReader2Casting.lua` | **2026-11-03T17:33:57.539Z** | 41,751 | `c75d5420145d8e10a0ffd65b68851e9a71b950cb0c2d4fa8738eafc0d5ce44a5` |

Both are **later than** the last verified start of PID 33936. Previous accepted collector save: **2026-11-03 06:24 UTC**, 74,216 bytes, SHA `bdf78a8811cc9fa58fcf649bfd8fec98aa3bc93c9d02ec6c01398cc5582da8ac`. A different file SHA does not by itself identify which in-game UI action occurred.

## Second post-start file observation

A separate subsequent read at **2026-11-03T18:11:04.712Z** found another original collector SavedVariables write: **74,215 bytes**, SHA-256 `2c3bd03dc9e8a0018f23a6c8e2ca06acfd4d3f08dcfd12077a7a54c3c7aa72b0`. The same literal parser independently verified root **v0.4.10**, **69 known abilities**, **96 candidate entries**, **seven distinct valid saved IDs**, and **slot #8 empty**. This later observation is a separate immutable *measurement receipt*; the original on-disk file may continue changing while RIFT is active. It is invalid to assert that the earlier 17:33 source SHA still matches the *current* file. Neither measured snapshot is independently associated with a particular in-game Pin → Undo operation.

**Later-job receipt:** `rre-live-saved-source-drift-20261103-a1`, exit 0, sanitized output only.

## New SHA-pinned collector parse

The pre-existing literal-only `tools/read-rrecollector-saved.mjs` parsed the new file without emitting raw account or ability IDs:

| Field | Verified result |
| --- | --- |
| Root addon version | **0.4.10** |
| API-known abilities | **69** |
| Latest capture complete | **true** |
| Candidate catalog | **96** |
| Candidate statuses | **51 returned**, **38 listed-not-queried**, **7 no-detail** |
| Candidate lookup sequence | **5** |
| Valid saved pinned ability IDs | **7 distinct** |
| Saved slot #8 | **Empty** |

The seven-valid/slot-eight-empty **counts match** the prior accepted snapshot; exact ID-by-ID equality with the older original file is **not established**. The *first* exploratory fingerprint `278d3938...` was computed with the **same erroneous fallback** that duplicated slot 7 and is **not accepted**. For the independently verified **18:11 UTC** source SHA `2c3bd03d...` only, the correctly indexed eight-position canonical fingerprint is SHA-256 `c95f2b01a39a00b5feca1c4a7557afe864e9dd5bb950f155d6eb8004f65151bf` (job `rre-rc30-corrected-sevenpin-fingerprint-20261103-a1`, exit 0). No raw ability IDs were emitted.

### Corrected inspection bug

An earlier exploratory snippet **incorrectly reported eight** valid pins because it used `toolbarSlots[String(i+1)] ?? toolbarSlots[i]` and counted slot 7 again as a fallback for missing slot 8. That was an **inspection-code error**, not evidence that slot 8 was pinned. A strict validation failed on the false eight-distinct assumption; the corrected recheck verified **seven distinct valid IDs and empty slot 8**. An independent 310-character raw-text window contained eight ability-shaped tokens but crossed the logical table boundary and is **not** evidence of eight toolbar entries. Preserve all these receipts rather than silently discarding negative checks.

## Read-only job receipts

| Job ID | Outcome |
| --- | --- |
| `rre-sc306-sc503-saved-states-requalification-20261103-a1` | Exit 0; file timestamps/sizes/SHA |
| `rre-new-postpid-rc410-sanitized-persistence-20261103-a1` | Exit 0; valid v0.4.10 69/96 parse, flawed pin-tally method |
| `rre-rc30-new-poststart-8pins-distinct-20261103-a1` | Exit 1; identified contradiction in pin count / uniqueness |
| `rre-rc30-new-poststart-narrow-raw-20261103-a1` | Exit 0; raw-region corroboration only, insufficient for pin count |
| `rre-rc30-8pins-duplicate-count-20261103-a1` | Exit 0; authoritative corrected seven distinct IDs / empty slot 8 |
| `rre-live-saved-source-drift-20261103-a1` | Exit 0; separately newer 18:11 saved version/counts |
| `rre-rc30-corrected-sevenpin-fingerprint-20261103-a1` | Exit 0; canonical eight-position fingerprint of 18:11 source only |

Another one-file, key-only documentation check `rre-sc306-saved-settings-api-narrow-20261103-a1` found **no Inspect.Setting documentation key** and no literal `ActionBars_AbilityQueue` entry in this particular newly saved RiftReader2Casting documentation file. This does **not** prove the RIFT settings API or the enum mapping is absent elsewhere.

**Proof boundary:** No current in-memory eight-slot visual baseline, actual Pin → Undo before Reload UI, restored toolbar table or deliberately associated subsequent persistence is established. **RC-30 still requires its independent operator UI gate**; do not edit the installed collector, rewrite SavedVariables, or bypass the desktop capture quarantine.
