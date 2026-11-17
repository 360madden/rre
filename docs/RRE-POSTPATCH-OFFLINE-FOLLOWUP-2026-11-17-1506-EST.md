# RRE postpatch offline discoveries — 2026-11-17 15:06 EST

## Identity, scope, and evidence

- Host: **AMD-DESKTOP**, named Workbridge instance 0.16.5-dev; repo `C:\work\rre` on `main`.
- New archived source: RIFT `STABLE-1-1179-a-1256672`, `rift_x64.exe`, SHA-256 `df954b798331e18359be62a31cc74b49fc3f50b87385ebb080a5448256322c01`, 60,574,536 bytes.
- Old source: `STABLE-1-1177-a-1256632`, SHA-256 `1935a05c9db6d468e34e0055014a4a99c1b5afceb1695884e24600f5c20a4be8`.
- Original full selector analysis: [RRE-POSTPATCH-SELECTOR-RECOVERY-2026-11-17-1406-EST.md](RRE-POSTPATCH-SELECTOR-RECOVERY-2026-11-17-1406-EST.md). This document is an incremental supplement, not an amendment of the earlier evidence.
- Independent read-only offline investigators: `guard_context`, `wa006_alias`, `state_transitions`, with separate exclusive questions and no source edits. Lead independently redecoded critical raw bytes using Capstone from the same SHA-pinned archive (`rre_dual_predicate_independent_20261117_1508`, `rre_postpatch_anchors_20261117_1504`, both exit 0).
- **No live client, current game executable, VM, process, memory, game input, addon installation, or sibling repository was touched.** State names and field meanings remain intentionally unknown.

## ROOT001: Path A context predicate

At RVA `0x81BFF0(context)`, the exact postpatch machine-code behavior is:

| Branch | Returned result | Source |
| --- | --- | --- |
| Byte `[context+0x3A] != 0` | true | `0x81BFF4: 80793a00`, `0x81BFF8: 7527` |
| Else `[context+0] == NULL` | `[context+0x10] != -1` | `0x81BFFA: 488b01`, `0x81C002: 48837910ff`, `0x81C007: 0f95c0` |
| Else byte `[context+0x38] != 0` | false | `0x81C00F: 80793800`, `0x81C013: 7513` |
| Otherwise | result of `0x81F5F0([context+0])` | `0x81C018: e8d3350000` |

The delegate `0x81F5F0` returns true immediately for `[object+0x2E0]==0`; returns false for both `+0x2E0` and `+0x2E1` nonzero; otherwise has protected-section/pointer-related checks involving `+0x2E2`, `+0x338`, `+0x3C8`, `+0x3D0` and helpers `0x81DF20`/`0x81DCF0`. Those checks do **not** yet identify a gameplay domain.

Instruction/PDATA-aligned direct-call census to `0x81BFF0`: `0x788243`, `0x788394`, `0xFCE978`, `0xFCEE8F`, `0xFCEEE4`, `0xFCEF56`, `0xFD07A4`. Source-pinned core predicate opcodes and direct call to `0x81F5F0` are now verified by the ROOT001 gate.

## ROOT001: more of the same singleton state machine

The state manager `0x9D57D0` is called with the singleton object in RCX and desired state in EDX. Source disassembly supports these **conditional paths**, not unconditional runtime transitions:

| Old state | Native action | Source evidence |
| --- | --- | --- |
| 0 | call `0x9D5C60`; guarded writer sets QWORD 1 | call `0x9D580E`, state-zero guard `0x9D5C85: 833900`, write `0x9D5CAD: 48c70101000000` |
| 1 | call `0x9D58B0`; either path may set DWORD 2 | null+8 path `0x9D58D8` (previously pinned), alternative `0x9D5C14: c70702000000` |
| 2 | write QWORD 3 | `0x9D5839: 48c70303000000` |
| 3 | call cleanup `0x9D6FC0` until zero | `0x9D588B: e830170000`; `0x9D6FDE: 833903` checks 3; `0x9D6FE1: 488bf9` saves receiver; `0x9D76F9: 33f6` clears ESI; `0x9D77C4: 8937` writes zero to saved receiver; manager `0x9D5890–0x9D5893` retries while nonzero |

The manager returns early for already-matching requested/current states and has explicit filters for prior state 2/desired 1 and prior state 0/desired 3. **Follow-up at 15:09 EST:** independent bounded Capstone CFG analysis from `0x9D6FC0` to `0x9D77C4` visited **547 instruction/ESI-state pairs**, with no unresolved indirect edge before the write; every path reaching the write had ESI zero, from `xor esi,esi` at `0x9D70E9`, `0x9D710D` or `0x9D76F9`. The manager selects the prior-state3 helper at `0x9D5883–0x9D588B`, checks `[rbx]==0` at `0x9D5890`, and repeats the call while nonzero at `0x9D5893`. The lead independently redecoded the guard, saved receiver, zeroing, store, direct call and retry bytes (`rre_independent_state3_trace_1517`, exit0). This establishes a **conditional source-level 3→0 transition**, completing a source cycle `0→1→2→3→0`, without proving live execution, termination, or game-state semantics. The gate now pins state-zero guard, 0→1 and alternative 1→2/2→3 write opcodes, plus the direct 0-state initialization-helper target. Its 15:09 follow-up additionally pins the **state3→0** source branch/receiver/zeroing/store/retry opcodes and direct cleanup call. `checkedStateManagerOpcodes=12`, `checkedStateManagerCallTargets=2`, `stateThreeToZeroSourcePinned=true`; still no runtime acceptance.

