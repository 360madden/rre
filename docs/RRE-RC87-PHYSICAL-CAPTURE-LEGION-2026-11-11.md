# RC-87 - physical load, quest/ability capture and persistence

**November11, 2026, approximately23:12-23:15EST. One user-approved bounded physical LEGION validation completed.** RRECollectorv0.4.20 loaded, captured real Rogue data, persisted through the approved reload and was read by the host reader. This closes the earlier current-client evidence gap for this bounded observation, not for continuous acquisition or game automation.

## Observed result

- **Abilities:**53 unique IDs,53 details, zero Detail failures, complete API list, sequence1. The53-record toolbar state survived reload. The actual C# SavedSource output is complete and source-hashed.
- **Quests:**27 quests,43 objectives,15 remaining goals, sequence1. The result is **partial**:40 scanned indicator entries were unsupported by the collector's projection, no indicators were retained, no map reads occurred and no Map.Detail call failed. Remaining quantities are usable; no map locations or travel success are established.
- **Persistence:** the actual50,639-byte original has SHA256`159f37a3551735814e92a69b53e64538c27cbeecfada947da08f5ea493ae973e`. Quest and ability reader outputs bind exactly that original hash. Runtime-created shared-counter encoding required the [RC86 parser fix](RRE-RC86-QUEST-COMPARISON-LEGION-2026-11-11.md); original Lua was never executed.
- **Existing combat observer:** its newly persisted local38,745-byte file read successfully at SHA256`57a42c68a8c3e3a9b479f7a88381c07a63d99ee192093a943aaa27b68f9f8d3a`; it contains no recorded trials. This replaces the earlier unreadable-current-file uncertainty, not with a cast-success claim.

## Authority and provenance

The user explicitly answered **Allow this bounded validation**. Exactly the proposed sequence ran: back up/deploy onlyRRECollector, initial UI reload, `/rre quests` once, `/rre capture` once, one persistence reload. No movement, combat, quest interaction, memory read/write/attach, VM or Workbridge action occurred. The bounded input sequence is complete; no further game action follows from it.

Fresh host/process/window identity was LEGION, physical Glyph/Live RIFT PID22648/window328486, executable SHA256`1935a05c9db6d468e34e0055014a4a99c1b5afceb1695884e24600f5c20a4be8`. The installed0.4.18 eleven-file package was hash-backed up before deployment; all eleven0.4.20 source/install hashes matched. Before reload the UI showed0.4.14; after reload its title/startup showed0.4.20. Backup and exact source hashes are in the [machine receipt](RRE-RC87-PHYSICAL-CAPTURE-LEGION-2026-11-11.json).

Four original screenshots, the original SavedVariables copy and private reader outputs remain locally under `artifacts/rc87-legion-live-20261111-2313/`, excluded from publication. Their hashes are recorded; account paths, original character records and chat-containing images are not committed. Repository addon source stays byte-identical to `a2d9660`.

## Remaining discriminator

The installed API Markdown documents Quest.Detail objective indicators and Map.Detail location identifiers. It explicitly documents `{id=true}` for Map.List, but does **not** specify the key/value schema of objective indicators. Therefore the40 rejected entries establish an unsupported projection, not malformed game data. Their raw shape was not retained and cannot be recovered from this saved capture. Do not guess a field or treat every string key as a location identifier.

Prepare a small bounded shape-diagnostic addition, verify it offline and obtain a separate deployment/read-only capture window before running it. Coordinate-frame validity, feasible travel, objective completion, actual combat and continuous freshness remain unverified. General reader live/authenticity flags remain false despite this separately recorded bounded human-observed receipt.
