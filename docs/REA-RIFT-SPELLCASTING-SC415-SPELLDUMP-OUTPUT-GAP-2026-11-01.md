# SC-415 — SpellDump October 29 saved-output lead: bounded source and archive audit

**November 1, 2026 EDT. Status: BLOCKED after two source groups.** Research was read-only on existing physical-PC RIFT screenshots, accessible disabled addon code, and saved RRE/RiftReader2 artifacts. No live game input, addon activation, SavedVariables modifications, process attachment or file cleanup.

## The precise lead

[SC-414](REA-RIFT-SPELLCASTING-SC414-SCREENSHOT-AUDIT-2026-11-01.md) visually reviewed original `2026-10-29_020726.jpg` (SHA-256 `e6f296be4f74765324023335f14ed1130d216dca547b13235b5ce1580d7052aa`). Its chat shows a SpellDump initialization message while a RiftReader2 Casting window is visible. **Initialization does not establish that `/spells` was executed, that an ability dump was copied, or that a saved file contains a known-ability list.**

## Source group 1 — Currently disabled addon implementations

| Original source | SHA-256 | Source-backed behavior |
| --- | --- | --- |
| `SpellDump.disabled/README.md` | `113945bccff6c11dfb792b1ca66a7970f146d2bed9a39b2f107f85a8f291f885` | Describes `/spells` refresh/window, Copy All, and SavedVariables for settings and diagnostic history |
| `SpellDump.disabled/SpellDump.lua` | `87388b61f638a49113fae6d31828bf3d566ddbf03be65d043c12f608f094dcbc` | `collectAbilities` at lines 793–825 calls `Inspect.Ability.New.List/Detail`; lines 828–862 generate `currentDumpText` and UI; lines 669–709 copy selection/all to clipboard |
| `SpellDump.disabled/RiftAddon.toc` | `a341c9d8ff3486ba0ca40ddc12fb76f6a85dfd3ddff27568a9ee55755daf4f84` | Declares **only** `SpellDump_Settings` and `SpellDump_Log` as character SavedVariables, not an ability-list store |
| `spelldump2.disabled/SpellDump2.lua` | `f1e6460a28eced2687ad3f109f2b0f73ee9a3b4b607faf4fb5c8a723eed92c04` | Lines 245–281 also call List/Detail but filter abilities by offensive shape and output a UI/export string. This filtered set is **not** a complete spellbook |
| `spelldump2.disabled/RiftAddon.toc` | `ac2ca2f6654be512c98c0977ebee7b689c05732bf93c04e0582a0a8b4c8b29d2` | Declares startup file, with **no** SavedVariables export contract |

**Direct conclusion:** These source versions support a known-ability *on-screen/copyable display* when explicitly requested, but do not establish that the complete ability list was automatically persisted on October 29. The code's SavedVariables are settings and log; a retained log entry would not itself contain the full ability catalog.

The directories are currently named `SpellDump.disabled` and `spelldump2.disabled`. Their present names do not establish whether/when they were enabled in October; no rename or addon edit was made.

## Source group 2 — Accessible RRE/RR2 reports and archives

- Exact text `SpellDump 2026-10-29`: **0 matches in 600 checked RiftReader2 non-ignored files**, and **0 in 223 checked RRE files** (complete bounded reports).
- Repeat in `rre/artifacts` with ignored/generated sources enabled: **0 matches among 544 files**, complete.
- An ignored/generated `riftreader2/artifacts` exact-stamp scan returned **0 matches but hit its time budget**. **Incomplete scan; cannot infer absence from the entire archive.**
- A bounded filename search in `riftreader2/artifacts` found `casting-20261025-01/spelldump-review-*` and associated source snapshots, i.e., prior **October 25 source review**, not an October 29 physical-host ability export. That filename inventory also hit the scan budget and is not exhaustive.
- Generic `SpellDump` text matches in normal RR2 files refer to the known API-reuse documentation, not a source-qualified October 29 current-role export.

**Verdict:** No source-qualified October 29 saved ability dump was produced by the two bounded source groups. This is an evidence/access gap, **not proof that the player never copied a dump**, nor a claim about all private SavedVariables/clipboard history or unseen archives.

## Next evidence and parking rule

To unblock SC-102/103, the existing live-capture owner should supply one **matching current physical-PC** snapshot: executable SHA, character/calling/level/role/soul allocation, complete `Inspect.Ability.New.List/Detail` IDs/metadata, and actual spellbook/soul/trainer UI at a bound time. Keep acquired vs eligible vs locked, usable and action-bar-bound separate. The old 55-ID list is historical and cannot substitute for this.

**Park SC-415.** Do not re-search the same failed source folders or start broad archive scans without a new source clue. The full spellbook and queue/GCD phases remain unresolved; no live game action was performed.
