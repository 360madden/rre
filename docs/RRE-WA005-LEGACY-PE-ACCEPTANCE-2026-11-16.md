# RRE WA-005 exact-build validation acceptance — 2026-11-16 12:02 AM EST

## Outcome and scope

**WA-005 offline inspector QA and complete research gate passed.** Three independent static source/delta review lanes WA-005A/B/C were accepted in [the prior QA report](RRE-WA005-INDEPENDENT-QA-2026-11-15.md). Inspector v1.1.2 remains SHA-256 `fdbc066c2da4a929fc8219a839ba8c02d72aad741f8157c8584cac5933347eb6`; its 67 focused tests and the 358-test RRE Node suite passed earlier. The new full nine-group gate passed **550 tests**, exit **0**, with no Python skips/duplicate IDs and stable tool-source hashes.

This is **offline source/fixture validation, not live world awareness**. WA-006 coherent non-self-entity/physics/camera evidence remains blocked, and WA-007's native-to-gameplay-identity connection is not proven. There was no RIFT process attachment, game input, UI reload, game/Windows restart, VM contact, installer, or deployment in this execution.

## Critical exact original PE discovery

A scoped read-only candidate search on **AMD-DESKTOP** found the historic executable in a pre-existing RiftReader2 artifact:

- Exact archive: `C:\work\riftreader2\artifacts\power-locator-20261025-01\rift_x64.exe`
- Size: **59,963,840 bytes**
- SHA-256 independently computed by Python: `7c356c9dde9e12fcbff3c08d953b0630b48b1510a0ffb36e4ec164606e7b17bd`
- Hash job: `rre_20261116_0706_old_pe_hash_python_01`, exit 0
- Earlier native-test source constants require precisely this hash and byte layout.
- The newer installed physical client and the archived RRE guest PE are **60,493,640 bytes**, SHA `1935a05c9db6d468e34e0055014a4a99c1b5afceb1695884e24600f5c20a4be8`. They are **not** interchangeable with the historical client.

The archive was **not** copied, moved, modified, staged, or installed. A complete bounded RRE-only search found no 59,963,840-byte executable or ZIP member in RRE itself; the matching file is in the sibling RiftReader2 repository. A general `C:\work` filename search identified it, and the exact SHA check qualified it. Historical RVA/manifest/opcode and PE-hash assertions were preserved.

## Implementation

Code commit: **`701cbc45500dc27cb2b43a44b1653c8cb58bdf35`** (`test(native): gate historical PE suites on explicit pinned archive`).

- `tools/agents/legacy_pe_fixture.py` provides a fail-closed exact-size/SHA selector requiring `RRE_LEGACY_PE` in native tests.
- `tools/validate-research.py --legacy-pe <original-PE>` independently preflights the archive **before** output creation; records its canonical path/size/SHA, isolates the environment to the collision/pathfinding groups, and hashes the archive again after all nine groups.
- Existing native verifier functions taking `binary=` receive the qualified path in their discovered tests. The displacement scanner now accepts an optional explicit binary argument; all seven test scan call sites use the qualified archive.
- `tools/agents/validation/test_legacy_pe_fixture.py` adds six positive/negative unit tests. No original evidence manifests or RVA/hash pins were rewritten.

**Boundary:** Some standalone legacy verifier CLIs still default to the installed path if invoked independently. The guarantee established here is that the **discovered research-gate test paths** never silently select the installed executable. Standalone utility selection is a separately scoped follow-up.

## Actual validation receipts

| Check | Job/evidence | Verified result |
|---|---|---|
| Fixture selector tests | `rre_20261116_0738_helper_test_01` | 6/6, exit 0 |
| Missing `--legacy-pe` | `rre_20261116_0738_missing_flag_01` | Expected rejection, exit 2 |
| Mismatched newer archived PE | `rre_20261116_0748_wrongbuild_cli_01` | Expected size rejection, exit 2 |
| Focused collision | `rre_20261116_0751_collision_focused_legacy_01` | 9/9, exit 0 |
| Focused pathfinding | `wafb_20261116_focused_suites_01` | 39/39, exit 0 |
| Complete research gate | `rre_20261116_0804_fullgate_original_01` | **550/550, nine groups passed, exit 0** |
| Diff formatting | `rre_20261116_0812_legacy_diff_check_01` | Exit 0; Windows LF/CRLF warnings only |

Full research receipt: `artifacts/research-gate-original-pe-20261116-0502-v1/validation.json`, SHA-256 `c19bb7c7f6698eb6a1c9a65a6feec2dd94ab13405dd8acb6f58757e1bd82b249`. Group counts: validation 171, C2M 30, follow 73, collision 47, pathfinding 57, navigation evidence 97, visual evidence 58, review adapter 17, roadmap 0. Receipt confirms `sourcesUnchanged: true`, `duplicatePythonTestIds: 0`, and `legacyPeFixture.unchangedAtEnd: true`.

Neither expected-rejection CLI attempt created its intended output directory. Source changes received independent integration architecture review by `/root/wa005c_no_tool_review`, with no high-severity issue found. Reviewer runtime session IDs and raw event traces were not exposed and are not invented.

## Safe repeat command

From **PowerShell in `C:\work\rre` on independently verified AMD-DESKTOP**, using a **new** output directory:

```powershell
& 'C:\work\rre\.venv\Scripts\python.exe' -B tools/validate-research.py --legacy-pe 'C:\work\riftreader2\artifacts\power-locator-20261025-01\rift_x64.exe' --output-dir 'artifacts\research-gate-next'
```

Never substitute the newer installed executable or rewrite expected hashes to force a pass. If the archive is unavailable/changed, the runner must exit 2 rather than disassemble a mismatched build.

## Next bounded priorities

1. **P0 WA-006 preparation:** Draft a precise coherent one-scene physical-RIFT player + distinct-entity + collision-hit + camera-landmark evidence protocol, identifying exact missing producers and preconditions. No live test without a separate, task-scoped approval and host proof.
2. **P1 standalone native verifier alignment:** Inventory remaining independent CLI defaults to installed `rift_x64.exe`; propose explicit optional archive selection with the same strict pins only where operationally valuable. Do not change the archived evidence.
3. **P2 durability and status:** Keep the task board/current roadmap and handoff synchronized to commit `701cbc4`, this accepted 550-test receipt and the still-blocked WA-006/007 scope. Preserve inherited untracked backups/probes and do not push without need.
