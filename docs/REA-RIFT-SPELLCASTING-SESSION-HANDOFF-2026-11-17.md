# RRE manager continuation handoff — 2026-11-17 00:04 EST

## Reader physical-only routing correction — bounded offline milestone

- **Host:** independently selected named AMD-DESKTOP Workbridge 0.16.5-dev, root `C:\work`; named Workbridge reports AMD-DESKTOP and prior `hostname.exe` verified it. **Repository:** `C:\work\rre`, `main`, starting HEAD `9478db4634f1e5357b8c069e220ef88e315c713f` equal to `origin/main`. No tracked dirt at entry. Nine pre-existing untracked `docs/rc*-backup` and raw-probe paths remain untouched. Workbridge agent assignment register empty, no owned running RRE jobs at entry. Two independent ChatGPT agents reviewed production collector and reader contract in read-only mode.
- **Confirmed policy mismatch (source, not runtime):** `reader/Rre.Reader/Program.cs` rejected `capture --source lab2` only for host LEGION and `doctor` advertised Lab-2 acquisition on AMD-DESKTOP, contradicting top-level `AGENTS.md:3` and `ROADMAP.md:1` November 10 physical-only/no-VM rule. Separate independent review found public `Lab2Source.ReadAsync` could bypass the CLI guard.
- **Manager-only source change:** `Program.RequireSourceHost` rejects `lab2` for *every* host before path/preflight; public `Lab2Source.ReadAsync` calls the same guard *before its own* preflight. `doctor.lab2AcquisitionAllowedThisHost=false`, its adapters list no longer advertises Lab-2 acquisition, and help/reader README mark the historical command disabled. All four offline sources (`saved`, `memory-scan`, `native-snapshot`, `publication`) remain usable. `Lab2Source.DecodeAcquired` and archived bytes remain intact. Reader version retains `0.2.7`; no installed/game package deployed.
- **Source SHA-256 after editing:** `reader/Rre.Reader/Program.cs` `d55d79ec1570445fc67213eb852121dc80c49a52ceafb00ffa9202a31ca54c44`; `reader/Rre.Reader/Lab2Source.cs` `0e39347940f59c1bc4e3508c6c66842aaa456f7517e565ab7d3a91ee392852d3`; `reader/Rre.Reader.Checks/ProductionChecks.cs` `35928b1f5ff915e61fc261e432652759521c304aa0c77e6abb746c45b05fa839`; `reader/Rre.Reader.Checks/Lab2Checks.cs` `20476b6aa7e6929b3683428941d28b5b3242e008aad69ac041e94826c1078a8c`; `reader/README.md` `31af9f10ca45d564005a7cabe05e4ef7caf7a0c9af75a56ca0e2e1f63079d911`.
- **Historical test-fix, no rebaseline:** Archived Nov 7 SC625 trial2 acquisition manifest SHA `69546e444fdd557bd7c8067dba31a7604cdcb858e5303e5a231f8a62007ea57f` declares acquisition helper `4f3315324df204d9c40f0477a65578b3126ba5c8db74cfb159c9e9e739d95154`. Current Nov 9 helper (source `Lab2Source.HelperSha`) is `0e7d9268840eaa10d7ac90833397632de900a4504b10af94e5491c26a732d5cc`; historical trial2 decode test was incorrectly using today's helper pin. Test now independently pins both immutable historical receipt SHA and original helper SHA; no archived artifact or production dependency pin changed. Independently corroborated by `docs/REA-RIFT-LAB2-READER-ADAPTER-2026-11-07.json` and `reader/contract-lab2-acquisition.md`.
- **Scope held:** No VMware inventory, observation, capture or control; no physical RIFT process, UI, input, memory, debugger, addon deployment, game restart, FreeBuff/Ollama, other-repository edits, privilege changes or external publication by commands in this slice. Only RRE source/doc and deliberately generated offline test artifacts were involved.

## Reproducible command receipts

