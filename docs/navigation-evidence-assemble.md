# NAV-006 — Strict source-fragment assembly for NAV-003

October 21, 2026. `tools/navigation_evidence_assemble.py` accepts a six-entry SHA-256 manifest for pre-existing normalized `binding`, `policy`, `frame`, `actions`, `samples` and `observationEndMs` JSON files. It produces a single trace plus a NAV-003 offline evaluation only when every required source exists and matches its declared hash. The manifest names relative paths under its directory, never arbitrary external files.

This is **not** a recorder or converter of incomplete RR2 historical receipts. The tool does not invent a selected target, current gesture, destination coordinates, event timings, source sequences, observations or missing cancel action. Missing files, changed bytes, unknown schema and unsafe paths fail; even a syntactically complete trace stays `liveAccepted=false` and requires independent review of image/action/game evidence.

From `C:\work\rre`, use the existing interpreter on a prepared bundle:

```powershell
& .\.venv\Scripts\python.exe -B tools/navigation_evidence_assemble.py --manifest artifacts\NAV006-prepared-source\manifest.json --output artifacts\NAV006-prepared-source\assembled.json
```

The output path must not exist. Do not use the listed illustrative directory as evidence of an already created bundle. Synthetic tests verify complete assembly, hash mutation rejection, incomplete manifests, unsafe paths and a recorded-looking label not establishing true provenance. The current saved RR2 dataset does not supply all six required source fragments, so no live RIFT trial or accepted navigation trace is claimed.

Next: the existing RR2 execution owner must deliver an actually reviewed, bound ground click, monotonic-timestamped before/during/after player samples and separate cancellation evidence, with live ownership and approval handled independently. The initial trial remains blocked.
