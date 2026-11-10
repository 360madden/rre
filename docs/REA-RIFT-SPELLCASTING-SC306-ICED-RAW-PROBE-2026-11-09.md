# SC-306 — LEGION bounded raw-x64 REA refusal and offline iced-x86 fallback

**November 9, 2026, ~22:05 EST.** Scope: RRE-owned static analysis of **LEGION's installed physical RIFT executable only**. No VMware operation, RIFT process/UI input, reload, injection, debugger, memory modification, or full-PE Ghidra import occurred.

## Exact physical source identity

| Item | Verified value |
| --- | --- |
| Windows hostname | `LEGION` |
| Original physical executable | `C:\Program Files (x86)\Glyph\Games\RIFT\Live\rift_x64.exe` |
| Original PE size / SHA-256 | `60,493,640` / `1935a05c9db6d468e34e0055014a4a99c1b5afceb1695884e24600f5c20a4be8` |
| PE image base | `0x140000000` |
| Bounded routine | RVA `0x129CAC4`, VA `0x14129CAC4`, length `452` bytes |
| Routine SHA-256 | `1d3b762a399fc53592032c11238eb151d41684b37fde0951713db760382f56e8` |
| Local installed toolchain | REA `6.8.0`, Ghidra `12.1.4`, JDK `21`, Python RRE `.venv` with pefile/iced-x86 |

The PE `.pdata` corroborated the routine's 452-byte extent in a preceding exact-build check. Raw body identity alone does not prove the Ability Queue enum mapping.

## One genuine REA provider attempt — definite blocker

- A hash-gated 452-byte raw input and fixed VA were prepared under `artifacts/sc306-legion-rea-raw-20261109-01/`. The normal session preflight passed without starting analysis, admitted the verified 452-byte input, and kept `allowFullPeImport: false`.
- **One** bounded real `tools/rea-session.mjs` session connected to REA and requested `open_binary`, then exited with failure in **27.05 seconds**, job `rre-legion-sc306-raw-real-rea-ghidra-session-20261109-01`, exit **1**. No request for procedure resolution ran.
- The exact `open-binary.json` result was `capability_unavailable / unsupported_provider`, `retryable: false`, `target_format_unsupported`. REA's Windows Ghidra P0 adapter states that it accepts native PE images and explicitly selected raw **6502** targets, but **not raw x86-64**. Hopper is unsupported on win32; IDA and Kuna were unconfigured and also did not admit this raw target.
- The runner failed closed without an automatic retry. `status.json` independently records `gameInputSent: false`, `gameProcessAttached: false`, `targetExecuted: false`, `completed: []`; an additional read-only `Win32_Process` check found **no lingering Ghidra/analyzeHeadless Java child**.
- The rejected provider format is a **tool capability restriction**, not evidence that source bytes were invalid or that Ghidra generally cannot analyze native x64 PE files. Do not rerun the same raw-x64 route until the provider explicitly supports it.

## Reliable offline replacement — success

The RRE-owned `tools/prepare-sc306-legion-raw.py` now **extracts only** the exact SHA-gated physical function and uses already installed **iced-x86** to generate a complete disassembly. It no longer creates an unsupported REA session or invokes Ghidra. Protections: hostname gate, full PE digest gate, PE Machine/ImageBase check, slice digest, strict 452-byte decoder coverage, unique output directory (`exist_ok=False`), dry-run mode and source-preserving output.

Successful jobs:

- `rre-legion-sc306-iced-offline-control-flow-20261109-01` — exit 0, 125 decoded instructions/452 bytes.
- `rre-legion-sc306-iced-prep-dry-run-20261109-01` — exit 0, verified before writing.
- `rre-legion-sc306-iced-offline-evidence-create-20261109-01` — exit 0, created **new** ignored local artifact namespace `artifacts/sc306-legion-offline-20261109-01/` containing the 452-byte binary, `sc306-label-register-delegate.asm` and `source-manifest.json`.
- Saved listing SHA-256: `d85308f10e28604864a64649f0721b6381f77e061be5283e282cbffd9c1ba2b2`.

To recreate with a fresh unique ID on **LEGION** after reconfirming the original source hash:

```powershell
cd C:\work\rre
.\.venv\Scripts\python.exe -B tools\prepare-sc306-legion-raw.py --run-id 20261109-fresh --dry-run
.\.venv\Scripts\python.exe -B tools\prepare-sc306-legion-raw.py --run-id 20261109-fresh
```

These commands operate on the disk image and repository artifact folder, never the running game or any VM. The `artifacts/` evidence is intentionally not in Git; the deterministic source helper and this report belong in Git.

## Narrow structural observations, not inferred game semantics

In the isolated instruction stream, the bounded routine contains direct calls near `0x14003C310`, `0x14129D004`, `0x14129CFC0`, and `0x14003C320`, plus indirect calls and conditional branches. That is consistent with the earlier generic UTF-16/hash-cache function finding; it does **not** establish a numeric queue-choice table, the ABI, a reachable call path in current gameplay, or the labels for values `0` or `2`.

**SC-306 remains blocked.** The only historical observed pair is `1 → Short`; do not promote it to fresh physical live acceptance. Pursue independent UI-choice-table/localization evidence or a separately approved same-epoch physical UI/native contrast. Full-PE REA/Ghidra opening is still **not authorized** by this successful offline fallback.
