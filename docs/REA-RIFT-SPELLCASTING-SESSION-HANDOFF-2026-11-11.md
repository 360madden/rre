# RRE RC-67 — three native Win32 keyboard record types 5/6/7 (LEGION, 2026-11-11 ~11:38 EST)

> **Accepted original-PE extension:** Two more source-qualified GetKeyboardState producers prove numeric typed records 5, 6 and 7 each carry 256B keyboard snapshot and call the same `0x7C1AC0` receiver writer already closed in RC-66. Types5/7 also map Win32 virtual-key to character through `MapVirtualKeyW(...,2)` in selected branches; type6 does not in selected branches. Numeric meanings, physical key actions and movement/stop still unproven.

## Fresh RC-67 checkpoint

- Host LEGION only, same original physical RIFT SHA `1935a05c9db6d468e34e0055014a4a99c1b5afceb1695884e24600f5c20a4be8`; starting clean RRE main HEAD `d866db5b7306a6441a220fceaf9a9e52d5862f30` (22 ahead). No game input/process/UI, AMD/VM, installers, provider calls, other repo writes or remote push.
- Two complete original producer windows: `[0xFB6D6D,0xFB6E9C)` 303B/56 SHA `91a114412e6a22966ae438c906274d7fe0f2a6a680ac0d4946349f5f47751da2`; `[0xFB51BF,0xFB5309)` 330B/69 SHA `6a252cb8f8999db41ea32ff484a75b1d5ce2f0331175a8ba8138aa165f34f39d`. Native receiver dataflow and mode2 characters independently checked.
- Three read-only agents; manager independent hashes/callcodes/OS IAT, jobs `rre-rc67-manager-two-producers-independent-20261111-01` and `rre-rc67-manager-record-code-mask-precision-20261111-01` exit0. RC-66 independent audit rechecked all 10 old source windows (683 original instructions), imports and semantics, no material defect; report `docs/RRE-C2M-MULTITYPE-KEYBOARD-RECORDS-LEGION-2026-11-11.md` + `.json`.
- Ranked next: (1) separately authorized passive physical RRECollector keyboard snapshot versus current SavedVariables; (2) one discriminating active receiver/player movement predicate; (3) do not widen broad setter scans until a new alias is established. Static proof does not prove live key acceptance.

## Preserved RC-66 checkpoint
# RRE RC-66 — Win32 keyboard-state provenance verified (LEGION, 2026-11-11 ~11:31 EST)

> **Accepted original-PE breakthrough:** `USER32!GetKeyboardState` at 0xFB6C95 writes 256-byte stack state; 0x7C0200 constructs type-6 record; 0x7C21F0 copies OS state to record+0x19 and maps high bits of VK_SHIFT/CONTROL/MENU; 0x7C1AC0 tail-jumps to 0x7C1AD0, which copies the 256B payload to receiver+0xA41. Separately 0x7C09E4 calls USER32!MapVirtualKeyW(index,2) while making type-7 reset records. Static OS-to-native dataflow proven; **actual gameplay input, movement/stop and active-player ownership unverified**.

## Fresh RC-66 checkpoint

- Host LEGION by `rre-rc66-host-verification-20261111-01` exit0; `C:\work\rre` clean main starting HEAD `04ecf656d50ebbaf43192180d258879eaeb7f726` (21 ahead). Original PE 60,493,640B SHA `1935a05c9db6d468e34e0055014a4a99c1b5afceb1695884e24600f5c20a4be8`, base `0x140000000`.
- Complete proven static chain: GetKeyboardState IAT RVA 0x25EFD68 -> stack buffer -> type6 initializer 0x7C0200 -> 256B copy/mask helper 0x7C21F0 -> accessor 0x7A3500 -> leaf 0x7C1AC0 -> writer 0x7C1AD0 -> receiver+0xA41. Windows VK indices 0x10/0x11/0x12 = Shift/Ctrl/Alt; Game `MapVirtualKeyW(index,2)` IAT RVA 0x25EFC68 in type7 reset path. No live movement or physical effect demonstrated.
- Receiver constructor 0x7C00A0 zeroes +0xA40 gate/+0xA41 256B table/+0x38 mask; owner caller 0x79A63C allocates 0xB48 and stores result at owner+0. Nonzero gate skips queued drains, not immediate 8..16. DL==0 reset loop emits type7 indexed records; type2 mask subcodes 1/2/4; r15d zero proven.
- Park type3 fragment 0x7C0780 direct-call origin: exact E8 scan and .rdata/.data literal pointer probe both negative; no claim unused. Later nonzero +0xA40 setter and active player object identity unresolved.
- Three independent read-only source agents plus manager SHA-verified original windows, named IAT slots and Win32 docs; all listed jobs exit0. Deliverables `docs/RRE-C2M-WIN32-KEYBOARD-STATE-PROVENANCE-LEGION-2026-11-11.md` and paired `.json`, this handoff. No game input, process attach, AMD/VM, install, provider, Ghidra import, or push.
- Ranked next: (1) separately authorized passive physical-game current RRECollector/SavedVariables correlation to a real key event; (2) discriminate actual movement/stop predicate and active receiver owner; (3) park unresolved broad/global scans absent new alias data. Full evidence/job receipts in RC-66 report.

## Preserved RC-65 checkpoint
# RRE RC-65 — native record-copy, type-3 snapshot, type-2 clear (LEGION, 2026-11-11 ~11:18 EST)

> **Accepted original-PE breakthrough:** Queue helpers 0x7C0170 and 0x7C0290 are exact record-copy routines with 256B body at +0x19; tails yield minimum 0x12E and 0x13C footprints. Type3 producer 0x7C0780 snapshots receiver+0xA41 and derives 3 mask bits from indices 0x10/0x12/0x11. A separate type2 fragment dispatches then uses confirmed VCRUNTIME140!memset to zero 256B receiver+0xA41. Root+0x350 later writer remains unqualified after excluding three nearby false positives. No physical input/actual game movement proof.

