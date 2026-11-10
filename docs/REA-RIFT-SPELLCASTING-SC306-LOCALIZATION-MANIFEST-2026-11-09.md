# SC-306 — LEGION physical localization-manifest and pointer-table triage

**November 9, 2026, ~22:18 EST.** Source-first, bounded, read-only independent research on **LEGION's physical RIFT installation**. No VMware, in-game input/UI capture, process memory, debugger, installed addon write, asset extraction, full PE Ghidra import, or download was performed.

## Exact source identities and admitted manifest

| Fact | Verified |
| --- | --- |
| Active Windows host | `LEGION` (fresh `hostname.exe`) |
| Original on-disk physical game executable | `C:\Program Files (x86)\Glyph\Games\RIFT\Live\rift_x64.exe` |
| Executable SHA-256 | `1935a05c9db6d468e34e0055014a4a99c1b5afceb1695884e24600f5c20a4be8` |
| Physical asset manifest | `C:\Program Files (x86)\Glyph\Games\RIFT\Live\assets64.manifest` |
| Manifest size / SHA-256 | `24,158,080` / `6e3c79b453ce5a4caa2eb5eeddb0240c7dcad9d5d54f6ce2a0f3d532b468715c` |
| Header | `TWAM`, version 3.0, little endian |
| Table 0 | 2,078 PAK references, stride 53 |
| Table 1 | 404,348 asset entries, stride 58; exact table coverage / bounds verified |
| Table 2 | 3 references, stride 12 |

The manifest's Table 1 language discriminator was read at entry byte **+31**. Bounded counts sum exactly to **404,348**: universal **338,789**; English **17,668**; German **24,405**; French **23,308**; Russian **178**. English entries refer to **52 distinct manifest-listed virtual PAK names**, including `assets/localization/english/english_17.pak`. Those named PAKs are **not loose files** under `Live`. The installed physical `Live\Assets` folder has 239 numbered `assets.*` segments without subdirectories. There was no archive extraction.

The manifest is an index with hashed filename identifiers. The physical manifest itself had no plaintext ASCII/UTF-16 `Ability Queue`, no `ActionBars_AbilityQueue`, and no literal ASCII `Full` / `Short` / `None`. This is a negative **manifest-text** search only; localization asset payloads were not read, so the absence of those strings from the manifest cannot establish their absence from RIFT resources.

Source for format interpretation: [The Ghar Station RIFT assets-manifest documentation](https://thegharstation.com/gharwiki/index.php/Assets_manifest). Its Table 1 description specifies filename FNV-1 hashes and language metadata. The manifest observations above were independently checked against **this exact physical install**, rather than assumed from the article.

**Read-only Workbridge jobs, all exit 0:** `rre-manifest-lead-verify-host-20261109-01`, `rre-manifest-lead-physical-header-20261109-01`, `rre-manifest-lead-table-validate-20261109-01`, `rre-manifest-lead-english-pak-ranking-20261109-01`, plus targeted English-PAK existence / physical-assets-layout inventory jobs.

## Independent exact-PE pointer-table check — two negative paths

A separate bounded reviewer again verified host `LEGION` and source PE SHA. Within **`.rdata`, `.data`, and `.rsrc`** it searched for both (a) literal 64-bit absolute addresses and (b) 32-bit RVA encodings for all three known source strings:

| String | Exact-build RVA |
| --- | --- |
| UTF-16 `Ability Queue` display label | `0x26B4178` |
| ASCII `ActionBars_AbilityQueue` setting key | `0x26ECC70` |
| UTF-16 `{0}` formatting literal | `0x26A3130` |

Both encodings returned **zero hits** in those sections. Jobs `rre-sc306-choice-pointertable-ro-20261109-01` and `rre-sc306-choice-rva32table-ro-20261109-01` exited 0. This rules out a simple literal-pointer/RVA representation in the inspected sections, **not** a dynamically created control, RIP-relative references, compressed localization, hashed keys, or other table representations. Park this direct-pointer method after two non-discriminating probes; do not broadly repeat it.

## Decision / next focused route

**SC-306 remains blocked.** The only historical game/UI association is `1 → Short` from the earlier recorded Lab-2 epoch; it is not a fresh LEGION runtime qualification. **Values 0 and 2 are unmapped.**

The highest-value next step is a **bounded, read-only examination of existing RiftAssetDumper/WAD reader code** to see whether its indexes can resolve a *single* manifest-listed English resource through the physical `Live\Assets\assets.*` segments. Do not extract the full archive or invent a filename→hash mapping. A shallow `C:\work` directory scan found no clearly named top-level `RiftAssetDumper` checkout; do not assume the tool is installed on LEGION.

If no existing, verified reader can map this resource safely, park the archive lead instead of adding speculative infrastructure. A separately approved same-epoch **physical** RIFT UI/native comparison remains the other acceptance route. This report only records native/resource research; it does not authorize new game interaction, archive modification, or full-PE analysis.
