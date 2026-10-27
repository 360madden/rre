# SC-501 — RIFT casting restrictions and diagnostic error classification

**October 27, 2026. Task accepted at observed-evidence scope; SC5 phase remains open.** REA worked offline using the physical-PC RIFT executable and previously saved RR2 evidence. No game input, process attachment, memory write, VMware control, new dependency, or changes to RR2/Workbridge occurred.

## Main native correction: `ABILITY` is UTF-16, not an ability-ID prefix

On the **new physical-PC executable** SHA-256 `1935a05c9db6d468e34e0055014a4a99c1b5afceb1695884e24600f5c20a4be8`, the already-verified `/cast` command source slice `0x6c7450–0x6c7b71` has SHA-256 `31c02f4e68ac0c8157ad4e8fd1f813fe724b02f607d9c67649bcd777d0890d85`.

A source-byte check of `.rdata` RVA **`0x26b6030`** confirms the null-terminated **UTF-16LE** bytes `41 00 42 00 49 00 4c 00 49 00 54 00 59 00 00 00`, spelling **`ABILITY`**. A naive ASCII-NUL string scan incorrectly renders only **`A`**. The cast code at RVA **`0x6c7750`** loads this literal before string-related calls. Later at RVAs **`0x6c78b2`**, **`0x6c78dd`**, and **`0x6c7922`**, the code references the distinct ASCII diagnostic template:

> `Could not cast unknown ability: [%ABILITY]`

The proximity and code references are **consistent with diagnostic placeholder/substitution preparation**, not proof of an `A`-prefix native ability-ID lookup. The analogous `use` diagnostic contains `Could not use unknown item: [%ITEM]`, supporting a templated error-message interpretation. No network request or cast permission check is proven by these strings alone.

A bounded source decode of helper **`0x4cb3d0–0x4cb48e`** (190 bytes, 47 decoded instructions, original-byte SHA-256 `768115115ca1cffbc39c5ea3dcc5addf3c5d89439177162a18a861e9f7a83ea0`) found a subordinate call to RVA `0x499cc0`, temporary string/container manipulation, and a return based on an object field. Its semantics remain **unqualified**. Given the verified full `ABILITY` placeholder, don't label this helper an ability resolver or pursue a generic recursive call search without new discriminating evidence.

## Four different failure/outcome classes — do not conflate them

| Class | Verified source and result | What remains unknown |
| --- | --- | --- |
| **Native unknown-ability diagnostic** | Source-backed error-text branch in the **new host executable** `/cast` command | Whether/when this exact message appears live, how abilities are resolved, or which server response is involved |
| **API-reported inability to use** | Historical **old-build** RR2 API inventory: 55 returned IDs, **10 explicitly had `unusable=true`**, 45 omitted the flag. `Discharge` ID `A23A6E91642EDEA34` is an example | Exact reason (proc, combo, target, role or another condition); absent flag is unknown, not necessarily usable |
| **Pre-activation out-of-range diagnostic** | Historical **old-build** RR2 supervised record: `Aggressive Block` was initially out of 3m range, later became API-ready after movement | Whether a native `/cast` packet was sent/rejected while out of range; the reader's diagnostic is not authoritative native enforcement |
| **Target avoidance after ability activity** | Historical **old-build** RR2 combat event: `Light's Decree` exact modern ID `A6B8B16CD6F8B3DB9` returned a **dodge** to the selected dummy in Trial 1, while Trial 2 caused **402 Life damage** on the same exact target | Shared GCD, castbar onset, cast/request transit, hitbox geometry and current-build parity |

**Evidence ownership/source pins:**

- Historical ability inventory `riftreader2/artifacts/casting-20261025-01/ranged-evidence-04/evidence.json` SHA-256 `9e81dccdf53640c5ae8f874b6bad16d38f75faeee06be7999032e9695d934630`.
- Historical supervised limitations `riftreader2/docs/workflows/casting-handoff-2026-10-26.md` SHA-256 `b1f7125715cc29584c43d99321b900ff6365fbbd2d5c3da66468a3725c9340b5` (notably Discharge full Power/zero cooldown but unusable; Aggressive Block initially out of range).
- Historical exact-target result `riftreader2/artifacts/exports/casting-ranged-20261026-01/report.json` SHA-256 `bca100aeb70f9bb6f95afd927971103909c45826f68fa1223e5f57f6d888372e`.
- New source-memory-free native strings, source code RVAs, helper SHA and independent classifications retained in [the machine evidence](REA-RIFT-SPELLCASTING-SC501-OFFLINE-2026-10-27.json).

## REA decision and handoff

**SC-501 acceptance at bounded observational/source scope:** at least one real negative API observation (`unusable=true`) plus historical out-of-range evidence is source-qualified; separate native static error text is verified; avoidance must not be misclassified as pre-activation failure; missing combat events never prove no cast when capture coverage is incomplete. No private credentials or control actions were exported.

**This is not complete native cast-rejection reverse engineering.** Current physical-PC client game/role ability observations, all native guard branches, server validation and update parity remain unverified. The corrected UTF-16 finding **eliminates the `A`-prefix hypothesis**, which should not be reopened without new bytes or dataflow.

**Next independent offline task:** SC-502 exact-ID multi-target outcome attribution using the two saved prior-build trials, keeping healing/overhealing and current-build outcomes unknown where no evidence exists. SC-503 channel, proc and interrupt cases still need new appropriate records. SC5 major phase remains **not completed**.

Tool jobs: `rea-offline-sc501-cast-controlflow-20261027-01`, `rea-offline-sc501-argument-path-20261027-01`, `rea-offline-sc501-cast-lookup-helper-20261027-01`, `rea-offline-sc501-local-literal-encoding-20261027-01`, `rea-offline-sc501-cast-use-template-parity-20261027-01`, all passed. No whole-image PE import.
