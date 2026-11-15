# RC-64 — Native status-record queues and receiver initialization (LEGION)

**Verified static breakthrough:** Five direct calls to the RC-63 status writer, clustered in two .pdata-qualified functions, reveal two native record queues. A lazily constructed global root initializes its +0x350 receiver pointer to NULL. Type 5 has a separately decoded candidate filter. These findings are **not** proof of physical keyboard, player movement, or in-game stop.

## Host, build and method

- Independently verified host LEGION: job `rre-rc64-identity-legion-20261111-01`, exit0. Repo `C:\work\rre`, branch `main`, starting clean HEAD `5c29aadc1654414fc256dfe1050847f3e2b2549e` (ahead 19).
- Installed physical original `C:\Program Files (x86)\Glyph\Games\RIFT\Live\rift_x64.exe`, size 60,493,640, SHA256 `1935a05c9db6d468e34e0055014a4a99c1b5afceb1695884e24600f5c20a4be8`. Preferred PE image base 0x140000000; all values below are RVAs.
- Three independent read-only agents; one exact E8-rel32 scan of original 39,772,160-byte .text and bounded .pdata selected function windows. Sole manager independently verified source, decoded code, commits/docs. No AMD, VMware, live process/game, UI input, reload, install, Ghidra import, or push.

## Two queue routes and five writer calls

| Region | Original bytes / instructions | SHA256 |
|---|---:|---|
| Dispatcher `[0x7C0480,0x7C0673)` | 499 / 126 | `0aaaad0bc6f186ab172dee5c4bfa77647d9f406288b257266422a82140c1fa97` |
| Separate drainer `[0x7C1D40,0x7C1E1D)` | 221 / 54 | `acd9156d25be9ac21cd0bd2ef188f02b2777ed09a6c8355f69bf2ac5b0eaabef` |

At `0x7C04A0`, `0x7C0480` reads record type from `[RDX]`; `RCX` is receiver.

- Types **8–16** call `0x7C1AD0` immediately at `0x7C0590`.
- Types **5–7** call buffer helper `0x7C0170` with write pointer `[receiver+0x568]`, queue base `[receiver+0x560]`, then advance write pointer by **0x130** at `0x7C0580`.
- All other types call buffer helper `0x7C0290` with write pointer `[receiver+0x48]`, queue base `[receiver+0x40]`, then advance write pointer by **0x140** at `0x7C0522`.
- At `0x7C0595`, only when `byte[receiver+0xA40]==0` the dispatcher drains 0x140-stride records through `0x7C05DD` and 0x130-stride records through `0x7C0630`, calling handler `0x7C1AD0`; then resets write pointers to queue bases.
- Separate `0x7C1D40` calls the handler at `0x7C1D90` and `0x7C1DE0` for the same two queues, then resets both, without an internal +0xA40 gate.

Exact original .text scan found **five direct E8 callsites** `0x7C0590,0x7C05DD,0x7C0630,0x7C1D90,0x7C1DE0` in **two .pdata functions**. Indirect callers are not ruled out. Queue append helpers' internal copies were not independently decoded; call arguments and post-call strides are directly verified.

RC-63 remains valid: first handler region `[0x7C1AD0,0x7C1B7F)` SHA `967e6ae9c1220e9c8c5a3d72b9360710ac37d25a8d126f9eb00ba91caa0ef0a5`; imported VCRUNTIME140.dll!memcpy transfers 256B from record+0x19 to receiver+0xA41. Only types1/2/3 additionally copy record+0x124 to receiver+0x38.

## Type-5 special branch (original source)

If `[incoming+0]==5` and `qword[incoming+8]==0xE5`, `0x7C1AF2..0x7C1B3A` calls `0xFB4860 -> 0xFAFC70` for a candidate and `0xFB4860 -> 0xFB0460` for a candidate check. When check `AL==0`, the handler writes candidate to `incoming+8` and `incoming+0x124`; when nonzero, leaves them. Both paths copy the 256B table. **Type5 does not copy record+0x124 to receiver+0x38.**

| Source region | Bytes / instructions | SHA256 |
|---|---:|---|
| Wrapper `[0xFAFC70,0xFAFC90)` | 32 / 7 | `3422104dd2064935f40d0d408fa8a96e66f296a823a839593ba67e24c16bf088` |
| Filter `[0xFB0460,0xFB04C4)` | 100 / 35 | `3e730de156d9c9246c709b784a17fe84545a0a6f3f6a157ba0d04ff18326325b` |

Filter checks literal candidate codes including 0x2E, 0x77, 0x90, plus bitset and conditional checks; neither physical key labels nor gameplay semantics are proven.

## Lazy global root: receiver pointer starts NULL

- Getter `0x49A020` reads global RVA `0x33623E0`. Its expanded region `[0x49A034,0x49A108)` (212B/50 instructions) SHA `bbb77cac52655ff813082bd0f0cbeaa915dc561ed5f9ffe27b4bd8f7e838f269`; it allocates 0xF40 bytes via `0x78E110`, calls `0x53DC70`, and publishes the root pointer into the global slot.
- Constructor `[0x53DC70,0x53E773)` (2819B/516 instructions) SHA `ad5de6f4c667efdb89b2b9d3d0445ae55e45fb7b9dc024f688e3e77b26ce8e75`. `0x53DCCB xor r13d,r13d` precedes `0x53DDEA mov [rsi+0x350],r13`, which **initializes root+0x350 to NULL**. Accessor `0x7A3500` later reads this field; its subsequent writer and receiver class are unknown.

## Exact evidence and limits

- Lane A: `rre-rc64-callsite-exact-direct-rel32-venv-fixed-20261111-01`, `rre-rc64-callsite-two-pdata-source-functions-20261111-01` exit0.
- Lane B: `rre-rc64-receiver-getter-upstream-complete-20261111-01`, `rre-rc64-receiver-ctor-pdata-20261111-01`, `rre-rc64-receiver-zero-register-confirm-20261111-01` exit0.
- Lane C: `rre-rc64-type5-handler-decode-20261111-03`, `rre-rc64-type5-helper-decode-20261111-01` exit0.
- Manager: `rre-rc64-manager-original-baseline-stdlib-20261111-01`, `rre-rc64-manager-4window-original-independent-20261111-01`, `rre-rc64-manager-constructor-type5-independent-20261111-01`, `rre-rc64-manager-two-queue-detailed-20261111-01`, `rre-rc64-manager-type5-handler-independent-20261111-01` exit0. Independent **six full windows / 788 instructions** plus separate first-handler disassembly source checked.
- LEGION global Python314 lacked `pefile`; existing RRE `.venv\Scripts\python.exe` provided pefile/capstone; no package installed.
- Unknown: record origin before `0x7C0480`, who assigns globalRoot+0x350, concrete player/physical input identity, indirect callers, actual gameplay movement/stop.

**Next:** (1) one bounded producer/caller of `0x7C0480`, (2) one bounded writer to root+0x350, (3) separately authorized current physical RRECollector v0.4.19 SavedVariables and observed movement/stop. Stop the static chain if the next probes give no decision-changing evidence.
