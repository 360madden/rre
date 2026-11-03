# SC-103 — Installed tooltip-ID reuse preflight and source-qualified stop

**Date:** 2026-11-03. **Task:** SC-103 (rank/variant/role ID reconciliation). **Owner:** RRE physical-PC manager.
**Status:** **Read-only installed-tooling capability review accepted; modern Protector's Fury Legendary ID still unresolved.** This is a route assessment, not a live `Inspect.Tooltip()` sample or proof that any inspected addon is currently enabled.

## Narrow question

Can an **already installed** RIFT addon reliably reveal the exact modern ability ID when the operator hovers the **native Paladin Protector's Fury Soul Tree tooltip**, without changing the frozen RRECollector v0.4.10 or adding another addon?

The user-supplied native Soul Tree PNG already establishes an image-level Righteous Defender baseline (Paladin 45, Void Knight 15, Paragon 0; Legendary counters **0/3**, **0/2**, **0/1**). No Legendary variant is visibly selected. See [the original-chat-image evidence](REA-RIFT-SPELLCASTING-SC103-CHAT-NATIVE-SOULTREE-2026-11-03.md); do not mistake a Normal/Legendary *description* for a selected variant.

## Read-only addon inventory

A bounded scanner inspected **921 installed .lua files**, **8,084,354 bytes** read, **one file skipped**, and completed its configured traversal without resource cutoff. Among **46 files** matching either `Inspect.Tooltip` or slash-registration patterns, the scan found **two literal direct `Inspect.Tooltip()` caller files**. This is source-text inventory only; dynamically assembled/aliased API calls or files not readable in the pass are outside the claim.

| Installed source | SHA-256 | Observed behavior | ID-evidence ceiling |
| --- | --- | --- | --- |
| `JAB/ActionSlot.lua` | `3bdfe4209f064f9cbfa385dfecb3d1a533f907ad7d1c8f5b859ecd1054a6fbcd` | Lines 161–166 call `Command.Tooltip(self.id)` for **JAB-owned slots**; lines 185–190 call `Inspect.Tooltip()` and clear when `tooltipShown == self.id` | Source demonstrates JAB comparing the current shown identifier to its **own slot ID**, not reading a native Soul Tree selection |
| `Rustys_Action_Bars/main.lua` | `cb42eeac6436b48f96e1da9a1d903e20519350c8436b670b4b6b3f65627a958a` | Lines 710–743 display/clear the addon button's tooltip; `Inspect.Tooltip()` is compared against `self.id` (or matching buff) | Same own-button tooltip/ID comparison; **not** a generic native-tooltip ID exporter |
| `RiftReader2Casting/main.lua` | `7e24d78eeaf589bf76a7e4d59b4f6be5242d8c8d4947448995c33a60da945213` | Includes `Inspect.Tooltip` in the documentation request list | Documentation provenance, **not** a validated tooltip sampler |
| `luapad/main.lua` | `8b076bd0a32395460c22be9c6de9b64d8dfab3f3d32326c70407c1165197ea42` | Exposes `/luapad` and `/lp` in-game commands; `LuaPad.doRun` uses `xpcall(loadstring(obj), xpError)` to run editor-supplied Lua | Installed **manual scripting surface** only; not proven loaded or capable of sampling a native tooltip while the pointer remains on it |

**Manifest check:** `luapad/RiftAddon.toc` SHA-256 `2c3dc4d361b2b29fa2519617a771f0ba9ab7c24b54cd7bf2f2bb57e22b818ec0`, version **1.8**, `Environment = "1.9"` (legacy metadata). This does **not** prove it cannot load on the present client, but no current-PID load receipt exists. JAB's manifest is version **1.4.2** and Rusty's is **3.0.4**; neither was current-PID load-tested here.

## Exact current-client tooltip documentation

A separate read-only decode of the previously saved Atank `RiftReader2Casting.lua` (source size **41,750 bytes**, SHA-256 `9ddba7798ed20c8a897b4a6196cf6bc9b5c4d6ff2d19ab5bc34c3e8458eab48b`) recovered the already known `Inspect.Tooltip` text:

