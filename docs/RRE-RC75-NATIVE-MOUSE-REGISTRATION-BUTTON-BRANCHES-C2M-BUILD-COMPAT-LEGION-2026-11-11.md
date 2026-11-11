# RRE RC-75 — native `Inspect_Mouse` registration, mouse-button message source, and current-build C2M compatibility (LEGION)

**Date:** 2026-11-11 · **Host:** independently verified **LEGION** · **Mode:** original installed PE, static/read-only, no running process or gameplay · **Verdict:** two newly closed source edges; historical C2M RVAs rejected for this executable. Camera/actor turn and live Lua invocation **not** proved.

## Source pin and reproduction scope

- Original file: `C:\Program Files (x86)\Glyph\Games\RIFT\Live\rift_x64.exe`.
- Length **60,493,640 bytes**, SHA-256 `1935a05c9db6d468e34e0055014a4a99c1b5afceb1695884e24600f5c20a4be8`, preferred base `0x140000000`. **All addresses below are RVAs**; no ASLR process VA claims.
- Host identity terminal job `rre-20261111-rc74-identity-001` returned LEGION, exit 0. Independent manager validation and three separated read-only agent source investigations; report assembled by the coordinator. No VM, AMD-DESKTOP, process memory attach, mouse/keyboard input, reload, installs, remote pushes or other repository edits.

## A. `Inspect_Mouse` has a direct native registration-shaped name/function edge — **verified static**

A bounded, complete linear decode of a **prefix** of original PE function `[0x9B18F7,0x9B41D0)` exposes a concrete `Inspect_Mouse` registration sequence. Source capture `[0x9B18F7,0x9B34D6)`, length 7,135 bytes / 1,703 aligned Capstone instructions, SHA `4814af543e10c690ab937bf61a1e067021f2d7df3c29c08b1620664269e7ed3b`; decisive `[0x9B3495,0x9B34D6)` length 65 SHA `fce330f92e99f994154afdfe9dd338aa664d05fe69ddd3021940cfca58ce7691`.

| RVA | Direct original-code observation |
|---|---|
| `0x9B3498`, `0x9B34B3` | References exact string literal `Inspect_Mouse` at RVA `0x26D6070` |
| `0x9B34BE` | `call 0x493790` builds a native name object on stack |
| `0x9B34C3` | `lea r8,[rip-0x72FA]` resolves **exact native builder `0x9AC1D0`** |
| `0x9B34CA`, `0x9B34CD`, `0x9B34D1` | Registry object as `RCX=RSI`, name object as `RDX=[RBP-0x38]`, then `call 0xA0CD80` |
| `[0xA0CD80,0xA0CE64)` | Wrapper passes the function pointer via native `0x16891C0` and the name via `0x1689A60`; wrapper source SHA `aa3e77220ff560d8b4b69a908e9294a6ad793be29db1467ac5adea2bf48dbcde` |

The `0x9AC1D0` result routine itself loads pointer metadata: `0x9AC200` reads .data RVA `0x2F63F48` → exact `Inspect.Mouse` string at RVA `0x26D7D98`; `0x9AC232` reads .data RVA `0x2F63F50` → `results@mouse` at RVA `0x26D7DB8`. RC-74 proved that builder obtains native X/Y and five button flags. **New distinction:** no longer just a descriptor with an unproven registration edge: the code passes **the exact native function pointer alongside the `Inspect_Mouse` name**. This still does **not** prove a current live Lua call, result, execution frequency, or ABI semantics beyond the native source.

## B. Windows mouse-button message table → native records — **verified static**

The dispatcher at `0x7C0F4D` subtracts Win32 `0x201` from the message ID in EDX; `0x7C0F70` selects byte table RVA `0x7C1928`; `0x7C0F78` reads the target-DWORD table RVA `0x7C18FC` and jumps. The manager decoded and crosschecked **nine** exact message→target pairs and eight bounded native branch bodies. Tables are original executable bytes, not annotations: `[0x7C1928,0x7C19AA)` SHA `770367361163fd8f09255565dd28c6e7589c47eccc52e55c371759c29bab376f`, `[0x7C18FC,0x7C1928)` SHA `755b1181d47e5ac7ae9cdd78ff447238f5fb65bcdaf5e74e481bed5107bf74a7`.

| Win32 message | Message ID | Target RVA | Record type | Native button subcode |
|---|---|---|---|---|
| `WM_LBUTTONDOWN` | `0x201` | `0x7C0F84` | 1 | 1 |
| `WM_LBUTTONUP` | `0x202` | `0x7C105B` | 2 | 1 |
| `WM_RBUTTONDOWN` | `0x204` | `0x7C113A` | 1 | 2 |
| `WM_RBUTTONUP` | `0x205` | `0x7C1215` | 2 | 2 |
| `WM_MBUTTONDOWN` | `0x207` | `0x7C12BD` | 1 | 4 |
| `WM_MBUTTONUP` | `0x208` | `0x7C1398` | 2 | 4 |
| `WM_XBUTTONDOWN` | `0x20B` | `0x7C147B` | 1 | 8/16 conditional XBUTTON1/2 |
| `WM_XBUTTONUP` | `0x20C` | `0x7C1592` | 2 | 8/16 conditional XBUTTON1/2 |
| `WM_MOUSEWHEEL` | `0x20A` | `0x7C1642` | different wheel/coordinate path | n/a |

