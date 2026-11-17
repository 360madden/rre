# RRE post-update continuation handoff — 2026-11-17 11:40 EST

## Resume identity and scope

- **Project:** RRE, `C:\work\rre`, `main` on **AMD-DESKTOP**. Named Workbridge connector independently reported `computerName=AMD-DESKTOP`, root `C:\work`, Workbridge `0.16.5-dev`. Do not assume LEGION or another connector.
- **Verified git:** `HEAD=3b20604b8cad50e1dba5819f19c4147223187a37`, matching `origin/main` at this handoff; `git status` shows no tracked changes. Nine historical untracked entries (seven `docs/rc*-backup-` directories, `docs/rea-raw-probe-profile-2026-10-18.json`, `tools/agents/ghidra/prepare_raw_probe.py`) remain untouched. Never stage/delete them without explicit review.
- **Scope:** offline/source-only postpatch RRE research. Both hosts' **physical** RIFT clients are the only potentially eligible live targets; no VMware operation. This handoff grants no game input, reload, restart, deployment, debugger/memory/process access, or runtime ownership. RC-30/RC-88 are stopped; FreeBuff/Ollama remain held. Coordinate with other live-client owners before any independently approved trial.
- **Game updated:** new physical/archived executable `STABLE-1-1179-a-1256672`, `60,574,536` bytes, SHA256 `df954b798331e18359be62a31cc74b49fc3f50b87385ebb080a5448256322c01`; previous `60,493,640`-byte SHA `1935a05c9db6d468e34e0055014a4a99c1b5afceb1695884e24600f5c20a4be8`. The new archived PE is at `C:\work\RIFT-Build-Baselines\df954b798331e18359be62a31cc74b49fc3f50b87385ebb080a5448256322c01\rift_x64.exe`.
- **Sibling helper:** `C:\work\Update Helper` tracks cross-project game-update deltas; read its evidence if useful, but do not overwrite its worktree or delegate RRE fixes there.

## Delivered, verified, pushed

1. `55c2c0d3018c97eee511071f8c14a9a5e8a00cdc` — two postpatch **source-only** verifiers:
   - `tools/verify_postpatch_root001_b.py`, `tools/test_verify_postpatch_root001_b.py` (**12/12 tests**).
   - `tools/verify_postpatch_wa006.py`, `tools/postpatch_wa006_source_map.json`, `tools/test_verify_postpatch_wa006.py` (**13/13 tests**); seven exact SHA-pinned windows and seven call edges; manifest digest `a8b8dbc2e5652af9b89849345c442ab6c9a6b50288d623237f45b9b5bd9b7f08`.
   - Existing `tools/test_rift_update_analyzer.py` **13/13 tests**. Independent reviews identified malformed CLI failure handling and manifest-read consistency; both fixed with regression tests before commit. Neither verifier accepts runtime gameplay identity.
2. `481d49b447349d60a9dc56428fb33b629fd3c223` — `docs/RRE-POSTPATCH-STATIC-LINKAGE-2026-11-17.md` bounded WA006 writer and B selector evidence.
3. `3b20604b8cad50e1dba5819f19c4147223187a37` — corrected WA006 global provenance and B selection identity gap; pushed to `origin/main`. Last `git push` job `rre-postpatch-alias-selector-push-1117-1` exit 0.

## Current P0 scientific evidence and boundaries

**ROOT001 / adapter B**

- New B vtable RVA `0x2721518`, virtual `+0x18 → 0xFCA0A0`; B prefix SHA256 `3069ebf7d3d72c4dd9882ebe0b5101edc8cbb831155909af619661443db3cbb8`; vptr seven-QWORD SHA256 `98e45c8e5dedb228c98e30cc58c17208fb094e0d7f23d788feb683351a00288e`. Independent Capstone source audit verified assignments `0xFC918A/0xFC9199` and `0xFC939F/0xFC93A9`, receiver register preservation, processor `0x788B00` and receiver+0x6A8 read `0x788C04`.
- `0x778BE9` allocates `0xA8` and `0x778C0E` calls B constructor `0xFC9170`. `0x778C56` accesses `host+0x240` container through `0x75DE60`, and `0x778C63` stores constructed B pointer at returned `node+0x30` value slot.
- Separate selection `0x776740` calls `[host_vptr+0xB8]` with `RDX=host+0x1F8`; non-null result is stored in `host+0x218` at `0x77679A`. Dispatcher `0x77A182` calls selected object's virtual `+0x18` with host in RDX. Prior selection receives virtual `+0x20` at `0x7766EA` if present.
- **NOT PROVED:** selector retrieves the B pointer from the +0x240 container; the selected live receiver, instance identity and owner remain unqualified. Do not conflate separate subchains.

