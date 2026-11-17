# RRE postpatch selector chain: concrete static resolution

**Tuesday, November 17, 2026 | ~14:02–14:46 EST | AMD-DESKTOP | RRE main.**

## Scope and source

Offline only. The physical RIFT client, processes, memory, UI, input, VMware, sibling repositories and full Ghidra import were untouched. All addresses are **RVA** unless explicitly prefixed by the image base (`0x140000000`). Source is the archived post-update `rift_x64.exe`, build `STABLE-1-1179-a-1256672`, SHA-256 `df954b798331e18359be62a31cc74b49fc3f50b87385ebb080a5448256322c01`. Prepatch archive was `STABLE-1-1177-a-1256632`, SHA-256 `1935a05c9db6d468e34e0055014a4a99c1b5afceb1695884e24600f5c20a4be8`.

This updates the *unresolved* host-selector section of [the earlier follow-up](RRE-POSTPATCH-FOLLOWUP-2026-11-17-1400-EST.md), which remains the source for prior tests, state-object methods and WA006 key formatting.

Independent patch provenance was checked read-only against `C:\work\Update Helper\PATCH_EVIDENCE_2026-11-17.md` (no edits to that sibling repository). Its before/after manifests measured **274→272 files**, **7 content modifications**, **2 removed download records**, **0 additions**, and two consistent 272-file post-update scans. The changed set includes `rift_x64.exe` (60,493,640→60,574,536 bytes), `rifterrorhandler_x64.exe`, `Assets/assets.242`, `manifest64.txt`, and three `assets64*.manifest` files; hashes of the RIFT executables/build identifiers agree with RRE's archived PE work. This cross-repo manifest supports patch provenance, **not any RRE runtime compatibility inference**.

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

Four additional SHA-pinned archived-PE read-only jobs (`rre-child-wa006-sameinstance-xrefs-1117-01`, `-callers-1117-02`, `-globalxrefs-1117-03`, `-manager-writers-1117-04`) exited0. Eight PDATA-aligned callers of wrapper constructor `0xF7CC20` (`0x4A298A`, `0x6A6986`, `0x751CFA`, `0x82E0B2`, `0xF7DD78`, `0xF7F0F9`, `0xF8431B`, `0xFD9ED2`) allocate **0x68 bytes**, then place the returned wrapper into the same RIP-global singleton at VA `0x143373C58` (RVA `0x3373C58`). Some callers store it twice. The initial scan confirmed 68 direct RIP-relative references to that singleton; a later broader aligned `.text` scan enumerated **72 direct decoded references in 30 PDATA-aligned functions**. These are different scan scopes, not contradictory counts. They provide a concrete root for bounded member-write tracing, **not proof of wrapper+8 owner**.

The manager increments `[rsi+0x48]` at `0x1274DA5`, compares its first-use transition at `0x1274DA8`, and conditionally calls `0x127647C`, `0x128F81C`, and `0x129347C`. Cleanup decrements `[rcx+0x48]` at `0x1274971`, with a zero-count callback to `0x129359C` at `0x12749DB`. Their domain/service identities remain unknown because these manager helpers are widely shared. Crucial alias distinction: `0x13E9A2B` clears **`[wrapper+8]`**, whereas `0x13E9A62` writes **`[child+8]=wrapper`** (a child backpointer). Both `0x13EA600` and `0x13E9F10` read `[wrapper+8]`; none of these demonstrates its missing nonzero writer. **Same-instance ownership remains unresolved.**

Further bounded SHA-pinned jobs (`rre-child-wa006-xref-classify-1117-01`, `-methods-1117-02`, `-function-writes-1117-03`, `-alias-proof-1117-04`; all exit0) examined direct singleton references and candidate member stores. Calls at `0x4A2918→0x4A2975`, `0x6A6923→0x6A6970`, `0x7328AB→0x732907`, and `0xF7F088→0xF7F0E4` initialize separate 0x10-byte child/backpointer structures before an independently allocated 0x68-byte wrapper is constructed and globally stored. These **cannot be promoted to same-wrapper `+8` writes**. At `0x13E7E2A`, helper `0x13E7E20` only reads `[rdx+8]`; `0x13EA632` likewise reads `[rcx+8]` before `0x786CC`. The 30-function direct-xref census found **no source-qualified nonzero writer**; indirect setters/alias lifetime remain to investigate.

Three final bounded follow-up jobs (`rre-child-wa006-longalias-job1-1117` through `-job3-1117`, all exit0) inspected PDATA range `0x7321A6–0x732DA7` and eight direct singleton references. After wrapper allocation and stores at `0x732928/0x732937`, `0x732942` loads wrapper as RCX and `0x732945` calls `0x13EA600`; this decrements `[wrapper+0x60]` at `0x13EA62A`, loads `[wrapper+8]` at `0x13EA632`, and forwards to `0x786CC`. A second allocation/store at `0x732CD0/0x732CDF` calls `0x13E9F10` at `0x732CED`; that increments `[wrapper+0x60]` at `0x13E9F40`, loads `[wrapper+8]` at `0x13E9F4C`, then calls helper `0x78538` at `0x13E9F50`. These prove **consumer forwarding of `wrapper+8`**, not its writer or service meaning. Four `+8` stores (`0x7328EC`, `0x732903`, `0x732C9E`, `0x732CB2`) are tied to separate 0x10-byte children before the 0x68 wrapper exists. A further SHA-pinned job `rre-child-wa006-longalias-followup-j1-1117` (exit0) qualified the fifth candidate `0x7326B5`: `0x73248D` obtains a hash container, `0x73266F` selects an existing entry or `0x73269A` allocates a new **0x18-byte table entry** with `0x12947C0`, `0x7326A7` reads its key, `0x7326B5` stores that key to `[rdi+8]`, then `0x7326B9` and `0x7326C7` populate/insert the map entry. **All five apparent `+8` stores in this function are source-qualified as non-wrapper fields**; the bounded negative remains: no verified nonzero write to the same wrapper's `+8` field.

