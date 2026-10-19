# Follow cancellation: offline findings

Branch: `research/nav-follow`. Worktree: `C:\work\rre-worker-follow`.
Research date: 2026-10-18 local time. Companion evidence: [follow.json](follow.json).

The strongest cancellation lead is the normal input dispatcher, which calls **two separate clear routines**: follow-state clear `0x534200` and parallel-state clear `0x534990`. A likely click-to-move activation path calls both before replacing its coordinate request. This supports a common input path, but does **not** prove one stop mechanism or in-game stopping.

## Build, sources and method

- Executable: `C:\Program Files (x86)\Glyph\Games\RIFT\Live\rift_x64.exe`.
- SHA-256 rechecked by fresh static queries: `7c356c9dde9e12fcbff3c08d953b0630b48b1510a0ffb36e4ec164606e7b17bd`.
- All addresses below are RVAs; preferred static base `0x140000000`. A live base is not assumed.
- Read the three required navigation baselines and coordination rules. Reused `tools/inspect-navigation-static.py` and `tools/inspect-navigation-names.py`, importing original RiftReader helpers read-only with their pinned hashes.
- Interpreter: `C:\work\rre\.venv\Scripts\python.exe`; measured dependencies: pefile `2024.8.26`, Capstone `5.0.7`. The latter differs from baseline prose `5.0.9`, but agrees with prior artifact metadata. Nothing was installed or changed.
- Four artifacts under `C:\work\rre\artifacts\navigation-20261018-01` were hash-checked against `docs/navigation-findings.json`: `static-navigation-command-callers.json`, `static-navigation-command-regions.json`, `static-navigation-string-references.json`, and `static-navigation-names.json`. Full hashes are in the companion JSON.
- Method: PE exception/unwind-chain ranges, Capstone disassembly, original helper call candidates, restricted string references and bounded PE table reads. No REA decompilation, import retry, process attachment, target execution, memory modification or live input.

`follow.json` retains all 16 qualified callers, 50 fresh region hashes/coverage records, 322 selected instruction rows, exact table/string bytes, interpretations and unknowns. `codeEvidence` keys below are evidence locators, not native symbol names.

## Directly observed native code

**Follow clear (`followClear`).** At `0x534240`, `r15 = this + 0xB60`; `r12d` is zeroed and `0x53424A` tests the qword. Zero jumps directly to `0x53494F`, which writes zero through `r15`. The nonzero path references the stopped-following message at `0x2646388` through `0x534339`, performs formatting/notification work, then reaches the clear. This establishes follow association, but not a movement side effect or callable external contract.

**Separate clear (`parallelClear`).** Root `0x534990` uses `component = [this+0xB90]`. If component `+0x70` is nonzero, it handles the `+0x70/+0x78` pair, calls `0x494830` and `0x860530`, and clears the pair at `0x534A0E/0x534A12`. It then clears bit 0 of component `+0x1A8` at `0x534A29`. Callee semantics remain unknown. This representation differs from follow `this+0xB60`.

**Coordinate request (`vectorSetter`, `inputAndSetting`).** `0x562BC0` calls both clears, copies 12 bytes from its second argument to component `+0x60/+0x68`, and sets bit 0 of `+0x1A8`. Its verified direct caller is `0x69468D`, in unwind-chain root `0x6942A0`. That path checks retrieved-object `+0x146` (`0x6943C2`), uses event integers `+0x128/+0x12C`, calls `0xF7A870`, forms vectors and calls `0xF671C0`; success reaches the setter. **Inference:** likely native C2M destination activation, given the baseline's `Misc_EnableClickToMove` association at settings `+0x146`. Retrieved-object alias to the baseline settings singleton, coordinate space, button meaning and query contract are not independently proved here. No pathfinding result is established.

**Input actions (`actionDispatch`, `inputReconcile`).** Event path `0x694315` calls binding resolver candidate `0x7B20A0`, then forwards its result to `0x695810` at `0x694377`. Its switch covers action IDs 2 through 16, table `0x6968A8`. IDs 2-7 converge on both clears at `0x695B0F/0x695B17`. ID 10 calls `0x572D30` before both at `0x695B31/0x695B39`; ID 9 calls `0x572EF0` before both at `0x695B53/0x695B5B`. The first helper toggles `this+0x39C`, making autorun a hypothesis for ID 10, not an assigned label. Separately, `0x6969F0` conditionally calls both after `0x697A40(false)` reports a change; that helper reads action states and updates input bits. Physical keys, action labels and press/release polarity remain unresolved.

