# RC-30 — post-start SavedVariables provenance (November 3, 2026)

**Outcome:** Post-start source hashes and v0.4.10 metadata qualified; **RC-30 Pin → Undo remains PENDING**. **IMPORTANT CORRECTION (later November 3):** [source-hashed eight-slot array correction](RRECOLLECTOR-RC30-EIGHT-SLOT-CORRECTION-2026-11-03.md) supersedes the earlier seven-slot/empty-slot-eight count and both erroneous fingerprints. The original 18:11 UTC save actually contains **eight distinct valid IDs in an implicit Lua array, slot #8 populated**; earlier 06:24/17:33 pin counts await a corrected reparse of their original bytes.

## Original local-file evidence

Read-only Windows inventory still identifies the physical game window at PID **33936**, HWND **16585300**. Its previously verified process start was **2026-11-03T11:09:52.813Z**. A later file modification does not independently prove that this exact process wrote the bytes.

| Original Atank SavedVariables | Modified UTC | Bytes | SHA-256 |
| --- | --- | ---: | --- |
| `RRECollector.lua` | **2026-11-03T17:33:57.499Z** | 74,216 | `4da64665b3bbc69ca5b6b2faa94dd6ed9b31e2508aca60c2af56748fe20ad056` |
| `RiftReader2Casting.lua` | **2026-11-03T17:33:57.539Z** | 41,751 | `c75d5420145d8e10a0ffd65b68851e9a71b950cb0c2d4fa8738eafc0d5ce44a5` |

Both are **later than** the last verified start of PID 33936. Previous accepted collector save: **2026-11-03 06:24 UTC**, 74,216 bytes, SHA `bdf78a8811cc9fa58fcf649bfd8fec98aa3bc93c9d02ec6c01398cc5582da8ac`. A different file SHA does not by itself identify which in-game UI action occurred.

## Second post-start file observation

A separate subsequent read at **2026-11-03T18:11:04.712Z** found another original collector SavedVariables write: **74,215 bytes**, SHA-256 `2c3bd03dc9e8a0018f23a6c8e2ca06acfd4d3f08dcfd12077a7a54c3c7aa72b0`. The literal parser independently verified root **v0.4.10**, **69 known abilities** and **96 candidates**. A later independently source-checked correction established **eight distinct valid saved IDs and a populated eighth slot**; the initial seven/empty result in this report was a JavaScript index error. This later observation is a separate immutable *measurement receipt*; the original on-disk file may continue changing while RIFT is active. It is invalid to assert that the earlier 17:33 source SHA still matches the *current* file. Neither measured snapshot is independently associated with a particular in-game Pin → Undo operation.

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
| Valid saved pinned ability IDs (corrected 18:11 source) | **8 distinct** |
| Saved slot #8 (corrected 18:11 source) | **Populated** |

The previously reported seven/empty baseline was **not valid for the implicit Lua array**. Two early fingerprints `278d3938...` and `c95f2b01...` were both derived using wrong JavaScript indices and are **rejected for this source**. For the independently verified 18:11 source SHA `2c3bd03d...`, the correct canonical eight-position fingerprint is SHA-256 **`b592926bdeaf9af039393efe956f32ee69cbdf9e7f13b9b0892d9c5333d9c160`** (independent raw-text and literal-parser verification). Exact ID-by-ID comparison with the older 06:24/17:33 original bytes remains unavailable. No raw ability IDs were emitted.

### Corrected inspection bug

The first exploratory code reported eight for an **invalid reason**: `toolbarSlots[String(i+1)] ?? toolbarSlots[i]` could duplicate an already counted ID while omitting array index 0. A subsequent code path incorrectly reported **seven** by reading keys 1–7 and treating absent JS key 8 as an empty eighth Lua slot. The corrected source inspection found an implicit array with **JavaScript keys 0–7**, plus an independently isolated raw `toolbarSlots` table containing **eight distinct ability-shaped values**. Earlier acceptance of seven was therefore wrong for source SHA `2c3bd03d...`. See the linked correction for each job receipt and scope limit.

## Read-only job receipts

| Job ID | Outcome |
| --- | --- |
| `rre-sc306-sc503-saved-states-requalification-20261103-a1` | Exit 0; file timestamps/sizes/SHA |
| `rre-new-postpid-rc410-sanitized-persistence-20261103-a1` | Exit 0; valid v0.4.10 69/96 parse, flawed pin-tally method |
| `rre-rc30-new-poststart-8pins-distinct-20261103-a1` | Exit 1; identified contradiction in pin count / uniqueness |
| `rre-rc30-new-poststart-narrow-raw-20261103-a1` | Exit 0; raw-region corroboration only, insufficient for pin count |
| `rre-rc30-8pins-duplicate-count-20261103-a1` | Exit 0; later **disproved** seven-slot interpretation caused by 1-based JS array indexing |
| `rre-live-saved-source-drift-20261103-a1` | Exit 0; separately newer 18:11 saved version/counts |
| `rre-rc30-corrected-sevenpin-fingerprint-20261103-a1` | Exit 0; later **disproved** fingerprint due to wrong array indexing |
| `rre-rc30-saved-toolbar-structure-only-20261103-a1` | Exit 0; original saved slots decoded as JS implicit array with indices 0–7 |
| `rre-rc30-raw-eight-slot-fingerprint-independent-20261103-a1` | Exit 0; independently confirms eight distinct IDs and correct `b592...` fingerprint |
| `rre-rc30-current-8slots-source-bound-20261103-a1` | Exit 0; new read-once checker proves eight distinct ID-shaped pins, eighth populated |

Another one-file, key-only documentation check `rre-sc306-saved-settings-api-narrow-20261103-a1` found **no Inspect.Setting documentation key** and no literal `ActionBars_AbilityQueue` entry in this particular newly saved RiftReader2Casting documentation file. This does **not** prove the RIFT settings API or the enum mapping is absent elsewhere.

**Proof boundary:** No current in-memory eight-slot visual baseline, actual Pin → Undo before Reload UI, restored toolbar table or deliberately associated subsequent persistence is established. **RC-30 still requires its independent operator UI gate**; do not edit the installed collector, rewrite SavedVariables, or bypass the desktop capture quarantine.
