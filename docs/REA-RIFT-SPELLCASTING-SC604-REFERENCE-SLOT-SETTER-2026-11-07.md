# SC-604 — guarded reference-slot setter behind the six-value cache source (November 7, 2026)

**Owner:** single RRE manager. **Scope:** bounded, offline static analysis of the physical-PC executable. **Verdict:** helper RVA `0x2030EF0` conditionally replaces a pointer held by its first argument, adjusts a DWORD at the pointed object's `+8`, and applies a `0x0E89` discriminator to a candidate. The two calls inside `0x1333200` target **two adjacent global slots**, `0x33E0AA8` and `0x33E0AB0`. This provides a concrete *candidate* initialization/assignment path for the shared pointer slot; it does **not** prove a live slot value, object class, ability identity or successful cast.

## Source and verification

- Original file: `C:\Program Files (x86)\Glyph\Games\RIFT\Live\rift_x64.exe`, exactly **60,493,640 bytes**, SHA-256 **`1935a05c9db6d468e34e0055014a4a99c1b5afceb1695884e24600f5c20a4be8`**, checked afresh in both read-only jobs. RVAs refer only to this physical-file build; no live process or VMware guest was inspected.
- Primary decode: Workbridge job `rre_20261107_0340_sc604_2030EF0_disasm_ro`, exit **0**, existing RRE venv `pefile` and Capstone decoding `0x2030EF0–0x2030F5A` and `0x1333200–0x1333290`.
- Independent verifier: `rre_20261107_0344_sc604_setter_stdlib_ro`, exit **0**, Python 3.14 standard library only. Parsed original PE sections and checked **28/28** size/hash, exact-byte, rel32, RIP-relative and virtual-section assertions, including a deliberately altered local byte negative control. No file was edited by either job.
- Agent capability check: `rre_20261107_0340_freebuff_capability_ro`, exit **0**, listed only fixed `sc103/rc30`, `sc306/sc503`, `slots/file`, `operator/ability` source-copy reviews. These unchanged prompts were previously used; no new independent model run was warranted. Workbridge verification jobs are not model agents.

## New native observations

| RVA | Exact static behavior | Qualified boundary |
| --- | --- | --- |
| `0x1333229` / `0x1333234` | `lea rcx, [rip+0x20AD878]` resolves to **`0x33E0AA8`**; calls `0x2030EF0` with candidate `RDX` derived from `[RCX+0x10]+0x28`. | First assignment destination is adjacent to the later getter slot. The candidate object's type is unknown. |
| `0x133325E` / `0x133326B` | `lea rbx, [rip+0x20AD84B]` resolves to **`0x33E0AB0`**; `rdx=rax` from indirect call; `rcx=rbx`; calls the same helper. | This is the previously identified *returned slot*, now with a candidate producer/assignment call. |
| `0x2030F0E–0x2030F21` | Loads old pointer from `[RBX]`, conditionally decrements `dword ptr [old+8]`; when the count becomes zero it calls `0x1272C18`; then zeroes `[RBX]`. | **Reference-count-like** shape; destructor/type semantics are not verified. |
| `0x2030F28–0x2030F3D` | Loads candidate pointer from `[RDI]`. If nonzero, calls `0x127303C`, loads `ECX=0x0E89`, compares `AX,CX`, and conditionally skips assignment. | Discriminator `0x0E89` is byte-verified; calling it a definitive class/type ID would overstate the evidence. |
| `0x2030F3F–0x2030F4A` | Tests destination pointer against candidate, then `mov [RBX], RAX` and `inc dword ptr [RAX+8]` on the allowed path. | Direct conditional pointer assignment confirmed, not proof the target path executed. |
| `0x2030F4D–0x2030F5A` | Returns `RBX` (destination-slot address); normal function ends at `ret`. | Getter uses returned address, not a resolved object type. |

Both slots are located in the original PE `.data` **virtual-only zero-fill tail**, so the on-disk executable does not encode their runtime contents. The `0x1333200` fast path only tests `0x33E0AB0` for nonzero. The slow path can call the setter twice, but the first and second destinations are **different**. Prior [slot-root](REA-RIFT-SPELLCASTING-SC604-GLOBAL-SLOT-ROOT-2026-11-07.md) and [six-source cache initializer](REA-RIFT-SPELLCASTING-SC604-SIX-REFERENCE-INITIALIZERS-2026-11-07.md) reports remain applicable with this qualification.

## Limits and next gate

This finding advances static provenance for SC-604's cached-reference setup without proving ownership, locking, identity, stable pointer lifetimes, actual cache values, Legendary/Protector's Fury IDs, native cast admission, queue mode or runtime acceptance. **SC-604 is interim; SC-103 and SC-306 remain blocked.** RC-30 historical v0.4.10 Pin→Undo→Reload UI still lacks same-trial pre-Pin and immediate post-Undo/pre-reload proof; later v0.4.11 UI/SavedVariables cannot close that historical gate.

**Next bounded discriminator:** qualify the return/pointee contract of `0x127303C` or trace the intermediate indirect `[RAX+0x50]` producer, **only if** a genuinely novel question remains without REA/RR2 owner overlap. Otherwise park until new live/operator evidence arrives. Do not retry broad native imports or parked probes.

**Safety:** No game input, UI reload, process manipulation, desktop-quarantine override, installed addon/SavedVariables write, dependency install, other-repository edit, or network push.
