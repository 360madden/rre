# WA-006 — AMD-DESKTOP local tool coverage and Havok RTTI cross-check

**Date:** 2026-11-16 ~04:52 EST. **Coordinator:** sole RRE Manager.
**Evidence tier:** exact-current-build on-disk static source; **WA-006 / WA-007 remain blocked**.
**Host:** independently verified AMD-DESKTOP (manager job `rre_20261116_inv_host_001`, exit 0; Workbridge 0.16.5-dev). **Repository:** `C:\work\rre`. Starting main HEAD `d391c7d1b42d26fa7bbe3f2889fc21c4730a2405` (ahead 46; tracked clean; 9 inherited untracked paths preserved). No VM/game/process/debugger attachment, UI/input, installed-addon change, provider invocation, full import or remote push.

## 1. Native tool coverage — actual execution distinguished from installation

| Tool | Verified on AMD-DESKTOP | Actual execution / limitation |
| --- | --- | --- |
| RRE Python venv | Python 3.14.6, Capstone 5.0.9, pefile 2024.8.26 | Capstone decoded `48 8B 07` to `mov rax,qword ptr [rdi]`; smoke `rre_20261116_inventory_venv_smoke_02`, exit 0 |
| REA | Package version 6.5.0 in `C:\work\tools\rea` | CLI `rea.mjs --help` executed successfully, `rre_20261116_inventory_rea_help_02`, exit 0; no analysis/import |
| Ghidra | Installation `C:\work\tools\ghidra_12.1.2_PUBLIC`; application.properties reports 12.1.2 | `analyzeHeadless.bat -help` reached launcher and printed usage, `rre_20261116_inventory_ghidra_help_ps_02`, exit 1 for invalid CLI arguments; **not an analysis test** |
| JDK | Temurin Java 21.0.11 | `java -version` executed by native toolchain doctor, `rre_20261116_inventory_native_doctor_02`, exit 0 |
| .NET SDK | 10.0.302 | Existing doctor executed SDK probe successfully |
| Node | 26.5.0 | Existing read-only native toolchain doctor executed, exit 0 |
| iced-x86 | Absent from checked RRE venv and global C:\Python314 environment | Not executed or silently installed; Capstone used instead |
| x64dbg | `C:\work\tools\x64dbg\release\x64\x64dbg.exe`, file version 0.0.2.5 | Located and hashed; **not launched or attached**. Debugger attach remains separately prohibited |
| ReClass.NET | Existing launcher located | Version/runtime and live-target use unverified |
| PowerShell | Windows PowerShell 5.1 executed | `pwsh.exe` was not found via PATH in this Workbridge command context |

Toolchain doctor is a dependency inventory, **not** a proof that REA/Ghidra can complete a fresh PE import. Both historical Ghidra full-import attempts exceeded 450s; `AGENTS.md` explicitly prohibits retry even if REA `analyze_function` appears narrowly targeted. The doctor's AMD `vmware-capable` route label is stale under the **November 10 physical-only/no-VM** directive.

## 2. Exact-build RTTI breakthrough — independent methods converge

**Source:** current AMD-DESKTOP on-disk `rift_x64.exe`, 60,493,640 bytes, SHA-256 `1935a05c9db6d468e34e0055014a4a99c1b5afceb1695884e24600f5c20a4be8`. These are **current-build RVAs**, not the historical 59,963,840-byte executable.