## WA-006: derived wrapper virtual setter (bounded source breakthrough)

- Wrapper constructor `0xF7CC20` calls base `0x13E9A10`. At `0xF7CC2E: 488d0533187a01` it obtains derived vtable RVA `0x271E468`; `0xF7CC3F: 488903` installs it on the wrapper.
- Three derived vtable slots `+0x18`, `+0x30`, `+0x58` all contain VA `0x14078D920` (`20d9784001000000`).
- Method `0x78D920`: `c7411800000000` writes DWORD 0 to `[rcx+0x18]`; `0x78D927: c74108eeff7f7f` writes **nonzero DWORD `0x7F7FFFEE`** to `[rcx+8]`; then returns.
- This is a demonstrated source-level derived-virtual method capable of writing the field. It **does not** prove that a live singleton wrapper invokes it or that the value is a pointer or service identity. It may be a sentinel; the previously examined consumers read a 64-bit quantity. Do not reinterpret the field from the store alone.

**15:09 EST bounded dispatch follow-up:** direct rel32 call scan found no callers of `0x78D920`, and eight PDATA-qualified constructor-caller functions contained no virtual calls at slots `+0x18/+0x30/+0x58`. One separate function uses indirect `[rax]` calls without demonstrated wrapper receiver. This is a **narrow negative**, not proof the method never executes. Stop broad repeated searches.

The WA-006 source gate now checks the exact constructor LEA target/vptr store, all three virtual slots, and complete 15-byte method source. It continues returning `ownerQualified=false` and `runtimeQualified=false`. No blanket claim of same-live-instance owner/writer has been made.

## RRECollector offline release check

`node tools/verify-rrecollector-package.mjs` passed (exit 0): version **0.4.21**, strict manifest, **11** source files, `installedShaMatches=null`, `runtimeUiVerified=false`. This is a source packaging check only. RC-88 remains user-stopped; no reload/deployment was attempted.

## Reproducible verification (AMD-DESKTOP)

| Command from `C:\work\rre` | Result / job receipt |
| --- | --- |
| `.venv\Scripts\python.exe -B tools/test_verify_postpatch_root001_b.py` | **26/26**, `rre_postpatch_1513_root_tests`, exit 0 |
| `.venv\Scripts\python.exe -B tools/test_verify_postpatch_wa006.py` | **15/15**, `rre_postpatch_1513_wa_tests`, exit 0 |
| `.venv\Scripts\python.exe -B tools/test_rift_update_analyzer.py` | **13/13**, `rre_postpatch_1515_analyzer_tests`, exit 0 |
| `.venv\Scripts\python.exe -B tools/test_verify_prepost_root001_layout.py` | **10/10**, `rre_postpatch_1515_crossbuild_tests`, exit 0 |
| `.venv\Scripts\python.exe -B tools/verify_postpatch_root001_b.py` | `SOURCE_PINNED_ONLY`, `rre_postpatch_1513_root_real`, exit 0 |
| `.venv\Scripts\python.exe -B tools/verify_postpatch_wa006.py` | `SOURCE_MAP_PINNED_ONLY`, `rre_postpatch_1513_wa_real`, exit 0 |
| `.venv\Scripts\python.exe -B tools/verify_prepost_root001_layout.py` | `SOURCE_PINNED_ONLY`, `rre_postpatch_1515_crossbuild_real`, exit 0 |
| `git diff --check` | exit 0; line-ending conversion warnings only |

**Total: 64/64 unit tests passed.** The state3→0 anchor extension was independently rerun after integration: ROOT001 26/26 (`rre_postpatch_state3_1512_root_tests`, exit0), archived ROOT001 gate `SOURCE_PINNED_ONLY` with `checkedStateManagerOpcodes=12` and `checkedStateManagerCallTargets=2` (`rre_postpatch_state3_1512_root_real`, exit0), and `git diff --check` (`rre_postpatch_state3_1512_diffcheck`, exit0). Other suites remained unchanged and passed earlier in the same integration. Both build layouts remain incompatible at source field/mask level. All runtime/function/owner qualification flags stay false.

## Next acceptance order

1. **P0 (Joey approval required):** exact current AMD-DESKTOP physical process/build/owner identity, then tightly bounded read-only receiver/adapter qualification. Source-static result alone cannot accept postpatch runtime compatibility.
2. **P1 (autonomous offline, only if decision-changing):** further qualify context delegate `0x81F5F0` or a specific WA006 dispatch receiver if a fresh source lead appears; avoid broad repeated scans after the targeted negative.
3. **P2 (requires coordinated physical-client evidence for runtime acceptance):** verify loaded Collector v0.4.21 UI/installed parity only after a normal operator-led addon load and relevant permission; the source-only 11-file check is not runtime proof.

Preserve all nine historical untracked entries and do not reactivate stopped Collector RC-88 or any VM/testing controller.