- **596 decoded characters**, SHA-256 **`14b6dea5b4e532bda5433028bd10218adbdb82568f1f2e9f2ae41c92f75633a1`** — exact match with the previously verified documentation hash.
- The documented forms include `type, shown = Inspect.Tooltip()` (either nil/nil or string/variant) and `type, unit, buff = Inspect.Tooltip()`.
- The documented `type` can be `ability`, `buff`, `item`, `itemtype`, or `unit`; `shown` is a variant/blob, *generally* an identifier used elsewhere in the addon system. **No documentation guarantee** says a *native Soul Tree* tooltip always returns a modern exact ability ID.

All source and documentation claims were independently rechecked by bounded job `rre-sc103-existing-tooltip-source-independent-check-20261103-a1`, **exit 0, 16 assertions**. Supplementary settled jobs: `rre-sc103-existing-tooltip-scanner-20261103-a1`, `rre-sc103-tooltip-stored-doc-qualified-20261103-a1`, `rre-sc103-new-asset-metadata-20261103-a1`, `rre-sc103-jab-rustys-tooltip-source-20261103-a1`, `rre-sc103-tooltip-addons-toc-20261103-a1`, `rre-sc103-tooltip-live-doc-decode-20261103-a1`, `rre-sc103-luapad-and-api-probe-source-20261103-a1` (each read-only, settled exit 0).

The same source metadata check found the physical **RRECollector.lua** and **RiftReader2Casting.lua** saves predate physical PID 33936 start; the physical screenshot directory still had **no new original screenshot written after that process start**. The later user-chat PNG is independently recorded; it is not a host Screenshots-folder capture and has no PID/time binding.

## Follow-up — bounded manual LuaPad source staged, not executed

A standalone, RRE-owned, **operator-triggered** LuaPad script and synthetic fixture are now staged at `tools/sc103_luapad_hover_probe.lua` and `tools/test_sc103_luapad_hover_probe.lua`. The [source-hashed test and operator procedure](REA-RIFT-SPELLCASTING-SC103-LUAPAD-HOVER-PROBE-2026-11-03.md) records **89 assertions passed in isolated Lua 5.4** (byte-identical source/test files). It accepts only an `ability`-typed `A` + 16-hex ID stable for three callbacks, then automatically detaches or times out. **Nothing was pasted into RIFT; LuaPad's current in-game load remains unverified.** This adds no addon, service or collector mutation, and does not prove an active Legendary variant.

## Decision and the smallest useful next trial

**Reuse-first decision:** Keep the existing JAB/Rusty's code as verified implementation examples of `Command.Tooltip` and `Inspect.Tooltip`. **Do not claim they provide a native Soul Tree ID capture workflow.** The installed LuaPad provides a *candidate* operator-run scripting surface, but a native hover must still be sampled without disturbing the pointer or reading/exporting arbitrary `shown` blobs. No actual live feasibility proof exists. Do not create a new addon or install another tool merely from this source scan.

1. **Immediate, non-mutating observation:** Operator hovers native **Protector's Fury** in the existing **Righteous Defender** Soul Tree and supplies a screenshot showing the *actual tooltip* beside the known **0/3 Paladin Legendary** counter. This determines whether the displayed text describes available choices versus a visibly selected state. No role change, spellcast, level change, or addon deployment is required.
2. **Only if ID sampling is still needed:** Coordinate a **separately authorized and tested** read-only `Inspect.Tooltip()` sampling method after the RC-30 v0.4.10 frozen-release gate and GUI owner status are reconciled. Limit any output to `type`, an exact-form validated **ability-shaped** ID/equality result if actually returned, or `null`. Never persist raw `shown`, third/fourth return values, unit IDs, buff values, or arbitrary tables. Verify tooltip **source identity and selected variant** separately.
3. **SC-103 stays blocked** on modern rank/Legendary variant identification; 2016 level 66–70 Legendary mechanics remain historical only. The displayed **0/n** screenshot and prior 51/51 self-equal `idNew` results cannot prove a positive Legendary selection or alternate variant ID. Do not retry unchanged native `Ability.New.List` descriptor trace.

**Safety/ownership:** RRE evidence documents only. No changes to other addons, RRECollector v0.4.10, SavedVariables, VMware labs, game process/input, Ghidra projects, Workbridge GUI lock or quarantined screenshot capture; no additional subagents spawned. Independent command jobs are not independent AI workers.
