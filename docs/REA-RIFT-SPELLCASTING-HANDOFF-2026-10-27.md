# Resume REA RIFT spellcasting research — October 27, 2026

**ACTIVE REA task:** `SC-000`, baseline inventory of ability-catalog, castbar, cooldown and combat-event evidence. **Next question:** what is already *known to the current role* versus *eligible but not yet learned*? Do **not** start with a Ghidra full PE import or gameplay input.

## First reads on a new Chat-mode turn

1. `git -C C:\work\rre status --short` and `git -C C:\work\rre log -1` through existing Workbridge; preserve any dirty/untracked files and inspect any known command IDs.
2. This file (brief), [five-pass roadmap](REA-RIFT-SPELLCASTING-ROADMAP-2026-10-27.md) only for the current phase, and [task register](REA-RIFT-SPELLCASTING-TASKS-2026-10-27.json).
3. Exact saved references, not broad repository dumps:
   - `C:\work\riftreader2\docs\reference\spelldump-api-reuse.md` — raw `Inspect.Ability.New.List/Detail` ability catalog;
   - `C:\work\riftreader2\addon\RiftReader2Casting\model.lua` — fields, castbar and readiness;
   - `C:\work\riftreader2\docs\validation\casting-ranged-2026-10-26.md` — exact-ID ranged hit and dodge plus cooldown/power;
   - `C:\work\riftreader2\docs\reference\riftmeter-api-reuse.md` — exact event IDs and outcomes.
4. Build: RR2 October 26 records guest PE SHA-256 `7c356c9dde9e12fcbff3c08d953b0630b48b1510a0ffb36e4ec164606e7b17bd`. It is **historical**; any new game test needs fresh current identity.

## Work for one ordinary Chat turn

Claim **SC-000**. Write a small source-index/evidence matrix with exact report hashes and a bounded gap statement for spellbook eligibility; cross-reference ability ranks/role. First check saved catalog/UI evidence already in RR2. If the actual role-scoped spellbook UI snapshot is missing, record `blocked-by-current-UI-evidence`, **not** a newly invented native spellbook mechanism.

Use only normal Chat + Workbridge scoped reads. REA installed 6.5.0/Ghidra 12.1.2 is ready for later **selective native** hypotheses, but previous whole-client imports over ~450 s were wasteful and raw x64 is unsupported by its current Windows provider. Do not modify REA installation/Workbridge/RiftReader2; RR2 owns live addons and supervised cast controls. No unapproved live input, guest action, memory writing, injection, remote push or key/credential access.

**Durability rule:** commit the bounded preflight/hypothesis if a probe may run long; otherwise commit immediately after the first verified source-backed result. In each turn record job request IDs and source SHA, never rerun uncertain jobs under new IDs. Keep at most one unresolved lead; use focused validation, not a full native research suite for doc-only steps. A negative or blocked result with exact reason earns a truthful small commit.

## Status at roadmap creation

- Five roadmap improvement passes documented; each stable pass has its own local commit on RRE `main`.
- REA spellbook/GCD lifecycle **research not executed in this roadmap-writing turn**; prior RiftReader2 outcomes are source references, not new REA reverse-engineering results.
- `SC-000` is `ready`; later role/eligibility and live timing tasks depend on saved evidence / separate RR2 authorization. No source changes, external repository edits or game input were made.
- **Next milestone receipt:** initial source matrix, ability-list completeness limits, one specific next question, exact verification and local commit hash. Then hand off the next `ready` task. The project does not continue asynchronously between Chat turns.

**Recent review commits (first four):** `4f54b3f` → `2a4c6f6` → `b9461b3` → `d28ad55`. Read the actual latest `git log` to identify the fifth-pass/final handoff commit rather than trusting a hardcoded older HEAD.