## Fresh RC-65 checkpoint

- LEGION only; original installed physical RIFT SHA `1935a05c9db6d468e34e0055014a4a99c1b5afceb1695884e24600f5c20a4be8`; RRE main starting clean HEAD `6f39217d8b420708f20125770c46ee285dbed817` (20 ahead). No game inputs, process attachment, AMD/VM, install, model provider, Ghidra import, remote push.
- Helper [0x7C0170,0x7C0200) 144B/34 SHA `433e49ea215ef4da8a77483ba5833bd2fc9963f5439854bb539f51a55d41c034`; helper [0x7C0290,0x7C0336) 166B/38 SHA `80f0a2150de236b90c4fc443041e8832ff3358902c21b5bae0246c478067c189`. Neither manages queue pointer; prior RC64 dispatcher proves stride.
- Type3 [0x7C0780,0x7C0909) 393B/106 SHA `a6fb7de6365dd92fd4f474fb7345391221f0a00881cea0d1f3d9986c873a60de`; type2 fragment [0x7C0A40,0x7C0BAA) 362B/82 SHA `d10dd985a73f7e52f18352ad9362d397b65753f93fe69511b81be0fd512e41ee`. 11 exact direct calls to dispatcher 0x7C0480 in five .pdata regions, selected two original windows. memcpy IAT0x25EFDF8 and memset IAT0x25EFE40 exact imported VCRUNTIME140 semantics checked.
- Focused getter+0x350 proximity scan found syntactic candidates only: [0x4E0920,0x4E17A9) 3721B/871 SHA `3944be714c1d4db2311f2da359a69938b522f955dd6d46b2faa659d4a5a3db18` has unrelated r14 owner; [0xD64827,0xD64A7E) 599B/149 SHA `22aae287174f249637c4a0c4a59d661fdebe05cf54581f8073e25456ed5a3b89` unqualified r15; one other rsp+0x350 stack local. Not proof no setter exists.
- Three independent read-only agents, manager separately verified six original windows / 1,280 instructions and both imports; jobs `rre-rc65-manager-copy-helpers-independent-20261111-01`, `rre-rc65-manager-mask-records-independent-20261111-01`, `rre-rc65-manager-mask-fields-focused-20261111-01`, `rre-rc65-manager-owner-false-positives-independent-20261111-01` exit0.
- Deliverables `docs/RRE-C2M-RECORD-COPY-SNAPSHOT-LEGION-2026-11-11.md` + `.json`, and this handoff. Future: (1) one bounded direct source above 0x7C0780 if discriminating, (2) park globalRoot+0x350 alias search absent new lead, (3) separately authorized current physical RRECollector SavedVariables and actual player movement/stop proof. Validate docs and commit.

## Preserved RC-64 checkpoint
# RRE RC-64 — two native status-record queues (LEGION, 2026-11-11 ~11:09 EST)

> **Accepted static breakthrough:** Dispatcher 0x7C0480 routes numeric records: 8..16 immediate, 5..7 queue stride 0x130 at receiver+0x560/0x568, other types queue stride 0x140 at +0x40/+0x48. Queue drains call status handler 0x7C1AD0 on five original sites; primary drain is gated on byte+0xA40==0 and a second function drains without that own gate. Root constructor initializes +0x350 pointer NULL. Physical input/player/live stop still unproven.

## Fresh RC-64 checkpoint

- Host LEGION verified via `rre-rc64-identity-legion-20261111-01` exit0; starting clean RRE main HEAD `5c29aadc1654414fc256dfe1050847f3e2b2549e` (19 ahead). Original physical RIFT SHA `1935a05c9db6d468e34e0055014a4a99c1b5afceb1695884e24600f5c20a4be8`; RVAs relative base 0x140000000. No VM/AMD, runtime game action, process attach, installer, Ghidra import, provider calls or push.
- Five direct calls: 0x7C0590 / 0x7C05DD / 0x7C0630 / 0x7C1D90 / 0x7C1DE0. Dispatcher [0x7C0480,0x7C0673) 499B/126 SHA `0aaaad0bc6f186ab172dee5c4bfa77647d9f406288b257266422a82140c1fa97`; drainer [0x7C1D40,0x7C1E1D) 221B/54 SHA `acd9156d25be9ac21cd0bd2ef188f02b2777ed09a6c8355f69bf2ac5b0eaabef`.
- Getter remainder [0x49A034,0x49A108) 212B/50 SHA `bbb77cac52655ff813082bd0f0cbeaa915dc561ed5f9ffe27b4bd8f7e838f269`. Allocates 0xF40 bytes and calls constructor [0x53DC70,0x53E773) 2819B/516 SHA `ad5de6f4c667efdb89b2b9d3d0445ae55e45fb7b9dc024f688e3e77b26ce8e75`: xor r13d at 0x53DCCB then stores r13 at root+0x350 in 0x53DDEA. Later setter/class unresolved.
- Type5 conditional incoming+8==0xE5 uses filtered candidate: if validator AL==0, updates incoming+8 and incoming+0x124; never copies +0x124 to receiver+0x38 (types1/2/3 only). Wrapper [0xFAFC70,0xFAFC90) 32B/7 SHA `3422104dd2064935f40d0d408fa8a96e66f296a823a839593ba67e24c16bf088`; filter [0xFB0460,0xFB04C4) 100B/35 SHA `3e730de156d9c9246c709b784a17fe84545a0a6f3f6a157ba0d04ff18326325b`.
- Three independent read-only agents; manager independently rehashed PE, six windows / 788 complete instructions, direct callers, queue branch and NULL write. Manager jobs `rre-rc64-manager-4window-original-independent-20261111-01`, `rre-rc64-manager-constructor-type5-independent-20261111-01`, `rre-rc64-manager-two-queue-detailed-20261111-01`, `rre-rc64-manager-type5-handler-independent-20261111-01` exit0. No code/addon changes.
- Deliverables `docs/RRE-C2M-RECORD-QUEUES-LEGION-2026-11-11.md` + `.json` and this handoff. Next: one bounded incoming caller of 0x7C0480, one later root+0x350 writer, then separately authorized physical v0.4.19 SavedVariables + actual movement/stop. Verify integrity, roadmap validator, Git after integration.

