# SC-611 — Word-keyed container helper at RVA 0x128E884

**November 7, 2026, 10:16 EST. Accepted bounded finding:** the next helper in the [SC-604 selector path](REA-RIFT-SPELLCASTING-SC604-SELECTOR-128D198-2026-11-07.md) implements **hashed-container lookup-or-create-shaped machinery**, not a directly returned spell-state enum. The local instructions read the referenced 16-bit key, derive a bucket location, select a prior or newly returned pointer, and return an output aggregate with a prior-null flag. The key's gameplay meaning and the stored payload remain unknown. This narrows the interpretation of SC-604; it does not finish its broader mechanism gate.

The [machine receipt](REA-RIFT-SPELLCASTING-SC611-SELECTOR-128E884-2026-11-07.json) retains the complete 272-byte function listing, source/original hashes, verification checks, job exits, fresh Lab-2 provenance and explicit limits. The task is SC-611 in the [casting register](REA-RIFT-SPELLCASTING-TASKS-2026-10-27.json), manager-owned documentation lane. Starting `main` was `92e739eed6f2ff198f543f05c981106b448ec02a`; nine historical untracked paths were preserved.

## Repository route and Lab-2 qualification

The [casting roadmap](REA-RIFT-SPELLCASTING-ROADMAP-2026-10-27.md), [M2 routing contract](REA-RIFT-SPELLCASTING-OFFLINE-TOOL-ROUTING-M2-2026-11-03.md) and preceding SC-604 handoff supplied the falsifiable question: **does this helper classify the selector, or consume it as a container key?** Existing exact-build static evidence is reusable after fresh Lab-2 qualification. No full REA/Ghidra import, debugger attach, injection, target execution or generic helper framework was needed.

At **2026-11-07T15:12:32.7439676Z**, the existing read-only VMware Tools route reported `RIFT-LAB-2`, RIFT PID **9752**, start UTC ticks **639294897826627677**, executable `C:\RIFT_TRANSFER\RIFT\rift_x64.exe`, **60,493,640 bytes**, SHA-256 **1935a05c9db6d468e34e0055014a4a99c1b5afceb1695884e24600f5c20a4be8**. The retained original guest executable from SC-610 was independently rehashed to that SHA. Temporary guest JSON cleanup was confirmed by exact path and hash. This is file/process provenance, not loaded-memory or continuous-call attestation.

The existing [external host VNC setup](REA-RIFT-LAB2-EXTERNAL-MOUSE-2026-11-07.md) captured a fresh original scene: Bolinao L43 in the game world, AFK, with RRECollector v0.4.11 / Known 54. Capture-only exited 0, with unchanged VM epoch, disconnect and mutex release. **No mouse movement/click, key, reload or casting input was sent.** The native controller remains intentionally stopped for external mode. A static helper question does not require an artificial live action.

## Direct original-byte observations

Existing `tools/inspect-navigation-static.py` reused the SHA-pinned RiftReader section/summary helper and installed pefile/Capstone, with **depth 0**. Original PE exception metadata identifies `0x128E884..0x128E994` (exclusive), file offset **0x128DC84**, length **272 bytes**, no unwind chain, complete window decoding and no queued recursion. Window SHA-256: **6399ce0f8b6755511049dcca2d671146d8ef6e0f555e4cc15c514b142fcfda32**.

