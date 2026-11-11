# RRE RC-72 — concrete registered listener, native event flags and type-3 producer link

**Host:** LEGION · **Time:** 2026-11-11 ~12:35 EST · **Method:** bounded read-only disassembly of original physical RIFT PE. **Status:** accepted source-qualified callback implementation; game movement, input meanings, active-player identity and physical result not proven.

## A. Registered 48-byte listener is a real native callback adapter

- The full original code region `[0x936950,0x937966)` contains `0x936CB0 mov ecx,0x30`, `0x936CB5 call 0x78E110` (allocation-like), `0x936CBA mov rbx,rax`. The non-null path builds the 48-byte listener. `0x936D03` saves it to `[r15+0x1B0]`, then gets root via `0x49A020`, receiver via `0x54F7C0`, and `0x936D1D call 0x7C1E20` passes **RCX=receiver, RDX=listener**. `R15` is the callback's owning object; no active-player/gameplay identity proven.
- Its outer listener vtable pointer `[listener+0x00]` is RVA **`0x26A79B8`** (from RIP-relative `0x936CE0`), with slots `+0=0x4E2B70`, **`+8=0x4E3210`** (receiver callback), `+0x10=0x4E2BE0` (outer predicate). Outer predicate `0x4E2BE0` reads byte `[listener+0x28]`. The constructor initializes this byte to zero using R14, proved zeroed at `0x93699C`; later state changes are not excluded.
- The same constructor embeds an inner adapter at `listener+0x08`: its vtable RVA **`0x26A3300`** is loaded by RIP-relative `0x936CC2` and stored at `[listener+8]` through an XMM copy. `listener+0x10` captures the owning-object pointer **R15**. `listener+0x18` contains the callback function pointer **`0x93B710`** (from `0x936CD1`, XMM copy at `0x936CFA`); `listener+0x20` is initially zero. These offsets describe the small adapter, not the receiver's list counters.
- The outer callback `[0x4E3210,0x4E3246)` calls inner vtable `+8` and, if AL nonzero, forwards the original record in RDX to inner vtable `+0x10`. Inner vtable slots: `+0=0x4951C0`, **`+8=0x497090`**, **`+0x10=0x494AE0`**.
- Inner predicate `0x497090` returns true iff `[inner+8]` (owner) and `[inner+0x10]` (callback function pointer) are both nonzero. The inner handler `0x494AE0` loads the callback pointer from `[inner+0x10]`, loads owner pointer from `[inner+8]` into RCX, then `jmp rax`. Therefore the callback **`0x93B710` receives RCX=R15 owner**, with the original incoming record in RDX. The owner-state fields discussed below are NOT fields of the 48-byte listener.

### Corrected RIP-relative address (critical review)

The first analysis accidentally described the inner table as RVA `0x26A9300`; exact instruction arithmetic says `0x936CC9 + 0x1D6C637 = 0x26A3300`. The mistaken address is UTF-16 data and must **never** be used as a callback vtable. Both independent agents and manager verified the correct table's actual code pointers before this RC-72 report.

## B. Callback 0x93B710 owns a five-flag native event-state machine

The callback begins at `0x93B710`, preserves owner in RBX (`0x93B718`), dispatches on `EAX=[record+0]`, and continues across two adjacent original `.pdata` regions. These are code **fragments of a cross-branch callback**, not three separate functions.

| Numeric type | Selected record field | Verified effect on R15 owning object |
|---|---|---|
| `1` | DWORD `record+0x120` | `1/2/4/8/16` select offsets `owner+0x1C0/1C1/1C2/1C3/1C4`; write byte `1` |
| `2` | DWORD `record+0x120` | Same selection; write byte `0` |
| `3` | DWORDs `record+0x128` and `record+0x12C` | Compare with `owner+0x1B8/+0x1BC`; save and, on differences, compute two scaled float results for `0x4BD9A0` |

**Precision:** For types1/2, subcodes outside `1/2/4/8/16` fall through to offset `owner+0x1C0`; this is NOT proof of strict key-code validation. The physical meanings of types/subcodes, which player they refer to, and whether flags affect turning/movement remain **unknown**. The `0x93B755` branch divides float-converted values by results from helper chain `0xFB4860` then `0xFAFAB0`, twice, before tail-jumping `0x4BD9A0`; caller-side scaled numbers are proven, not what that callee does.

## C. Exact type-3 producer → callback field match

The full type-3 producer `[0x7C0780,0x7C0909)` supplies precisely the fields the listener reads. Its stack alias matters: prologue `0x7C078B lea rbp,[rsp-0x70]` followed by `0x7C0790 sub rsp,0x170` establishes **RBP=RSP+0x100** at record emission; record base is `0x7C08DB lea rdx,[rsp+0x20]`.

1. From receiver fields `+0x30/+0x34`, the producer derives two sign-extended/truncated 16-bit integer values, including `movsx` conversions at `0x7C083C` and `0x7C0848`.
2. `0x7C085D mov [rbp+0x48],ecx` writes **record+0x128**; `0x7C084F mov [rbp+0x4C],eax` writes **record+0x12C**.
3. `0x7C07F7` writes numeric type `3` to the record, which is dispatched to `0x7C0480` at `0x7C08E3`.
4. Registered owner callback `0x93B724` reads record+0x128, `0x93B72B` reads record+0x12C, and `0x93B731/0x93B73A` compares against owner+0x1B8/+0x1BC. On changed path, `0x93B766/0x93B76D` saves them then computes and forwards scaled values.

