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

## Read-only upstream RiftAssetDumper source check (~22:24 EST)

The existing public [360madden/RiftAssetDumper](https://github.com/360madden/RiftAssetDumper) Git HEAD was verified via read-only `git ls-remote` at **`7e1d5a8699545b16bb4649d90f7d082cd55e1881`** (job `rre-legion-riftassetdumper-remote-existence-20261109-01`, exit 0). Its GitHub tree and bounded raw source lines were fetched **in memory only**, with no clone/install or changes to that repository.

- [`scripts/build_live_archive_index.py`](https://github.com/360madden/RiftAssetDumper/blob/7e1d5a8699545b16bb4649d90f7d082cd55e1881/scripts/build_live_archive_index.py) indexes installed `assets.*` **TWAD** segments by 16-hex asset-ID prefix, but the current workflow matches an existing **NIF geometry cohort**. It does not resolve an arbitrary English localization name to its content.
- [`scripts/extract_live_nifs.py`](https://github.com/360madden/RiftAssetDumper/blob/7e1d5a8699545b16bb4649d90f7d082cd55e1881/scripts/extract_live_nifs.py) contains a reusable 44-byte TWAD entry decoder with 8-byte content ID, offset, size and compression metadata. **Important source discrepancy:** its `read_archive()` calls `f.read()` on the **entire archive**, even though the index-builder module's comment describes a header/table-only scan. Do not invoke that full-archive path as a supposedly metadata-only probe.
- The existing reader is therefore a **source reference**, not yet a qualified safe extraction path for the 17,668 English entries. Any follow-up should use strictly bounded header/table reads and require a specifically identified manifest asset ID before examining payload bytes. No asset was decompressed or copied in this checkpoint.

Read-only jobs: `rre-legion-riftassetdumper-remote-tree-readonly-20261109-01`, `rre-legion-riftassetdumper-source-paths-readonly-20261109-01`, `rre-legion-riftassetdumper-index-script-readonly-20261109-01`, `rre-legion-riftassetdumper-twad-reader-readonly-20261109-01`; all exited 0. **SC-306 decision unchanged**.

## Reproducible source-backed filename-to-record lookup (~22:39 EST)

- The public [World Data Files documentation](https://thegharstation.com/gharwiki/index.php/World_data_files) provides the literal filename `world_map.cdr`. On the exact SHA-gated physical `assets64.manifest`, normalized ASCII FNV-1 `0x98AEBEEF` and byte length **13** yield exactly one Table 1 candidate: index **241405**, language **0**, content-ID prefix **`7e1a8b5b695906bc`**, PAK index **616**, virtual name **`assets/map/map_core_0.pak`**. Table 0's PAK name pointer is an **absolute** manifest offset **131788**, independently checked against the physical bytes. The candidate is metadata only: no PAK content was opened.
- New standalone standard-library `tools/lookup-twam-name.py` performs only a caller-selected filename lookup against a caller-supplied file and exact SHA-256; optional `--expected-host LEGION` rejects another host before reading the manifest. It validates the TWAM v3 table bounds/strides, resolves only matched PAK strings, and returns JSON. Exit **0** = one hash/length candidate; **3** = absent or ambiguous; **2** = CLI preflight error (wrong host/SHA). **A unique 32-bit FNV-1 + filename-length candidate is not proof of plaintext filename identity; collisions are possible.** Only ASCII input is admitted because Unicode normalization is unverified. The tool does not read payloads, interact with the game, or write files.
- Reproduction from `C:\work\rre`: `python -B tools/lookup-twam-name.py --manifest "C:\Program Files (x86)\Glyph\Games\RIFT\Live\assets64.manifest" --sha256 6e3c79b453ce5a4caa2eb5eeddb0240c7dcad9d5d54f6ce2a0f3d532b468715c --filename world_map.cdr --expected-host LEGION`. The 9 offline synthetic checks include duplicate hash/length rejection, malformed tables, invalid PAK pointer and non-ASCII rejection; actual physical positive, absent-file negative, wrong-host and wrong-SHA checks were also exercised. The independent read-only agent confirmed offsets and the 4 real CLI behaviors before the stronger proof-ceiling/ASCII revision.
- Additional physical `assets64_debug.manifest` and `assets64_dev.manifest` are byte-identical, SHA-256 **`361b3fd275bfeccfdddc13885a8110963fef86aca53e19ddacc3ec5f93618715`**, each 25,583,492 bytes. Relative to normal, 23,464 additional universal entries but **zero additional English entries**. No `Ability Queue` literal or independently evidenced localization asset filename was found. Park this debug/dev avenue.
- Public `RiftAssetDumper` `Program.cs` includes `hash-name` and `match-names`, with a `--require-unique` collision safeguard. Its README and sample candidate names do not qualify an Ability Queue filename; its extraction-capable code was not executed. **SC-306 still blocked for 0/2**; the manifest mechanism is ready only when a source-backed candidate filename exists.

## English language asset → physical TWAD archive (22:51 EST)

- The Ghar Station's [RIFT `Lang_cds` format](https://thegharstation.com/gharwiki/index.php/Lang_cds) explicitly names **`lang_english.cds`** as a localization key/text file. [telarafly's `EnglishLang.cs`](https://github.com/imathrowback/telarafly/blob/master/Assets/RiftAssets/EnglishLang.cs) independently uses `extractUsingFilename("lang_" + lang + ".cds")` and describes Huffman-compressed text records. This grounds an actual localization filename, **not evidence that Ability Queue's particular labels are in it**.
- On physical LEGION's exact `assets64.manifest` SHA `6e3c79b453ce5a4caa2eb5eeddb0240c7dcad9d5d54f6ce2a0f3d532b468715c`, `tools/lookup-twam-name.py --filename lang_english.cds --expected-host LEGION` exited **0**. Filename length **16**, FNV-1 **`0x70BAA82E`**, unique hash+length **candidate** at Table1 index **178030**, language **1**, content ID prefix **`bbeea48a7564ed10`**, PAK index **447**, virtual PAK **`assets/localization/english/english_core_0.pak`**. Source-hash qualification and 32-bit collision ceiling remain explicit.
- A fresh physical nonrecursive inventory established exactly **239 `assets.NNN`** files and **zero `assets64.NNN`** under `Live\\Assets`. Sampled headers were TWAD v1, 20-byte header, max entry count **1489**. Primary layout references: [The Ghar Station TWAD format](https://thegharstation.com/gharwiki/index.php/Assets_File_Format) and [360madden/RiftAssetDumper 44-byte reader](https://github.com/360madden/RiftAssetDumper/blob/7e1d5a8699545b16bb4649d90f7d082cd55e1881/scripts/extract_live_nifs.py). The existing RiftAssetDumper indexing route loads entire archives with `f.read()` and was **not** invoked.
- New `tools/lookup-twad-id.py` checks only bounded TWAD 20-byte headers and 44-byte metadata tables for a supplied 8-byte content-ID prefix, with host gate and strict filename/count/offset/file bounds. It traversed **355,871 metadata slots across 239 segments** (no payload access) and found **exactly one** candidate in **`assets.002`**, entry **1211**, stored content at offset **79,474,811** for **4,794,377 bytes**, compression flag **1** (documented ZLIB); record's 20-byte SHA field `99c6c384b281d28c2f94351c04b163f71db869b6`. Matched file metadata header+table SHA-256 **`6817892160d3b884819ac9fe914628bc0b6d11ad7c1cbe1b0107e546f5f96f22`**. The 8-byte prefix is not a full payload hash; the 20-byte SHA field is recorded, not independently verified. This scan checks **all metadata slots**, without following the archive's linked-entry list, so **active membership is unverified**. The SHA-256 covers only the inspected header plus table, not any intervening bytes or payload. Tool plus eleven synthetic tests passed, physical locator exit 0, wrong-host exit 2 as expected. Read-only job IDs `rre-legion-sc306-twad-id-physical-proof-20261109-01`, `rre-legion-sc306-twad-id-nine-tests-20261109-01`, `rre-legion-sc306-twad-id-wronghost-20261109-01`.
- **Gate remains blocked:** No text was extracted, decompressed or inspected; this path does not yet prove `Ability Queue`, `Full`, `Short`, or `None` appear inside the localized payload, and certainly not the `0/2` enum mapping. The useful next experiment is a *separately planned, bounded single-asset content/decoder verification*, not another filename guessing pass or full-archive extraction.
