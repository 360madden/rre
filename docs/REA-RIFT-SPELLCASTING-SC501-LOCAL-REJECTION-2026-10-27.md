# SC-501 — Local RIFT cast-command rejection evidence (partial)

**October 27, 2026. Status: partial, not an accepted complete failure matrix.** Physical-PC installed `rift_x64.exe` SHA-256 `1935a05c9db6d468e34e0055014a4a99c1b5afceb1695884e24600f5c20a4be8`. Read-only REA research; no VM or game action.

The previously proven `/cast` code slice `0x6c7450–0x6c7b71` retains SHA-256 `31c02f4e68ac0c8157ad4e8fd1f813fe724b02f607d9c67649bcd777d0890d85`. A bounded Capstone RIP-relative string-operand scan of **only this source region** found six printable text references: three to `Console` at code RVAs `0x6c780a`, `0x6c7845`, `0x6c788f`, and three to `Could not cast unknown ability: [%ABILITY]` at `0x6c78b2`, `0x6c78dd`, `0x6c7922`. These original-byte references are source-backed and confirm the unknown-ability diagnostic branch already established in SC-407.

**No other printable static string directly referenced by RIP-relative memory operands in this bounded region identifies cooldown, insufficient resources, line of sight, target eligibility, or a server rejection reason.** This does **not** prove such guards are absent; they may be numeric/status codes, callee behavior, computed strings or server-side logic. The source confirms an **unknown ability error path**, not all possible cast restrictions.

**Next discriminating question:** correlate actual local-game observable refusal states to a **specific** verified cast input and code data-flow, rather than making up error categories from absence of strings. SC-501 remains partial; SC4 and SC5 are not newly completed. Preserve this work under a separate commit. Evidence job `rea-localpc-sc501-cast-error-literals-20261027-01` exited 0; no process attach, memory write or target input.
