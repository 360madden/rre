# SC-604 — independent cast helper leaf and guarded `abilityNew` source (November 6, 2026, ~21:21 EST)

**Owner:** sole RRE manager. **Gate:** SC-604 remains INTERIM. This is a bounded, read-only exact-build native source qualification, not an observed cast, confirmed ability ID, reliable telemetry field, or authorization to invoke native functions.

## Source provenance and independent methods

- The physical on-disk `C:\Program Files (x86)\Glyph\Games\RIFT\Live\rift_x64.exe` is **60,493,640 bytes**, freshly SHA-256 verified as `1935a05c9db6d468e34e0055014a4a99c1b5afceb1695884e24600f5c20a4be8`. The executable was only read as a file; no process or live memory was opened.
- RRE prior output provenance: `docs/REA-RIFT-SPELLCASTING-SC604-ABILITYNEW-COLD-PRODUCER-2026-11-06.md`, SHA-256 `f72c87f96baa1ac2d7ecc78b0b8d214d972094044badf2add454d7e61b9604bc`.
- Read-only reuse-first RR2 crosscheck: `C:\work\riftreader2\docs\reference\native-current-client-code-map.md` SHA-256 `a9c85eb80e584cf3574fe2e91f8679e1b5c56b2e2e8539dac03489101ab18656`, and `native-current-cast-candidate.md` SHA-256 `ab047772294c07179de67e85d8e4b94d973cdfd3f601ef1bd6c1149ff4755f5e`. These existing notes already associate `0x58B30` with child `+8` access via `0x5A75C0`; this step *independently* confirms the leaf instructions and ties the producer call's guarded argument to them.
- Exact-build Capstone/pefile disassembly from qualified entry boundaries (not from a misaligned middle address) in Workbridge jobs `rre_20261106_2119_sc604_helper58b30_ro` and `rre_20261106_2121_sc604_helper58b30_callpath_ro`. Both settled **exit 0**, untruncated.
- A separate **Python 3.14 standard-library-only PE section mapper**, with neither Capstone, pefile nor RR2 code, verified **13/13** direct opcode anchors and independently computed the `call rel32` destination `0x91E083 → 0x58B30`. Workbridge `rre_20261106_2122_sc604_stdlib_leaf_assert_ro` **exit 0**, untruncated.

## Verified narrow instruction chain

| RVA | Instruction | Verified implication |
| --- | --- | --- |
| `0x91E04C` | `mov rcx,[rbp-0x39]` | Reloads saved pointer (also set `0x91E006`). |
| `0x91E069` | `test rcx,rcx`; `0x91E06C` conditional exit | A zero saved pointer bypasses this helper call. |
| `0x91E072` | `mov rax,[rcx+0x10]` | Reads an associated pointer; null validity is **not** separately established by this local sequence. |
| `0x91E076` | `cmp byte ptr [rax+0xC8],r13b` | Branch condition checks a byte against R13B, previously zeroed in the producer. |
| `0x91E07D` | Conditional exit on nonzero comparison | Helper is on only one branch of this predicate. |
| **`0x91E083`** | **`call 0x58B30`** | Direct target verified by raw relative-call displacement. |
| **`0x58B30`** | **`8B 41 08: mov eax,dword ptr [rcx+8]`; `C3: ret`** | The callee itself is a four-byte **read-only leaf** (no explicit write/call), reading a DWORD at its **RCX argument +8**. |
| `0x91E090` | `mov [rbp-0x51],eax` | Saves the helper's result before further native helper calls. |
| `0x91E49F` → `0x91E4BA` | `mov eax,[rbp-0x51]` → `mov [rdi+0x40],eax` | Existing cold-region proof carries that optional value to output `+0x40`. |

**Value-chain conclusion (static only):** On the guarded branch, the call at `0x91E083` reads a DWORD from **saved RCX +8**, and this value may reach the output field `+0x40` through the previously qualified stack local. The other reaching definition remains the initial zero. The *helper* is not a complex computed-ID routine: it is exactly `mov eax,[rcx+8]; ret`. This is a material narrowing of the formerly unknown callee semantics, not proof that the DWORD is an ability identity or active spell.

## Separate accessor and consumer evidence

- `0x5A75C0`: reads `[rcx+0x280]`; on nonzero, **tail-jumps** to the same leaf `0x58B30`, otherwise returns zero. `0x5A7570` is the analogous `+0x290` accessor. These match the existing RR2 static map, but **do not independently show that the RCX at the producer's direct call is one of those same child pointers**; its true owner/type is not proven by this bounded step.
- The castbar consumer B subsequently reads output `+0x40` at `0x9B8767` and calls `0x49FA20`; a small exact-entry decode of `0x49FA20` shows further calls and reference-count operations. Its boolean outcome and `0x1357250` identity conversion remain **unqualified**. Do not invoke these helpers externally.

## Gates, limits and stop rule

This analysis cannot establish pointer lifetime, exception/alias paths, runtime feasibility of the guard, value units/identity, actual casting, whether the `abilityNew` Lua setter executes, or the semantics of `0x49FA20`. Matching source bytes and control-flow leads are **not** game observation.

- **SC-604** interim; **SC-103** current Legendary/Protector's Fury ID blocked; **SC-306** queue enum blocked.
- **RC-30** same-trial Pin→Undo→Reload archival evidence incomplete despite earlier operator-functional acceptance; **RC-32** physical retry/startup unverified.
- The newest RR2 source already covers passive candidate component access. No RR2/REA write, generic scanner, new reader or duplicate model task was launched. Fixed RRE FreeBuff modes remain previously exercised; Workbridge command jobs are not independent model agents.
- The next discriminating step, if newly justified and nonoverlapping with RR2, is to characterize the **conditional consumer `0x49FA20` → `0x1357250`** without treating its result as a current ability ID. Do not repeat the `0x58B30` leaf scan.

No RIFT input, reload, process manipulation, installed-addon/SavedVariables edit, quarantine override, cross-project mutation or native invocation occurred.
