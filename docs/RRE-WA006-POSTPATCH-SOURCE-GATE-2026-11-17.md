# WA-006 updated-client offline source-map gate — 2026-11-17

**Machine:** AMD-DESKTOP, independently verified. **Build:** STABLE-1-1179-a-1256672, SHA-256 `df954b798331e18359be62a31cc74b49fc3f50b87385ebb080a5448256322c01`, 60,574,536 bytes. All evidence comes from the SHA-verified archived PE; **no RIFT process, gameplay, UI, VMware, memory read or addon was accessed**.

## Findings, exact scope

The old-build WA-006 32-byte sampling missed changed function bodies. A bounded re-search with 24-byte context windows found one candidate **callback at 0x6A67A1** (+0x4F0 from old 0x6A62B1), with 17 unique context matches spanning +200..+616. Seven relevant new-build functions are now source-window hash pinned:

| Candidate | RVA | Window bytes | SHA-256 |
|---|---|---:|---|
| Callback | `0x6A67A1` | 637 | `c0f122fa4dbc2f913bf2122774e3dab910075766dcbbe5a966a7001042d0d459` |
| Wrapper constructor | `0xF7CC20` | 160 | `46a977f8b898f29854e575f89a76070b940866367efe47489737e7350fc5d54b` |
| Wrapper | `0xF7CCF0` | 551 | `e3b35ee28826e26cab3ae20c69eb2e7b300d83c25447487cadeeab8dfe337eac` |
| Base constructor | `0x13E9A10` | 154 | `ce8d15a4c8da79057f84ddda275e237408b86382bbfa1a80e4fe51986710a27b` |
| Helper | `0x13E9F90` | 32 | `7d0edba6c599dcfcd1bee784bfeb6ba704ae6a72849b7d15b3edcfa8c811e073` |
| Parent query | `0x78B1C` | 261 | `5783c1af60da88a06759a7abd513ad17798b4cf1f5c68708d7faaafa50543696` |
| Virtual adapter | `0x9FD68` | 180 | `ed5bd9baca08a7727075b50b76bb290dfbc4e1bdb5a07d0acdc4279f6f98dc31` |

The following seven direct rel32 CALL source→target edges were independently checked with Capstone and a separate Python standard-library decoder:

1. `0x6A6986 → 0xF7CC20` callback→wrapper constructor
2. `0x6A69DC → 0xF7CCF0` callback→wrapper
3. `0xF7CC29 → 0x13E9A10` wrapper constructor→base constructor
4. `0xF7CDCE → 0x13E9F90` wrapper→helper
5. `0x13E9F9D → 0x78B1C` helper→parent query
6. `0x78B8E → 0x8E744` parent→query
7. `0x78BD0 → 0x9FD68` parent→virtual adapter

Seven deliberate in-memory mutations were rejected during source verification; no executable disk bytes were changed.

### Reproducible gates

`tools/postpatch_wa006_source_map.json` is SHA-scoped, human-readable static evidence. Its exact file SHA is pinned by `tools/verify_postpatch_wa006.py`, which independently rechecks both game binary digest and PE image mapping; validates seven exact source-window hashes plus seven call targets; double-hashes the PE to detect an update race; returns a JSON result and **never** promotes runtime or owner identity.

Run in PowerShell on AMD-DESKTOP:

```powershell
& 'C:\Python314\python.exe' -B 'C:\work\rre\tools\verify_postpatch_wa006.py'
& 'C:\Python314\python.exe' -B 'C:\work\rre\tools\test_verify_postpatch_wa006.py'
& 'C:\Python314\python.exe' -B 'C:\work\rre\tools\verify_postpatch_root001_b.py'
& 'C:\Python314\python.exe' -B 'C:\work\rre\tools\test_verify_postpatch_root001_b.py'
```

Expected successful source-gate statuses: `SOURCE_MAP_PINNED_ONLY` for WA-006 and `SOURCE_PINNED_ONLY` for ROOT001 B, **always with runtimeQualified=false**. Wrong file/manifest/bytes/call or malformed input must reject with `ERROR`, exit 3. Initial verified runs: WA-006 7/7 source windows/edges, 13/13 unit tests; ROOT001 B five opcode anchors, seven-QWORD vtable, two RIP-relative vptr assignments and processor call; 12/12 unit tests after rejecting malformed CLI flags with exit 3. These are **source-byte checks**, not complete function or live-player proofs.

## Remaining critical gaps

- **P0 — Find and prove the `wrapper+8` nonzero writer.** Current static path does not identify an owner or prove parent pointer is valid. Autonomous offline investigation; acceptance is a source-hashed writer/call chain or a documented negative.
- **P1 — Requalify WorldManager and object identity.** Confirm virtual-adapter receiver, conditional dispatch, related object layout and callsites. Offline first; acceptance is independent structural evidence, never just preserved bytes.
- **P2 — Controlled physical RIFT observation if needed.** Only with the current owner, fresh PID/start time/hash/module/epoch proof, and Joey's task-specific authority; acceptance requires independent Lua/native self-vs-target identity and matching same epoch. No movement/click/reload/restart implied.

Old SHA-pinned WA-006 replay tests remain historical evidence; **do not replace their pins** to obtain a green result. No old findings, addons, or sibling repositories were altered for this gate.

## Command evidence

- Callback relocation, source maps and Capstone call chain: `rre-postpatch-wa006-context-relocation-1117-1`, `rre-postpatch-wa006-newbuild-stdlib-edgeproof-1117-1`, `rre-postpatch-wa006-newbuild-source-window-hashes-1117-1` (exit 0).
- New manifest verification: `rre-postpatch-wa006-gate-real-first-1117-1` (exit 0).
- WA-006 synthetic/real regression suite: `rre-postpatch-wa006-gate-tests-1117-1` (13/13, exit 0; includes malformed-record negatives).
- ROOT001 new-build gate: `rre-postpatch-b-gate-vptr-final-real-1117-1` (exit 0).
- ROOT001 synthetic/real regression: `rre-postpatch-b-gate-invalidarg-regression-1117-1` (12/12, exit 0).
