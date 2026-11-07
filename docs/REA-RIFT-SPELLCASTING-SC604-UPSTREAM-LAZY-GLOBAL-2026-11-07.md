# SC-604 — upstream lazy global-pointer initialization (November 7, 2026, ~06:15 EST)

**Owner / scope:** single RRE manager; one bounded offline, read-only qualification of the *physical-PC* RIFT executable. **Verdict:** helper `0x1339EC0`, called by the previously characterized `0x1333200` slot-address getter, reads and conditionally initializes a distinct global pointer at RVA **`0x33E0BE0`**. It is not a literal ability-ID accessor. Object type, real runtime execution, and the meaning of any downstream discriminators remain unknown.

## Exact build and independent methods

Original: `C:\Program Files (x86)\Glyph\Games\RIFT\Live\rift_x64.exe`; **60,493,640 bytes**; SHA-256 **`1935a05c9db6d468e34e0055014a4a99c1b5afceb1695884e24600f5c20a4be8`**. Both jobs independently rehashed the original file. RVAs apply to this on-disk build only, not the VM clients or a current game process.

- `rre_20261107_0620_sc604_1339ec0_disasm_ro` (exit 0): existing RRE venv, `pefile` and Capstone; decoded the bounded `0x1339EC0–0x1339FB6` function plus the call in `0x1333200`.
- `rre_20261107_0624_sc604_1339ec0_stdlib_ro` (exit 0): independent standard-library PE/section parser and direct source-byte/signed-displacement checks; **47/47 assertions passed**, including size/hash, instruction bytes, nine rel32 call targets, four separate RIP-relative accesses resolving to `0x33E0BE0`, and two negative controls (one-byte misalignment and a modified copy). Both logs untruncated. No project test file or binary changed.
- `rre_20261107_0624_freebuff_capability_ro` (exit 0): adapter `--check` only; no model ran. Existing modes `sc103/rc30`, `sc306/sc503`, `slots/file`, `operator/ability` cover previously reviewed, unchanged prompts; they do not offer a new scoped review of this helper. **Independent reasoning agents: zero**; Workbridge commands are not model agents.

## Qualified static data flow

| RVA | Original-byte observation | Narrow conclusion |
| --- | --- | --- |
| `0x1339EC4`, `0x1339ECE` | `mov rax,[rip+0x20A6D15]`; `jne 0x1339FB2` after zero test | Nonzero `[0x33E0BE0]` takes a fast return path with its loaded pointer. |
| `0x1339EDE`, `0x1339EE9` | Direct calls to `0x129B744` then `0x3C310` | Precedes a second global-slot check; synchronization intent is **not established**. |
| `0x1339EEE`, `0x1339EF8` | Load `rbx` from the **same** `0x33E0BE0`; branch if nonzero | A second check can skip the allocation path. |
| `0x1339EFE–0x1339F53` | Conditional `0x10`-byte allocations and pointer/function-pointer stores; calls to `0x129B69C` | Constructs a candidate nested pointer arrangement; actual class/ownership not established. |
| `0x1339F56–0x1339F86` | `0x50`-byte allocation, five 16-byte zero stores when nonnull, call to `0x12746C8` | There is a statically reachable zero-initialized candidate setup, **not** proof the object exists at runtime. |
| `0x1339F8F`, `0x1339FA6` | Two `mov [rip+disp32],rbx` instructions | Both stores address **the same global RVA `0x33E0BE0`** on their respective paths. |
| `0x1339F99–0x1339FB6` | Call to `0x3C320`, move `rbx` to `rax`, return | Slow path returns the current candidate pointer; cleanup-helper semantics are unverified. |
| `0x1333210` | Direct call `0x1339EC0` inside the downstream getter | Statically establishes an upstream call relation to the prior `0x1333200` analysis. |

The global `0x33E0BE0` is in the **virtual-only tail of `.data`**, with no initialized on-disk QWORD. Do not treat the image's implied zero-fill as a read of running RIFT memory. This upstream global is **different** from the downstream pointer slot `0x33E0AB0` returned *by address* from `0x1333200`; the intermediate `0x12748C8` and indirect dispatch still prevent a definitive same-object/type claim. See [prior pointer-slot proof](REA-RIFT-SPELLCASTING-SC604-GLOBAL-SLOT-ROOT-2026-11-07.md) and [indirect discriminator boundaries](REA-RIFT-SPELLCASTING-SC604-INDIRECT-DISCRIMINATOR-2026-11-07.md).

## Evidence ceiling and next action

This is one new **static** link in the upstream initialization chain. No ability identity, Legendary/Protector's Fury selection, queue enum, executed dispatch, cast completion, server acceptance, actual lock semantics or live reference count is proven. **SC-604 remains interim; SC-103/SC-306 blocked.** The historical **RC-30 v0.4.10 same-trial** Pin → Undo (before Reload UI) → restored baseline → Reload UI + matching SavedVariables receipt remains incomplete despite later qualified v0.4.11 load/persistence; RC-32 physical Retry remains unverified.

Further native work should require a genuinely new source-qualified question around `0x12748C8` or an actual concrete indirect dispatch target, with RR2/REA ownership checked first. Do not repeat the prior source-hashed upstream/static proofs merely to fill a lane. No game input/reload, process manipulation, installed-addon/SavedVariables write, desktop quarantine bypass, other repo edit, dependencies or push occurred.
