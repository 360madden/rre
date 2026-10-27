# RIFT October 27 update — REA build qualification checkpoint

**Date:** October 27, 2026 (America/New_York). **Scope:** REA read-only research on the physical-host RIFT installation. RiftReader2 and Workbridge retain separate source/runtime ownership.

## Verified changed RIFT binary

| Measurement | Historical referenced build | Newly observed **host** build |
| --- | --- | --- |
| Executable | `C:\Program Files (x86)\Glyph\Games\RIFT\Live\rift_x64.exe` | Same path |
| SHA-256 | `7c356c9dde9e12fcbff3c08d953b0630b48b1510a0ffb36e4ec164606e7b17bd` | `1935a05c9db6d468e34e0055014a4a99c1b5afceb1695884e24600f5c20a4be8` |
| Length | 59,963,840 bytes | **60,493,640 bytes (+529,800)** |
| File last-write UTC | 2026-09-29 12:04 | **2026-10-27T10:56:49.6396025Z** |
| Static code attribution | Prior REA/RRE and October 26 RR2 observations | **Unqualified for native offsets and code behavior** |

The live **host installation** also has **14 files** with modification timestamps since 2026-10-26 00:00 UTC, including new/changed `Assets/assets.*` and `assets64*.manifest`. Only the host installation was inspected. The exact current RIFT **guest** executable hash is **unknown**.

The new host binary is a valid x64 PE (`Machine=0x8664`), preferred image base `0x140000000`, image size **63,164,416 bytes**, entry RVA `0x24e1a24`, seven sections. Full per-section source hashes, RVAs and byte sizes are saved in [the machine-readable build inventory](REA-RIFT-BUILD-INVENTORY-2026-10-27.json). Notably, new `.text` SHA-256 is `76e504d8f26ba7b01cb97bb9741efb158b15f4324d8db5ea094866d9a4884d7c`. We have **not** compared its original bytes against the previous `.text` section: the historical SHA for the whole old executable does not by itself quantify precisely which instructions changed.

VMware read-only running-list showed **one running VM**: `C:\rift modding\VMs\RIFT-Lab-2\RIFT-Lab.vmx`. This establishes neither the guest game build nor its casting behavior. Old RIFT-Lab-1 game process/PID and RR2 October 26 trial IDs must never be assumed current in Lab-2.

## Research impact / what not to invalidate

- **Retain accepted historical evidence unchanged:** 55-ID API inventory, original source hashes, exact-ID ranged dodge/hit, 1.5s and 12s observed effective cooldowns, and SC0/SC2 handoffs remain valid **for their original captured client**.
- **New-build native offsets are not accepted:** any PE RVAs, function signatures, xrefs, vtables, inferred pointer chains, static ABI or Ghidra instruction dossiers from the old executable require selected original-byte and caller-context requalification before use on the **new hash**. Never bulk search/replace the old pin inside historical reports or change RR2's expected hash to silence an identity mismatch.
- **API-level work can continue:** SC-304 can investigate precision limitations of previously saved traces **offline**, while new guest API/level/role samples await separate RiftReader2 source ownership and current build/session proof. Do not call a saved ability list "current" after an update.
- **Client/server update notes aren't a substitute for binary evidence:** official October 26 notices schedule Glyph platform maintenance October 27 and an October 28 update. This local October 27 binary mutation is independently confirmed; without a source-pinned release manifest, the exact change content is not attributed to either announcement.
- **REA installation:** installed REA 6.5.0/Ghidra 12.1.2 is unchanged and sufficient for the current offline investigation; no installer/tool update was needed or attempted.

## One focused requalification strategy

1. Keep the new SHA as a **separate build** in the REA task ledger, alongside the original historical reference, not as a rewrite of old findings.
2. Before native SC-401/402 work, identify an **actual** spellcasting-specific byte/string/API/event anchor from the new PE and compare original old bytes or qualified source metadata when available. Literal names are *leads*, not proven functions. Start with a small saved region and read-only existing REA/Ghidra functions; no default whole-client import (two earlier >450s attempts timed out).
3. Reverify API behavior separately on a fresh guest session through RR2's owner; the observed VM is Lab-2, whose exact game build is not known here. Do not send game inputs, bypass RR2 controls, or modify its deployment.
4. Proceed independently on **SC-304** precision/clock-domain analysis using previously verified immutable recordings. That analysis does not claim new executable compatibility.
5. Deliver one commit per stable evidence increment with full source hash, bounded job IDs, negative findings and short handoff.

**Evidence and verification:** exact host SHA and length measured by read-only PowerShell, recursive host file timestamps, running VM list, and Python `pefile` offline PE section/source hashes, all via Workbridge read-only commands. No executable or VM modified; no active RIFT process attached; no game inputs or Git push.

**Next task:** SC-304 historical measurement precision, then a selected (not broad) spellcasting-native compatibility probe once there is a source-backed hypothesis. No stage is considered requalified solely because the new EXE has been indexed.
