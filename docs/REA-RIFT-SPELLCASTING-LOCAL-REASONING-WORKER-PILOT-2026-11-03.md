# RRE local reasoning-worker pilot and reviewed SC-103 feedback (2026-11-03)

**Coordinator:** single RRE manager (main-branch file owner). **Outcome:** 2/2 independent local model reviews completed, with source-tool receipts. **Integration result:** one additional combined failure regression and clarified frame-clock caveat. **No independent game evidence.**

## Actual worker capability and receipts

- Workbridge `0.16.4-dev` exposed 36 **concurrent command jobs**, not AI-agent slots. Its `agent_assign` / `agent_dispatch` tools allocate or bind already-running jobs; they do not start reasoning agents themselves.
- Local installed tools: `codex-cli 0.166.0`, OpenCode launcher, and `Ollama 0.40.13` with preinstalled `gemma4:12b` (11.9B Q4_K_M, tool-capable).
- Two initial ephemeral Codex read-only `--oss --local-provider ollama` jobs failed (exit 1) before inference because Ollama was not listening: `rre-real-local-agent-probe-audit-20261103-a1` and `rre-real-local-agent-api-audit-20261103-a1`. Starting Ollama in an earlier **separate** Workbridge job did not keep that process alive for the next job.
- One combined supervised Ollama + two Codex attempt `rre-local-ollama-two-agents-supervised-20261103-a1` reached two `thread.started` events but **both Codex workers failed** (exit 1) at `turn/start` with `modelProviderMismatch` (Ollama session versus current OpenAI provider); no Codex model review completed. Do not count those as successful agents. OpenCode help probe `rre-opencode-run-options-20261103-a1` failed `UNKNOWN`, so it was not used to make unsupported review claims.
- **Successful fallback:** `rre-two-direct-local-reasoning-workers-20261103-a1` (Workbridge command **exit 0**). A supervised, loopback-only `ollama serve` used local `gemma4:12b`; **two independent model conversations**, each with one restrictive **read_files** tool call against a hardcoded RRE source allowlist, completed in **107,199 ms** overall. The model had no file-write, game-control, external network or tool-execution capabilities. Both workers completed 2 model rounds. The supervisor stopped its own Ollama child after the reviews. These are real **local LLM reasoning workers**, not ChatGPT-native spawned subagents or 36 Workbridge reasoning slots.

| Worker | Read-only question | Result | Manager's independent disposition |
| --- | --- | --- | --- |
| `A-probe-logic` | Review `tools/sc103_luapad_hover_probe.lua` and its Lua fixture for specific lifecycle defects | **Completed**, 1 source-tool call | **Accepted one missing combined test**: timeout plus failed detach. **Rejected two false positives**: nil-versus-false detach is already covered, and the global state cleanup line runs even on a failed detach |
| `B-RIFT-API` | Review `Inspect.Tooltip` applicability and G1/Legendary identity limits | **Completed**, 1 source-tool call | Confirmed already documented limitation: even a valid ability-shaped ID lacks proof of native tooltip origin, current role/slot binding or a selected Legendary variant. Do not promote ID to Legendary selection |

**Reasoning quality gate:** Independent model suggestions are *leads*, not accepted truth. The manager reviewed actual source lines and existing assertions before incorporating any change.

## Applied source/test integration

- **Production staging file unchanged:** `tools/sc103_luapad_hover_probe.lua`, SHA-256 `b97bf0a1c0489114c71bd11f7d9b9868bea22c7f8b57d5a7de0fbd8d57c7127d`.
- **Synthetic fixture extended:** `tools/test_sc103_luapad_hover_probe.lua` now tests timeout with `Command.Event.Detach` returning false, verifies the temporary global clears despite a failed detach, and proves that a stopped frame-event stream has no automatic wall-clock callback and can be manually canceled. These are test-only improvements; no live game behavior is claimed.
- The exact revised Windows fixture was SHA-matched in an isolated assistant container and **110 assertions passed** in its Lua 5.4 shared-library runtime. This is **not** Lua 5.1/RIFT runtime proof. Verify the current fixture SHA from the RRE task register and the staged operator-probe report.
- The probe's `WINDOW_SECONDS = 12` is **frame-clock elapsed time checked on delivered frame events**, not an independent wall-clock watchdog. No callbacks => no automatic timeout until events resume or an operator manually cancels/rearms. Do not promise a universal real-time deadline.

## Productivity / resource judgment

The two local workers used no paid cloud-model inference but took approximately **107 seconds for two small reviews** (not counting failed preflights). The observed results were useful for extra negative coverage but **do not establish a speedup over direct ChatGPT review**. Attempt local agent launches on substantive independent tasks as the user requested; limit worker count to available GPU/runtime capacity and avoid retries of the same known-failing provider mismatch. Two useful workers are better than 36 inert command slots. If a future dedicated model-agent provider becomes callable, prioritize its explicit receipts over simulation.

**Preserved boundaries:** only RRE-owned task/test/document work; no installed addon, game input, runtime debugger, RIFT process or guest operation, remote push, raw SavedVariables export, Workbridge service replacement, or competing manager. SC-103 remains blocked on exact modern role/Legendary ID. RC-30 v0.4.10 and the desktop screenshot quarantine remain separate unverified live gates.