## Preserved RC-63 checkpoint
# RRE RC-63 — confirmed 256-byte status producer (LEGION, 2026-11-11 ~10:58 EST)

> **Accepted static breakthrough:** Handler 0x7C1AD0 imports VCRUNTIME140.dll!memcpy to write 256 bytes from incomingRecord+0x19 to receiver+0xA41. For incoming types 1/2/3 it copies incomingRecord+0x124 to receiver+0x38. Both primitive RC62 fields now share one source handler. Upstream getter 0x49A020 reads another lazy global slot RVA 0x33623E0. Actual physical input and player/stop remain unproven.

## Fresh RC-63 checkpoint

- Host LEGION independently verified; repository C:\work\rre, starting clean HEAD 5dff76e6af91f96045ce113ce23bdff9332fd213, 18 ahead. Original physical RIFT SHA 1935a05c9db6d468e34e0055014a4a99c1b5afceb1695884e24600f5c20a4be8; static RVAs based 0x140000000.
- Producer exact original .pdata [0x7C1AD0,0x7C1B7F) 175B/44 instructions SHA 967e6ae9c1220e9c8c5a3d72b9360710ac37d25a8d126f9eb00ba91caa0ef0a5. Callsite 0x7C1B52 -> thunk 0x25047A9 -> IAT 0x25EFDF8, PE metadata VCRUNTIME140.dll!memcpy. Source +0x19, destination +0xA41, 256B. Incoming numeric type1/2/3 updates receiver+0x38 from record+0x124. Type5 special helper unknown.
- Second global getter first [0x49A020,0x49A034) 20B/4 SHA ad5a1d91bef924f80931fed89ad975f01d2ec53b911e21ef37ed4fdc2ce4e7a1; remainder [0x49A034,0x49A063) 47B/10 SHA 202bc12dafdf3393c15aefecae65da10bcabc717899b5cc40893d8978255c015. Global RVA 0x33623E0 .data zero-fill, distinct from RC61 registry slot 0x336F8B8. Object identity not yet known.
- Two read-only agents, one bounded .text displacement search + one function decode. Manager independently checked 58/58 instructions/3 windows, plus PE import thunk and named DLL export via rre-rc63-manager-producer-globals-independent-20261111-01, rre-rc63-manager-copy-callee-first-bounded-20261111-01, rre-rc63-manager-copy-import-identity-20261111-01, all exit0. No process attach, input, reload, VM, AMD, install or push.
- Deliverables docs/RRE-C2M-STATE-PRODUCER-LEGION-2026-11-11.md and .json, and this handoff; sole manager writes.
- Next: (1) one bounded producer/caller for 0x7C1AD0, (2) object/class identity of getter 0x49A020, (3) separately authorized physical RRECollector v0.4.19 and movement/stop observation.

## Preserved RC-62 checkpoint

# RRE RC-62 — indexed flag primitives and constructed accumulator (LEGION, 2026-11-11 ~10:52 EST)

> **Accepted static breakthrough:** The RC-61 condition tuple primitive helpers are now exact-byte decoded: mask test 0x7C19D0 reads receiver +0x38 with masks 4/8/16; general checker 0x7C1A00 reads high bit of receiver+0xA41+index8. A separate constructor 0x7C3920 initializes owner+0x58 subobject +0x68=1.0f which evaluator updates via verified 0.99*x or 0.99*x+0.01. No physical key/owner/live cancellation proof.

## Fresh RC-62 checkpoint

- **Host/source:** Actual `LEGION` verified by `hostname.exe` job `rre-rc62-verify-legion-20261111-01` exit0; `C:\work\rre` branch main starting clean HEAD `f25ae24cdfa8e8122ddf1f7c33e6bfe6e4c2537f` (17 ahead). Physical original `rift_x64.exe` SHA `1935a05c9db6d468e34e0055014a4a99c1b5afceb1695884e24600f5c20a4be8`.
- **Primitive 1:** Leaf `[0x7C19D0,0x7C19D7)` 7B/3 instructions SHA `2ae2064520604b6cb477c16276b9ceaf8e9555e8d53a10a9edd32ad9fb60689d`: `test [rcx+0x38],edx; setne al; ret`, indices 4/5/6 in RC61 map to masks 4/8/16.
- **Primitive 2:** Leaf `[0x7C1A00,0x7C1A0F)` 15B/4 instructions SHA `d8fd27add70c646095b670a6b3af33adc5c101827a9a2b73dd0a53c89837ef51`: return high bit of `[rcx+0xA41+(edx&0xff)]`. Accessor `[0x7A3500,0x7A3515)` 21B/5 ins SHA `0378fdba4c8a06aac40d9c2c896ad095c2885e8e1421ab1402d17f9c270b322e` calls `0x49A020`, gets pointer `+0x350`; original owner identity unknown.
- **Constructed subobject:** `[0x7C3920,0x7C39D1)` 177B/43 ins SHA `f0829d2d8dfab7a96feabc2d1c005ba7d229a172255f4c8148d4b1e99e4a2ae0`: 0x70B allocation, owner `+0x58` stores subobject, sets `+0x68=1.0f` and `+0x40=0.75f`. Reused evaluator 0x7C98D0 applies `0.99*x` or `0.99*x+0.01`; constants RVA `0x26A4488`/`0x26A33CC` original bytes independently verified. Do not conflate unrelated `+0x38` owners.
- **Verification:** 3 separate read-only worker lanes; manager independently checked 4 new function windows **55/55 decoded instructions** and 2 float literal paths, jobs `rre-rc62-manager-bitfield-ctor-verify-20261111-01`, `rre-rc62-manager-tableaccessor-independent-20261111-01`, `rre-rc62-manager-verify-smoothing-constants-20261111-01` exit0. Agent job receipts in new docs/JSON; no game/process input, cross-host, installers, reload or network push.
- **Deliverables:** `docs/RRE-C2M-INPUT-PRIMITIVES-LEGION-2026-11-11.md`, paired `.json`, this handoff. Sole manager repo writer. Preserve RC61 and earlier source-hashed findings. No addon source changes or live validation.
- **Next ranked:** (1) bounded producer of general flag table `receiver+0xA41`; (2) one receiver owner `0x49A020` or registry record construction `0x7C3920`; (3) separately authorized physical RRECollector v0.4.19 actual receipt + movement/stop test. Static source does not prove input actuation.

