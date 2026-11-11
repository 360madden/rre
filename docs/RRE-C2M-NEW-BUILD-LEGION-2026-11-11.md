# RC-56 — New-build click-to-move setter/consumer requalification (LEGION, 2026-11-11)

**Accepted static result:** Two targeted, read-only exact-byte probes locate the historical C2M **destination setter** and the **destination consumer entry** in the current physical LEGION `rift_x64.exe` build. The setter's destination-state writes and the consumer's activation-bit read are preserved. This is **not** a live movement test.

## Build and scope

- Current original executable: `C:\Program Files (x86)\Glyph\Games\RIFT\Live\rift_x64.exe`
- Original-file SHA-256: `1935a05c9db6d468e34e0055014a4a99c1b5afceb1695884e24600f5c20a4be8`. Historical C2M report SHA: `7c356c9dde9e12fcbff3c08d953b0630b48b1510a0ffb36e4ec164606e7b17bd`.
- Method: recheck full binary SHA, find **one exact old source instruction sequence** for each of setter/consumer in the new PE, use full `.pdata` unwind region boundaries and Capstone to verify code bytes. All addresses below are **RVAs** relative to preferred image base `0x140000000`. Do not use as absolute live pointers.

| Relationship | Historical old RVA | Current new RVA | Qualification |
|---|---:|---:|---|
| Destination setter | `0x562BC0` | **`0x5749C0`** | Unique 20-byte signature and 88-byte complete unwind-region decode |
| Destination consumer entry | `0x5765D0` | **`0x588420`** | Unique 14-byte signature and 135-byte complete selected unwind-region decode |
| Follow-clear call target | `0x534200` | `0x5460A0` | Current setter direct call |
| Parallel state-clear call target | `0x534990` | `0x546830` | Current setter direct call |

## Setter and consumer original-code evidence

- At `0x5749D0` (`e8cb16fdff`) and `0x5749D8` (`e8531efdff`) the setter directly calls `0x5460A0` and `0x546830`.
- `0x5749E1` (`4c8b87900b0000`) reads a component pointer at receiver `+0xB90`.
- `0x5749E8` (`f2410f114060`) copies the first two destination components into state `+0x60`; `0x5749F6` (`41894068`) stores the third at `+0x68`.
- `0x574A01` (`0fb681a8010000`), `0x574A08` (`0fbae800`), and `0x574A0C` (`8881a8010000`) read/set/write **bit 0** in state `+0x1A8`.
- The consumer region begins `0x588420`. It checks a follow-like receiver field `+0xB60` at `0x588447`, loads component `+0xB90` at `0x588454`, and checks state `+0x1A8` bit 0 at `0x58845B`. This is only the **entry region**, not full subsequent consumer behavior.

Exact reproduced window SHA-256:
- Setter `[0x5749C0,0x574A18)` = `e6427f87b5f3f2a407bd742142181cffe82125a2b9943b80a690b8aa374d6075`; 21 instructions.
- Consumer entry `[0x588420,0x5884A7)` = `2b57dcbdb4c7a84f243a5ba8ad35f5b1988f4135c1401158a8e9b7cee8e3ec26`; 32 instructions.

The manager independently re-read the SHA-checked original file and re-verified **both complete selected windows (53 instructions)** in `rre-rc56-native-independent-window-verify-20261111` (exit0). The two bounded discovery jobs `rre-rc56-native-c2m-samebytes-20261111` and `rre-rc56-native-c2m-setter-consumer-20261111` both exit0. Original byte signatures, window hashes, job IDs and machine interpretation are recorded in [the companion JSON](RRE-C2M-NEW-BUILD-LEGION-2026-11-11.json).

## What this does and does not establish

**Established for the current SHA:** the same static destination setter/activation-state relationship and the consumer's matching bit check can be found on the changed executable. Direct clear-call targets are requalified. This upgrades the old-build C2M code layout from merely historical to a narrowed **current-build static candidate**.

**Not established:** the current-build game-event callback and its registration, screen-to-world segment query, current player's ownership of this receiver, runtime object value, type-7 route handler linkage, an actual movement request, successful movement, stop/cancel, or obstacles. A static bit test is not a gameplay proof; do not call a native routine or write these fields.

**Stop condition honored:** exactly two discriminating searches were performed; no broad string/Xref sweep or full REA/Ghidra import. No RIFT input, process attach, VM access, external repo modification, deployment or restart.

### Next ranked actions

1. Requalify the **event callback→setter** direct caller on the current build with one exact call-site and surrounding source-byte proof; stop if ownership remains ambiguous.
2. Inspect a minimal continuation beyond the consumer entry only to determine whether the destination-distance/near-stop behavior persists, not to reimplement routing.
3. Later, correlate against a genuinely session-bound RIFT player XYZ + operator-controlled movement/stop observation; static evidence alone cannot complete NAV-002.
