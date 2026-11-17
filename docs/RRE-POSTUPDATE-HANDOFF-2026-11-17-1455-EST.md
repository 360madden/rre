# RRE post-update continuation handoff — 2026-11-17 14:55 EST

## Verified resume identity

- Machine: **AMD-DESKTOP** using the named Workbridge connector, root `C:\work`; repository `C:\work\rre`, branch `main`.
- Last independently tested and pushed **source** HEAD before this handoff document: **`45acb31574af98b7c62d3d4983297b398750278a`**, equal to `origin/main` at that checkpoint. The handoff commit will advance HEAD; recheck on resume. No unrelated tracked changes; **nine historical untracked entries** (seven old backup folders, one raw JSON, one Ghidra probe script) must remain untouched.
- Do not assume this SHA at resume: independently recheck host, `AGENTS.md`, Git state and concurrency. Physical RIFT only, **no VMware**; no game input/process/memory/reload/restart without fresh task-specific approval.
- Old build `STABLE-1-1177-a-1256632`, archived executable SHA-256 `1935a05c9db6d468e34e0055014a4a99c1b5afceb1695884e24600f5c20a4be8`; new build `STABLE-1-1179-a-1256672`, SHA-256 `df954b798331e18359be62a31cc74b49fc3f50b87385ebb080a5448256322c01`. Offline archives live under `C:\work\RIFT-Build-Baselines\<SHA>\rift_x64.exe`.
- Read-only Update Helper evidence `C:\work\Update Helper\PATCH_EVIDENCE_2026-11-17.md` independently confirms **seven modified game files, two removed download records, 0 added**, and two stable post-update 272-file captures. This is file provenance, not compatibility proof.

## Verified/pushed increments this afternoon

1. `6297f309` — SHA-pinned old/new B state-object source verifier and regression tests; WA006 singleton report.
2. `c4acdba0` — Path A `InGame` guard source anchors; WA006 alias-negative report.
3. `e3ae565c` — Update Helper manifest reconciliation, lazy state-singleton provenance and WA006 base/vtable source report.
4. `45acb315` — exact **same-object state1→2** source regression anchors and tests.

**Offline verification: 60/60 passing** — `tools/test_verify_postpatch_root001_b.py` **24**, `tools/test_verify_postpatch_wa006.py` **13**, `tools/test_rift_update_analyzer.py` **13**, `tools/test_verify_prepost_root001_layout.py` **10**. Real archived-PE ROOT001 and cross-build gates returned **`SOURCE_PINNED_ONLY`**, WA006 gate **`SOURCE_MAP_PINNED_ONLY`**. `functionIdentityQualified=false`, `runtimeQualified=false`, `ownerQualified=false` where applicable. `git diff --check` passed.

## Research state and evidence limits

- **P0 ROOT001 B:** normal host allocation `0xA50` at `0x762394` and constructor `0x75BE50` install vtable RVA `0x26CD000`; selector virtual `+0xB8` maps to `0x7664D0` and keyed host registry `+0x240` with static `InGame` B registration. Two `InGame` state-setter paths `0xFCEFFE` and `0xFCF5CF` and their guarded argument flow are source qualified. **Live active receiver/adapter remains unobserved.**
- **Path A state transition breakthrough:** `0x4C4180` is lazy 0x1B8 singleton getter (global RVA `0x337D2C8`), initial DWORD state `0`. Path A passes desired `1` into manager `0x9D57D0`; helper `0x9D58B0` checks state `1` and null `+8`, then `0x9D58D8` writes **DWORD `2` to that same object's `+0`**. Path A `InGame` requires first DWORD `2` plus eligibility/context gates. This proves a *possible native branch*, **not a current client runtime event or the gameplay meaning of value 2**.
- **Cross-build B layout:** actual corresponding B allocation path changes `0xA8→0xA0`, B state field `+0x20→+0x18`, flag mask `0x01→0x80`. Pinned tests prevent silent regression.
- **WA006:** `!91b4eae3` key is **copied**, not hashed by `0x52DD00`. Wrapper constructor `0xF7CC20` allocates 0x68 and registers global singleton RVA `0x3373C58`; 72 RIP references / 30 aligned functions. Base clears wrapper+8; child backpointers and a hash-table entry at `0x7326B5` are **not** wrapper+8 writers. Consumers `0x13EA600` / `0x13E9F10` forward `[wrapper+8]` to helpers. **No same-instance nonzero `wrapper+8` writer or manager service identity proven.**

All fine-grained RVA/opcode details, job receipts, and evidence qualifiers are in **`docs/RRE-POSTPATCH-SELECTOR-RECOVERY-2026-11-17-1406-EST.md`**. Consult it rather than repeating scans.

## Ranked next actions

| Priority | Action | Reason | Acceptance | Execution |
| --- | --- | --- | --- | --- |
| **P0** | Seek fresh task-specific approval for **read-only physical RIFT active-receiver qualification** with exact PID/build/owner checks | Source proofs cannot establish actual adapter selection | One verified current-instance receiver/adapter identity, or a fail-closed result with no game mutation | **Joey approval required** |
| **P1** | If offline work remains preferable, analyze guard `0x81BFF0` and state-manager transitions only where relevant to P0 | Domain/branch meaning remains unknown | Evidence-backed, bounded new call path or explicit negative | Autonomous, offline |
| **P2** | Trace WA006 derived-wrapper indirect setter aliases beyond proven base/child consumers | Nonzero same-wrapper `+8` writer unresolved | Same-instance writer or narrow negative with clear coverage | Autonomous, offline |

**Stop line:** No live compatibility, actual `InGame` execution, active receiver, WA006 owner, or gameplay behavior was asserted. No running game/client, controller, VM or sibling repository was changed. Commit and push verified new milestones only; preserve nine unrelated untracked entries.
