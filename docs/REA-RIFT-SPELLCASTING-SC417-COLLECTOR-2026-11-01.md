# SC-417 — RRECollector v0.1.0 standalone addon scaffold (2026-11-01)

**Implementation:** source complete and independently reviewed; installed on physical PC; **live game loading/capture not yet verified**. This is a working-source scaffold, not completion of SC-102.

## Scope and source

- Standalone package: `addons/RRECollector/RiftAddon.toc`, `main.lua`, `README.md`.
- Manifest: `Identifier = RRECollector`, `Version = 0.1.0`, `Environment = 4.4`, character SavedVariable `RRECollectorData`.
- Commands: `/rre help`, `/rre status`, `/rre capture`, `/rre page N`, `/rre export`.
- Explicit manual snapshot, **no background polling or game actions**. Single API list, batch Detail with per-ID fallback, stats, player identity and combat-role type, optional active role slot/names, target, build/version field when supplied. All captures carry sequence/frame-clock and documented completeness/error counters.
- One snapshot per character SavedVariable `RRECollectorData.latest`; `/reloadui` or normal logout is required for on-disk flush. The frame clock is *not* UTC.
- List supports both string-keyed maps (including **false-valued memberships**) and numeric-array values; bounded to 1,024 raw entries / 512 IDs, sorted, distinct; misses and truncated/ignored entries prevent complete status. Scalar fields preserve false/zero. No assumption that known API IDs include unlearned trainer/soul/locked abilities.
- `Inspect.Unit.Detail("player").role` is the combat-role type; the optional `Inspect.TEMPORARY.Role()` is recorded separately as a candidate role slot, not a proved soul allocation.

## Reused evidence

- Installed `BotDsBridge/ability_catalog.lua` SHA-256 `3a2c4a7b5a6fa2e091e3b7846187973cf1344a16cdffba191cf00236fea8d300`: direct known catalog and character SavedVariables.
- Installed `RiftReader2Casting/model.lua` SHA-256 `dbd689b9f47140e95153a583e47a445ae3ac35794d293cf58c5d58e1143ce2bc`: batch Detail and useful scalar fields.
- Installed `RiftReader2Casting/main.lua` source audit: saved-variable load-end and slash-event lifecycle.
- Installed `RiftApiCollector/main.lua` SHA-256 `47755e48c8616a423eb69c2d4b1adf74c560a8d49d96e5b3f9a446fe0ec880be`: list-shape edge cases, completeness and slash registration.
- Independent review corrected false-valued list omission and added `gainCharge`/`racial`.

## Deployment and validation boundary

- Host install directory: `C:\Users\mrkoo\OneDrive\Documents\RIFT\Interface\AddOns\RRECollector` (new directory; no preexisting addon overwritten).
- Host copy/hash verification: Workbridge job `rre-sc417-host-addon-copy-hash-20261101-a1` exited **0**, `HOST_ADDON_COPY_PASS`; all three installed SHA-256 hashes equal Git source:
  - `RiftAddon.toc`: `cf98f6cce40c2be66e23edf003a89493eab00bad76ce1b1c69095dec0aa80419`
  - `main.lua`: `93fd9d3147c1b467c5d937b500d95eb2b5c9567f20c13d069ed2cddfa67532c5`
  - `README.md`: `10f3830e74f7f8801c379132ff883fd5e7628d658a978662c257904e58187be3`
- No working `lua`/`luac`/`lupa`/`luaparser` present in the Windows Python PATH check `rre-sc417-lua-availability-20261101-a1` (exit 0). Therefore no honest claim of bytecode-compiled Lua or live loaded state. Focused static package check `rre-sc417-static-package-20261101-a1` exit **0**, `SC417_STATIC_PACKAGE_PASS`; checked manifest/version/command/API/SavedVariable/false-valued ID path and 3/3 installed SHA matches. Roadmap validation `rre-sc417-roadmap-validate-20261101-a1` exit **0**, no failures (47 historical NAV tasks). Both checks are offline and do not prove live Lua load.
- A read-only physical-host process check (`rre-sc417-local-rift-process-20261101-a1`, exit 0) returned `NO_PHYSICAL_HOST_RIFT_PROCESS` on November 1. Consequently this session could not honestly verify an in-game addon load.
- No game commands, keyboard/mouse input, cast, process attach, or RR2/Workbridge changes. Physical-PC installed executable is the authoritative SC-102 target. VMware guest deployment deferred.
- Preserve the two unrelated pre-existing untracked RRE historical files.

## Next user/operator smoke check

1. On the **physical PC** RIFT client, load RRECollector through a normal game UI reload/start; confirm initialization message.
2. In game enter `/rre status`, `/rre capture`, `/rre page 1`. Ensure captured character/calling/level and a nonzero count of ability details; note partial/incomplete warnings.
3. Save with normal UI reload/logout. Inspect the newest character-scoped `RRECollectorData.latest` from SavedVariables and match its character/role to exact-time spellbook/soul UI and local executable SHA for SC-102.
4. Only after a genuine game smoke result promote SC-102 evidence; source/installation alone does not unblock spellbook or native casting research.

**Current state:** SC-417 package complete for first live trial; SC-102 awaits real matched API+UI evidence. M2 telemetry/event monitoring intentionally deferred until M1 actually loads.
