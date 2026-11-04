# Provisional SC-402 cross-project static lead — constructor +0x88 byte reset (2026-11-04)

**Status:** Independently reproduced **local native control/dataflow**, not accepted gameplay semantics. **Owner:** RRE research manager, documentation-only. **Source owner:** REA-Lab1 (read-only to RRE). **Related parked RRE task:** SC-402, unchanged; this note does not reopen or complete it.

## Exact source identity and provenance

- Physical RIFT Live x64 on-disk PE: 60,493,640 bytes; SHA-256 `1935a05c9db6d468e34e0055014a4a99c1b5afceb1695884e24600f5c20a4be8`.
- Original PE `.text` RVA `0x675220` maps to file offset `0x674620`. Source is the matching physical/current-build executable; this does **not** establish a current RIFT process or character session.
- Related REA-Lab1 source: `C:\work\REA-Lab1\NATIVE-L1-030.md`, observed untracked on `main` at HEAD `7784c316`; report-file SHA-256 `62e806ade7c4609bb1145e766524818249fb7e5db9603fe157b42787e125d1dd`. **Uncommitted source:** this is a provisional cross-repository reference, not an accepted immutable Lab1 source revision.
- Two independent read-only analyst passes decoded the original PE with different disassembly routes (one bounded in-memory objdump pass; one Capstone pass using the existing RRE Python environment). The second independently rechecked full PE size/SHA and the decisive register/branch/alias path. No saved binary, process attachment, game input, VM interaction, or repository edits were required for those passes.

## Reproduced local instruction and alias sequence

| RVA | Exact instruction/branch | Supported narrow conclusion |
| --- | --- | --- |
| `0x67522C` | `xor r14d, r14d` | R14 becomes zero |
| `0x67523A`, `0x675241`, `0x675255` | `mov r15d,r14d`; `neg r15`; `sar r15,4` | R15 remains zero |
| `0x675259` | `mov qword ptr [rcx+0x30],r14` | Stores zero at object +0x30 |
| `0x675265` | `mov byte ptr [rcx+0x88],1` | First byte write is **1** |
| `0x67526C`, `0x675270` | `cmp r15,4`; `jae 0x675316` | With R15=0, the unsigned-above/equal branch is **not** taken |
| `0x675279`, `0x67527D` | `lea r13,[rcx+0x48]`; `lea r12,[r13+0x40]` | R12 aliases the exact address `rcx+0x88` |
| `0x675285` | `mov byte ptr [r12],r14b` | On this normal path **overwrites that same byte with 0** |
| `0x675289`–`0x675290` | `mov rsi,[rcx+0x30]`; `test rsi,rsi`; `je 0x675303` | Zero-initialized value makes the jump **taken**, bypassing the intervening conditional path |

**Exact claim:** In the normal uninterrupted instruction path entering at `0x675220` with writable object memory, `[rcx+0x88]` is first written as 1 and then deterministically overwritten as 0 before the `0x675290` branch. This corrects an interpretation of the earlier `write 1` as a persistent initialized value; it does **not** prove the field's value at all later returns/calls.

## Negative result, uncertainty, and stop rule

A bounded original-byte `E8 rel32` target search across RVA `0x665000–0x685000` (128 KiB, 32 consecutive 4-KiB segments, consistent source version) found **zero direct calls to `0x675210` inside that particular window**. The search is *not* a whole-`.text` xref inventory; indirect and out-of-window callers remain unknown. No full-program import or unbounded scan was attempted.

The tooltip routine's **dword** comparison `[object+0x88]==5` (REA-Lab1 `NATIVE-L1-008.md`) must not be equated with this constructor's **byte** `+0x88` solely because the numeric offsets coincide. Nor is the object proven to alias Path-A's `+0x848` member or an ability/queue manager. G0 original-byte identity and narrow local G3 flow are supported; live G2 gameplay identity and G4 cast/effect mechanism are **not**.

## Next useful verification

1. Let the **REA-Lab1 owner** first preserve/correct its own untracked NATIVE-L1-030 report, including transient `1 → 0` semantics and source SHA. Do not modify that repo from RRE.
2. If an already available indexed-xref route can enumerate constructor callers without a broad import, examine at most eight qualified call sites and allocation/receiver provenance; otherwise park this lead.
3. Promote to RRE SC-402 only when original source is stable, an independent object/alias proof is reproduced and linked to one specifically needed readiness/casting question. Until then preserve the task's parked state.

**No runtime action:** This note supplies source-exact static analysis only, no permission for RIFT input, attach, addon deployment or runtime modification.