1. **RED (expected test before fix):** `rre_20261116_lab2_policy_red_0001` `dotnet run ... --production-only` exited 1, exact `Historical Lab2 source was not rejected: AMD-DESKTOP`.
2. **GREEN:** `rre_20261116_lab2_physical_allroutes_final_green_0001` `dotnet run --project reader/Rre.Reader.Checks/Rre.Reader.Checks.csproj -- --production-only` exited **0, 101/101**, including direct C# acquisition and both-host offline-source checks.
3. **Build:** `rre_20261116_lab2_physical_reader_final_build_0001` `dotnet build reader/Rre.Reader/Rre.Reader.csproj -c Debug` exited **0, zero warnings/errors**, .NET 10.
4. **Direct CLI:** `rre_20261116_lab2_policy_doctor_0001` exited 0 with `lab2AcquisitionAllowedThisHost=false`; `rre_20261116_lab2_policy_cli_denial_0001` returned expected exit **2** `lab2-acquisition-disabled` even without an input file.
5. **Saved parser:** `rre_20261116_lab2_policy_saved_adapter_regression_0001` exited **0, 57/57** Node tests. Roadmap `rre_20261116_lab2_policy_roadmap_validate_0001` exited 0, 47 tasks/11 milestones/nine WA-006 source pins and negative control; `rre_20261116_lab2_policy_diffcheck_0001` `git diff --check` exited 0 (only a standard Git LF-to-CRLF notice for a test file).
6. **Historical all-checks limitation (not GREEN):** `rre_20261116_lab2_policy_full_reader_checks_0001` exited 1 after 173 earlier checks at `lab2-source-hash` because archived trial2 expected current helper bytes. The narrow historical test-pin fix reaches beyond this failure, but `rre_20261116_lab2_policy_full_reader_replay_green_0001` still exited **1** after the 173 earlier checks at `dependency-pin-changed` when a November 9 Python helper's `execution_hashes` inspected current installed legacy VMware/RR2 helper dependency hashes. This is obsolete host-dependency drift under physical-only policy; do **not** weaken/update those source pins or call VMware to make it pass. Preserve exact job output and historical evidence; active `--production-only` gate is green.
7. **Generated test artifacts:** `artifacts/reader-checks-cf955e4d973c492db187b209b33e000a` and `artifacts/reader-checks-e97b28e4e1ee4ebbb0bf80020c2bea11` are this slice's synthetic failure-output directories, separately inventoried. Both were inventoried as generated flat fixture directories and removed by an explicit two-path PowerShell cleanup, job `rre_20261117_scoped_reader_fixture_gc_windowsps_0001` exit 0. Workbridge retains failure/output job receipts; no historical source artifacts or inherited untracked paths were touched.

## 2026-11-17 ~00:10 EST — SC-629 physical readiness preflight (read-only)

