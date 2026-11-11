# RRE → RR2 discovery handoff

**Owner:** the existing single RRE manager (not a new agent or scheduler). **Consumer:** RR2's existing AMD-DESKTOP owner. **Scope:** read-only discovery notes; no cross-repository edits or shared game-input ownership. Each project continues its own SC/RC/NAV or RR2 implementation tasks.

## One useful shared priority

**ROOT-001 — module-rooted current-player object chain.** **Open / not yet verified by this handoff.** Reuse the existing RR2 `CurrentBuildPlayerLookup` implementation and retained RRE/REA static analysis before attempting new searches. RRE's next bounded question: can the verified current-build `rift_x64.exe` code establish a module-relative root and dereference path to the same *current player* object, and distinguish player identity from a target/NPC, a transient allocation and a cached snapshot? Record the decisive source RVA/instructions, offsets, raw capture or test hash, and unknowns. Do **not** run another full Ghidra import or game action merely for this handoff.

Matching physical build for the existing RR2 sample (not a universal build claim): SHA-256 `1935a05c9db6d468e34e0055014a4a99c1b5afceb1695884e24600f5c20a4be8`. RRE must independently check byte/build identity before asserting static applicability.

## ROOT-001 — independent self-key origin check (November 10, 2026, ~22:40 EST)

**Status:** **independently validated exact-build *static entry fragment***, **not** a new live-qualified entity locator. This corroborates, rather than supersedes, RR2's existing `CurrentBuildPlayerLookup`. **Owner:** RRE owns this source-evidence feed; the existing RR2 owner alone owns candidate-reader integration, process reads and any controlled input.

- **Source and identity:** preserved RRE-owned `artifacts/lab2-live-20261107-0922/guest-rift_x64.exe` (60,493,640 bytes), SHA-256 `1935a05c9db6d468e34e0055014a4a99c1b5afceb1695884e24600f5c20a4be8`. Original bytes at RVA `0xA07093` for `0x2C` bytes: SHA-256 `f540923901a2a0ffbe9c0dd32aeb9c5008ba1c9017868aa2d55e94416ef73afd`.
- **Direct code facts (all RVAs):** literal `player` at `0x26D0D3C` is referenced by `0xA07093`; after the comparison, `0xA070AA` calls singleton accessor `0x49A020`, and `0xA070AF` reads QWORD `[RAX+0x360]` as the self-key candidate. Accessor `0x49A024` loads the singleton from `[module+0x33623E0]`. Separately, `Inspect.Unit.Detail` at `0x9B89A7` calls key parser `0xA1AAA0`; `0x9B89CA` calls manager accessor `0x4A4750` (global load `0x4A4754 → module+0x33624A8`); `0x9B89E8` calls identity lookup `0x6A0040` with the parsed key and manager. The neighboring `focus` and `mouseover` alias branches are distinct; this particular literal branch is not a selected-target read. This check **did not independently re-derive** the full manager hash-table internals.
- **Independent verification:** bounded source-file SHA+Capstone/pefile disassembly `rre_20261110_2233_root001_pe_selfpath_capstone_venv_ro` and `..._aliasbranches_capstone_ro`, plus independently written Python-stdlib PE/rel32, alias-literal and negative byte-mutation verifier `rre_20261110_2233_root001_independent_bytes_verifier_ro`; all final checks **exit 0**. Current inspected RR2 reader source: `C:\work\riftreader2\src\RiftReader2.Live\CurrentBuildPlayerLookup.cs`, SHA-256 `f3e9964b10609dbf6fe88d597d88f544d9a91e78923a29f74810607306cf4367` (**read-only**).
- **One RR2-owned follow-up:** on a newly authorized, source-qualified process epoch, use the *existing* `Resolve` to bracket the self-key and hash-resolved entity with PID/start/module/reader build checks, then separately compare a selection-changed `player.target` key while requiring the native self key to retain the independently observed player identity; record unavailability rather than substituting the target. No RRE game input or RR2 source change authorized here.

**Limitations:** static on-disk original bytes only; no live loaded-module attestation, simultaneous identity capture, current-player-versus-target runtime change, passive freshness, full restart re-resolution or atomicity proof. The exact executable SHA matches RR2's recorded expected build but does **not** prove the current physical process uses those bytes. Do not promote ROOT-001 to live-qualified.

## Existing lead to avoid rediscovery

**ORIENT-001 — owner of orientation matrix candidates.** **Candidate only; not RR2-ready as qualified facing.** RR2 observed two near-identical Y-planar matrix descriptors on the AMD-DESKTOP physical process, five samples with no angle change, while process/player/component identity remained fixed. Raw artifact `C:\work\riftreader2\artifacts\physical-native-orientation-ae0dcc6e91484f5c9241f6e89301c864.json`, SHA-256 `2b6940a75015524dcb1a5718ba20d35eadf66090f24c9165f17d4da99229e8bd`; RR2 commits `f2b1982` and `1dcafd5`. RRE can investigate whether code references establish the actual owner/refresh path. Static evidence alone will not qualify body yaw/camera yaw or freshness. No additional input authorized by this note.

## Publish only findings that RR2 can act on

For a useful finding, add one short entry here with:

- **Status:** observed static candidate / independently validated exact-build structure / ready for RR2 candidate implementation / live-qualified (with distinct evidence). Do not skip stages.
- **Identity and provenance:** exact executable SHA-256, source artifact path and SHA-256, original relative RVA(s), relevant offsets, owner and acquisition method; never publish a bare session absolute address as a durable pointer.
- **Action:** one concrete RR2 reader/experiment suggestion, the evidence supporting it, unresolved limitations, and any independent validation needed.

RR2 reads this file as an **information source**, never as an instruction to execute game actions, change environments or adopt an unverified offset. A static finding can be worth integrating as a **candidate**, but only RR2's own exact-host/epoch checks and later changed-state/restart evidence can qualify a live field.

**Coordination rule:** RRE owns the shared research priority and this feed; RR2 owns .NET/Lua integration and its validation. The two existing hourly automations remain separate workers under this single discovery-priority arrangement. No second coordinator, new service, broad sync, extra controller or automatic scan loop is introduced. When nothing new is proven, leave the feed unchanged.
