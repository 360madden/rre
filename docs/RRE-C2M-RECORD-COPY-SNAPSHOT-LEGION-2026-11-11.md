# RC-65 — Native record-copy layouts, type-3 snapshot and type-2 reset (LEGION)

**Accepted static breakthroughs:** Two queue-copy helpers copy distinct packed record layouts with the same 256-byte body. One producer snapshots current receiver table bits into a new type-3 record; another source fragment dispatches type-2 records before clearing the same table. A focused search did not prove any writer of the lazy global root's +0x350 pointer. **No physical keyboard/device semantics or live movement is established.**

## Host and exact source

- Independently verified host LEGION, RRE `C:\work\rre`, main starting clean HEAD `6f39217d8b420708f20125770c46ee285dbed817`, 20 ahead of origin.
- Original physical `C:\Program Files (x86)\Glyph\Games\RIFT\Live\rift_x64.exe`, 60,493,640 B, SHA256 `1935a05c9db6d468e34e0055014a4a99c1b5afceb1695884e24600f5c20a4be8`, preferred image base `0x140000000`; all addresses are original-file RVAs. No AMD/VM/process/input/reload/installer/REA import/provider/remote push.
- Three real independent read-only agents, manager sole writer. One finite exact E8 scan per named target with two selected caller windows; one focused setter false-positive filter. Unresolved leads parked after bounded probes.

## Two exact native record-copy helpers

| Region | Bytes / instructions | SHA256 | Copied footprint |
|---|---:|---|---|
| Special `[0x7C0170,0x7C0200)` | 144 / 34 | `433e49ea215ef4da8a77483ba5833bd2fc9963f5439854bb539f51a55d41c034` | Through `+0x12D` (minimum 0x12E B) |
| General `[0x7C0290,0x7C0336)` | 166 / 38 | `80f0a2150de236b90c4fc443041e8832ff3358902c21b5bae0246c478067c189` | Through `+0x13B` (minimum 0x13C B) |

Both receive `RCX=destination`, `RDX=source`; copy initial dwords at +0/+4, qwords at +8/+0x10, byte at +0x18, and **exactly 256 bytes at +0x19..+0x118** through imported `VCRUNTIME140.dll!memcpy` at thunk `0x25047A9`; then copy trailing fields +0x120/+0x124/+0x128. Special copies byte +0x12C/+0x12D, general copies dwords +0x12C/+0x130/+0x134/+0x138. Both return destination pointer. **Neither helper itself advances queue pointers or allocates memory**; corresponding `0x130` and `0x140` queue strides are proven separately in RC-64 dispatcher, not from these helpers.

## First concrete record producers

One exact original .text direct E8-rel32 scan for dispatcher `0x7C0480` found **11 direct callsites in 5 .pdata regions**; these are not exhaustive of indirect dispatch. Two bounded selected regions were decoded:

| Region | Bytes / instructions | SHA256 |
|---|---:|---|
| Type-3 state snapshot `[0x7C0780,0x7C0909)` | 393 / 106 | `a6fb7de6365dd92fd4f474fb7345391221f0a00881cea0d1f3d9986c873a60de` |
| Type-2/reset fragment `[0x7C0A40,0x7C0BAA)` | 362 / 82 | `d10dd985a73f7e52f18352ad9362d397b65753f93fe69511b81be0fd512e41ee` |

**Type 3:** At `0x7C07F7` a stack record is marked type 3. At `0x7C0896..0x7C08A8`, `VCRUNTIME140.dll!memcpy` snapshots `receiver+0xA41` (256 B) into the stack record at `rsp+0x39`. Tests of the copied bytes' sign/high bit set mask bits in stack record `+0x04`:

| Indexed copied table byte | Record mask | Source |
|---|---:|---|
| Index `0x10` (`rsp+0x49`) | `0x02` | `0x7C08AD..0x7C08BB` |
| Index `0x12` (`rsp+0x4B`) | `0x01` | `0x7C08BF..0x7C08C9` |
| Index `0x11` (`rsp+0x4A`) | `0x04` | `0x7C08CD..0x7C08D7` |

Then `0x7C08DB..0x7C08E3` passes the stack record through `0x7C0480`. This is a **derived state snapshot**, not an independently observed physical key event.

**Type 2/reset:** A separate selected unwind region `0x7C0A40` contains stack-record type 2 initialization at `0x7C0A84`, `0x7C0AED`, `0x7C0B56`, calls to dispatcher `0x7C0480` at `0x7C0A9E`, `0x7C0B07`, `0x7C0B70`, and mask-conditional paths. At `0x7C0B75..0x7C0B84`, the confirmed `VCRUNTIME140.dll!memset` receives `RCX=receiver+0xA41`, `RDX=0`, `R8D=0x100` and **clears all 256 status bytes**, followed at `0x7C0B89` by `receiver+0x38=r15d` (source of R15 unresolved). The selected region is an unwind/epilog fragment, **not independently qualified as a standalone complete entry**. Do not infer upstream triggers from it.

PE import metadata independently identifies `0x25047A9` via IAT `0x25EFDF8` as `VCRUNTIME140.dll!memcpy` and `0x25047AF` via IAT `0x25EFE40` as `VCRUNTIME140.dll!memset`.

## The root+0x350 writer remains unproved (bounded negative)

An exact .text direct-call scan of lazy getter `0x49A020` yielded 3,845 raw hits; 107 had encoded `+0x350` within a 100-byte neighborhood. Instruction-level destination filtering left only three *syntactic* nearby writes:

- `0x4E09A7 mov [r14+0x350],eax`: in `[0x4E0920,0x4E17A9)` 3721B/871 instructions, SHA `3944be714c1d4db2311f2da359a69938b522f955dd6d46b2faa659d4a5a3db18`; `r14` is original entry `rcx`, **not** getter result.
- `0x928E7E mov [rsp+0x350],r13`: stack local, not root.
- `0xD64A11 mov [r15+0x350],0xffffffff`: in `[0xD64827,0xD64A7E)` 599B/149 instructions, SHA `22aae287174f249637c4a0c4a59d661fdebe05cf54581f8073e25456ed5a3b89`; no proven alias of `r15` to global root.

**Correct result:** No writer to **globalRoot+0x350** is proven by this focused proximity probe. It does not exclude alias-based or indirect setters elsewhere. Park this lead until a new discriminating owner reference is available.

## Verification receipts and next work

- Copy helpers lane `rre-rc65-queue-two-windows-20261111-01` exit0.
- Callsite/producer lane `rre-rc65-callsite-exact-7c0480-20261111-01`, `rre-rc65-callsite-two-selected-functions-20261111-01`, `rre-rc65-callsite-import-25047af-20261111-01` exit0.
- Owner negative lane `rre-rc65-receiver-writer-classify-20261111-01`, `rre-rc65-receiver-two-write-pdata-20261111-01`, `rre-rc65-receiver-two-candidate-alias-disasm-20261111-01` exit0.
- Independent manager `rre-rc65-manager-copy-helpers-independent-20261111-01`, `rre-rc65-manager-mask-records-independent-20261111-01`, `rre-rc65-manager-mask-fields-focused-20261111-01`, `rre-rc65-manager-owner-false-positives-independent-20261111-01` exit0. **Six original windows / 1,280 instructions** fully decoded and SHA matched, plus PE import metadata and focused source semantics.

Next priorities: (1) one source-linked entry above type-3 snapshot `0x7C0780` if it can discriminate origin; (2) do not repeat broad root+0x350 searches absent new alias evidence; (3) separately authorized physical RRECollector v0.4.19 SavedVariables / actual movement+stop observation. Everything here is static only.