**Follow command family (`followNameLeaf`, `followCommand`).** The exact eight-byte leaf at `0x6ADA60` returns ASCII `follow` at `0x264EBD0`. Its pointer at `0x264EBB0` is adjacent to execution candidate `0x6ADA70` at slot `0x264EBA8`. The latter obtains a target-like argument through `0x53CE30 -> 0x5DADF0`, then calls `0x5706D0`. That routine starts with both clears (`0x570709/0x570711`); a later path stores a qword at `this+0xB60` (`0x571203`) and references the following message (`0x5712B6 -> 0x2646360`). **Inference:** standard follow command execution. Dispatch/accepted slash syntax are not runtime-tested. Repeating `/follow` may replace or restart follow; it is not a qualified stop command.

**Receiver (`singletonAccessor`).** `0x486BF0` returns a cached pointer from module RVA `0x32E0200`, initializing a `0xF40`-byte object through `0x52BDE0` when needed. Compact callbacks compare their associated object's `+0x30` against the accessor result's `+0x360`. This strengthens a common local-identity association; concrete class/player-controller identity remains unknown.

## Classification of all 16 verified direct callers

These are instruction-boundary-qualified direct **sites**, not 16 source functions. Classification beyond listed operations is inference. Full ranges and uncertainties are in JSON `directCallers`.

| Follow call site | Root / context | Observed operations and interpretation |
| --- | --- | --- |
| `0x4D1661` | `0x4D1530` | Compares `InGame`, toggles a global boolean, calls both clears plus `0x5341E0`; likely UI/mode transition. No proof of Escape, pause or menu. |
| `0x562BD0` | `0x562BC0` | Both clears before replacing 12-byte request and activating its bit; likely C2M replacement. |
| `0x570709` | `0x5706D0` | Clears old states before processing target-like argument; likely follow initialization/replacement. |
| `0x57670F` | `0x5765D0` | Guarded maintenance branch calls both clears. No demonstrated input gesture. |
| `0x5768A5` | `0x5765D0` | Passes address of `this+0xB60` to `0x68E150`; null result sets a flag reaching both clears. Likely failed target resolution. |
| `0x576BAA` | `0x5765D0` | Scalar threshold comparison plus follow guard reaches follow clear only in this local branch. Quantities/arrival meaning unresolved. |
| `0x695B0F` | `0x695810` | Actions 2-7 reach both clears; strongest normal manual-movement candidate. |
| `0x695B31` | `0x695810` | Action 10 toggles `+0x39C`, then both clears; autorun-like hypothesis. |
| `0x695B53` | `0x695810` | Action 9 calls another helper then both; action meaning unresolved. |
| `0x696A36` | `0x6969F0` | State reconciliation gates both clears and marks event `+0x18`. |
| `0x71B23C` | `0x71B1F0` | Identity and resolved payload byte `+0x20` gates; both clears, then `0x5341E0`. |
| `0x71B2BC` | `0x71B270` | Same pattern, payload byte `+0x24`. |
| `0x71B4CC` | `0x71B480` | Same pattern, payload byte `+0x30`. |
| `0x71B54C` | `0x71B500` | Same pattern, payload byte `+0x44`. |
| `0x71B5CE` | `0x71B580` | Identity gate, no corresponding byte gate; same three calls. |
| `0x76C3A8` | `0x76C330` | Boolean setter at receiver `+0x9A0`; guarded follow clear and PvP-disabled message. Likely restriction enforcement. |

Compact callbacks have stored code pointers at `0x2655FA8`, `0x2656098`, `0x2655F58`, `0x2655FF8`, `0x2656048`, respectively. Registration, event/property meanings and physical input mappings remain unknown. Restricted reference searches did not resolve constructors from guessed enclosing table starts. Do not label these keyboard, death, teleport or focus callbacks from their shape.

`0x5341E0` is a third operation: it clears receiver `+0x39C`, then tail-calls `0x697140(true)` through `0x697C90`. Its presence further argues against attributing all cancellation to the follow field alone.

