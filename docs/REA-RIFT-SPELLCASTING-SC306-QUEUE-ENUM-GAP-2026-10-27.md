# SC-306 — Local AbilityQueue value-to-label mapping: bounded negative result

**2026-10-27. REA research on physical PC only.** This task investigated whether the local game's native setting value **`1`** can be reliably mapped to user-visible **Full / Short / None** without modifying gameplay or stealing focus. **Outcome: unresolved / blocked on direct user-interface mapping evidence.** This is a saved negative result, not a claim that the value has no mapping.

## Source-backed facts retained

- New local RIFT executable SHA-256 **`1935a05c9db6d468e34e0055014a4a99c1b5afceb1695884e24600f5c20a4be8`**.
- [SC305 dossier](REA-RIFT-SPELLCASTING-SC305-QUEUE-DOSSIER-2026-10-27.md) qualifies `ActionBars_AbilityQueue` key, settings global RVA `0x33958c0`, **32-bit `+0xA4`** value field, and raw observed local value **`1`** under standard read-only process access. Labels remain unverified.
- A bounded search of likely local RIFT `.cfg` / `.ini` paths found **zero matching entries for the literal `ActionBars_AbilityQueue`**. This does not mean no configuration exists or that an unknown alternate file format is absent.
- `.text` source analysis of the **settings-global RVA `0x33958c0`** yielded **329 raw displacement candidates**, 329 RIP-relative instruction *candidates* confirmed locally using bounded Capstone decodes, across **27 `.pdata` function ranges**, clustered at roughly `0xBCE7C0–0xBDC915`. These predominantly appear to be UI/settings plumbing. Matching the setting-object global pointer is **not equivalent to a demonstrated read of field `+0xA4` in cast dispatch**.
- User32 enumerated exactly one visible RIFT top-level window for local PID 66436, but **the RIFT window was not foreground**. No screenshot of a displayed queue setting was available, so REA did not bring the game foreground or send input while the user could be using the desktop.
- `Full`, `Short`, and `None` are three **potential UI labels** in RIFT's queue setting, but **no numeric mapping was qualified** by the preceding sources. Do not promote the plausible `0/1/2` ordering to a fact.

## Decision and stopping rule

**SC306 is blocked until new independent evidence:** a source-hash-tied local game **Settings → Ability Queue** screenshot showing the selected mode *at a time when the numeric field is also read*; alternatively original client resources or code proving the enum-label association.

That evidence could be collected later through an explicitly reviewed operator-safe local UI session. A raw field sample without a simultaneously established UI mode remains unknown. Do not guess, auto-toggle UI settings, or treat the settings parser as a confirmed cast queue handler.

**Next separate REA work: SC-402 native castbar/readiness function data-flow**, starting from the already pinned `Inspect.Unit.Castbar` descriptor family. This is independent of the mapping gap. Its result still cannot establish the actual GCD or server acknowledgement without appropriate observations.

**Workbridge jobs:** `rea-localpc-queue-config-scan-20261027-01` (no matches), `rea-localpc-game-foreground-windows-20261027-01` (background game), `rea-localpc-queue-global-xrefs-20261027-01` (329 candidate references / 27 function ranges). All were read-only, exit 0, source-hash or local-process bound; no game input or memory write.

## November 3, 2026 follow-up — primary UI semantics confirmed, enum still unknown

Three separate read-only ChatGPT research lanes checked official documentation, RRE-local evidence and other-project text indexes. **SC-306 remains blocked: the integer-to-label mapping is not proved.** The research adds an official source for the *meaning of each UI choice*, not a serialization/field mapping:

| User-visible setting | Officially described behavior |
| --- | --- |
| `Full` | Allow one ability to be queued. |
| `Short` | Queue only in a short interval near the end of the current cast or cooldown. |
| `None` | Disable ability queuing. |

Primary documentation, retrieved November 3 (US Eastern): [Gamigo — RIFT: Customizing the User Interface](https://gamigo.freshdesk.com/en/support/solutions/articles/201000105477-rift-customizing-the-user-interface), **Action Bars → Ability Queue**. The public help article does **not** assign `0`, `1` or `2` to those labels, and does not certify the behavior of the exact hashed physical build. Do not substitute UI drop-down order for code evidence.

Local source review reconfirmed the October 27 physical executable SHA `1935a05c9db6d468e34e0055014a4a99c1b5afceb1695884e24600f5c20a4be8` and the exact `ActionBars_AbilityQueue` setting at object offset `+0xA4`; the historical raw sample **`1` has unknown UI meaning**. See the source-hashed [SC-305 dossier](REA-RIFT-SPELLCASTING-SC305-QUEUE-DOSSIER-2026-10-27.md) (SHA `f88ec863158597518ec40b0dc06e34595b8018c86356e1d3ffa75828ef436e5c`) and this report's original preflight. A bounded text search across `riftreader2` (608 files), `REA-Lab1` (185) and `Rift API` (192) found **no literal `AbilityQueue` reference**. These negative matches do not rule out an encoded implementation or unindexed source.

**Acceptance gate unchanged:** independently capture the currently selected RIFT Settings → Ability Queue label **and** read the exact-build `+0xA4` field in the same settings epoch; preferably repeat with a second user-selected label, capturing exact timestamps, build hash, screen evidence and read-only receipt. Alternatively qualify original matching-build label/enum code. No RRE-controlled input, settings change, process control or external repository write was performed in this follow-up.
