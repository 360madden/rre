# SC-414 — Bounded review of saved physical-PC RIFT UI screenshots

**November 1, 2026 EDT. Status: BLOCKED as a source-qualified spellbook/queue evidence route; bounded 12-image review complete.** Original JPGs were not changed. No game input, VM access, process attach, or new capture.

## Source and reproducible sample

Workbridge exposes the saved screenshot directory at `C:\Users\mrkoo\OneDrive\Documents\RIFT\Screenshots`. A read-only filename inventory found **18 October 2026 JPGs** and sampled the **12 newest by date parsed from filename**. Each original file was SHA-256 hashed with its size and source-file modification timestamp, captured in [the machine-readable inventory](REA-RIFT-SPELLCASTING-SC414-SCREENSHOT-AUDIT-2026-11-01.json).

Visual review used **actual saved JPG pixels**, not synthetic images: a contact sheet made **in memory** with the existing Windows `System.Drawing` capability and two higher-resolution candidate crops. No thumbnails or crops were written to disk. The in-memory contact sheet is a selection aid; it does **not** prove the contents of small or illegible interface fields.

| # | Original screenshot | Visual observation, qualified only at sampled resolution |
| ---: | --- | --- |
| 1 | `2026-10-31_094442.jpg` | RIFT scene/chat or addon overlay; no readable spellbook, soul tree, or queue-mode selector |
| 2 | `2026-10-29_020726.jpg` | High-resolution review: **RiftReader2 Casting v0.4.0**, `BLOCKED` with no target selected, plus an addon error panel. Not a complete spellbook/role/queue screen |
| 3 | `2026-10-28_195441.jpg` | Game scene/overlay; no identifiable requested UI in contact sheet |
| 4 | `2026-10-28_183147.jpg` | High-resolution review: **RiftReader2 Casting v0.3.0**, selected `Dreadfern Basher` / `Ace Shot`, `BLOCKED` target out of API range. Not a native spellbook or ability-queue settings selector |
| 5–12 | `rift_auto_2026-10-28_*.jpg` | In-game addon/dialog/debug overlays in the contact sheet; no reliably readable spellbook/soul/trainer or selected `Full/Short/None` queue setting |

**No sampled frame provides a source-qualified current local-character `Inspect.Ability.New.List/Detail` ↔ spellbook/soul/role ↔ selected queue-mode UI comparison.** This is a bounded **negative evidence result**, not proof those UIs never appear in older/other screenshots or that no output exists elsewhere.

## Exact source receipts

| Workbridge read-only job | Result |
| --- | --- |
| `rre-sc414-saved-screenshots-sheet-20261101-manager-a1` | Passed: 12-image real-pixel preview |
| `rre-sc414-ui-candidate2-crop-20261101-manager-a1` | Passed: enlarged 2026-10-29 UI review |
| `rre-sc414-ui-candidate4-crop-20261101-manager-a1` | Passed: enlarged 2026-10-28 UI review |
| `rre-sc414-saved-screenshot-hash-inventory-20261101-manager-a1` | Passed: 12 original file SHA-256/size/time receipts |

The existing RRE virtualenv and system Python lacked Pillow; a read-only attempt failed (`ModuleNotFoundError`). The built-in Windows System.Drawing decoder successfully supplied actual pixel previews without dependency installation, writable artifacts or changes to RIFT.

## Evidence boundaries and next discriminator

- The path is a **host-visible screenshot folder**, but that alone does **not** establish which RIFT process/build/character/role created each picture. The separately verified current host PE SHA `1935a05c9db6d468e34e0055014a4a99c1b5afceb1695884e24600f5c20a4be8` is **not** automatically bound to these October frames.
- RR2 Casting's visible availability verdict is not a complete learned/learnable/locked spellbook; `BLOCKED` or “out of API range” is not server refusal.
- An October 29 chat overlay appears to show **SpellDump addon initialization**. That is a lead for an **existing saved output search**, not proof an ability list was exported. The next narrow offline task should check accessible saved artifacts before requesting another live capture.
- To resolve SC-102/103 and SC-301/306, still require same-character/same-role local-host API inventory plus actual native UI evidence and selected queue-mode label, with time/build/identity binding. An existing RR2/live-capture owner handles any future supervised input separately.

**Conclusion:** SC-414's bounded saved-image audit is documented, but the requested full spellbook/queue-mode evidence is **still blocked**. Major SC1 and SC3 phases remain open. Preserve these original images and hashes; do not repeat the same 12-image sweep next Chat turn.