Each button-down branch places 1 into EDI and writes type1 at its native record slot; each up branch writes type2 explicitly; branch-specific subcodes 1/2/4 and 8/16 are bounded source observations. All reach the shared `0x7C17F2 call 0x7C0480` route **under their local conditions**. The `WM_MOUSEWHEEL` case is the *separate* `USER32!ScreenToClient` branch at `0x7C1642` and `0x7C16A6`; RC-74 had conservatively marked its selector unknown, **now resolved**.

Bounded button branch source-window SHA-256 in table order (excluding wheel):

1. `[0x7C0F84,0x7C105B)` `83098a33e2a981ec3f06822b1bb40c7b3974a8590733c6956b4377f538df45bd`
2. `[0x7C105B,0x7C113A)` `38f0efc1a0fcfc5199af15fa5068603ae1c86790c2c61a1d818f3ca177151027`
3. `[0x7C113A,0x7C1215)` `cad5df846a847de2e84b207cd7c2c75a72f64baa8f7c747befac4a6fc8e72b87`
4. `[0x7C1215,0x7C12BD)` `9dfa7853ecad46ebad7cce24c534f65473a66b5e4f7469c1f915a3d2376bc2b0`
5. `[0x7C12BD,0x7C1398)` `a9f6b8afb26309f8165952fb3bb7ddda2b6523e1ee925a37aa2475853c4d9713`
6. `[0x7C1398,0x7C147B)` `b2e5abe6a5f46460b5b713a22912b2b42305588f0398ab8a4748475a5e7bee05`
7. `[0x7C147B,0x7C1592)` `1795da87fadacfbce737d4e836d791ad08608706905991274315b3e0472fca4d`
8. `[0x7C1592,0x7C1642)` `95a85bf30fde312545e3dcfbfef3c5316e8893a4621e999e8de5a6968ee04b40`

This extends RC-72/73's native record listener mapping into actual Win32 producer cases. Do **not** equate mouse-button input with player movement/turn command or proof of live RIFT behavior.

## C. C2M pointer drift: old movement anchors **invalid in this installed build**

Older project C2M notes (`docs/agents/c2m.md`, `ROADMAP.md`) used a **different** PE SHA `7c356c9dde9e12fcbff3c08d953b0630b48b1510a0ffb36e4ec164606e7b17bd` and length **59,963,840**. It is not the LEGION installed build pinned above.

- Historical setter RVA `0x562BC0`: current code begins `lea rdx,[rdx*2+2]`, **not** the old 12-byte destination setter. Current `[0x562BC0,0x562C17)` SHA `5ba3cb6367634f38fa000d889a4748872887d62f69ed91cce432d6cbfd68a059`.
- Historical callback `0x6942A0`: current code is unrelated singleton/object allocation, **not** the historical mouse/callback routine. Current `[0x6942A0,0x69436C)` SHA `4ec2fa53ae5b1b9e902fa7615ac1d6f46521db62ca8815af194b889d0b116d4c`.
- A **candidate** nearby cleanup/clear routine `0x546830` reads `[this+0xB90]`, performs refcount cleanup, reads a flag at `[state+0x1A8]` (`0x5468C2`), executes `btr eax,0` (`0x5468C9`), and writes back (`0x5468CD`). Broad source `[0x546821,0x546921)` SHA `7eeedd77f0d97421aa48eae8a522d37d6b63adddb416dd1d24aed4e60f02826f`; function-based `[0x546830,0x5468E0)` SHA `9e2ef685c88e4543ac7bb5d2a7f39029df0007bd5dcc3d40f6c9c33a8c8d4f66`. **No validated identity** as a current-build click-to-move destination setter or active-player path. Do not wire this into runtime controls.

**Operational consequence:** source hash + structure must gate every old-RVA usage. Re-discover current-build C2M producer/setter/callers before suggesting a runtime test; avoid porting stale pointer chains by matching raw RVA.

## D. Exact verification receipts, boundaries, and next work

All listed jobs exited **0** without attaching to the game. Manager: `rre-rc75-mgr-inspect-mouse-registration-independent-qa-20261111-01` (full disassembly, exact literals and wrapper edge); `rre-rc75-mgr-native-mouse-builder-metadata-precision-20261111-01`; `rre-rc75-mgr-mouse-buttons-jumptable-independent-qa-20261111-01` (all 9 dispatch entries, table hashes); `rre-rc75-mgr-button-record-types-source-qa-20261111-01` (eight original branch windows, type writes); `rre-rc75-mgr-old-c2m-offsets-independent-qa-20261111-01` (historical/current mismatch and candidate).
Independent agents: `rre-rc75-mouse-buttons-jumptable-20261111-a`, `rre-rc75-mouse-buttons-type-subcode-bounded-20261111-a`, `rre-rc75-mouse-buttons-dispatch-writer-crosscheck-20261111-a`, `rre-rc75-agent-c2m-old-rva-current-build-compare-20261111-01`, `rre-rc75-agent-c2m-nearby-old-setter-relocation-20261111-01` and native registration bounded-source study. **Runtime invocation, keyboard or camera effects are deliberately untested.**

1. **P1 (highest leverage):** find current-build native click-to-move destination *setter* from data/control flow and find its real caller; require source proof plus new hash-qualified RVA.
2. **P2:** follow the native button/mouse record dispatcher to the exact Lua-facing event registration and current-build route, without confusing input and locomotion.
3. **P3 (later, explicitly coordinated):** perform one controlled physical LEGION trace linking operator gesture, passive input/button readout, and observed XYZ/camera effects. Addon deployment/reload or game restart require explicit notice before action.
