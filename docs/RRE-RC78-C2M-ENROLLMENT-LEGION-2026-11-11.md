# RC-78 — actual native C2M callback enrollment (LEGION, November 11, 2026)

**Result:** The constructed click-to-move callback has a source-proven registration route into the same primary listener collection consumed by the native input dispatcher. This closes RC-77's static enrollment gap. It does not establish current execution, active-player identity, movement, or stopping.

## Source and practical consequence

Codex local tools independently identified LEGION and rehashed the original physical `C:\Program Files (x86)\Glyph\Games\RIFT\Live\rift_x64.exe`: 60,493,640 bytes, SHA256 `1935a05c9db6d468e34e0055014a4a99c1b5afceb1695884e24600f5c20a4be8`, preferred image base `0x140000000`. Every address below is an RVA. No Workbridge, game input, process attachment, VM, import, or external provider was used.

The existing input dispatcher can deliver records to the real constructed C2M callback; there is no need to invent an input backend or directly call a destination setter. Remaining work can concentrate on the callback's gates, source gesture, and actor identity. This is an implementation finding, not a completed runtime trial.

## Exact static route

| Link | Verified original instructions |
|---|---|
| Construct/publish the same root | `0xFDCA0D` requests `0xF40`; `0xFDCA1F` calls constructor `0x53DC70`; the successful path retains its result in RBX. `0xFDCA2B` and `0xFDCA3A` write RBX to global `0x33623E0`. |
| Initialize that root | `0xFDCA41 mov rcx,rbx`; `0xFDCA44 call 0x5725F0`; initializer `0x5725FA` retains RCX in RDI. |
| Pass the C2M callback as the listener | `0x572680` reads root `+0x350`; the nonzero owner path reads owner `+0` as receiver; `0x572694 mov rdx,[rdi+0x3F0]`; `0x57269B call 0x7C1E20`. The root constructor's `+0x3F0` callback identity is preserved from RC-77. |
| Insert that exact listener | `0x7C1E36` retains RDX in RBX; `0x7C1E77` writes listener to new node `+0x10`; `0x7C1E7B` increments receiver `+0x10`; `0x7C1E88..0x7C1E98` links into receiver `+0x08`'s primary sentinel list. |
| Dispatch the same collection | `0x7C1BAB` loads primary sentinel; `0x7C1BD4` loads node `+0x10`; `0x7C1C28` appends that listener to the dispatch array; `0x7C1CC9` calls listener vtable `+0x08`. RC-77's wrapper/thunk then conditionally reaches `0x6A5E10` and C2M handler `0x6A6120`. |

## Correction: ordering anchor is not the inserted listener

The previously cited `0x6A3933→0x7C1F30` call passes **RDX = `[r15+0x20]`** as the inserted listener and **R8 = `[root+0x3F0]`** as an ordering anchor. The callee retains the anchor in RBP, searches for it at `0x7C1F80`, and writes the separate RDX-derived listener at `0x7C1FB1`. That call alone never demonstrated C2M enrollment. The newly identified `0x57269B→0x7C1E20` supplies the actual enrollment route.

## Verification and remaining boundaries

One independent Codex agent discovered and source-checked the route. The manager separately rehashed all seven original windows in the [evidence JSON](RRE-RC78-C2M-ENROLLMENT-LEGION-2026-11-11.json) and decoded the decisive instructions. Full-window alignment was checked before accepting instruction claims; arbitrary mid-instruction slices are not accepted disassembly. The agent found 14 syntactic E8 callers to the insert routine and one to the initializer; this does not exclude indirect callers.

Registration/dispatch remain conditional on the initialized receiver, secondary-list exclusions, special-listener handling and callback predicates. The initializer's zero-owner path passes null receiver rather than returning early; this trace does not prove its runtime precondition. A registered callback does not prove receipt of a particular real mouse message.

Next bounded questions: identify `0x6A6620`'s callback gate and exact type2/subcode1 Win32 provenance; separately identify global `0x336FD20` and transform-object ownership. Actual movement/arrival/stop still requires current physical LEGION evidence. The new seven-hour objective prioritizes practical combat/quest work alongside these specific native gaps.