## Existing runtime evidence and future tests

Supplied baselines document player/target readback, advancing-source checks and displacement observation. They contain no recorded successful native follow/C2M cancellation experiment. This pass adds static evidence only; it neither invokes addresses nor proposes field writes.

Future tests require a separate live-input assignment; none were executed or requested here:

1. Review actual movement/Follow bindings and a flat, empty scene. Qualify fresh player/target telemetry and a stationary baseline. Start follow through a visible standard Follow action or UI-confirmed `/follow` command, using a consenting nearby target. Static association alone does not certify slash syntax.
2. Prefer one shortest practical pulse of the client's **bound backward or strafe movement action**, followed by release. Manual movement has the strongest static cancellation lead; backward/strafe avoids deliberately advancing into the target. Confirm key/action mapping first. Keep a human ready with reviewed movement input; script deadline/key-up alone cannot stop a latched state.
3. Require advancing position samples to settle within a predeclared tolerance **while away from arrival**. Record the stopped-following message, but do not accept it alone. After candidate follow cancellation, a small controlled target move should not restart following. This distinguishes cancellation from reaching a stationary target.
4. Independently repeat against one already qualified native C2M destination, checking stable position before reaching it. A follow pass does not certify C2M. Only then consider obstacle trials.

Do not treat guessed `/stopfollow`, repeated `/follow`, Escape, controller pause, mouse-up, key-up, timeout, zone/PvP transitions, or native calls as verified stopping. The exact normal gesture that reliably halts both modes is the main unanswered question.

## Coverage, failures and validation

- First query hit the wrapper's 40-region cap with 8 queued items. Focused 11-region input follow-up completed with no pending queue; it does not close every original item. A one-region predicate check also completed. No persistent jobs remain.
- Broad unwind range `0x695810..0x6969EC` stops linear decoding at `0x696921`. Used switch/follow sites are earlier; complete control flow remains unresolved. No claim depends on decoding switch-table data as instructions.
- PE unwind chains are not guaranteed source-function boundaries. Linear decoding does not prove reachability. Indirect calls remain unresolved; direct-call candidate search caps at 64 per target.
- The `follow` getter lacks a PE unwind entry; only its exact eight bytes were decoded. Adjacent table command role remains inference. No RTTI/class conclusion for compact callbacks.
- Source hashes, target hash, captured region hashes, instruction bytes/decoding, table/string bytes and all 16 direct-call prefixes are checked by `tools/agents/follow/verify_follow.py`. Run using the existing interpreter with `-B` to suppress bytecode writes.
- Self-review: an initial verifier assertion caught a mistaken message-reference site (`0x534256` references `Info`). Corrected it to `0x534339`, which resolves to `0x2646388`, and reran successfully: 322 excerpts, 16 direct-call prefixes, 50 region hashes and four source hashes. JSON parsing and verifier syntax parsing passed.
- Delivery blocked at staging: `git add` could not create `C:/work/rre/.git/worktrees/rre-worker-follow/index.lock` (Permission denied). Shared Git metadata is outside this worker's writable boundary. No permission request or workaround was attempted; no commit SHA exists. Base commit: `c7815b762dbdfe4d681a96cd14a69f658668595c`. Only the three owned follow-lane files remain for manager review/staging. No push, process control, settings change, install or full import occurred.

Next static validation: map action IDs 2-7 to registered action names/bindings, and resolve `0x534990 -> 0x860530`. Next behavior validation: separately qualify the reviewed movement gesture for follow and C2M using advancing displacement evidence.


## Follow-up: 2026-10-19 / M2-002 ? normal input and cancellation order

This follow-up preserves the 2026-10-18 report above. **Numeric input actions 2?7, 9 and 10 call follow-clear `0x534200` before separate C2M-clear `0x534990` on their selected dispatch branches. The input update occurs before both clears and can return early while follow is active. None of this proves a physical stop.**

Build rechecked: SHA-256 `7c356c9dde9e12fcbff3c08d953b0630b48b1510a0ffb36e4ec164606e7b17bd`, preferred base `0x140000000`; every address below is an RVA. Worktree HEAD at start: `9375a276b861e46c2dd8f0bde528ee3353bc58bb`. The current manager roadmap/task board and navigation baselines were read. The machine summary is appended under `follow.json ? followUps[0]`; older findings and historical delivery status are retained.

