# SC-604 — exact-build native castbar field-key binding (November 6, 2026, 14:29 EST)

**Owner:** sole RRE manager; source-only bounded continuation. **Result:** independently qualified two native consumers' shared key-string/field-helper associations. **Gate:** SC-604 remains **INTERIM**; this is not a live spellcast, full Lua API reconstruction or a proven runtime field-semantic map.

## Source and independent checks

- Original physical-PC on-disk `C:\Program Files (x86)\Glyph\Games\RIFT\Live\rift_x64.exe`, **60,493,640 bytes**, SHA-256 **`1935a05c9db6d468e34e0055014a4a99c1b5afceb1695884e24600f5c20a4be8`**, freshly verified twice. No process or memory was opened.
- First read: existing RRE `.venv` Capstone/pefile, starting only at qualified unwind-owner boundaries, decoded instructions in the two previously sourced castbar paths. Workbridge `rre_20261106_1423_sc604_consumer_semantics_ro` exited **0**, untruncated.
- Independent check: **Python 3.14 standard library only** (manual PE section table, raw x64 relative-displacement arithmetic; **no Capstone or RR2 helper**). For each field in *both* paths, it verified the raw `lea r8,[rip+disp32]` instruction, NUL-terminated exact ASCII key at the resolved RVA, raw direct `call rel32` to **`0x1689A60`**, and shared key target between paths. **14/14 passed** via Workbridge `rre_20261106_1423_sc604_rip_byte_assert_ro`, exit **0**, untruncated.
- Helper crosscheck: source-only Capstone decode of exact function owner `[0x1689A60,0x1689B09)` shows `mov r10,r8`, a NUL-byte length loop over that key, calls `0x163DE20` and `0x167D4D0`, then a stack adjustment; `0x16893D0` writes an XMM-derived double to the VM-associated stack, while `0x1689190` writes a boolean-like record. Workbridge `rre_20261106_1423_sc604_helper_wrapper_ro` exited **0**, untruncated. These support a **field-setting helper candidate**, not independently proven standard Lua library function identities.

## Seven independently duplicated key associations

Both native callsites to producer `0x91DED0` are as qualified previously at `0x9B8299` (caller A, output `rsp+0x30`) and `0x9B8644` (caller B, output `rsp+0x60`). The following are **exact field-key pointer and common setter-call byte observations**:

| Key | ASCII string RVA | A: `lea` → setter `call` RVAs | B: `lea` → setter `call` RVAs |
| --- | --- | --- | --- |
| `begin` | `0x26D6BC8` | `0x9B82CF` → `0x9B82DE` | `0x9B8675` → `0x9B8684` |
| `duration` | `0x26D6BB0` | `0x9B82F4` → `0x9B8303` | `0x9B869D` → `0x9B86AC` |
| `remaining` | `0x26D6A98` | `0x9B8320` → `0x9B832F` | `0x9B86C9` → `0x9B86D8` |
| `expired` | `0x26D6BC0` | `0x9B835D` → `0x9B836C` | `0x9B86FD` → `0x9B870C` |
| `uninterruptible` | `0x26D8D50` | `0x9B8385` → `0x9B8394` | `0x9B8728` → `0x9B8737` |
| `channeled` | `0x26D6440` | `0x9B83AD` → `0x9B83BC` | `0x9B8753` → `0x9B8762` |
| `abilityNew` | `0x26A5E68` | `0x9B83E9` → `0x9B83F8` | `0x9B8795` → `0x9B87A4` |

All fourteen setter-call instructions encode the **same** target `0x1689A60`. The string keys above are real static constants; **whether a runtime branch executes each setter is a separate question**.

## Producer-buffer relative value path (instruction observations)

- `begin`: `movss` loads output **`+0x28`** at A `0x9B82BE` / B `0x9B8661`, then float-to-double conversion and a value-stack helper before the named-key helper.
- `duration`: corresponding **`+0x30`** reads at A `0x9B82E3` / B `0x9B8689`.
- `remaining`: corresponding **`+0x2C`** reads at A `0x9B8308` / B `0x9B86B1` pass through `maxss` with XMM6 (explicitly zeroed in A) or XMM7 (its reaching definition is not independently qualified in B) before the value/helper call. The same `+0x2C` is re-read at A `0x9B8334` / B `0x9B86DD`, with conditional negative-only path toward `expired`. This is a **static value transformation**, not a proven timer unit or expiry event.
- `uninterruptible`: branches compare **`+0x38`** at A `0x9B8371` / B `0x9B8711`; the zero branch uses `edx=1` and boolean-like helper `0x1689190` before the keyed helper. **Meaning/inversion of the original byte remains unproved.**
- `channeled`: a newly observed analogous comparison of **`+0x39`** at A `0x9B8399` / B `0x9B873C`, followed by a conditional boolean-like helper and the keyed helper.
- `abilityNew`: the paths load a dword from output-relative **`+0x40`** at A `0x9B83C1` / B `0x9B8767`, then take a helper-conditioned branch toward `abilityNew`. The producer's origin/value of this field and any modern ability-ID semantics are **not qualified**.

These are **instruction-, address- and control-dependence leads**, not full basic-block/reaching-definition proofs. The producer's write sites `+0x28/+0x2C/+0x30/+0x38` were previously qualified in [the producer note](REA-RIFT-SPELLCASTING-SC604-CALLER-OUTPUT-DISASM-2026-11-06.md); this run independently links their *consumer* sites to named static setter-call patterns. The previous [consumer baseline](REA-RIFT-SPELLCASTING-SC604-CASTBAR-CONSUMER-2026-11-06.md) established field reads but **not** these literal field-key associations.

## Evidence limits, ownership and stop rule

There is no live source-selected player/ability proof, no full control-flow or interprocedural reaching-definition proof, no tested helper return/side-effect contract, no successful casting or server response, and no qualification of a GCD, queue enum or current Legendary selection. Specifically **do not promote** `begin`, `duration`, `remaining`, `expired`, `channeled`, `uninterruptible` or `abilityNew` to reliable external telemetry based only on these static instructions; branch absence/transformations remain material.

**SC-604 stays interim. SC-103 and SC-306 stay blocked. RC-30 strict same-trial archive and RC-32 physical recovery remain unverified.** RR2's research owner retains all RR2 writes/native-reader decisions, REA-Lab1 owns its queued review files, and NAV-002 remains with RR2. No independent AI model session was launched: the existing RRE FreeBuff adapter accepts fixed `sc103`/`rc30` review questions already exercised on unchanged evidence; **Workbridge command jobs are not reasoning agents**. No game input, reload, process control, quarantined desktop lease override, installed addon/SavedVariables or cross-repository mutation.

**Next discriminating step:** obtain real basic-block reaching-definition evidence linking the producer's branched writes through these consumer value-stack helpers, including the `+0x39` and `+0x40` sources and the negative `expired` path; avoid rescanning literals, creating live readers or duplicating external RR2 development.
