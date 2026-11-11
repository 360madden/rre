# RC-32 / SC-103 — installed RRECollector 0.4.18 ability-capture gate audit

**November 11, 2026, ~16:39 EST.** Owner: single RRE manager on independently verified **AMD-DESKTOP**. Method: read-only, original installed-disk Lua source and synthetic off-game execution. This is **not** proof that a game process loaded 0.4.18, nor RC-30 live acceptance.

## Exact files and finding

- Repo `addons/RRECollector/abilities.lua` (TOC version 0.4.14): SHA-256 `816ded745b98a997996208b486cfc732f39808ed94c848ab0cb90851fbe2bf82`.
- Already installed `Documents/RIFT/Interface/AddOns/RRECollector/abilities.lua` (disk TOC version 0.4.18): SHA-256 `53ce2cbec81f160009470bfa24b00de23685e56dd02df400ff763c6bae8dd4ef`.
- Installed `core.lua`: `66c6733eaef353f0be5464b2893aca07ecf20a5ad55a05842e126fe380d28914`; installed `context.lua`: `e00a98330dcaf78410d54f72a034a18a859eca461520056b5b22074e1a135ba9`; installed `main.lua`: `28be36d96130b022f405d35fb261cf35e1d6efbba73a301a404839355ccc0204`.
- Both ability exports retain **exactly the same 34 `Inspect.Ability.New.Detail` allowlisted fields**. Neither exports an explicitly named rank, variant, legendary, unlock or selected-Legendary field; this is a source-export limitation, not a declaration about all native/API possibilities.

Compared with repository 0.4.14, installed 0.4.18:
1. Rejects candidate List keys unless exactly **17 ASCII characters**, `A` plus **16 uppercase hexadecimal digits**; older source admitted other nonempty keys up to 128 bytes.
2. Treats a batch Detail table without a substantive `name`, `idNew` or `description` as inconclusive; attempts one scalar Detail fallback and otherwise reports failure. Older source accepted any Detail table, including `{}`, as a record.
3. Rejects empty successful Lists as **incomplete**, and requires qualified player ID, name, calling, level, role slot, finite frame and real times before marking `captureComplete`. Older source could mark an empty catalog or an incomplete player context as complete.
4. Bounds/resets malformed, negative, nonintegral, nonfinite or too-large saved sequence values instead of incrementing them blindly.
5. Installed `main.lua` lines 275–315 preserves an earlier complete `latest` when a new capture is incomplete; the stronger installed `captureComplete` decision therefore reduces the chance of replacing a prior good capture with an apparently complete empty/blank catalog. This is a **source-level implication**, not a measured live persistence result.

## Tests and controls

- Job `rre-20261111-1631-v0418-offline-lua`: pinned existing Lua 5.3 executable/DLL and installed `abilities.lua` hashes, **14/14 synthetic assertions**, exit **0**. Cases: valid List/batch, empty List, malformed ID, blank batch with successful scalar fallback, blank scalar, missing player/role, nonfinite frame time and invalid sequences. An **in-memory mutation** removing the nonempty-List check was explicitly detected by its false acceptance.
- Job `rre-20261111-1631-v0418-differential`: independent Python hash/34-field equality verification and **10/10 source-executed Lua differential assertions**, exit **0**. Actual repo 0.4.14 and installed 0.4.18 functions were executed against the **same** mocked API/context scenarios. The expected older false accepts and installed rejections/fallback were observed. Runtime exe/DLL were hash-pinned; no source, SavedVariables, installed addon, or game files were written.

These mocks establish implementation behavior on the inspected disk files; they do not establish in-game Lua load, current source/process epoch, current player identity, real ID distribution or an actual capture/save event. The stricter 0.4.18 completeness requirements can also produce intentional **false negatives** when an expected context field is legitimately unavailable; this needs a version-matched live receipt, not relaxation on speculation.

## Decisions and next gate

Preserve installed 0.4.18; **do not synchronize repo 0.4.14 over it**. Do not re-run historic RC-30 operator actions to fill the missing same-trial screenshot C/pre-Pin save. The SC-103 modern Protector's Fury Legendary variant ID is still **unresolved**; unchanged 34-field whitelist provides no new ID. SC-306 native values `0/2`, SC-604 end-to-end cast mechanism and ROOT-001 live identity remain unqualified.

**Next authorized-owner step:** At the next separately approved current-process observation, confirm the *actually loaded* addon version, a new `latest.addonVersion == loaded version` sequence and valid current player/role/timing fields before comparing Lua/native identity. Preserve original evidence; no RRE-owned game input, reload, process control, installed addon change or RR2/REA repository edit. No new native RVA/offset was discovered, so the RRE-owned RR2 discovery feed must not be rewritten.
