# P1/P2 plan — read-only cross-project evidence and bounded offline tool selection

**Planning checkpoint:** 2026-11-03
**Owner:** Physical-PC RRE spellcasting manager; proposed work is within `C:\work\rre`.
**Status:** Reviewed plan saved for future execution; **no implementation or cross-project integration has begun**.
**Priority:** P1 evidence intake first, P2 tool selection second. This plan does not supersede SC/RC task acceptance gates or authorize new game actions.

## Decision

Reuse the existing **Workbridge** connection to read and qualify independently owned REA-Lab1 findings. Maintain a compact source-linked evidence index in RRE rather than another MCP service, shared mutable data store, agent system, copied toolchain, or new Ghidra import. Select among established Capstone/iced-x86, focused Ghidra, REA and RRECollector capabilities using a simple decision policy. Add glue code only when a real pilot exposes a reproducible gap.

**Current source-build match:** Physical-PC RRE and the offline REA-Lab1 binary both report 60,493,640-byte `rift_x64.exe`, SHA-256 `1935a05c9db6d468e34e0055014a4a99c1b5afceb1695884e24600f5c20a4be8`. This supports same-build static byte/RVA comparisons only. The identity must be rechecked against the actual source when evidence is imported, and it does **not** transfer runtime pointers, session epochs, character/role states, server outcomes, Ghidra analysis semantics or gameplay observations.

## P1 — read-only cross-project evidence intake

### Architecture and ownership

```text
C:\work\REA-Lab1                         [independent owner; read-only to RRE]
    committed reports / SHA-pinned source receipts
                 |
                 | existing Workbridge read_file / git history / hash
                 v
C:\work\rre\docs\...                     [RRE manager-owned citation/index]
    source + build verification -> claim-level review -> local evidence link
                 |
                 v
RRE SC milestone or an explicitly unresolved external lead
```

- The physical-PC RRE manager writes **only** RRE-owned planning/index documents and approved RRE task records. The REA-Lab1 manager alone owns Lab1 files, source, tests, artifacts, commits and VMware actions. No RRE changes in `REA-Lab1`, `riftreader2`, `workbridge-mcp` or the installed game.
- Consult `REA-Lab1/AGENTS.md`, `REA-Lab1/TOOLCHAIN-L1.md`, `REA-Lab1/BASELINE.md` and the specific native report before importing a claim. Use Git history for a committed provenance anchor and a live SHA-256 for exact bytes. Uncommitted Lab1 reports are provisional, not frozen reference versions; avoid reading during another owner's writes without a stable snapshot.
- RRE's evidence entry should include: unique local claim ID; exact original repo/path; source commit or explicit uncommitted state; source SHA-256 and size; observed time if known; target PE SHA/size; exact RVAs and supporting byte/fixture receipt; read-only method; source scope; positive and negative findings; G0–G4 proof tier; independent reviewer outcome; explicit remaining unknowns; no invented game-side result.
- Classify imported Lab1 findings as **external source-qualified leads** until RRE independently checks the original and accepts the precise claim. A matching PE and a valid static instruction can support an RRE static claim; a Lab1 guest claim is not a physical-client observation.
- Keep evidence intake file-based, bounded and append-only at the claim level. Do not copy whole Ghidra projects, guest saves, raw client binaries, volatile account data, executable memory or private credentials.

### First pilot and exit condition

Choose **one** already published, stable Lab1 static finding with a matching PE and a focused verifier (for example, an existing committed constructor/field-offset observation). Verify the exact report source/hash, confirm its PE context, reproduce at least one small original-byte or independent decoder check through an already working read-only route, and state what the evidence **does not** prove. Record the RRE-reviewed result in its own citation/index file, link it to a current SC research question, and narrowly commit. If the candidate is still dirty or its evidence cannot be reproduced, record the limitation and select a stable alternative rather than changing Lab1.

**P1 done:** One RRE-owned, source-hashed cross-project evidence entry with an independent review, exact provenance and no writes outside RRE. No claim of current gameplay identity or SC-103 Legendary resolution merely from a static field-offset coincidence.

## P2 — bounded offline tool-selection policy

Use **question type and current evidence** to choose the smallest working tool. Do not automatically launch every tool.

| Research question | First route | Qualification / stop rule |
| --- | --- | --- |
| Verify binary/build, tool prerequisites and evidence | Existing file SHA receipts, Workbridge, Lab1-style `doctor` reference | Stop on missing or changed SHA; do not silently substitute an older binary |
| Exact bytes, known RVA, narrow instruction or field-offset claim | Existing Capstone and iced-x86 routines | Independent agreement within declared bounded regions; no inferred exhaustive scan, object alias or function semantics |
| Specific bounded function/call/dataflow | Existing read-only Ghidra project and `ghidra-plan` → explicit focused analysis | Revalidate PE SHA; Ghidra ` -readOnly -noanalysis `; at most four valid unwind-function start RVAs per Lab1 helper; no reimport, project save or broad retry |
| Ability metadata exposed through RIFT API | Existing source-qualified RRECollector snapshots and API docs | Distinguish Known/Detail from Learnable/Locked/Usable/Bound; freshness and character role matter |
| Native behavior not settled by the above | Narrow REA hypothesis/targeted analysis *if the provider is actually available* | REA 6.5.0 exists and has prior Codex MCP verification, but **direct REA MCP from this ChatGPT session is not established**; do not claim a direct connection or force a full import |
| Gameplay, live Soul/Legendary identity or cast timing | Operator-qualified live observations after separate current session and capture gates | These questions cannot be solved by a static tool dispatcher alone; no unsupported RIFT input/capture |

