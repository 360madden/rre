# RRE RC-68 — native input receiver ownership and callback propagation

**Host:** LEGION, November 11, 2026 (~11:50 EST). **Status:** accepted source-level owner alias and listener callback path; active-player ownership, keyboard event semantics, movement and stopping remain unverified at runtime.

## Practical breakthroughs

1. **The root-to-receiver owner is no longer a speculative alias.** One original `.text` E8-rel32 callsite to `0x79A590` occurs at `0x772DFB` inside the complete caller `[0x772DC0,0x772E27)`. The same caller gets the existing lazy global input root via `0x49A020` at `0x772DC9`, loads `outer+0x1B8` into RDX at `0x772DD3`, and invokes a trivial root setter at `0x772DDD`. That setter at `0x77E410` executes `mov qword ptr [rcx+0x350],rdx; ret`. It then passes `[outer+0x1B8]` as RCX to constructor caller `0x79A590` at `0x772DFB`; the RC-66 traced constructor path allocates 0xB48 and places receiver at `owner+0`. Therefore the RC-62 accessor chain `globalRoot+0x350 -> owner -> owner+0 -> native input receiver` is now original-source-proven. The owner has **not** been tied to an active player in a live session.
2. **The keyboard-state receiver can notify callback-like listeners.** After `0x7C1AD0` copies incoming 256-byte record payload from `record+0x19` into `receiver+0xA41`, it tests `receiver+0x10` for zero and skips callbacks when zero. The nonzero branch traverses the list whose actual sentinel pointer is at `receiver+0x08` (RC-70 correction: +0x10 is count-like, **not** a callback-root pointer) in `[0x7C1B7F,0x7C1D32)`. With wrapper flag `r13b` set, calls through listener vtable offset `+0x10` conditionally filter callbacks (`0x7C1C5B`, `0x7C1CB9`); calls through vtable offset `+0x08` notify selected listener objects (`0x7C1C6C`, `0x7C1CC9`) with RDX = original incoming record pointer. We have **not** identified which listener, if any, changes player movement or stop behavior.
3. **A practical live-observation boundary was established without touching the game.** Current RRECollector v0.4.19 source has a manual `/rre capture` context snapshot with optional player/target `coordX/Y/Z`, frame/real clocks and client-version fields when the API returns them. It has no continuous keyboard-state sampling, movement event timeline or passive stop correlation. Reader C# already accepts v0.4.19 and has an offline regression check; `reader/README.md` and `reader/contract-rrec2.md` were lagging and are updated in this milestone.

## Exact original-PE evidence

- Original installed executable: `C:\Program Files (x86)\Glyph\Games\RIFT\Live\rift_x64.exe` (60,493,640 bytes), SHA-256 `1935a05c9db6d468e34e0055014a4a99c1b5afceb1695884e24600f5c20a4be8`; image base `0x140000000`. Addresses below are RVAs.
- Caller `[0x772DC0,0x772E27)`: 103 bytes, 24 fully decoded instructions, SHA-256 `4dfcc44cebb1e12c7dd6a878e15599366d6ba456d270b0164ecec9db28c0988d`.
- Setter `[0x77E410,0x77E418)`: 8 bytes, 2 instructions, SHA-256 `85307e7dc88d2f6e162ce491e825ad427671ea63a6d1013ce53dd83e1ebd1bc8`. This trivial leaf has no `.pdata` entry; a first metadata-only lookup found no owner and was corrected by bounded original-byte disassembly.
- Receiver writer `[0x7C1AD0,0x7C1B7F)`: 175 bytes, 44 instructions, SHA-256 `967e6ae9c1220e9c8c5a3d72b9360710ac37d25a8d126f9eb00ba91caa0ef0a5`.
- Callback fragments `[0x7C1B7F,0x7C1BA3)`: 36 bytes, 6 instructions, SHA-256 `869637d1a2c144884bfc2be6f851c4a29c6c3283b8c3515b912c1f1f29f592df`; `[0x7C1BA3,0x7C1C53)`: 176 bytes, 47 instructions, SHA-256 `9830306d14cdec382ea8c14363d56b0952484dd8d95a4a26c58ea491d8241c70`.
- Callback fragments `[0x7C1C53,0x7C1CF3)`: 160 bytes, 48 instructions, SHA-256 `b0ae0c6a9a2689bfc914794d28a450e4dc9569a31caba89243c1bfb4d9e718f4`; `[0x7C1CF3,0x7C1D32)`: 63 bytes, 18 instructions, SHA-256 `7084ddc6c9c81b6606d7229eb93698146e2c8e7c11ca040227a47424a87e5236`.
- The manager independently verified all seven windows, exact hashes and complete Capstone decoding against the original executable: `rre-rc68-manager-independent-callback-owner-20261111-01` (exit 0). Source-to-reader version truth cross-checked `reader/Rre.Reader/ProductionFrameCodec.cs` SHA `dc220e4fa4d2bf711625506c575b6c7c2c08d6c284f064c311ff3b89ef47d151` and `reader/Rre.Reader.Checks/ProductionChecks.cs` SHA `114b8ff65c90060bba60c847e0afe9d36b34d2f5a3ae93b4dd8132dad7ba9da0`.

