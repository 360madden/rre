# SC-604 — exact-build cast-producer caller/output disassembly (2026-11-06, 12:19 EST)

**Owner:** single RRE manager; bounded read-only native verification. **Status:** qualified static instruction *candidate* and caller-output layout; SC-604 remains INTERIM. This addendum extends the raw-encoding-only [earlier crosscheck](REA-RIFT-SPELLCASTING-SC604-CAST-PRODUCER-CROSSCHECK-2026-11-06.md), and does not replace the immutable SC-604 evidence graph.

## Source and method

- Original physical-PC `C:\Program Files (x86)\Glyph\Games\RIFT\Live\rift_x64.exe`: **60,493,640 bytes**, SHA-256 **`1935a05c9db6d468e34e0055014a4a99c1b5afceb1695884e24600f5c20a4be8`**, checked before both independent reads.
- Read-only RR2 research reference `C:\work\riftreader2\docs\reference\native-cast-owner-followup-2026-11-06.md`, SHA-256 **`ace7b578a9490f912f1140c3f57278da67ac5d2e99fd2eba3607c6d5d2fd8bee`**. The prior work supplied 13 target hypotheses; RRE did **not** invoke RR2's scanner, edit its repository or accept its helper-role labels as proved.
- RRE's **pre-existing** `.venv\Scripts\python.exe`, with installed `pefile` and `capstone`: map original PE `.text` using section raw offset/RVA; linearly decode exactly **[0x91DED0, 0x91E2B6)** starting at the independent exception-directory entry. This range is **998 bytes**, yielding **253 contiguous decoded instructions** ending precisely at `0x91E2B6`.
- Workbridge read-only jobs: `rre_20261106_1220_cast_linear_disasm_ro` (exit 0; 13 callsite alignment checks) and `rre_20261106_1221_cast_output_fields_ro` (exit 0; bounded instruction and branch audit), with `rre_20261106_1223_cast_cold_branch_ro` (exit 0; independent `.pdata` owner check). All outputs untruncated. No output artifacts or interpreter packages were installed.

## Results: stronger than raw opcode patterns, still not CFG proof

**13/13 previously verified `E8` byte patterns land at actual `call imm` instruction starts in this exact straight-line Capstone decode**, with decoded immediate destinations matching the prior list: `0x91DF13`, `0x91DF2D`, `0x91DF88`, `0x91DF92`, `0x91DFB0`, `0x91DFC9`, `0x91E093`, `0x91E0A4`, `0x91E0AB`, `0x91E148`, `0x91E154`, `0x91E1F1`, `0x91E20C`. All 42 decoded jump instructions target either a decoded instruction boundary within the range or a qualified external segment; **zero decoded intra-range branches target non-boundaries**.

The output argument is more concrete: at `0x91DEFD`, **`mov rdi, r8`** preserves the x64 third argument; `0x91DF08` initializes a word at `[r8]`, and `0x91DF0E` initializes byte `[r8+2]`. The following instructions write into the same saved pointer (`rdi`), including:

| Producer RVA | Decoded instruction / relation | Supported statement (not semantic label) |
| --- | --- | --- |
| `0x91DF85` | `mov dword ptr [rdi+0x3C], eax` | Copies a dword previously loaded from a source object at `[r15+0x2B8]`; object identity is not independently qualified. |
| `0x91E09C` | `mov byte ptr [rdi+0x38], al` | Copies low-byte result after call to `0x49F960`. |
| `0x91E0B3` | `movss dword ptr [rdi+0x30], xmm0` | Float-size write after mutually branched calls `0x49D440` / `0x49DFE0`. |
| `0x91E0CA` | `mov byte ptr [rdi], 1` | Conditional byte flag set; not proven to mean `isCasting`. |
| `0x91E0EA` | `movss dword ptr [rdi+0x28], xmm2` | Copies the branch-selected float loaded from source `+0x30` or `+0x34`. |
| `0x91E101` | `movss dword ptr [rdi+0x2C], xmm2` | Stores derived floating-point arithmetic. |
| `0x91E0F3`, `0x91E124`, `0x91E13F` | Initialize/update `[rdi+0x34]` | Stores `0x3F800000` (IEEE-754 1.0f) and conditional float updates. |
| `0x91E150` → `0x91E154` | `lea rcx,[rdi+8]` → `call 0x4948E0` | Passes output substructure as a *callee destination candidate*; callee effects unverified. |

The call to `0x5A6CB0` at `0x91DFC9` is followed by `mov rsi,[rax]` and `mov rbx,[rax+8]`, then a reference-management sequence. **Never invoke these helpers** to obtain telemetry: native side effects are possible. Values may be transformed, retained or branch-dependent.

**Critical unwind qualification:** `[0x91DED0,0x91E2B6)` is not the whole proven control-flow body. Eight decoded jumps target **`0x91E466` / `0x91E46B`**, outside that first unwind record. Original PE exception data independently assigns `[0x91E2B6,0x91E2F8)` to unwind RVA `0x2E49B9C` and `[0x91E2F8,0x91E4D9)` to `0x2E49BB0`; both external targets are in the latter range. Do not treat the end at `0x91E2B6` as function-wide termination.

## Gates and next discriminating step

This establishes instruction alignment and raw caller-output writes, **not** path feasibility, full CFG, native helper semantics, player/ability ownership, unit timebase, queue value, current/remaining/expired cast meaning, a successful cast, or marshaller consumption. Linear decoding can misinterpret embedded data and cannot prove all branches reach their targets dynamically; the consistent branch boundaries are supporting evidence only. **No `begin`, `duration`, `remaining`, `expired`, `channeled`, `ability`, `uninterruptible` or `isCasting` field is authorized from these offsets.**

The next *new* static step, coordinated with RR2's native research owner, is a bounded basic-block/def-use trace across the **three qualified unwind ranges** and the two known Lua castbar marshallers, verifying which of the caller-owned output fields they actually read. Avoid another literal/callsite scan, broad import or any passive live reader before that consumer-side qualification.

**Boundaries:** no RIFT input, reload, process control, debugger, installed-addon modification, SavedVariables mutation, desktop-quarantine override, external repository write, new dependency or native helper call. No new model reviewer was launched: the supported FreeBuff adapter accepts only already-exercised fixed review questions on unchanged evidence; Workbridge jobs are commands, not reasoning agents.
