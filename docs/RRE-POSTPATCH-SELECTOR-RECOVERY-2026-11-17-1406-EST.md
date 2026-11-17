# RRE postpatch selector chain: concrete static resolution

**Tuesday, November 17, 2026 | ~14:02–14:30 EST | AMD-DESKTOP | RRE main.**

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

Six bounded specialist jobs exited 0: `rre-sel-table-01-20261117` … `rre-sel-table-04-20261117`, plus two bounded follow-up jobs documenting registry selection. Coordinator additionally ran independent disassembly and decoded the NUL-terminated `InGame` literal directly from `.rdata` in `rre-1117-selector-reg-independent-1409` (exit0). No live game interaction.

## P1 WA006: corrected key-manager classification

The `!91b4eae3` key is copied/assigned, **not hashed by `0x52DD00`**. The wrapper constructor obtains manager `0x893FC0` and invokes `0x1274D64`; `0x1294AAC` derives C-string length and `0x52DD00` stores key bytes with allocation/SSO and NUL handling. `0x1274DA5–0x1274DAC` increments manager `+0x48`, with first-use conditional calls at `0x1274DD4`, `0x1274DFF`, `0x1274E6C`. Paired wrapper destructor `0xF7CC89` calls cleanup `0x1274968`, which decrements the count and follows a final-release branch when zero. **Exact manager service, meaning of key and wrapper+8 owner remain unproven.**

Independent bounded jobs: `rre-child-wa006-manager-deps-1117-02`, `rre-child-wa006-manager-dasm-1117-03`, `rre-child-wa006-manager-lifetime-1117-04` all exit0. First command `rre-child-wa006-manager-small-1117-01` exit1 due system Python lacking `pefile`; the already-installed repo `.venv` solved this without installation. The corresponding phrase in the prior report was corrected in place.

### WA006 singleton root, without a premature owner claim

Four additional SHA-pinned archived-PE read-only jobs (`rre-child-wa006-sameinstance-xrefs-1117-01`, `-callers-1117-02`, `-globalxrefs-1117-03`, `-manager-writers-1117-04`) exited0. Eight PDATA-aligned callers of wrapper constructor `0xF7CC20` (`0x4A298A`, `0x6A6986`, `0x751CFA`, `0x82E0B2`, `0xF7DD78`, `0xF7F0F9`, `0xF8431B`, `0xFD9ED2`) allocate **0x68 bytes**, then place the returned wrapper into the same RIP-global singleton at VA `0x143373C58` (RVA `0x3373C58`). Some callers store it twice. The scan confirmed 68 direct RIP-relative references to that singleton; this is a concrete root for bounded member-write tracing, **not proof of wrapper+8 owner**.

The manager increments `[rsi+0x48]` at `0x1274DA5`, compares its first-use transition at `0x1274DA8`, and conditionally calls `0x127647C`, `0x128F81C`, and `0x129347C`. Cleanup decrements `[rcx+0x48]` at `0x1274971`, with a zero-count callback to `0x129359C` at `0x12749DB`. Their domain/service identities remain unknown because these manager helpers are widely shared. Crucial alias distinction: `0x13E9A2B` clears **`[wrapper+8]`**, whereas `0x13E9A62` writes **`[child+8]=wrapper`** (a child backpointer). Both `0x13EA600` and `0x13E9F10` read `[wrapper+8]`; none of these demonstrates its missing nonzero writer. **Same-instance ownership remains unresolved.**

## P0 host normal construction now source-qualified

An additional bounded caller trace established the **normal factory** rather than relying on the teardown/reset vptr assignment:
- At `0x762394`, factory `0x762390` allocates a **0xA50-byte host**; `0x7623B0` directly calls constructor `0x75BE50`.
- Constructor calls base init `0x12602F8` at `0x75BE77`, then `0x75BE84 lea rcx,[rip+0x1F71175]` and `0x75BE8B mov [rax],rcx` install **the same vtable RVA `0x26CD000`**.
- `0x75C02D–0x75C036` initializes state key at host `+0x1F8`; `0x75C043` clears selected adapter `+0x218`; `0x75C06C–0x75C075` initializes registry `+0x240`.
- Factory calls `0x6A4350` at `0x7623D1` with the new host and a global address (precise ownership still unknown). The separate `0x76234D` state setter call constructs **`ConnectToGameFailed\0`** only on a false predicate; that path is **not** the normal `InGame` activation.

The archived executable and opcodes were independently checked by coordinator job `rre-1117-independent-host-ctor-1418` (exit0). Four specialist jobs `rre-host-ctor-01-function-windows-1117` through `rre-host-ctor-04-factory-call-window-1117` exited0. This **proves source-level normal construction and registry initialization**, but no currently running process or active receiver was sampled.

### Two `InGame` state transitions independently source-qualified

Aligned, function-boundary-aware Capstone disassembly (not raw opcode-proximity scanning) identifies two actual calls that construct `InGame` and pass it to setter `0x77DC50`:

- **Path A, call `0xFCEFFE`:** Literal `InGame` at RVA `0x26B5FD0` is loaded at `0xFCEF8F` (short-buffer branch) or `0xFCEFD8` (heap branch). The local SSO object is copied and NUL terminated; `0xFCEFF7 lea rdx,[rbp-0x21]`, `0xFCEFFB mov rcx,r13` (host), then `0xFCEFFE call 0x77DC50`. Guards at `0xFCEF24–0xFCEF5D` examine `r14b`, `r15d`, predicate `0xFA3940`, result of `0x4C4180 == 2`, and optionally `0x81BFF0`. **Their gameplay meanings are unknown**.
- **Path B, call `0xFCF5CF`:** The same `InGame` literal appears at `0xFCF523`, `0xFCF558`, or `0xFCF5A2` across string-size branches; the local string is NUL terminated. At `0xFCF5C2`, host getter `0x766490` is called, then `0xFCF5C7 mov rcx,rax`, `0xFCF5CA lea rdx,[rsp+0x30]`, and `0xFCF5CF call 0x77DC50`. Getter `0x766490` uses global-holder RVA `0x3383CB0` and calls `0x6A43D0`, the **same getter** the host factory calls at `0x7623DE`. This connects a normal host-factory holder with a concrete `InGame` activation path.

