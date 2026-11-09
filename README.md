# RRE

Research workspace for reverse engineering older MMO games, starting with RIFT.

## Navigation roadmap and current priorities

Begin at [ROADMAP.md](ROADMAP.md) for the staged prototype plan, dependency gates, and reuse-first decisions. The [manager-owned task register](docs/roadmap-tasks.json) records task IDs, branch ownership, blockers and accepted evidence. Agents must follow both rather than launch independent off-roadmap work. Use the [manager-led multi-agent launch prompt](docs/MULTI_AGENT_PROMPT.md) for new sessions; verify task dependencies and exclusive lanes with `node tools/validate-roadmap.mjs`.

## Native navigation research

Start with [the current research report](docs/navigation-research-2026-10-18.md) and
[the reproducible workflow](docs/navigation-workflow.md). The
[findings record](docs/navigation-findings.json) preserves exact-build evidence and
artifact hashes. The [experiment specification](docs/native-navigation-experiment.json)
is prepared for later native-movement validation; it has not been executed.

The current client contains a type-7 job category labeled TtPathfinding. Its handler
registration and connection to player movement remain unresolved. Reuse of native game
behavior, routes and collision queries takes priority over writing a new pathfinder.

## Screenshot evidence and visual validation

The [visual-evidence contract and commands](docs/visual-evidence.md) define a reusable saved-screenshot package, recorded VM/game/action checks, bounded image diagnostics and side-by-side HTML/JSON reports. Use `tools/visual-evidence.py` with the existing Pillow runtime. Original images, metadata and source hashes are preserved. The unified research gate includes a separate image test group. A successful command is not proof of a visible game response; ambiguous images remain inconclusive. See [the integration roadmap](docs/VISUAL_EVIDENCE_ROADMAP.md). No live recorder or independent AI image reviewer is launched by this offline consumer.

## Host-aware native-analysis dependency check

RRE supports physical RIFT on **LEGION** and separately authorized VMware-backed RIFT on **AMD-DESKTOP**; VMware is not installed on LEGION. The lightweight toolchain doctor detects the machine's actual hostname and inventories dependencies without contacting the game or any VM:

```powershell
node tools/native-toolchain-doctor.mjs --python "C:\\Path\\To\\Python\\python.exe"
node --test tools/test-native-toolchain-doctor.mjs
```

Optional absolute-path overrides: `--rea-home`, `--ghidra-home`, `--java-home`. With no configured Ghidra root the result is **unverified**, not globally absent. REA checks the installed `rea-agents` package metadata; Java uses a bounded `-version`; Python checks `capstone`, `pefile`, `Pillow`, and `iced-x86` package versions without importing analysis modules. This is a dependency inventory only, not proof of native-analysis capability or live RIFT acceptance. No package installation or service change occurs.

## Tracking work

- Keep source code, scripts, research notes, and reproducible instructions in Git.
- Record verified observations separately from hypotheses. Include the game build,
  file hash, or other evidence needed to reproduce a finding when available.
- Make small commits that describe a completed change or finding.
- Use `git status` to review pending changes and `git log --oneline` to review history.

## Local inputs and outputs

The following root directories are ignored by Git:

- `local/`: game installations, original binaries, and other local inputs.
- `artifacts/`: generated reports and tool outputs.
- `captures/`: network captures and memory dumps.
- `extracted/`: extracted game data and assets.
- `scratch/`: temporary experiments.

Put lasting research conclusions and scripts outside those directories so they can
be tracked. Keep credentials out of committed files.

## Repository

The initial branch is `main`. Remote hosting can be configured when needed.
