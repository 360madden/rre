# RC-63 — Native status-table producer and upstream owner (LEGION, 2026-11-11)

**Verified static breakthrough:** The same native incoming-record handler writes both fields read by the RC-62 primitive condition checkers. The 256-byte transfer is a proven imported memcpy, not a merely copy-like candidate. Record origin, physical keyboard/mouse semantics, active-player identity, and live movement remain unverified.

## Scope and source

- Host: LEGION, independently verified via Workbridge. Repo C:\work\rre, physical installed RIFT Live x64 only.
- Original PE: C:\Program Files (x86)\Glyph\Games\RIFT\Live\rift_x64.exe, 60,493,640 bytes, SHA256 1935a05c9db6d468e34e0055014a4a99c1b5afceb1695884e24600f5c20a4be8. Preferred image base 0x140000000; addresses below are RVAs.
- No VMware or AMD-DESKTOP access; no process attachment, code/game mutation, keyboard/mouse input, UI reload, installer, Ghidra import, cross-repo change, or remote push.
- Two genuine independent read-only agents; manager alone integrates. Worker scan was one finite exact .text displacement pass and one selected full function, not a broad Xref inventory.

## Incoming record handler (original .pdata-qualified)

- RVA region [0x7C1AD0,0x7C1B7F), 175 bytes / 44 complete instructions.
- Original-window SHA256: 967e6ae9c1220e9c8c5a3d72b9360710ac37d25a8d126f9eb00ba91caa0ef0a5.
- At 0x7C1AF9, r15 receives incoming record pointer rdx. At 0x7C1AFC, r14 receives object pointer rcx.
- At 0x7C1B41, rdx becomes incomingRecord+0x19 (source).
- At 0x7C1B45, r8d becomes 0x100 (256 bytes).
- At 0x7C1B4B, rcx becomes receiver+0xA41 (destination).
- At 0x7C1B52, call 0x25047A9 executes the imported copy.
- The original thunk 0x25047A9 begins ff2549b60e00, jumping through IAT slot RVA 0x25EFDF8. PE import metadata names that slot **VCRUNTIME140.dll!memcpy**. Manager independently verified source bytes, import lookup, and calling argument registers. Thus the complete 256-byte table transfer is confirmed.
- At 0x7C1B57–0x7C1B67, incoming record types 1, 2 and 3 select another copy: 0x7C1B69 loads dword [r15+0x124] and 0x7C1B70 writes it to [r14+0x38].
- A type-5 special branch 0x7C1AF2–0x7C1B3A may alter incomingRecord+0x124 after unqualified calls. Do not infer type-5 semantics from this result.

This identifies one concrete producer for **both** RC-62 primitive fields: indexed high-bit byte table at receiver+0xA41+(index & 0xFF) and mask word at receiver+0x38. It does **not** identify the incoming record as physical keyboard state or prove event-7 will stop a character.

### Producer evidence receipts

- Finite exact-byte displacement scan 410a0000: 14 raw .text matches; .text SHA 76e504d8f26ba7b01cb97bb9741efb158b15f4324d8db5ea094866d9a4884d7c. Job rre-rc63-writer-text-exact-displacement-20261111-01 exit0.
- Selected candidate map and original full function: jobs rre-rc63-writer-candidates-pdata-20261111-01 and rre-rc63-writer-selected-copy-function-20261111-01 exit0.
- Independent manager 3-window SHA/disassembly verification: rre-rc63-manager-producer-globals-independent-20261111-01 exit0.
- Thunk and PE import recognition: rre-rc63-manager-copy-callee-first-bounded-20261111-01 and rre-rc63-manager-copy-import-identity-20261111-01 exit0.

## Upstream global for receiver source

RC-62 function 0x7A3500 calls 0x49A020 and reads [returnedObject+0x350]. The RC-61 predicate then dereferences the accessor return before calling primitive checkers.

| Region RVA | Bytes / decoded instructions | SHA256 |
|---|---|---|
| [0x49A020,0x49A034) | 20 / 4 | ad5a1d91bef924f80931fed89ad975f01d2ec53b911e21ef37ed4fdc2ce4e7a1 |
| [0x49A034,0x49A063) | 47 / 10 | 202bc12dafdf3393c15aefecae65da10bcabc717899b5cc40893d8978255c015 |

- At 0x49A024, a RIP-relative load reads global slot RVA 0x33623E0; 0x49A02B–0x49A02E check nonzero and take the return path. Other initialization branches are not exhaustively decoded.
- Global slot 0x33623E0 is in the .data virtual zero-fill tail: section RVA 0x2F56000, file-backed raw 0x40BC00, slot offset 0x40C3E0 beyond raw. There is no file-backed initial pointer.
- This is a distinct global slot from the RC-61 registry RVA 0x336F8B8. The actual class identity and whether these objects ever alias remain unknown.
- Independent worker jobs rre-rc63-owner-verify-legion-20261111-01, rre-rc63-owner-root-49a020-pdata-20261111-01, rre-rc63-owner-root-49a020-remainder-20261111-01, and rre-rc63-owner-global-slot-metadata-20261111-01 exited 0.

## Ranked practical next checks

1. P1 — One bounded incoming-record producer or caller of 0x7C1AD0. Establish where numeric record types 1/2/3/5 are produced; stop if the call-site mapping is ambiguous.
2. P2 — Qualify the receiver type/origin from 0x49A020 or original record constructors; do not assign keyboard codes merely from a 256-byte table.
3. P3 — Separately authorized genuine RRECollector v0.4.19 navigation SavedVariables plus physical LEGION gameplay correlation. Static copy/flag/clear code is not in-game movement proof.

**Evidence status:** Original-PE source and import semantics verified; live input, callback ownership, physical controls and observed cancellation still unverified.
