# SC-604 — Indexed selector entry initialization (November 8, 2026)

**Owner:** sole RRE manager. **Scope:** one bounded, offline, read-only original PE verification. This extends the [0x128D198 selector report](REA-RIFT-SPELLCASTING-SC604-SELECTOR-128D198-2026-11-07.md). **SC-604 remains interim.**

## Source and verification receipts

- Original executable: C:\Program Files (x86)\Glyph\Games\RIFT\Live\rift_x64.exe; **60,493,640 bytes**; SHA-256 **1935a05c9db6d468e34e0055014a4a99c1b5afceb1695884e24600f5c20a4be8**. Both successful jobs rehashed the file. Static RVA observations only; no fresh guest/process or live state.
- Workbridge command **rre_nov8_sc604_helper_disasm_01**: exit **0**, existing RRE .venv Capstone, bounded 256-byte windows at RVAs 0x12E6F1C and 0x12E39D8, untruncated output. Window SHA-256s respectively: 88a22b5e05a12f57b14450799a2cd688ae2f6b48d6e140099044ec6529aff907 and a0c4f76424672a7f3cdfd29895a42a22987d224dbc3c4186f057d97c0bbaeabe.
- Independent **rre_nov8_sc604_helper_stdlibverify_01**: exit **0**, Python 3.14 standard library only, **15/15** PE/hash/instruction/rel32 checks, including two negative controls (wrong stride and wrong status byte). All data read directly from the original exact-build file.
- Initial exploratory command **rre_nov8_sc604_helper_bytes_01**, exit 0, confirmed size and SHA but extracted no windows due to its own incorrect escaped NUL section-name splitter. Exclude it from the two successful instruction-verification claims; corrected in later commands.

## Direct byte-qualified findings

| RVA | Observed instruction | Evidence boundary |
| --- | --- | --- |
| 0x12E6F1C and 0x12E6F38–0x12E6F49 | Sign-extend incoming R8D, preserve in RBP; call 0x12EA3BC and branch away when EAX is nonzero | A numeric selector and a gate; no label or range semantics. |
| 0x12E6F4B–0x12E6F5C | Compute ESI−1, multiply by **0x38** and add pointer from [RDI+0x68]; move preserved selector to RDX and call 0x12E39D8 | **56-byte indexed entry** addressing; count, bounds and ownership unknown. |
| 0x12E39D8–0x12E39ED | Preserve RDX into RBX and RCX into RDI; call 0x12E38E0; move RBX into qword [RDI] | Stores the supplied sign-extended numeric argument at entry **+0** after an unclassified preparation call; do not label it an ability ID or pointer. |
| 0x12E39F5 and 0x12E39FB | Write word 4 to [RDI+0x24], byte 1 to [RDI+0x26] | Two literal entry fields; **not** proved SC-306 queue enum or gameplay flags. |
| 0x12E6F61–0x12E6F89 | Optional indirect call and return original saved gate result | Caller and runtime result semantics unknown. |

**New static connection:** A selector-preserving call can conditionally initialize a 56-byte-stride indexed entry, storing the sign-extended selector plus two literal fields. Preparation helper 0x12E38E0 is not decoded; no live branch, receiver identity, spellcasting, server admission, modern Legendary identity or queue-mode mapping is established. Do not re-run the parked generic analyses or promote SC-604 beyond **interim** until independent receiver identity or source-bound runtime evidence changes the decision.

**Safety:** no game input, RIFT reload, process or VM manipulation, addon or SavedVariables changes, desktop lease override, cross-project edit, dependency installation, or remote push.