## Preserved RC-61 checkpoint

# RRE RC-61 — lazy condition source and composite stateful records (LEGION, 2026-11-11 ~10:46 EST)

> **New accepted static result:** The RC-60 indexed-state getter `0x6A9C10` lazily instantiates a global source pointer at RVA `0x336F8B8`; condition records encode up to three predicate fields and can be evaluated by a **state-mutating** helper. Key identities, callback ownership and live cancellation are **not proved**.

## Fresh RC-61 checkpoint

- **Host/source:** Independently verified LEGION, original installed physical `rift_x64.exe` SHA `1935a05c9db6d468e34e0055014a4a99c1b5afceb1695884e24600f5c20a4be8`, RRE `C:\work\rre`; clean starting HEAD `c9d47962ab4cdae51f6cc81532817ac06a2fd95e` (16 ahead). All RVAs relative preferred base `0x140000000`.
- **Registry:** Getter `[0x6A9C10,0x6A9C24)` 20B/4 ins SHA `675e02151333724dcee64887c3c5a129dc9c73c27a46497677a19618376f73f9`; remainder `[0x6A9C24,0x6A9CF8)` 212B/50 ins SHA `0ca1c71725d60beffc3a92b1537b0694823e8bb2f77a07b9b1134930f2196a0f`. Globals slot `0x336F8B8` is `.data` virtual zero-fill; allocation/constructor candidate `0x7C3920`; runtime contents unknown.
- **Predicate:** `[0x7C3C90,0x7C3D37)` 167B/52 ins SHA `327d8e2ade259baece6b5ebb441c723ce00fa29930f922503a2d46defe4bc699`, up to three tuple condition checks; first -1 false, later -1 skip, 4/5/6 special-mapped to arguments 4/8/16. Primitive callee identities unknown.
- **Stateful evaluator:** `[0x7C98D0,0x7C9BD6)` 774B/207 ins SHA `6b7058cff85b3acb859e04139739c7f9a4191e63cc55e8652ff2f3fb9b8a6988`, iterates 12B tuples, conditionally returns true, writes its own float `+0x68` through object `+0x58`. Do **not** call it pure read, input key, time interval, or movement implementation.
- **Verification:** Two independent read-only lanes and manager independently verified all 4 regions, 313 original instructions, `rre-rc61-manager-registry-predicate-independent-20261111-01` exit0; PE-section and tuple-loop manager job `rre-rc61-manager-global-metadata-tuple-loop-20261111-01` exit0. Full job receipts are in RC61 MD+JSON. No game process access, UI/input, restart, cross-host, installer, or network push.
- **Deliverables:** `docs/RRE-C2M-CONDITION-REGISTRY-LEGION-2026-11-11.md` and `.json` plus handoff. Sole manager writer; preserve all RC-60 and earlier checkpoints.
- **Next ranked:** (1) one bounded primitive flag checker `0x7C19D0`/`0x7C1A00`; (2) one registry constructor `0x7C3920` or record writer; (3) separately authorized genuine v0.4.19 navigation SavedVariables and observed physical movement/stop.

## Preserved RC-60 checkpoint

# RRE RC-60 — input/state transition gate qualified (LEGION, 2026-11-11 ~10:40 EST)

> **Accepted static result:** Event-7's same-receiver follow/destination clear is conditional on `0x6A98C0`, which samples numeric indexed conditions and detects cached-bit transitions or special side effects. It is **not** proven to be a physical input key, player-owned callback, or real stop.

## Fresh RC-60 checkpoint