## Bounded negative checks and cautions

- Predicate `0x7C3C90` had three direct `.text` E8 calls: `0x7C9846`, `0x7C987E`, `0x7C9B4D`, in two small decoded evaluators. This identifies conditional-evaluation callers, **not** the movement or stop listener; lane parked after two source probes.
- Exact direct E8-rel32 scans for `.pdata` fragment starts `0xFB6C5F`, `0xFB51BF`, `0xFB6D6D` returned zero raw matches. These are fragment starts rather than guaranteed callable entrypoints; absence of such E8 sites says nothing about overall reachability.
- RRECollector 0.4.19 has manual context capture, not a passive keyboard/movement sensor. Its installed/loaded physical-game state was not tested. SavedVariables is persisted on reload/logout, so a stale retained capture alone does not demonstrate real-time movement.
- RC-66 numeric record types and 256B snapshots remain proven; type5/6/7 event meaning, actual accepted key movement, listener object identity, stop-event causal chain and current session player binding remain **unknown**.

## Reproducibility and source ownership

- The owner caller agent ran `rre-rc68-owner-caller-79a590-e8scan-20261111-01`, `rre-rc68-owner-caller-772dc0-full-20261111-01`, and `rre-rc68-owner-root-link-leaf8-sha-20261111-01`, all exit 0. A metadata-only `.pdata` attempt for the tiny setter exited 1 (`NO_OWNER`) and was resolved via precise byte inspection. The callback agent jobs were `rre-rc68-a-predicate-direct-call-index-20261111-01` and `rre-rc68-a-two-predicate-caller-windows-20261111-01`, exit 0.
- The addon/source auditor's hostname and source inspection ran on LEGION only (`rre-rc68-addon-audit-host-20261111-01`, exit 0). Main addon has no event polling; manual capture (`main.lua` lines 273-314, 410-411) and navigation introspection are not movement tracing. `SavedSource.cs` explicitly keeps `eventDeliveryVerified` and `eventComparisonReady` false.
- All direct source work was offline/read-only; no physical RIFT input, game UI, process access, VM/AMD, changes to other repositories, installer, provider usage or remote push. The RRE repository documentation updates are the sole writes.

## Prioritized next discriminating work

1. **Receiver listener identity:** one bounded original-PE virtual-table/registration-site trace for callbacks `vtable+0x08`; distinguish actual player movement consumers from unrelated UI/event subscribers before making movement claims.
2. **Minimal authorized live validation:** first verify physical RRECollector v0.4.19 load and exact capture receipt, then two timestamped position snapshots around a separately approved controlled movement/stop, compared to an independent physical-input timeline. Coordinates alone show displacement, not the native stop cause.
3. **Reader/source contract drift:** keep v0.4.19 offline acceptance documented and run narrow production reader checks; do not expand to VMware or legacy Lab2 testing on LEGION.

**Truth boundary:** The original program's ownership alias and callback delivery mechanics are demonstrated; its live use for player movement/stop is not.
