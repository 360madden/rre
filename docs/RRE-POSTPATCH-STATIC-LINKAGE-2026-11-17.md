# RRE postpatch static linkage and negative-writer checkpoints — 2026-11-17

**AMD-DESKTOP | 10:47–10:49 EST | Offline archived PE only.** Updated build `STABLE-1-1179-a-1256672`; exact archived executable SHA-256 `df954b798331e18359be62a31cc74b49fc3f50b87385ebb080a5448256322c01`. No live RIFT process, input, VM or addon touched. Read [current new-build gates](RRE-WA006-POSTPATCH-SOURCE-GATE-2026-11-17.md), [postupdate recovery](RIFT-POSTUPDATE-RECOVERY-2026-11-17.md).

## WA-006: `wrapper+0x08` writer is **still unresolved**

Batched bounded Capstone inspection of the **new archived PE** verified:

- Base ctor `0x13E9A10` clears EDI; `0x13E9A2B: mov [rcx+0x08],rdi` **zeros the wrapper's `+8` field**.
- `0x13E9A62` and `0x13E9A88: mov [rax+8],rbx` store a wrapper backreference in **different, newly allocated 16-byte adapter objects**, not the wrapper's parent field.
- Apparent `[rbx+8]` and `[rdi+8]` writes at `0x6A695D`/`0x6A6970` occur **before** the 0x68-byte wrapper allocation (`0x6A6974–0x6A6979`), not to the wrapper.
- Callback calls wrapper ctor at `0x6A6986`, then stores the returned wrapper pointer in RDI (`0x6A698B`), publishes it **twice to the same** RIP-relative global RVA `0x3373C58` (`0x6A6992`/`0x6A69A1`), and dispatches the wrapper method at `0x6A69DC`. **No post-constructor wrapper+8 store was verified in this direct callback slice**.
- Wrapper method `0xF7CCF0` saves receiver to RSI at `0xF7CD27`; passes it to helper `0x13E9F90` via `0xF7CD6C`/`0xF7CDCE`. Helper `0x13E9F96` reads `[rcx+8]`, **not a writer**.
- `[r14+8]` at `0xF7CE02` and `[r15+8]` at `0xF7CE40` are 32-bit output-coordinate writes, not wrapper owner writes.

A separate read-only RIP-relative access scan found **72 candidate instruction-form references** to that shared RVA across multiple callback clusters. At least callbacks around `0x4A2997/0x4A29A6` and `0xF7DD84/0xF7DD98` publish wrappers made by the same `0xF7CC20` constructor. Those 72 references are **not** 72 verified wrapper owners or setters; provenance and true instruction boundaries remain to be qualified (`rre-child-alias-global-xrefs-1117-1`, `rre-child-alias-windows-1117-1`, `rre-child-alias-methods-1117-1`, all exit 0).

**Correct conclusion:** verified **zero initialization** and reader; **no nonzero parent/owner writer qualified** in examined paths. This does **not** rule out setters via aliases, indirect calls, other object lifetimes or unseen paths. It is invalid to promote `wrapper+8` into a confirmed gameplay owner simply because some instructions elsewhere write `+8`.

Independent bounded jobs (exit 0): `rre-child-wa006-w8-ctor-disasm-1117-1`, `rre-child-wa006-w8-callback-local-1117-1`, `rre-child-wa006-w8-wrapper-local-1117-1`. Coordinator independently read the mapped bytes at the five key RVAs in `rre-postpatch-wa006-writer-hex-read-1117-1` and confirmed the 0x68 allocation plus duplicate same-global publication in `rre-postpatch-wa006-global-correction-hex-1117-1` (both exit 0).

## ROOT001 adapter B: constructor/container and selector/dispatch are separate **static** links

- Constructor `0xFC9170` has one direct `E8` callsite `0x778C0E` among **803,811 scanned candidate E8 instructions** (bounded source analysis). Its caller allocates a candidate `0xA8`-byte object at `0x778BE9`/`0x778BEE`, constructs it, then at `0x778C3D–0x778C63` resolves and publishes the object to a slot associated with `host+0x240` (through `0x75DE60`). Specifically, `0x778C56` obtains an entry from the `host+0x240` container and `0x778C63` stores B in the returned node's value field (`node+0x30`, derived via helper `0x75DE60`).
- Separate selector writer at `0x77679A` stores a non-null virtual-method selection to `host+0x218`; the source is the host's method `[host_vptr+0xB8]` invoked at `0x776740` with `RDX=host+0x1F8`. The prior selection is checked near `0x776670`; a previous non-null selected object receives virtual `+0x20` at `0x7766EA` before reselection.
- Dispatcher `0x77A158–0x77A182` reads `host+0x218`, forwards the saved host via RDX, calls selected object's vptr `+0x18`. The B candidate vptr `0x2721518` has `+0x18 → 0xFCA0A0`; its code's source checks are pinned by `tools/verify_postpatch_root001_b.py`.

**Correct conclusion:** static object construction/publication and selector/dispatch subchains are supported; **the B object being selected and any actual shared live host identity are NOT proven**. The key missing edge is whether `host_vptr+0xB8` retrieves the constructed B object from the `host+0x240` container given the distinct `host+0x1F8` selection input and object lifetime. Do not equate the container's `node+0x30` B pointer to the selector's return without evidence.

Independent bounded jobs (exit 0): `rre-b-vptr-ctor-caller-xref-1117-1`, `rre-b-vptr-caller-host-constructor-disasm-1117-1`, `rre-b-vptr-hostslot-setter-disasm-1117-1`, `rre-b-vptr-caller-disasm-bounded-1117-1`. Coordinator independently re-read exact opcode bytes and confirmed direct call `0x778C0E → 0xFC9170`: `rre-postpatch-b-ctor-selection-bytecheck-1117-1` (exit 0).

## Next bounded evidence targets

1. **P0 — WA-006 nonzero writer or negative path:** Trace aliases of the published wrapper and its virtual methods to find a post-construction `+0x08` writer; qualify source and lifetime, do not infer from unrelated `+8` stores. Autonomous offline.
2. **P1 — ROOT001 selected-object linkage:** Resolve `host_vptr+0xB8`, `host+0x240` container selection and `host+0x218` slot update; prove or refute direct B identity. Autonomous offline.
3. **P2 — Physical game observation only if offline evidence narrows the exact unknown:** coordinate with RR2/current owner, verify PID/start/executable/module and same epoch; Lua self/target identity must agree before any game-facing offset use. Requires Joey's task-specific live approval.

All native compatibility remains **runtime-unqualified**. Preserve old-build SHA pins and RC-30/RC-88 user-stopped tasks.
