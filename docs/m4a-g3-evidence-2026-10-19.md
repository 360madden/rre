# M4A offline target-approach — G3 evidence

**Date:** October 19, 2026 (America/New_York)  
**Repository:** C:\work\rre  
**Status:** G0–G3 integrated; independent G4 QA and G5 Manager acceptance remain separate gates.  
**Scope:** Synthetic-only deterministic decision replay, not native Rift navigation or game actuation.

## Locked synthetic inputs

Plan `docs/M4A_OFFLINE_TARGET_APPROACH_ROADMAP.md`; contract `docs/m4a-offline-target-contract.json`; 13-case/24-sample locked synthetic corpus `docs/m4a-offline-target-fixtures.json`. X/Z horizontal, Y vertical, distances are *fixture-defined*, not qualified Rift world metres. Historical Rift executable SHA256 `7c356c9dde9e12fcbff3c08d953b0630b48b1510a0ffb36e4ec164606e7b17bd` is provenance metadata, not an input opened by the replay program.

## Genuine independent AI agent work

Four distinct OpenCode CLI 1.18.4 sessions authored disjoint source and tests in existing Git research worktrees. The Manager separately reviewed, ran tests, and sequentially cherry-picked their contributions:

| Task | Worker original commit | Integrated main commit | Test verification |
| --- | --- | --- | --- |
| M4A-003 C2M | `60e14c39d3c7c220481b6774d42f161bb3bab3dc` | `091a494567b7bbacdfd6061203b0c55ea5a1175e` | 30 passed |
| M4A-004 Follow | `0967b96158dd2e18fd0fb78480e92136aa0fc9b9` | `1b8addbb46c86e1e97070d67a3639e8414da7ab6` | 73 passed |
| M4A-005 Collision | `01a061833c17770b2abea5010192b2a4713e2a59` | `7adeeaf3673baf89786f67fdb397b94332d9f163` | 32 passed |
| M4A-002 Validation | `88925b89bcf5fe41d0f42fcfb662bd8a473035fc` | `ae8fbeeb773ff48d50d192ed68361869924b4756` | 36 passed; real locked 13/13 corpus audit, zero errors |

C2M, Collision and Follow independent workers corrected rejected drafts when the Manager found status-literal or flat-schema defects. The initial independent Validation worker **timed out**; Manager directly recovered and corrected its status vocabulary and added real-corpus tests. Do not attribute that correction to the agent.

## G3 Manager integration

Manager-created offline CLI `tools/offline-target-approach.py` integrated in main as `c0ada6124cac73b7e44f7f2acd90a0be6d87002e`. The command:

```powershell
& C:\work\rre\.venv\Scripts\python.exe -B C:\work\rre\tools\offline-target-approach.py
```

runs the locked corpus without output-file changes, printing deterministic JSON. An optional fresh `--output C:\work\rre\artifacts\NEW-FILE.json` writes one exclusive file only under artifacts and refuses overwrite.

- G3 replay `rre-m4a-g3-replay-13-fixtures-20261019-01`: exit 0; **13/13 scenario golden traces**, **24 samples**, zero discrepancies, `commandsIssued:0` and `gameInputSent:false`.
- Generated artifact `artifacts/m4a-replay-integration-20261019-01.json`: 12,248 bytes, SHA256 `289c1f5bdace882c0b4665ed4b6b61ec86aad459bfff12849e66fbf6d4cddda7`.
- Independent duplicate run `rre-m4a-g3-determinism-second-replay-20261019-01` generated the same SHA256 in fresh `...-02.json`.
- A separate live-source mutation failed closed (`rre-m4a-g3-unqualified-source-negative-20261019-01`), exit 0 for the verification command.
- Existing RRE Validation suite `rre-m4a-g3-previous21-regression-20261019-01`: **21/21 tests passed**.
- Manager-only adversarial QA `rre-m4a-g4-manager-adversarial-cli-check-20261019-01`: passed, covering repeatability, output path guards, no-clobber, non-synthetic input rejection, malformed input refusal, locked-file hashes and absence of known runtime/game-control imports in CLI source.
- All four independent component suites independently rerun from integrated main: 30 + 73 + 32 + 36 = **171 passed**; plus 21 historical = **192 passed**.

## Remaining gates

**G4** must be independent Validation-lane golden-output/negative QA, reviewed and tested on *integrated main*. First OpenCode Mimo G4 agent `rre-m4a-g4-independent-qa-agent-20261019-01` timed out while reading unrelated legacy reports; wrote no files. A narrower Nemotron worker was launched as `rre-m4a-g4-nemotron-qa-onefile-20261019-01`; record actual outcome before declaring G4 complete.

**G5** Manager final acceptance requires recorded G4 results and reviewed clean Git. Do not mark M4A, full M4, M5 live trials or M6 in-game navigation successful prematurely.

Native type-7 `TtPathfinding` handler registration and player-use remain unverified. No game input/process attach/memory modification/native navigation call, dependency install, Git remote push or new custom A*/navmesh was performed. Preserve the two preexisting untracked raw-x64 probe files in main.