### Directly observed native code

The event branch at `0x694315` resolves event `+0x124` through `0x7B20A0`, passing `(event+0x12C == 0)` as its third argument. It forwards the returned numeric action ID and the original byte at `+0x12C` into `0x695810` at `0x694377`. Another event path calls that dispatcher at `0x69478B` with forwarded byte zero. The resolver searches a tuple of event code and two modifier-like fields and returns entry `+0x14` or `-1`; it does not supply action names in these inspected regions. A concrete physical key or press/release polarity is therefore still unknown.

After the dispatcher's earlier gates reach its switch, table `0x6968A8` maps actions 2?7 into the following branches. Table `0x6968E4` maps their optional bit writes. These are numeric action IDs, not names or scan codes.

| Action ID | Primary branch | Input-object `+0xC` bit | Clear order |
| --- | --- | --- | --- |
| 2 | `0x695A58` | 4 | follow `0x695B0F`, C2M `0x695B17` |
| 3 | `0x695A58` | 5 | same pair |
| 4 | `0x695A68` | 3 | same pair |
| 5 | `0x695A68` | 2 | same pair |
| 6 | `0x695A68` | 6 | same pair |
| 7 | `0x695A68` | 7 | same pair |

For IDs 2/3, raw forwarded byte zero also clears receiver `+0x39C` (`0x695A61`); the nonzero branch skips that write. Both paths still converge on the clear pair. A virtual-predicate result captured at `0x6958E0..0x6958ED` can skip the bit-write/update block directly to `0x695B08`; it does not skip that pair. The two calls use the same saved receiver `[inputObject+0x10]`. They finish by marking event `+0x18` handled at `0x6967E3`. This marker is not a motion observation.

On the bit-write path, `0x697140(true)` at `0x695B03` runs **before** both clears. Its guard at `0x69716E..0x697199` checks receiver `+0xB60`; nonzero follow state sets `BL=1` and returns through `0x697634` before downstream mode selection/installation. Other guards call `0x562570` and `0x561BE0`, whose meanings were not qualified in this budget. Thus the input update call is not proof that a manual mode was installed, and there is no second update call between the two clears or their local jump to the handled marker.

| Other selected path | Order in native code | Qualification |
| --- | --- | --- |
| Action 9 | `0x572EF0` at `0x695B47` ? follow at `0x695B53` ? C2M at `0x695B5B` | Helper/action name unresolved. |
| Action 10 | `0x572D30` at `0x695B25` ? follow at `0x695B31` ? C2M at `0x695B39` | Helper toggles `+0x39C` and tail-calls input update before returning to the clear pair; autorun remains an inference. |
| Reconciliation `0x6969F0` | `0x697A40(false)` at `0x696A19` ? update at `0x696A26` ? conditional follow at `0x696A36` ? C2M at `0x696A3E` | Nonzero changed result gates the pair. |
| Destination replacement `0x562BC0` | follow at `0x562BD0` ? C2M at `0x562BD8` ? vector writes ? activation bit set | Clears old states before installing the new coordinate request. |

`0x697A40` queries action IDs 2, 3, 6, 7, 4, 5, 8 and 16 through `0x7B78C0`. Both set and clear transitions can mark its changed result (for example bit 4: `0x697B05/0x697B09` and `0x697B15/0x697B19`). `0x7B78C0` looks up an action-ID tree and tests binding-like records through untraced helpers. This strengthens the movement-action interpretation but does not prove a key-up-only cancellation handler. Stable state can return unchanged and skip the pair.

### C2M clear and its downstream handle cleanup

`0x534990` still operates on `[receiver+0xB90]`, independently of follow `receiver+0xB60`. If component `+0x70` is zero it skips handle work and still clears activation bit 0 of `+0x1A8`. Otherwise it copies the `+0x70/+0x78` handle/owner pair, with reference-count-like operations at `0x5349BE..0x5349C9`, then calls `0x494830` and `0x860530` at `0x5349DE/0x5349EB`. After return it conditionally releases the owner through `0x48CEA0`, zeros both component qwords at `0x534A0E/0x534A12`, and clears the activation bit at `0x534A29`. It does **not** erase the stored coordinate vector at `+0x60/+0x68`.