| RVA / original bytes | Source-qualified meaning |
| --- | --- |
| `0x278C978`: 8-byte SHA `c9fa33a2411748b7c1cbd8c610ae5d34a8ac646af32d1de192d152848ef38bb5` | Descriptor vtable[-8] is absolute VA `0x142DF1B10` |
| `0x278C980`: 64-byte SHA `dea4f646f9944c1acf36b364687f96ff2e5476e2414c19197247067f08d9606f` | Visitor descriptor table; virtual +0x08 -> selector `0xA2514` |
| `0x2DF1B10`: 24-byte SHA `25ae3c402885eac18647b6cfebe14a69cfabc5bf136ac816209054f009e11c64` | MSVC x64 Complete Object Locator, 6 dwords `[1,0,0,0x2F993C8,0x2DF1B38,0x2DF1B10]` (signature 1 and valid self RVA) |
| `0x2F993C8`: 100-byte SHA `847c0507e70e915ab0755fbf51aeaf7806ad903c02101790b97397a79c8422cb` | Type descriptor literal `.?AVhkpKdTreeCollidableRaycaster@@` |
| `0x2DF1B38`: 16-byte SHA `9c3cab62c6d750cbc4696e4fa2ea45b53b8fc66969b2e137594bbfb66ddac188` | Class hierarchy descriptor, 2 bases: self and `hkKdTreeCastCollector` |

Separate bounded original-byte inspection also verifies `0x8E74B` obtains this table and `0x8E75A` installs it in a **stack-local visitor**. It is **not** the candidate object's dynamic `[R8]` vptr. Other inspected neighbor RTTI types include `hkpKdTreeWorldLinearCaster` and `hkpKdTreeWorldManager` (some with multiple subobject vtables); no scene/gameplay owner is thereby established.

**Independent original-source witnesses:** `rre_20261116_ivtable_rtti_fullhash_07`, `rre_20261116_ivtable_rtti_hierarchy_06`, `rre_c40_child_rtti_corroborate_20261116_01`, `rre_c40_child_rtti_hierarchy_bound_20261116_01`, `rre_wa006_qa_rtti_witness_20261116_01`; all exit 0, no game access.

## 3. Persistent verification, controls, and source limits

New RRE-only verifier: `tools/agents/collision/verify_wa006_rtti.py` imports only existing `pefile` and existing PE/host constants. It independently validates five original SHA-pinned windows, the MSVC COL, self-relative RVA, type name, hierarchy and selector table slot. Three **in-memory semantic mutation controls** (COL signature, RTTI type name, hierarchy base count) must be rejected without relying on the outer PE SHA gate.

Run from `C:\work\rre`:
```powershell
& 'C:\work\rre\.venv\Scripts\python.exe' -B tools\agents\collision\verify_wa006_rtti.py
```

- First fresh run `rre_20261116_new_rtti_verifier_01` returned exit **2**: its initial Python source incorrectly encoded a literal backslash+zero instead of a NUL terminator. This was a verifier bug, not a source mismatch.
- Corrected using a byte `0` terminator; `rre_20261116_new_rtti_verifier_fix_02` exit **0**, exact class, all five hashes, **3** negative controls.
- Independent full source gate previously rechecked: candidate-pointer verifier 21 anchors/2 mutations, current query 9 windows/1036 instructions, seven original Lua snapshots/24 source SHA pins, plus six additional branch-byte mutation rejections; QA jobs `rre_wa006_qa_ptr_20261116_01`, `rre_wa006_qa_current_20261116_01`, `rre_wa006_qa_matrix_20261116_01`, `rre_wa006_qa_selector_mutations_20261116_01`, all exit 0.
- **Static proof does not identify** candidate-object `[R8]` class, virtual `+0x40` callee, wrapper result `+0x60`, native hit/miss, real collision shape, gameplay unit owner, same-scene nonself correlation or restart invalidation.

## 4. Decision and ranked next work

1. **P0 (bounded offline):** Trace actual kd-tree candidate-record creation or a different concrete virtual-dispatch source; park repeated wrapper/producer/selector windows after two non-decision-changing probes. The stack visitor RTTI is **not** an owner proof.
2. **P1 (separate authority):** Capture two independent nonself addon/API IDs and native keys in the **same** verified physical client epoch, with host/build/scene/source receipt; do not combine PID 18092 and PID 51524 historical evidence.
3. **P2 (separate authority):** Only after P1, collect one actual hit/miss vs obstacle with independent shape/owner and camera landmarks plus scene/restart invalidation. No acceptance of WA-006/WA-007 until their respective gates pass.

