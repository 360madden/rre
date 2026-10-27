# SC-401 — New RIFT build: first native code xrefs for ability/castbar metadata

**October 27, 2026. Status: PARTIAL but SOURCE-VERIFIED.** REA research only. This is a short Chat-mode checkpoint, **not** SC401/SC4 phase acceptance. No game inputs, runtime attach, Ghidra whole-client import, game patch or RR2/Workbridge source changes.

## Source scope

Physical-host **updated** RIFT x64 executable: SHA-256 `1935a05c9db6d468e34e0055014a4a99c1b5afceb1695884e24600f5c20a4be8`. Original PE has preferred image base `0x140000000`. VM Lab-2's actual guest game build is **unverified**. Reuse of prior SHA `7c356c9dde9e12fcbff3c08d953b0630b48b1510a0ffb36e4ec164606e7b17bd` offsets remains disallowed without byte evidence.

Inputs: [new-build static API anchors](REA-RIFT-SPELLCASTING-SC404-NATIVE-ANCHORS-2026-10-27.json) and [exact code-reference records](REA-RIFT-SPELLCASTING-SC401-XREF-2026-10-27.json). All addresses below are **new-build RVAs**, not current runtime pointers. Function ranges are taken from original PE `.pdata` unwind records; instructions from original `.text` decoded by already-installed Capstone. No synthetic/rebased mini-PE was needed.

## Three bounded functions with confirmed data references

| Candidate description | Original new-build function RVA | Original function bytes SHA-256 | Direct data reference |
| --- | --- | --- | --- |
| Ability-data descriptor manipulation | `0x9b0376–0x9b0776` (1,024 bytes) | `5e474301f73f561abb8d2f1d023d42f556eb7311eec5085099e9494d11a9dc52` | 25 source-verified RIP-relative references into `0x2f62d00–0x2f62df0` |
| Castbar-data descriptor context | `0x9b84f0–0x9b88cd` (989 bytes) | `abab568192a29d07ba21efd8252a4c1f1efb3c2f339ea338840036aa75c611c0` | 4 RIP-relative references into `0x2f649b0–0x2f64a60` |
| Ability-data maintenance candidate | `0x255f5c0–0x255f63d` (125 bytes) | `07a631965b4bcef261d5c1a515c427c36ec3f5f6256dc87a4eb17d8698250837` | 8 references into `0x2f62d00–0x2f62df0` |

**Verified instruction examples:**

- At RVA `0x9b0567`: source bytes `48 8D 0D BA 27 5B 02` decode as `lea rcx, [rip + 0x25b27ba]`, reaching `0x2f62d28`. Next instructions include `mov edx,0x30` and direct call to **RVA `0x12942a0`**. This proves a code use of that data region; it **does not** establish that the callee enumerates abilities.
- At RVA `0x9b8519`: bytes `4C 8B 05 D0 C4 5A 02` decode as `mov r8, qword ptr [rip + 0x25ac4d0]`, reaching castbar data RVA `0x2f649f0`. This is a source-backed native code-to-data reference, not proof of live castbar semantics.
- At RVA `0x255f5ca`: bytes `48 8B 1D 37 37 A0 00` decode as `mov rbx, qword ptr [rip + 0xa03737]`, targeting ability-data RVA `0x2f62d08`; nearby instructions access adjacent fields and call a separate function at RVA `0x58c650`.

**Decoder constraints:** all three bounded intervals decoded through their reported `.pdata` ends (269, 218 and 27 instructions respectively). Code regions are **not named from symbols** and their roles have not been authenticated by native call graph/arguments or live behavior. The first large region appears to manipulate descriptor-like state; assuming it implements `Inspect.Ability.New.List` would be unjustified.

The initial raw signed RIP-displacement scan yielded candidate offsets, including false-positive possibilities. Four candidate instructions were independently decoded with Capstone and their computed target RVAs matched the expected data regions exactly. The final bounded source group is therefore stronger than a byte-pattern guess, but still short of a function contract.

## Next native decision — do not enlarge the scope prematurely

**SC401 remains ready with a partial checkpoint.** Determine whether the newly found descriptor/code regions connect to the actual **ability enumeration callback** or merely static API-description registration. Follow one call/caller at a time from the source-backed candidates (notably `0x12942a0` and `0x16894e0`) and look for a verifiable input/output link to current known-ability IDs or native storage. Use the existing source-backed RRE/REA bounded query path and return `supported`, `disproved` or `unresolved`. Avoid the previous unproductive >450s whole-image imports; no code injection or live game input in this REA lane.

The relation to `ActionBars_AbilityQueue` or independently timed GCD remains **not demonstrated**. The old 55-ability list / damage events apply to the old guest build. Today's new host PE is **not yet the qualified binary inside Lab-2**.

## Durable evidence

- [Machine-readable instruction/source record](REA-RIFT-SPELLCASTING-SC401-XREF-2026-10-27.json): original file SHA, exact instruction bytes, source function ranges, call target samples, descriptor references and task limits.
- Focused Workbridge jobs `rea-oct27-sc401-ripdisp-candidates-01` (raw candidate search), `rea-oct27-sc401-xref-disasm-02` (four exact instructions), `rea-oct27-sc401-limited-functions-03` (bounded `.pdata` function regions), all exit 0.
- Status **partial**, next task still SC-401; Ghidra/REA 6.5.0 install unchanged. No acceptance of a native casting handler, current-game executable, GCD or server response.
