# RC-01 — RRECollector modular source scaffold (2026-11-02)

**State:** COMPLETE at source/structural compatibility scope; **NOT deployed or proven loaded in-game**.  
**Prerequisite:** [RC-00 capability assessment](RRECOLLECTOR-RC00-API-FEASIBILITY-2026-11-02.md).  
**Owner:** RRE `addons/RRECollector` only.

## Concrete change

- Versioned the RRE-owned source addon from **v0.1.0** to **v0.2.0**; **SavedVariables schema stays 1**, `RRECollectorData.latest` stays the same.
- Kept one addon identifier `RRECollector`, one slash prefix `/rre`, the same `help`/`status`/`capture`/`page N`/`export` logic and all original List/Detail safeguards.
- `RiftAddon.toc` lists scripts in dependency order: `core.lua` → `context.lua` → `abilities.lua` → `main.lua`. Preserved complete metadata including `Email`, `NameShort`, `Environment`, `SavedVariables` and `RunOnStartup`.
- `core.lua` exports shared safe wrappers and a single version/schema namespace. `context.lua` exports player, target, role, stats and clock capture. `abilities.lua` exports the existing bounded ID/Detail collector. `main.lua` remains event/command/persistence bootstrap. No new API probe, polling, cast action or other behavior was added here.

| Source file | SHA-256 after RC-01 |
| --- | --- |
| `core.lua` | `4275fd0b096aab0758f792fd31f92b14ba89423bf35dd1a430dfb46550bd7a83` |
| `context.lua` | `79338dcee1fc70ecd8e039031dd7526e636c6c96a4fae3a133957467f6aef658` |
| `abilities.lua` | `2e20896e7d02c5af159d4f7fec0583e6c8d43671f804ffe851472470653c1c4e` |
| `main.lua` | `ec7dad8fbc1d39127ab290387e4ff704901695dc29345e46c228ef1000eb0d39` |
| `RiftAddon.toc` | `b38cfdda10dd526d5cc9529d1a1a1716578b266f300e13afc0747273c811d28e` |
| `README.md` | `3df3f8a5ee1aa696d9231802006c3fc66f8aa11528da7734a993b5cc2c3fe3a5` |

## Focused validation

- Job `rre-rc01-structural-compat-20261102-a1`, exit **0**, `RC01_STATIC_PASS`: programmatically compared every original function body from Git v0.1 to the module contents, including exact bounded field arrays; checked the complete four-script TOC load order, v0.2 version/schema, slash registration and saved-data assignment.
- Job `rre-rc01-diff-check-20261102-a1`, exit **0**. Git gave only the normal Windows LF/CRLF working-copy warning.
- **Limit:** This is a source-level structural check, **not** a Lua bytecode-compiler check and **not** an in-game load/capture. No source-file success is promoted to a live guarantee without the operator's later smoke check.

## Deployment and next step

**No file in the installed physical-PC `Interface/AddOns/RRECollector` was changed by RC-01.** The accepted v0.1 SC-418 69/69 SavedVariables record remains the live reference and must not be overwritten for convenience.

Next **RC-02**: implement a single manual read-only `/rre probe` to test the exact runtime `Inspect.Documentation`/role/setting/soul/action candidate API surface, keeping the existing `latest` ability snapshot untouched. Review source and TOC, then after coherent implementation hash-compare the installed addon's files before requesting the user to run one live command and normal `/reloadui`.
