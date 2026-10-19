# RRE

Research workspace for reverse engineering older MMO games, starting with RIFT.

## Native navigation research

Start with [the current research report](docs/navigation-research-2026-10-18.md) and
[the reproducible workflow](docs/navigation-workflow.md). The
[findings record](docs/navigation-findings.json) preserves exact-build evidence and
artifact hashes. The [experiment specification](docs/native-navigation-experiment.json)
is prepared for later native-movement validation; it has not been executed.

The current client contains a type-7 job category labeled TtPathfinding. Its handler
registration and connection to player movement remain unresolved. Reuse of native game
behavior, routes and collision queries takes priority over writing a new pathfinder.

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
