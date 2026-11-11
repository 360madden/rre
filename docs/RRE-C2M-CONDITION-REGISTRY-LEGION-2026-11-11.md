# RC-61 — Lazy native condition registry and composite stateful predicates (LEGION, November 11, 2026)

**Static breakthrough:** The RC-60 event-7 transition detector gets its indexed-condition source from a **lazily initialized global pointer**, and those indexed records carry **composite condition tuples evaluated through a stateful native helper**. This advances the producer/ownership chain, without identifying any numeric condition as a physical keyboard, mouse, or game action.

## Host and evidence boundary

- Independently verified **LEGION**, repository `C:\work\rre`, installed physical RIFT `C:\Program Files (x86)\Glyph\Games\RIFT\Live\rift_x64.exe`, size 60,493,640 bytes and SHA256 `1935a05c9db6d468e34e0055014a4a99c1b5afceb1695884e24600f5c20a4be8`. Preferred PE image base `0x140000000`; all addresses are **static RVAs**.
- All four specified original-byte regions, **313/313 instructions**, independently rehashed and fully decoded by manager job `rre-rc61-manager-registry-predicate-independent-20261111-01`, exit 0. Additional manager PE-section/tuple-loop check `rre-rc61-manager-global-metadata-tuple-loop-20261111-01`, exit 0.
- Two independent read-only lanes used exactly two native-function probes each; no process attachment, debugger, memory write, game input, reload, addon install, VMware, AMD-DESKTOP, third-party repo write, broad scan, or remote push.

## 1. Condition source `0x6A9C10` — lazy global instance

The RC-60 event-7 gate calls `0x6A9C10` at `0x6A98DE`. Original source getter:

| Region (RVA) | Size / decode | SHA256 |
|---|---|---|
| `[0x6A9C10,0x6A9C24)` | 20 bytes / 4 instructions | `675e02151333724dcee64887c3c5a129dc9c73c27a46497677a19618376f73f9` |
| `[0x6A9C24,0x6A9CF8)` | 212 bytes / 50 instructions | `0ca1c71725d60beffc3a92b1537b0694823e8bb2f77a07b9b1134930f2196a0f` |

- `0x6A9C14 mov rax,[rip+0x2CC5C9D]` reads the global **RVA `0x336F8B8`**; `0x6A9C1B–1E` test and branch to return when nonzero.
- Otherwise, the remainder allocates using `0x78E110` with `0x10` and `0x60` requests, calls constructor **candidate `0x7C3920`** at `0x6A9CC8`, and stores the resulting pointer to the same global slot at `0x6A9CD0/0x6A9CE7`. Allocation identity and object type are not yet qualified.
- The global slot lies in the **virtual zero-fill** tail of PE `.data`: section RVA `0x2F56000`, virtual size `0x695660`, raw size `0x40BC00`; slot offset `0x4198B8` exceeds raw size. No original-file initializer pointer bytes are available. This supports a lazy runtime singleton without proving the runtime object's contents or role.

Read-only agent jobs `rre-rc61-condition-source-pdata-20261111-01`, `rre-rc61-condition-source-remainder-20261111-01`, `rre-rc61-condition-global-section-metadata-20261111-01`: **exit 0**.

## 2. Primitive record predicate `0x7C3C90`

Complete original unwind `[0x7C3C90,0x7C3D37)`, **167 bytes / 52 instructions**; SHA256 `327d8e2ade259baece6b5ebb441c723ce00fa29930f922503a2d46defe4bc699`.

- Called from RC-60's index evaluator `0x7C97E0` with a **three-int tuple**: EDX first, R8D second, R9D third. First field `-1` returns false (`0x7C3CB4/0x7C3CB7/0x7C3D20`). Second/third `-1` skip their check.
- First field values **4, 5, 6** select specialized `0x7C19D0` checks with respective arguments **4, 8, 16** (`0x7C3CBC–0x7C3CEA`). Other values select `0x7C1A00`; any supplied second/third field also uses `0x7C1A00`. Each returned boolean gates continuation to the next check.
- These are **composite conditions**, not a proven Win32 virtual-key table. `0x7C19D0`/`0x7C1A00` primitive semantics and record producer remain unknown.

Agent job `rre-rc61-evaluator-7c3c90-native-20261111-01`: **exit 0**.

## 3. Stateful record evaluator `0x7C98D0`

Complete original unwind `[0x7C98D0,0x7C9BD6)`, **774 bytes / 207 instructions**; SHA256 `6b7058cff85b3acb859e04139739c7f9a4191e63cc55e8652ff2f3fb9b8a6988`.

- It obtains an object via `0x7C991E mov rbx,[r15+0x58]` and performs concrete **float writes to `[rbx+0x68]`** at `0x7C9991` and alternate `0x7C99F1`. The meaning of this float is not qualified.
- Its loop at `0x7C9B2E–0x7C9B62` walks **12-byte records** from the supplied begin/end pointers. It passes each record's three dwords to `0x7C3C90` at `0x7C9B4D`, advances by `0x0C` on false, and sets `dil=1` at `0x7C9B62` when any matches. `0x7C9BA5 movzx eax,dil` returns that result; some buffer cleanup/reorganization follows the loop.
- **Important correction to simplistic models:** The RC-60 indexed query path can invoke a helper that **mutates its own native state**, not merely return a stateless read. Static float writes do **not** establish timeouts, movement velocity, a keypress mechanism, or gameplay effects.

Agent jobs `rre-rc61-evaluator-7c98d0-native-20261111-01` and `rre-rc61-evaluator-timing-tail-confirm-20261111-01`: **exit 0**.

## Practical impact and next gates

Evidence chain now: **lazy singleton → indexed ordered-tree record → up to three condition checks / stateful evaluation → cached transition flag → event-7 guarded same-receiver state clear**. This is verified static structure across bounded original source windows, **not proof that the chain belongs to the current player or represents a physical input/control**.

1. **P1 — Primitive meaning:** Qualify one small `0x7C19D0` or `0x7C1A00` function and its owner so the tuple's flags can be named from evidence, not inference.
2. **P2 — Record producer/owner:** Trace one bounded initialization path from `0x7C3920` or an actual indexed-record writer to determine source lifetime and identifier provenance.
3. **P3 — Live provenance:** Acquire separately authorized genuine v0.4.19 RRECollector navigation receipt, then test physical input→destination→actual stop under operator control. Until then, keep static and live claims separate.
