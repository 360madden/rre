# RC-66 — Proven Win32 keyboard-state-to-native receiver dataflow (LEGION)

**Accepted static breakthrough:** Original RIFT calls `USER32!GetKeyboardState`, builds a type-6 record containing its 256-byte result, then calls a leaf wrapper that tail-jumps to the native receiver writer. The writer copies record+0x19 to receiver+0xA41. The paired reset path calls `USER32!MapVirtualKeyW` on active table indices and creates type-7 records. This proves native Windows virtual-key dataflow; it does **not** prove live movement, simulated-key acceptance, a specific player owner, or actual stop behavior.

## Host, source and proof boundaries

- Actual `hostname.exe` returned `LEGION` (job `rre-rc66-host-verification-20261111-01`, exit 0). Project `C:\work\rre`, branch `main`, starting clean HEAD `04ecf656d50ebbaf43192180d258879eaeb7f726` (21 ahead of origin).
- Original installed physical `C:\Program Files (x86)\Glyph\Games\RIFT\Live\rift_x64.exe`, 60,493,640 bytes, SHA-256 `1935a05c9db6d468e34e0055014a4a99c1b5afceb1695884e24600f5c20a4be8`, preferred base `0x140000000`. RVA labels throughout.
- Four independent read-only source investigation lanes and manager independent byte/hash/instruction/import checks. Only the original PE and existing RRE Python tooling were read. No game process attachment, input, UI, reload, AMD/VM access, installs, Ghidra/REA import, network push or other repository writes.

## Full original-code keyboard-state path (new, static proof)

| Step | Original RVA / operation | Verified meaning |
|---|---|---|
| 1 | `0xFB6C8D` buffer=`rsp+0x150`; `0xFB6C95` indirect call via IAT `0x25EFD68` | `USER32.dll!GetKeyboardState` fills a 256-byte stack buffer on success; return value is not checked in the selected fragment. |
| 2 | `0xFB6C9E..0xFB6CAB` calls `0x7C0200` with `RCX=rsp+0x20`, `EDX=6` | Creates **record type 6**, with 256-byte body at +0x19 initially zeroed. |
| 3 | `0xFB6CB0..0xFB6CBD` calls `0x7C21F0` with `RDX=rsp+0x150` | Imported `VCRUNTIME140!memcpy` copies exactly 256 bytes from the OS state buffer into record+0x19; high-bit tests at 0x10/0x11/0x12 derive record mask 2/4/1. |
| 4 | `0xFB6CD9..0xFB6CE6` accessor `0x7A3500`, then `RCX=[RAX]`, `RDX=rsp+0x20`, call `0x7C1AC0` | Sends record and resolved receiver pointer to an eight-byte leaf wrapper. **Concrete runtime owner identity remains unknown.** |
| 5 | `0x7C1AC0` sets `r8b=1`; `0x7C1AC3` jumps to `0x7C1AD0` | Preserves receiver/record pointer registers and immediately enters the established writer. |
| 6 | `0x7C1B41..0x7C1B52` source=`record+0x19`, destination=`receiver+0xA41`, length=`0x100` | Copies all 256 bytes into the same native state table sampled by RC-62 predicates. The later +0x38 mask update is conditional on record types 1/2/3 and **not claimed for type 6**. |

