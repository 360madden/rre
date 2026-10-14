# RRE

Research workspace for reverse engineering older MMO games, starting with RIFT.

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
