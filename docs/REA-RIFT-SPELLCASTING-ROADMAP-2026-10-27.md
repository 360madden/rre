# REA / RIFT Spellcasting Reverse-Engineering Roadmap

**Created:** 2026-10-27  
**Status:** research plan, not live execution  
**Owner:** REA research workflow. RiftReader2 and Workbridge keep independent roadmaps and ownership.  
**Research repository:** `C:\work\rre`; installed REA tool package: `C:\work\tools\rea` (not a source-development checkout).  
**Companion task register:** [REA-RIFT-SPELLCASTING-TASKS-2026-10-27.json](REA-RIFT-SPELLCASTING-TASKS-2026-10-27.json).  
**Working rule:** one decision-changing finding per short ChatGPT Chat-mode turn; commit each stable milestone, negative finding or blocker together with its documentation.

## Purpose, research questions and definitions

Explain **how the RIFT MMO actually exposes, authorizes, queues, executes and reports player spells and abilities**, from discovery to completion and failure. Produce an evidence-backed model that remains useful across sessions/build changes. We are researching the game's mechanics and binary implementation, **not** building or operating a rotation bot.

The research must distinguish five sets, rather than treating a spellbook list as every spell available at a level:

| Set | Meaning | Where it may be established |
| --- | --- | --- |
| K — Known | Abilities currently reported as learned/owned for this character and active context | RIFT API list/detail + spellbook UI cross-check |
| L — Learnable now | Currently eligible to learn/unlock *but not necessarily already owned* | Soul trees/root and branch thresholds, mastery, class trainer, rank, requirements; separate evidence needed |
| F — Future/locked | Seen in the game's UI or data but unmet level, soul points, role, quest, mastery, trainer or access requirements | Explicit UI/game data; **not** absence from API alone |
| U — Usable now | Known ability that passes the current target, resources, restrictions, timing and environment | Fresh API readiness and actual qualified response; varies by instant |
| B — Bound | Subset visible on an action bar or macro | Action-bar snapshot, **not** the source of the complete catalog |

Track character **level, calling/class, active role, selected souls, point allocations, ability rank/variant, mastery/legendary/planar state when applicable**, and exact game build. A character may have known passive/free abilities, abilities not on action bars and items/buffs not equivalent to native spells. Do not classify by ability name or generic tooltip alone.

Research outcomes to explain:

1. Exact spellbook/ability identities; learned vs learnable vs unavailable; active role and level changes.
2. Ability data: targets, requirements, range, cost, type, rank, status, effects and metadata unknowns.
3. Request path: keypress/key release or secure action → local UI/queue → any exposed request/acknowledgment → cast/channel execution → event/effect.
4. Independent clocks: effective per-ability cooldown, shared GCD, cast duration, channel ticks, queue window, resource consumption, server/network delay and animation/projectile/effect arrival.
5. Failures and exceptional semantics: no target, range/facing/LOS, health/death, silence/stun/movement, insufficient resource, disabled abilities, missing proc/stealth/combo/weapon, interrupt, target changed, dodge/parry/immune/resist, lag, pet/ground targeting and off-GCD cases.
6. An evidence-qualified state machine with alternative hypotheses marked unresolved and source-pinned native call paths where the client executable supports the claim.

## Scope and evidence authority

