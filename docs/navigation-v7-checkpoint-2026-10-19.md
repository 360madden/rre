# V7 exact-run provenance acceptance checkpoint — October 19, 2026

## Outcome

M1-003 is accepted for **bounded offline navigation research captures**, not full call-graph or runtime navigation proofs. Existing source scanners were reused unmodified; the new validation-lane runner adds a separate immutable schema-2 manifest beside the upstream schema-1 artifact. No older evidence was rewritten.

**Source branch:** `research/nav-validation`, commit `a68094131c7cd6d93387cb280bbc1fc304b1d753`. Integrated to main as `ba30b70`. The worker's first real names sample and source-derived observations are preserved in `docs/agents/validation.md` and the committed `tools/agents/validation/v7-exact-*.json` files.

## Real exact-build capture on integrated main

- Job: `rre-v7-static-rea-dispatch-capture-20261019-01` — **passed, exit 0** (bounded scan, approximately 12.1 seconds).
- Native input: `C:\Program Files (x86)\Glyph\Games\RIFT\Live\rift_x64.exe`; SHA-256 `7c356c9dde9e12fcbff3c08d953b0630b48b1510a0ffb36e4ec164606e7b17bd`.
- Original helper SHA-256: `c62d729ea027c271c8b4113c927ab039ae760d6db20f479166e7769dd4891319`. The transitive AST-local source inventory records **five files**, including `workflow_common.py`, `postupdate_owner_root_rediscovery.py`, and `scan_current_pid_coordinate_family.py`. Dynamic imports and external package internals are explicitly outside this inventory.
- Recorder: `tools/agents/validation/capture_v7.py`, raw SHA-256 `7d7de94ddded627402cd2173a5e4f9d0a6eb117a5207754bac1f0b1304bf3aa2` on this main checkout; SHA and full recorder argv recorded inside the manifest.
- Upstream query: `--rva 0xf3fa4 --caller-rva 0xf3fa4 --depth 0`. Three PE-unwind code regions, no missing requested anchors, no incomplete windows or pending queue; **two** boundary-qualified direct callers at `0x8A9E6` and `0x8EFD0`. Per-target scan was complete within the declared direct-E8 method and not clipped at its 64-result cap. This is not exhaustive xref, player linkage or type-7 handler evidence.
- Captured schema-1 artifact: `artifacts/v7-static-dispatch-20261019-01.json`, **126,475 bytes**, SHA-256 `210fe5e97e45a0171f154d3fec524850be073b2e352f343bcc02fb829e6ea14e`.
- Captured schema-2 manifest: `artifacts/v7-static-dispatch-20261019-01-manifest.json`, **96,934 bytes**, SHA-256 `a036b4c92b8b3df664146361e2ef0cbb9cf31f2a82178edd66edb64b844f60b1`.
- Unfiltered pefile exception-directory warnings: **825**, retained as original message text and a separate ordered-list SHA-256. These are known duplicate shared-parent bookkeeping warnings in the selected build, not automatically suppressed. Source identity was checked again after the scan. Python, pefile and the separate Capstone module/distribution/engine versions are recorded.

## Validation and remaining limits

`rre-v7-integrated-full-tests-20261019-01` ran the full integrated synthetic suite: **21 passed, zero failures/skips** (the original 13 plus eight V7 tests). Separate V7 synthetic test cases cover no-clobber inputs, source inventory, requested zero results, version labels, omitted caller summaries, missing requested anchors, clipped caller hits and incomplete decoding. A previous real names scan also passed with zero *restricted* references for `0xF3FA4` and all 825 parser warnings recorded; zero refs does not mean the native dispatcher is absent.

This V7 milestone establishes **repeatable recording of what existing scans actually did**. It does not prove every disassembly is reachable, inspect every indirect call, reconstruct a native navmesh, identify active type-7 handlers, or run Rift. Output under `artifacts/` is Git-ignored by design; the report above pins each artifact's SHA and exact path. For future runs choose **new output filenames**, never replace an existing artifact or manifest.

**Next critical task is M3-001:** revalidate/preserve five original untracked pathfinding query files, then investigate type-7 handler writers and producers without generating a replacement planner prematurely.
