# RC-84 — combat feedback from the existing casting observer

**November 11, 2026, LEGION. Functional offline reader integration.** RRE previously had no supported consumer for the installed casting observer's trial records. Reader0.2.4 now provides source-hashed combat feedback through one command:

```powershell
dotnet reader/Rre.Reader/bin/Debug/net10.0/Rre.Reader.dll combat --input 'FULL_PATH_TO_RiftReader2Casting.lua' --repo C:\work\rre --output 'NEW_combat.json'
```

Direct Node use: `node tools/rre-casting-observation.mjs FULL_PATH_TO_RiftReader2Casting.lua`. Omit `--output` to print JSON. Existing files are never overwritten. No addon, observer, game process or gameplay input is changed.

## Result

The `rre-casting-evidence/1` report distinguishes exact-target damage, effective healing, overheal-only, matched miss/dodge/parry/resist/immune, missing outcomes and inconclusive observations. The latest reported readiness/reason and typed resource/cooldown fields are retained as historical sample data. A recording or aborted observation can contain an earlier positive event; that does not make the observation finished or establish present readiness.

This contract is separate from the ability `SourceCapture` contract. It invents neither an inventory nor a publication sequence. All live/freshness/process/source-authenticity/cast-delivery/action-authority qualifications remain false. Frame clocks are not wall-clock timestamps. File modification time and reader invocation time do not establish current execution.

## Evidence rules

- Initial selected ability Detail binds the trial's frozen modern ID and exact target. Sample identities, sequence and clock ordering are checked.
- Modern `abilityNew` presence takes precedence over legacy matching. Its mapping marker preserves that precedence even when an unsupported raw value was omitted by the observer. A wrong modern ID cannot be rescued by a raw ID or name.
- Positive outcomes require exact caster, target and ability matching, a clock within the recorded60-second window, and positive finite damage/heal/overheal. Names, cooldown, castbar, health loss and producer booleans alone do not confirm an outcome.
- Positive `lastHit`/`lastHeal` records can survive after the64-event list cap. Their source slot and kind must agree. Missing evidence with positive producer flags/reason is inconclusive. Capped arrays never prove complete history.
- The root's latest-trial alias is not counted twice. Archived producer versions remain unknown; unsupported older shapes stay unqualified without erasing valid current-load trials. A current root version does not rewrite historical verdicts.
- The producer's `last={status="unavailable",reason="readout-update-failed"}` recovery shape preserves finished-trial feedback while marking the latest sample unavailable.
- Literal Lua is parsed, never executed. Only the exact collector and casting assignment contracts are admitted. Casting supports a practical32MB/4M-value consumer ceiling; original RRECollector2MB/100k defaults stay unchanged. Explicit Lua nil is treated as absence for optional-field/ID precedence, while false/zero retain their meanings.

## Validation and actual availability

Installed observer source was read-only audited at v0.4.0: model SHA256 `dbd689b9f47140e95153a583e47a445ae3ac35794d293cf58c5d58e1143ce2bc`, main `7e24d78eeaf589bf76a7e4d59b4f6be5242d8c8d4947448995c33a60da945213`, TOC `f957e327c793073293ffbfc29d98411d9cf1ded9cea5738a0cc42cfbd087d6b0`. These source versions do not prove the currently loaded game addon version.

- **90/90 Node tests:**24 combat regressions plus existing saved/quest/navigation checks. Cases include identity mismatch, modern precedence, capped lists, zero/absorbed damage, overheal, malformed clocks/flags, Lua nil, readout failures, old archives, exclusive output and path-free errors.
- **99/99 C# production contracts** passed; build passed with warnings treated as errors.
- **8/8 actual Node/.NET adapter checks** passed, including CLI output, modern-ID rejection, original byte hash, executable-Lua rejection, unavailable input and unchanged collector SavedSource behavior. Synthetic artifacts: `artifacts/combat-checks-bdc34d165cdc4964b71d5082b6c2b11d`.
- A16-trial/630-sample-per-trial regression exceeds the old input limit and passes. Independent in-memory capacity review also parsed25,021,049 bytes including the serialized latest-trial alias, producing33,658 bytes of summary. These are synthetic capacity checks, not combat observations.
- The historical full research gate ran once for this integration: `artifacts/rc84-research-gate-20261111-2218/validation.json`,507 tests, overall **FAILED** with the same10 validation helper errors,2 collision fixture/source errors,9 pathfinding errors/1failure and2 navigation skips seen before this feature. Its source inventory stayed unchanged during execution. The final narrow Lua-nil correction followed that gate and passed the90 Node/8 adapter checks. No old-build hash was rebaselined and no full-suite pass is claimed.

The bounded fresh original-save read failed with Node `UNKNOWN(-4094)`; current genuine trial counts remain **unverified**. The earlier empty-trial observation is historical, not refreshed here. No cloud hydration/retry or copying of private original content occurred.

RRECollector source remains frozen at v0.4.20/a2d9660. The pending request for RRECollector-only deployment, UI reload and read-only quest/ability capture remains unanswered. This reader increment performs none of those actions. The seven-hour practical RRE/REA goal remains active.

Coverage clarification, November11: a later command audit found a profession-suite filename omission. Profession coverage should use the explicit12-check RC88 receipt (`artifacts/rc87-profession-correction.log`) and final correct suite inventory, rather than this earlier aggregate coverage description. Historical counts and hashes are unchanged.
