# SC-604 — exact-build castbar consumer crosscheck (November 6, 2026, 12:42 EST)

**Owner:** single RRE manager, source-only bounded verification. **Status:** new static producer-to-consumer evidence; SC-604 remains an accepted **interim** mechanism, not a recovered end-to-end cast chain.

## Provenance and independent method

- Original physical-PC `C:\Program Files (x86)\Glyph\Games\RIFT\Live\rift_x64.exe`: **60,493,640 bytes**, SHA-256 **`1935a05c9db6d468e34e0055014a4a99c1b5afceb1695884e24600f5c20a4be8`**, freshly checked before each bounded decode. No process was opened; only original on-disk bytes were read.
- Existing RRE `.venv\Scripts\python.exe` with `pefile` and Capstone; exact original PE RVA→raw mapping. Read the PE exception directory as 12-byte little-endian begin/end/unwind entries; find the **unique** owner of each target call RVA. Decode only bounded owner regions, not the entire executable. An initial arbitrary-midinstruction decode was rejected and replaced by owner-start decoding.
- Prior source-only [RRE producer-output note](REA-RIFT-SPELLCASTING-SC604-CALLER-OUTPUT-DISASM-2026-11-06.md), SHA-256 `ccffc73e400b114df87ceb1b2cfea2186d4ac3b6580bff36b6972a10c48772ed`; the separate RR2 code map supplied candidate castbar regions, **not** accepted field semantics.
- Read-only Workbridge jobs and exits: `rre_20261106_1240_sc604_castbar_callsite_ro` (0), `rre_20261106_1243_sc604_castbar_consumer_ro` (0), `rre_20261106_1245_sc604_first_consumer_ro` (0), `rre_20261106_1247_sc604_two_pdata_consumers_ro` (0), `rre_20261106_1249_sc604_first_buffer_reads_ro` (0). All outputs untruncated. No output files, installed packages or game actions.

## Reproduced caller-to-consumer edges

A bounded raw relative-call search of RVA `[0x9B8000,0x9B8900)` found **exactly two** encodings that target native producer **`0x91DED0`**. Independent disassembly from their PE unwind-entry starts confirmed **both are instruction-aligned `call` instructions**, and their owner regions decode continuously to the recorded end:

| Caller RVA | Sole matching unwind range / unwind RVA | Output argument before `call 0x91DED0` | Immediate return test |
| --- | --- | --- | --- |
| `0x9B8299` | `[0x9B8220,0x9B82AC)` / `0x2E50980` | `0x9B828F: lea r8,[rsp+0x30]`; buffer initialized at `0x9B8285/0x9B828A` | `0x9B829E: cmp byte ptr [rsp+0x30],0` |
| `0x9B8644` | `[0x9B84F0,0x9B88CD)` / `0x2E4FD60` | `0x9B863A: lea r8,[rsp+0x60]`; buffer initialized at `0x9B8630/0x9B8635` | `0x9B8649: cmp byte ptr [rsp+0x60],0` |

Both calls pass `rdx=0` and a native unit-associated pointer in `rcx` immediately before the call. This shows **two separate stack-local output buffers shifted by 0x30**, not a proven persistent shared cast record. It independently corroborates the upstream producer's r8→rdi output-pointer preservation reported in the producer note.

The consumer-side instructions explicitly load the same relative output fields:

| Relative output offset | First caller: buffer `rsp+0x30` | Second caller: buffer `rsp+0x60` | What the bytes establish |
| --- | --- | --- | --- |
| `+0x00` | `0x9B829E` compares `[rsp+0x30]` byte | `0x9B8649` compares `[rsp+0x60]` byte | A branch gate on a byte; not proved `isCasting`. |
| `+0x28` | `0x9B82BE` `movss` from `[rsp+0x58]` | `0x9B8661` `movss` from `[rsp+0x88]` | A float-size value consumed in each path. |
| `+0x2C` | `0x9B8308`, `0x9B8334` `movss` from `[rsp+0x5C]` | `0x9B86B1`, `0x9B86DD` `movss` from `[rsp+0x8C]` | Float-size value, with branch-dependent operations afterward. |
| `+0x30` | `0x9B82E3` `movss` from `[rsp+0x60]` | `0x9B8689` `movss` from `[rsp+0x90]` | A second float-size value. |
| `+0x38` | `0x9B8371` compares `[rsp+0x68]` byte | `0x9B8711` compares `[rsp+0x98]` byte | Another flag-like byte gate; semantic identity unknown. |

The first consumer spans three qualified adjacent unwind chunks (`[0x9B8220,0x9B82AC)`, `[0x9B82AC,0x9B8347)`, `[0x9B8347,0x9B84E2)`); arbitrary decoding starting at `0x9B8230` terminated immediately and was **not** used as proof. The second consumer's containing chunk is `[0x9B84F0,0x9B88CD)`. The relevant sections were successfully decoded from **actual unwind starts** before promoting any instruction boundary.

**Difference versus previous checkpoint:** The November 6 12:19 producer note proved **writes** to candidate output offsets, but had not independently verified **consumer reads**. This note establishes direct, same-build, stack-relative reads in both native castbar paths. It does not yet establish each producer branch's reaching definition or field meaning.

## Limitations, gates and next discriminating step

This is original-executable **static evidence only**. Calls can be bypassed by branches; the return test can skip most reads. These observations do **not** prove field labels (begin/duration/remaining/expired/channeled/ability/uninterruptible), units/timebase, same-frame Lua table keys, in-world casting, server acceptance or GCD/queue behavior. The observed consumer instructions do not prove output offsets `+0x34` and `+0x3C` are consumed here or that the side-effecting native helpers are safe to invoke.

**Next useful qualified question:** follow the actual first/second consumer branch paths to the associated Lua field-string and table-set instructions, including caller-output `+0x38` flag usage, without assigning a semantic name until exact code and reaching definitions agree. Coordinate with RR2's external native-research owner; do not modify RR2 or duplicate its live reader. Do not repeat literal scans, broad Ghidra/REA imports or parked SC-103/SC-306 probes.

**Unchanged:** SC-604 **interim**, SC-103/SC-306 **blocked**, RC-30 strict same-trial archive **pending**, RC-32 physical Retry **unverified**, NAV-002 externally owned. No game input, RIFT UI reload, process control, installed-addon change, SavedVariables write, quarantined-desktop bypass or cross-project write.
