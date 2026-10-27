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

## Pass 3 — Causal cast lifecycle and timing experiments (SC2–SC3)

### Candidate state machine (hypothesis, not yet native-verified)

`Known ability` → `current availability inspected` → `input/secure action attempted` → `locally accepted / queued / rejected / unknown` → `cast start / instant activation / channel start` → `cast end, interruption, cancellation or unknown` → `effect(s), miss/dodge/immune/resist or no observed outcome` → `readiness and resource recovery`.

Alternative paths must remain explicit:

- An **instant** ability may produce no visible castbar. Missing `castingTime` metadata must not be labelled instant.
- A **channeled** ability can have periodic ticks and interruption semantics different from a cast-time windup.
- A **passive/proc/toggle/continuous** ability can change state without the same active cast request or event structure.
- **Ground targeted** and other positioned abilities may require a second targeting confirmation. Do not reduce this to a single ordinary targeted click.
- A **melee-weapon-labelled ability** can still affect a target beyond melee distance (already seen with Light's Decree); `weapon`, `rangeMax` and actual hitbox geometry are independent.
- A successful cast request can yield a **dodge, miss, resist, immune** or no damage; this is distinct from the cast command never being admitted. Compare exact `abilityNew`, source/target and result type.
- Separate **client/UI/secure-action** admission from **server acceptance or validation**; the last two cannot automatically be inferred from API/UI frames, and actual packet/authority boundaries remain hypotheses.

### Define timing landmarks before any measurement

| Landmark | Evidence | Common trap |
| --- | --- | --- |
| `t_input_press` and `t_input_release` | Bound supervised operator/guest control receipt, with actual keypress-vs-release setting | Treat host delivery time as the instant the client acted |
| `t_local_admission / t_queue_offer` | UI/API change if exposed; otherwise **unknown** | Queue setting declared `Full` is not proof the command actually queued |
| `t_cast_start` and `t_cast_end` | Castbar begin/duration/remaining or relevant events, with source-time bounds | Castbar animation start is not independently proven server acknowledgement |
| `t_channel_tick[n]` | Exact caster+ability+target outcome sequence | Counting DoT ticks as repeated casts |
| `t_gcd_begin / t_gcd_end` | Correlated cross-ability readiness changes after a known activation | A 1.5 s *effective* ability cooldown is not itself proof of global GCD |
| `t_ability_cd_begin/end` | Ability-specific remaining and cooldown Begin/End events | Assuming base cooldown and observed effective cooldown are identical |
| `t_resource_change` | Ordered player Power/Mana/Energy/etc. samples | Resource regeneration after the ability makes the final value look unchanged |
| `t_effect / t_result` | Modern ability ID + caster/target + typed combat event; aura/buff/proc separately | Arrival after a projectile or channel tick mistaken for cast start |
| `t_host_receive / t_export` | Host receive/flush/save time, not the game frame clock | Subtracting guest `Inspect.Time.Frame` from host wall-clock time without calibration |

Each landmark carries `clockDomain`, `earliest/latest source time` (or null), event/sample ID, source hash, sampling precision and confidence. Use monotonic frame intervals for intervals **within the same source**, not absolute guest-vs-host subtraction. A 60-second capture with ~560 samples gives roughly 100 ms nominal spacing in previously saved evidence, **not** 1 ms timing precision. Missing intermediate frames widen the interval; no interpolation disguised as measurement.

**Minimal outcome claims:** `attempted`, `input-delivered`, `castbar-start-observed`, `cooldown-change-observed`, `target-hit-observed`, `target-avoidance-observed`, `source-unavailable`. The word `cast succeeded` requires a named acceptance definition, not just one changed timer.

### Distinguishing GCD from ability cooldown and other delay

Compare readiness of **at least two independent already-known abilities** with verified effective targets, costs and cooldown metadata. After one approved activation of A, observe whether B acquires a simultaneous/shared lockout even though its base cooldown is absent or separately known. Repeat against a third ordinary ability and, if the current catalog supplies a valid candidate, an off-GCD/control ability. Treat any observed shared pause as a **candidate GCD**, not necessarily its native timer.

Keep these variables separated in the evidence:

- `GCD policy` / ability family (possibly varying by ability or buffs).
- `Ability cooldown` / shared cooldown group / charge recharge / internal proc cooldown.
- `Cast-time windup` and haste or interrupt effects; instant and on/off-GCD are not synonyms.
- `Client ability queue` `Full / Short / None` and whether a queued command replaces an earlier queued request.
- `Input policy` "Use abilities on keypress" vs release, operator and transport timing.
- `Server/network RTT`, latency and time-of-day variability, visually delayed feedback, framerate/UI sampling; unknown until actual source timestamps permit an estimate.
- `Effect delay` from projectile travel, animation, ground placement, DoT/channel ticks and target outcome.

**Controlled contrast matrix** (each requires a separate supervised RR2 authorization and one-action ownership; REA only designs/reviews saved evidence):

| Trial | Single variable/question | Positive evidence / falsifier |
| --- | --- | --- |
| T1: ordinary instant ability | Effective cooldown vs independently observed shared lockout | A cooldown receipt plus B/C readiness snapshots; no claim of GCD without B/C |
| T2: `Full / Short / None` queue | Does next cast begin before, at or after active cast/cooldown completion? | Queue-mode screenshot, one bounded next-ability attempt, ordered cast transitions; mode alone is insufficient |
| T3: cast-time ability | Does predeclared cast time match castbar interval? | Explicit nonzero metadata, castbar start/end, event clock bounds; absent castbar is inconclusive |
| T4: channeled ability | Tick cadence and interrupt behavior | One channel start, each exact-ID tick, channel end/abort; no inferred packet clock |
| T5: distinct cooldown / charge | When do base timer, charge readiness and any shared lockout differ? | Two ability clocks plus recharge/resource traces, not just initial/final states |
| T6: negative readiness | Do range, resource, target or movement suppress request, cast, effect or cooldown? | Validated negative UI reason plus retained event absence under complete observation coverage |
| T7: hit vs avoidance | Can request reach target without damage? | Exact typed dodge/miss/resist/immune; separate from absent cast request |
| T8: proc/buff/ground effect | Does dynamic availability or repeated outcome map to one or multiple casts? | Proc/aura and exact caster/target/ability sequence; unknown if source lacks it |

Start with T1/T2/T3 and the smallest abilities available in the **existing RR2 catalog**. Use safe training targets, one action per reviewed attempt, bounded recording and physical STOP/recovery by RR2's owner. Later T4–T8 only after necessary source/event clocks are qualified. No unattended rotation, cooldown-spam loop, PVP target or health-loss requirement. Stop after two distinct non-decisive probes and record a new evidence trigger to reopen.

### SC2–SC3 acceptance

- **SC2:** at least one successfully observed outcome and one **different failure class** linked by immutable modern caster/target/ability IDs; label request, start, effect and cooldown as separate events.
- **SC3:** two independent ability-readiness traces with a predeclared clock mapping and sample bounds support or refute a *candidate* shared GCD; queue-mode observations are tagged by actual UI setting. Never universalize from the existing ~1.5 s and ~12 s historical recoveries.
- **Timing confidence:** one trial = observation; several comparable trials under explicitly constant conditions = repeatability evidence; timing distribution/model needs outlier, jitter and source-freshness accounting. Unknown server path cannot be promoted to client-native proof.

## Pass 4 — REA-native investigation without whole-client dead ends (SC4–SC5)

### Use the working software and historical findings correctly

REA is already installed as `rea-agents@6.5.0` at `C:\work\tools\rea` with Ghidra 12.1.2; the current browser ChatGPT mode typically reaches it through the **existing** Workbridge CLI/MCP bridge. No new installation or agent framework is needed for planning.

Prior source-bound tool result: two original **large RIFT PE** investigations exceeded ~450 seconds during startup/import. A separately assembled **2,560-byte synthetic PE slice** was analyzed by REA/Ghidra in ~19.6 s, but it has relocated code with missing external callers/RTTI/data and does **not** prove original-program behavior. Raw headerless x64 was rejected by this Windows provider. Do not repeat the raw-x64 path or infer that a synthetic slice proves a real client call chain. See `docs/rea-small-pe-probe-2026-10-19.md`. When full context matters, prefer already-saved source-backed static byte scans and a justified bounded full-PE analysis; large binary jobs need explicit cost/exit criteria.

### Three selective native targets — only after an observed discrepancy

| Focus | Research question | Minimal anchor | Credible native evidence |
| --- | --- | --- | --- |
| N1: Ability identity and catalog | Is `Inspect.Ability.New.List/Detail` a projection of client-owned known-ability state, a UI catalogue, or another source? | Exact modern/legacy IDs and a role-scoped API-vs-UI mismatch | Reference to matching build-local code/data with a function caller/callee trail and input/output validation, not a text-name hit |
| N2: Cooldown, castbar and readiness | Where are effective cooldown, shared lockout, cast/channel and resource rules computed or exposed? | Same-session cross-ability readiness/castbar transitions from SC3 | Exact-build value-flow candidate tied to observed field changes or event emission; prove that it is per-ability versus common if claimed |
| N3: Cast attempt and queue path | What handles secure action or macro submission, stores any pending action and emits outcomes? | One cast, one rejection/queue decision, source-timed event IDs | Function/data-flow trace from input or game-API boundary to a local queue/dispatcher/state update; server acceptance remains unknown without separate proof |

Only after one of these anchors is qualified should we investigate:

- Shared cooldown groups, charge counters, procs/conditional abilities, Soul/Role change invalidation or rank/variant replacement.
- Ground-target confirmation, movement/facing/LOS and target identity.
- Client/server request protocol, sequencing and prediction/correction, **only if a separately authorized and lawful data source makes this observable**; do not derive a purported server rule solely from the client binary.
- Possible GCD/vs cast restrictions for PvP or different class/soul families; no generalization from one Warrior/dummy sample.

**Failure-case research must be discriminating.** `unusable=true` with full Power and cooldown zero (already seen for Discharge) is a useful hypothesis for another missing gate; it does not prove which one. In a native follow-up, formulate two competing explanations (e.g., proc prerequisite vs effect target restriction), locate the least expensive source-observable discriminant, and stop if neither source can answer. Do not scan all "cast" strings as progress.

### REA query ladder and stop rule

1. **Prepare target:** pin original shipped executable path, SHA-256, PE sections/arch, build version, RVA/image-base mapping, user supplied state/source evidence, already indexed native research. A user-reported update is not a new binary until bytes differ; do not import stale V1 pointer chains.
2. **Form one falsifiable hypothesis:** specify the exact ability ID and observed transition, proposed code/data anchor, source file, expected positive AND negative signatures, and result that would change the model. If only name-based folklore exists, stay API/UI-first.
3. **Cheapest answer first:** search existing REA evidence IDs/bundles, saved RRE native indexes/strings/RTTI/disassembly, then narrowly bounded REA `search_strings` / `search_procedures` / `xrefs` / `read_bytes` / function views **when supported by the active provider**. Do not assume every 207 MCP tool works on Windows Ghidra.
4. **Escalate exactly one function/region:** decompile a supported bounded procedure, record pseudocode *and* assembly source ranges, references, callers/callees and ambiguity. Use `inspect_analysis_view` on a retained Evidence ID instead of rerunning expensive analysis to retrieve another facet. If a native call's arguments/receiver ownership are unknown, report the unknown.
5. **Cross-check and decide:** check source PE bytes in the named RVA window and (where already authorized) compare saved RR2 API observations; classify `supported`, `disproved` or `unresolved`. Synthetic probe success is a tooling property only. Never equate source-backed code references with a successfully invoked game ability.
6. **Timebox and park:** one bounded narrow attempt per Chat turn, usually **30–90 s per tool job**, hard job limit **120 s** for this research track unless an expressly reviewed durable/resumable workflow exists. If import/startup exceeds the budget, retain the last artifact, label `provider-timeout` and switch to *existing* static evidence or a smaller question. **Two materially different non-decisive probes** park a hypothesis until new observed IDs, bytes or changes arrive. No retry loops or entire binary rescans as a default.
7. **Patch handling:** same original SHA permits reuse of **static byte-qualified** RVAs only (runtime ABI, ASLR, pointer lifetimes and code semantics still need proof). Different SHA starts an isolated build comparison and requalification of the selected spellbook/casting anchors, **not** a blanket update of prior offsets or identical function names.

### Required native function dossier

For every candidate create a small immutable dossier with `taskId`, `buildSha256`, `sourceFileSha256`, `RVA/start-end`, `virtual image base`, provider/revision, exact query/job ID, original machine bytes/range, method, pseudocode snippet references, caller/callee hypotheses, event/API observation IDs, competing interpretations, evidence confidence, failed attempts, reopening trigger and **one next bounded query**. Keep observed values and inferred meanings in separate fields.

### SC4–SC5 acceptance

- **SC4:** at least one source-pinned native finding that answers a **specific** unresolved catalog/readiness/request question OR a clearly qualified provider/target blocker with preserved evidence. An RVA/string match alone fails.
- **SC5:** classify representative failure/outcome states (rejected, queued, interrupted, dodged/missed/resisted/immune, target-changed and normal hit/heal) by actual saved events and supported semantics. Missing event coverage does not establish absence.
- **Never block SC1 catalog usability or SC2/SC3 behavioral analysis solely because Ghidra's whole-client import is slow.** They can advance from game API/observations while native attribution remains pending.

## Pass 5 — ChatGPT Chat-mode survival, frequent commits and durable resume (SC6)

**This is a first-class requirement**, not optional process overhead. Most work is in ordinary Chat mode; individual Chat/tool sessions can terminate, and a long Ghidra job or multi-stage plan may lose conversational state. The durable unit is **a reviewed Git commit plus a small on-disk evidence receipt**, not the assistant's promise to "continue" later.

### The short-cycle research transaction

**One Chat turn = one narrow REA question and one useful durable result.** Do not attempt to finish the whole roadmap in a single session. A suggested transaction:

| Point | Required action | What survives if Chat times out immediately afterward |
| --- | --- | --- |
| **0. Resume preflight** | Read `docs/REA-RIFT-SPELLCASTING-HANDOFF-2026-10-27.md` (~one page), this roadmap's `TASKS.json`, actual RRE Git HEAD/status and known job IDs. Confirm tool/target SHA and protect other worktrees. | The last accepted commit and old receipt; no need to rebuild context from chat logs |
| **1. Claim one task** | Select the first `ready` task with satisfied dependencies; write its hypothesis, inputs, owner, target file and bounded acceptance to a **small tracked task checkpoint** and commit it *before* a risky/slow probe. | The exact next action and source version are already in Git |
| **2. Execute one bounded probe** | Prefer existing API/UI/evidence; only when needed run one source-pinned REA query with a unique deterministic Workbridge request ID. Write raw immutable result into a new `artifacts/rea-casting/<task>/<probe>/` directory (not a shared overwrite). | Partial result/job ID remains in local artifacts/Workbridge journal |
| **3. Validate at the smallest scale** | Check source hashes, status/exit code, contradicting evidence and task acceptance. Run focused regressions for a code change. Mark `inconclusive` as a valid negative-result outcome if the evidence cannot support a positive claim. | Evidence remains honest even when a tool is unavailable |
| **4. Commit the finding** | Commit **the task's bounded finding + any changed research source + the updated task status and documentation**, with exact file hashes and expected HEAD. Preserve unrelated dirty/untracked files. Do not wait for several large tasks before committing. | Fully repeatable milestone; downstream work can begin next turn |
| **5. Write the resumption receipt** | Update the small handoff: result, Git hash, immutable artifact hashes/paths, exact unfinished job IDs, blocked hypotheses, one next command, and whether any inputs or live controls were used. Commit the handoff with the milestone or an immediate separate lightweight documentation commit. | The next chat reads only handoff+task register, not an entire prior conversation |

**Cadence:** target a Git checkpoint after **each completed submilestone or source-backed fact**, including a bounded *negative* result. No more than **one unresolved research lead** and **one or two code/document edits** should accumulate uncommitted before checkpointing. For unusually long work, commit the preflight/plan first; checkpoint between independent source-range probes. Every commit must be internally truthful; incomplete results are labelled `partial`, not `accepted`.

### Hard operational budgets (not promised wall-clock completion times)

- **Per Chat turn:** choose at most **1–3 focused read/analysis commands**, one hypothesis, and one validation/commit cycle. Cross-project handoffs count as their own task. If work becomes extensive, split at the next exact evidence boundary and commit the partial result now.
- **Tool job limits:** default ≤ **60 s** for focused reads/tests; ≤ **90 s** for ordinary REA analysis; no single Ghidra/provider attempt over **120 s** without a separately reviewed resumable execution strategy. Existing historic >450-second imports are explicitly non-default.
- **Cost gate:** if a task needs >one long import, unknown third-party agent support, installation, guest deployment or dozens of new screenshots, first produce an evidence-led split plan rather than launch everything from Chat.
- **No imaginary workers or background execution:** Workbridge has bounded command-job slots, not independent AI agents. Ordinary Chat calls do not create continuous unattended work between conversations. If an actual job persists, record its ID and status; never claim it continues unless the tool reports it.
- **No repeating blocked tools:** tool safeguard denial ends that route. If a job returns `unknown`, first inspect its saved job status/artifacts. Reusing the exact request ID is reserved for the same uncertain invocation; do not create a new ID to duplicate an in-flight request. If a provider fails after two distinct probes, park it and advance another independent task.
- **Validation budget:** for documentation-only findings, check task-register JSON, links, source hashes and `git diff --check`—**do not** rerun the entire 530+ RRE navigation suite. For actual research/source changes, run narrow tests immediately, and one complete relevant gate at a cohesive integration milestone.
- **Patch/ABI safety:** source SHA and current client identity are gating inputs, not incidental metadata. If a newer binary does not match, pause only the affected native task. The API-level spellbook research can still proceed if its own game/session evidence is qualified.
- **External ownership:** only RR2's established owner may prepare its live evidence; REA requests named observations/hashes and makes no changes in RR2/Workbridge repositories. No user permission to type/cast/attach follows from writing this roadmap.

### One-page resume packet fields

`HEAD`; `taskId` / state; `question / falsifier`; exact source/probe hashes; the **last passed check** and job ID/exit; immutable evidence paths; one next action; what **not** to redo; exact blockers and needed owner; cross-project boundary; `gameInputSent=false` unless separately and factually observed. A claim not represented in this packet should not become an accepted result.

The handoff file begins with the single next task: **SC-000 inventory of existing RIFT ability API and casting evidence, without new client input**. The first real research session should publish a compact baseline mapping before trying the GCD timing hypotheses.

### Milestone reporting and final useful outputs

A summary should show **knowledge gained**, not just tests or commits: current spellbook catalog coverage, unresolved *learnable-at-level* sources, lifecycle states mapped, GCD-vs-cooldown evidence, source-verified native dossiers, blocked questions and next experiment. Maintain a small `spellbook-catalog.jsonl`, `ability-availability.csv`, `cast-event-timeline.jsonl`, `timing-comparison.md`, `native-dossiers/` and `research-uncertainties.md` only **as each deliverable becomes real**. Do not precreate empty schemas/tools to simulate progress.

For every result label **source type** (`original PE`, `actual Lua API`, `UI image`, `live event`, `synthetic test`, `external documentation`), build/session identity, source-hash and known caveats. Source evidence may stay in ignored `artifacts/` if too large/private; tracked conclusions must include immutable digest and a recoverable path, and a portable sanitized export can be prepared later if necessary.

**Completion of this roadmap is not "all spells figured out."** Completion of an initial research tranche requires: (a) one verified known-ability list and explicit learnability gap, (b) a supported casting lifecycle from attempts to outcomes, (c) a testable GCD/queue model with qualified time uncertainties, (d) at least one genuinely useful native REA dossier *or* a named provider/data blocker, and (e) durable handoff/commits allowing a fresh Chat session to reproduce the result. Deeper per-soul and server-side mechanics become later evidence-gated increments.

### Five-pass review decision summary

1. **Scope:** distinguish *known / learnable / locked / usable / bound*, plus REA ownership and role/rank provenance.
2. **Existing evidence:** reuse RR2's actual modern ability APIs/events and grounded outcomes; no redundant binary-only spellbook scanner.
3. **Timing:** cross-ability GCD identification, cast vs channel vs effect, queue-mode and keypress/release controls, clock-domain uncertainty.
4. **Native RE:** concrete API-linked hypotheses, bounded original-build source probes and provider-stop rules; neither huge imports nor synthetic PE evidence can stall the catalog.
5. **Chat durability:** one useful result per short turn, **checkpoint commit before risky work** and **commit after every verified milestone**, exact job/artifact receipts, concise resume file and no silent background work.

**Next action:** begin `SC-000` in an ordinary Chat turn; existing source evidence first, no game input. Check this handoff and register, then commit the first source-backed inventory baseline.
