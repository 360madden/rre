# Validation lane: navigation evidence and tool audit

The six baseline static artifacts pass their recorded SHA-256/size checks and reproduce against the qualified executable. **Five synthetic regressions remain unfixed in the shared tools.** Prioritize provider-admission hash verification and caller-search truncation reporting. No game-world navigation success is established.

Worktree: `C:\work\rre-worker-validation`; branch: `research/nav-validation`; starting commit: `c7815b762dbdfe4d681a96cd14a69f658668595c`. Only this lane's reports and three audit/test scripts were created. Original wrappers, RiftReader, installed tools and evidence remained read-only. No live input, process attach, target execution, full import, dependency installation, remote operation, or nested agent was used.

## Build, sources and method

- Executable: `C:\Program Files (x86)\Glyph\Games\RIFT\Live\rift_x64.exe`; measured SHA-256 `7c356c9dde9e12fcbff3c08d953b0630b48b1510a0ffb36e4ec164606e7b17bd`; 59,963,840 bytes; x64 PE; preferred image base `0x140000000`. All native addresses below are RVAs.
- Baseline: `docs/navigation-research-2026-10-18.md`, `docs/navigation-findings.json`, `docs/navigation-workflow.md`; six artifacts under `C:\work\rre\artifacts\navigation-20261018-01`.
- Reused pinned helpers: `C:\rift modding\RiftReader\scripts\postupdate_static_access_chain.py` (SHA-256 `c62d729ea027c271c8b4113c927ab039ae760d6db20f479166e7769dd4891319`) and `scripts\anti-re\rtti_class_scanner.py` (`3636e5ca9c39318c27a7c5fdbccfd01e3258ef079139a0d9df64f49961448331`). Neither was edited.
- [Read-only auditor](../../tools/agents/validation/audit_saved_evidence.py): checks artifact hashes, original bytes, PE ranges, raw chained-RUNTIME_FUNCTION triples, saved instruction text/bytes, direct-call/RIP target arithmetic, string offsets and reference boundaries using existing pefile/Capstone. It does not reconstruct a decoder.
- [Wrapper tests](../../tools/agents/validation/test_wrappers.py) use synthetic PE bytes and the actual pinned helpers/decoders. [Driver tests](../../tools/agents/validation/test_rea_driver.py) run the actual driver against temporary fake SDK modules; the fake transport never starts REA, Java or Ghidra. Fixtures are removed automatically from the lane directory.
- `validation.json` retains exact input/artifact/source hashes, audit counts and machine-readable findings. No memory-derived offset or runtime claim was used as current evidence.

## Verified static evidence

These are direct observations of recorded bytes and offline metadata, not observed execution.

| Artifact suffix | Recorded regions | Instruction rows verified | Coverage |
| --- | ---: | ---: | --- |
| `anchors.json` | 25 | 967 | All captured windows decode; 12 unresolved anchor records, including duplicates |
| `chains.json` | 11 | 620 | All captured windows decode; stored chain roots match raw chain triples |
| `command-regions.json` | 16 | 6,343 | All captured windows decode; stored chain roots match raw chain triples |
| `command-callers.json` | 30 | 4,500 | One decode stops at `0x696921`, before region end `0x6969EC` |

Totals are 82 recorded regions and 12,430 rows across overlapping listings, not unique-function counts. No audited window is empty. All recorded work queues are exhausted; that does not resolve missing leaf boundaries, indirect edges or reachability.

All 18 saved direct callers requalify from their unwind-range starts: 2 target `0xF3FA4`, 16 target `0x534200`. Neither query reached 64 candidates. The string-reference artifact has 12 LEA candidates: 11 have reproducible instruction alignment; `0x6ADA60` has no containing unwind range and remains explicitly unverified. All 147 saved text matches and 14 restricted RTTI-name matches reproduce at their recorded offsets in each names artifact; strings stay in non-executable sections.

