# RC-17 — Native RIFT toolbar buttons and startup retry

**Date:** 2026-11-02 UTC. **Target:** physical-PC RIFT. **Release:** RRECollector v0.4.1. **Accepted scope:** source/install, not new-version runtime.

## Screenshot and diagnosis

- Joey supplied an in-chat physical-PC screenshot of v0.4.0 RRECollector showing eight toolbar icons, a Known/Candidates browser, Known 69, Static 96 and the exact candidate startup deferral warrior-player-context-not-ready. The TOC had loaded correctly.
- User screenshot hashes: expanded toolbar 0cb774eb029f6250a8530a23c077efdb95b85de8b00ecc81a20e8783a9cad38b; full-screen c6a7051559299fcddd2d665a365e3de1d8e332756d5f836edf261f23b85be757. These are conversation images, not the older 162-file physical Screenshots-folder audit.
- Previous 0.4.0 buttons looked flat and lacked apparent hover/depressed feedback. Local installed addons JAB, Gadgets, Rustys_Action_Bars demonstrate RIFT native RiftButton; ApiAtlas and ApiBrowser provide pointer-state patterns.

## What changed in v0.4.1

- UI commands use native RiftButton, preserving existing click actions while supplying game-native hover, depress and disabled visuals. Selected rows/tabs, pagination and ability tiles gain explicit visual feedback. Toolbar remains read-only: no ability casts or continuous readiness polling.
- When a SavedVariables startup lookup defers for exact reason warrior-player-context-not-ready, main.lua tries again only via Addon.Startup.End or the player entry in Unit.Availability.Full, up to two automatic retries. Successful lookup stops retry; failure preserves prior latest/probe and manual Retry. The candidateAttempt receipt tracks automaticRetries.
- Full RiftAddon.toc manifest retains ten required fields (including Email and Environment 4.4) and eight scripts in dependency order. Existing schema 1 SavedVariables remain compatible.

## Validation and host deployment

- Source Git commit 95c64d5fac5fdc424f495e596dbb18434a6e9b4f; parent fa459beb.
- Focused source checks 6/6 passed: rc17-rre-focused-20261102-a1. Strict source TOC pass: rc17-rre-toc-source-20261102-a1. Diff check passed: rc17-rre-diffcheck-20261102-a1.
- Deployed only C:/Users/mrkoo/OneDrive/Documents/RIFT/Interface/AddOns/RRECollector through reversible host journals rc17-rre-v041-host-stage1-20261102-a1, rc17-rre-v041-host-stage2-20261102-a1, then manifest last rc17-rre-v041-host-toc-last-20261102-a1.
- Strict installed verifier rc17-rre-v041-install-gate-20261102-a1 exited 0: version 0.4.1, manifest strict-pass, sources 10, installedShaMatches 10, runtimeUiVerified false.
- Important changed hashes: main.lua 4c6f74f19c47a2f3bfdf51ab0f276f146a897d4eb45d9f66d87c8f1ff395fe87; ui.lua eb5dcc7c292c997e56b2b8b84f58c300646191e6f3b10d3675271208a589406e; RiftAddon.toc 068018823649fc720dbf9219fee994aca6d9082118e51f6e075632d6630cfed4.
- Independent addon-source audit found no confirmed RIFT API mismatch with native button calls or player availability event table values. This is not a live test.

## Remaining open gate

- The visual evidence verifies previous v0.4.0 only. v0.4.1 is installed on disk; the currently running game will load it on the next ordinary operator-controlled UI load. Do not claim runtime proof or candidate success yet.
- On that next load, check hover/press briefly. The next normal SavedVariables flush will show candidateAttempt.status/reason/automaticRetries and optional candidateLookup, while retaining original 69 known records and probe.
- RC-08 remains open until that actual saved receipt. Availability, GCD, rank/eligibility and native casting remain unknown. Rollback only RRECollector with verified before/after hashes and reversible journal, preserving any newer operator changes; no RRE-owned game input.
