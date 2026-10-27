# SC-404 — RIFT October 27 native spellcasting build qualification

**Result:** Native-data anchor recovery on the **new physical-host RIFT x64 PE**. This does **not** identify an implemented function, prove live guest compatibility, or complete SC4. REA only; no game input, process attach or full-PE Ghidra import.

## Source and old-build separation

- New host executable: `C:\Program Files (x86)\Glyph\Games\RIFT\Live\rift_x64.exe`, **60,493,640 bytes**, SHA-256 `1935a05c9db6d468e34e0055014a4a99c1b5afceb1695884e24600f5c20a4be8`.
- Previous build: **59,963,840 bytes**, SHA-256 `7c356c9dde9e12fcbff3c08d953b0630b48b1510a0ffb36e4ec164606e7b17bd`. Prior native findings and RR2 trials remain attached to this **old** build and are not silently updated.
- New x64 PE preferred base `0x140000000`. Section RVAs and hashes: [exact seven-section inventory](REA-RIFT-BUILD-INVENTORY-2026-10-27.json). Observed `.rdata` begins RVA `0x25ef000` and original file offset 39,773,184; `.data` begins RVA `0x2f56000` and original file offset 49,628,672.
- Original old PE bytes were **not** available for a full old/new instruction comparison; no assertion of RVA equivalence is made.
- Only RIFT-Lab-2 was reported running by VMware, but its **guest** binary hash is unverified. Lab-1 and saved October 26 process IDs are historical.

## Four verified native literal anchors

| Exact string in new `.rdata` | Source byte offset | New-build RVA | Full-width absolute pointer location, if observed |
| --- | ---: | --- | --- |
| `Inspect.Ability.New.List` | 40,720,920 | **`0x26d6618`** | `.data` file offset **49,681,248**, RVA **`0x2f62d60`** |
| `Inspect.Ability.New.Detail` | 40,720,976 | **`0x26d6650`** | `.data` offset **49,681,272**, RVA **`0x2f62d78`** |
| `Inspect.Unit.Castbar` | 40,730,976 | **`0x26d8d60`** | `.data` offset **49,688,560**, RVA **`0x2f649f0`** |
| `ActionBars_AbilityQueue` | 40,812,656 | **`0x26ecc70`** | No exact full-width absolute string-pointer hit in the original PE |

Nearby metadata supports these as practical **native API-description / settings candidates**:

- Adjacent to `Inspect.Ability.New.List` and `Inspect.Ability.New.Detail` are `abilities`, `ability@detail`, `abilities@detail`, `detail@ability`, `details@ability` and the field names `costPower`, `costMana`, `costEnergy`, `costCharge`, `costSpirit`, `costPlanarCharge`, `focusMin`, `focusMax` and `weapon`.
- Next to `Inspect.Unit.Castbar` are `uninterruptible`, `detail@castbar` and `details@castbar`.
- `ActionBars_AbilityQueue` appears among `ActionBars_BottomActionbars`, `ActionBars_SideActionbars` and other UI setting names. This is **a settings-string clue only**, not a recovered queue buffer or GCD scheduler.

The found `.data` words are pointers **to strings**, not demonstrated function pointers. We have not identified source-level handler semantics or code xrefs. Exact preferred-base eight-byte pointer matching can miss RIP-relative code references and runtime indirections. Absence of an exact literal or pointer is not proof no implementation exists.

## REA interpretation and next experiment

**Established:** on today's *new host binary* the client contains literal ability enumeration and castbar API names and nearby typed metadata. Their original file byte offsets and new-build RVAs are reproducible, without transplanting old offsets.

**Unknown:** the actual client handler functions, data structures backing known abilities, active-role eligibility, cast queue/GCD clock, server request/acceptance rules, and whether the running VM guest has this binary.

**Next SC-401 falsifiable task:** determine whether `.data` RVA `0x2f62d60` (descriptor for `Inspect.Ability.New.List`) has a **source-backed registration/code reference** that can be followed to one bounded native enumeration function. Check original executable instruction bytes, xrefs and calling context before assigning any function role. Reuse REA/Ghidra retained state or a small scoped source-range analysis where supported; previous 450-second whole-PE imports are not a default. If two distinct probes fail to establish a decision, park the lead with exact evidence.

**SC-404 exit:** old/new SHA applicability recorded, new original PE source/section mapping verified, one source-backed ability/queue/castbar metadata anchor family identified with explicit limits. This is a *build inventory task*, **not SC4 phase completion**. SC1 learnability and SC3 independently measured GCD remain open.

## Read-only audit receipts

Verified Workbridge request IDs, each exit 0 and source-SHA guarded: `rea-oct27-sc404-native-string-probe-01`, `rea-oct27-sc404-api-anchors-02`, `rea-oct27-sc404-registration-context-03`, `rea-oct27-sc404-castbar-queue-pointer-04`. Portable original-byte address/response summary: [machine-readable anchor record](REA-RIFT-SPELLCASTING-SC404-NATIVE-ANCHORS-2026-10-27.json).

No source/games files modified, no REA package version changed, no VM control and no RR2/Workbridge repository edits. Future live character/guest compatibility is RR2-owned and separately verified.
