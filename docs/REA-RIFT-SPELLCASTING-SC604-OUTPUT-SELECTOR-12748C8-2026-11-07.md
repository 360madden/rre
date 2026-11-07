# SC-604 — output-pointer and selector routing at 0x12748C8 (November 7, 2026, ~06:35 EST)

**Owner / scope:** the single RRE manager, a bounded **offline read-only** examination of the physical-PC RIFT executable. **Finding:** the previously unresolved helper `0x12748C8`, reached from `0x1333200`, uses the caller's `RDX` as a pointer-to-pointer output location, attempts to construct a `0x78`-byte object, reads a **16-bit** selector from upstream `[RSI+0x40]`, and passes the selector plus the output address to `0x1290768`. The object/selector meaning and runtime behavior are **unverified**.

## Source, verification and receipts

- Original source: `C:\Program Files (x86)\Glyph\Games\RIFT\Live\rift_x64.exe`; **60,493,640 bytes**, SHA-256 **`1935a05c9db6d468e34e0055014a4a99c1b5afceb1695884e24600f5c20a4be8`**. Both completed offline jobs independently rehashed the **original file**. The target is RVA `0x12748C8`, file offset `0x1273CC8` in `.text`; RVAs **do not** identify running process memory or another build.
- **Primary method:** Workbridge job `rre_20261107_0635_sc604_12748c8_disasm_ro` (exit 0), existing RRE venv + pefile/Capstone, bounded 200-byte native decode; direct caller also inspected in prior source-hashed `0x1333200` report.
- **Independent method:** `rre_20261107_0645_sc604_12748c8_stdlib_fixed_ro` (exit 0), Python standard-library-only PE header/section parser, original byte matching, signed `rel32` call/RIP resolution and two negative controls: **32/32 assertions passed**. Both logs untruncated. Preliminary verifier `rre_20261107_0643_sc604_12748c8_stdlib_ro` exited 1 because the **verifier** constructed literal backslash-zero PE-signature bytes instead of null bytes; the corrected verifier passed. The initial failure is *not* evidence of a defect in the target RIFT binary.
- FreeBuff's supported RRE review adapter was checked read-only using `rre_20261107_0635_freebuff_check_ro` (exit 0); it exposes only prior fixed prompts `sc103/rc30`, `sc306/sc503`, `slots/file`, `operator/ability`. These were already reviewed against unchanged evidence and do not meaningfully review this new helper. **New genuine model agents: 0**. Workbridge commands are **not** AI workers.

## Exact static observations

| Original-byte anchor | Qualified narrow result |
| --- | --- |
| `0x1333218–0x1333222`: `lea rdx,[rsp+0x30]`; direct call `0x12748C8`; `mov rcx,[rax]` | The upstream caller supplies a stack output address and dereferences the returned address after the call; it does **not** receive the object pointer directly as the helper's return. |
| `0x12748D7–0x12748E7`: `mov rsi,rcx`; `mov rbx,rdx`; `mov ecx,0x78`; direct call `0x126EB88` | Preserves source object in `RSI`, output address in `RBX`, and requests a 120-byte allocation. |
| `0x12748F2–0x1274904` | On the nonnull allocation branch, calls `0x1274660`, zeros `[RDI+0x70]`, writes `[RBX]=RDI`, then increments `[RDI+0x70]`. The latter is **counter-like**, without proven lifetime semantics. |
| `0x1274906–0x1274914` | Null allocation branch writes a null pointer into `[RBX]`; the joined path reloads `RAX=[RBX]` and stores zero to byte `[RAX+0x68]`. This is a **statically unguarded dereference on the null branch**, but the branch's actual reachability and allocation-helper guarantees are unknown. Do not claim a reproduced crash. |
| `0x1274914–0x127492C` | Reads and conditionally initializes the **same** global slot at RVA `0x3372C18` via `0x1274748` on the zero path; both RIP-relative displacements independently resolved to that RVA. |
| `0x127492C–0x127493B` | Zero-extends a word from `[RSI+0x40]` into `EDX`, sets `R8=RBX` (the output **address**), sets `RCX` to the global-slot **value**, and directly calls `0x1290768`. This qualifies a **16-bit selector/input argument**, not its semantic type or ability identity. |
| `0x1274940–0x127494D` | Moves `RBX` to `RAX` and returns; caller's read of `[RAX]` is consistent with returning the supplied pointer-to-pointer output location. |

All five direct-call targets in the bounded verification were independently checked: `0x126EB88`, `0x1274660`, `0x1274748`, `0x1290768`, and the caller-to-helper `0x133321D → 0x12748C8`.

## Proof boundary and gate status

**What changed:** The upstream `0x1339EC0 → 0x1333200 → 0x12748C8` chain now has a specific **object-output + word-selector + shared-global helper** interface grounded in original instruction bytes. This is not a resolved second-stage dynamic dispatch target, real instance identity, runtime object classification, native ability ID, Legendary/Protector's Fury selection, game action, or successful cast.

**What did not change:** SC-604 is marked `completed` for its earlier **interim** mechanism only; SC-103 Legendary identity and SC-306 queue enum remain blocked. RC-30 historical **v0.4.10 same-trial** Pin → Undo-before-Reload UI → matching SavedVariables archive remains incomplete despite separate v0.4.11 load/persistence evidence; RC-32 physical Retry is unverified. No register status change is justified.

**Possible next bounded question:** characterize `0x1290768`'s use of the word selector and the output pointer **only if** independent exact-build evidence and other-repository ownership permit a small nonduplicative test. Otherwise park this lead. Do not broadly import the client, treat a pointer as an ability ID, or launch redundant review prompts.

**Safety/ownership:** physical game input/reload, process or desktop-lease access, installed-addon or SavedVariables writes, other-repository edits, new dependency installs, and network publishing were not performed. Seven existing auxiliary RRE worktrees were inspected without mutation; the pathfinding branch's two preexisting untracked scripts remain preserved. RRE main's nine historical untracked paths remained untouched.
