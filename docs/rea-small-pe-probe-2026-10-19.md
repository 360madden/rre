# REA small-PE bridge qualification — 2026-10-19

## Decision and outcome

**A small, disposable native x64 PE probe successfully completed a real REA 6.5.0 / Ghidra 12.1.2 procedure-resolution request in 19.574 seconds.** This proves that the installed Windows provider can analyze a supported tiny PE and export evidence. It **does not** repair the two prior 450-second whole-client startup timeouts, identify active player pathfinding, or establish a callable game interface.

The existing **raw-x64** approach is **not supported** by the installed REA Windows Ghidra provider. The first 603-byte headerless request failed at `open_binary` with `capability_unavailable / target_format_unsupported`: Windows Ghidra P0 admits native PE x86/x64 and specifically selected raw 6502, not raw x64. Do not retry that unchanged profile or infer this is a general REA inability to analyze native PE.

## Exact provenance

- Original read-only input: `C:\Program Files (x86)\Glyph\Games\RIFT\Live\rift_x64.exe`; SHA-256 `7c356c9dde9e12fcbff3c08d953b0630b48b1510a0ffb36e4ec164606e7b17bd`.
- Native dispatcher fragment RVA `[0xF3FA4, 0xF41FF)`: 603 bytes, SHA-256 `6f31c492e5028ed20758e711746dc3152406e6db9b0273336f2b5224d6636e8b`.
- **Synthetic** PE: `artifacts/navigation-pe-slice-probe-20261018-01/dispatcher-synthetic-pe.exe`, 2,560 bytes, SHA-256 `0ee37d4a6d3030ae13ec39528af8ae183443ac8f0940b8c6a0cf8e462ebb953c`; its entry is rehomed to static VA `0x140001000`, *not* the Rift module's actual RVA. This PE contains a **partial relocated code slice**, not the full game binary, imports, native data or real cross-references.
- Builder: `tools/agents/ghidra/prepare_pe_slice_probe.py`, using the existing test suite's synthetic PE fixture and read-only `pefile` mapping. It refuses to overwrite any existing output namespace. For a fresh offline replay use `C:\work\rre\.venv\Scripts\python.exe -B tools/agents/ghidra/prepare_pe_slice_probe.py --run-id YYYYMMDD-token` with a unique token. The original run's default is `20261018-01` and remains protected; never delete old evidence to rerun.
- Manifest: `artifacts/navigation-pe-slice-probe-20261018-01/source-manifest.json`, SHA-256 `a6a070c3ab72dbf30291ed42cf6e34d657400c4c13afed4004808d321ecfcc65`. Manifest records both original and synthetic hashes, builder hash and no-game-input flags.
- Validated real REA job: `rre-resume-mini-pe-rea-20261019-01`, exit **0**, 2026-10-19, invoking existing `tools/rea-session.mjs` with `artifacts/navigation-pe-slice-probe-20261018-01/session-profile.json`.

## Observed REA response

REA connected, admitted the synthetic PE, initialized Ghidra and returned a successful `resolve_containing_procedure(address=0x140001000)`. The result reported one procedure named `entry`, full **603-byte** contiguous body `0x140001000..0x14000125A`, with evidence ID `ev_b804c0633592ca4c8430baefd9733d1f4e9a1721a7173a5e65c4a6e30da9485b`. Evidence export reported **one** record; close produced a snapshot. Source remained immutable, no game process attached, and no game input sent.

- `artifacts/navigation-pe-slice-probe-20261018-01/session/status.json`: SHA-256 `fa7e9071ef49319eae08fdfdeb59804b9571bbbc7d7d5475694235199838166c`.
- `artifacts/navigation-pe-slice-probe-20261018-01/session/responses/01-resolve.json`: SHA-256 `5d023b2501969f06ba039ae5f59ac42ddf97e64feeb69e5789fc26403c92f184`.

The result is a **provider/toolchain readiness proof** on a small PE, not proof of valid Rift jump targets, native dispatch handler registration, route output, collision semantics, or the player controller. The imported and relocated fragment lacks distant code and data, so decompilation may include invalid edges or missing inputs.

## Next gated step

Keep the new small-PE preparation code as a reusable offline tool with validated `--run-id` isolation. Treat additional small-PE experiments as **bounded hypotheses** with exact source hashes and an isolated fresh evidence namespace. If an interaction depends on imports, RTTI, the original image base, or outside fragment targets, use the complete original executable offline scanners and/or a separately justified supported persisted Ghidra project; do **not** present the synthetic PE analysis as a real application-level pathfinding call.

M1 Ghidra small-PE readiness is resolved; **full-binary analysis performance remains unresolved**. No installed REA/Ghidra files were modified, no process/debugger attached, no live controls issued, and no remote publishing occurred.
