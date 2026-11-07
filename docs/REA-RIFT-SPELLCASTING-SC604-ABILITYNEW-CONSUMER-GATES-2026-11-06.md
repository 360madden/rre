# SC-604 — conditional castbar `abilityNew` consumer gates (November 6, 2026, ~21:56 EST)

**Owner:** sole RRE manager. **Status:** new exact-build static branch evidence; SC-604 remains an **accepted interim mechanism**, not validated current casting or ability identity. **Scope:** read-only physical-PC original executable, no game/process interaction.

## Source and independent verification

- On-disk physical RIFT `C:\Program Files (x86)\Glyph\Games\RIFT\Live\rift_x64.exe`: **60,493,640 bytes**, SHA-256 **`1935a05c9db6d468e34e0055014a4a99c1b5afceb1695884e24600f5c20a4be8`**, rehashed in both independent verification methods.
- Existing RRE preceding links: [field-key associations](REA-RIFT-SPELLCASTING-SC604-LUA-FIELD-KEYS-2026-11-06.md), [cold producer +0x40](REA-RIFT-SPELLCASTING-SC604-ABILITYNEW-COLD-PRODUCER-2026-11-06.md), and [guarded producer leaf](REA-RIFT-SPELLCASTING-SC604-HELPER58B30-CALLPATH-2026-11-06.md) (last two document the **candidate** 32-bit output source; neither proves ability identity). The guarded-leaf note SHA-256 at read: `3f7049acccde4aa24e2995c4e84c56c4bc5f6499bfa59a54657998d83bc67110`.
- Workbridge `rre_20261106_2155_sc604_49fa20_disasm_ro` and `rre_20261106_2157_sc604_branch_predicate_ro`: **2/2 exit 0**, no truncation; RRE's existing Capstone/pefile venv decoded instruction-aligned consumer/callee entries and `.pdata` boundaries. `0x49FA20` has `.pdata [0x49FA20,0x49FAA1)` and 38 decoded instructions. `0x49FAB0` starts a distinct unwind region `[0x49FAB0,0x49FAD7)`; its continuation is larger and not semantically traced here.
- **Independent method:** Workbridge `rre_20261106_2158_sc604_independent_branch_bytes_ro`, **exit 0**, no truncation: Python 3.14 standard-library **only** (no Capstone/pefile/RR2) mapped PE sections to raw bytes, rehashed the executable, asserted **17/17 exact opcodes**, **5/5 rel32 direct-call targets**, and **3/3 short conditional branch targets**. No process or live memory was opened.

## New bounded chain — exact RVAs in this physical executable

| RVA | Direct static fact | Limited consequence |
| --- | --- | --- |
| `0x9B8767` → `0x9B876E` | Consumer B loads `ecx` from `[rsp+0xA0]` (previously matched output buffer `rsp+0x60` plus `0x40`) and calls **`0x49FA20`**. | Candidate producer `+0x40` reaches a **conditional lookup/test**, not unconditionally a Lua ID. |
| `0x9B8773` / `0x9B8775` | `test al,al; je 0x9B87A9`. | False result **skips** the next `0x1357250` conversion and associated key-assignment sequence. |
| `0x49FA5F` / `0x49FA65` | Compares a stack-held pointer `[rsp+0x40]` to zero; zero branches to `0x49FA8C`. | One false exit occurs if this intermediate result pointer is null. The pointer's type is unknown. |
| `0x49FA6E` / `0x49FA73` / `0x49FA75` | Calls `0x49FAB0`, tests `al` and branches to `0x49FA8C` when zero. | A **second** predicate must be nonzero for the positive path. `0x49FAB0` is not yet semantically characterized. |
| `0x49FA7C` / `0x49FA83` vs `0x49FA8C` / `0x49FA98` | Positive path sets `bl=1`; negative path zeroes `bl`; both return `movzx eax,bl` after cleanup. | The wrapper's observed normal-return code emits **1 or 0**, subject to unmodeled exceptions/side effects. |
| `0x9B877E` → `0x9B8790` → `0x9B87A4` | On the positive gate only, calls `0x1357250` with the same stack-derived DWORD; moves its return to `r8`, calls `0xA17E00`, and then calls named-key setter candidate `0x1689A60`. | A further transformation precedes the candidate `abilityNew` setter; **no stable ID or Lua runtime success** is established. |

**Exact independent control edges:** `call 0x9B876E→0x49FA20`, `call 0x9B877E→0x1357250`, `call 0x49FA6E→0x49FAB0`, `call 0x9B8790→0xA17E00`, and `call 0x9B87A4→0x1689A60` all matched rel32 bytes. Short branches `0x9B8775→0x9B87A9`, `0x49FA65→0x49FA8C`, `0x49FA75→0x49FA8C` matched encoded offsets.

## Proof ceiling and stop rule

The code **statically gates** the candidate `abilityNew` field in consumer B; it does **not** show `0x49FAB0`'s predicate meaning, whether any gate succeeds in the running game, full `0x1357250` behavior, a modern Legendary/Protector's Fury ID, server authorization, valid casting, or queue enum mapping. `0x1357250` itself has split unwind regions, so its first prologue must **not** be mistaken for its entire routine. This finding applies only to the SHA-qualified physical executable, not unqualified VMware builds.

**Unchanged gates:** SC-103 current Legendary ID **blocked**; SC-306 numeric queue mode **blocked**; SC-604 **interim**; RC-30 strict same-trial operator evidence **incomplete** despite operator acceptance and historical v0.4.10 save; RC-32 physical v0.4.11 error/retry evidence **unverified**. NAV-002 remains RR2-owned.

**Next meaningful discriminator:** only if nonoverlapping with a live RR2/REA owner and supported by new source evidence, characterize the conditional check at `0x49FAB0` or the `0x1357250` return type using its complete split function regions, with an independent negative control. Do **not** repeat the already resolved `0x58B30` leaf. No game input, reload, process control, installed addon/SavedVariables edit, desktop quarantine override, external repository write, or native invocation was performed.
