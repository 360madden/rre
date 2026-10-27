# SC-408 — local RIFT cast-command downstream probe (October 27, 2026)

**Result: bounded investigation completed, semantic answer unresolved.** Source is the physical-PC installed `rift_x64.exe`, SHA-256 `1935a05c9db6d468e34e0055014a4a99c1b5afceb1695884e24600f5c20a4be8`. The prior SC-407 cast entry `0x6c7450` is the verified starting point; do not relabel uncertain helpers as request submission. No VMware, gameplay input, source mutation or full Ghidra import.

## First selected branch

SC-407 `call 0x5a5ff0` at `0x6c752c`. Original PE `.pdata` bounds `0x5a5ff0–0x5a60ad` (189 bytes), SHA `b0a76bde02791107c0236013235a3ca63542dd86f3d3f45dbbf1f1877f03c073`. Bounded Capstone linear decode covered 42 instructions to the reported end. It has direct call `0x5a603e -> 0x521260` and several references into `.data` near `0x2f57290`, plus one to `.rdata` `0x26a4488`. The observed register moves and state references are not sufficient to establish ability-name/ID resolution or cast admission. **Classification: unresolved**, not a known ability lookup.

## Second selected branch

SC-407 `call 0x7de6f0` at `0x6c7a10`. A first attempted `.pdata` range assertion failed: **no matching runtime-function entry starts at the target**. A subsequent tightly bounded 192-byte read verified its opening bytes form a short wrapper: `mov rax,r8; mov rcx,rdx; movzx r8d, byte ptr [rsp+0x28]; mov rdx,rax; jmp 0x14137fc80`. Padding bytes `int3` separate it from the next routine starting at `0x7de710`. The **stub-only** conclusion is supported by these first instructions; there is **no proved function-body extent** for the following code. The 192-byte source slice SHA is `1e200856bcff965891f51629442962fd1d42fdc2b62efc28b66c1f36cbd44b93`. No evidence establishes the jump target as native cast dispatch; its semantics remain unknown.

## Stop decision and resumption

The two chosen downstream branches did not independently establish an ability resolver or native game/server cast-submission interface. **Park this SC-408 branch under the project's two-probe rule**; re-open only with a new discriminating source anchor (e.g., a verified ability ID/string lookup xref or a controlled local-game observation that ties a specific native state transition to a cast). Do not relaunch a broad binary import or assume that an unrelated call is a cast request.

SC4 overall is still active but not complete. SC1 known-versus-learnable and SC3 independent GCD remain unresolved. All evidence is **local physical-PC RIFT build only**. Neither RR2 nor Workbridge source was edited.

Tool jobs: `rea-localpc-sc408-callee-study-20261027-01` passed; `rea-localpc-sc408-alternate-callee-20261027-01` failed its .pdata assertion (preserved); `rea-localpc-sc408-alternate-bounded-20261027-01` passed. No execution in game.
