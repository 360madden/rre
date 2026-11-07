# SC-624 — Type51 getter is descriptor initialization; C9 remains unnamed

**Accepted bounded negative finding.** The known type51 method atRVA0x1899BF0 forwards to a lazy in-place type-descriptor getter. It is not a getter for record+0xC9 and supplies no semantic name for that byte. The C9 interpretation route is parked after two probes; learned/unlocked/owned/usable/role/restart meanings remain unknown. [Exact source/window/mapping/deviation receipt](REA-RIFT-TYPE51-LIST-DISCRIMINATOR-2026-11-07.json).

## Matching source and direct bytes

Only the retained Lab2 PE was read:60493640bytes, SHA1935a05c9db6d468e34e0055014a4a99c1b5afceb1695884e24600f5c20a4be8, preferred base0x140000000. No game process or VM was operated. The pinned F414 reader source names the byte only`ApiListFilterNonzeroRaw`. [SC614](REA-RIFT-SPELLCASTING-SC614-NATIVE-API-LIST-2026-11-07.md) established54nonzero records matching both54-ID API Lists among134typed records; that cohort agreement remains the full runtime semantic scope.

| Known window | Direct observation |
| --- | --- |
| RVA0x1899BF0,5bytes | `E9 DB 6D 01 00`, jump toVA0x1418B09D0 |
| RVA0x18B09D0,156bytes | TLS guard; normal return of the addressRVA0x344A6B0; slow path initializes descriptor storage, installs descriptor-vtableRVA0x28A9C38, returns its address |
| Object vtableRVA0x28A08C0,128bytes | slot+0x40points toVA0x141899BF0 |
| Descriptor vtableRVA0x28A9C38,128bytes | slot+0x08points toVA0x1418C06C0 |

The decoded156-byte getter contains no memory operand with displacement0xC9 and does not dereference a type51 record. It returns a type-description object, not an ability eligibility value. These four windows total417file-backed bytes and were independently hash-checked with the existing local PE/Capstone stack. Exact instructions and hashes are retained in the receipt.

## Mapping QA correction: the descriptor storage is not file-backed

The initial agent and manager extraction both accepted `pefile.get_offset_from_rva(0x344A6B0)` arithmetic and read128bytes from fileoffset0x3448CB0. **That slice is not mapped descriptor data.** Header QA showed:

- `.data` starts atRVA0x2F56000.
- VirtualSize0x695660; SizeOfRawData0x40BC00.
- Descriptor delta0x4F46B0 is beyond the raw-data boundary.

Microsoft's [PE section specification](https://learn.microsoft.com/en-us/windows/win32/debug/pe-format#section-table-section-headers) defines the excess virtual tail as zero-filled when loaded. The getter then performs runtime initialization of the in-place descriptor. Raw PE file-offset arithmetic beyond that section's raw bytes cannot recover the initialized descriptor or its field names.

The original extraction/incorrect mapping receipt and128-byte file slice are preserved as negative evidence, with an explicit [mapping-audit correction](../artifacts/sc624-type51-bounded-20261107-1435/mapping-audit.json). Their hash`26e1e0...` must not be cited as bytes at descriptorRVA0x344A6B0. No C9 absence or name claim is derived from those invalidly mapped bytes. This correction does not change the valid417-byte code/vtable findings.

## Probe limit and import deviation

The first delegated request opened the raw PE in REA/Ghidra and asked for functionVA0x141899BF0. Despite the single-function selector, this invoked the provider's full-program import/default auto-analysis prerequisite without the manager's explicit approval, contrary to the repository rule. It returned no useful result and was terminated after approximately124seconds (Codex cell`g108:167`, termination`Script terminated`, no REA evidence/operation ID). It was not retried or broadened.

The agent then closed the target; REA reported open=false, no observed analysis/providers, no binding or registered run. A separate root OS check found no java.exe/javaw.exe at19:32:50Z. The second probe used only bounded local byte windows and PE metadata; the mapping QA is validation of that same probe. [AGENTS.md](../AGENTS.md) now explicitly warns that a focused raw-PE REA function query can trigger the forbidden full-import prerequisite.

This is recorded as a deviation, not a successful analysis or an authorized import. No game input, live memory read, AI-worker CLI, shared dependency change or external source write occurred.

## Decision-changing next evidence

Do not repeat the parked List-registration trace or this descriptor getter. A future step needs either a schema/serialization/type name tied specifically to object offset0xC9, or a controlled observation that independently changes one candidate classification while reading C9 and API List together. Until then, use **raw API-list discriminator for the observed cohort**. A label such as learned, locked, visible or owned would exceed the evidence.
