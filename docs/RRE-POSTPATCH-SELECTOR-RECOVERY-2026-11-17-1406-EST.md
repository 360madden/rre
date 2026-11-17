# RRE postpatch selector chain: concrete static resolution

**Tuesday, November 17, 2026 | ~14:02–14:07 EST | AMD-DESKTOP | RRE main.**

## Scope and source

Offline only. The physical RIFT client, processes, memory, UI, input, VMware, sibling repositories and full Ghidra import were untouched. All addresses are **RVA** unless explicitly prefixed by the image base (`0x140000000`). Source is the archived post-update `rift_x64.exe`, build `STABLE-1-1179-a-1256672`, SHA-256 `df954b798331e18359be62a31cc74b49fc3f50b87385ebb080a5448256322c01`. Prepatch archive was `STABLE-1-1177-a-1256632`, SHA-256 `1935a05c9db6d468e34e0055014a4a99c1b5afceb1695884e24600f5c20a4be8`.

This updates the *unresolved* host-selector section of [the earlier follow-up](RRE-POSTPATCH-FOLLOWUP-2026-11-17-1400-EST.md), which remains the source for prior tests, state-object methods and WA006 key formatting.

## P0 ROOT001 B: source-only selector chain is now resolved

| Stage | Exact native evidence | Static interpretation |
| --- | --- | --- |
| Host vptr | `0x75D4E9 mov rax,[rsp+0x60]`; `0x75D4EE lea rcx,[rip+0x1F6FB0B]`; `0x75D4F5 mov [rax],rcx` | Vptr assigned table VA `0x1426CD000` (RVA `0x26CD000`) |
| Table identity | `[0x26CD008]=0x14076F520` | Known large host adapter-registration method at vtable slot `+0x08` |
| Selector target | `[0x26CD0B8]=0x1407664D0` | Exact vtable slot `+0xB8` target |
| State setter | `0x77DC63` uses host `+0x1F8`; `0x77DC98 call 0x776670` | Updates state and invokes reselection |
| Dynamic call | `0x77671A–0x776740` loads host vptr; `0x776740 FF 90 B8 00 00 00` | Calls virtual slot `+0xB8` with host and state-key pointer |
| Registry selection | `0x7664EC add rax,0x240`; `0x7664FF call 0x783FC0`; `0x766525 call 0x75DCB0`; `0x766536 call 0x75E110`; `0x76653B mov rax,[rax+0x20]` | Searches hashed host registry keyed by state; extracts matching node's adapter payload (`node+0x30`), or returns null |
| `InGame` registration | `0x778C29` references `InGame\0` at `0x26B5FD0`; `0x778C0E` creates candidate ROOT001 B via `0xFC9170`; `0x778C45` uses host `+0x240`; `0x778C56` inserts and `0x778C63` stores B in node | Verified static registration for key `InGame` uses the same host registry |

The `0x75D4EE` vptr assignment **may execute in an object-reset/destruction path**. Static table/slot identity is established by that write and raw table entries; an active host instance's current vptr/selected adapter remains **unobserved**. Accordingly, `functionIdentityQualified=false` and `runtimeQualified=false` must remain until separate acceptance. The selector returns the B object only *if* the matching `InGame` state is selected and its registry entry persists.

Independent coordinator's PE-header/raw-byte check `rre-1117-independent-selector-bytes-1408` exited 0 and rechecked:
- `0x26CD000 → 0x14075E720`, `0x26CD008 → 0x14076F520`, `0x26CD0B8 → 0x1407664D0`;
- vptr LEA/write `488d0d0bfbf601488908`, selector `ff90b8000000`;
- archived SHA-256 matches exactly.

Six bounded specialist jobs exited 0: `rre-sel-table-01-20261117` … `rre-sel-table-04-20261117`, plus two bounded follow-up jobs documenting registry selection. Coordinator additionally ran independent disassembly and decoded `InGame\\0` directly from `.rdata` in `rre-1117-selector-reg-independent-1409` (exit0). No live game interaction.