| RVA | Established local flow | Interpretation limit |
| --- | --- | --- |
| `0x128E891..0x128E8AA` | Incoming R8 is preserved in RBP, RDX in RSI, RCX in RBX. The key pointer is passed onward as RDX to `0x126D838`. | These register roles are local; no recovered source signature or gameplay type. |
| `0x128E8B2..0x128E8C1` | Loads a pointer-like value from stack `+0x60`, tests it, records **whether it is zero** in R14B, and branches to `0x128E972` when nonzero. | The recorded boolean is a null-result flag, not independently a cast/queue/readiness flag. |
| `0x128E8C7..0x128E920` | Null-result path uses object fields `+0`, `+0x10`, `+0x18`, helper calls, a comparison and optional `0x128EB78` call. | Allocation/capacity-management interpretation is plausible; the callees were not recursively analyzed. |
| `0x128E925..0x128E92E` | `movzx ecx,word [rbp]`; EDX=`0x1F31D`; indirect call through IAT RVA **0x25F0880**. | Original import metadata binds that entry to **`ldiv`**, `api-ms-win-crt-utility-l1-1-0.dll`; it is not an unidentified game callback. |
| `0x128E934..0x128E965` | Splits the call result, multiplies by **0x41A7** and **0xB14**, subtracts, conditionally adjusts by **0x7FFFFFFF**, then uses `div [rdi]`. The remainder is multiplied by `[rbx+8]` and added to `[rbx]`. | This establishes key-derived bucket-address arithmetic. No runtime bucket count, key meaning or payload is observed. |
| `0x128E95D..0x128E970` | Passes the original key pointer and computed location to `0x1266AA8`, retaining its RAX result. | Insert/create semantics remain an inference from the full local shape; callee internals are unresolved. |
| `0x128E972..0x128E993` | Hit path uses a prior stack location. Both paths write `[out]=context`, `[out+8]=location`, `[out+0x10]=pointer`, `[out+0x18]=prior-null byte`; RAX becomes **out** and returns. | The return is the output-structure pointer, not a directly returned accepted-cast boolean or spell-class enum. |

The independently verified parent call at **0x128D2BD** targets this exact start. The earlier parent report supplies the selector-by-pointer connection; no broad caller scan or unverified pointer reuse was performed. Calls beyond this helper remain opaque. The six local call sites comprise five direct calls and the identified import; that does not characterize their descendants.

**Inference:** the whole local shape supports a word-keyed hashed-container lookup-or-create helper. **Directly proved:** key load, arithmetic, branches, call targets/import identity, output writes and return dataflow. **Unresolved:** which game entity the key identifies, actual runtime keys, container contents, caller's payload meaning, Legendary selection, queue policy and cast/server outcomes. No live traversal of this function was observed.

## Independent verification and stopping decision

The primary existing-tool command exited **0** locally in about eight seconds. An independent **Python 3.14 standard-library** verifier parsed the original PE sections, exception directory and import descriptor/thunk, checked selected instruction bytes, relative targets, output writes, the parent call and two negative controls. Workbridge job **`rre_20261107_sc611_independent_original_v1`** exited **0**, untruncated, **54/54 checks**, **two negative controls**; its recorded interval was 15:15:48.808Z–15:15:49.368Z.

This is independent raw-byte/metadata/edge verification, **not a second disassembler or decompilation**. The current RRE environment could not import iced-x86, despite the older M1 record having used it; no dependency was installed or prior decoder result transferred to this new function. Accordingly, acceptance is limited to the source-backed local flow above, with container semantics explicitly inferred.

Two attempted `command_run` dispatches were rejected before execution (long-command schema, then `COMMAND_NOT_CONFIGURED`). The primary ran through the existing local interpreter; the independent check used supported Workbridge `terminal_run` with literal argv. No timeout was treated as completion. FreeBuff capability check exited 0 but offers fixed older question modes, so no inappropriate model prompt was rerun; **zero new model agents and no Ollama**.

Stop here: the selector reference led to generic key/container mechanics rather than a new spell-state discriminator. Do not recurse through allocator/hash helpers merely because they are reachable. A useful reopening trigger is **new caller/payload value-flow or role-bound runtime evidence connecting this key or returned payload to a particular ability/state**. SC-103 and SC-306 remain blocked; broader SC-604, RC and navigation gates are unchanged. No live cast success is claimed.

Only the report, machine receipt, SC register and [current handoff](REA-RIFT-SPELLCASTING-SESSION-HANDOFF-2026-11-07.md) are integrated. Documentation validation covers source/artifact hashes, relative links, JSON, unchanged other task records, roadmap and diff checks; there is no tool/addon implementation change requiring the full historical test suite. Originals remain under `artifacts/lab2-sc611-20261107-1012/`.
