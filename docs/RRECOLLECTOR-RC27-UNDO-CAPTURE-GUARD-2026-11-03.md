# RC-27 — Reversible pinning and complete-capture preservation

**Date:** November 3, 2026 UTC. **Target:** physical-PC RIFT Live x64 RRECollector. **Release:** source and installed v0.4.9; physical runtime v0.4.9 **not yet verified**.

## Changes

- The browser now labels its destination `Pin to #N` rather than silently overwriting the next round-robin slot.
- `Undo pins` is disabled until a pin is made. On the first pin, it holds the complete pre-edit eight-slot in-memory baseline, original cursor, and exact character SavedVariables slot-table value (including absent/nil). Multiple pins can be undone as one session before Reload UI or logout. Undo restores old values without rewriting unrelated `latest`, `probe`, or `candidateLookup`.
- A failed or unavailable ability List/Detail capture no longer overwrites an earlier `captureComplete=true` snapshot or sequence. A valid complete capture still replaces it; an incomplete capture can replace an earlier incomplete capture when the List API exists.
- The working restricted Reload UI macro setup, readback, secure parent, and visible control placement are unchanged.
- Text/caption layout remains the v0.4.8 measured two-row design. The narrow lower browser legend now reads `No casting / polling` to make space for Undo.

## Focused verification

- **23** source-extracted Lua pin/undo assertions passed, including repeated pins, the nil-table case, invalid static/unknown selections, wraparound and exact restoration.
- **10** source-extracted Lua Capture-preservation assertions passed, including unavailable API, exception, incomplete result, previous complete record, successful full/partial captures.
- Existing **26** lifecycle, **25** control and **9** caption Lua assertions passed under a local Lua 5.3 interpreter with its DLL found on the host; no new dependencies installed.
- `luac64 -p` passed for changed addon Lua and new Lua fixtures.
- Candidate/TOC Node suite **6/6** passed; strict package test passed.
- Independent Extra High review: **APPROVE** exact RC-27 UI/main changes. It recommends tracking pre-existing partial-UI-startup cleanup and small-viewport geometry separately; no new release-blocking defect.
- Physical deployment: prior installed v0.4.8 hashes verified before copy. All ten previous installed files backed up in `artifacts/rc27-v048-host-backup-20261103`; only five changed package files copied, TOC last. Strict source/installed verifier: **10/10 SHA-256 matches**, manifest strict-pass.

## Exact live boundary and next test

The current physical SavedVariables record still identifies **v0.4.8**, 69 known IDs and a 96-entry candidate lookup; no v0.4.9 screenshot or real pin/Undo interaction was observed at this checkpoint. The physical RIFT window was not reloaded or otherwise controlled for this source/installation milestone. RC-26 remains open for a version-matched, reversible pin test and exact semantic before/after slot comparison. Do not restore a file on disk while the game holds stale in-memory values.

A previous source P2 risk remains: failure halfway through UI creation can leave partially constructed controls before a retry. The successful v0.4.8 normal-start path was physically verified, and the RC-27 change does not modify secure initialization. If a new startup fails, stop and investigate rather than issuing repeated /rre ui retries.
