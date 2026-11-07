# SC-604 — fallback lookup key provenance from castbar producer (November 7, 2026, ~01:23 EST)

**Owner:** single RRE manager. **Scope:** bounded static analysis of the original physical-PC RIFT executable. **Verdict:** qualified *static input-value chain*, not a proved ability ID, live path, queue mode or casting outcome. SC-604 stays interim.

## Exact source and independent checks

- Physical file: `C:\Program Files (x86)\Glyph\Games\RIFT\Live\rift_x64.exe`; **60,493,640 bytes**, SHA-256 **`1935a05c9db6d468e34e0055014a4a99c1b5afceb1695884e24600f5c20a4be8`**. SHA freshly matched on disk in the decoder and independent byte-verifier jobs. Addresses are **RVAs in this file only**, not live pointers or offsets for unqualified VM binaries.
- Workbridge read-only jobs: `rre_20261107_0126_sc604_keychain_decode_ro` (exit **0**, existing RRE venv Capstone/pefile), `rre_20261107_0128_sc604_consumer_key_decode_ro` (exit **0**, independently selected consumer neighborhood) and `rre_20261107_0131_sc604_keychain_stdlib_verify_ro` (exit **0**, Python 3.14 standard library only). All outputs complete/untruncated; **22 exact RVA byte anchors**, **4 rel32 direct-call destinations** and a deliberately **misaligned byte negative control** passed. The second method independently verifies bytes, call encodings and stack-offset arithmetic; it does **not** independently prove all exceptional flows.
- This builds on the already qualified [consumer-gate path](REA-RIFT-SPELLCASTING-SC604-ABILITYNEW-CONSUMER-GATES-2026-11-06.md), [dual-route predicate](REA-RIFT-SPELLCASTING-SC604-PREDICATE-49FAB0-2026-11-06.md), and [fallback helper](REA-RIFT-SPELLCASTING-SC604-FALLBACK-5AF690-2026-11-07.md). No helper was broadly rescanned or imported.

## New input-value chain — exact-build static instructions

| RVA | Instruction / call | Direct consequence |
| --- | --- | --- |
| `0x9B8767` → `0x9B876E` | `mov ecx,[rsp+0xA0]`; `call 0x49FA20` | Reads the previously established consumer-B output-buffer `+0x40` DWORD and forwards it as the wrapper's first argument. |
| `0x49FA26`, `0x49FA6C`, `0x49FA6E` | `mov ebx,ecx`; `mov ecx,ebx`; `call 0x49FAB0` | Wrapper retains the incoming DWORD and passes it to the predicate, subject to its earlier nonnull/intermediate gate. |
| `0x49FAE2`, `0x49FC32`–`0x49FC38` | `mov r15d,ecx`; `mov edx,r15d`; `mov rcx,rdi`; `call 0x5AF690` | Predicate retains that DWORD and forwards it as the fallback helper's second argument after the failed six-reference path and pointer/table guards. |
| `0x5AF690`, `0x5AF694`, `0x5AF695`, `0x5AF6A3`, `0x5AF6AD` | `mov [rsp+0x10],edx`; `push rbx`; `sub rsp,0x40`; `lea r8,[rsp+0x58]`; `call 0x58C790` | The helper's third argument is a pointer to the **same saved incoming DWORD**, not a separately sourced hash/key. At entry `rsp=S`, the stored value is at `S+0x10`; after push/sub, `rsp=S-0x48` and `rsp+0x58=S+0x10`. |
| `0x58C7AE`, `0x58C7B9`, `0x58C7FD`–`0x58C800`, `0x58C811`–`0x58C814` | `mov r14,r8`; `mov ecx,[r8]`; `mov ecx,[r14]` / `cmp [r8+8],ecx`; `mov ecx,[r14]` / `cmp [rax+8],ecx` | The subordinate lookup consumes the forwarded DWORD both before its indexed/hash-style operation and in candidate entry equality checks. Its `r8` at `0x58C800` is a candidate pointer, distinct from the original third-argument `r8` retained as `r14`. |

All four direct calls above matched their **encoded signed rel32 targets**, not merely disassembler labels: `0x9B876E→0x49FA20`, `0x49FA6E→0x49FAB0`, `0x49FC38→0x5AF690`, `0x5AF6AD→0x58C790`.

**New narrow conclusion:** On the fallback path, the candidate castbar `abilityNew`-related DWORD from producer output `+0x40` is the exact DWORD **used as the subordinate candidate-comparison input**. That is stronger than calling it an unknown independent lookup key, but it **does not classify the DWORD's semantics**. The fallback is bypassed by a positive six-reference comparison and can fail earlier pointer checks. Other paths, callee side effects, any runtime traversal and the actual Lua assignment remain subject to their prior qualifications.

## Proof ceiling and next decisions

This analysis does **not** establish a learned/usable or Legendary/Protector's Fury ID; the source of all six reference globals; dynamic return value; a server-accepted action; an accurate channel/remaining/expired timestamp; or the numeric queue/GCD mapping. **SC-103 and SC-306 remain blocked**, **SC-604 remains an accepted interim mechanism**. Strict **RC-30 same-trial Pin→Undo→Reload UI** and version-matched archival proof remains incomplete even though physical **v0.4.11** package/load/persisted-version evidence has been recorded separately; **RC-32** live Retry remains unverified.

**Next genuinely new static discriminator only:** inspect one of the six-reference globals' producer/initializer provenance from the same exact build, or stop this branch if no bounded source-discriminating evidence exists. Do **not** repeat this key chain, the helper `0x58C790`, parked searches, or general native imports. No game input, reload, process manipulation, installed-addon edit, SavedVariables write, desktop-quarantine bypass, cross-project write or push occurred.