- **Host/source:** LEGION physically verified; current `rift_x64.exe` SHA `1935a05c9db6d468e34e0055014a4a99c1b5afceb1695884e24600f5c20a4be8`; local RRE main starting clean HEAD `1b37379ad4652267606e08b2b51e99e69c33ab25` (15 ahead). Recheck actual Git HEAD/status after this milestone.
- **Gate:** Event7 caller `0x6A8899` invokes `0x6A98C0` with EDx=0, saves returned AL in BL, then `0x6A88AB` tests it before the clear calls. Gate unwind `[0x6A98C0,0x6A9B0E)`, 590B/186 instructions, SHA `3f10a058b42ec0145fbf7de76fd8d42d3d367af1110be071bf9b13db711ffb32`. It compares indices 2,3,6,7,4,5 to bit cache `this+0x0C` and tests 8/16 with special `this+0x0D` flags. A cached change or special helper branch returns AL=1.
- **Index helper:** `[0x7C97E0,0x7C98CD)`, 237B/74 instructions, SHA `0b2676dcc89d521b6795a826c851d6756c1e8157779acccd8ab314354ae94250`: ordered tree lookup by index and condition evaluation, **not physical-key identity proof**. Companion `0x6A8FC0` first unwind only 102B/30 instructions, SHA `b14f1dfc92c259413990403af5df8c23b101b045b055bafc6fd0bb3b1f673441`, accesses the same `this+0x10` receiver and state.
- **Verification:** read-only agent jobs `rre-rc60-gate-pdata-20261111-01` and `rre-rc60-gate-index-helper-20261111-01` exit0; manager independent 3/3 source-hash and complete 290-instruction recheck `rre-rc60-manager-two-helper-independent-20261111-01` exit0; focused gate and map jobs exit0. No game input, reload, process attach, PC/VM crossing, install, network push.
- **Deliverables:** `docs/RRE-C2M-TRANSITION-GATE-LEGION-2026-11-11.md`, same-basename `.json`, this handoff. Sole manager owns repository writes. Prior RC-59, RC-58 source receipts preserved.
- **Next ranked:** (1) indexed-condition owner/source `0x6A9C10` with bounded branch; (2) callback/receiver `this+0x10` identity; (3) separately authorized physical-client v0.4.19 navigation receipt and actual movement/stop correlation. No Ghidra bulk import or speculative key labels.

## Preserved RC-59 checkpoint

# RRE RC-59 — event-7 same-receiver state clear and native 2D-to-3D projection (LEGION, 2026-11-11 ~10:35 EST)

> **New accepted static breakthrough:** The same `this+0x10` receiver used by the RC-58 event-type-2 destination setter reaches **follow-clear `0x5460A0` and destination-clear `0x546830`** on a separately guarded event-type-7 path. A two-dimensional bounded coordinate projector `0x1154840` and wrapper `0xF903D0` are now original-byte qualified. Still no actual runtime cancellation/player ownership.

## Fresh RC-59 checkpoint

- Host **LEGION** independently verified `rre-rc59-verify-legion-20261111-01` exit 0; RRE repo `C:\work\rre` main, starting clean HEAD **`607540e8ca532257b0878a38920e2298bf25a2d5`** (14 ahead of origin). Recheck Git HEAD/clean status after RC-59 commit.
- Current original physical RIFT executable SHA `1935a05c9db6d468e34e0055014a4a99c1b5afceb1695884e24600f5c20a4be8`, 60,493,640 bytes; RVAs relative preferred base `0x140000000`. Never substitute another host/build.
- Event-7 function `[0x6A8870,0x6A8FB2)`, 1,858B SHA `92213304d979200d6b95f7fff890070d337e629c7220d601a667610060e4c491`, original-byte complete 453 instructions. Event7 sets consumed `+0x18` only after a nonzero predicate and calls both clear helpers on the receiver at `this+0x10`. Type7 **event discriminator is unrelated to type7 pathfinding dispatch**; do not label it physical stop.
- Projection `[0xF903D0,0xF9044F)`, 127B/31 instructions SHA `7906a185a07ea33b722b9c843dccce8a5523db47f4e2e9b54e2b4e49d0624300`; helper `[0x1154840,0x1154A87)`, 583B/112 instructions SHA `ffe16977f0c9ef1b07371fbd0d7fbf7b8b54a6f16e3df02bec81402aa840b162`. It checks 2D bounds and generates three-component transformed values, but no runtime coordinate calibration.
- Manager independently rehashed original PE + **3/3 full windows / 596 decoded instructions**, job `rre-rc59-manager-three-window-independent-20261111-01` exit0. Three independent read-only agent lanes: event7 same-owner route, exact pointer table probe, RC58 quality audit. Quality 28 opcode spot-checks passed; no material previous report error.
- Exact callback pointer `0x1406A6120` absent as literal 8 bytes from current PE `.rdata` (9,855,488B) and `.data` (4,242,432B), job `rre-rc59-vtable-directptr-data-20261111-01` exit 0. Not a vtable/registration disproof.
- New deliverables `docs/RRE-C2M-CLEAR-PROJECTION-LEGION-2026-11-11.md` + `.json` and this handoff. Sole manager writes. No source code, RRECollector, Windows settings, game, VM, AMD-DESKTOP, process memory or remote edits; no install, restart, input or push.
- Ranked follow-ups: **1.** one bounded `0x6A98C0` prerequisite decode; **2.** constructor/receiver owner `this+0x10` candidate; **3.** separately authorized genuine RRECollector0.4.19 navigation receipt and later physical movement/stop validation. Keep the static/live gate distinction and old RC-58 original evidence.

## Preserved RC-58 and earlier checkpoints

### RRE RC-58 — current-build event identity, native spatial query and distance clear (LEGION, 2026-11-11 ~10:26 EST)

> **Fresh accepted static finding:** The same LEGION RIFT build now has an original-byte-qualified callback root (type **2**, event subcondition **1**, setting `+0x146` gate), query wrapper with optional 3D outputs, and consumer squared-distance state clearing. Nine windows / 671 instructions independently checked. **No live movement or local-player ownership is proven.**

## Fresh RC-58 checkpoint