**WA-006 / wrapper+8**

- Current new-build callback `0x6A67A1`, wrapper ctor `0xF7CC20`, method `0xF7CCF0`, base ctor `0x13E9A10`, helper `0x13E9F90`.
- `0x13E9A2B` **zeros** wrapper `[rcx+8]`; `0x13E9F96` **reads** it. Apparent early `+8` writes `0x6A695D`/`0x6A6970` occur before `0x68`-byte wrapper allocation at `0x6A6974`; `0x13E9A62`/`0x13E9A88` store wrapper backreferences to other small adapter objects, not the wrapper field.
- `0x6A6992` and `0x6A69A1` publish the wrapper **twice to the same** global RVA `0x3373C58`. A bounded scan found 72 candidate RIP-relative references across multiple callback clusters, including similar publications at `0x4A2997/0x4A29A6` and `0xF7DD84/0xF7DD98`. These are candidates, not 72 proven owner setters.
- **NOT PROVED:** any nonzero writer to the same wrapper's +8; owner binding; live callback occurrence or gameplay identity.

Read `docs/RIFT-POSTUPDATE-RECOVERY-2026-11-17.md`, `docs/RRE-WA006-POSTPATCH-SOURCE-GATE-2026-11-17.md`, `docs/RRE-POSTPATCH-STATIC-LINKAGE-2026-11-17.md` before continuing. All findings are static archived-PE evidence, not live acceptance. Independent bounded analysis job IDs and exact opcodes are in the latter report.

## Recommended small, timeout-resistant work queue

| Priority | Owner/lane | Action | Evidence gate / acceptance | Authority |
| --- | --- | --- | --- | --- |
| **P0 — recommended** | ROOT001 selector, exclusive read-only analyst | Resolve concrete host vtable and `+0xB8` selector implementation; connect container node+0x30 B value to selected pointer or prove mismatch | Reproducible instruction-by-instruction keyed lookup/return path on SHA-pinned new PE, independently checked; no unjustified instance claim | Autonomous offline |
| **P1** | WA-006 wrapper writer, independent read-only analyst | Trace wrapper's virtual setters and classify candidate references to global `0x3373C58` by ownership | Exact pointer provenance for any nonzero wrapper+8 store, or bounded negative with explicit coverage | Autonomous offline |
| **P2** | New-vs-old static diff, independent read-only analyst | Compare mapped callback, ctor, selector and wrapper methods between old/new archived binaries | Address-independent signatures, source-byte evidence and changed/unchanged paths | Autonomous offline |

Lead coordinator alone integrates evidence and modifies RRE docs/code; agents must have mutually exclusive read-only analysis lanes. Reuse installed Capstone, pefile, REA/Ghidra saved output; **do not** trigger a full Ghidra import. Run only bounded jobs (typically seconds, not long imports), recheck Git HEAD/dirty state before committing, preserve the nine untracked files, run relevant offline tests and `git diff --check`. Commit/push only independently verified milestones. Never count Workbridge command-job slots as independent AI agents.

## Continuation procedure

1. Independently verify named AMD-DESKTOP, `C:\work\rre`, actual HEAD/remote status, inherited untracked inventory, and current workers/jobs. Other RRE hourly automation or chat may have advanced the branch; rebase plan on **actual** state, not this historical SHA.
2. Read `AGENTS.md` physical-only override, `ROADMAP.md`, latest handoff, postpatch recovery + source-gate + static-linkage docs, and the two source-only verifiers.
3. Advance P0 selector analysis with a single bounded archived-PE task; assign P1/P2 to independent read-only AI workers if capacity and meaningful objectives exist. Require exact byte/RVA/branch evidence and second-method verification.
4. Integrate only accepted evidence into a concise document, test, commit, push as authorized, and give Eastern-time, measured-elapsed SITREP.
5. Seek a new, explicit game-specific owner/authorization only if offline evidence reaches a genuinely decisive live test; do not interact with physical RIFT otherwise.

**Current stop line:** no runtime B selection, nonzero WA006 owner writer, active RREC2 acceptance, or post-update in-game behavior has been established by these static gates.
