# Five-pass critique and refinement: REA RIFT spellcasting roadmap

**Date:** October 27, 2026  
**Scope:** improve the research plan, prevent Chat-mode timeout waste, and make every accepted finding persistent. No live game input or native Ghidra import was part of these five reviews.

| Pass | Problem exposed in initial idea | Change made | Outcome and durable checkpoint |
| --- | --- | --- | --- |
| **1. Correct scope and ownership** | "Every spell at current level" is ambiguous; native reversing and RR2 implementation could get conflated. | Defined `Known / Learnable now / Future-locked / Usable now / Bound`, actual Role/souls/rank, REA research ownership and separate Workbridge/RR2 lanes. | Source-scoped milestone ladder + task register. Commit `4f54b3f` |
| **2. Stop rediscovering verified features** | Unnecessary spellbook-memory scans would duplicate RR2's `Inspect.Ability.New.List/Detail`; API enumeration does not expose all unlearned skills. | Reuse source-pinned RR2 Lua and exact-ID combat evidence, add UI/API/action-bar reconciliation and tri-state availability, rank/variant handling, spell origins. | SC1 acceptance + tasks SC-101..104. Commit `2a4c6f6` |
| **3. Avoid wrong GCD/delay conclusions** | 1.5-second effective cooldown, 12-second timer, input latency, queue and cast time risk being conflated. | Define independent event/clock landmarks and cross-ability tests, `Full/Short/None` queue and keypress/release contrasts, channels, cast-time, resources, range, misses and explicit uncertainty. | SC2/SC3 trace and experiment protocol. Commit `b9461b3` |
| **4. Prevent native-analysis dead ends** | Original 60 MB RIFT binary has previously timed out in Ghidra; synthetic PE fragments lose context. | Use only concrete API-linked hypotheses; source-hash/RVA/ABI checks, retained REA evidence, bounded single-function probes, two-probe stopping rule and explicit provider limitations. | SC4/SC5 research and failure-case gates. Commit `d28ad55` |
| **5. Survive ordinary Chat session loss** | Long sessions/large prompts can time out; uncommitted findings and unknown job states lead to rerunning expensive work. | One narrow task per turn, milestone **preflight commit before costly probes**, **postfinding commit with evidence**, immutable artifacts/job IDs, concise handoff, focused tests and honest partial results. | SC6 + one-page recovery handoff + final independent tasks, committed in the fifth/final checkpoint (read latest Git HEAD). |

## Net improvements

**Critical path:** `SC-000 source inventory` → `SC-101 known ability catalog` → `SC-102 learnability UI comparison`; `SC-201 request/outcome taxonomy` and `SC-301 timing contrasts` proceed when their own evidence is available; `SC-401+` selective native attribution runs *only* when the API or observed behavior leaves a concrete answerable question. Nothing waits for whole-PE import or a complete spell tree.

**Truth model:** a known ability is not automatically eligible to learn at the current level; cooldown ≠ proven GCD; command delivery ≠ cast acceptance; miss/dodge ≠ no cast; castbar ≠ server acknowledgement; client native code ≠ complete server rules; source hash ≠ current runtime identity.

**Chat recovery model:** committed milestone state, current task and bounded request IDs are the record. The next turn performs Git/status/receipt reconciliation, chooses one `ready` task, avoids repeating known outputs, then commits one useful result. Unavailable capabilities and inconclusive tests are documented instead of hidden or recreated.

**Non-goals now:** duplicate RR2's addon/controller, change Workbridge, enable unattended casting, move the character, patch game memory, collect credentials or install new REA agents. These remain separate authorizations and workflows.

## Research gaps after the reviews

- Actual evidence for **unlearned but currently eligible** abilities from the same live character/role.
- Source-clock-aligned **cross-ability** observation that can distinguish shared GCD from ability-specific cooldown.
- A controlled **queue-mode** comparison with UI setting verified.
- Cast-time and channel/tick examples with real source timestamps.
- Exact client-side native function/dataflow only after a bounded, falsifiable anchor is identified.

**Acceptance of this review:** the roadmap and independent task register exist; five edits yield five stable commits; a short handoff names the very next ready task; there is no uncommitted source, live action, long-running REA job or conflated cross-project ownership.
