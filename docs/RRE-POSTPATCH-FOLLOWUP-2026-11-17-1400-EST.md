# RRE postpatch continuation — host selector, state bitmask and WA006 key

**November 17, 2026 | ~13:54–14:00 EST | AMD-DESKTOP.** Source-only analysis against SHA256-pinned archived post-update `rift_x64.exe` (`df954b798331e18359be62a31cc74b49fc3f50b87385ebb080a5448256322c01`, `STABLE-1-1179-a-1256672`). Named AMD-DESKTOP Workbridge 0.16.5-dev, `C:\work\rre`. No gameplay, UI, process/memory, VMware, sibling repo writes, or Ghidra full import. This builds on [prior recovery evidence](RRE-POSTPATCH-RECOVERY-SITREP-2026-11-17-1340-EST.md) and [handoff](RRE-POSTUPDATE-HANDOFF-2026-11-17-1140-EST.md).

## Verified regression checkpoint

Coordinator re-ran actual source gates and tests, all **exit 0**, against the current archived executable:

- `rre-1117-continue-b-unit`: ROOT001 B **13/13** tests.
- `rre-1117-continue-wa-unit`: WA006 **13/13** tests.
- `rre-1117-continue-analyzer-unit`: update analyzer **13/13** tests.
- `rre-1117-continue-b-real`: `SOURCE_PINNED_ONLY`, five original + six new state-delta opcode anchors, two candidate vptr assignments; `functionIdentityQualified=false`, `runtimeQualified=false`.
- `rre-1117-continue-wa-real`: `SOURCE_MAP_PINNED_ONLY`, seven pinned windows + seven direct calls; `ownerQualified=false`, `runtimeQualified=false`.
- `rre-1117-continue-head-verify`: start HEAD `67194c7088300492f677eafe7e561ef3502fb1ec`, tracked clean and equal remote at entry; nine historical untracked items preserved.

## ROOT001 B: state object has generic 32-bit bitmask methods

The known B path `0xFCAA3F/0xFCAA45/0xFCAA4C` works on the fresh 0xA0-byte reference-counted state object built at `0x1C10390`, vptr RVA `0x2A293E8`. Independent bounded new-build Capstone analysis confirms the following virtual methods:

| Virtual offset | Function RVA | Verified operation |
| --- | --- | --- |
| `+0x08` | `0x17097D0` | `mov eax,[rcx+0x10]`, `bt eax,edx`, `setb al`; arbitrary bit test |
| `+0x18` | `0xF45AD0` | `bts/btr eax,edx`, gated by `R8B`; arbitrary bit set/clear |
| `+0x20` | `0x1709720` | Serializes the four bytes of `+0x10` mask and zeroes remaining output bytes |
| `+0x28` | `0x1718890` | Reconstructs flags from four input bytes while preserving bit 31 |

Thus `OR dword [rax+0x10],0x80` in the new B path **sets bit 7 of this 32-bit mask**. Its game-domain meaning, class name and runtime behavior remain **unknown**. Proven by `rre-p1-state-vtbl-ctor-bounded-1117-next1`, `rre-p1-state-vtbl-rtti-functions-1117-next2`, `rre-p1-state-vtbl-flagops-second-1117-next3` (all exit0).

## ROOT001 host vptr: bounded lookup still incomplete

- State setter `0x77DC50` copies incoming SSO state to `host+0x1F8` at `0x77DC71`, then calls reselection `0x776670` at `0x77DC98` under its guard.
- Selector at `0x776740` is a virtual `call qword ptr [rax+0xB8]`; its nonnull return becomes `host+0x218`. This is separate from candidate B registered as key `InGame` in `host+0x240`.
- Large `0x76F520–0x772BF4` routine saves the host RCX at `0x76F525` to stack, reloads it from `[rsp+0xE00]` at `0x772446` and calls adapter-registration routine `0x7781F0` at `0x77244E`. A unique executable function pointer `0x14076F520` occurs at `.rdata` RVA `0x26CD008`, surrounded by table values `0x14075E720`, `0x140780120`, `0x14077A0B0`.
- **No concrete host vtable assignment/table start or +0xB8 implementation is proven.** A nearby function-pointer table is evidence to investigate, not permission to declare an identity/slot offset. The B object selected under current `InGame` state is still unqualified.

Bounded jobs exit0: `rre-child-hostslot-parent-provenance-1117-a`, `rre-child-host-prologue-1117-a`, `rre-child-host-callsites-1117-a`, `rre-child-host-vtable-1117-a`, `rre-child-host-vtable-neighbors-1117-a`, `rre-child-hostvptr-windows-1117-a`.

## WA-006: changed constructor tag is a generated !hex key, not owner evidence

- Old constructor `0xF7CC50` passes immediate `0xA40FE1CA` to formatter `0x126EA44`; new constructor `0xF7CC20` passes `0x91B4EAE3` to `0x126EA14`.
- Formatter starts string with ASCII `!`, writes eight lower-case hex digits from right to left via nibble conversion and terminates NUL. Independent raw opcode + standard-library reproduction confirms old exact key **`!a40fe1ca\0`** (hex `21613430666531636100`) and new **`!91b4eae3\0`** (hex `21393162346561653300`).
- New constructor calls manager getter `0x893FC0`, then `0x1274D64` using address of formatted key. Callee determines the C-string length (`0x1294AAC`), calls `0x52DD00` to assign/copy the key bytes with NUL termination (not to hash them), and increments manager `[rsi+0x48]`. The paired wrapper destructor calls manager cleanup `0x1274968`, which decrements this count. This supports a **registration-lifecycle-like** path; exact manager domain, first-use callback semantics, and gameplay owner remain unqualified.
- Actual wrapper vptr at `0x271E468` points to sole method/destructor `0xF7CC70`; the next QWORD begins a distinct adjacent vtable `0x271E470`. Base constructor `0x13E9A10` zeros `wrapper+8`; **no same-wrapper nonzero writer or live owner is verified**.

WA006 jobs exit0: `rre-child-wa006-vtable-true-shape-1117-1`, `rre-child-wa006-ctor-helper-calltargets-1117-1`, `rre-child-wa006-base-lifetime-1117-1`, `rre-child-wa006-key-formatter-secondmethod-1117-1`, `rre-child-wa006-key-oldnew-calls-1117-1`.

## Next work (ranked)

1. **P0, autonomous offline:** identify exact host vptr assignment and virtual +0xB8 target, then prove or falsify `InGame` registry → B object selection. Acceptance: full concrete lookup path with independently checked opcodes.
2. **P1, autonomous offline:** follow users of state-object **bit 7** and the constructor vptr `0x2A293E8` to identify flag meaning. Acceptance: source-backed behavior/type, no speculative game label.
3. **P1, autonomous offline:** resolve WA006 key manager `0x1274D64 → 0x52DD00` and same-instance wrapper+8 writer. Acceptance: qualified key registration/owner path, or bounded negative with exact coverage.
4. **P2, task-specific Joey approval:** if source analysis cannot resolve runtime identity, design a separate physical-RIFT read-only observation with fresh host/build/process/window/current owner gates. Do not act on live RIFT solely because the source gates pass.

**Stop line:** no RRE postpatch runtime receiver or owner acceptance; do not treat static source equality as proof of gameplay compatibility.
