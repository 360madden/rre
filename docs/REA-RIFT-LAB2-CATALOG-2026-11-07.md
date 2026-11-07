# SC-610 — Lab-2 current-known ability catalog, November 7, 2026

Accepted scope: the existing RRECollector captured and persisted **54 unique current-known ability IDs and 54 Details** for **Bolinao, level 43 Rogue, role slot 1**, on Lab-2. The UI, saved root and saved snapshot all report **v0.4.11**. This is an API-known catalog observation; learnable, locked, usable, bound, cast/queue internals and server acceptance remain separate questions.

The [machine-readable receipt](REA-RIFT-LAB2-CATALOG-2026-11-07.json) contains the sanitized exact-ID catalog, source hashes, per-action original-image/review/result hashes and limitations. Raw SavedVariables, guest executable and original images remain local under `artifacts/lab2-live-20261107-0922/`; they are not committed. Work began from `30df4d4c80f4eb50229c4467a211d287d9bf6be6` on `main`. Observations span approximately 09:22–09:45 EST; recovery/cleanup was checked at 09:50 EST.

## Research method and reused instructions

The question and owned paths are **SC-610** in the [casting task register](REA-RIFT-SPELLCASTING-TASKS-2026-10-27.json). The [SC-605 playbook](REA-RIFT-SPELLCASTING-SC605-CUSTOM-ADDON-PLAYBOOK-2026-11-01.md) routes API-exposed unknowns through RRECollector first. The [M2 tool-routing contract](REA-RIFT-SPELLCASTING-OFFLINE-TOOL-ROUTING-M2-2026-11-03.md) and [casting roadmap](REA-RIFT-SPELLCASTING-ROADMAP-2026-10-27.md) keep this observation distinct from a recovered native mechanism. The [Lab-2 policy](REA-RIFT-LAB2-LIVE-TARGET-2026-11-07.md) and [external mouse procedure](REA-RIFT-LAB2-EXTERNAL-MOUSE-2026-11-07.md) govern the live route.

Reused without implementation changes: `tools/external-lab2-mouse.py` with installed host `vncdotool 1.4.2`, existing RR2 per-VM identity/mutex/credential helpers, the strict RRECollector package verifier, and the literal-only SavedVariables reader. No addon deployment, guest mouse package, new input backend, Ollama or new model execution occurred. FreeBuff capability check only; no suitable new bounded question was launched through its fixed older review modes. Command jobs are not independent model agents.

## Build and package provenance

- Sole live target: `RIFT-LAB-2`, VMX `C:\rift modding\VMs\RIFT-Lab-2\RIFT-Lab.vmx`.
- Before/after guest observations agree on RIFT **PID 9752**, process-start UTC ticks **639294897826627677**, executable `C:\RIFT_TRANSFER\RIFT\rift_x64.exe`, **60,493,640 bytes**, SHA-256 **1935a05c9db6d468e34e0055014a4a99c1b5afceb1695884e24600f5c20a4be8**. The host copy of that guest executable independently matches. The post-test observation is **2026-11-07T14:44:51.2510073Z**. These are bracketed file/process observations, not mapped-memory or continuous-session attestation.
- All **10 installed guest RRECollector files** byte-match current repository **v0.4.11**. The existing strict TOC/version/order/source-install verifier passed. A separately copied, recognized installed **BotDsBridge v0.3.3** TOC supplies an independent metadata reference, including `Email`.
- The initial loaded RRE UI was **v0.4.10**, with Known 0 and Static 96; the original character saved file was only 23 bytes, `RRECollectorData = nil`. Installation and load were therefore treated separately. A normal UI reload subsequently loaded the already installed v0.4.11; no source copy was made to the guest.

## Observed live sequence

Every input used the existing external tool with a fresh original before-image review, exact capture-ID approval, one action, button release, VNC disconnect and console-mutex release. Positions below are full guest-desktop coordinates, 1211×757. The machine receipt binds each action to its VM identity and original evidence.