- Host verified **LEGION** using job `rre-rc58-host-legion-20261111-01` exit 0. RRE repository `C:\work\rre`, `main`, starting HEAD `ffb3ff39e1c63bf60f12000fb7d4bda59738e824`, starting tree clean (13 local commits ahead); inspect new HEAD after RC-58 commit.
- Original installed executable SHA **`1935a05c9db6d468e34e0055014a4a99c1b5afceb1695884e24600f5c20a4be8`**; all addresses are static RVAs relative to PE base `0x140000000`.
- **Callback boundary corrected:** root `0x6A6120`, `this` first argument `rcx→r14`, event second argument `rdx→rsi`. Numeric event2 dispatch `0x6A615C→0x6A6201`; `[event+0x120]==1` and `[settingsHandle+0x146]!=0` gate before coordinate query `0xF7CD20` and setter `0x5749C0`. **Owner/physical button meaning unknown**.
- **Query** original-byte window `[0xF7CD20,0xF7CF47)` 551 bytes/144 instructions; optional 3D output and result record check, but no ground-hit identity.
- **Consumer:** squared delta `xmm7` compared to `xmm8/xmm9`; default static squared literals **9.0**, **20.25**, optional **0.0625**, dynamically overwritten in branches. Conditional state-clear `call 0x546830` at `0x588A1F`. No measured arrival or physical stop.
- **Verified:** manager independent `rre-rc58-manager-nine-window-crosscheck-20261111-01` **exit 0**, 9/9 original-window SHA and 671/671 instruction decoding; three read-only agent lanes: callback owner, event fields, query wrapper, with 6 successful original-byte jobs. Manager additionally ran four focused consumer/constant jobs (exit 0).
- **New docs:** `docs/RRE-C2M-EVENT-QUERY-STOP-LEGION-2026-11-11.md`, companion `.json`, plus this handoff. Only manager owns writes; report references all hashes and jobs. Tests: source-bound independent byte verification (not a live test); run scoped JSON parser and Git diff validation before integration. No code/addon changes, VM, AMD-DESKTOP, input, memory access, UI reload, install or push.
- **Next ranked:** (1) native callback registration / `this+0x10` owner with one bounded discriminator; (2) genuine separately authorized v0.4.19 navigation API SavedVariables receipt; (3) separately approved physical client gesture + movement/stop proof to distinguish computed clears from actual movement. Keep existing RRECollector source v0.4.19 / installed last documented v0.4.18; root `C:\work` scope unchanged.

## Preserved RC-57 and earlier checkpoints

### RRE RC-57 — current-build native event/query to C2M setter (LEGION, 2026-11-11 ~07:28 EST)

> **Third original-byte milestone:** A focused, bounded direct-caller check on the current LEGION RIFT PE connects query success at `0x6A64EC` to the RC-56 destination setter at `0x5749C0` via one verified `call` at `0x6A650D`. This is still a static code chain, **not** live movement or player input acceptance.

## Fresh RC-57 checkpoint

- Source: LEGION physical `rift_x64.exe` SHA-256 `1935a05c9db6d468e34e0055014a4a99c1b5afceb1695884e24600f5c20a4be8` (same verified current build as RC-55/56); no VMware, AMD-DESKTOP, game input, process attachment, game-file or memory changes, UI reload, addon deployment, new package, or remote push.
- One E8 direct-call candidate and one PE boundary-qualified caller in `[0x6A62B1,0x6A652E)`. Query `call 0xF7CD20` at `0x6A64EC`, `test al,al` at `0x6A64F1`, `je 0x6A6516` at `0x6A64F3`; receiver from `[r14+0x10]` at `0x6A6501`, setter `call 0x5749C0` at `0x6A650D`, event consumed flag `[rsi+0x18]=1` at `0x6A6512`.
- Independent manager `rre-rc57-manager-original-byte-confirm-20261111` exit0: original PE source hash matches, 637-byte code-window SHA `e820bb56a8d8b4ed6f21d61314d40ce003e01ec4a17e3c5d795da0f2a1e1fa09`, **142/142 instructions** decoded within region, exact call targets verified. Independent agent discovery job `rre-rc57-native-newbuild-c2m-direct-call-20261111` exit0.
- New files: `docs/RRE-C2M-EVENT-NEW-BUILD-LEGION-2026-11-11.md`, `docs/RRE-C2M-EVENT-NEW-BUILD-LEGION-2026-11-11.json`, plus this checkpoint. Sole main-branch writer: manager; one read-only agent, stopped on useful one-probe finding.
- Last accepted commit before RC-57: `a7342735715b2151804c121f6878cbb3f78a5fc4` (RC-56). Recheck Git HEAD, status, SHA-qualified docs after integration. No RC-57 addon changes; prior RC-55 v0.4.19 preflight and 53/53 relevant Node checks still stand.
- Remaining gates: specific input-event type/button, callback registration and local-player receiver identity, real game-world destination/motion, stop/cancel, and type-7 route linkage **unqualified**. Do not promote static code to a callable automation contract.
- Next tasks (ranked): **1.** read-only callback ownership/registration with one bounded discriminator; **2.** event type/button meaning from the already selected range; **3.** separately authorized operator-owned physical RIFT movement/stop observation. No broad type-7 scans or Ghidra PE imports.

## Prior RC-56 checkpoint (preserved)


> **Second verified native milestone:** Two bounded original-byte probes located the current executable's click-to-move destination **setter** and **consumer entry**; manager independently requalified their complete `.pdata` windows. Still static-only, not active gameplay movement or a qualified player-owned pointer chain.

## Fresh RC-56 checkpoint

