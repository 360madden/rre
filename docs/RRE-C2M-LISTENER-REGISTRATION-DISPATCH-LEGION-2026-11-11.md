# RRE RC-71 — native input listener registration and callback filtering

**Host:** LEGION · **Date/time:** 2026-11-11 ~12:20 EST · **Evidence:** original physical RIFT executable, static read-only · **Result:** accepted native receiver list count, direct registration paths and queued/immediate predicate distinction. No physical movement/stop result.

## 1. Definitive listener-list layout and writers

- `receiver+0x08` is a circular primary-list sentinel pointer; `receiver+0x10` is its **64-bit element count**, not a callback-root pointer. The initializer writes zero, callback fanout uses it as the nonempty guard, and the following exact code **increments/decrements it as nodes are inserted/removed**.
- `receiver+0x18` is the secondary circular-list sentinel pointer and `receiver+0x20` its corresponding count, also decremented by the same list-update code.
- `0x7C1E20` (260 B, 69 instructions): list movement/update, including `inc qword ptr [rdi+8]` at `0x7C1E7B` with `rdi=receiver+8`, and `dec [rsi+0x10]` at `0x7C1F09`; secondary count `dec [rsi+0x20]` at `0x7C1EBB`.
- `0x7C1F30` (302 B, 81 instructions): listener node allocation/reordering. At `0x7C1FB1` writes listener pointer to `[node+0x10]`, `0x7C1FB5 inc [receiver+0x10]`, and `0x7C1FC2..0x7C1FD2` splices the 0x18-byte node into the primary list; `0x7C2043 dec [receiver+0x10]` on removal. Also `0x7C1FF5 dec [receiver+0x20]` on secondary-list relocation.
- The receiver destructor `0x7C0340` independently traverses/frees both chains and their sentinels. These frees are for list nodes/sentinels; destruction of listener objects themselves is **not** proven.

## 2. Direct root-to-receiver listener registration calls

An exact syntactic `.text` E8-rel32 scan found **14** sites targeting `0x7C1E20` and **16** targeting `0x7C1F30` (syntactic calls, not 30 proven runtime executions). Complete relevant caller decode validates the following reachable *code paths*, not that every branch executes live:

1. Five branches of caller `[0x6F2D40,0x6F3FC9)` call `0x7C1E20` at `0x6F2E27`, `0x6F2F2D`, `0x6F3050`, `0x6F3111`, `0x6F3410`. The calling object is held in RSI (`0x6F2D6A mov rsi,rcx`). The example at `0x6F2E0D` loads `RBX=[RSI+0x170]` listener; `0x6F2E14 call 0x49A020` obtains root; `0x6F2E1C call 0x54F7C0` fetches receiver via `root+0x350 -> owner+0`; `0x6F2E21 mov rcx,rax`, `0x6F2E24 mov rdx,rbx`, then registration call `0x6F2E27`.
2. The same full caller invokes `0x7C1F30` at `0x6F3EDF` after identical root/receiver lookup, using the listener `[RSI+0x170]` as RDX and a separate R8 anchor read through `root+0x330` and `+0x150`; exact anchor meaning not qualified.
3. In `[0x936950,0x937966)`, `0x936D03` stores a newly constructed/chosen candidate pointer to `[r15+0x1B0]`; `0x936D0A call 0x49A020`, `0x936D12 call 0x54F7C0`, then `0x936D1D call 0x7C1E20` with receiver RCX and listener RDX.
4. Separate bounded `[0x6A3912,0x6A3948)` proves `0x6A3933 call 0x7C1F30` with root/receiver getter, listener `[r15+0x20]`, and R8 anchor `[root+0x3F0]`. Another complete function `[0x4FB020,0x4FCA91)` uses `0x7A3500` receiver-accessor-like path, `RDX=RSI`, and `0x4FB038 call 0x7C1E20`; exact RSI listener class remains unknown.

**Boundary:** The small getter `0x54F7C0` is fully decoded and previously linked to the owner receiver. No new caller-side null check immediately after the getter was observed in these selected branches; preconditions are not proven. Static callsites do **not** prove that the active player's movement/stop listener has been identified or that injected input is accepted.

## 3. Why the queued and immediate-delivery paths differ

