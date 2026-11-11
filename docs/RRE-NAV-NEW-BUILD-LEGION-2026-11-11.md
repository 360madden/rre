# RC-55 — LEGION new-build native navigation bridge (November 11, 2026)

**Result:** A selected piece of RRE's historical navigation model **survived the changed physical RIFT build**. Fresh, exact-hash offline disassembly on LEGION recovered the type-7 `TtPathfinding` and type-3 `TtRayCast Query` selection/indirect-dispatch pattern on the newer executable. This does **not** prove an active pathfinder or navigation input.

## Original-source identity

- Current physical installed file: `C:\Program Files (x86)\Glyph\Games\RIFT\Live\rift_x64.exe`
- SHA-256: `1935a05c9db6d468e34e0055014a4a99c1b5afceb1695884e24600f5c20a4be8` (60,493,640 bytes).
- Prior NAV static pin: `7c356c9dde9e12fcbff3c08d953b0630b48b1510a0ffb36e4ec164606e7b17bd` (59,963,840 bytes).
- Read-only process-path check saw `rift_x64.exe` PID **22648** using the new file path. The source hash was already recorded in RRE's October 27 build checkpoint; today's **new** finding is the selected NAV code requalification. A path match is not in-memory image-byte proof.

## Selected new-build anchors (RVAs, not absolute process addresses)

| Literal in original PE | Current RVA | Old-build literal RVA | Current verified RIP-LEA code RVA |
|---|---|---|---|
| `TtPathfinding` | `0x2DCCF38` | `0x2D51598` | `0x102719` |
| `TtRayCast Query` | `0x2DCCF00` | `0x2D51560` | `0x1027B3` |
| `Misc_EnableClickToMove` | `0x26EC228` | `0x26851F8` | `0xBD10FE`, `0xBD1126`, `0xBD74E8` |

These are original-PE string references, **not confirmed function entries, caller contracts or movement controls**. The five reference instructions were Capstone-verified within PE `.pdata` unwind boundaries; no full decompiler import was used.

## Stronger finding: current type-7 dispatch

- The new executable's unwind interval `[0x102634, 0x10288F)` contains both job-label branches and a per-type indirect-dispatch tail.
- A bounded decoded branch comparison routes value **7** to the `TtPathfinding` label at `0x102719`; value **3** reaches `TtRayCast Query` at `0x1027B3`.
- At `0x102814`, the routine loads the job-type byte from `[rsp+0x21]`; at `0x102819` it also reads a subtype byte from `[rsp+0x20]`.
- At `0x102824`: `shl rcx,5`. At `0x102828`: bytes `488b843930010000` decode to `mov rax, qword ptr [rcx+rdi+0x130]`.
- At `0x102833`: bytes `42ff14c0` decode to `call qword ptr [rax+r8*8]`.

The table-pointer offset for type **7** is thus `0x130 + 7*0x20 = 0x210` in this **new** build as well. Type **3** uses `0x190`. This is a **static dispatch layout** finding, not proof of table population, a known handler, an actual call at runtime, a route, or an accessible player navigation command.

## Click-to-move setting dataflow (not gameplay input)

A separate reference to `Misc_EnableClickToMove` resolves a source read at `0xBD1136` through a root pointer RVA `0x33958C0`; byte `+0x146` is compared at `0xBD113D` and written at `0xBD114A`, followed by a dirty-bit-3 operation at `0xBD1155`. Another adjacent byte `+0x147` appears in this setting region. This is **static setting-storage evidence**; it does not show the current value, whether click-to-move is enabled in-game, the destination path, or whether movement is accepted.

## Reproducibility and boundaries

The source hashes were verified in each targeted read-only Windows job, using the existing RRE virtual environment's `pefile` and `Capstone` with literal scripts. Exact job IDs and structured fields are recorded in [the RC-55 JSON evidence record](RRE-NAV-NEW-BUILD-LEGION-2026-11-11.json). Key jobs: `rre-rc55-native-newbuild-nav-lea-xrefs-20261111` and `rre-rc55-native-newbuild-dispatch-tail-20261111`, both exit 0. Neither attaches to RIFT nor changes it.

**Still unknown:** type-7 table registration/handlers, gameplay producer, real movement/follow/collision, current player binding, cancellation, dynamic pointer chains, in-memory loaded-image equality and in-world verification. Do not transplant old root pointers or call the old-build NAV-002 route validated.

**Next smallest test:** Trace only the new `+0x210` table setup/producer from original bytes and compare relevant setting consumer, then independently obtain player/session-bound live evidence under an explicit single-owner test window. Do not launch a full REA/Ghidra import or repeat broad type-7 scans.
