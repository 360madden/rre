# RC-32 — Retained nested-payload versions inside a v0.4.11 SavedVariables root

**Observation:** November 5, 2026, 15:51 EST. **Scope:** Read-only, SHA-pinned interpretation of the already-qualified physical-character RRECollector SavedVariables revision. No game actions, reload, addon changes, process inspection, or SavedVariables edits.

## Exact original-file receipt and version partition

- Source: original physical-character `RRECollector.lua` (private absolute path omitted); 74,216 bytes; observed SHA-256 `8321e9e3fa850c2b1500287cf72da4c0f4f29b47c1ad581b016a1de2a184c4ed`. It exactly matches the independently recorded 13:08 EST post-load file receipt in `RRECOLLECTOR-RC32-POSTLOAD-SAVED-2026-11-05.json`; **this is not a new file revision**.
- Root `RRECollectorData.addonVersion`: **0.4.11**. This field is stamped on the SavedVariables.Load.End callback in current `addons/RRECollector/main.lua` lines 325–359; it does **not** rewrite nested report versions.
- Retained `RRECollectorData.latest.addonVersion`: **0.1.0**, capture sequence **1**. The capture producer stamps `VERSION` at `addons/RRECollector/abilities.lua` lines 87–100; no saved **v0.4.11** known-ability capture is present in this file revision.
- Retained `RRECollectorData.candidateLookup.addonVersion`: **0.4.10**, report sequence **5**; top-level `candidateSequence` is also **5**. The producer stamps `RRECollectorRuntime.VERSION` in `addons/RRECollector/candidates.lua` lines 59–65; `main.lua` lines 155–164 replace the candidate report only on a successful recorded lookup. No saved **v0.4.11** candidate lookup report is present in this file revision.
- Retained `RRECollectorData.candidateAttempt.addonVersion`: **0.4.10**; not evidence of a new v0.4.11 failure/retry.

The independent source-branch review confirms that `main.lua` lines 337–359 intentionally retain a qualified prior catalog (same catalog version and valid counts) while updating the root addon's version. Hence a root 0.4.11 / nested 0.4.10 (or 0.1.0) combination is expected and **does not demonstrate that a v0.4.11 collection/retry was run**. It also does not prove that no unsaved in-memory action occurred, nor identify the writer process or correlate screenshot/session timing.

## Reproducibility and evidence tier

The existing strict `parseSavedLua` decoder from `tools/read-rrecollector-saved.mjs` parsed the single original file as literal data (no Lua execution). A bounded `node --input-type=module -e` read-only Workbridge job emitted **only** version strings and sequence integers after enforcing the exact full-file SHA: `rre_1105_1548_safe_saved_payload_version_audit_corrected`, exit **0**. The first ad-hoc formatter attempt exited 0 but had an over-escaped display regex, so its version labels were rejected; the corrected, independently cross-checked version extraction above is authoritative. No raw ability IDs, player names, character folder, or private source data were emitted.

**Acceptance effect:** Evidence for the physical v0.4.11 *installation, visible UI and saved root version* stays valid. **RC-32 live retry/recovery remains PENDING.** The missing RC-30 same-trial pre-Pin save and immediate post-Undo screenshot remain PENDING. SC-103 Legendary/Protector's Fury identity, SC-306 numeric Ability Queue mapping remain blocked; SC-604 remains interim. Do not request unnecessary repetition or promote old nested records to fresh v0.4.11 runtime evidence.

**Coordination:** Initial read-only Git/Workbridge inspection found `main` tracked clean at `d96da5a41e3f335c1eda9f032a8c8392fca19afa`, nine historical untracked main entries preserved, zero RRE owners/running jobs and incomplete historical job inventory. RR2/REA boundaries remained undisturbed. FreeBuff `--check` passed (job `rre_1105_1548_freebuff_readonly_preflight`, exit 0), but it executes no AI model; its four fixed review pairs concern previously exercised topics and were not rerun. This was one manager-only bounded evidence audit, not an independently commissioned model review.