All five state-key specialist jobs passed: `rre-host-statekey-01-ssosource-1117` through `rre-host-statekey-05-guard-hostgetter-1117`. These establish **static reachability and argument flow**, not that the current game process executed either path, populated registry, or selected B.

## P1 bit7: genuine old/new B-path layout and mask change **qualified**

The earlier generic constructor search was inconclusive; a subsequent **actual B-helper call-chain comparison** resolved the homolog without guessing an RVA:

| Evidence | Old `STABLE-1-1177-a-1256632` | New `STABLE-1-1179-a-1256672` |
| --- | --- | --- |
| B helper | `0xFCAA65 → 0x1C162C0` | `0xFCAA35 → 0x1C1AE90` |
| Object allocation | `0x1C162F3`, **0xA8 bytes** | `0x1C1AEC3`, **0xA0 bytes** |
| Object constructor | `0x1C0BC80` | `0x1C10390` |
| Constructor vtable | `0x2A1CFB0` | `0x2A293E8` |
| B state field | `+0x20` | `+0x18` |
| B mask set | `OR [object+0x10],0x01` (**bit0**) | `OR [object+0x10],0x80` (**bit7**) |

Both constructors clear refcount at `+0x08` and mask at `+0x10`. In both builds, matching virtual slots `+0x08` (bit test), `+0x18` (bit set/clear), `+0x20` (four-byte mask serialization), and `+0x28` (flag reconstruction retaining bit31) establish a **corresponding functional object family**. Four cross-build jobs `rre-oldb-homolog1-1117` through `rre-oldb-homolog4-1117` exited0 against SHA-verified archives. **This is a verified change to allocation size, state-field offset and flag bit, not a mere RVA relocation.** The class name, bit meaning and runtime consequences remain unknown.

## Regression and acceptance gates

The coordinator independently re-ran **46/46 unit tests** after the normal-host and `InGame` checks: ROOT001 B **20/20**, WA006 **13/13**, analyzer **13/13**. Jobs `rre-1117-host-ingame-final-b-unit-1421`, `-wa-unit-1421`, `-an-unit-1421` exited0. Real archived PE jobs `rre-1117-host-ingame-final-b-real-1421` and `-wa-real-1421` also exited0: respectively **`SOURCE_PINNED_ONLY`** and **`SOURCE_MAP_PINNED_ONLY`**. The B gate checks the earlier selector opcodes/vptr/+0xB8/registry and now the normal factory allocation, ctor vptr, four RIP-relative LEA targets (including `InGame`), four direct-call targets, six host-state opcodes and literal bytes. Seven added mutation-test methods across the two increments reject altered anchors. Source outputs `selectorSourcePinned=true`, `hostConstructionSourcePinned=true`, `inGameTransitionsSourcePinned=true`, but **`functionIdentityQualified=false`** and **`runtimeQualified=false`**. This source-chain proof does **not** upgrade runtime compatibility.

New standalone **`tools/verify_prepost_root001_layout.py`** compares both SHA-256/size-pinned archived PEs, five opcode anchors, three rel32 calls, one vtable LEA and four vtable slots **per build**. On direct coordinator rerun, archived-PE gate `rre-coord-1117-1430-cross-real` exited0 with `SOURCE_PINNED_ONLY`, the **0xA8→0xA0**, **+0x20→+0x18**, and **0x01→0x80** differences; 10 synthetic/optional-real regression tests in `tools/test_verify_prepost_root001_layout.py` passed (`rre-coord-1117-1430-cross-test`, exit0, 0.168s). `git diff --check` exited0 (`rre-coord-1117-1430-diff-check`). The gate reports `layoutCompatible=false`, **`functionIdentityQualified=false`**, and **`runtimeQualified=false`**. Invocation from `C:\work\rre`: `.venv\Scripts\python.exe tools\verify_prepost_root001_layout.py`; no live client attachment.

## Next work, ranked

| Priority | Action | Reason | Expected result | Execution |
| --- | --- | --- | --- | --- |
| **P0** | Qualify the active adapter/receiver against the physical postpatch client only after fresh task-specific authority and exact build/process/owner gates | Static selector and `InGame` transitions now pass source gates; gameplay behavior is still unknown | Verified live receiver identity and compatibility result or safely recorded failed gate | Requires Joey approval before live observation |
| **P1** | Qualify the remaining `InGame` Path A activation-guard meaning using archived source and existing trace | Both `InGame` setter paths are pinned, but guard predicates are not yet understood | Function-boundary proof of guarded activation conditions without asserting live behavior | Autonomous, offline |
| **P1** | Trace same-instance `[wrapper+8]` writes from the 68 singleton references, then examine helper `0x078538`/`0x0786CC` if needed | Manager first/last callbacks and singleton roots are source-verified, but nonzero member writer and service meaning remain unknown | Source-qualified member writer or bounded negative without confusing child backpointer | Autonomous, offline |

**Stop line:** static registry/call-path qualification is not proof of current running RIFT behavior. Preserve other sessions' nine untracked entries and all current controller/game state.
