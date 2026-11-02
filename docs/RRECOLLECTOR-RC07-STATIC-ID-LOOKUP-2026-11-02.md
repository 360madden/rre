# RC-07 / SC-103 — Warrior static-ID API lookup scaffold, physical-PC installation

**Date:** 2026-11-02. **Owner:** RRE/REA manager. **Scope:** source-qualified static inventory and RRECollector v0.3.0 install; **not** a live candidate lookup result.

## Decision and outcome

Reused the single independent, read-only `RRECollector` addon and `Inspect.Ability.New.Detail(id)` documented parameter shape. The v0.1 `RRECollectorData.latest` current-API baseline (69/69) and v0.2 `RRECollectorData.probe` capability receipt (1,910 indexed names, 22 relevant) remain separately preserved in character SavedVariables; neither was recaptured or overwritten. No new standalone addon or external helper app was needed.

A source-hashed, disabled ProjectAbilityBook Warrior static catalog yields **96 distinct IDs**: 34 Paladin, 33 Void Knight, 29 Paragon. Against Atank's preserved 69 current API-listed IDs, **39 are listed and 57 are absent**. Six screenshot-named Paladin static candidates are among the latter. An absent ID says nothing by itself about unlock, trainer offer, rank, learnability, slot binding or castability. Static name/ID mismatches or stale source remain possible.

| Static file (installed disabled ProjectAbilityBook) | SHA-256 | Candidate IDs |
| --- | --- | ---: |
| `Callings/Warrior/Paladin.lua` | `e4af04464201adbc5cbae9d07cab0e36a9da616b5b30abd466f8ca44c8f92f28` | 34 |
| `Callings/Warrior/VoidKnight.lua` | `b8dd0a75359fac18515a346d1492ce2885eb1a0fdd01ca459dffbdb236a94439` | 33 |
| `Callings/Warrior/Paragon.lua` | `6798169325e337613a5ff28c4a0c1f2830f67d8ac0da9dc584cde1e8a1421a9b` | 29 |

The machine-readable [96-record source inventory](REA-RIFT-SPELLCASTING-SC103-WARRIOR-STATIC-ABILITIES-2026-11-02.json) preserves exact source IDs, names, soul, category and icon without collapsing duplicate names; the source-hashed `candidate_catalog.lua` carries the four fields required for client lookup. Catalog version: `pab-warrior-96-e4af0446-b8dd0a75-67981693`.

## Read-only runtime behavior (v0.3.0)

- Complete TOC metadata retained (including Email), startup order `core` → `context` → `abilities` → `capabilities` → `candidate_catalog` → `candidates` → `main`.
- New `/rre candidates` command and one opportunistic, **single-pass** startup attempt after character SavedVariables load; a prior successful same-catalog receipt suppresses repeated startup querying. If Warrior identity or List/Detail is unavailable, the attempt defers without overwriting prior data.
- Guarded List membership snapshot, then at most one currently listed Detail control and eight absent-ID canaries (six named Paladin screenshots, first absent Void Knight and Paragon). If at least one absent ID returns identifying metadata, expand to remaining static unlisted IDs; otherwise mark unattempted candidates explicitly. Hard caps: 128 catalog IDs and 1,024 raw List entries.
- Whitelisted scalar detail fields (name, idNew, description, cooldown, costs, range, etc.) are stored only when returned; explicit statuses distinguish `returned`, `no-detail`, `lookup-error`, `inconclusive-table`, and `not-attempted-canary-stop`. No assertion of unlearnability follows a negative result.
- New receipt `RRECollectorData.candidateLookup` and `candidateSequence`; old `latest`, `sequence`, `probe`, `probeSequence` semantics remain untouched. Data flush occurs on a **normal** UI reload/logout; no RRE-owned game input, polling, casting, process control or other-addon writes.

## Physical-PC installation receipt

User-authorized scope: only `C:\Users\mrkoo\OneDrive\Documents\RIFT\Interface\AddOns\RRECollector`. All **seven** previously installed v0.2 files matched the Git source hashes before the operation. Two new files were added; old addon files updated with the TOC **last**. A single bounded host command completed with exit code **0** and **9/9** source/installed SHA-256 parity:

| File | Installed SHA-256 | Match |
| --- | --- | --- |
| `candidate_catalog.lua` | `10dddab8779fdb6253fa372ca47632c2396e1d3a15edddb40c17c495bd3adccd` | Yes |
| `candidates.lua` | `f558b68cab4804f78bbff4d5d1c4a234a6973fbdce60c76d93be77b487c38e85` | Yes |
| `core.lua` | `ef5a3d1f95d9f7b90a0a979795082140c696b748d1e25181331ad4f263fed095` | Yes |
| `context.lua` | `f0e1750e815a7e43cbf4c36231ffd7f354b27a7b3636a23637de1c57129f5e10` | Yes |
| `abilities.lua` | `d181ba0061a5959474dd3487b41c114f631122375a8b67421817fd54fdc1c510` | Yes |
| `capabilities.lua` | `0ed3ccf0fad438008d9e76d0ec5ddeefd31b5b28c860ba523d53392659f202ef` | Yes |
| `main.lua` | `866b4ab3b6e3aeb5bde2e1204d3675b0cf569ce847c42b78a45e7e70e68ab640` | Yes |
| `README.md` | `e9bf01cfe4ef0c5715b020cb5194ac070a0c9c20edd24acde40627244d2748ba` | Yes |
| `RiftAddon.toc` | `0c3b8f05a0226bffdf4a127ae2212ae49aa893ef1552e3447144ab936ab9fe53` | Yes |

Physical RIFT process `rift_x64.exe` was observed running in the earlier read-only preflight (PID 66992, volatile). The running client had already loaded its previous scripts; **v0.3 live loading, startup lookup, and persisted candidate data were not verified**. No RRE-owned reload, slash command, gameplay input or process action was performed. v0.2 Git/source provenance remains available to roll back RRECollector alone if necessary.

## Checks and remaining gate

- `node --test tools/verify-rrecollector-candidates.mjs`: **4 passed, 0 failed**. Validates 96 unique/source-matched IDs and six screenshot canaries, Lua/static JSON agreement, all TOC fields/dependency order, caps and separate SavedVariables. This is **not** a Lua runtime compilation/test.
- `node tools/validate-roadmap.mjs` and `git diff --check`: final integration gate to be recorded before commit.
- **RC-07 source+installation accepted. RC-08 live receipt blocked:** on the next **operator-controlled normal UI load**, allow the addon to attempt one read-only lookup; after normal SavedVariables flush, read `RRECollectorData.candidateLookup`, reconcile character/role/build and all statuses, confirm `latest` remains 69 records and `probe` remains independent. If the startup attempt deferred, the operator may invoke `/rre candidates`. A negative canary does not justify expanding API brute-force or pretending eligibility resolved.

**SC1 rank/variant and SC3 current selected queue-mode/ability readiness remain open.** A source-only crosswalk, even with a verified installation, is not a live ID resolver or proof of native cast submission.
