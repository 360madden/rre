# SC-103 — Protector's Fury Normal/Legendary variant-ID gap (source-first)

**November 3, 2026 UTC.** Offline read-only research against the physical PC's installed disabled historical ProjectAbilityBook and committed RRECollector. No game input, addon change, SavedVariables write, client reload or variant-ID assertion.

## Accepted facts

| Source | Verifiable observation | Limit |
| --- | --- | --- |
| Installed disabled `projectabilitybook.disabled/Callings/Warrior/Paladin.lua` | SHA-256 `e4af04464201adbc5cbae9d07cab0e36a9da616b5b30abd466f8ca44c8f92f28`; the only `Protector's Fury` entry maps to `A0E2112FD6FE262EE` at lines 106–109 | Historical static data, not authoritative current-client variant resolution |
| Bounded recursive search of 138 historical addon source files | Exactly one match for the name and one for that ID; zero `Legendary` or `variant` text matches; no truncation | Absence in this file collection does not prove the game has no separate variant implementation |
| [SC-102 physical UI tooltip](REA-RIFT-SPELLCASTING-SC102-PALADIN-TOOLTIPS-2026-11-02.md) | November 1 original screenshot `2026-11-01_210700.jpg`, SHA-256 `f5ff8c9b10e5ce00c34046fe6862f8259ce66089191979c7b6ad90e2a444f03d`, presents Normal and Legendary descriptions | The screenshot does **not** expose modern stable IDs or prove a selected active variant |
| [RC-29 exact-ID atlas](REA-RIFT-SPELLCASTING-SC103-353-ID-DETAIL-ATLAS-2026-11-03.json) | SHA-256 `5da0b32bc6fd67e86b883d44155c86fb5ff05cab1655b216ebed2fb4e5cd5fb7`; original list did not contain that ID; one explicit-ID canary returned `no-detail` | Not evidence of locked, removed, unlearnable or variant-mismatched status |
| `addons/RRECollector/abilities.lua` | SHA-256 `d181ba0061a5959474dd3487b41c114f631122375a8b67421817fd54fdc1c510`; the Detail field-copy allowlist at lines 7–15 does not include `rank`, `variant`, `legendary` | Missing fields in our saved export cannot disprove native API support |
| `addons/RRECollector/capabilities.lua` | SHA-256 `0ed3ccf0fad438008d9e76d0ec5ddeefd31b5b28c860ba523d53392659f202ef`; exact `Inspect.Ability.New.Detail` function presence is checked, but its name is not in the eight-element `DOCUMENTED_NAMES` query list | Prior `/rre probe` did **not** request its detailed documentation string |

The earlier [RC-02 capability receipt](RRECOLLECTOR-RC02-FIRST-PROBE-2026-11-02.md) established that physical client `Inspect.Documentation` was callable, indexed 1,910 entries and found `Inspect.Ability.New.Detail` callable. **Superseding November 3 correction:** The narrower RRECollector probe did not request this string, but a different already-installed addon, `RiftReader2Casting`, had saved it. [SC-103 runtime documentation](REA-RIFT-SPELLCASTING-SC103-RUNTIME-ABILITY-DETAIL-DOCS-2026-11-03.md) verifies 2,711 stored characters, 34 documented Detail return fields, and **34/34 exact coverage** by the RRECollector whitelist. No documented rank/variant/legendary/unlock member, but undocumented/UI/native mechanisms remain unknown. The original 'not captured' statement applied only to RRECollector's own probe.

**Related name, not a variant ID:** the screenshot's Legendary description references `Light's Balm`, a separate named Paladin healing ability with historical ID `A250E73987922CA1B`. It was listed in the preserved 69-ID API catalog. Neither that association nor the screenshot establishes a second Protector's Fury ID.

## Highest-value next checks

1. **P1 — Complete the currently installed v0.4.10 runtime gate.** A user-supplied screenshot confirms visual load (Known69, Static96). Physical SavedVariables latest root is still v0.4.9; a version-matched v0.4.10 save plus reversible Pin→Undo and stale saved-ID display remain unverified. Do not add speculative fields.
2. **P2 — Documentation retrieval complete; do not re-probe unchanged text.** The existing RR2Casting SavedVariables already contain exact in-client Detail documentation (34 members), separately audited. No more broad documentation request is warranted unless an independently identified game-build change or field-drift question requires a new qualification.
3. **P3 — Same-session visual + single-ID comparison only if needed.** Record current Protector's Fury rank and Normal/Legendary UI state, then the single exact ID's List membership and Detail response. Existing `/rre candidates` can expand to all 57 unlisted IDs; do not use it as though it were a two-ID tool. Any new manual selective query must be separately source-tested.
4. **P4 — Only then consider revised metadata export.** If current documentation or a bounded raw-object shape probe verifies a new scalar field, add an explicitly typed, privacy-reviewed whitelist entry and tests. Do not save arbitrary Detail objects or runtime target IDs.

**Decision:** One historical static ID is proved; a distinct modern variant ID is **unsupported by current evidence and unresolved**, not disproven. No character rank threshold, eligibility or cast result was established.
