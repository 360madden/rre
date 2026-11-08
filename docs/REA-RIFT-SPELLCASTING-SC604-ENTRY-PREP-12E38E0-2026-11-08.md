# SC-604 — Indexed-entry preparation before selector replacement (2026-11-08)

**Owner:** single RRE manager. **Scope:** one bounded, static, read-only original-PE inspection; follow-up to [indexed-entry initialization](REA-RIFT-SPELLCASTING-SC604-SELECTOR-ENTRY-12E39D8-2026-11-08.md). The SC-604 mechanism is **interim**; no identified game object or successful spellcast follows from this report.

## Exact source and independent checks

- Original host RIFT `rift_x64.exe`: **60,493,640 bytes**, SHA-256 **`1935a05c9db6d468e34e0055014a4a99c1b5afceb1695884e24600f5c20a4be8`**; each successful job rehashed the entire original file and read only exact mapped `.text` bytes. This is not a fresh Lab-2 image/process identity check.
- Capstone 64-bit disassembly using existing RRE virtual environment: Workbridge job `rre_nov8_sc604_prep_helper_20261108_0722_a1`, exit **0**, 176-byte `0x12E38E0` window SHA-256 **`08c5aab8407dcaa946b538f695a6bc6e1ce7c524886e02db1d7dd023f296ca12`**, plus 80 bytes at `0x12E39D8`.
- Separate Python 3.14 standard-library PE mapper and direct opcode/relative-call verifier: `rre_nov8_sc604_prep_helper_stdlib_20261108_0722_b1`, exit **0**, **22 checks**, including two negative controls (wrong helper target and wrong cleared offset). It requires exact original bytes and rechecks the 176-byte SHA.
- An initial independent verifier `rre_nov8_sc604_prep_helper_stdlib_20261108_0722_a1` exited **1** due to its author's expected `31 c0` encoding for `xor eax,eax`; the actual bytes are `33 c0`. Read-only byte-discovery job `rre_nov8_sc604_prep_bytes_20261108_0722_a1` exited **0** and clarified the encoding before the successful corrected run. The initial failure is **not** a RIFT error and is not counted as a pass.

## Native observations (original PE only)

| RVA | Verified operation | Evidence boundary |
| --- | --- | --- |
| `0x12E39E8` | The indexed-entry writer at `0x12E39D8` calls preparation helper `0x12E38E0` **before** storing the incoming selector in entry `+0` and literal fields at `+0x24/+0x26`. | Order is static; branch occurrence/runtime table ownership unknown. |
| `0x12E38E9` | Preparation helper preserves `RCX` as `RBX`, then calls `0x12E3910`. | The subhelper examines flag bits, but flags' gameplay meaning is not identified. |
| `0x12E38EE–0x12E38F6` | Loads entry pointers `[RBX+0x30]` into `RDX` and `[RBX+0x10]` into `RCX`, then directly calls `0x12CB918`. | Callee's resource/ownership behavior remains unknown. |
| `0x12E38FB–0x12E390E` | Zeroes `EAX`, stores zero qwords to entry `+0x18`, `+0x30` and `+0x28`, then returns. | This is a static field reset, not proof of deallocation or execution in a live scene. |
| `0x12E3916–0x12E395A` | The preliminary helper reads a word at `+0x24`, tests mask `0x2460`, and contains guarded branches including an indirect `call RDX` after loading `[RBX+0x28]` and checking it nonzero. | An optional callback path is present. Its actual target, flags, conditions and invocation remain unqualified. |

**New bounded conclusion:** The selector-entry write is preceded by a **state-preparation/clearing path**, not simply a blind store. Conditional cleanup/callback logic exists in that path. This strengthens the structural native mechanism map but does **not** identify an ability ID, spellcasting, target acquisition, queue mode, selected Legendary power, engine entity, server action, or active runtime execution. Neither the unknown callee `0x12CB918` nor the indirect callback was recursively followed; defer further generic exploration pending a specific table-owner discriminator.

## Safety and integration

No game input or reload; no process, guest, VM, desktop lease, installed addon, SavedVariables, third-party repositories or shared environment changed. The host PE was read only. Independent model-agent launches remain suspended under the current explicit FreeBuff/Ollama hold; the two verification jobs are **commands, not AI reasoning agents**.
