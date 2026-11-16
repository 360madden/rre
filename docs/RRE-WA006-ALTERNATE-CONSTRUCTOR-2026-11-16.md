# WA-006 — alternate type-3 wrapper arm initializes the same candidate-container layout (static only)

**Verification:** 2026-11-16 ~06:31 EST, independently verified AMD-DESKTOP with Workbridge 0.16.5-dev and `hostname.exe` (exit 0). **Owner:** single RRE manager. **Status:** exact-build source-qualified conditional initializer/output-slot relation, **not** a live or collision-qualified object. WA-006/WA-007 remain blocked.

## Original executable and function windows

- RRE archived on-disk `artifacts/lab2-live-20261107-0922/guest-rift_x64.exe`: **60,493,640 bytes**, SHA-256 `1935a05c9db6d468e34e0055014a4a99c1b5afceb1695884e24600f5c20a4be8`, image base `0x140000000`. It is an archived original, **not** evidence of a currently running process or loaded memory.
- **Previously undocumented alternate arm:** RVA `0x8EA08–0x8EBA6`, 414 bytes, SHA-256 `16198e31b14dbbaee1f8ff2c0f92a30050ad201268aa0f29d1e48c0f18eacb6a`; matching `.pdata` function boundaries; independently decoded **105/105** complete instructions.
- Existing dispatch wrapper: `0x8F204–0x8F22D`, 41 bytes, SHA-256 `67f197e75d675474765f891519b36ea5f4f7c73368b32fac0a7d73b6a2741943`.
- Existing other arm: `0x8ECB4–0x8F1B6`, 1,282 bytes, SHA-256 `7268ee4408787cf59e880dde4ed1d831c53e12c5335b6ef3d665ed79e26f580b`; already proved `0x8ED93 → 0xD088C` and `0x8EDA4 mov [rbp],rax`, with `RBP` preserving incoming output-slot `RDX`.

## New original-byte data flow

1. The wrapper tests `R9` at `0x8F208` and a stack argument at `0x8F20D–0x8F215`. When both gates pass, `0x8F21C` directly calls `0x8ECB4`; otherwise `0x8F223` directly calls **`0x8EA08`**. The wrapper does **not** overwrite incoming `RDX` before either call; it is the caller-provided output-slot pointer in both alternatives.
2. On the new alternate arm, `0x8EA29 mov rdi,rdx` saves the output-slot pointer. `0x8EA3A cmp qword ptr [rdi],rbx` tests its prior value (after `0x8EA38 xor ebx,ebx`), and nonzero invokes `0x8EA45 → 0x8E7F0` with the previous slot contents. Do not assume the effect of that helper without separate qualification.
3. An **unresolved** virtual `+0x80` call occurs at `0x8EA78`; the later branch uses a candidate `RAX` or obtains a conditional fallback from `0x70C64`. If `RAX` is nonzero, `0x8EAD3 lea rdx,[rsp+0x50]` and **`0x8EADB → 0xD088C`** invoke the **same 0x20-stride layout-compatible initializer** as the other arm. `0x8EAE0 mov rbx,rax` retains its result. If the fallback remains null, the call is bypassed and `RBX` remains zero.
4. **`0x8EAE3 mov qword ptr [rdi],rbx`** writes the resulting pointer **or zero** to the incoming output slot on the joined path. Later `0x8EB3D mov rdx,[rdi]` supplies that slot's current contents to `0x8EB45 → 0xD13A4`. This is a source-proven **output-slot publication and consumer call**, not an identity or gameplay claim.

**Refined conclusion:** both `0x8F204` wrapper arms can reach initializer `0xD088C` and write a value into their common caller-supplied output slot (through distinct flows). This strengthens source-level container provenance compared with the prior one-arm proof. It does **not** establish that the caller's slot is the separate query receiver field `+0x28`, that either branch was reached in a physical session, that `0xD088C` writes candidate-record `+0x08/+0x14`, that virtual `+0x40` resolves to a specific object, or that any collision/hit/current-player object has been qualified.

## Independent verification and guards

- Workbridge job `rre1116_0625_alt_branch_original_source` **exit 0**: original PE SHA, `.pdata` extent, 414-byte function hash, complete Capstone decode, original wrapper and alternate arm relationships.
- Workbridge job `rre1116_0625_alt_branch_full_disasm` **exit 0**: independently printed all **105** original instruction boundaries and exact key branch/call/store bytes.
- Workbridge job `rre1116_0625_alt_independent_stdlib` **exit 0**: separate **standard-library-only** PE section mapper confirmed original SHA and 414-byte SHA, **13 exact original instruction anchors**, **4 direct E8 targets**, and **2/2 in-memory negative byte mutations** rejected by specific anchor checks. No modified executable was written.
- Existing historical `0xD088C` initializer and `0x8ECB4` proof remains in [WA-006 split-pointer report](RRE-WA006-SPLIT-CANDIDATE-POINTER-2026-11-16.md). No new broad scans, Ghidra/REA imports, or installed dependencies.

**Next discriminator:** a source-proven caller that supplies the output slot to `0x8F204` and ties it to the **different** query receiver `+0x28`, or actual candidate-record field writers `+0x08/+0x14`. If neither emerges from existing bounded evidence, **park static recursion**; physical same-epoch nonself identities and hit/miss need separate operator authority. Do not change RR2 discovery feed or promote WA-006 without that proof.

**Scope/permissions:** no game input, UI reload, process/memory manipulation, debugger attach, installed-addon/SavedVariables change, VMware access, RR2/REA/Workbridge edits, or remote push. FreeBuff/Ollama model agents stayed on operator hold; Workbridge commands are independent source-verification jobs, **not model agents**.