- Host: **LEGION**, physical RIFT executable only; original SHA-256 `1935a05c9db6d468e34e0055014a4a99c1b5afceb1695884e24600f5c20a4be8`. No VM, AMD-DESKTOP, game input/reload, process attach, game-file or memory write, deployment, network push or new dependency.
- Previous accepted local RC-55 commit: `b4ac7ed2ada41e38329bfebe95c81d266b5da80b` on `main` (11 ahead of origin, clean immediately after RC-55).
- **Static C2M setter:** old `0x562BC0` -> current `0x5749C0`; unique **20-byte** source signature; full unwind `[0x5749C0,0x574A18)`, 88 bytes, 21 instructions, SHA `e6427f87b5f3f2a407bd742142181cffe82125a2b9943b80a690b8aa374d6075`. Setter clears old state, writes supplied 12-byte destination to receiver `+0xB90` component `+0x60/+0x68`, sets `+0x1A8` bit0.
- **Static consumer entry:** old `0x5765D0` -> current `0x588420`; unique **14-byte** signature; unwind `[0x588420,0x5884A7)`, 135 bytes, 32 instructions, SHA `2b57dcbdb4c7a84f243a5ba8ad35f5b1988f4135c1401158a8e9b7cee8e3ec26`. It reads the same component and tests the activation bit. Further consumer branches uninspected.
- Current new direct clear call targets `0x5460A0` and `0x546830`. This confirms selected cross-build static state relationship, **not** current player ownership, event delivery, actual movement, cancellation, route planning or collision.
- Evidence saved: `docs/RRE-C2M-NEW-BUILD-LEGION-2026-11-11.md` and `.json`. Native jobs `rre-rc56-native-c2m-samebytes-20261111` and `rre-rc56-native-c2m-setter-consumer-20261111` exit0, two-probe stop. Independent manager `rre-rc56-native-independent-window-verify-20261111` exit0, exact full-window SHA and all **53 decoded instructions**.
- One read-only agent investigated and stopped; manager alone wrote documentation and commits. Starting worktree for RC-56 was clean; selected RC-56 changed files are the two reports plus this handoff.
- **Next:** (1) one bounded current-build event callback direct-caller and owner trace for new setter `0x5749C0`; (2) small consumer continuation for near-stop state; (3) separately authorized manual runtime player XYZ + click/stop proof only after current client version, exact session and input ownership. Do not repeat broad type-7 scans.
- Offline RC-55 Node tests remain **53/53**, package preflight v0.4.19 exit0; **no new addon source changes or live tests in RC-56**. RC-56 JSON/provenance and Git diff checks are its relevant acceptance; no full .NET test rerun warranted.

## Prior RC-55 checkpoint (preserved)


> **New accepted offline result:** The current LEGION physical RIFT executable's type-7 `TtPathfinding` label and type-indexed dispatch pattern were requalified on SHA `1935a05c9db6d468e34e0055014a4a99c1b5afceb1695884e24600f5c20a4be8`. This is **static code behavior only**; navigation handler registration and live movement are still unverified. The current SHA was already documented October 27; new in RC-55 is the selected navigation requalification.

## Fresh RC-55 evidence and changes

- Independently verified machine via LEGION Workbridge `hostname.exe`. Only LEGION connector/physical RIFT path; no AMD-DESKTOP, VM lab, game input, UI reload, debugger, native memory write, live deployment, dependency installation or Git push.
- Physical `rift_x64.exe` PID 22648 path matches the current installed executable, 60,493,640 bytes. In-memory binary identity, current playable scene and addon load remain **unverified**.
- **Native breakthrough:** original-PE pathfinding/raycast strings at `0x2DCCF38`/`0x2DCCF00`; corresponding instruction-aligned RIP references at `0x102719`/`0x1027B3`. Exact build dispatch type7 uses `dispatcher+0x130+7*0x20 = +0x210` then indirect subtype handler call at `0x102833`. Click-to-move setting literal `0x26EC228`, root-pointer RVA `0x33958C0`, setting byte `+0x146` compared/written at `0xBD113D/0xBD114A`. Old-build source RVAs and static pointers are not portable. Full source-bound evidence: `docs/RRE-NAV-NEW-BUILD-LEGION-2026-11-11.md` and `.json`, job IDs included there.
- Independent manager original-PE byte check `rre-rc55-native-byte-independent-confirm-20261111` **exit0**, hash rechecked, **7/7 exact opcode bytes decoded correctly** in Capstone. No generic/native import attempted.
- **RC-55 release preflight:** `tools/deploy-rrecollector-onedrive.ps1` now gates solely v0.4.19 and calls strict source package validator before both preflight/deploy. Read-only `pwsh.exe` preflight `rre-rc55-v0419-deploy-preflight-readonly-20261111` **exit0**: installed v0.4.18 / source v0.4.19 / 11 expected files / strict source passed / `PREFLIGHT_OK_NO_FILES_CHANGED`. Direct package validator `rre-rc55-v0419-strict-package-20261111` exit0 with 11 sources. **No deployment took place.**
- **RC-55 exporter fix:** `tools/export-rrecollector-navigation-api.mjs` now renders producer-permitted backticks as Markdown-escaped text rather than malformed code spans. Independent bug reproduction `rc55-agent-backtick-repro-11`; added regression in `tools/test-export-rrecollector-navigation-api.mjs`.
- Tests: focused RC-55 exporter **11/11** (`rre-rc55-export-backtick-tests-20261111`); combined four relevant Node suites **53/53** (`rre-rc55-node-four-suites-20261111`); `git diff --check` exit0 with Git's nonfatal LF/CRLF warnings. Existing .NET production 97/97 pass is a *prior RC-53 record*, not retested for RC-55.
- Read-only reviewers: native original-byte investigation (7 primary job receipts); independent collector/exporter source review; live-receipt availability audit. Sole manager made all repository writes.
- Starting HEAD `2f68afa82e52f5ba8b79823e1d9e4d3df486462b` on `main` (previous RC-54), originally clean and 10 ahead of origin. RC-55 changed files: `tools/deploy-rrecollector-onedrive.ps1`, `tools/export-rrecollector-navigation-api.mjs`, `tools/test-export-rrecollector-navigation-api.mjs`, `docs/RRE-NAV-NEW-BUILD-LEGION-2026-11-11.md`, `docs/RRE-NAV-NEW-BUILD-LEGION-2026-11-11.json`, this handoff. Inspect current Git HEAD/status after local RC-55 commit; no remote publication.
- Live API capture still blocked: last documented installed v0.4.18 has no v0.4.19 `navigationProbe`; Workbridge roots list only `C:\work`, so original Documents\RIFT SavedVariables cannot be read through root-scoped APIs. Do not invent API observations or circumvent root policy.