A later three-job SHA-pinned base-class inspection (`rre-child-wa006-base-provenance-j1-1117` through `j3`, all exit0) rechecked base constructor `0x13E9A10`, which clears wrapper+8 at `0x13E9A2B`, then creates two separate 0x10-byte children with their own `[child+8]=wrapper` backpointers at `0x13E9A62` and `0x13E9A88`. Derived 0x68-byte wrapper constructor `0xF7CC20` calls this base, but has no demonstrated nonzero `wrapper+8` assignment. Base vtable RVA `0x27A2568` has methods `0x13E9FC0` and `0x13EA010` that **read** `[rcx+8]` and forward to `0x13EA060`; method `0x13EA720` clears **one byte** at `[rcx+8]`. Derived wrapper vtable RVA is `0x271E468`. Neither a read, child backpointer, nor partial zeroing qualifies the missing same-instance nonzero writer, and the active vtable is unobserved.

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

### Path A `InGame` activation guard control flow (source only)

Four later SHA-verified PDATA-aware archived-PE jobs (`rre-patha-guards-1117-j1` through `j4`, all exit0) traced combined range `0xFCE920–0xFCF1D8`, including a split function record at `0xFCEB1C`. At entry `0xFCE941 mov rsi,rcx` saves context, and `0xFCE944 mov r13,rdx` saves the host pointer supplied by the caller; `r15d` originates via `0x1593510→0x1593070` at `0xFCEA55–0xFCEA65`. The setter at `0xFCEFFE` is reached only if **(1)** `r14b != 0` OR (`r15d==0` AND `0xFA3940` returns nonzero), **(2)** the first dword of the singleton object returned by `0x4C4180` equals integer `2`, AND **(3)** `[rsi+0x48]` is null OR `0x81BFF0([rsi+0x48])` returns nonzero. Failures branch to alternate work at `0xFCF054`. `r14b` starts zero at `0xFCEE87`, and may be set at `0xFCEEED` after cached state comparisons (`[rsi+0x70]`, `[rsi+0x74]`), a float threshold, and a context check. Predicate `0x81BFF0` reads internal offsets `+0x3A`, `+0x38`, `+0x10`, with a conditional call `0x81F5F0`. These are **verified source control-flow prerequisites**, not identified gameplay states; no active branch execution was observed.

A later three-job SHA-pinned state-provider investigation (`rre-child-state2-getter-disasm-1117-01`, `-cont-1117-02`, `-ctor-callers-1117-03`; all exit0) found that `0x4C4180` is a **lazy singleton pointer getter**, not an integer-valued API: it reads global RVA `0x337D2C8` at `0x4C4184`; if null it allocates a 0x1B8-byte object at `0x4C4221`, calls ctor `0x9C96E0` at `0x4C4238`, and stores the pointer globally at `0x4C4240/0x4C4257`. Constructor `0x9C977E` clears the object's first dword to **0**. Path A's comparison at `0xFCEF44` therefore requires **`[singleton_object+0]==2`**. Its writer, enum meaning and live value are still unverified; 267 raw direct-call-shaped references to the getter were only discovery hits, not 267 validated caller paths.

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

The ROOT001 source gate now also pins **12 concrete Path A guard opcodes/branches and five rel32 call targets** (`INGAME_A_GUARD_OPCODES`, `INGAME_A_GUARD_CALL_TARGETS`); it reports `inGameAGuardsSourcePinned=true` while retaining false runtime/function-identity qualifiers. Two new mutation-test methods reject changed branches and call targets. Coordinator's independent validation `rre-coord-1117-1440-root-real` returned `SOURCE_PINNED_ONLY`, exit0. The complete four-suite rerun passed **58/58**: ROOT001 **22**, WA006 **13**, analyzer **13**, cross-build **10** (jobs `rre-coord-1117-1440-root-tests`, `-wa-tests`, `-an-tests`, `-cross-tests`; all exit0). These check source bytes, **not** live execution.

## Next work, ranked

| Priority | Action | Reason | Expected result | Execution |
| --- | --- | --- | --- | --- |
| **P0** | Qualify the active adapter/receiver against the physical postpatch client only after fresh task-specific authority and exact build/process/owner gates | Static selector and `InGame` transitions now pass source gates; gameplay behavior is still unknown | Verified live receiver identity and compatibility result or safely recorded failed gate | Requires Joey approval before live observation |
| **P1** | Trace exact writes/transition conditions for `[0x1B8 singleton+0]` reaching value `2`, and qualify the `0x81BFF0` predicate if needed | `0x4C4180` is now a verified lazy singleton getter, but state `2` meaning and writer are unknown | Source-qualified state-transition writer/guards or bounded negative | Autonomous, offline |
| **P1** | Trace derived-wrapper virtual methods and indirect setter aliases beyond the examined base/vtable paths | Base ctor, two child backpointers, consumers, and one-byte zeroing are source-verified but no nonzero same-wrapper+8 writer | Proven writer/owner link or explicit bounded negative | Autonomous, offline |

**Stop line:** static registry/call-path qualification is not proof of current running RIFT behavior. Preserve other sessions' nine untracked entries and all current controller/game state.
