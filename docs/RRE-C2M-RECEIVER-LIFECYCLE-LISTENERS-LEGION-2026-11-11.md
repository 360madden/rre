# RRE RC-69 — native input receiver teardown and listener-object layout

**Host:** LEGION | **Date:** 2026-11-11 (~11:58 EST) | **Evidence:** original installed RIFT PE only; no live game input or process access.

## Accepted static findings

1. **The root input-owner pointer has both an assignment and a cleanup.** RC-68 showed `0x772DDD -> 0x77E410` assigns `[outer+0x1B8]` into `globalRoot+0x350`. An exact direct E8-rel32 count for setter `0x77E410` found two raw sites: `0x772DDD` and `0x779365`. The separate complete cleanup function `[0x779140,0x779607)` reaches `0x77935B call 0x49A020` (global root getter), `0x779360 xor edx,edx`, `0x779362 mov rcx,rax`, then `0x779365 call 0x77E410`. Since setter body is `mov qword ptr [rcx+0x350],rdx; ret`, this **explicitly clears globalRoot+0x350 to NULL** in that cleanup path. The callback to a particular movement actor and real runtime order remain unverified.
2. **Receiver creation and empty callback-list state are source-proven.** Owner construction `[0x79A590,0x79A9D3)` allocates 0xB48 at `0x79A62A`, invokes receiver initializer `0x7C00A0` at `0x79A63C`, and stores the returned receiver at `owner+0` (`0x79A641 mov [rdi],rax`). The complete initializer `[0x7C00A0,0x7C016A)` establishes receiver+0x10 as NULL at construction (`0x7C00BD`, RDI zero), together with queue starts and the existing zeroed 256-byte keyboard state. No later callback-list registration at receiver+0x10 was identified in the two bounded probes. A separate 0x18-byte helper allocated inside owner construction also uses a +0x10 field; **do not confuse it with the 0xB48 receiver**.
3. **Listener vtables are attached to listener objects, not to the owner/queue.** Complete `[0x7C1B7F,0x7C1D32)` fanout derives a listener-list sentinel at notification object `r14+0x08`; list node `+0x10` carries each listener object pointer, `r14+0x18` is an exclusion list, and `r14+0x28` is an optional special listener. The optional vtable `+0x10` call filters when enabled; vtable `+0x08` (`0x7C1C6C`, `0x7C1CC9`) calls the listener object with the incoming record pointer in RDX. Concrete listener class/movement meaning remains unproven.
4. **Buffered records have a confirmed drain/clear path.** Independent complete `[0x7C1D40,0x7C1E1D)` disassembly confirms 0x140 stride in receiver+0x40/+0x48 buffer, 0x130 stride in receiver+0x560/+0x568 buffer; both submit each record to `0x7C1AD0` with R8D=0 (`0x7C1D90`, `0x7C1DE0`). At end, end pointers are reset to start (`0x7C1E00`, `0x7C1E0B`). This supports RC-64's queue model but **does not identify the driver that drains queues**.

## Immutable original-source receipts

- Installed original RIFT PE 60,493,640B SHA-256 `1935a05c9db6d468e34e0055014a4a99c1b5afceb1695884e24600f5c20a4be8`, image base `0x140000000`. All addresses are RVAs.
- Teardown `[0x779140,0x779607)` 1,223B / 248 fully decoded, SHA-256 `05c8651136160cb12f5a5ed17af6d98b961b14b6167fb425fddf2475282431b9`.
- Owner constructor `[0x79A590,0x79A9D3)` 1,091B / 237 fully decoded, SHA-256 `3c8cfd1121328b2fc65160f976991f908cc98817b3f2e3eae62690c81faa018f`.
- Receiver initializer `[0x7C00A0,0x7C016A)` 202B / 48 fully decoded, SHA-256 `91dd527b1562b535ed21c3675fde7a711f04b40f30416a55e894d4979b7cee2a`.
- Fanout `[0x7C1B7F,0x7C1D32)` 435B / 119 fully decoded, SHA-256 `b0a6e17f33aacc531541bcb07611bed13d22bf4a54d250e7ce5396f81da93ee5`.
- Drain `[0x7C1D40,0x7C1E1D)` 221B / 54 fully decoded, SHA-256 `acd9156d25be9ac21cd0bd2ef188f02b2777ed09a6c8355f69bf2ac5b0eaabef`.
- Manager independently checked all five original-byte hashes, 706 complete Capstone instructions and specific owner/clear/dispatch instructions in `rre-rc69-manager-owner-lifecycle-independent-five-windows-20261111-01` (exit0). The exact setter E8 search `rre-rc69-manager-owner-setter-exact-caller-count-20261111-01` (exit0) found exactly two syntactic matches; this does not exclude indirect calls.
- Parallel read-only probes `rre-rc69-cbowner-79a590-bounded-complete-filtered-20261111-01`, `rre-rc69-cbowner-7c00a0-init-pdata-20261111-01`, `rre-rc69-cbowner-second-rootsetter-caller-full-filtered-20261111-01`, `rre-rc69-a-callback-fanout-complete-20261111-01` and `rre-rc69-a-first-adjacent-registration-candidate-20261111-01` all exit0. Attempts to cap large functions returned PARK_LARGE/OVER_900, followed by complete same-function disassembly (not a wider exploratory search).

## Parked routes, missing proof and next priorities

- A one-time exact direct-E8 scan for generic accessor `0x7A3500` found 3,276 raw sites (`rre-rc69-manager-input-receiver-accessor-direct-index-20261111-01`), so this path is **too broad to discriminate** listener/player identity; park it. The nearby candidate `0x7C1D40` is a queue drainer, not a listener-registration function.
- **Not proved:** runtime active player binding, listener subscription site that writes receiver+0x10, which listener (if any) controls movement/stop, numeric event type meanings, actual physical key effectiveness, current RRECollector physical load.
- **P1:** Find one specific registration/write into receiver+0x10 using a newly grounded object/constructor reference; stop after two non-discriminating probes.
- **P2:** Match a concrete listener-object vtable to a game-local player movement consumer, anchored to a proven registration call rather than generic vtable scans.
- **P3:** With separate authorization and current physical-load receipt, compare two timestamped RRECollector coordinate captures and an independent input timeline; do not call coordinate delta proof of the native stop cause.

**Boundaries:** No gameplay input, UI automation, process attachment, AMD-DESKTOP, VMware, provider, installation, other-repo writes or remote push.