- **Fresh host/ownership:** named AMD-DESKTOP Workbridge 0.16.5-dev, project `C:\work\rre`, `main` HEAD `90ff66cbba890d300faf9cf606258c15bc195ca0`, tracked tree clean; nine inherited untracked backup/probe entries preserved. No Workbridge-coordinated worker tasks or active RRE command jobs at entry. One independent ChatGPT read-only SC-629 acceptance audit found no new actionable offline code defect.
- **Source:** `addons/RRECollector/RiftAddon.toc` declares v0.4.21, SHA `1753b250e82ec0af68d5593b6534d0d8e09e351e112f4713e24bcbfe37620f59`; strict source package verifier job `rre_20261117_sc629_source_package_readiness_0001` exited **0**, 11 source files and strict manifest, no installed or runtime qualification.
- **Installed physical-addon files (read-only):** canonical OneDrive `RIFT/Interface/AddOns/RRECollector/RiftAddon.toc` still declares **v0.4.20** (SHA `0721255c6967c6f94a2e0e0a9f6da29e10aa7156ee2610aea9f4e6a624e0fba0`, modified 2026-11-12 02:23 UTC). Exact SHA comparison of all 11 source/installed files: **3/11 match** (`abilities.lua`, `candidates.lua`, `ui.lua`); **8/11 differ** (`core.lua`, `context.lua`, `capabilities.lua`, `candidate_catalog.lua`, `wire.lua`, `main.lua`, `README.md`, `RiftAddon.toc`). Installed parity verifier job `rre_20261117_sc629_installed_parity_expected_red_0001` exited expected **1** at the first `core.lua` mismatch. This is a real deployment **readiness failure**, not a failed v0.4.21 source test.
- **Physical character SavedVariables (read-only):** canonical OneDrive `RIFT/Interface/Saved/[account]/Deepwood/Atank/SavedVariables/RRECollector.lua` SHA `1c72fc3497914f03c42fadf35d21f0ad4caf87fbc89aed1da51b6be62aaad559`, modified 2026-11-17 05:08:15.983 UTC (00:08:15 EST). Root `addonVersion` and `latest.addonVersion` both **0.4.20**, `latest.sequence=2`, `latest.capabilities.experience=true` with three finite numeric fields. `memoryPublication.status=not-published`, `reason=addon-load`. These are persisted bytes, **not** proof of currently loaded UI, active game, full RREC2 publication, or current task ownership.
- **Current acceptance stop:** SC-629 register still `pending` with `gameInputAuthorized=false`. Source v0.4.21 **must not be marked installed or loaded**. No copy/deployment, game process/window inventory, in-game input, UI reload, reader memory acquisition, process/debugger action or VMware access was performed. No source files changed. Current reader supports offline replay sources; the retired `lab2` live acquisition command is disabled. A future approved physical trial requires (1) exact host/build/process/owner and separate deployment authority; (2) 11/11 installed SHA parity and loaded v0.4.21 UI proof; (3) operator-authorized manual Capture; (4) an independently authorized physical-client **active RREC2** extraction route and complete session/sequence; (5) same-trial SavedVariables root/latest v0.4.21 and cross-source parity. The SavedVariables file by itself is insufficient.

## Next gates / recovery packet

- **SC-629:** v0.4.21 collector remains source-only; physical installed/loaded RIFT, same-trial RREC2 and SavedVariables Experience receipts still need task-specific owner/host/process/build and separate approval. `gameInputAuthorized=false`.
- **WA-006/WA-007:** no verified same-scene two-nonself Lua/native identity; parked pending original evidence. Avoid parked Ghidra/REA breadth and repeated synthetic G2 cycles.
- **RC-30 / RC-88:** explicitly user-stopped, do not resume on generic continuation.
- **Resume:** Re-verify named AMD-DESKTOP host, `C:\work\rre` branch/HEAD/status, nine inherited untracked paths and running jobs. Check scoped five reader files plus this handoff; only manager commits/pushes after source-hash/diff/test review. Preserve original archived Lab2 files and old helper SHA. New physical RIFT input/deployment/reload needs a new specific authorized window.

```yaml
checkpoint:
  timezone: America/New_York
  host: AMD-DESKTOP
  repository: C:\work\rre
  branch: main
  startingHead: 9478db4634f1e5357b8c069e220ef88e315c713f
  task: reader-physical-only-routing
  offlineProductionChecks: 101/101
  offlineSavedChecks: 57/57
  fullLegacyChecks: blocked-by-host-dependency-pin-drift
  gameExecution: false
  vmAccess: false
  physicalAcceptance: false
  gameInputAuthorized: false
  nextTask: SC-629
  lastVerifiedHead: 90ff66cbba890d300faf9cf606258c15bc195ca0
  sourceCollectorVersion: 0.4.21
  installedCollectorVersion: 0.4.20
  installedSourceHashParity: 3/11
  savedCollectorVersion: 0.4.20
  savedMemoryPublication: not-published
```
