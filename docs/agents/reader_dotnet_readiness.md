# Reader .NET 10 readiness — offline LEGION lane, 2026-11-10

- Host: verified `LEGION`; isolated worktree `C:\work\rre-dotnet-readiness-20261110`, branch `agents/reader-dotnet-readiness-20261110`.
- Purpose: report whether the .NET 10 SDK needed by `reader/Rre.Reader/Rre.Reader.csproj` is available. A missing SDK must not break the existing REA/Ghidra/Java/Python inventory.
- Implementation: `tools/agents/reader_dotnet_readiness/probe-dotnet.mjs` (read-only `dotnet --list-sdks`, bounded 4-second subprocess, Windows standard-path fallback, no install or game access).
- Real LEGION smoke: `{ "host":"LEGION", "executable":"dotnet", "status":"not-found", "reason":"ENOENT" }`; command exited 0. This is local SDK absence, not a statement about the game.
- Unit tests: `node --test tools/agents/reader_dotnet_readiness/test-probe-dotnet.mjs` → **6/6 passed**; existing `node --test tools/test-native-toolchain-doctor.mjs` → **6/6 passed**.
- Synthetic AMD-DESKTOP test: SDK list `10.0.302 [C:\Program Files\dotnet\sdk]` returns `status:"present"`. Actual AMD SDK 10.0.302 was verified separately using `dotnet --list-sdks`.
- Proposed manager-owned integration in `tools/native-toolchain-doctor.mjs`: import `{ probeDotnetSdk }` from `./agents/reader_dotnet_readiness/probe-dotnet.mjs`, then add `dotnet: probeDotnetSdk(),` as an **informational** field beside existing probes. Never make reader SDK presence mandatory for native analysis.
- Scope: only this worker's `tools/agents/reader_dotnet_readiness/` files and this report; no shared source changes, installs, game/VM operations or push.
