# RRE updated-client recovery: keyed selector, B state drift and WA-006 alias audit — 2026-11-17

**AMD-DESKTOP | source-only archived executable research | November 17, 2026, ~13:35–13:45 EST.** Independently confirmed named Workbridge host/version and clean tracked RRE `main` at entry. No RIFT game process, input, reload, memory, VM or sibling-repository changes. This is a continuation of [the 11:40 EST handoff](RRE-POSTUPDATE-HANDOFF-2026-11-17-1140-EST.md) and [static linkage checkpoint](RRE-POSTPATCH-STATIC-LINKAGE-2026-11-17.md).

## Exact build provenance

- Pre-patch: `STABLE-1-1177-a-1256632`, 60,493,640 bytes, SHA256 `1935a05c9db6d468e34e0055014a4a99c1b5afceb1695884e24600f5c20a4be8`.
- Post-patch: `STABLE-1-1179-a-1256672`, 60,574,536 bytes, SHA256 `df954b798331e18359be62a31cc74b49fc3f50b87385ebb080a5448256322c01`.
- Sibling `C:\work\Update Helper\PATCH_EVIDENCE_2026-11-17.md` is a separate read-only corroboration: 7 changed-content game files including executable, 2 removed download records, 0 added, 265 unchanged. Its repository owns only the before/after recorder, not RRE source fixes.

## ROOT001 B: newly verified patch changes, not just RVA relocation

Two independent byte/disassembly analyses compared aligned **865-instruction** B adapter windows. The new aligned window is **6 bytes longer** due to two larger OR immediates. **Exactly six operand-structure instructions differed** in the examined window:

| Operation | Old RVA / operand | New RVA / operand |
|---|---|---|
| first state test | `0xFCAA6F: cmp [rax+0x20],1` | `0xFCAA3F: cmp [rax+0x18],1` |
| first mark flags | `0xFCAA75: or dword [rax+0x10],1` | `0xFCAA45: or dword [rax+0x10],0x80` |
| first state set | `0xFCAA79: mov dword [rax+0x20],1` | `0xFCAA4C: mov dword [rax+0x18],1` |
| second state test | `0xFCAAA8: cmp [rax+0x20],0` | `0xFCAA7B: cmp [rax+0x18],0` |
| second mark flags | `0xFCAAAE: or dword [rax+0x10],1` | `0xFCAA81: or dword [rax+0x10],0x80` |
| second state set | `0xFCAAB2: mov [rax+0x20],ebx` | `0xFCAA88: mov [rax+0x18],ebx` |

Exact old/new bytes for first OR `83481001` → `81481080000000`, first state MOV `c7402001000000` → `c7401801000000`, second MOV `895820` → `895818` were independently decoded and corroborated. **Meaning of RAX object, state flag and runtime effect remains unknown; do not label +0x18 a universal new field or claim a live fix.**

P2 jobs exit 0: `rre-postpatch-p2-six-window-structure-venv-1117-1`, `rre-postpatch-p2-b-adapter-diff-1117-1`, `rre-postpatch-p2-operand-structural-diff-1117-1`, `rre-postpatch-p2-opcode-confirm-1117-1`; independent check `rre-child-bdiff-opcode-crosscheck-1117-1`, `rre-child-bdiff-branchcontext-1117-1` (exit 0).

**Further bounded P1 provenance:** In both changed B branches, `0xFCAA30/0xFCAA6C` pass `&[rsp+0x58]` to helper `0x1C1AE90`; `0xFCAA3A/0xFCAA76` load RAX from that output. The helper releases prior slot, allocates **0xA0 bytes** through `0x126EB58`, invokes constructor `0x1C10390`, publishes object through the output slot and increments its refcount at +8. Constructor vptr RVA `0x2A293E8` initializes +8 reference count and **+0x10 flags to zero**, and initializes a 0x18-byte region beginning at **+0x18** from zero-filled template RVA `0x3116A68` through `0x2511EF9`. This supports these exact field accesses on a fresh 0xA0-byte state object, but does **not** establish its named type, flag `0x80` semantics or runtime effect. Jobs `rre-p1-flag80-context-disasm-1117-1`, `rre-p1-flag80-slotproducer-disasm-1117-1`, `rre-p1-flag80-a0-ctor-disasm-1117-1`, `rre-p1-flag80-state-template-1117-1`, exit 0.

