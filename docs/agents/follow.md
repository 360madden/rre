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