- `0x7C1AC0` writes `R8B=1` then tail-jumps to `0x7C1AD0`. Six exact direct E8 sites from the already-qualified 5/6/7 keyboard-record producers call this wrapper (`0xFB523E`, `0xFB528E`, `0xFB5302`, `0xFB6CE6`, `0xFB6DFF`, `0xFB6E6F`).
- In `0x7C1AD0`, the saved flag becomes `R13B` at `0x7C1AF5`. The special listener at receiver+0x28 and primary list listeners call virtual `+0x10` predicates **only when R13B is nonzero** (`0x7C1C53..0x7C1C60`, `0x7C1CAE..0x7C1CBE`). If the predicate returns false, virtual `+0x08` delivery is skipped; otherwise the callback receives the original record in RDX.
- `0x7C1D40` drain passes `R8D=0` at `0x7C1D87/0x7C1DD7` into `0x7C1AD0` calls `0x7C1D90/0x7C1DE0` for 0x140/0x130-stride queues. Three direct calls from `0x7C0480` (`0x7C0590`, `0x7C05DD`, `0x7C0630`) also set R8D=0. Therefore these selected buffered/direct paths **skip the optional listener predicate**, while 0x7C1AC0 wrapper invokes the predicate.
- This is an internal callback filter distinction, **not a gameplay input security conclusion**.

## 4. Original source window receipts

Physical original `C:\Program Files (x86)\Glyph\Games\RIFT\Live\rift_x64.exe`: 60,493,640 B, SHA-256 `1935a05c9db6d468e34e0055014a4a99c1b5afceb1695884e24600f5c20a4be8`, image base `0x140000000`; all addresses are RVAs.

| Half-open source region | Bytes / decoded instructions | SHA-256 |
|---|---:|---|
| `[0x7C1E20,0x7C1F24)` | 260 / 69 | `e7e612ae943c3e7c50075d85e3adc0a21bf1e2d0ce0c3f120f53d8f966bcffba` |
| `[0x7C1F30,0x7C205E)` | 302 / 81 | `0f6c2731e8c237a67cc1a6bdb193e3c4276d4901d88a200038e3180c219a4e3f` |
| `[0x6F2D40,0x6F3FC9)` | 4,745 / 1,148 | `39087e0d86061741a5e2d95718b759aa31c8ebc283c304155723b09feae089be` |
| `[0x936950,0x937966)` | 4,118 / 974 | `313d90e9458f9d789e04fd85f5e064ec9abfbdbda330ae9f183161c8b48d7aea` |
| `[0x6A3912,0x6A3948)` | 54 / 11 | `ac541f75182cc7934443efe78be8e36f9535b6eae9f83726cf8a9f61d6182615` |
| `[0x4FB020,0x4FCA91)` | 6,769 / 1,629 | `8c17cb5af01164f584d974cecfb444b87bf4a4745d4b83bab61a157ec8068364` |
| `[0x7C1B7F,0x7C1D32)` | 435 / 119 | `b0a6e17f33aacc531541bcb07611bed13d22bf4a54d250e7ce5396f81da93ee5` |
| `[0x7C1D40,0x7C1E1D)` | 221 / 54 | `acd9156d25be9ac21cd0bd2ef188f02b2777ed09a6c8355f69bf2ac5b0eaabef` |
| `[0x7C1AC0,0x7C1AD0)` | 16 / 10 | `19f86ef4e3d48ea74f780a677e6c04217a6cb5541239e2bdcd34f72903891e62` |
| `[0x7C0480,0x7C0673)` | 499 / 126 | `0aaaad0bc6f186ab172dee5c4bfa77647d9f406288b257266422a82140c1fa97` |
| `[0x54F7C0,0x54F7D1)` | 17 / 6 | `66a56a6b070f8087cdd68637f4dab49dbd8fbdd6b6107b0599340b36f2d93d64` |

Manager jobs passed: `rre-rc71-manager-registration-filter-confirm-20261111-01`, `rre-rc71-manager-immediate-wrapper-dispatch-20261111-01`, `rre-rc71-manager-list-registration-e8-callsite-scan-20261111-01`, `rre-rc71-manager-anchored-registration-caller-context-20261111-01`. Independent read-only LEGION agent jobs passed: `rre-rc71-lane-a-list-insert-remove-two-windows-20261111-01`, `rre-rc71-lane-a-registration-two-callsite-functions-20261111-01`, `rre-rc71-lane-c-registration-two-callsites-original-20261111-01`, `rre-rc71-lane-c-second-registration-window-6a3912-20261111-01`, `rre-rc71-b-two-registration-caller-original-full-20261111-01` and prior vtable/destructor jobs. One manager bounded `.pdata` context probe scanned 8 selected sites; no gameplay executed.

## 5. Next high-value work

1. **Trace the actual listener concrete class:** Follow construction/assignment of `[eventHandler+0x170]`, then inspect its vtable+0x08 callback and +0x10 predicate in bounded original-PE windows. Only classify as movement when event-to-coordinate evidence warrants.
2. **Connect listener classes to record types and per-key processing:** Source-trace targeted callback callee(s), maintain record type5/6/7 *numeric* meanings as unqualified until proven.
3. **Separately approved physical correlation:** Confirm RRECollector loaded version, capture timestamped XYZ before/after a controlled manual input and independent physical-key timeline. No such live test in RC-71.

**Scope:** LEGION only. Source reading and documentation; no game input, process attachment, VM/AMD access, installs, other repo writes or remote push.
