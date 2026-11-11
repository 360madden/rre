# RRE RC-77 — current RIFT C2M callback dispatch, native arrival and transform (LEGION, 2026-11-11)

> **Source breakthrough, not live movement acceptance.** The current LEGION binary now has a bounded native route from a constructed callback object, through an input-dispatch vtable wrapper, to callback `0x6A5E10`, which conditionally tail-jumps to the current click-to-move handler `0x6A6120`. The native arrival-radius comparison and a downstream orientation-component writer are also recovered. Whether a real mouse click delivers to this specific object and whether the component is the active player are still unknown.

## Identity, source and safety

- **Actual machine:** `LEGION`, independently verified through `C:\Windows\System32\hostname.exe` (exit 0).
- **Source:** installed `C:\Program Files (x86)\Glyph\Games\RIFT\Live\rift_x64.exe`, **60,493,640 bytes**, SHA-256 `1935a05c9db6d468e34e0055014a4a99c1b5afceb1695884e24600f5c20a4be8`, preferred base `0x140000000`. All offsets below are **RVAs**, not virtual addresses or portable offsets.
- **Scope:** static original-executable PE inspection only; no process attachment, gameplay input, UI automation/reload, install, VMware/AMD-DESKTOP access, RR2 edit, external provider, or push. The older 59,963,840B build's RVAs remain incompatible.
- **Provenance:** paired [machine-readable RC-77 evidence](RRE-RC77-CURRENT-C2M-CALLBACK-ARRIVAL-AND-TRANSFORM-LEGION-2026-11-11.json) records **20 independently rehashed PE source windows**, individual RVAs, caveats and job IDs. No inference about runtime is hidden as fact.

## 🟢 Practical breakthrough #1 — native callback delivery machinery

| Link | Original instruction / field | Status |
| --- | --- | --- |
| Construct callback | `0x53E58B` loads `0x6A5E10`; `0x53E5A8` installs vtable `0x26A79B8`; `0x53E5BC` saves callback object at owner `+0x3F0` | Source-proven |
| Pass object to receiver routine | `0x6A391E` reads `[context+0x3F0]`; `0x6A3925` finds receiver; `0x6A3933` passes callback object in `R8` to `0x7C1F30` | Source-proven call, full membership not proven |
| Dispatcher virtual call | `0x7C1CC9 call [vtable+8]` | Source-proven dispatch slot |
| Outer virtual method | Static vtable `0x26A79B8+8` contains `0x4E3210` | Source-proven pointer value |
| Wrapper / inner guard | `0x4E3228 call [inner_vtable+8]` resolves to `0x497090`; if true, `0x4E3238 call [inner_vtable+0x10]` resolves to `0x494AE0` | Source-proven conditional dispatch |
| Inner callback thunk | `0x494AE0 mov rax,[rcx+0x10]`; `0x494AE4 mov rcx,[rcx+8]`; `0x494AE8 jmp rax`. Stored function `0x6A5E10` | Source-proven object layout / jump |
| Callback gate / handler | `0x6A5FAD call 0x6A6620`; `0x6A5FB4 jne 0x6A610D` skips C2M when predicate nonzero; otherwise `0x6A5FCF jmp 0x6A6120` | Source-proven conditional tail jump |
| Event-to-destination | Handler type **2**, subcode **1** checks setting `+0x146` at `0x6A6242`; `0x6A650D call 0x5749C0` stores destination | Previously RC-76 source-proven |

**Critical boundary:** A function call passing the callback object to `0x7C1F30` and a matching virtual dispatch design do **not** yet establish this precise object as a member of the collection traversed by the `0x7C1AD0`/ `0x7C1C90` dispatcher. `0x7C1F30` manipulates receiver-linked lists, and a newly allocated node holds a separate token. Likewise, native record **type2/subcode1 has not yet been traced uniquely back to a particular Win32 button-up message**. This is a source-proven **potential** event path, not observed delivery or live movement.

**Important correction to RC-76:** callback `0x6A5E10` and handler `0x6A6120` have distinct `.pdata` function entries. Their linkage is an explicit, guarded tail `jmp` at `0x6A5FCF`; mere proximity was never sufficient. The predicate call occurs at `0x6A5FAD`, **not** at `0x6A5FA7` (a `mov`). An initial QA assertion failed due to that misread; the corrected second independent QA passed. Preserve this as a regression guard.

## 🟢 Practical breakthrough #2 — precise native arrival radius

