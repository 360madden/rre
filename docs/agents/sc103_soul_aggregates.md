# SC-103 — LEGION Soul Tree aggregate path (two offline PE probes)

**2026-11-10, 11:22 EST.** Bounded static analysis only; no game process, VM, input, REA/Ghidra import, installation or source-code change.

## Exact source

- Verified physical LEGION `C:\Program Files (x86)\Glyph\Games\RIFT\Live\rift_x64.exe`: **60,493,640 bytes**, SHA-256 `1935a05c9db6d468e34e0055014a4a99c1b5afceb1695884e24600f5c20a4be8`.
- Probe jobs `rre-sc103-legion-soul-probe1-20261110-01` and `rre-sc103-legion-soul-probe2-20261110-01`, both exit **0**, using installed RRE virtualenv pefile/Capstone and only bounded RVA windows. No third native/source probe was run.

## Directly observed code (matching PE)

1. Vtable RVA `0x2704798` slot 12 (entry RVA `0x27047F8`) contains VA `0x140EAB4D0`, method RVA `0xEAB4D0`. Installation instructions at `0xE8A9A3` and `0xE8B6AA` compute this same table and store the pointer in an object vptr. That verifies virtual dispatch/table installation, **not** a particular Soul-entry object identity.
2. Method `0xEAB4D0` has unwind span `[0xEAB4D0,0xEAB5DB)`. It invokes virtual slots at vptr offsets `+0xB8` and `+0xC0` before dirty-state handling. Conditional branch `cmp byte ptr [rdi+0x255],0` at `0xEAB53A` skips a rebuild when zero; if nonzero, call at `0xEAB543` reaches `0xEAB7D0`, call at `0xEAB54E` reaches `0xEA2ED0`, then `0xEAB553` clears byte `[rdi+0x255]` and `0xEAB55A` clears `[rdi+0x2F2]`. This is source-qualified conditional update/rebuild behavior; a *selection callback* is not established.
3. Pre-rebuild helper `0xEAB7D0` has unwind span `[0xEAB7D0,0xEAB860)`. It zeroes DWORD totals at object offsets `+0x26C` and `+0x300`, uses an intrusive-list sentinel at object `+0x278` with initial cursor from `[object+0x288]`, and iterates nodes until sentinel equality. The loop adds `[node+0xE8]` to `[object+0x26C]` and `[node+0xF4]` to `[object+0x300]`; cursor advancement uses call RVA `0x1294774`.
4. After accumulation, native arithmetic is exactly `object[+0x268] = object[+0x264] + object[+0x260] - object[+0x26C]` and `object[+0x2FC] = object[+0x2F8] + object[+0x2F4] - object[+0x300]` (DWORD operations at RVAs `0xEAB825..0xEAB849`). Two residual channels are directly evidenced; labels such as selected Soul, ability ID, point spending or Legendary counter **remain inferred/unverified**.
5. Method `0xEA2ED0` begins with generic global/interface lookups and a large frame; the sampled entry region did not yield a verified Soul-entry identity parameter. The `0xEA2F80` decode window began mid-instruction and is **discarded**, not used as evidence.

## Decision

**New confirmed:** class-level conditional refresh plus two list-aggregate/residual channels. **Unresolved:** which list node corresponds to which Soul/Legendary entry, whether an exact ability ID exists in its state, and whether any method here is the user selection callback. The two probe limit was exhausted; no broad native import, scan or speculative ID assignment followed.

Next discriminating evidence needs an independently tied node identity field and an actual selection callback or role-bound runtime comparison; this call path alone cannot identify Protector's Fury Normal versus Legendary.
