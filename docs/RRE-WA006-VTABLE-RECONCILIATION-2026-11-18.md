# WA-006 vtable-overlap reconciliation — 2026-11-18 15:20 EST

## Scope and identity

- Host: **AMD-DESKTOP**, Workbridge **0.16.5-dev**, RRE `C:\work\rre` on `main`.
- Evidence source: archived RIFT build `STABLE-1-1179-a-1256672`, `rift_x64.exe` SHA-256 `df954b798331e18359be62a31cc74b49fc3f50b87385ebb080a5448256322c01`, **60,574,536 bytes**.
- Only SHA-pinned offline executable bytes and existing RRE source/tests were used. No physical RIFT input, process-memory operation, debugger, addon installation, VM or sibling-repository edit.

## Why this reconciliation was necessary

`docs/RRE-POSTPATCH-RECOVERY-SITREP-2026-11-17-1340-EST.md` rejected method `0x78D920` as evidence for a same-wrapper `+8` writer because a second constructor-referenced vptr begins only eight bytes after the first. The later `docs/RRE-POSTPATCH-OFFLINE-FOLLOWUP-2026-11-17-1506-EST.md` and `tools/verify_postpatch_wa006.py` nevertheless described three raw pointers as derived-wrapper virtual slots. This attributed a method to a particular receiver without verifying a dispatch or table-ownership boundary.

## Independent original-byte result

Bounded read-only RRE virtualenv probe `rre_20261118_vtable_6lea_17ptr_original_byte_02`: **exit 0**, SHA pinned.

| Constructor LEA RVA | Exact RIP target |
| --- | --- |
| `0xF7CC2E` | `0x271E468` |
| `0xF7D735` | `0x271E470` |
| `0xF7D9EC` | `0x271E470` |
| `0xF7DACA` | `0x271E470` |
| `0xF7DBAA` | `0x271E470` |
| `0xF835A4` | `0x271E470` |

- Exact pointers at RVAs `0x271E480`, `0x271E498`, `0x271E4C0` all contain VA `0x14078D920`. All three lie in overlapping address ranges potentially interpreted relative to either constructor-referenced pointer.
- Method bytes at `0x78D920`: `c7411800000000c74108eeff7f7fc3`. These encode a DWORD zero store at receiver `+0x18` and a DWORD `0x7F7FFFEE` store at receiver `+8`.
- The raw bytes are real. **The identity of the object actually receiving that method remains unqualified.** Constructor LEA targets eight bytes apart do not by themselves prove either that the tables are unrelated or that they share the same receiver. No same-wrapper dispatch was demonstrated.

## Corrective gate

`tools/verify_postpatch_wa006.py` now independently verifies the five additional constructor LEAs, the original wrapper vptr LEA/store, three absolute overlapping pointer positions and candidate method bytes. It reports:

- `adjacentConstructorLeasChecked=5`, `overlappingMethodPointersChecked=3`, `candidateMethodBytesPinned=true`
- **`sameWrapperField8WriterQualified=false`**
- `status=SOURCE_MAP_PINNED_ONLY`, `ownerQualified=false`, `runtimeQualified=false`

It no longer promotes the raw pointers to derived-wrapper virtual-slot ownership. `tools/test_verify_postpatch_wa006.py` asserts that matching pointer bytes plus adjacent constructor references cannot qualify receiver ownership, and mutates every protected LEA and pointer.

## Verification

- `rre_wa006_vtable_regression_tests_20261118_01`: **16/16 PASS**, exit 0.
- `rre_wa006_vtable_real_source_gate_20261118_01`: **SOURCE_MAP_PINNED_ONLY**, exit 0 against archived build; all new checks passed.

## Remaining work

1. **P0:** Identify an instruction-aligned dynamic dispatch receiver reaching `0x78D920`, with same-object evidence before upgrading same-wrapper writer status. Do not repeat the already negative broad scans.
2. **P1:** Independently qualify currently active postpatch physical-RIFT process/adapter only within the current owner and approval gates; disk SHA does not prove a running image's mapped bytes.
3. **P2:** RRECollector v0.4.21 disk parity and persisted initialization have advanced, but full same-trial native RREC2 plus SavedVariables acceptance remains open. Preserve RC-30/RC-88 stop states.

All nine pre-existing untracked RRE items remain outside this change.
