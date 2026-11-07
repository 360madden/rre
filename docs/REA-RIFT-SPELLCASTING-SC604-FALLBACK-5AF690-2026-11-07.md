# SC-604 — fallback predicate helper `0x5AF690`: bounded static qualification (November 7, 2026)

**Owner:** single RRE manager. **Scope:** offline inspection of the exact physical-PC RIFT executable only. **Status:** new qualified static step; SC-604 remains **interim**.

## Source, method, and receipts

- Original: `C:\Program Files (x86)\Glyph\Games\RIFT\Live\rift_x64.exe`, **60,493,640 bytes**, SHA-256 **`1935a05c9db6d468e34e0055014a4a99c1b5afceb1695884e24600f5c20a4be8`**. SHA and length freshly verified independently during all successful decoding/byte-verification jobs. All code addresses below are exact-build **RVAs**, not process pointers or guest-build addresses.
- This is the previously unknown nonzero predicate callee of `0x49FAB0`'s fallback branch documented in [the prior predicate analysis](REA-RIFT-SPELLCASTING-SC604-PREDICATE-49FAB0-2026-11-06.md). No previous `0x58B30` or six-reference probe was repeated.
- Workbridge read-only job `rre_20261107_0030_sc604_5af690_venv_ro`: exit **0**, original PE + Capstone from existing RRE `.venv`, no output truncation; `.pdata` owner **`[0x5AF690,0x5AF6EC)`**.
- Workbridge read-only job `rre_20261107_0032_sc604_58c790_helper_ro`: exit **0**, bounded callee disassembly; `.pdata` owner **`[0x58C790,0x58C86F)`**.
- Independent, **Python 3.14 standard-library only** PE/byte checker `rre_20261107_0036_sc604_5af690_stdlib_verifier`: exit **0**, untruncated. Checks **27 exact instruction-byte anchors, 10 encoded short-branch destinations, one encoded direct-call target, two `.pdata` ranges, and one deliberately misaligned-byte negative control**. This does not independently decode all instructions or prove full dynamic control flow.
- Preliminary `rre_20261107_0028_sc604_5af690_disasm_ro` failed because standalone `C:\Python314\python.exe` lacks Capstone. Recovery used the **already installed** `C:\work\rre\.venv\Scripts\python.exe`; no dependencies were installed.

## Direct findings

The bounded routine at RVA **`0x5AF690`** uses `RBX = RCX + 0x1C0`, forwards `RBX` and two caller-stack output addresses to **`0x58C790`** at `0x5AF6AD`, then computes an end-like pointer from the container fields: if `[RBX+0x10]` is nonzero, `[RBX] + ([RBX+0x10]-1) * [RBX+0x08]`; otherwise `0`. These are arithmetic/control-flow facts, **not** proven game-object types.

After the call, the normal return path compares three parts of the returned local record:

| Instruction RVA | Direct comparison | On mismatch |
| --- | --- | --- |
| `0x5AF6C6` | `qword [rsp+0x30] == 0` | return `AL=1` |
| `0x5AF6CE` | `qword [rsp+0x28] == computed end-like pointer` | return `AL=1` |
| `0x5AF6D5` | `qword [rsp+0x20] == RBX` | return `AL=1` |
| `0x5AF6DC` / `0x5AF6E4` | all three equalities hold / at least one fails | `AL=0` / `AL=1` |

The invoked routine **`0x58C790`** reads an input DWORD, traverses an indexed/linked candidate structure, compares an element DWORD at `[candidate+8]` to the input, and writes three values to the output record: `[RSI]` (container pointer), `[RSI+8]` (candidate or end-like pointer), and `[RSI+0x10]` (candidate node or zero). Notable exact instructions include `0x58C7F9 test al,1`, `0x58C800 cmp dword [r8+8],ecx`, `0x58C814 cmp dword [rax+8],ecx` and three result stores at `0x58C850`, `0x58C857`, and `0x58C85F`. Hash/index mathematics and an indirect call at `0x58C7C1` are present, but its external target and side effects were not established here.

**Narrow consequence:** the fallback path is no longer an opaque Boolean. On ordinary return, it calls a bounded key-comparison/lookup-style helper and distinguishes a three-part *end/no-candidate-like* result from any nonmatching result. This is consistent with a lookup/membership discriminator, but identifying the underlying container, key taxonomy, or meaning of a positive result requires additional evidence. In particular, a return of `1` does **not** itself prove a spell is known, learned, usable, Legendary, queued, or successfully cast.

## Boundaries and next gate

- This study did **not** establish external helper `0x58C790`'s indirect callee, full exceptional paths, object invariants, thread-safety, process/runtime values, ability ID semantics, global reference identities, queue rules or GCD.
- **SC-604 remains interim. SC-103 and SC-306 remain blocked.** Strict RC-30 same-trial Pin→Undo→Reload archive and version-matched before/after evidence remain incomplete; RC-32 physical Retry guard unverified. NAV-002 belongs to RR2.
- Next discriminating task **only when nonoverlapping and evidence-bearing**: qualify the input key/value path feeding `0x58C790` from `0x49FAB0`, or identify the six reference origins by a different exact-build source. Do not start a new large import, relabel the lookup as an ability-ID API, or repeat this routine without new evidence.
- No game input, RIFT reload, process manipulation, new dependency, installed addon, SavedVariables write, desktop-quarantine override, cross-project write, or push occurred. Workbridge jobs are command executions, **not** reasoning agents.
