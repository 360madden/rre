# RC-08: first persisted explicit-ID lookup

Date: 2026-11-02. Physical-PC RIFT, Atank Warrior, role slot 1, game build STABLE-1-1178-A-1256632 (Oct 23 2026 RIFT-BUILD-12). Character SavedVariables modified 2026-11-02T21:48:02.154728Z, SHA-256 2d472f9af0fdc15d0cb0889a75edbef7eedbc8f4c315438264eee0ffedf96b2d, 72,245 bytes. Read with tools/read-rrecollector-saved.mjs literal-only Lua parser, not evaluated or executed.

v0.4.4 root and candidateLookup report: API ready, manual trigger, candidateAttempt recorded. Original known snapshot (69 API IDs, version 0.1.0) and separate API probe preserved. Static catalog: 96 Warrior IDs (39 listed, 57 unlisted). Explicit Detail requests: 58 total, one listed control and 57 unlisted. Returned identifying data: 51, including 50 unlisted; no detail: 7; errors: 0; inconclusive: 0; skipped: 0. All 50 unlisted names agree with static-source names; no mismatch. Positive canary triggered bounded expansion.

Soul results among unlisted: Paladin 5/6, Void Knight 23/26, Paragon 22/25 returned. No-detail names: Protector's Fury, Void Summon, Unstable Void, Void Presence, Flurry, Rising Waterfall, Alacrity.

RC-08 accepted at current-client explicit-ID response scope. Arbitrary-ID Detail return does NOT prove that an ability is learned, learnable, slotted, unlocked or castable. SC-103 rank/eligibility and SC-3 GCD/queue remain open. Do not repeat this same 96-ID capture without a new discriminator.
