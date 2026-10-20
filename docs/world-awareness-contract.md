# File-only world inspector v1 contract

This is an offline research consumer. It accepts a saved JSON observation, never executes Lua, opens a process, queries the game, sends input, or accesses the network. Main implementation: `tools/world-inspector.py`. Documentation of the RIFT API is not treated as runtime verification.

## Supported inputs

`readerbridge`: a JSON object matching the actual ReaderBridgeExport snapshot shape: integer `schemaVersion: 1`, string `sourceMode`, optional `playerId`/`targetId`, nullable `player`/`target`, nullable arrays `nearbyUnits`/`partyUnits`. A unit has an actual string `id`, optional `name`, nullable boolean `player`, optional `coord` object with `x`, `y`, `z`, and optional `zone`. Supported observed sourceMode values are `DirectAPI` and `ReaderBridge`; explicit `sourceMode: SyntheticFixture` marks test inputs. The source's ReaderBridge mode always sets nearbyUnits to nil, so absent data in that mode is reported as `not-exported-by-bridge-mode`. Ordinary saved observations are recorded, never live. Unknown additional legacy fields are ignored rather than reinterpreted.

`rr2-receipt`: implemented against the retained `C:/work/riftreader2/artifacts/live-validation/live-fresh-receipt.json`, SHA256 `a7cddc62cd66a14f943e0bc2de82666fcd7de0013c5e6db12780518e726329d5`. Read the typed player and coordinates at `observation.riftReader2.observation`; all nested schemas must be 1 and addonVersion must be 0.1.0. The outer `observation.target` is the recorded process identity, NOT the selected game entity. This adapter is player-only; targets/scenery/enumeration are never fabricated. Old bound/fresh claims are retained as historical metadata only.

Input is bounded to 8 MiB and at most 512 total unit records; reject invalid UTF-8/Unicode scalars, duplicate JSON keys, non-finite numbers including exponent overflow, wrong schema, malformed arrays and object-ID ambiguity. Missing coordinates remain missing; partially specified or nonnumeric coordinates are rejected. Coordinates and ordinary numeric values must not accept booleans. IDs are not names or native addresses; specifiers such as `player`/`player.target`/`group01` are not qualified entity IDs. Root playerId/targetId disagreements with record IDs are errors.

## Identity and coverage

Merge the same actual ID only inside this one input snapshot. Preserve all source paths and union roles. Different IDs sharing a name or coordinates remain distinct. If same-ID records disagree in position, zone, character kind or name, expose an identity/data conflict; do not select a convenient position or project that record. Self-targeting merges the player and target roles, not two entities. No cross-capture tracking is performed; session/scene/generation are not inferred.

The legacy producer returns nil for both an unavailable enumeration and no retained nearby rows. Therefore missing/null nearbyUnits means `unavailable-or-empty`, never verified empty. An explicit empty list means `reported-empty-scope-unverified`. Nonempty means `partial-reported`; original order is not an exhaustive distance-sorted census. Party and selected-target scope are separate. World/scenery coverage is always unknown in this slice.

## Output and uncertainty

Inspector 1.1.0 writes `report.json` and a self-contained, script-free `report.html` into a NEW caller-named output directory, then writes `complete.json` last. The completion receipt contains the two fixed filenames, byte sizes, SHA256 hashes and input source hash. `--verify-output DIRECTORY` verifies the receipt and files without regenerating them. A missing, partial, malformed or mismatched receipt is not a complete publication; old 1.0 reports are not silently upgraded. Partial new directories remain available for diagnosis and are never deleted as a cleanup shortcut. File-set integrity is not source authenticity, current freshness or live-world qualification. Existing output directories and files are never replaced. Validate/render before creating the directory; input is unchanged. Record original source SHA-256, input format, recorded-versus-synthetic kind, parser version, absent binding and freshness-unverified state. A file mtime or old receiver flag must not establish current live freshness.

Each row retains exact ID, roles, name/kind if present, XYZ or unknown/conflict, provenance source paths, and `visibility`, `collision`, `support`, `reachability` set to unknown. Historical binding/freshness claims must be bounded nullable strings, not arbitrary JSON objects. An unknown zone and a literal zone name `unknown` remain distinct plotting groups. A raw X/Z scatter plot with explicitly displayed Y coordinates is diagnostic only: not a ground-plane/walkability claim and not native geometry. No obstacles, paths or object bounds are invented from unit positions.

## Optional candidate camera sidecar

A separately supplied JSON object has `schemaVersion: 1`, `sourceSha256` matching the EXACT input bytes, `convention: row-major-column-vector-zero-to-one`, `viewProjection` with exactly 16 finite numbers and `viewport` with finite x/y and positive integer width/height at most 16384. Its `evidenceKind` is synthetic or candidate, never silently verified. A synthetic camera is rejected for a recorded input. A hash binds the selected input, not acquisition time or scene calibration.

For point (x,y,z,1), multiply the row-major matrix by this column vector; accept screen projection only if w>0 and -w<=clipX<=w, -w<=clipY<=w, 0<=clipZ<=w. Screen y is inverted; apply viewport origin. Return not-in-frustum for clipped/behind points, not occluded. Candidate projections remain unvalidated against a real screenshot. Reject singular matrices, numeric overflow and mismatched source hashes. No camera is inferred from player heading/position or historical offsets.

## Acceptance tests

Check self-target merge, separate same-name IDs, inconsistent IDs, same-ID coordinate/name/zone/kind conflicts, missing and partial positions, unavailable/empty/capped nearby scope, invalid/nonfinite/bool numeric data, duplicate keys, malformed schema, source hash, recorded data always non-live, immutable inputs/output no-clobber, HTML escaping, absent camera, explicit projection conventions and behind/outside/near/far/viewport behavior. Synthetic checks never qualify real geometry, camera calibration or live world recognition.