## ROOT001 B: state registry key discovery and remaining selector gap

- Exact RIP-relative LEA `0x778C29` bytes `48 8D 15 A0 D3 F3 01` resolves to RVA `0x26B5FD0`, exact ASCII `InGame\0` (`49 6E 47 61 6D 65 00`). The new-build constructor at `0x778C0E` creates B; `0x778C63` bytes `48 89 08` stores B to the keyed host+0x240 registry node+0x30. Previous registration at `0x778B9E` resolves to distinct `ConnectedToGame\0` RVA `0x26CE028`.
- Generic map insertion `0x75AB30` hashes SSO string keys using FNV-1a 64-bit constants (basis at `0x75AB60`, prime at `0x75AB72`). Separate state setter `0x77DC50` copies an incoming SSO string into `host+0x1F8` via `0x4AE4B0` at `0x77DC71`. Selection at `0x776740`, bytes `ff90b8000000`, calls `host_vptr+0xB8` and stores its nonnull return to `host+0x218`; dispatcher then invokes selected virtual +0x18.
- **Still not proven:** the concrete host +0xB8 method; whether the current state string equals `InGame`; whether it maps through the registry to the same B pointer and becomes the live selected receiver. Registration by name is not enough to accept identity.
- Bounded jobs (exit 0): `rre-agent-selector-branches-1117-b`, `rre-agent-selector-caller-key-1117-a`, `rre-agent-selector-registry-keys-1117-a`, `rre-agent-selector-pdata-bound-1117-a`, `rre-agent-selector-keyupdate-disasm-1117-a`, `rre-agent-selector-key-raw-independent-1117-a`, `rre-agent-selector-init-callers-1117-a`.
- Follow-up xref/constructor-boundary check identified `0x7781F0` as **adapter-registration routine**, called by `0x77244E` with the host pointer already passed from caller, not a host constructor. State setter `0x77DC50` writes the SSO state at host+0x1F8 and triggers reselection `0x776670` at `0x77DC98` when its guard allows. A targeted `.rdata` exact pointer scan found no direct entries for several investigated registration/selector helpers; **this is not evidence the host vtable is absent**. The concrete host +0xB8 implementation remains unresolved. Bounded jobs `rre-child-selector-impl-ctor-windows-1117-1`, `rre-child-selector-host-init-window-1117-1`, `rre-child-selector-host-vptr-rdata-xrefs-1117-1`, exit 0.

## WA-006: source structure and owner-negative refinement

- Old/new WA-006 callback (142 instructions), wrapper method (144), base ctor (40) and helper (11) have matching normalized operand structure in bounded comparisons, despite RVA/rel32/RIP changes. Wrapper ctor (49) includes **one changed immediate/tag**: old `0xF7CC65 mov edx,0xA40FE1CA`, bytes `bacae10fa4` → new `0xF7CC35 mov edx,0x91B4EAE3`, bytes `bae3eab491`. Tag identity/semantics **unproven**. Jobs `rre-postpatch-p2-wa-ctor-tag-confirm-1117-1`, `rre-postpatch-p2-operand-structural-diff-1117-1`, exit 0.
- Wrapper constructor LEA at `0xF7CC2E` installs vptr `0x271E468` into `[rbx]` at `0xF7CC3F`. **Another vtable begins at `0x271E470`**, established by separate RIP-LEA constructor references `0xF7D735`, `0xF7D9EC`, `0xF7DACA`, `0xF7DBAA`, `0xF835A4`. A tentative `0x78D920` 32-bit `[rcx+8]=0x7F7FFFEE` writer belongs to that adjacent table **and is rejected as evidence of wrapper+8 owner writing**.
- Bounded RIP-reference classification of shared `0x3373C58` global: **73 instruction-form candidates** (36 MOV loads, 36 MOV stores in 18 publication pairs, 1 CMP). Earlier 72 count omitted the CMP; this scan does **not** prove 73 owner paths. Original callback and two independently inspected callback clusters allocate a fresh 0x68-byte wrapper lazily via `0xF7CC20` and publish it twice to the shared global. Their apparent +8 stores target separately allocated adapters before wrapper allocation.
- **No qualified nonzero write to the same wrapper's +8 field.** Virtual ownership, player association and runtime result remain unresolved.

