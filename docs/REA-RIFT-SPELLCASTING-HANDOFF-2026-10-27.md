# REA RIFT spellcasting — current Chat-mode handoff

**As of:** October 27, 2026. **Current phase:** SC1 partially underway; **next task:** `SC-104` readiness vs catalog knowledge.  
**Owner:** REA research only. No RR2/Workbridge source edits or live-game actions.

### Completed and committed

- **SC0 COMPLETE:** validated source baseline, 55 matching unique lookup IDs in two historical RR2 captures, 9 SHA checks, 17/17 acceptance. Commit `e76e6b2`. [Phase handoff](REA-RIFT-SPELLCASTING-SC0-HANDOFF-2026-10-27.md).
- **SC-101 COMPLETE:** [55-ID API catalog JSONL](REA-RIFT-SPELLCASTING-SC1-API-CATALOG-2026-10-27.jsonl) and [CSV](REA-RIFT-SPELLCASTING-SC1-API-CATALOG-2026-10-27.csv), exact ID/raw metadata and unknown-field preservation, 12/12 checks. Commit `4eea4e9`. [Source notes](REA-RIFT-SPELLCASTING-SC1-API-CATALOG-NOTES-2026-10-27.md).

### Next bounded task

Read `C:\work\riftreader2\addon\RiftReader2Casting\model.lua` (SHA `82aa8395a36fbc2c3f83ff32392dcb4bbc43aa6bd18fd39a4339ab01c264a812`) and historical saved `ranged-evidence-04/evidence.json` (SHA `9e81dccdf53640c5ae8f874b6bad16d38f75faeee06be7999032e9695d934630`). Deliver SC-104 as a source-backed matrix distinguishing `apiListed`, `learnableNow`, `known` and `usableNow` at a specific observation time. The 55-ID list is **not** an independently qualified list of unlearned/current-level skills. A 12s Light's Decree timer or 1.5s Aggressive Block effective cooldown does not independently prove GCD.

**SC1 remains NOT COMPLETE:** SC-102 needs the native RIFT spellbook/soul-tree/trainer UI and the same character's current level, role and soul point allocation. The saved UI screen is only RR2's ability picker. SC-103 rank/variant role association is also unresolved; preserve duplicate names and distinct IDs.

If SC-104 is accepted, proceed to SC-201 (observed cast lifecycle from actual hit/dodge/input receipts) or SC-103 as evidence permits. Do not start huge REA PE imports, repeat SC0, or make live input through this research lane.

### Resume safely

Use Workbridge `git_status(rre)` + latest RRE HEAD and [independent task register](REA-RIFT-SPELLCASTING-TASKS-2026-10-27.json) as authority. Workbridge request IDs for accepted checks: `rea-sc0-source-check-v2-20261027-01` and `rea-sc101-catalog-acceptance-20261027-01`. Commit one bounded finding and refresh this handoff immediately; preserved unrelated untracked raw-probe files remain untouched. No work continues asynchronously after a Chat turn.