The existing `REA-Lab1/tools/l1_toolchain.py` has tested `doctor`, `crosscheck`, `ghidra-plan`, `ghidra-run`, `ghidra-run --focused` and `reclass-status` routes. However `crosscheck` currently targets **two fixed instruction intervals**, and focused Ghidra supports at most **four validated unwind starts**. The helper is Lab1-owned and its output is Lab1-scoped; **do not assume a generic RRE dispatcher exists**, modify the Lab1 helper from RRE, or execute Lab1 write-producing modes without its owner's scoped approval. Prefer borrowing the method/receipts read-only, then decide whether RRE even needs a tiny adapter.

### Selection contract

Before running a research tool: name the SC task and narrow question; read existing RRE evidence; check current source hash and owner; choose a bounded tool; specify success and stop conditions; assign a unique Workbridge request ID; capture real exit status/bytes; independently review the claim; write only the resulting useful RRE evidence and tests. A failed or inconclusive bounded probe must not be relabeled as success.

## Proposed milestones (not yet added as executable tasks)

| Milestone | Deliverable | Acceptance | Dependencies |
| --- | --- | --- | --- |
| **M1 — Evidence intake** | One verified Lab1 → RRE evidence record | Source path/commit/hash, PE SHA, reproducible static claim, independent review, no cross-repo edit | A stable Lab1 source |
| **M2 — Router policy** | Short mapping of question types to existing tools and stop gates | Every supported route has build check, bounded scope, clear proof tier, failure behavior | M1 |
| **M3 — SC pilot** | One real decision-changing, source-qualified SC-103-related finding or explicit no-go | New discriminator and focused regression; no repeat of parked `Ability.New.List` forwarding trace absent new evidence | M1–M2, suitable fresh source |
| **M4 — Minimal automation if justified** | Only targeted glue for a demonstrated repetitive manual step | Repeatable check with idempotent job IDs and no new service/agent framework | M3 demonstrates a gap |
| **M5 — Effectiveness review** | Before/after work receipts and short updated handoff | Less duplicated research, no unsafe full imports, preserved owners, verifiable continuation | M1–M4 as applicable |

Implementation starts only after the RRE manager assigns active board IDs/lane/path ownership and reconciles `ROADMAP.md`, `docs/roadmap-tasks.json`, SC/RC registers, HEAD, dirty files and command jobs. Run `tools/validate-roadmap.mjs` after board changes. Proposed milestones here do **not** change any current board state or imply worker/agent launches.

## Hard boundaries and known blockers

- **Physical-PC first:** `C:\work\rre` studies the physical client. REA-Lab1 owns VMware Lab-1, has its own manager and must remain an independent read-only source to RRE. A current matching PE SHA is not proof of matching live account, role, PID, UI or selected Legendary ability.
- **RC-30 freeze:** Keep installed physical RRECollector **v0.4.10** unchanged until the eight-slot in-memory baseline, Pin → Undo (no intervening Reload UI), full baseline restoration, Reload UI and fresh matching SavedVariables are independently verified. RC-31 and RC-32 source/deployment work remains gated.
- **Desktop quarantine:** Existing Workbridge GUI lease is quarantined after `DESKTOP_TREE_UNSETTLED`. Do not bypass, remove, force capture or infer settlement from time elapsed. The Workbridge desktop owner must explicitly reconcile the process tree and lease.
- **SC-103 stop:** The `Ability.New.List` descriptor forwarding thunk (`0x12942a0` toward `0x78e110`) is a parked evidence tier, not proven role-bound spellbook enumeration. Do not repeat unchanged probes without a novel callback/dataflow discriminator. A source-qualified *current* native Soul Tree/Legendary observation remains higher-value when available.
- **No unnecessary infrastructure:** No second MCP server, provider installation, replacement RE framework, new broad binary import, CI scheduler, nested AI swarm or duplicated automation task as part of M1/M2. Workbridge's 36 **command slots** are not 36 independent AI reasoning agents.
- **No unrelated writes:** Preserve unrelated untracked files and Lab1 dirty work. No physical/VM game input, service restart, process manipulation or executable modification as part of this planning milestone. Do not reintroduce removed browser automation dependencies.

## Sources for the implementation manager

- `rre/AGENTS.md`; `rre/ROADMAP.md`; `rre/docs/REA-RIFT-SPELLCASTING-ROADMAP-2026-10-27.md` and its task register.
- `rre/docs/REA-RIFT-SPELLCASTING-SESSION-HANDOFF-2026-11-03.md` and `rre/docs/REA-RIFT-SPELLCASTING-SC103-ABILITY-LIST-DESCRIPTOR-TRACE-2026-11-03.md`.
- `REA-Lab1/AGENTS.md`, `REA-Lab1/TOOLCHAIN-L1.md`, `REA-Lab1/BASELINE.md`, `REA-Lab1/tools/l1_toolchain.py` and relevant individual committed reports.
- Installed `C:\work\tools\rea` (`rea-agents@6.5.0`) and existing Ghidra 12.1.2; verify actual invocation rather than assuming direct ChatGPT REA tools.

## Copy-paste continuation instruction

> Implement **M1 only** from `docs/REA-RIFT-SPELLCASTING-CROSS-PROJECT-EVIDENCE-TOOL-ROUTING-PLAN-2026-11-03.md`. First reconcile RRE Git/worker state, read REA-Lab1 instructions and choose a **stable** source-hashed Lab1 finding. Verify original PE SHA and one bounded static claim independently, then create an RRE-owned evidence index entry with provenance and limits. Do not edit Lab1, install tools, rerun the parked SC-103 List descriptor trace, alter physical RRECollector v0.4.10, use quarantined capture or issue game input. Run relevant checks and commit only reviewed RRE-owned files. Report what is actually proved versus still unknown.