At `0xF4194`/`0xF4198`/`0xF41A3`, the bytes decode as a shift by 5, pointer load at indexed queue offset `+0x130`, then indirect call through subtype times 8. Thus `0x130 + 7*0x20 = 0x210` is arithmetically consistent. This does not identify handlers, queue ownership, player use or a runnable interface.

The signed `CALL rel32` formula (`site + 5 + displacement`), RIP-relative formula (`site + instruction_size + displacement`), and high static VA/RVA conversion pass synthetic positive/negative-displacement tests. The common two-entry unwind chain also passes. Exceptions describe unwind regions; neither these checks nor sequential decoding establish a complete CFG.

## Reproduced issues for manager

Priorities describe research correctness and reproducibility, not a live security assessment. No shared-tool fix was made.

| ID | Priority | Reproduction and actual result | Source and recommended correction |
| --- | --- | --- | --- |
| V3 | P1 | Fake `open_binary` returns a different SHA-256; driver reaches `completed` and exits 0. | `tools/rea-session.mjs:122-125`: compare provider admission path/hash/architecture with the prequalified identity, rejecting absent/mismatched identity before queries. Current saved admission **does** match, so historical corruption was not observed. |
| V1 | P1 | 64 `E8` patterns inside `movabs` immediates precede one real caller at `0x1280` to `0x1800`. Returned candidates: 64, qualified callers: 0; real caller omitted. | `tools/inspect-navigation-static.py:93-115`, original helper `postupdate_static_access_chain.py:162-190`: cap is applied before instruction qualification. Use bounded incremental scanning/qualification and explicit per-target scan/truncation coverage. Merely increasing 64 postpones the issue. Baseline's 18 sites are unaffected. |
| V2 | P2 | Synthetic unwind range `0x2000..0x2010` lies outside executable bytes: no instructions, empty window hash, yet `instructionDecodingCoversWindow=true`. | `tools/inspect-navigation-static.py:137-166`: require a nonempty executable-backed window and propagate helper blockage. `windowTruncated=true` is present; consumers must not infer completeness from the decoding flag alone. Not seen in the six artifacts. |
| V4 | P2 | Synthetic zero-duration run ends `time-budget-reached`, performs no queued query and exits 0. | `tools/rea-session.mjs:23,130,167,197`: validate duration and make incomplete terminal states distinguishable by exit status. The same exit expression covers ordinary budget exhaustion. Saved attempt 01 correctly recorded failure, not false success. |
| V5 | P2 | Preexisting `identity.json` without `status.json` is replaced. | `tools/rea-session.mjs:19-20,43-44,69`: reserve a fresh evidence namespace or use exclusive creation for immutable receipts; keep only status deliberately mutable. Python wrapper outputs already use exclusive creation and pass no-clobber tests. Only synthetic files were overwritten. |

Each `test_bug_v*` contains the minimal carrier and desired assertion. Normal tests mark these five as expected failures. Strict mode removes that marker and produces **exactly 2 wrapper assertion failures and 3 driver assertion failures**, confirming the intended conditions failed rather than setup/import failures.

Two additional audit observations deserve manager follow-up:

- **V6 / P2, silent parser diagnostics:** pefile reports **825 warnings** while parsing 302,344 runtime-function entries on this exact file. The retained examples say `Failed parsing FunctionEntry ... 'Chained function entry cannot be changed'` at file offsets `0x32DE96C`, `0x32DFC38`, `0x32E0A24`. The wrappers do not capture `pe.get_warnings()`. Selected stored roots passed checks against the raw embedded parent triples; the warnings are not proof those selected roots are wrong. Persist warnings and investigate shared-UnwindInfo bookkeeping before claiming global chain completeness.
- **V7 / P2, reproducibility/summary gaps:** artifacts pin binary and top-level helper hashes but omit wrapper hashes and full CLI parameters; the static helper also imports unpinned `workflow_common.py` and `postupdate_owner_root_rediscovery.py`. Names outputs omit dependency versions. Artifact layouts evolved without changing `schemaVersion=1` (earliest anchors lack chain fields, earliest names lack reference fields). The static stdout summary omits decoding/truncation flags: the saved JSON must be read. Record source/config/import hashes, distribution/module/engine versions, queried targets even with zero matches, per-target limits, parser warnings and a summary completion state.

