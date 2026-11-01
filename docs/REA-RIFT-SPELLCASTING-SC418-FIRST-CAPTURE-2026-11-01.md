# SC-418 — First real RRECollector saved ability capture (2026-11-01)

**Status:** COMPLETE as a saved *current API-known* character catalog. **SC-102 UI/soul/trainer eligibility reconciliation is still open.**

## Provenance and source qualification

- User confirmed in this ChatGPT conversation: capture was performed on the **physical-PC RIFT client**, followed by `/reloadui`, then closing the client. This is **operator-attested origin**, not a contemporaneous process-ID or executable-hash binding.
- Persisted character SavedVariable: `C:\Users\mrkoo\OneDrive\Documents\RIFT\Interface\Saved\<account>\Deepwood\Atank\SavedVariables\RRECollector.lua` (account component intentionally not reproduced in Git).
- Original saved file: **26,758 bytes**, SHA-256 `abbf08e8108faa2a9c85d1a61f9c4ab63070ee5ac9a29a041ebd83c058090482`, last modified `2026-11-01T21:41:31.367442Z` (flush/file time, not exact capture time). Source remains at its original path; raw private saved record was not committed.
- RIFT API-reported client internal version: `STABLE-1-1178-A-1256632`, build label `Oct 23 2026 11:32:27 RIFT-BUILD-12`, external `1.0.0`. Separate static physical-PC executable hash observed later in `rre-sc102-current-host-target-check-20261101-a1`: `1935a05c9db6d468e34e0055014a4a99c1b5afceb1695884e24600f5c20a4be8` (60,493,640 bytes). **Do not assert this PE hash is process-bound to the captured client without contemporaneous process proof.**
- Windows host process check after the operator closed RIFT returned `NO_PHYSICAL_HOST_RIFT_PROCESS`; this is consistent with the operator's sequence and does **not** imply that the capture originated from a VMware guest.
- RRECollector source package: commit `332ad7f`, `addons/RRECollector`, manifest `885527d8d007c6b785cbeeeb52fef73ccf1962abe4ab6c04400b285f2d24789f`, schema 1, addon version 0.1.0.

## Result

| Property | Actual record |
| --- | --- |
| Character | `Atank`, level 45, Warrior |
| Character ID | `u035400012FA2D207` (session-scoped; not a static player pointer) |
| Combat role | `tank` |
| Active role slot | `1` (from optional `Inspect.TEMPORARY.Role()`) |
| Role names available | `Righteous Defender`, `Beast/Warlord`, `Role 3`, `Role 4`; exact role-slot-to-name mapping requires confirmation |
| HP | 18,208 / 18,208 |
| Power | 100 |
| Ability list | **69 raw entries, 69 unique lookup IDs, 69 details** |
| Detail errors / fallback | **0 / 0** (batch Detail succeeded) |
| Ignored / truncated / duplicate | **0 / 0 / 0** |
| API list completeness | `enumerationComplete=true`, `captureComplete=true` for **current listed abilities only** |
| Optional sections | player, role slot/list, stats, client version and frame time present; target unavailable at capture |

Each of 69 records has `lookupId`, `id`, `idNew` and `name`. Field presence (not true/false counts): `cooldown` 39, `castingTime` 17, `channeled` 2, `passive` 7, `rangeMax` 27, `costPower` 33, `unusable` 12. Absent fields are **unknown**, not false or zero.

Examples: Righteous Charge, Shield of the Chosen, Spark, Patron's Artifact Tracking, Interfere, Summon Primalist Trainer, Amnesty and Legacy of the Shade. These are sample known-API names, not a classification of trainer unlocks.

## Evidence checks and limits

- `rre-sc102-savedvar-discover-20261101-a1` exit 0: found one `RRECollector.lua` under SavedVariables, hashed size and mtime.
- `rre-sc102-savedvar-inspect-20261101-a1` exit 0: confirmed Lua saved table and `captureComplete=true`.
- `rre-sc102-savedvar-context-20261101-a1` exit 0: established character, role, stats, API build and counts.
- `rre-sc102-savedvar-ability-integrity-20261101-a1` exit 0: independently counted **69 records and 69 unique IDs** from original serialized source; summarized populated metadata fields.
- `rre-sc102-current-host-target-check-20261101-a1` exit 0: host process absent *after* game closure and executable static SHA observed.

The current ability catalog is a successful milestone. It does **not** prove all learnable/unlearned/locked abilities, current soul point allocations, action-bar bindings, an actual cast request, or current UI spells. Existing Lab1 Atank screenshots are a different time/source, not an automatically qualified physical-PC UI match. **SC-102 now waits on the physical-PC spellbook/soul/trainer/action-bar UI cross-check**, rather than on missing ability API output. No additional game session is required merely to retrieve this saved catalog.
