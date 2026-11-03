# SC-103 — Current saved RIFT ability-detail API documentation recovery

**November 3, 2026 UTC. Decision:** The missing documentation probe is already satisfied at stored in-client documentation scope. A separate installed `RiftReader2Casting` addon previously captured the text from `Inspect.Documentation("Inspect.Ability.New.Detail")`. No new game input, addon change, API call, or raw SavedVariables export was needed for this finding.

## Audited provenance

| Item | Evidence |
| --- | --- |
| Installed addon source | `Interface/AddOns/RiftReader2Casting/main.lua`, lines 357–367, SHA-256 `7e24d78eeaf589bf76a7e4d59b4f6be5242d8c8d4947448995c33a60da945213` |
| Mechanism | Protected `pcall(Inspect.Documentation, "Inspect.Ability.New.Detail")`; stores bounded text under `RiftReader2CastingEvidence.runtimeApi` (16,000-character cap) |
| Initial physical saved documentation evidence | 41,980 bytes, SHA-256 `2bf6d92f9c1b437f7d8764db6596225435e78785af5d3d68214e3be11157afe4`; last modified `2026-11-03T04:12:44.560Z` (superseded as newest file, retained as the original audited 34-field source) |
| Stored addon version | `0.4.0` |
| Exact returned documentation | 2,711 characters, SHA-256 `73d52608384c39888bd4328143b092bb1f0f3de7d3e0eb8f001118a1438b753d`, not truncated |
| Current RRECollector serializer | `addons/RRECollector/abilities.lua`, SHA-256 `d181ba0061a5959474dd3487b41c114f631122375a8b67421817fd54fdc1c510` |
| Sanitized field-only machine evidence | [SC-103 field inventory](REA-RIFT-SPELLCASTING-SC103-RUNTIME-ABILITY-DETAIL-FIELDS-2026-11-03.json) |
| Focused verifier | `node --test tools/verify-rift-ability-detail-runtime-fields.mjs`: **3/3 passed** |
| Independent review | Extra High reviewer verified current source, saved-file SHA/document hash, exact 34/34 field match, and privacy boundary in two read-only audit jobs; **APPROVE** |

The saved file modification time is a *persistence* timestamp, not proof of when the addon originally called the documentation API. The record does not independently bind that text to a presently rehashed RIFT executable. The same documentation hash observed across character saves is a consistency check, not a per-build proof.

## Exact coverage finding

The in-client documentation describes **34 returned members**. The `RRECollector` Detail-field export allowlist contains exactly those **34**, with **zero documented members omitted and zero extra members**. These include `id`, `idNew`, `name`, `description`, `castingTime`, `channeled`, `continuous`, `cooldown`, six resource costs plus `gainCharge`, focus range, `rangeMin`/`rangeMax`, `outOfRange`, `unusable`, and current cooldown timestamps/durations. The full deterministic field list is in the JSON report.

Not documented as returned members: `rank`, `variant`, `legendary`, `requiredLevel`, `soulPoints`, or `unlockState`. This is **not proof** that the engine lacks these concepts or cannot expose them through an undocumented member, different API, game UI, or native code. In particular, `idNew` is **not** a demonstrated Legendary mapping, and `unusable` alone is **not** proof of an unlearned or locked ability.

The documentation explicitly describes `target` as a Unit ID. The sanitized JSON includes the *word* `target` only as a field name; no target values, private character identity, raw save contents, or ability snapshots are exported.

## Subsequent current-save key qualification (07:54 UTC, November 3)

A **new read-only, bounded** inventory of Atank's physical-PC `Deepwood/Atank/SavedVariables` found 36 Lua files. The three recent, relevant saved files below were inspected for literal `legendary`, `soul`, `role`, `talent`, and `invested` tokens and matching quoted Lua table keys. Only filenames, sizes, modification times, hashes, token counts and matching key names were emitted; no saved values, target IDs or character state were exported.

| Save basename | Bytes | SHA-256 | Relevant explicit evidence |
| --- | ---: | --- | --- |
| `RiftReader2Casting.lua` | 44,313 | `94b8b4a47d72f2715b4e8ebbc877f31361425d18ab2789209144cb78bcf1956c` | Saved `2026-11-03T06:24:32.122Z`; `legendary` token **0**, `soul` **2**, `role` **9**, `talent`/`invested` **0**. A separate exact key-name pass found no quoted `legendary`, `soul`, `role`, `talent`, or `invest` table keys. |
| `RiftReaderValidator.lua` | 1,119 | `a396524b66006be2f44f54a90fd824c2763f8f9efdb837a4f0db68b68d9c315c` | Saved `2026-11-03T06:24:32.152Z`; no matching structured keys or `legendary`/`soul`/`talent`/`invested` tokens; two generic `role` occurrences. |
| `SpellDump.lua` | 27,315 | `4b76e9885f1d28335bc68a0cb8a2d1f32fd7d39a5ebfb987f9dcfa77dcb6462e` | Saved `2026-11-03T06:24:32.169Z`; no matching structured keys or any of the five tokens. |

**Limit:** A literal saved-key/token check cannot rule out differently encoded, undocumented or separately stored soul state, and a save timestamp is not proof of a fresh client API call. The other 33 files were inventoried by filename, not content-audited. None of the three examined files supplies a **verified current role, invested-point layout, Legendary selection, or normal-vs-Legendary Protector's Fury identity**. An operator-qualified native Soul Tree observation remains the next discriminator; do not rerun the parked descriptor trace or broaden live probes on this negative finding.

## Revised task outcome

1. **Close the SC-103 API documentation retrieval sub-question:** Current stored documentation was available from an already installed addon. The earlier statement that no in-client `Inspect.Ability.New.Detail` documentation had been captured was too broad; only the narrower RRECollector capability probe omitted it.
2. **Keep the SC-103 rank/variant/eligibility task blocked:** Protector's Fury historical exact ID `A0E2112FD6FE262EE` returned no current Detail; alternate Legendary or rank ID is unknown. Other abilities returning `unusable=true` are not automatically learned/unlearned.
3. **Next discriminating observation:** Operator-supplied, same-session/current-role tooltip or Soul Tree comparison for normal versus Legendary Protector's Fury, preserving exact ability IDs where actually exposed. If decisive, do one bounded current Detail lookup of the *new* exact ID; do not rerun a broad scan or duplicate the documentation query.
4. **Physical RC-30 gate separate:** The user-supplied v0.4.10 browser screenshot proves visible UI load, and the later collector SavedVariables SHA `bdf78a8811cc9fa58fcf649bfd8fec98aa3bc93c9d02ec6c01398cc5582da8ac` proves **pre-Pin v0.4.10 persistence**. Neither establishes the current in-memory slot baseline, manual Pin→Undo, stale saved-pin rendering, Reload UI click, post-Undo persistence, or castability.

**No RRE-owned game input or process control, no modifications to the installed RR2Casting addon, and no private data publication.**