## P1 WA006: corrected key-manager classification

The `!91b4eae3` key is copied/assigned, **not hashed by `0x52DD00`**. The wrapper constructor obtains manager `0x893FC0` and invokes `0x1274D64`; `0x1294AAC` derives C-string length and `0x52DD00` stores key bytes with allocation/SSO and NUL handling. `0x1274DA5–0x1274DAC` increments manager `+0x48`, with first-use conditional calls at `0x1274DD4`, `0x1274DFF`, `0x1274E6C`. Paired wrapper destructor `0xF7CC89` calls cleanup `0x1274968`, which decrements the count and follows a final-release branch when zero. **Exact manager service, meaning of key and wrapper+8 owner remain unproven.**

Independent bounded jobs: `rre-child-wa006-manager-deps-1117-02`, `rre-child-wa006-manager-dasm-1117-03`, `rre-child-wa006-manager-lifetime-1117-04` all exit0. First command `rre-child-wa006-manager-small-1117-01` exit1 due system Python lacking `pefile`; the already-installed repo `.venv` solved this without installation. The corresponding phrase in the prior report was corrected in place.

## P1 bit7: cross-build homolog **not** established

Current state-object constructor `0x1C10390` installs vtable `0x2A293E8`; the `0xA0`-byte reference-counted object's `+0x10` flag mask is set by `OR ...,0x80`, meaning **bit7**. In the older archived executable, the same RVA contains a *different* function. An exact generic constructor-family byte pattern occurs 14 times; old RVAs `0x23BAB50` and `0x1B19BF0` resemble the new constructor but **are not identity qualified**. Do not assert patch changed this object's layout until tracing old B's allocator/constructor directly. Four short comparison jobs passed; an initial invalid executable path was retried without modification. No source files or game touched by that lane.

## Regression and acceptance gates

The coordinator independently re-ran **42/42 unit tests** after adding the selector source checks: ROOT001 B **16/16**, WA006 **13/13**, analyzer **13/13**. Jobs `rre-1117-postpatch-integration-b-unit-1412`, `-wa-unit-1412`, `-an-unit-1412` exited 0. Real archived PE jobs `rre-1117-postpatch-integration-b-real-1412` and `-wa-real-1412` also exited 0: respectively **`SOURCE_PINNED_ONLY`** and **`SOURCE_MAP_PINNED_ONLY`**. The B gate now checks three selector opcodes, host vptr target, vtable `+0xB8` target, and the registry offset; three new mutation-test methods ensure corruption is rejected. `selectorSourcePinned=true`, but **`functionIdentityQualified=false`** and **`runtimeQualified=false`**. This source-chain proof does **not** upgrade runtime compatibility.

## Next work, ranked

| Priority | Action | Reason | Expected result | Execution |
| --- | --- | --- | --- | --- |
| **P0** | Trace host object's construction/activation path, distinguishing the proven vptr write from reset/destruction | Current vtable slot is concrete, but active instance identity is not | Prove constructor-side vptr assignment and state-key activation, or bounded negative with exact paths | Coordinator autonomous, offline |
| **P1** | Follow old B's allocator call to qualify the prepatch state-object constructor | 14 generic constructor hits cannot establish identity | Proven cross-build homolog and field/flag comparison or bounded negative | Autonomous, offline |
| **P1** | Trace the registration manager's first-use/last-release callbacks and wrapper same-instance `+8` ownership | WA006 domain and runtime owner still unknown | Confirmed service/owner link or documented bounded negative | Autonomous, offline |
| **P2** | Seek new, task-specific authority for physical RIFT read-only selection observation once static gates are stable | Executable code alone cannot prove current active in-game receiver | Source-and-runtime receiver identity with exact build/process/owner gates | Joey involvement required before any live operation |

**Stop line:** static registry/call-path qualification is not proof of current running RIFT behavior. Preserve other sessions' nine untracked entries and all current controller/game state.