## Three prioritized next decisions

1. **P1 — Real API:** With separately confirmed release authority, use v0.4.19 scripted backup+hash deployment, **operator** /rre navigation and normal game save, then authorized original SavedVariables acquisition and strict Markdown export. Preflight success is not install/load proof.
2. **P2 — Native discovery:** From the newly requalified `+0x210` dispatch and `+0x146` C2M setting anchors, select the *smallest* handler registration/producer or current-build destination setter probe. Do not resume broad type-7 scans or full Ghidra import.
3. **P3 — Coverage quality:** Once an authentic navigation index exists, decide whether the 18-document ordering oversamples generic spatial APIs and starves NPC/other-target details; do not expand a synthetic-only atlas spec prematurely.

## Prior RC-54 exporter checkpoint (preserved)


> Source-only/offline milestone. The physical RIFT client has **not** produced a v0.4.19 navigation receipt. The exporter is implemented and tested with **synthetic fixtures only**; it does not assert current API facts.

## Ownership and context

- Machine: **LEGION verified via Workbridge**. Repository: `C:\work\rre`, branch `main`.
- Starting commit: `c9ff52e346bfb5ec87b81f1410aaccb1c2d85a0b` (RC-53, v0.4.19 bounded `/rre navigation` Lua discovery, source-only).
- Previous comprehensive handoff: `docs/REA-RIFT-SPELLCASTING-SESSION-HANDOFF-2026-11-10.md` (RC-53 section).
- Sole writer managed RC-54 changes; independent read-only reviewers inspected exporter against the source producer. No cross-host contact, VM use, game input, Windows/RIFT restart, Workbridge root bypass, deployment, new tool installation or remote push.

## Concrete RC-54 deliverable

- Added `tools/export-rrecollector-navigation-api.mjs` with `summarizeNavigationReceipt(saved, source)`, `renderNavigationMarkdown(qualifiedReceipt)`, `readNavigationReceipt(originalPath, requiredVersion)` and a CLI.
- CLI (Windows terminal opened at `C:\work\rre`), after a **real** physical RIFT `/rre navigation` + normal SavedVariables persistence:
  `node.exe tools/export-rrecollector-navigation-api.mjs "C:\verified\path\RRECollector.lua" --require-version 0.4.19 --output "C:\work\rre\artifacts\navigation-api.md"`
  Replace example path; `--output` uses exclusive `wx` create and will never overwrite an existing document.
- Reuses the literal-only Lua SavedVariables parser and original-file stable reader (2 MB cap, path/file-change guards). Reports original-byte SHA-256, byte size and mtime. No arbitrary Lua execution or game calls.
- Exact source contract: saved-root/probe version **0.4.19**, bound sequence, schema/scope, 8 exact guarded `Inspect` member-type paths, 2,048 scanned names, 96 retained names, 18 exact retained-name documentation entries, 512 UTF-8 bytes per excerpt, matched/ignored/truncated counter consistency, priority ordering then Lua-equivalent UTF-8 bytewise order. Empty Lua `{}` document maps are handled.
- Markdown enumerates qualified names, path types and returned bounded doc strings; clearly labels `observed-without-index`, partial scans, and lack of verified current-game load or movement control. Escapes HTML and Markdown image/link/emphasis syntax in data so descriptions remain inert research text. Source names with producer-permitted Unicode/punctuation are not falsely rejected.
- Updated `addons/RRECollector/README.md` with exact CLI and source-only qualifications.
- Added `tools/test-export-rrecollector-navigation-api.mjs` with valid synthetic fixtures, absent/stale/malformed data, ordering, cap/partial status, unavailable-index state, UTF-8/escaping, source byte hash, and exclusive no-overwrite CLI tests.

## Verified tests and limitations

- **65/65 PASS** combined Node: 10 RC-54 exporter + 14 collector source/calling + 29 SavedVariables adapter + 12 profession reader. `git diff --check` exit0.
- RC-53 package remains v0.4.19 **strict-pass**, 11 addon files. RC-53 .NET10 production-only tests **97/97 PASS**, unchanged by this exporter.
- Independent reviewers found and manager fixed: (1) extra ASCII regex incompatible with Lua producer, (2) misleading bounded-index status for documentation unavailable, (3) active Markdown images/links from documentation. Tests cover each.
- Entire new exporter remains **offline/synthetic** until a source-verified original `RRECollector.lua` with `navigationProbe` exists. Do not generate a factual current RIFT API library from these tests. No Lua 5.1 runner available. The historical full .NET checks trial stops at a missing Lab2 fixture, not counted as full-pass.
- Workbridge still admits only `C:\work` (`additionalRoots=[]`); original user Documents\RIFT SavedVariables cannot be read by this connector until separately coordinated allowed-root change/restart. v0.4.19 was **not installed** into the physical client; deployment script intentionally permits only prior v0.4.18.

## Prioritized next actions

1. **Actual data:** qualify a Lua 5.1 offline runner or a version-matched physical RIFT v0.4.19 addon load, manually invoke `/rre navigation`, persist SavedVariables and obtain original SHA-qualified file through authorized roots. No RIFT restart inherently needed.
2. **First API reference:** run strict exporter against genuine original; inspect `scanLimitReached`, counts, returned docs and evidence caveats; then deliver source-backed Markdown to the ChatGPT project.
3. **RRE/RR2 research:** investigate only source-supported navigation/position/target APIs from that reference and native REA disassembly as complementary evidence; don't infer gameplay-control APIs from names alone. Preserve SC-103 spellcasting and RC-53 collector boundaries.
