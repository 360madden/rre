# SC-103 — Physical-client Ability.New.List descriptor trace (bounded stop)

**2026-11-03 UTC. Status: read-only static-byte verification and callback/dataflow stop; SC-103 rank/Legendary mapping remains blocked.** One already-documented native descriptor path; no broad PE scan, full decompiler import, game input or process control.

## Build and original-byte provenance

- Physical installed RIFT Live x64 PE: **60,493,640 bytes**, SHA-256 `1935a05c9db6d468e34e0055014a4a99c1b5afceb1695884e24600f5c20a4be8`, freshly recalculated and matching the saved `docs/REA-RIFT-SPELLCASTING-SC404-NATIVE-ANCHORS-2026-10-27.json` evidence. This is on-disk identity, not an in-memory call trace or live role-state binding.
- Existing List literal RVA `0x26d6618`; its descriptor pointer at .data RVA `0x2f62d60` equals VA `0x1426d6618`. Adjacent Detail pointer at RVA `0x2f62d78` equals `0x1426d6650`; descriptor word at RVA `0x2f62d28` is zero. These are API-related literal references, **not** proof of a callback.
- Previously qualified descriptor-related code interval RVA `0x9b0376–0x9b0776`: exactly 1,024 original bytes, independently rehashed SHA-256 `5e474301f73f561abb8d2f1d023d42f556eb7311eec5085099e9494d11a9dc52`, matching `docs/REA-RIFT-SPELLCASTING-SC401-XREF-2026-10-27.json`. Prior descriptor manipulation includes a call at `0x9b0573` to `0x12942a0`; it has not been shown to enumerate abilities.

## Bounded read-only Workbridge job receipts

1. `rre_sc103_ability_list_descriptor_trace_20261103_agent_a1`: **exit 1, intentional stop gate**, not an analysis pass. Verified full PE, original interval and descriptor qwords. The followed target RVA `0x12942a0` had **no matching .pdata unwind-function entry** in the bounded metadata lookup, triggering `no unwind bound; stop`.
2. `rre_sc103_ability_list_target_96b_20261103_agent_a1`: **exit 0**. Same PE SHA verified; first 96 bytes at RVA `0x12942a0` SHA-256 `500bf3e08c9700b07aa91496ba302a7c68fdcb859a905e8d0dae8fa411cfecd4`. First eight bytes `48 8B CA E9 68 9E 4F FF` directly indicate `mov rcx,rdx` then a relative branch toward RVA `0x78e110`; that branch target was **not traced**. Capstone was unavailable in configured Python; no broader function-boundary or parameter semantics are claimed.
3. No output file, debugger attachment, game input, installed-addon change or broad native scan. Both command receipts were independently retrieved by the manager.

## Decision and stop condition

- **Confirmed:** physical on-disk PE identity; original descriptor/literal references; source-region bytes; first-instruction forwarding pattern at followed target.
- **Not confirmed:** the actual `Inspect.Ability.New.List` callback, enumeration implementation, spellbook producer, Soul/Legendary state consumer, identity substitution or current Protector's Fury Legendary ID.
- **Stop:** no source-verified mapping from named List descriptor to a player-role/Legendary-dependent enumerator. A forwarding thunk or matching API string pointer cannot establish the gameplay semantics. Repeating unchanged native descriptor probes is parked until a concrete callback/dataflow discriminator exists.
- **Higher-value next observation:** current role/Soul Tree UI with visibly selected Legendary state, followed if feasible by one sanitized native `Inspect.Tooltip` identity sample or separately approved role-change event delta. Retain SC-412/SC-413 writer/error-branch probes as parked.

**Result:** One source-hashed native path reached a defensible registration-only evidence tier, not a rank/variant/eligibility conclusion.