- **REA research**: bounded static PE analysis, symbol/string/caller/value-flow dossiers, build comparison, hypothesis classification, experiment design, synthesis and reusable findings.
- **RiftReader2**: owns installed Lua addons, current game telemetry/capture, secure in-game controls, deployment, supervised experimental trials and its own development commits. REA may **read and cite** its existing reports, but does not edit RR2 or acquire a gameplay-control lease in this plan.
- **Workbridge**: file/command/Git transport only; six job slots do not equal six AI researchers. Do not modify its service/roadmap as incidental setup.
- **Proof tiers**: G0 raw source/binary bytes with hash; G1 API/UI description; G2 repeated bounded in-game observations; G3 client-native code/data-flow established for that exact build; G4 proposed end-to-end explanation supported by G2+G3 and explicit remaining server-side unknowns. A label such as `SpellCast`, RVA or cooldown field alone is not G4.
- **Safety**: research read-only by default. No live game input, debugger attach, memory patch/injection, process manipulation, guest installation or bypass of anti-cheat/secure-action constraints under this roadmap. Future supervised actions require the separately authorized RR2 owner and the game's permitted input path. Raw event files/credentials stay protected; no leaking private tokens into git.
- **Build gate**: historical pinned RIFT PE SHA-256 `7c356c9dde9e12fcbff3c08d953b0630b48b1510a0ffb36e4ec164606e7b17bd`. RR2's October 26 evidence also reports this hash, but **every future observation** must bind its own file hash, process/VM epoch and role/session. Reuse code RVAs only after qualifying the exact file. Absolute process pointers never transfer between runs.

## Milestone ladder (overview)

| Phase | Target outcome | Minimum verifiable exit |
| --- | --- | --- |
| **SC0 — Baseline** | Sources, capability and build inventory | Known evidence catalogued; no unsupported "spellbook complete" claim |
| **SC1 — Spellbook** | Known/learnable/future/usable/bound separation | One character-role inventory with IDs, unknowns and UI/API reconciliation |
| **SC2 — Cast lifecycle** | Deterministic observed state vocabulary | Cast request → effect or rejection cases mapped without conflating acknowledgement with result |
| **SC3 — Timing** | Distinguish GCD, ability cooldown, cast/channel, queue and delay | Controlled clock-aligned contrasts; unresolved clocks remain explicit |
| **SC4 — Native REA tracing** | Selective client-side call/data-flow dossiers | Exact-build source-backed native leads with disproving tests and stop criteria |
| **SC5 — Exceptions** | Targeting, resources, buffs, procs and failure semantics | Matrix of representative ability families and event outcomes |
| **SC6 — Integration** | Traceable mechanism map, exports and handoff | Reproducible bundle, verdicts, gaps and resumed next task; no live automation claim |

**First useful result:** validate what `Inspect.Ability.New.List/Detail` currently enumerates versus the spellbook UI for a *single* saved role, then identify the first learnable-but-not-known test case. Do **not** start by dumping the entire binary or implementing cast automation.

## Pass 2 — Evidence coverage, spellbook semantics and concrete first deliverables

### What is already grounded (do not rediscover by scanning)