Thus a complete **receiver-field → native record → registered listener → owning-object field** mapping is source-proven. The upstream source of receiver+0x30/+0x34, and the downstream effect of `0x4BD9A0`, are **not** yet qualified. Do not call these mouse coordinates, viewport dimensions, camera angles or player position absent supporting source.

## D. Exact original source receipts

Original PE path `C:\Program Files (x86)\Glyph\Games\RIFT\Live\rift_x64.exe`, size 60,493,640B, SHA-256 `1935a05c9db6d468e34e0055014a4a99c1b5afceb1695884e24600f5c20a4be8`, base `0x140000000`; all addresses below RVAs. Code rows have full linear byte decode across the named region; data rows are table bytes rather than instructions.

| Region `[begin,end)` | Bytes / instructions | SHA-256 |
|---|---:|---|
| `[0x936950,0x937966)` | 4,118 / 974 | `313d90e9458f9d789e04fd85f5e064ec9abfbdbda330ae9f183161c8b48d7aea` |
| `[0x936CB0,0x936D22)` | 114 / 27 | `6d2f7638326789c1755e7415f4805759c01eb4d1a367d477679085101764d87a` |
| **Data** `[0x26A79B8,0x26A79D0)` | 24B | `ff18b009b1d6824f82cb61389c0285c33fba3259fa2b791bfc252f4ddc47d09e` |
| **Data** `[0x26A3300,0x26A3328)` | 40B | `dea69830d02e25e66535ec1fd8814dd0bd127291a677c90e6d06afbb8a10d518` |
| `[0x4E3210,0x4E3246)` | 54 / 18 | `c71d6afccaa44cd8dbc4c9e3a329e61d1e28bff37b5037a1b406bb52b9df1577` |
| `[0x4E2BE0,0x4E2BE5)` | 5 / 2 | `bb387a300471d399f6b29027841df3c4a1f506542e32eac98101e1bb537b2486` |
| `[0x497090,0x4970A4)` | 20 / 8 | `72139e9caba53fadada204bc19b46d0cb4da8ff2ebdfc3a88b7cb7b4bcdcbcc8` |
| `[0x494AE0,0x494AEB)` | 11 / 3 | `5a917f02f2532cc34d87ce23934f7d9300f77107e2032a05b5cc1ddfe8921f5d` |
| `[0x93B710,0x93B755)` | 69 / 17 | `cc90debb4fd97122c9a16643272eddc42150e2a92e476b60765c3f7c974d5c06` |
| `[0x93B755,0x93B7BA)` | 101 / 23 | `826d832566908760f22ae15991e1678a133f87476fea617e34837447a6ef62ca` |
| `[0x93B7BA,0x93B8A3)` | 233 / 78 | `fca35ef7ad9ec79d61382490c59cd24d5e0430b877b554da5a7bfb2f63eefebe` |
| `[0x7C0780,0x7C0909)` | 393 / 106 | `a6fb7de6365dd92fd4f474fb7345391221f0a00881cea0d1f3d9986c873a60de` |
| `[0x4BD9A0,0x4BD9D0)` | first 48 / 11 only | `8f7dad264f178a720f37adb26cbbf759d77d05e727cc66d33403b56d73ac5f54` |

Manager independently verified key branch windows and both correct vtable pointers (`rre-rc72-manager-concrete-listener-ctor-wrapper-inner-vft-20261111-01`, `rre-rc72-manager-correct-inner-vtable-26a3300-20261111-01`, `rre-rc72-manager-inner-callback-leaf-bounded-20261111-01`, `rre-rc72-manager-inner-leaf-and-flag-origin-20261111-01`, `rre-rc72-manager-concrete-callback-93b710-source-20261111-01`, `rre-rc72-manager-type123-listener-state-windows-20261111-01`, `rre-rc72-manager-final-windows-source-validation-20261111-01`), all passed. A first `.pdata`-enclosing-method assumption failed for tiny leaves and was replaced by exact bounded byte disassembly. Read-only independent agent confirmations: `rre-rc72-lane-a-listener-936c-vtable-qacheck-20261111-01`, `rre-rc72-b-wrapper-leaf-minimal-sha-20261111-01`, `rre-rc72-lane-c-correct-inner-vtable-handler-20261111-01`, `rre-rc72-lane-a-callback-next-fragment-93b755-20261111-01`, `rre-rc72-b-type3-fallthrough-93b7ba-original-20261111-01`, `rre-rc72-lane-c-type3-producer-handler-reconcile-20261111-01`.

## E. Three next discriminating priorities

1. **Upstream source of receiver+0x30/+0x34**: one bounded caller/writer chain to native OS message fields. Do not assign screen/mouse semantics until proven.
2. **Downstream meaning of `0x4BD9A0`**: source-qualify what consumes the two scaled values; decide whether it affects UI, pointer/camera or player movement with evidence.
3. **A live position/input proof only when separately controlled**: verify physical RRECollector load, timestamped XYZ and key timeline. Neither native flags nor formulas alone prove character movement.

**Scope:** No live game input, process attachment, VM/AMD access, installers, unrelated repository edits or remote push. RRE docs only.