`0x860530` searches a tree rooted through its receiver `+0x38`, comparing node key `+0x20` with the copied handle. An exact match calls **`0x860370(handle, false)` at `0x86058A` before `0x85CAE0` at `0x8605A1`**. A missing key skips both. Both paths tail-call `0x4877D0` on the copied pair. Only the prefix of `0x85CAE0` was inspected, so removal/erase is an inference rather than an established contract.

`0x860370` iterates a child range at handle `+0x330..+0x338`, calls child virtual `+0x58` with a conditionally selected boolean, clears child `+0x11`, and resets that range's end. It then invokes virtual slot zero with argument 1 for non-null entries of a second range `+0x370..+0x378` and resets that end. These are concrete cleanup operations; the child types, virtual implementations, planner ownership and effect on ongoing player motion are unresolved. Passing false into the outer routine does not mean every child receives false.

### Inference, rejection and runtime boundary

The evidence supports a common normal input path that coordinates **two distinct state clears**, with additional handle cleanup on the C2M side. It does not support treating follow-clear alone as a combined stop operation. IDs 2?7 are movement-direction-like from their bit reconciliation and mode selection, but forward/back/turn/strafe names and current bindings remain unqualified. The earlier suggested backward/strafe trial therefore remains conditional on reviewing actual bindings.

Reject these promotions: raw byte zero equals a proven physical release; event handled equals stopped motion; downstream virtual cleanup equals proven path-job cancellation; cleared activation equals immediate braking; a stopped-follow message certifies C2M stopping. No runtime evidence was added. The supplied baseline documents available telemetry but no passing native follow/C2M cancellation test.

### Bounded coverage, evidence and verification

Exactly **25 unique PE unwind regions** were inspected in two depth-zero queries (14 + 11), with automatic unwind-chain expansion disabled and both queues drained. No further research region was decoded. Source hashes, exact commands' anchor lists, complete retained listings and coverage are reproducible from:

- [First query](../../tools/agents/follow/m2-002-static-20261019.json) and [selected continuations](../../tools/agents/follow/m2-002-continuations-20261019.json).
- [Machine summary](follow.json), appended `followUps[0]`: source/tool hashes, per-claim instruction RVAs, seven ordered call sequences, numeric mappings, failures and rejections.
- [M2-002 verifier](../../tools/agents/follow/verify_m2_002.py) and unchanged [prior verifier](../../tools/agents/follow/verify_follow.py), run with `C:\work\rre\.venv\Scripts\python.exe -B`.

The query reused the Manager's hardened read-only `C:\work\rre\tools\inspect-navigation-static.py` (SHA-256 `6b9fd1827194d380307fc109bd7b412ffb80a8b93154271f8b17d2cf41046a3c`), not the older worktree copy. Original helper SHA-256 remains `c62d729ea027c271c8b4113c927ab039ae760d6db20f479166e7769dd4891319`. Dependencies report pefile `2024.8.26`, Capstone `5.0.7`. No source/tool installation or environment change occurred.

Limitations/failures: `0x695810` linear decoding again ends at `0x696921`, before region end `0x6969EC`; all used action sites precede it. Resolver continuation `0x7B228D` ends decoding at `0x7B2544`, before `0x7B255C`; bytes from `0x7B24FC` are switch tables and were not treated as executable evidence. The resolver's return precedes them at `0x7B24F8`. `0x697C90` has no PE exception entry and was left unresolved without guessing a boundary. Accessor continuations, `0x85CAE0` beyond its prefix and virtual callees were excluded at the region budget. No new global caller enumeration was performed; this follow-up qualifies selected local paths and preserves the prior 16-site inventory. An attempted local lookup of `docs/agents/c2m.md` found it absent in this worktree; no out-of-lane writes followed.

Verification and delivery results are recorded below after execution. No live input, process access/control, native invocation, memory write, debugger, network action, full import, persistent job, main-tree change or out-of-lane change occurred.

Next concrete static validation is to resolve names/binding provenance for IDs 2?7 and identify the C2M handle's child virtual `+0x58` implementation. Future separately authorized behavior validation must test follow and C2M independently, away from arrival, using advancing displacement and no-resume evidence. The static evidence does not authorize that trial.
