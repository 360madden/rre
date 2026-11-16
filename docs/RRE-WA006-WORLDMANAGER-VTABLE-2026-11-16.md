# WA-006 — concrete native world-manager class attribution for candidate-container initializer caller

**Verified:** November 16, 2026, ~07:54 EST, AMD-DESKTOP, Workbridge 0.16.5-dev; independent `hostname.exe` exit 0. **Owner:** single RRE manager. **Scope:** original executable bytes only. **Status:** accepted *static RTTI/vtable attribution*, not WA-006 or WA-007 live acceptance.

## Exact original source

- Preserved offline PE: `artifacts/lab2-live-20261107-0922/guest-rift_x64.exe`, **60,493,640 bytes**, SHA-256 `1935a05c9db6d468e34e0055014a4a99c1b5afceb1695884e24600f5c20a4be8`; x64 image base `0x140000000`. No current process was opened.
- **New ownership discriminator:** `.rdata` QWORD at RVA **`0x278CA28`** points to `0x14008F230`. It is **vtable +0x18** of the separate **`0x278CA10`** vtable, not slot `+0xA8` of the adjacent `hkpKdTreeCollidableRaycaster` vtable at `0x278C980`.
- `0x278CA08` contains a Complete Object Locator (COL) pointer to **`0x2DF1B90`**. The exact 24-byte COL fields are `(signature=1, offset=0, cdOffset=0, type=0x2F99400, hierarchy=0x2DF1BB8, self=0x2DF1B90)`. The type descriptor at `0x2F99400+0x10` spells **`.?AVhkpKdTreeWorldManager@@`**. The next independent COL is at **`0x278CA30`**, bounding this four-QWORD vtable.
- The four table entries at `0x278CA10` are `0x8F1B8`, `0x71610`, `0x71614`, **`0x8F230`**. Thus original static RTTI identifies `0x8F230` as a **`hkpKdTreeWorldManager` virtual-method implementation at +0x18**. Whether that virtual method is invoked at runtime is unknown.
- Earlier independently verified function `0x8F230–0x8F37A` (330 bytes, SHA-256 `a97f396a877d5a35db5b39bb0d723ecb599c8f11e716bd6752bb98ba2e52a732`) saves incoming receiver in RBX, passes `[RBX+0x28]` **by address** at `0x8F2E2`, and calls `0x8F204` at `0x8F2F6`. These facts now have a class-associated vtable but are **still not a proved same-object link** to the separate query wrapper receiver at `0x8E744/0x8E7C5`.

### Source windows (RVA / size / SHA-256)

| Window | RVA | Bytes | SHA-256 |
| --- | --- | ---: | --- |
| WorldManager COL pointer | `0x278CA08` | 8 | `32f7bc0900cc025bab744085415efda6b3301a58c87c1321ea536c2e666b0d97` |
| Four-entry vtable | `0x278CA10` | 32 | `bc87a831fd7733e57b9898e026227a0545aa5d4cf5fdfeed5916b2123e2a40a5` |
| Next COL boundary | `0x278CA30` | 8 | `e63b8707f806c53d592f8aa8258b95624fedfc200e0d7aee24ac6c74244240d3` |
| WorldManager COL | `0x2DF1B90` | 24 | `a74addbbf6d79ba3e861159f59fe41fc93c920c955df80c8b4b80695cfb28c3f` |
| WorldManager type descriptor | `0x2F99400` | 44 | `8c8b693c12f41b14f4accc1d1539fe0d259ce34bbfe7d42a5d85040759cc5068` |
| Member-associated method | `0x8F230` | 330 | `a97f396a877d5a35db5b39bb0d723ecb599c8f11e716bd6752bb98ba2e52a732` |

## Independent checks and rejection controls

1. PEfile/Capstone bounded original-byte check `rre-hour11-caller-8f230-20261116` **exit 0**: 0 direct `E8` candidates to `0x8F230` across executable `.text`; direct-call absence **does not** exclude virtual or indirect invocation.
2. Independent direct-target positive controls `rre-hour11-8f230-pointer-control-20261116` **exit 0**: `0x8F204` has the known single `E8` call at `0x8F2F6`; `0xD088C` has the two known calls at `0x8EADB`/`0x8ED93`. An exact absolute pointer lookup finds `0x8F230` **once** in `.rdata`, at `0x278CA28`; no direct `E8` caller was asserted.
3. Source-checked vtable inventory `rre-hour11-vtable-8f230-20261116` and RTTI decode `rre-hour11-8f230-rtti-20261116`, both **exit 0**. This explicitly separates several adjacent interior COLs. The original visitor's first 64 bytes retain independent SHA `dea4f646f9944c1acf36b364687f96ff2e5476e2414c19197247067f08d9606f`.
4. **Independent standard-library-only PE parser** `rre-hour11-8f230-stdlib-independent-20261116`, **exit 0**: validates exact PE/source hashes, COL, vtable pointer and boundaries, and **rejects all 3 in-memory mutations** to COL type reference, method pointer and type-name bytes. No executable, source code or installed addon was altered.

## Confidence boundary and task gates

**Qualified:** `0x8F230` has a source-hashed `hkpKdTreeWorldManager` vtable/class association, a concrete `+0x18` table slot, and the previously qualified local receiver+`0x28` container output relationship. **Not qualified:** actual virtual dispatch, `0x8E744` query-receiver identity, dynamic candidate-object virtual `+0x40`, record field writers, physics/gameplay collision owner, current player, physical hit/miss, or same-epoch nonself IDs. Nearby RTTI does not establish an owner for `[R8]`. **WA-006 and WA-007 remain blocked.** ROOT-001 live ownership unqualified; RC-30/RC-88 operator-stopped; SC-103/SC-306 blocked; SC-604 interim-only.

**Next discriminator:** an independent exact-build constructor/vptr assignment or actual dispatch/call chain connecting **the WorldManager receiver** to the **separate query wrapper receiver**. Do **not** infer sameness from `+0x28` layout alone; park this branch if no new caller/assignment evidence exists. The RRE-owned RR2 discovery feed stays unchanged; no player-owner result warrants promotion. No VM/game/process/input/reload/deployment/cross-repository/remote action occurred.