WA006 bounded jobs exit 0: `rre-wa006-p1-virtual-ctor-disasm-venv-1117-1`, `rre-wa006-p1-wrapper-vptr-array-1117-1`, `rre-wa006-p1-vptr-constructors-lea-xrefs-1117-1`, `rre-wa006-p1-global-owner-clusters-1117-1`, `rre-wa006-p1-global-roles-count-1117-1`. An initial system Python dependency failure was resolved by using RRE's existing virtual environment, without installing packages.

## Coordinator regression and source gates

All on AMD-DESKTOP, read-only and **re-run during this continuation**, exit **0**:

- `rre-postpatch-regression-b-1117-a`: initial **12/12** tests, before the new state-anchor guard.
- `rre-postpatch-regression-wa006-1117-a`: **13/13** tests.
- `rre-postpatch-regression-analyzer-1117-a`: **13/13** tests.
- `rre-postpatch-real-b-1117-a`: `SOURCE_PINNED_ONLY`, five opcode anchors, two vptr assignments, `runtimeQualified=false`, `functionIdentityQualified=false`.
- `rre-postpatch-real-wa006-1117-a`: `SOURCE_MAP_PINNED_ONLY`, seven windows and seven calls, `ownerQualified=false`, `runtimeQualified=false`.
- New six-operand fail-closed state guard added to `tools/verify_postpatch_root001_b.py`: checks two `cmp [rax+0x18]`, two `or [rax+0x10],0x80`, and two `[rax+0x18]` writes. `rre-postpatch-b-delta-opcode-six-read-1117-1` independently checked all exact source bytes (exit 0). The unit fixture mutates each operand to require rejection; the report remains `SOURCE_PINNED_ONLY`, not runtime accepted.
- `rre-postpatch-bstate-unit-green-1117-1`: **13/13** tests, exit 0 (includes mutation of every new state anchor). `rre-postpatch-bstate-real-green-1117-1`: real archived PE **11 total opcode checks** (five original + six new), exit 0, no runtime/instance qualification.
- `rre-postpatch-recovery-diffcheck-1117-a`: prior `git diff --check`, exit 0.

Do not upgrade SOURCE_PINNED results to runtime acceptance.

## Next bounded work

1. **P0 ROOT001 selector:** resolve host virtual `+0xB8` concrete implementation and prove which keyed registry entry is selected. Acceptance: exact source-to-selection object identity or a documented gap, independent second-method verification; offline/coordinator authorized.
2. **P1 B state delta:** RAX's 0xA0-byte allocation provenance is now traced; resolve constructor vtable `0x2A293E8` and other consumers of `0x80`. Acceptance: named type and flag meaning or explicitly scoped unknown. Offline/coordinator authorized.
3. **P1 WA006 owner:** find true same-instance `wrapper+8` nonzero writer, not adjacent-vtable or adapter writes; acceptance: exact writer + allocation lineage or bounded negative. Offline/coordinator authorized.
4. **P2 future guard:** B state anchors are now guarded; consider analogous exact WA006 constructor-tag regression only if useful after source/semantic interpretation. Acceptance: real-pass, deliberate mutation-fail tests without guessing gameplay semantics. Offline/coordinator authorized.

No live game action is requested by this report. Historical state and nine inherited untracked entries must be preserved.
