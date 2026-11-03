# RRE / RRECollector — session handoff (2026-11-03)

**Owner:** REA/RRE research manager. **Target:** physical-PC RIFT Live x64, not VMware. **Repository:** `C:\work\rre`, branch `main`. **Verified starting HEAD:** `90afd7ce2491234215fd2024a5e18dd63e1ef6ef` (SC-103 bounded Ability List descriptor trace). This is a resumption checkpoint, not a claim of fresh in-game testing.

## Resume gate and safety

1. Read `AGENTS.md`, `ROADMAP.md`, `docs/REA-RIFT-SPELLCASTING-ROADMAP-2026-10-27.md`, both SC/RC task registers and the canonical `docs/REA-RIFT-SPELLCASTING-HANDOFF-2026-10-27.md`. Recheck HEAD, status, jobs, ownership and any newer handoff before doing work.
2. Preserve existing unrelated untracked entries; at this checkpoint Git had no tracked changes and these eight untracked entries: `docs/rc18-v042-host-backup-20261102/`, `docs/rc19-v043-host-backup-20261102/`, `docs/rc20-v044-host-backup-20261102/`, `docs/rc21-v045-host-backup-20261102/`, `docs/rc23-source-backup-20261102/`, `docs/rc23-v046-host-backup-20261102/`, `docs/rea-raw-probe-profile-2026-10-18.json`, `tools/agents/ghidra/prepare_raw_probe.py`.
3. Current RRE scope does not authorize ChatGPT-operated game input, process control, injection, privileged changes, other repository edits or new addons. The operator handles in-game clicks/commands. The permitted deployment scope is only the RRECollector addon with backup, TOC last and source/install hashes. Do not disturb the live RIFT session.

## What is verified

