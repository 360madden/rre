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

## November 3, 2026 — exact-key LuaPad API probe staged, not run

A new bounded read-only API route is justified **for an operator-run experiment only**, not an enum mapping. Historical client-generated [RIFT setting API documentation](https://www.seebs.net/rift/pts/Setting_index.html) specifies `Inspect.Setting.Detail(setting: string)` returning a table with `id` and `value`; it is an old PTS reference, **not a current-client call result**. Independently, an installed RIFT API docs copy describes the same function (`inspect_setting_detail.md` SHA `1c5c3dbb79b0f38190afb9e1441464d1adcbbf7320ee1907c4c3944e48af23d3`). The [RC-02 runtime receipt](RRECOLLECTOR-RC02-FIRST-PROBE-2026-11-02.md) (report SHA `63d2c5669e46538362d8d17bd3d7811b9b353a4c4c0170c5ff0d4fc53970b124`) proves the function exists in the November 2 physical client, but **did not invoke it**.

- **Source:** `tools/sc306_luapad_queue_setting_probe.lua` performs only one guarded `pcall(Inspect.Setting.Detail, "ActionBars_AbilityQueue")`. It never calls `Inspect.Setting.List()`, writes settings, registers events or polls. It reports bounded statuses and permits a scalar value only if `item.id` exactly matches the requested key; arbitrary strings and errors are redacted.
- **Offline test:** `tools/test_sc306_luapad_queue_setting_probe.lua` mocks missing/error/mismatched/non-table/numeric/string/boolean/redaction/unsupported responses and ensures `Inspect.Setting.List()` is never called. **89/89 focused checks passed** in hash-pinned Windows Lua 5.3 (job `rre-sc306-one-key-privacy-offline-20261103-a1`, exit 0). Reviewed final source SHA `fb6eb4100b8e47343fb7dee795f8cc95fd18daaef7b841f61ed02742537d57b3`; fixture SHA `b97efd2d5428cb0046f9bf9d360063bb01e8d6373ad54f96e00db56267d310b4`. The independent reviewer found and the manager fixed unrestricted scalar printing and table metamethod lookup; this is still synthetic-only.
- **Manual gate:** Operator opens physical RIFT Settings → Interface → Action Bars → Ability Queue, notes selected Full/Short/None, opens already-loaded LuaPad (`/lp`), runs this one-shot RRE script, and captures Output plus the same-session UI. The operator need not change any setting. Treat nil/error/key-mismatch as **inconclusive**, not as evidence that no native setting exists. Even an exact API numeric result must be correlated to the native `+0xA4` field and displayed UI mode before resolving SC-306.

**Status:** Source staged and synthetic-only. Not executed in RIFT, not installed as an addon, and no game input/settings change authorized by this note.

## November 4, 2026 — exact-output and out-of-domain privacy regression

An independent read-only QA review found that the staged fixture originally matched a status **substring**, so an unintended second output line or a missing mandatory follow-up could pass. This pass changed **only** the offline fixture; the operator-pasted probe remains byte-identical and unexecuted in RIFT.

- **Source:** `tools/sc306_luapad_queue_setting_probe.lua` SHA-256 `fb6eb4100b8e47343fb7dee795f8cc95fd18daaef7b841f61ed02742537d57b3` (unchanged).
- **Fixture:** `tools/test_sc306_luapad_queue_setting_probe.lua` SHA-256 `5a99460eb90df9d2676d928dc07061870a4316c030d85a89eaa890dbc1f0be95`. Its mocked `print` rejects multiargument calls; the test now requires exact complete output, including `UI_LABEL_AND_NATIVE_CORRELATION_REQUIRED` only for non-early-return `EXACT_KEY_*` statuses. `NONFINITE_NUMBER` exits early and correctly has no trailer. Added `3` and `-1` numeric values, both required to be redacted rather than assumed valid enum values.
- **Green:** Source-exact, hash-pinned Windows Lua 5.3 fixture returned **99/99 checks**, exit 0, job `rre-sc306-exact-output-wrapper-20261104-a3`. The first direct Lua invocation (job `rre-sc306-exact-output-lua53-20261104-a1`) failed at DLL search before executing the fixture; the isolated Python wrapper placed only the existing SHA-verified Lua 5.3 DLL directory on its child PATH. A first strict-output draft then correctly exposed an erroneous test expectation about the `NONFINITE_NUMBER` early return (job `rre-sc306-exact-output-wrapper-20261104-a1`, exit 2); the fixture—not the probe—was corrected and rerun.
- **Negative controls:** Three **in-memory only** source substitutions independently triggered intentional assertion failures: (1) injecting an extra emitted line and (2) allowing `3` in the numeric allowlist, and (3) emitting `print(status, synthetic_secret)` with two arguments. Jobs `rre-sc306-exact-output-red-mutants-20261104-a1` and `rre-sc306-multiarg-red-mutant-20261104-a1` returned exit 0 after detecting all three expected-red outcomes, with no mutant files written.

**Gate remains blocked:** This confirms that the fixture detects output drift and protects against unknown numeric values; it does **not** map `0/1/2` to Full/Short/None, prove that `3` is a real mode, establish same-epoch native `+0xA4`, or authorize in-game input or setting changes.
