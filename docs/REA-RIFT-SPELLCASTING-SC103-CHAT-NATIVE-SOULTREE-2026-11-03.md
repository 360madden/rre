# SC-103 — User-provided native Soul Tree image: Righteous Defender and zero Legendary counters

**Evidence date:** 2026-11-03 (conversation upload, not verified in-image capture time).
**Source:** Joey's in-chat PNG `image(7).png`, verified in the model-side container at `/mnt/data/image(7).png`; **3,191,033 bytes**, **1910 × 1035**, SHA-256 **`4c232df9d7aa76f07f9fcd2e2c321dc9180a6f6c536cadab4b865a4569b290ce`**. PNG has no capture-time metadata. The file was supplied directly in the conversation, not acquired through Workbridge desktop capture or verified against an original physical-PC Screenshots folder image.

## Direct visible observation (G1: one operator-supplied native UI view)

| UI region | Visible text / data | Qualification |
| --- | --- | --- |
| RIFT native Soul Tree dialog | `SOUL TREE` centered above the three trees | Direct image content, not an addon-derived approximation |
| Character portrait | `Atank`, displayed level **45** | Displayed/effective level; actual unmentored level not verified |
| Bottom role picker | **Righteous Defender** | Selected/displayed role label in this image; no current-PID session attestation |
| Left tree | **Void Knight**, **15 points**, `Max Legendary: 0/2` | Counter is visibly zero of two; the specific semantics of "Max" are not independently API-documented |
| Center tree | **Paladin**, **45 points**, `Max Legendary: 0/3` | Counter is visibly zero of three |
| Right tree | **Paragon**, **0 points**, `Max Legendary: 0/1` | Counter is visibly zero of one |
| Bottom-left summary | `Points Spent: 60`; `Points Remaining: 0` | 15 + 45 + 0 = 60 |
| Partial right-side RRECollector | `Known: 69`, `Static: 96`, and text resembling `Candidate: saved 58 queries` | Ancillary, partly obscured; no readable installed-addon version and **no RC-30 Pin→Undo proof** |

**Defensible interpretation:** In the shown **Righteous Defender** Soul Tree, each of the three native Legendary counters displays a numerator of **0**. This is direct visual evidence of the *displayed* Legendary allocation/counter state in that screenshot, which is more directly relevant than old candidate-catalog `soul` strings or saved `player.role` metadata. It does **not** reveal an actively selected Legendary ability, a modern exact Protector's Fury variant ID, which ability would become available at another level, the character's true unmentored level, or other role slots.

## Comparison with existing RRE evidence

- Prior **SC-102** screenshots established Atank's displayed level 45, Righteous Defender and 45 Paladin / 15 Void Knight / 0 Paragon points. The new in-chat image **independently shows matching UI labels and adds clearly readable Legendary counters**; it is not evidence that the role changed between observations.
- **SC-103 historical publisher research** describes Legendary choices as Soul- and role-specific, historically tied to progression at levels 66–70. Do **not** automatically apply that 2016 rule to this exact modern game session or assume displayed level 45 is the account's true maximum level.
- Prior **SC-103 M3 no-go** found that the previously saved v0.4.10 `RRECollector.lua` predates physical RIFT PID 33936 and its 96 `candidateLookup.entries[].soul` labels describe the static catalog. This new chat image resolves the *visual role/counter observation* gap for the image **without** qualifying current PID, input controls, exact spell ID or fresh SavedVariables.
- **No native tooltip for Protector's Fury is open** in this image, and **no Legendary selection change** is shown. A native Soul Tree can display possible Legendary ability descriptions without proving the Legendary is actively selected.

## Session and provenance boundaries

- This chat upload alone does **not** prove that the image was captured from PID **33936**, HWND **16585300**, nor its exact capture UTC timestamp, current executable SHA, actual mentoring status, or current client state after the upload. Windows process/window inventory in other independent checks is not bound to the image bytes.
- It is one user-supplied **G1 native UI snapshot**. It does **not** meet G2's repeated/current source-qualified in-game observation threshold, and it does not grant G3/G4 native code or end-to-end gameplay mechanism proof.
- No original physical Screenshot-folder PNG match was verified; this report keeps the exact **chat-uploaded byte hash** as its provenance anchor. No raw image is committed to RRE, and there is no claim that Workbridge created a new screenshot.

## Revised SC-103 action and precise next discriminator

**SC-103 remains BLOCKED for rank/variant/modern exact-ID mapping.** It now has direct visible role, points and Legendary counters for **this image**; zero counters cannot identify a selected Legendary variant.

1. **Preferred non-mutating next observation:** In a native Soul Tree, keep the active role and points visible and hover **Protector's Fury**, then capture its actual tooltip alongside the native Legendary counter. The tooltip must display which state (if any) is visibly selected, not just Normal/Legendary *possibility* descriptions. Current unmentored/effective level and role-slot identity should be separately qualified if available.
2. **If variant selection is the actual test:** Only a separately source-qualified role/character **with a visibly selected Legendary ability** can prove selected-variant behavior; do not infer one from the current 0/n display or change this character's role as a prerequisite without a separate authorized trial.
3. **If a matching exact ID is needed:** Correlate with a separately approved, sanitized and documented `Inspect.Tooltip()` ability identity or a newly justified role-bound List/Detail delta. Do not export raw target/unit IDs, invent a Legendary ability ID, or replay the parked native Ability.List forwarding trace.

**Other gates unchanged:** Physical RRECollector **v0.4.10 remains frozen** until RC-30 eight-slot → Pin → Undo → Reload UI and fresh version-matched SavedVariables proof; Workbridge desktop capture `DESKTOP_TREE_UNSETTLED` quarantine is not bypassed. No client process, input, addon, VMware guest or other repository was modified to create this evidence.