**Preservation:** no Workbridge files outside RRE edited, no VMware even read-only, no RIFT process/UI, no x64dbg attach, no imports, no FreeBuff/Ollama, no push. This is an accepted **static RTTI identification** only.

## 5. 05:16 EST independent QA hardening — inheritance and false-vptr prevention

A fresh read-only QA lane found that the initial 5-window verifier emitted the `hkKdTreeCastCollector` inheritance name without itself checking its original base-descriptor bytes. The manager independently inspected the exact-source PE (`rre_20261116_manager_rtti_base_descriptors_03` and minimal name `rre_20261116_manager_rtti_base_name_minimal_04`, both exit **0**) and extended that same verifier, rather than creating another disposable scan.

New SHA-pinned static windows now include:

| RVA / size | Exact SHA-256 | Meaning |
| --- | --- | --- |
| `0x2DF1B50` / 8 | `0e26c371e1003883a23a75825b5b59d0acbe6601f9f9db729623f9c56ae80fda` | MSVC class-hierarchy base array: `[0x2DF1B68,0x2DF1AE8]` |
| `0x2DF1B68` / 28 | `62d9f3397726503004f702bd8d66fd04127bfc0f4fb5c79c212eda4754fe1796` | Raycaster self BaseClassDescriptor, type `0x2F993C8`, contained bases 1 |
| `0x2DF1AE8` / 28 | `02684a6e507258f6894e73d60da8c6937346156b4866b4329187445bfd6a6225` | Collector base BaseClassDescriptor, type `0x2F99398`, contained bases 0 |
| `0x2F99398` / 44 | `f1fec0515dad5d06f7413b0da2f89003ae90244eab3c053d409c5096e093b4b2` | Original type name `.?AVhkKdTreeCastCollector@@` |

The persistent `verify_wa006_rtti.py` now checks **9 original RTTI windows**, both descriptor structures (including PMD and attributes), base array and type names, with **7 RAM-only semantic mutation rejections**. Test `rre_20261116_manager_rtti_9windows_7mutations_test_01` exit **0**. Independent QA `rre_20261116_qa_extra_rtti_base_03` also exit0 and independently confirms the visitor vtable assignment is to stack-local `[rsp+0x30]`.

**Important negative owner result:** bounded adjacent RTTI probes `rre_20261116_c40class_probe1_adjacentrtti_0517` and `rre_20261116_c40class_probe2_postvisitor_0523` both exit0 but find **no source binding** from any nearby Havok class to the dynamic candidate `[R8]` vptr. `hkKdTreeCastCollector` table at `0x278C958` ends before the **next** COL at `0x278C978`; a naive collector `+0x40` read crosses into the visitor's table. `hkpKdTreeWorldManager` subobject tables do not have demonstrated `+0x40` slots; `hkpKdTreeWorldLinearCaster` apparent `+0x40` is non-code ASCII-like data. **Do not identify the candidate class from neighboring virtual-table addresses.** The separate query verifier's diagnostic now explicitly says *stack visitor vtable*, with a clarifying role field; its 9-window/1,036-instruction gate still passes (`rre_20261116_manager_query_verifier_vptr_label_test_01`, exit0).

**REA/Ghidra reuse check:** existing full-import sessions `navigation-20261018-01` and `-02` timed out after ~450.7s on the *older* executable SHA `7c356c9d...`, with empty analysis snapshots. Saved Ghidra project search (bounded locations) found no current-build persistent `.gpr/.rep` project (`rre_20261116_ghidrareuse_bounded_projectscan_01`, exit0). Synthetic PE provider analysis uses ephemeral projects and may reimport the original binary on the next query. REA `analyze_function` is **not** safe for the current full PE under `AGENTS.md`; no such import was initiated.

**Gate remains blocked:** these improve exact-source reproducibility and prevent a false collision-owner assignment. They do not prove dynamic `+0x40` callee, hit/miss, shape, two independent same-epoch nonself IDs, camera calibration or scene/restart invalidation.
