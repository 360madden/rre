# LEGION native-analysis toolchain — 2026-11-09

Verified on **LEGION** at approximately 14:22 EST. This is a host-local dependency installation receipt, not native RIFT behavior acceptance.

**Host policy:** RRE is one public cross-host repository. On LEGION, only the **physical RIFT** client is a permissible future live target. **No VMware labs**. No game process, addon, UI, binary, settings, or VM was touched during installation.

| Component | Verified location | Version / evidence |
| --- | --- | --- |
| Python | C:\work\rre\.venv\Scripts\python.exe | 3.14.10, isolated virtual environment |
| Capstone | RRE virtual environment | distribution 5.0.9; x64 nop/ret disassembly passed |
| pefile | RRE virtual environment | 2024.8.26; imported |
| Pillow / iced-x86 | RRE virtual environment | 13.0.0 / 1.22.0; imported |
| Node.js | C:\work\tools\node-v24.22.2-win-x64\node.exe | 24.22.2; existing PATH Node 24.20.0 preserved |
| Temurin JDK | C:\work\tools\jdk-21.0.13+9 | Java/javac 21.0.13 passed |
| Ghidra | C:\work\tools\ghidra_12.1.4_PUBLIC | 12.1.4; headless/decompiler verified by REA doctor |
| REA Agents | C:\work\tools\rea\node_modules\rea-agents | 6.8.0; MCP Client and Stdio imports passed |

## SHA-256 verified before extraction

- Node Windows x64 ZIP against official SHASUMS256: ca1bff5d8ead13c9f2ea404a176db46bd430704d5b5113734049fa365e7799e2
- Temurin JDK ZIP against Adoptium release API: a4dbaa05fca4bd89d84584e58c459bd732efebb1722af80ab13c6516832004f9
- Ghidra ZIP against the NSA release page: ddac49f903da9d5bac833e5cc79395098b9c33cfd3279be5f31bd00387d2d4db

Official sources: [REA prerequisites](https://rea.tools/get-started/), [Node 24.22.2](https://nodejs.org/en/download/archive/v24.22.2), [Adoptium JDK 21](https://adoptium.net/temurin/releases/?version=21), [NSA Ghidra 12.1.4](https://github.com/NationalSecurityAgency/ghidra/releases/tag/Ghidra_12.1.4_build).

## Re-run checks on LEGION

From PowerShell in C:\work\rre. **Preferred on LEGION:** the doctor now selects the verified host-local Python, REA, Ghidra and Java paths automatically; all command-line flags remain available to override a particular tool without changing AMD-DESKTOP's independent configuration. Environment assignments below are scoped to the current terminal only.

~~~powershell
& 'C:\work\tools\node-v24.22.2-win-x64\node.exe' tools\native-toolchain-doctor.mjs
& 'C:\work\tools\node-v24.22.2-win-x64\node.exe' --test tools\test-native-toolchain-doctor.mjs

$env:GHIDRA_INSTALL_DIR = 'C:\work\tools\ghidra_12.1.4_PUBLIC'
$env:JAVA_HOME = 'C:\work\tools\jdk-21.0.13+9'
$env:REA_ANALYSIS_PROVIDER = 'ghidra'
& 'C:\work\tools\node-v24.22.2-win-x64\node.exe' 'C:\work\tools\rea\node_modules\rea-agents\scripts\rea.mjs' doctor --provider ghidra --json
~~~

**Recorded results:** Toolchain doctor detected all components; zero-argument LEGION smoke and tests **6/6** passed; REA Ghidra provider doctor exited **0**, reported healthy=true, and verified native x64 decompiler, headless launcher, JDK21, and Windows native controls. Its environment_healthy=false refers to unconfigured *optional other providers and agent-client registrations*.

**Updated LEGION source gate (21:31 EST):** The physical on-disk `C:\Program Files (x86)\Glyph\Games\RIFT\Live\rift_x64.exe` **has now been verified** as 60,493,640 bytes with SHA-256 `1935a05c9db6d468e34e0055014a4a99c1b5afceb1695884e24600f5c20a4be8`; see the [SC-306 bounded source addendum](REA-RIFT-SPELLCASTING-SC306-QUEUE-ENUM-GAP-2026-10-27.md). Existing `docs/rea-session-options.json` still references **historical** REA 6.5.0, Ghidra 12.1.2, and Java paths; **do not run it unchanged on LEGION**. A future whole-PE REA session requires a separately reviewed, LEGION-specific options file and startup/import cost gate. For the current task, targeted Capstone/pefile decoding and independent standard-library PE verification succeeded without starting Ghidra analysis. No native RIFT import, client registration, PATH change, OS/game restart, reload, game input, or VMware operation. REA npm skipped an optional Frida install script, unnecessary for the verified Ghidra provider.
