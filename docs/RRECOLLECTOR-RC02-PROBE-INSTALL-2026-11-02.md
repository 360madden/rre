# RC-02 — Guarded runtime API probe installation receipt (2026-11-02)

**State:** source implementation **committed**, physical-PC add-on installation **SHA-verified 7/7**. **Subsequent operator-driven `/rre probe` succeeded:** see [live persisted receipt](RRECOLLECTOR-RC02-FIRST-PROBE-2026-11-02.md). This document preserves the **pre-probe** installation and instructions; it is no longer the latest runtime-status source.
**Source commit:** `8d41ed8` (bounded `/rre probe`) after `17580f7` modular core.  
**RC-00 decision:** [exact capability goals and source limits](RRECOLLECTOR-RC00-API-FEASIBILITY-2026-11-02.md).

## What works in source

- One standalone `RRECollector` identifier and `RiftAddon.toc` with full metadata (`Email`/`NameShort`, `Environment`, `SavedVariables` and dependency-ordered `RunOnStartup`): `core.lua` → `context.lua` → `abilities.lua` → `capabilities.lua` → `main.lua`. Version `0.2.0`, saved schema **1**.
- Existing `/rre help|status|capture|page N|export` and `RRECollectorData.latest` still exist. The new manually invoked **`/rre probe`** writes a separate `RRECollectorData.probe`; failure leaves the previously accepted known-ability record untouched.
- The probe checks exact `Inspect`/`UI.Native` paths by type (no invocation); calls `Inspect.Documentation()`/named documentation through guarded `pcall` only; limits index scan to 2,048 entries, retained matching names to 96, names to 160 characters, and individual description excerpts to 512 characters. It does **not** invoke `Inspect.Setting.Detail`/`Role.List`/`Action` APIs, read every setting, act in game, cast, poll or extract all documentation.
- Saved receipt includes character/role context, build/frame/real-time, path types, short relevant name list, document return status/errors, truncation and count metrics. Missing APIs are reported as “not present in this probe,” **not** a universal API absence verdict.

## Physical-PC deployment receipts

The installed `C:\Users\mrkoo\OneDrive\Documents\RIFT\Interface\AddOns\RRECollector` was an exact known v0.1 package before mutation (manifest `885527d8...`, main `93fd9d31...`, README `10f3830e...`). Job `rre-rc02-host-process-preflight-20261102-a1` exit **0** returned `NO_RIFT_X64_PROCESS` immediately before installation. The four new Lua modules were written first, then own README/main, and the own TOC **last**. No other addon/game file changed.

| Source + installed file | SHA-256 (matched on physical PC) |
| --- | --- |
| `core.lua` | `4275fd0b096aab0758f792fd31f92b14ba89423bf35dd1a430dfb46550bd7a83` |
| `context.lua` | `79338dcee1fc70ecd8e039031dd7526e636c6c96a4fae3a133957467f6aef658` |
| `abilities.lua` | `2e20896e7d02c5af159d4f7fec0583e6c8d43671f804ffe851472470653c1c4e` |
| `capabilities.lua` | `0ed3ccf0fad438008d9e76d0ec5ddeefd31b5b28c860ba523d53392659f202ef` |
| `main.lua` | `fa028516660ef4f1bf01686f873d966aa171598c6b4e2ca00d5867851319cf87` |
| `RiftAddon.toc` | `62edef2a40df8b1665f968ccb3321ada45b25002f9d82cac1dfb277dfcede874` |
| `README.md` (post-deployment status corrected) | `3ceaccb47ce3527929776733014ff648f62d8959cfce3c191f99ffeec0ca6692` |

Every hash was re-read and compared (7/7); README was corrected and re-deployed again after that first parity check, with its final SHA shown above. No repeat game capture or private SavedVariables commit was performed.

## Focused checks and their limits

- `rre-rc02-source-structural-20261102-a1` exit **0**: `RC02_SOURCE_PASS`, verifying selected bounded strings, read-only path, separate `probe` save, retained `latest` write, TOC order and version/schema.
- `rre-rc02-source-diffcheck-20261102-a1` exit **0**, only normal Windows LF/CRLF warning.
- **These source-only checks did not compile Lua or establish live load.** At the installation checkpoint the actual 2026 RIFT API index and soul/setting/action availability were unknown; the later operator-attested persisted [RC-02 runtime receipt](RRECOLLECTOR-RC02-FIRST-PROBE-2026-11-02.md) supersedes that uncertainty for the tested paths. The saved `SC-418` original 69/69 catalog remains separately qualified.

## Historical operator instructions (completed; retained for reproducibility)

On the **physical PC** (not a VMware lab):

1. Open RIFT normally, on the same Atank character/role if possible. Confirm a green/normal `[RRECollector] v0.2.0 ready` message, or record the exact addon error.
2. In RIFT chat, manually enter **`/rre status`** then **`/rre probe`**. Record the console response about `documentation` and `matching names`. Do not re-run `/rre capture` merely to retrieve the existing 69 known abilities.
3. Enter **`/reloadui`** (or normal logout) to flush character SavedVariables. Report when done; RRE can inspect and hash the new `RRECollectorData.probe` alongside the preserved `latest`.

The operator completed the probe and the saved source was inspected as [RC-02 first runtime receipt](RRECOLLECTOR-RC02-FIRST-PROBE-2026-11-02.md). The tested direct Soul/Action methods were `nil`; no new soul/eligibility/bar producer is justified, and **SC-102 same-role spellbook/soul/trainer/action-bar screenshots** remain the next gate. RC-02 is complete at operator-attested runtime scope, not from installation alone.

**Rollback:** Source history `332ad7f` is the accepted v0.1 installed package; Workbridge per-file guarded mutation journal recorded each v0.2 host write. Before rollback check current host hashes and preserve any newer operator edits. Do not delete/overwrite unrelated addons.
