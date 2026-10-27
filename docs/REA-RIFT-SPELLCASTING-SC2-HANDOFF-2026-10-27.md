# SC2 PHASE HANDOFF — Observable RIFT spellcasting lifecycle

**As of:** October 27, 2026. **Status:** **SC2 COMPLETE (observed API/event layer only)**.  
**Owner:** REA research; RR2 remains the owner of any actual game trials and secure controls.  
**Scope limit:** no native/client server-side function, queue or GCD mechanism claimed recovered.

## Durable accepted output

- [Source-bound SC2 analysis](REA-RIFT-SPELLCASTING-SC2-LIFECYCLE-2026-10-27.md).
- [Machine-readable event timeline](REA-RIFT-SPELLCASTING-SC2-TIMELINE-2026-10-27.json), SHA-256 `1236f5eb182b38df50daa1f237070ea21ea9cfc94ac490908ace1b53a5f5e728`.
- Two historical Light's Decree attempts: **dodge** on intended target, then **402 damage** on same intended target with modern `abilityNew` ID `A6B8B16CD6F8B3DB9`. Cooldown Begin/End ~12 seconds each, Power 100→80→100. Other-target area damage excluded.
- Aggressive Block historical melee hit of **118 damage**, effective cooldown ~1.514 seconds, distinct autoattacks excluded; earlier RR2 range rejection and API `unusable=true` samples retained as **pre-activation** restrictions, not proof of native/server rejects.
- The sanitized host input record reports left-click inserted/released and `responseVerified=false`. Do not mistake it for game consumption, cast acceptance or timing proof. RIFT game-frame timestamps and Windows UTC timestamps lack a qualified mapping.
- No live input, attach, memory edits, new REA native function decompilation, RR2 source edits, service changes or Git push in this phase.

## Next bounded work

**SC-303:** use the existing 55-ID [catalog](REA-RIFT-SPELLCASTING-SC1-API-CATALOG-2026-10-27.jsonl) to isolate **cast-time vs channel metadata**, identify which safe examples would distinguish windup/channel ticks from effective cooldown, and list specific missing event coverage. This is *offline-only* research. Next SC-301/SC-302 shared GCD/queue contrasts remain blocked pending actual same-session cross-ability readiness and verified UI queue setting through RR2's independent supervised workflow.

**SC1 remains incomplete** despite SC-101 and SC-104 results: a native spellbook/role/soul/trainer UI sample is needed for learnable-at-level classification.

For resumption in normal Chat mode: verify latest RRE Git HEAD/status, read the independent SC task register and this one-page handoff, and inspect the exact input hashes in SC2 report. Do not reread full 5MB raw events if the saved summary suffices. Source validation job `rea-sc2-event-acceptance-20261027-01`; check its exit, then make a **separate durable commit for this phase**. Do not rerun SC0/SC101 or a whole-game Ghidra import.
