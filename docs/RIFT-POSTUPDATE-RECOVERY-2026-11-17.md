# RRE post-update recovery gate — 2026-11-17 (AMD-DESKTOP)

Status: **POST-PATCH EXECUTABLE CONFIRMED; NATIVE COMPATIBILITY BLOCKED**. Captured independently on AMD-DESKTOP around 09:18–09:23 EST. This document is a recovery checkpoint, **not** a declaration that RRE is functional on the new client.

## Authoritative binary identities

| | Pre-update preserved baseline | Installed post-update |
|---|---|---|
| Game version (Update Helper capture) | STABLE-1-1177-a-1256632 | STABLE-1-1179-a-1256672 |
| SHA-256 | `1935a05c9db6d468e34e0055014a4a99c1b5afceb1695884e24600f5c20a4be8` | `df954b798331e18359be62a31cc74b49fc3f50b87385ebb080a5448256322c01` |
| Bytes | 60,493,640 | 60,574,536 |

Installed physical file (read-only investigation): `C:\Program Files (x86)\Glyph\Games\RIFT\Live\rift_x64.exe`.

SHA-named, hash-verified analysis copies (preserve; outside Git):
- Old: `C:\work\RIFT-Build-Baselines\1935a05c9db6d468e34e0055014a4a99c1b5afceb1695884e24600f5c20a4be8\rift_x64.exe`
- New: `C:\work\RIFT-Build-Baselines\df954b798331e18359be62a31cc74b49fc3f50b87385ebb080a5448256322c01\rift_x64.exe`

The newly archived copy, the installed file before copying, and the installed file afterward were each SHA-256 verified to the new digest. Machine identity independently verified by native PowerShell (`AMD-DESKTOP`).

## RRE's reproducible executable report

Run `& 'C:\work\rre\tools\Run-RiftUpdateAnalyzer.ps1'` on AMD-DESKTOP after the updater is idle. The first post-update run produced:
`C:\work\rre\artifacts\rift-update-analyzer-20261117-141843-68528324\report.json` and `report.md`.

Result `CHANGED`, **exit 2 as designed**, not a broken analyzer; schemaVersion 1, stable input double-hash check, four SHA-pinned anchors, seven PE sections. `nativeOffsetsQualified=false`; runtime requalification required.

- `.text` bytes changed, raw size 39,772,160 -> 39,826,944 (+54,784 bytes).
- `.rdata`, `.data`, `.pdata`, `.rsrc`, `.reloc`: bytes changed.
- `_RDATA`: content hash unchanged but section RVA moved 0x3965000 -> 0x3978000.
- ROOT001 old-RVA instruction canaries all differ at those old addresses:

| Semantic label | Old RVA | Old bytes | New bytes **at same RVA** |
|---|---|---|---|
| dispatch_forward_host_rdx | `0x779C6D` | `48 8b 54 24 50` | `9f eb 00 00 48` |
| adapterB_save_host_r13 | `0xFCA11F` | `4c 8b ea` | `ff 48 8b` |
| adapterB_restore_host_rcx | `0xFCA4AD` | `49 8b cd` | `85 db 75` |
| adapterB_processor_call | `0xFCA4B0` | `e8 2b e1 7b ff` | `7a b9 10 00 00` |

These results **invalidate reuse of the four old addresses**. They neither locate equivalent new functions nor prove those functions were removed. No current runtime/native pointer chain, callback identity, receiver identity, or vtable is accepted yet. Historical old-build evidence remains valid for the SHA to which it is pinned.

## Shared Update Helper evidence (read-only reuse)

The separately maintained `C:\work\Update Helper` repository holds:

- `data\RIFT-Live-baseline-20261117-0742EST-verified.json`
- `data\RIFT-Live-postpatch-20261117-0915EST-rr2.json`
- `data\RIFT-Live-diff-20261117-0916EST-rr2.json` and `.md`

The RR2-produced before/after manifests report **7 modified, 2 removed temporary Download files, 0 added, 265 unchanged**. Modified: `rift_x64.exe`, `rifterrorhandler_x64.exe`, `manifest64.txt`, `assets64.manifest`, `assets64_debug.manifest`, `assets64_dev.manifest`, and `Assets/assets.242`. RRE independently confirms the executable hash/size; other file-level counts are attributed to the Update Helper manifests.

Do **not** rehash all ~25.27 GiB of game assets for this RRE checkpoint. Do **not** edit or commit in Update Helper: its comparison source/tests currently include active owner changes. Update Helper owns file-level patch evidence; RRE owns RRE-specific behavior and native compatibility qualification.

## Fail-closed recovery tasks

1. **P0 — Rebuild ROOT001/WA-006 static identities against the new archived executable.** Use bounded offline binary/REA/Ghidra analysis and independent matching of control flow and callsites. Store new-build-specific candidate RVAs, source windows, section hashes, provenance, and confidence; avoid large default Ghidra reimports. Do not rewrite historical SHA pins to make old tests pass.
2. **P1 — Distinguish archived-only green tests from installed-client gates.** `tools/agents/collision/verify_wa006_wrapper_parent_route.py` and `tools/verify-root001-registry.mjs` can pass using old archived PE only. `verify_current_query_wa006.py` and `verify_wa006_candidate_pointer.py` read installed PE but pin the old SHA and therefore must fail closed on this update. Test acceptance must explicitly include **new SHA** and independently checked semantic evidence.
3. **P2 — Physical-only runtime requalification when a specific test requires it.** Independently verify new build, process/window owner and authorization; then revalidate native reads/receiver linkage and addon telemetry, without inferring compatibility from static canaries. RRECollector v0.4.21 installed-file parity was verified previously, but the last directly observed loaded UI/save was v0.4.20. SC-629 still open; RC-30/RC-88 remain stopped. Coordinate before any gameplay/UI input, reload, restart, or process access.

No VMware interaction, RIFT input, reload, process modification, addon deployment, or game restart was performed in this checkpoint. Do not install or launch the archived executable; archives are analysis-only.

## Evidence/job IDs

- Current executable hash: `rre-postupdate-exe-sha1117-1` and independent `rre-review-postupdate-readonly-sha-1117-1`.
- RRE analyzer: `rre-postupdate-compare-original-new-1117-1` (expected exit 2).
- Four-anchor/section extraction: `rre-postupdate-compact-sections-1117-1` (exit 0).
- Prearchive collision check: `rre-postupdate-archive-preflight-1117-1` (exit 0).
- Archive+independent source/destination rehash: `rre-postupdate-archive-newsha-1117-1` (exit 0).
- RRE analyzer synthetic regression suite: `rre-postupdate-regression-suite-1117-1` (13/13 tests passed, exit 0; Python 3.14).