| Action | Position | Direct observation |
| --- | --- | --- |
| RRE toolbar Reload, loaded v0.4.10 | 1125,335 | Immediate and later original frames still showed v0.4.10. Reload success **unverified**; no blind retry. |
| RRE Capture, loaded v0.4.10 | 1020,335 | Chat reported capture-complete, 54 IDs/54 Details; Known became 54. |
| Hover existing action-bar macro | 765,705 | Tooltip directly exposed both macro name and body `reloadui`. |
| Click that tooltip-bound macro | 765,705 | Addon shutdown/loading screen observed; original saved receipt v0.4.10, sequence 1, 54/54. |
| Hide occluding idle casting panel | 1015,238 | UI-only Hide revealed in-world RRE **v0.4.11**, Known 54. Panel was NOT RECORDING. |
| RRE Capture, loaded v0.4.11 | 1020,335 | At 09:39:14 EST, chat reported capture-complete, 54 IDs/54 Details. |
| Click existing action-bar reload macro | 765,705 | “Restarting RIFT UI” loading screen observed; matching v0.4.11 snapshot subsequently persisted. |
| Hide idle panel after reload | 1015,238 | Final original frame at about 09:42 EST showed in-world RRE v0.4.11, Known 54. |

Total: **seven left clicks and one hover move**. Two normal UI reload/save transitions were directly observed through the existing action-bar macro. There was no casting, movement-key input, recording start, controller restart or addon source change. Source inspection and the saved `registered/readback-matched` macro status do **not** establish that the first toolbar Reload click worked; its cause remains unknown. That old-loaded-version case is retained for later bounded investigation.

## Catalog and persistence result

The original v0.4.11 save is **21,670 bytes**, SHA-256 **5e2f8bab564fb4916dc87ba929fc3c1d022bab913bb7b4896cd2923197aae7fb**. Root/snapshot versions are both 0.4.11 and sequences both 2. Guest saved-file last-write UTC is **2026-11-07T14:39:49.3826873Z**, consistent with the observed save transition. The literal reader reports:

- API List and batch Detail available; **54 raw entries, 54 unique IDs, 54 Details**; enumeration complete.
- **Zero** duplicates, Detail failures, ignored entries, truncation or fallback calls.
- Player Bolinao, Rogue, level 43, role slot 1. Role labels are present; actual soul allocation was not observed.
- Client build `Oct 23 2026 11:32:27 RIFT-BUILD-12`, internal `STABLE-1-1178-A-1256632`, external `1.0.0`.
- v0.4.10 sequence 1 and v0.4.11 sequence 2 contain the **same 54 exact IDs**, with **zero name mismatches**.

The existing decoder qualifies the saved structure, while deliberately retaining `freshnessVerified=false`, `processBuildVerified=false`, `eventDeliveryVerified=false` and `eventComparisonReady=false`. A saved file alone cannot prove those properties. The separately retained original UI actions and before/after process/file observations provide this report's live provenance; they do not turn the snapshot into event/timing evidence. Reported frame/real times are retained in their original game clock domains, without UTC conversion.

Static 96 is the existing **Warrior** candidate list. This Rogue receipt reports `candidateAttempt.status=deferred`, reason `warrior-player-context-not-ready`. No Retry was requested and no Rogue eligibility, locked-spell or failed-candidate-lookup conclusion follows. Loaded research tiles also do not prove usable action bindings.

## Validation, cleanup and next gate

The strict installed-copy package verifier exited 0, v0.4.11, 10/10 SHA matches. Existing `node tools/test-rc30-saved-receipt.mjs` exited 0 with **15 passing tests**. Documentation integration also checks source/original artifact hashes, complete ID/Detail coverage, unchanged unrelated task states, JSON, links, `node tools/validate-roadmap.mjs`, and `git diff --check`. No implementation changed, so the full research test suite is unnecessary for this evidence-only integration.

Existing VMware Tools diagnostics were read-only observations apart from creation/removal of their own temporary JSON receipts; exact-path/hash-guarded cleanup was confirmed. An initial process-list formatting assertion and unsupported cleanup verb failed and were replaced with the existing supported read-only PowerShell observation and guarded cleanup route; neither failure was a RIFT build mismatch.

At final recovery, Workbridge reported **zero live command jobs**, and the RRE owner registry had **zero tasks/owners**. Historical job inventory remains incomplete. Every external mouse result records release/disconnect/mutex release. Native controller PID 41888 remains stopped for external mode. Preserve nine historical untracked paths and the independently committed SC-604 note. No background worker was launched.

**SC-610 is accepted only for this current-known catalog and its capture/save route.** SC-103 (Warrior Legendary/Protector's Fury identity/selection), SC-306 (queue enum), SC-604's broader native mechanism, RC-26/30/31/32 live acceptance and NAV-002 retain their prior gates. Resume by rereading the current [session handoff](REA-RIFT-SPELLCASTING-SESSION-HANDOFF-2026-11-07.md), then selecting a concrete remaining SC question applicable to the actual Lab-2 character. Reuse this exact-build source/capture baseline; do not replay captures or restart a competing native controller merely to recover context.
