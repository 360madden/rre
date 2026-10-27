# SC0 PHASE HANDOFF — REA RIFT spellcasting

**Phase:** SC0 evidence baseline — **COMPLETED** (October 27, 2026).  
**Current owner:** REA research only; RR2/Workbridge remain separate projects.  
**Next task:** `SC-101` — produce a source-pinned ability table from the **55 saved API-returned IDs**; do not claim the table contains all unlearned or level-eligible spells.  
**Phase source and scope:** [SC0 baseline](REA-RIFT-SPELLCASTING-SC0-BASELINE-2026-10-27.md), [independent register](REA-RIFT-SPELLCASTING-TASKS-2026-10-27.json).

## Accepted result

- Two saved Oct 26 RR2 `ranged-evidence-03/04/evidence.json` records, 55 entries each, have identical 55 unique lookup IDs.
- Character/role caution: `Atank` appears in the evidence; player ID `u035400012FA2D207`. Role/soul points/rank progression were **not** source-verified in these snapshots. Old guest PE SHA was the previously qualified one.
- Installed RIFT API documentation describes `Inspect.Ability.New.List()` as returning available-ability IDs, with batched `Detail` metadata. Do not equate this with the complete native spellbook of learnable abilities.
- Native spellbook UI is **not** yet verified. The source-hash-reviewed October 26 screenshot is RR2's casting ability picker, **not** the soul tree or trainer.
- Names collide: three `Building Fury`, four `Changing Role` under distinct IDs. Some metadata absent; never normalize unknown to zero.
- RR2 already has exact modern-ID dodge and damage events and cooldown observations, but **GCD is unverified**.

## Resume instructions in normal ChatGPT Chat mode

1. Read RRE `git status` and current HEAD plus [this handoff](REA-RIFT-SPELLCASTING-SC0-HANDOFF-2026-10-27.md) and [task register](REA-RIFT-SPELLCASTING-TASKS-2026-10-27.json). Preserve old untracked raw-probe work. SC0 phase validation job: `rea-sc0-source-check-20261027-01`; inspect its actual result if necessary.
2. Read **only** the saved RR2 ability inventory at `C:\work\riftreader2\artifacts\casting-20261025-01\ranged-evidence-04\evidence.json`; source SHA `9e81dccdf53640c5ae8f874b6bad16d38f75faeee06be7999032e9695d934630`. Read `abilities` in a bounded offline parser (5 MB); original RR2 file remains read-only.
3. Implement **SC-101** as a small, versioned *research export* (JSONL/CSV) containing the exact 55 API lookup IDs, name, rank if reported, ability metadata with missing values as unknown, and source provenance. Keep known/learnable/usable separate. Compare row/ID counts and checksum before committing.
4. SC-102 is **blocked** on a real native spellbook/soul/trainer UI snapshot with level/calling/role/soul allocations matching that character. RR2 owns any live evidence collection. REA does not implement or trigger controls.
5. Commit SC-101 export+source note+task-register/handoff checkpoint before any costly Ghidra work. No new engine, full-client import, or code modifications in RR2/Workbridge by default.

**Last SC0 milestone commit:** verify `git log`; historical plan HEAD was `0f35601` before SC0 work. No live game input, host restart, PE analysis/import, or remote push was performed in SC0.

**Next completion notification:** show large colored `SC1 — COMPLETE` **only** after one source-pinned role-scoped inventory and actual native spellbook/API reconciliation; a 55-ID API export alone completes SC-101, not SC1.