The C2M-active consumer loads float `0.0625` from `0x26AE4D8` at `0x588747`; zeroes the vertical delta at `0x58889F`; computes squared horizontal displacement through `0x5888C6`; and executes `0x588A16 comiss` followed by `0x588A1A jae`. When squared distance is **strictly less** than the constant, `0x588A1F call 0x546830` clears C2M state:

\[
(\Delta X)^2 + (\Delta Z)^2 < 0.0625\quad\Leftrightarrow\quad \mathrm{horizontal\ distance}<0.25\ \mathrm{native\ coordinate\ units}.
\]

This is **not a calibrated world-meters figure** and **not evidence the player stopped in a running game**. A different branch compares against a dynamic squared threshold at another object `+0x20` and can call `0x5460A0`; it must not be folded into the fixed arrival-radius proof.

## 🟢 Practical breakthrough #3 — downstream orientation-component writes

The consumer calls `0x588925→0x698C90` and conditionally `0x5889A2→0x698DB0`, each reaching shared writer `0x698EC0`. The latter conditionally writes an object's **36-byte transform**:

- `0x698EED`: 16 bytes at `object+0x60`.
- `0x698EF5`: 16 bytes at `object+0x70`.
- `0x698EFC`: four bytes at `object+0x80`.
- `0x698F65`: optionally writes an angle-like float at `object+0xF0`.
- `0x698F6D`: sets a dirty/changed byte `object+0xF4 = 1`.

**Object transform mutation is proven.** That object (the consumer's `r14`) has not been proven to be the local player, nor do these writes establish authoritative yaw, translational velocity, locomotion actuation, or collision resolution. This gives the next investigation precise pointer edges and a dirty-flag consumer to trace.

## 🟢 Setting identity narrowed, runtime value unknown

`0x798B80` (called at C2M handler `0x6A6238`) attempts a component-specific handle first. Its **fallback** calls `0xE76790→0xBCF470`, which addresses the same global pointer slot `0x33958C0` as the native `Misc_EnableClickToMove` writer/reader. The handle-copy helper `0x1C62670` returns the pointer used for the handler's `+0x146` gate. No proof that **every** call uses fallback or that the setting is currently enabled.

The constructor's own `owner+0x10` self pointer is **not** the callback object's `+0x10` context. The callback context resolves via `0x6A9B10→0x6A3EE0→0x58B20` to **global qword slot `0x337FD20`**. Its writer and object type are still unknown; do not call it the active player without proof.

## Verification and what this does *not* prove

- Five independent read-only specialist lanes inspected callback, ownership, settings, arrival, and transform paths. The coordinator separately verified **all 20/20 source-window SHA-256 values against the pinned original installed PE**, including outer/inner vtables and both transform builders.
- Independently checked exact instructions `0x6A391E/0x6A3925/0x6A3933`, `0x4E3228/0x4E3238`, `0x494AE0..0x494AE8`, `0x6A5FAD/0x6A5FCF`, and `0x698EED/0x698EF5/0x698EFC/0x698F65/0x698F6D`.
- Independent primary QA jobs and one corrected assertion are listed in JSON. No real mouse delivery, live process, setting value, position trace, actual player turn, or verified stop occurred.
- Preserve the existing [NAV-002 behavior-test gates](navigation-first-behavior-test.md): exact local client + current setting/bindings, location-bound delivered destination, time-aligned player XYZ showing displacement and stop, and separate execution ownership/approval. Reuse the existing RR2 telemetry/control when coordinated; no speculative new helper app is needed for this proof.

## Ranked next practical advances

1. **🥇 Resolve registration-to-dispatch enrollment:** trace `0x7C1F30`'s receiver lists into the exact dispatcher array, and separately source-qualify the record type/subcode Win32 provenance. Use only bounded hash-pinned PE windows.
2. **🥈 Prove actor/object identity:** find who writes global `0x337FD20`, qualify consumer `rdi`/transform `r14` identity and trace consumers of dirty flag `+0xF4`. Stop short of asserting player yaw/velocity until owner identity is source-proven.
3. **🥉 Obtain real NAV-B01–B04 evidence only in a separately coordinated physical LEGION trial:** confirm settings and gesture, record actual delivery and timestamped player XYZ/arrival, and observe stop. Preannounce any addon reload or RIFT restart and obtain the applicable task-specific approval. No such test was conducted at RC-77.
