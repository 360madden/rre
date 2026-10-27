# SC-305 — Native RIFT ability-queue setting, local PC

**October 27, 2026 — REA source-backed native setting discovery.** This research used the RIFT installation and active process on the **physical PC**, not VMware. The setting field and current raw value are qualified; **Full/Short/None enum mapping and actual spell-queue behavior remain unknown**.

## Source identity and reproducibility

- Local executable: `C:\Program Files (x86)\Glyph\Games\RIFT\Live\rift_x64.exe`
- PE SHA-256: `1935a05c9db6d468e34e0055014a4a99c1b5afceb1695884e24600f5c20a4be8`.
- Recorded local running RIFT process: PID **66436**, module image base **`0x7FF720420000`**. These are **volatile observation identifiers**, not persistent pointers.
- [Machine-readable native and runtime receipt](REA-RIFT-SPELLCASTING-SC305-QUEUE-FIELD-2026-10-27.json), source-hash guarded.
- Local executable bytes, native instruction fields, and five selected **loaded process instructions** matched byte-for-byte. No debugger or special privilege escalation, no injection, memory writes or game inputs; a standard **PROCESS_QUERY_LIMITED_INFORMATION | PROCESS_VM_READ** handle was used briefly.

## Directly observed source-code relationship

New-build literal `ActionBars_AbilityQueue` resides in `.rdata` at **RVA `0x26ecc70`**.

| Evidence | Instruction RVA | Source instruction | Meaning supported |
| --- | --- | --- | --- |
| Compare setting key | `0xbd2d6f` | `lea rcx,[rip + 0x1b19efa]` | References the exact literal |
| Match parsed setting name | `0xbd2d97` | `lea rdx,[rip + 0x1b19ed2]` | Same name passed into a comparison/check path |
| Load settings object | `0xbd2da7` | `mov rcx,[rip + 0x27c2b12]` | Global pointer RVA **`0x33958c0`** |
| Compare and store | `0xbd2dae` / `0xbd2dba` | `cmp ebx,[rcx+0xa4]` / `mov [rcx+0xa4],ebx` | This setting maps to a **32-bit field at object offset `+0xA4`** |
| Mark settings updated | `0xbd2dc0` onward | reads `[rcx+0x19]`, sets bit 7 and writes back | Setting change-tracking likely; bit semantics not independently verified |
| Read same field elsewhere | `0xbd7153` | `mov ebx,[rax+0xa4]` | Another client routine consumes the same field |
| Reference UI/key name | `0xbd71a2` | `lea rdx,[rip+0x1b15ac7]` | The latter routine also references `ActionBars_AbilityQueue` |

The two containing function ranges are independently grounded in the new executable's `.pdata` records:

- Source RVA **`0xbd2b70–0xbd3179`**, SHA-256 `1572b1bb9ef05d57d07b028b165d426753484bd877b14ef96b2b2107722d2679`.
- Source RVA **`0xbd6732–0xbd7f84`**, SHA-256 `7ca055f421ed13d08083d6196ee7c23d1055555e307ec14c7bfe59e2acc056f4`.

The second function copies `[rax+0xA4]` into `ebx`, references the setting literal, later passes `ebx` to another helper; this supports **settings UI/serialization**, not proof of the runtime spell queue implementation.

## Actual local runtime reading

A bounded read-only Windows API observation used the local module base + RVA **`0x33958c0`** to read the **8-byte settings-object pointer** and then read only four bytes from its `+0xA4` field:

**Raw observed unsigned 32-bit value: `1`.**

That value is **not yet assigned to Full, Short, or None**. No source-backed enum labels/values, UI screenshots showing the current queue selection, or controlled setting contrasts have been correlated. The setting may change during the session.

Five loaded instructions at RVAs `0xbd2d6f`, `0xbd2dba`, `0xbd71a2`, `0xbd7153`, and `0x9b0567` matched the disk bytes from this exact executable. This validates the local process code-byte association for the *sampled* regions only, not every loaded page.

## Negative finding: original SC-401 API name lead

The earlier ability API descriptor candidate (`0x9b0376–0x9b0776`) calls helpers that behave like **generic container allocation/manipulation**. In this turn:

- `0x12942a0` was observed as a two-instruction register-move + tail jump to `0x78e110`, without its own `.pdata` entry.
- `0x58c650` recursively traverses `[rdx+0x10]` and `[rdx+0x18]` and passes `0x30` as a node size to a helper at `0x12942a8`.
- `0x16894e0` stores a returned pointer in a bounded growable-buffer-style structure; `0x16893b0` handles a value in the same buffer style.
- Nearby `.data` global words at `0x2f62d10`/`0x2f62d18` refer to sentinel `0x2f62d00`, compatible with a data-structure registry.

**Conclusion:** API names currently lead to descriptor/registration-style machinery, **not yet an identifiable native enumeration handler**. After two non-decisive approaches, park this lead until a new handler-callback/value-flow trigger arises. Do not spend another long session recursively decompiling generic utilities.

## Next useful work

**SC-306**: qualify the **enum mapping for `1`** and whether it changes with the user's actual local queue UI choice, preferably from existing client UI resources or an independently reviewed current local settings screenshot. No assumption that `1` means Full, Short or None. **SC3 remains active**, because queue settings discovery does not measure shared global cooldown, accepted queue requests, cast start times, or true server RTT.

Later native research can trace **readers of the offset `+0xA4`** outside the setting UI path and link it to actual input admission. Prioritize real consumer code over repeated schema registration strings.

SC-305 is a **native settings-field subtask completion**, *not a completion of SC3 or SC4 phase*.

## Workbridge evidence IDs

`rea-localpc-queue-setting-riprefs-20261027-01` • `rea-localpc-queue-function-context-20261027-01` • `rea-localpc-abilityqueue-current-field-read-20261027-01` • `rea-localpc-code-memory-match-20261027-01` (exit 0). Config search `rea-localpc-queue-config-scan-20261027-01` found no matching `.cfg/.ini` entry in limited directories; that negative search does not prove a setting file is absent globally. No game input, code modifications or memory writes were issued.