- **RRECollector v0.4.10** source/physical installed package **10/10 SHA matches**; all **107/107 source-extracted Lua assertions** and eight Lua syntax checks passed for RC-30. Joey's original 646×612 screenshot, SHA-256 `6d4060ede113ad1f055419a80193ba561bee313d8895f540901e7846ea6c1dfb`, visibly proves v0.4.10 toolbar/browser loaded with **69 Known / 96 Static**, plain rectangular controls, `Pin to #1` and initially disabled `Undo pins`. It does **not** prove actual Pin→Undo, stale saved-slot rendering or persistence.
- **Latest saved Atank collector data still reports v0.4.9**, write time `2026-11-03T04:12:44.514Z`, SHA-256 `0303d1cde261cf7096c1a65651c9e07a725eb9c99c43889a02793ad9214b94d3`. No version-matched v0.4.10 post-Pin→Undo save has been observed. **Keep physical v0.4.10 installed and unchanged until this gate closes.**
- **RC-29/SC-103 atlas:** 353 distinct exact IDs from 323 historical Warrior IDs plus 69 current-known IDs, with overlaps removed. Of 96 candidate entries, 51 returned Detail, 7 returned no detail, and 38 were already listed/not queried; 50 were newly unlisted positives, 49 with `unusable=true`, one passive without that field. These are metadata responses, **not** learnability or castability.
- **Six historical Paladin tooltip candidates:** five current Detail responses, one no-detail (Protector's Fury, historical ID `A0E2112FD6FE262EE`); four historical UI cooldowns closely match current Detail. Historical UI and current responses were not simultaneous. The existing runtime `Inspect.Ability.New.Detail` documentation has **34 returned fields**, all exported by collector, but no documented rank/Legendary/unlock field.
- **SC-103 native trace** at commit `90afd7c`: physical on-disk `rift_x64.exe` 60,493,640 bytes SHA `1935a05c9db6d468e34e0055014a4a99c1b5afceb1695884e24600f5c20a4be8`; verified List descriptor and related bytes. A forwarding jump was found at RVA `0x12942a0` toward `0x78e110`, but no matching unwind boundary/callback semantics; one job intentionally stopped at exit 1, the bounded 96-byte check exited 0. **Actual list enumerator/Legendary state reader remain unresolved.** Do not repeat the unchanged trace without a discriminator.
- **Workbridge desktop capture is quarantined** after `DESKTOP_TREE_UNSETTLED`; a retained exclusive lease requires owner-verified process-tree recovery. Do not delete its lock or bypass quarantine. Workbridge reported v0.16.4-dev and 36 command/coordination slots; slots are not independently spawned AI agents.

## Next prioritized work

**P1 — RC-26/27/30 live Pin→Undo→normal save (operator-controlled).** On visible v0.4.10, note original eight pinned slots. In Known select **Aggressive Block**, click **Pin to #1**, verify slot #1 changes, then click **Undo pins** and verify slot #1 returns to **Summon Banker** and all other slots remain original. **Do not reload between Pin and Undo** (Undo baseline is in memory). If Undo fails or the baseline is uncertain, stop and diagnose before any save. Only after Undo is confirmed, use **Reload UI**, inspect fresh v0.4.10 SavedVariables version, pin data and source hash. Separately test a deliberately available stale saved-ID case; do not fabricate one or overwrite saved slots.

**P2 — RC-31 UI polish, after P1.** Implement the reviewed contract: page-aware selection validity so Pin/Check cannot act on an earlier page's item; disabled state until a valid API-known selection; retain distinguishing words in long captions; simplify redundant `[API]` browser labels and test text/interaction layout. Keep the working restricted-context Reload UI macro and plain button visuals unchanged.

**P3 — RC-32 reliability repair, after P1.** `abilities.lua` normalizes at most 512 IDs yet passes uncapped `rawList` to batch Detail; skip batch on incomplete/duplicate/ignored lists and use bounded per-ID fallback. `candidates.lua`/ `main.lua` may overwrite a useful prior candidate result on explicit Detail exceptions; preserve prior useful report/sequence and record bounded `candidateAttempt` with error status. Nil/no-detail without exception remains legitimate negative data. Use the detailed source-hashed fixture contract in `docs/RRECOLLECTOR-RC32-RELIABILITY-PREFLIGHT-2026-11-03.md`. No actual oversize/error failure has yet been seen live.

**P4 — SC-103 rank/Legendary identity.** Prefer a current, role-bound native Soul Tree screenshot showing actual Legendary selection, then an operator-qualified/sanitized `Inspect.Tooltip()` type/identifier observation or separately approved ability event delta. An RRE-authored icon hover is not a native Soul Tree hover. Don't export volatile unit/target IDs and don't equate absence from the known 69 with locked/unlearnable.

**P5 — Screenshot service recovery.** Request Workbridge owner to check quarantined process-tree identity before releasing the desktop lease; do not auto-retry the affected capture until cleared.

## Handoff references

- `docs/RRECOLLECTOR-RC30-STALE-PIN-DISPLAY-2026-11-03.md`
- `docs/RRECOLLECTOR-RC32-RELIABILITY-PREFLIGHT-2026-11-03.md`
- `docs/REA-RIFT-SPELLCASTING-SC103-ABILITY-LIST-DESCRIPTOR-TRACE-2026-11-03.md`
- `docs/REA-RIFT-SPELLCASTING-SC103-RUNTIME-ABILITY-DETAIL-DOCS-2026-11-03.md`
- `docs/REA-RIFT-SPELLCASTING-SC103-353-ID-DETAIL-ATLAS-2026-11-03.json`
- RC-31 test contract in commit `2419382`; RC-32 audit commit `0f6bb77`.

**Per-milestone workflow:** evidence source/hash → focused tests and independent review if available → strict TOC/package checks for addon changes → physical installation with TOC last → separate current-version runtime proof → update SC/RC registers and canonical handoff → roadmap validator, Git diff checks → narrow local commit. Do not claim a physical behavior from source tests alone.

## Copy-paste resume prompt

> Resume the RRE spellcasting workflow from `C:\work\rre\docs\REA-RIFT-SPELLCASTING-SESSION-HANDOFF-2026-11-03.md`. Read AGENTS.md, canonical handoff, ROADMAP.md and SC/RC task registers; reconcile HEAD, dirty files, worker ownership and live tool state first. Keep physical RRECollector v0.4.10 unchanged until the operator completes RC-30 Pin→Undo→Reload UI and you verify a v0.4.10 SavedVariables receipt. Then implement reviewed RC-31 UI and RC-32 reliability fixes with tests, review, guarded deployment and narrow commits. Continue SC-103 with source-qualified current Soul Tree/Legendary evidence; do not redo the parked native descriptor trace or bypass screenshot quarantine. Report observed vs unverified distinctly and preserve unrelated files.
