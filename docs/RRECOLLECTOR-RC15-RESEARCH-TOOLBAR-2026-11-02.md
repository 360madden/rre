# RC-15 / SC-103 — RRECollector v0.4 on-screen research toolbar and candidate diagnostics

**Date:** 2026-11-02 UTC. **Owner:** RRE/REA manager. **Scope:** one additive, display-only module and physical-PC addon install; runtime toolbar and candidate results **not yet verified**.

## Why this increment

The user requested an ability toolbar that removes repeated spellbook navigation and shows whether an ability is currently usable. The prior v0.3 candidate lookup also had an observability gap: a **new** Atank SavedVariables flush at `2026-11-02T15:18:17.647Z` contains root `addonVersion="0.3.0"`, the preserved 69 known ability Details and v0.2 probe, but **no** `candidateLookup`. Saved-file SHA-256: `e08dfbb4e994e40a985992bc6be0b7f04d633c8e55a626c0cd632e9bd91fadfe` (31,081 bytes). This establishes a new persistence observation, **not** the reason the lookup failed. v0.4 now writes a small `candidateAttempt` status/reason on lookup deferral or completion.

## Single-addon source implementation

- One new `addons/RRECollector/ui.lua` loaded after `candidates.lua` and before `main.lua`; complete `RiftAddon.toc` fields remain, including `Email`, `Environment="4.4"`, and character-scoped `SavedVariables`.
- Draggable 636x110 research strip with eight known-ability icons; Browse, Check 8, Capture, Retry and Hide controls; `/rre ui` toggles the strip.
- Optional 636x452 eight-row paginated Known/Candidates browser; exact IDs, saved API-known versus historical static provenance, three-soul filter, description and base cooldown when available; selecting a known ability pins an ID into a bar slot and stores optional `RRECollectorData.toolbarSlots`.
- Clicking one icon or Check 8 performs **manual, bounded** `Inspect.Ability.New.Detail` rechecks of known exact IDs. State colors: red on explicit `unusable=true` or `outOfRange=true`; amber for a positive current cooldown or paused cooldown; grey for missing/inconclusive readiness; cyan only if `unusable=false`, `outOfRange=false` and `currentCooldownRemaining=0`. Cyan means *no blocker in those specific API fields*, **not** a verified game action-bar Ready/cast/GCD/LOS/facing verdict. No continuous polling, macros, targeting or casting.
- Candidate Retry calls the existing guarded `/rre candidates` policy, preserving previous successful `candidateLookup`, prior `latest`, and prior `probe`. New status is displayed on strip and `/rre status`; only bounded diagnostic codes are saved. Normal in-game UI reload/logout is still required for SavedVariables persistence.
- Additive implementation keeps v0.1 snapshot schema compatible. One package and one addon identifier; no other addon, RR2, game binaries, VM or process input changed.

## Physical-PC install receipt

Read-only preflight `rc16-toolbar-host-preflight-20261102-a1` passed **9/9** old v0.3 hash parity before writes. Installed changed `core.lua`, `main.lua`, `README.md`, and new `ui.lua`, then updated `RiftAddon.toc` **last**. Only `C:\Users\mrkoo\OneDrive\Documents\RIFT\Interface\AddOns\RRECollector` was targeted. Job `rc16-toolbar-host-install-20261102-a1`: **exit 0; 10/10** source/installed SHA-256 parity.

| File | Source and physical-PC installed SHA-256 |
| --- | --- |
| `core.lua` | `1e1e77eb0c2edc9c5248a7b4f838cb69606d86c3bc43897dc2031e37e4d47396` |
| `context.lua` | `f0e1750e815a7e43cbf4c36231ffd7f354b27a7b3636a23637de1c57129f5e10` |
| `abilities.lua` | `d181ba0061a5959474dd3487b41c114f631122375a8b67421817fd54fdc1c510` |
| `capabilities.lua` | `0ed3ccf0fad438008d9e76d0ec5ddeefd31b5b28c860ba523d53392659f202ef` |
| `candidate_catalog.lua` | `10dddab8779fdb6253fa372ca47632c2396e1d3a15edddb40c17c495bd3adccd` |
| `candidates.lua` | `f558b68cab4804f78bbff4d5d1c4a234a6973fbdce60c76d93be77b487c38e85` |
| `ui.lua` | `e16f8de7a1e703a2fc660d081700ed1f27d66e7d0f160a7ec54f6702fb53824d` |
| `main.lua` | `64b3a31ada2a4e01d6e928cdfdb0287403f2166d4382d3b9e37b8f430af316fd` |
| `README.md` | `59ad2557cc289725a90c3cd099130ecaa32b9d3c01af6c4f8720c9001959db56` |
| `RiftAddon.toc` | `82a18451d54992b98fd98ff3d24888dc038f64e555d5c28ad47fad7b9760e3b3` |

## Verification and next discriminator

- `rc16-toolbar-final-focused-20261102-a1`: **5/5 focused source/manifest/guard checks passed**; `rc16-toolbar-roadmap-validate-20261102-a1`: roadmap validator exit 0; `rc16-toolbar-diff-check-20261102-a1`: exit 0 (Git CRLF warnings only).
- Independent read-only Lua/RIFT API review found no confirmed bootstrap blocker. A Lua compiler/runtime was not installed; the review and five structural tests are **not** a live UI proof.
- **RC-08 remains open:** the next *operator-controlled* normal RIFT addon load plus save is needed to see whether v0.4 initializes, reports `candidateAttempt` and/or writes `candidateLookup`, and displays the toolbar. A manual `/rre candidates` retry remains possible if startup defers. No operator input was issued by RRE.
- If the UI renders behind native game frames, consider changing the UI context strata in a separate evidence-guided increment; drag motion may also stall when leaving the drag handle. Neither is a confirmed failure.
- For genuinely live action-bar availability, independently verify supported current-client ability usable/cooldown events or secure buttons, and correlate actual game state. The display-only scaffolding does not assert SC1 eligibility/rank, SC3 GCD/queue or native castability.

**Rollback:** source control retains pre-v0.4 v0.3 files; revert only this addon after comparing installed hashes, without touching existing character SavedVariables or other addons.
