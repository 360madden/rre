# SC-604 — six guarded reference-value initializers (November 7, 2026, ~01:37 EST)

**Owner:** single RRE manager. **Verdict:** six static cache initializers independently tied to six different DWORD source offsets; **not** spell-ID semantics, a live value or a successful cast.

## Source and bounded methods

- Original physical-PC `C:\Program Files (x86)\Glyph\Games\RIFT\Live\rift_x64.exe`; 60,493,640 bytes, SHA-256 `1935a05c9db6d468e34e0055014a4a99c1b5afceb1695884e24600f5c20a4be8`, freshly verified from file bytes. RVAs below apply **only** to this exact build. All six targets reside in a writable `.data` section; file-initialized bytes **cannot** establish their current runtime values.
- Bounded read-only Workbridge jobs: `rre_20261107_0138_sc604_globals_decode_ro` (Capstone, exit 0), `rre_20261107_0142_sc604_initializer_decode_ro` (Capstone/PE, exit 0), `rre_20261107_0145_sc604_six_sources_ro` (Capstone, exit 0), `rre_20261107_0147_sc604_globals_stdlib_ro` (independent Python 3.14 standard-library-only PE/RVA/rel32 check, exit 0). All four output captures untruncated. The independent check passed **60** exact guard/call/load/store/section assertions and one misaligned-address negative control. The second method validates file bytes and encoded target arithmetic, not the full CFG or callee effects.
- Builds on the [predicate and its two routes](REA-RIFT-SPELLCASTING-SC604-PREDICATE-49FAB0-2026-11-06.md) and the [forwarded lookup-key chain](REA-RIFT-SPELLCASTING-SC604-LOOKUP-KEY-PROVENANCE-2026-11-07.md); no resolved helper, general import or parked probe was repeated.

## Newly qualified guarded cold paths

The six pre-comparison checks at `0x49FAF9–0x49FB45` use the guard addresses below; when their comparison branches reach their respective cold regions, the region checks its guard against `-1`, calls `0x1333200` and `0x171BFF0`, then reads a DWORD through `[rax] → rdx → [rdx+offset]` and copies it into an adjacent writable global. This shared instruction pattern does **not** establish source-object identity or runtime branch feasibility.

| Cold region begins | Guard DWORD RVA | Adjacent cached DWORD RVA | DWORD load from `[rdx+...]` | Global store RVA |
| --- | --- | --- | --- | --- |
| `0x49FD2B` | `0x3362434` | `0x3362430` | `+0x18` at `0x49FD63` | `0x49FD66` |
| `0x49FD82` | `0x336243C` | `0x3362438` | `+0x50` at `0x49FDBA` | `0x49FDBD` |
| `0x49FDD9` | `0x3362444` | `0x3362440` | `+0x4C` at `0x49FE11` | `0x49FE14` |
| `0x49FE30` | `0x336244C` | `0x3362448` | `+0x48` at `0x49FE68` | `0x49FE6B` |
| `0x49FE87` | `0x3362454` | `0x3362450` | `+0x40` at `0x49FEBF` | `0x49FEC2` |
| `0x49FCD4` | `0x336245C` | `0x3362458` | `+0x2C` at `0x49FD0C` | `0x49FD0F` |

Each of the six independently checked routes encodes a direct call to `0x1333200`, then to `0x171BFF0`; the checked bytes `8B 42 xx` are the stated source-DWORD loads, and each `89 05 <rel32>` store resolves **exactly four bytes before its paired guard**. A bounded decode of `0x171BFF0` shows it returns its local destination wrapper (`mov rax,rbx` near `0x171C047`), compatible with the following `mov rdx,[rax]`; the object's type, the meaning of `+0x960` in its pre-call setup, and any exceptional side effects are unresolved.

**Decision-changing result:** The six-reference route does not rely exclusively on six hardcoded numeric literals: the exact physical binary contains **six explicit guarded pathways that populate six writable cache DWORDs from six distinct offsets on an indirectly reached pointer**. Whether those six invocations refer to the same object instance is **not proven**. This narrows the unresolved origin question. It does **not** establish whether any particular values represent ability IDs, flags, learned spells, Legendary/Protector's Fury selection, GCD modes or native queue enums. Do not infer that all six cold paths run in a given session.

## Limits, coordination and next discriminator

SC-604 remains an **accepted interim mechanism**; SC-103 and SC-306 remain blocked. Strict RC-30 Pin→Undo→Reload same-trial screenshot/pre-Pin archival evidence remains missing, and RC-32 live Retry remains unverified. The already qualified v0.4.11 physical package, UI-load and SavedVariables version evidence does not close those gates.

The smallest possible new research would be a **bounded, owner-cleared qualification of the object returned by `0x1333200`** (or the data source passed via `+0x960`), but only if it is not already handled by RR2/REA; otherwise park the source-meaning question. No inference from unqualified VM code or dynamic process state. No game input, reload, process control, installed-addon or SavedVariables write, desktop-quarantine override, cross-project mutation or push occurred.
