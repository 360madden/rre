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

## November 10, 2026, 16:13 EST — independent Soul Tree role-UI caller of the same helper

**New cross-context discriminator (offline only):** In the preserved exact-build Lab-2 executable copy `artifacts/lab2-live-20261107-0922/guest-rift_x64.exe` (60,493,640 bytes; independently rehashed SHA-256 `1935a05c9db6d468e34e0055014a4a99c1b5afceb1695884e24600f5c20a4be8`), the previously verified `soulTree.HandleRolesButtonClicked` callback entry at RVA `0xE94CC0` contains a **second direct caller** of the same helper `0x5AF690`. At `0xE94E95–0xE94E9F`, native code loads `R14D` from `[RAX+0x18]`, sets `RCX=RSI`, sets `EDX=R14D`, and calls `0x5AF690`. In the already documented SC-604 castbar predicate, the original direct call is at `0x49FC38 → 0x5AF690`. These calls occur in different, separately named source contexts; they do **not** demonstrate a runtime connection between role selection and casting.

**Additional owner-context evidence:** RIP-relative source string references at `0xE94D0B` and `0xE94D5D` in that callback resolve to `mc_RoleSelector` (RVA `0x27055B0`) and `m_RoleLC` (RVA `0x27055A0`). These are exact static literals and consistent with role-selector UI code, not proof of the helper's input key taxonomy, object type, role ID, or an actual UI action.

**Independent checks:** Workbridge jobs `rre_20261110_1612_rolesbutton_qualify_ro_v1` (existing Capstone/pefile disassembly) and `rre_20261110_1619_roles_predicate_crosspath_stdlib_ro_v1` (Python standard-library-only PE section mapper, exact rel32 calls, both RIP-relative string addresses, in-memory mutated displacement negative check) both exited **0** without output truncation. The Capstone inspection was a bounded 0x210-byte window, not a complete callback CFG. This is a stronger reason **not to label `0x5AF690` as a cast-specific or spell-known predicate** based solely on its SC-604 caller. No new Legendary identity, Ability Queue enum mapping, successful cast, runtime table ownership, or server behavior is established. Park further generic expansion absent a separately justified owner/data discriminator. SC-604 remains **interim**. No game/process/VM/input/reload/lease operation, addon installation, SavedVariables edit, unrelated repository write, dependency installation, or remote push occurred.

## November 10, 2026, ~17:13 EST — role-click key provenance and gated downstream use

A narrow new source-qualified continuation of the **already identified role-UI caller** resolves where its comparison key is read and how it is reused after the common helper. The source is the preserved Lab-2 client PE `artifacts/lab2-live-20261107-0922/guest-rift_x64.exe`, **60,493,640 bytes**, freshly matched SHA-256 `1935a05c9db6d468e34e0055014a4a99c1b5afceb1695884e24600f5c20a4be8`. All addresses below are **exact-build RVAs**; no live memory or UI state was sampled.

- In `soulTree.HandleRolesButtonClicked`, `0xE94E7F` adds `0x20` to the candidate pointer, and `0xE94E83` calls `0x20D1650` with an output at `[RBP-0x58]`. The later `0xE94E88` reloads the resulting pointer, `0xE94E8C/8F` guard null, and `0xE94E95` reads a **DWORD at `[RAX+0x18]` into `R14D`**. The identity of that record and the call's side effects are unknown.
- `0xE94E99–0xE94E9F` passes `RCX=RSI` and `EDX=R14D` into the previously qualified shared lookup `0x5AF690`. The result is tested at `0xE94EA4`; a zero result branches away at `0xE94EA6`. On the decoded nonzero continuation, **the same `R14D` key** is passed as `EDX` into `0x797D60` at `0xE94ECE` with `R9B=1` and a stack-address `R8`. The downstream call has **not** been shown to commit a role, cast an ability or alter game state.
- Separately, the castbar predicate's already documented `0x49FAE2` retains its first input DWORD (`ECX`) in `R15D`, then forwards that value as `EDX` to `0x5AF690` at `0x49FC38`. Thus the **same membership-style helper** accepts a *role-UI-derived record key* in one static path and a *castbar predicate input* in the other. **Key equality, object identity, shared gameplay semantics and actual path execution are not established.** This is a provenance distinction, not a claim that the role key equals an ability ID.

Verification: bounded original-code Capstone/pefile jobs `rre_20261110_1709_sc604_key_provenance_bounded_ro_v1` and `rre_20261110_1715_sc604_key_entry_window_ro_v1` both exited **0**. An independent Python 3.14 **standard-library-only** PE-section/byte verifier `rre_20261110_1720_sc604_rolekey_stdlib_guard_ro_v2` exited **0** with 19 original-byte anchors, four rel32 direct-call targets, two branch-target checks and one mutated-byte negative check. Its first draft `..._v1` failed due solely to the script's malformed Python PE-magic literal; the corrected verifier passed without changing any project files. These methods do not prove dynamic branch reachability or independent game semantics.

**Decision:** One additional bounded native **role key → membership result → downstream consumer** relationship is established; SC-604 remains **interim**. The only prospective next native discriminator here is a separately justified *record type / `0x797D60` consumer contract*; do not expand the generic `0x5AF690` helper, claim successful casting, invent modern Protector's Fury IDs or reuse another owner's live control window. No RIFT input/reload, process/VM/desktop-lease action, addon/SavedVariables change or cross-repository write was performed.