| Source | What it establishes | What it does **not** establish |
| --- | --- | --- |
| RR2 `docs/reference/spelldump-api-reuse.md`; source SHA `b9243cfe34a9436eca742e682d71f243506a70b253f3bcbaf2f962810feb6e7d` | On the actual client, `Inspect.Ability.New.List()` plus batched `Inspect.Ability.New.Detail(ids)` enumerates a current **known-ability** catalog and returns selected descriptive fields. | Full list of every unlearned or level-eligible trainer/soul spell; correct offensive/melee categorization from heuristic labels. |
| RR2 `addon/RiftReader2Casting/model.lua`; source SHA `82aa8395a36fbc2c3f83ff32392dcb4bbc43aa6bd18fd39a4339ab01c264a812` | Existing Lua model retains exact lookup ID/name, costs, range/cast/channel/cooldown fields, live player/target state and observed castbar. | Independent GCD, authoritative future skill prerequisites, exact server acknowledgement. |
| RR2 `docs/validation/casting-ranged-2026-10-26.md`; source SHA `87336f71d597dccab933818b577d3e4455d765afff801c1c7008e709c0fc878e` | Source-bound Light's Decree exact-target damage and dodge attempts, 560–565 samples, Power and cooldown changes. | A universal range limit, exact GCD clock, LOS/facing, projectile flight time, or all ability families. |
| RR2 `docs/reference/riftmeter-api-reuse.md` | Existing independent addon code uses `Event.Combat.abilityNew`, caster/target, dodge/miss/resist/heal/overheal/mitigation. | Names alone cannot prove a matching ability; one event is not necessarily a complete cast. |
| RIFT official [Ascended Class System](https://riftgame.com/game/ascended-class-system/) and [Soul FAQ](https://support.gamigo.com/en/support/solutions/articles/201000105428-rift-soul-system-frequently-asked-questions) | Soul branch/root point allocation and different Roles influence the abilities a character can possess. | Specific active character point totals, rank learned, unseen eligibility or unlocks. |
| Official [RIFT Action Bar Settings](https://support.gamigo.com/en/support/solutions/articles/201000105468-rift-action-bar-settings) | Queuing `Full/Short/None` and "use abilities on keypress" are separate user settings; unlearned abilities can be cleared from bars on soul reset. | The precise milliseconds, client-side queue data layout or protocol on this build. |

**Key research improvement:** build a **three-way reconciliation**: current API list ↔ on-screen spellbook/soul tree ↔ action bar. Save unknown eligibility as unknown. A level-45 Warrior and a different active Role do not necessarily share the same spellbook. "At level X" is not enough without calling, soul points, role, acquisition requirements and unlocked content. Do not infer all skills from the character's level.

### Catalog field contract (research export; not an RR2 feature request)

Create a source-pinned, role-scoped inventory record with:

- **Identity:** game build SHA, character ID/level/calling, shard if essential to provenance, active role, soul allocation/version when observed, source timestamp/sequence, raw lookup ID, modern ability ID if reported, legacy event ID if separately observed, name, rank/variant and owning group when known.
- **Metadata:** cost/resource type, `castingTime` (zero vs missing), `channeled`, `cooldown`, `rangeMin/rangeMax`, target type, `positioned`, `passive`, `continuous`, `autoattack`, `weapon` and any flags actually present. Raw values remain alongside interpretations; unobserved fields are `null / unknown`, not false/zero.
- **Availability dimensions:** `known`, `learnableNow`, `futureOrLocked`, `usableNow`, `boundToBar` — each separate tri-state `true/false/unknown` with a reason and supporting source. A temporary cooldown changes usability, not whether the player knows the spell.
- **Acquisition hypothesis:** soul branch/root, class trainer/rank, mastery/legendary, planar attunement, quest/event/reward, pet/companion, profession/item, or other. These are **candidates to verify**, not claims that every system exposes a directly enumerable spellbook.
- **Display:** UI spellbook tab, displayed tooltip/rank, action-bar or macro binding if observed; duplicate names or related ranks cannot be merged absent stable ID correspondence.

Export the original observations plus a derived `catalog.csv` and `availability-diff.json` for inspection. The user-facing result should allow filtering by role, required level, acquisition status, source, cast/cooldown, passive/active, target and available-resource type; **REA reports findings**, while a future consumer application remains RR2's decision.

### Priority experiments to disambiguate learnability (no live action implied)

1. For **one existing character and role**, take one API inventory snapshot and one exact-time spellbook UI snapshot. Compare IDs/names/ranks and preserve missing/mismatched entries.
2. Inspect the **same level and active role** in soul tree/trainer screens for at least one **eligible-but-not-learned** ability, if present. Report that none was found only after a defined sampled coverage, not as a universal truth.
3. Where already saved evidence exists, compare two role snapshots to determine whether `List()` changes with selected role or retained learned repertoire. Do not change live roles solely for this roadmap.
4. Establish UI/metadata associations for upgrades, rank replacement, selected mastery/legendary variants or proc-granted abilities where visible. Classify unobserved parts as `unknown`.
5. Only if API/UI cannot explain a concrete discrepancy, open an **REA native hypothesis** for the missing list, role/point gate or data table; do not make binary scanning a prerequisite for finishing the initial known-ability catalog.

### SC1 acceptance

A small real catalog sample with exact IDs, a provenance label for each availability dimension, a bounded list of unlearned/locked examples **or a specific UI-data blocker**, and a discrepancy report. No magic "100% spellbook complete" claim. Publish a minimal source-verified inventory even if the broader eligibility model is incomplete.

<!-- REA-CAST-NEXT-PASS -->