## REA provenance and environment

For saved attempt **01**, `identity.json`, `open-binary.json` and `analysis-snapshot.json` all identify the exact target hash. The diagnostic response matches the hash in `docs/rea-import-attempt-2026-10-18.json`. Export/close receipt byte counts match their files; bundle records, snapshot primitive entries and workflow entries are empty. Status records the first analysis query as an error after approximately 450.7 seconds, then export and close. This corroborates a timeout with zero analysis evidence, not absence of native navigation.

Attempt **02** was reviewed through its tracked report only; its outside artifact directory was not independently audited in this lane. No import was repeated. Installed SDK 2.3.1 source advertises `callTool(params, options)`, consistent with the driver's argument placement; the older three-argument SDK convention is not an applicable bug here.

Capstone distribution metadata is **5.0.9**, its Python `__version__` is **5.0.7**, and `cs_version()` is `[5,0,1280]`. Saved static outputs record the module value; the requirements pin records the distribution value. This observed distinction does not demonstrate an environment downgrade. pefile is 2024.8.26.

The main seed file is 170 LF bytes, hash `595a104e79b264f716f64f4ea9898e0dca6b868c0cbbc301264a63edd7b6aba5`, matching the saved profile. This clean worktree has 173 CRLF bytes, hash `ded1e9b6475f415895c96dcd79f9ad7db0204147e99f9adab523af81d1aa883e`; normalizing CRLF yields identical bytes. Current main/worktree wrapper copies are likewise equal after newline normalization. Preserve actual raw hashes; do not silently substitute normalized hashes for identity checks.

## Validation and limits

Run from this worktree with the existing interpreter; no installation is needed:

~~~powershell
& C:\work\rre\.venv\Scripts\python.exe -B -m unittest discover -s tools/agents/validation -p 'test_*.py' -v
& C:\work\rre\.venv\Scripts\python.exe -B tools/agents/validation/audit_saved_evidence.py
# Both commands above exit 0. Suite: 12 cases = 7 passes + 5 expected failures.
& C:\work\rre\.venv\Scripts\python.exe -B tools/agents/validation/test_wrappers.py --strict -v
& C:\work\rre\.venv\Scripts\python.exe -B tools/agents/validation/test_rea_driver.py --strict -v
# Strict commands intentionally exit 1 until the reported tool issues are fixed.
~~~

The tests verify stdout JSON syntax, fail-closed binary/helper hashes, Python output preservation, signed address math, basic chain expansion, non-executable string scope and explicit decoder stops. Driver controls verify JSON-lines stdout, export/close order and no second open after a query error. New Python sources passed syntax compilation without writing bytecode; the unchanged Node driver passed `node --check`.

Existing documented runtime evidence remains attributed to the baseline/RiftReader reports and was not reacquired or promoted. Native pathfinding handlers, gameplay destination formation, following cancellation behavior and collision semantics remain unresolved. No result here turns historical proximity graphs into native navmeshes, player-centered bounds into fixed goals, or cached `+0xD8` into a verified destination.

**Recommended next validation:** manager fixes V3 and V1 in an authorized tool branch, reruns these synthetic strict tests, then makes one bounded offline query with explicit completion/provenance diagnostics. Investigate V6's warnings before expanding any claim of unwind-chain coverage. No new full import or live experiment is required for those fixes.

## Delivery status

Local staging was attempted with the five explicit owned paths only. Git failed before staging:
    fatal: Unable to create 'C:/work/rre/.git/worktrees/rre-worker-validation/index.lock': Permission denied

The Git administrative directory is outside this lane's writable source tree. No permission escalation, identity change, alternate index, branch operation or commit retry was attempted. **No new commit SHA exists; all five owned files remain unstaged for manager review/commit.** Starting/current HEAD is recorded above for provenance, not as a delivered worker commit.