Microsoft primary docs: [GetKeyboardState](https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-getkeyboardstate) (256 bytes; high bit down), [Virtual-Key Codes](https://learn.microsoft.com/en-us/windows/win32/inputdev/virtual-key-codes) (`VK_SHIFT=0x10`, `VK_CONTROL=0x11`, `VK_MENU/Alt=0x12`), [MapVirtualKeyW](https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-mapvirtualkeyw) (mapping mode 2 means `MAPVK_VK_TO_CHAR`). OS documents explain semantics; RIFT relationships are verified separately from original PE instructions.

## Construction, event reset and gating (other source-verified results)

- Receiver allocation site `0x79A62A` requests `0xB48` bytes through `0x78E110`; `0x79A63C` directly invokes constructor `0x7C00A0`, then `0x79A641` stores resulting pointer at caller owner+0. The owner class and relation to active player are not qualified.
- Constructor `0x7C00A0` sets `receiver+0xA40` (queue-drain gate) to 0, clears 256 bytes at `+0xA41` via imported `memset`, sets `+0x38` mask to 0, and initializes queue containers. Nonzero +0xA40 later skips **queued drains and pointer resets**, but record types 8..16 bypass that branch for immediate handler processing.
- A distinct reset path at `0x7C0940` enters body only when incoming `DL=0`; its active-byte loop creates **type-7** records. At `0x7C09E4`, RIFT calls `USER32.dll!MapVirtualKeyW(index, 2)` (IAT `0x25EFC68`), writes returned character code to record+0x120, index to record+0x124, and a 256-byte snapshot to record+0x19; dispatches at `0x7C0A0C`. Three later mask branches emit **type-2** records with subcodes 1, 2 and 4 at +0x120, not type-1.
- The reset subsequently uses imported `memset` to clear receiver+0xA41 (0x100 bytes) and stores zero in receiver+0x38, because prior `0x7C0981 xor r15d,r15d` defines the source register. These are compiler-defined `.pdata` fragments, not independently established public entry points.

## Exact original-byte verification windows

| Label / half-open RVA interval | Bytes | Instructions | SHA-256 |
|---|---:|---:|---|
| OS state source `[0xFB6C5F,0xFB6D0B)` | 172 | 36 | `f03d32d78486f93d7be9ef3bc16a498366ab0dc54c4133c3d20505e0ac281b97` |
| Record type-6 constructor `[0x7C0200,0x7C0286)` | 134 | 33 | `c010ae7d7309e77f768c89ff060177e88f153c41ac2c46627392110e9efa0e82` |
| VK record copy/mask `[0x7C21F0,0x7C222C)` | 60 | 18 | `6d2f06910e6579acc8bb4ba7e8c0514742433726b7926dc91e4e268e5689cf23` |
| Leaf wrapper `[0x7C1AC0,0x7C1AC8)` | 8 | 2 | `890375bf530a9b9cc41e1c92ebd56eb78e373e4ff696ce536f88c639a94afaf3` (no `.pdata` entry) |
| Receiver writer `[0x7C1AD0,0x7C1B7F)` | 175 | 44 | `967e6ae9c1220e9c8c5a3d72b9360710ac37d25a8d126f9eb00ba91caa0ef0a5` |
| Receiver constructor `[0x7C00A0,0x7C016A)` | 202 | 48 | `91dd527b1562b535ed21c3675fde7a711f04b40f30416a55e894d4979b7cee2a` |
| Constructor owner `[0x79A590,0x79A9D3)` | 1091 | 237 | `3c8cfd1121328b2fc65160f976991f908cc98817b3f2e3eae62690c81faa018f` |
| Dispatcher `[0x7C0480,0x7C0673)` | 499 | 126 | `0aaaad0bc6f186ab172dee5c4bfa77647d9f406288b257266422a82140c1fa97` |
| Reset prologue/loop `[0x7C0940,0x7C0A40)` | 256 | 57 | `3dff7574010a45e934bc05814988f235f2d57c3ddb7cba8b74aa25c2c62f9f7f` |
| Reset tail `[0x7C0A40,0x7C0BAA)` | 362 | 82 | `d10dd985a73f7e52f18352ad9362d397b65753f93fe69511b81be0fd512e41ee` |

## Bounded negatives, receipts and next tasks

- One exact `E8` target scan for fragment `0x7C0780` found **zero** direct callsites across original `.text` (39,772,160 B, SHA `76e504d8f26ba7b01cb97bb9741efb158b15f4324d8db5ea094866d9a4884d7c`); one literal VA-pointer search in `.rdata` and `.data` also found zero. **Not proof unreachable**: indirect, chained-unwind and runtime-linked callers remain possible. Park this two-probe route.
- Source lane receipts (all exit0): `rre-rc66-snapshot-caller-exact-rel32-20261111-01`, `rre-rc66-snapshot-caller-literalptr-two-sections-20261111-01`, `rre-rc66-receiver-type2-fragments-20261111-01`, `rre-rc66-a40-writer-pdata-decode-20261111-01`, `rre-rc66-osvk-import-table-20261111-01`, `rre-rc66-osvk-iat-ff15-ff25-exact-20261111-01`, `rre-rc66-osvk-two-selected-getkeyboardstate-functions-20261111-01`, `rre-rc66-osvk-helper-7c21f0-single-pdata-20261111-01`, `rre-rc66-i-7c1ac0-trampoline-8byte-20261111-01`, `rre-rc66-laneg-ctor-caller-complete-20261111-01`, `rre-rc66-lanej-7c0200-complete-20261111-01`.
- Independent manager receipts (all exit0): `rre-rc66-manager-reset-independent-20261111-01`, `rre-rc66-manager-constructor-gate-independent-20261111-01`, `rre-rc66-manager-prologue-type7-independent-20261111-01`, `rre-rc66-manager-win32-import-mapvk-independent-20261111-01`, `rre-rc66-manager-getkeyboardstate-chain-independent-20261111-01`, `rre-rc66-manager-vkcopy-owner-independent-20261111-01`, `rre-rc66-manager-endtoend-wrapper-independent-20261111-01`, `rre-rc66-manager-type6-record-ctor-independent-20261111-01`, `rre-rc66-manager-type6-handler-conditional-inspection-20261111-01`, `rre-rc66-manager-osvk-branch-proof-20261111-01`.

**Ranked follow-ups:** (1) reproduce a current *read-only* physical-game RRECollector/SavedVariables keyboard-state correlation, separately authorized and host-bound, before claiming an observed input; (2) prove the active receiver's owner/activation and the specific movement/stop predicate consumers using only discriminating cross-references; (3) keep the +0xA40 nonzero writer and `0x7C0780` callsite searches parked unless new source evidence supplies a narrow discriminator. No live movement/stop proof exists yet.

