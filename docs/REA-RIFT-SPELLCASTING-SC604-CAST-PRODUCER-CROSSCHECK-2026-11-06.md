# SC-604 — exact-build cast-producer crosscheck (November 6, 2026)

**Owner / lane:** RRE manager only; a bounded offline verification under SC-604. This is a source-hashed *interim supplement*, not a replacement for the immutable SC-604 graph or a completed native cast-chain milestone.

## Provenance

- Physical original `rift_x64.exe`, 60,493,640 bytes, SHA-256 `1935a05c9db6d468e34e0055014a4a99c1b5afceb1695884e24600f5c20a4be8`, independently read and hashed.
- Read-only RR2 **untracked draft** `C:\work\riftreader2\docs\reference\native-cast-owner-followup-2026-11-06.md`, SHA-256 `ace7b578a9490f912f1140c3f57278da67ac5d2e99fd2eba3607c6d5d2fd8bee`. Its owner, code and uncommitted repository files were not touched. Its semantic labels remain unreviewed here.
- Independent Windows Python 3.14 standard-library reader, invoked through Workbridge in the RRE directory: job `rre_nov06_1030_native_cast_crosscheck_001`, **exit 0, untruncated**, November 6, 10:33 EST. Verified complete binary SHA before parsing DOS/PE32+ section RVAs, 13 raw `E8` relative-call encodings and exception-directory entries. This did **not** invoke RR2 scanners, process memory or native functions.

## Byte-level result

**13/13 exact callsite-to-target encodings matched, 0 mismatches.**

| Site RVA | Encoded target RVA |
| --- | --- |
| `0x91DF13` | `0x4A4750` |
| `0x91DF2D` | `0x6A0040` |
| `0x91DF88` | `0x5A75C0` |
| `0x91DF92` | `0x5A7570` |
| `0x91DFB0` | `0x5A9940` |
| `0x91DFC9` | `0x5A6CB0` |
| `0x91E093` | `0x49F960` |
| `0x91E0A4` | `0x49D440` |
| `0x91E0AB` | `0x49DFE0` |
| `0x91E148` | `0x49D210` |
| `0x91E154` | `0x4948E0` |
| `0x91E1F1` | `0x4A4750` |
| `0x91E20C` | `0x6A0040` |

Exactly one exception record starts at `0x91DED0`, with range **[0x91DED0, 0x91E2B6)** and unwind RVA **0x2E49B74**. All 13 callsites fall within that range.

**Proof limit:** This independently confirms *encoded bytes and a PE unwind owner*, **not instruction boundaries, actual execution, function semantics, a currently loaded process build, or cast-state values**. RR2's helper-role interpretations are still its own provisional research, not independently verified by this byte check. In particular the output-buffer def/use relation and any reference-management side effect require RR2 owner review before a passive native reader is proposed.

**Decision:** This is a useful exact-build research anchor for future SC-604/native cast-state research, **not** a proven successful cast submit path, spell/Legendary ability ID, current cooldown, or queue enum. SC-604 stays interim; SC-103 and SC-306 remain blocked. The RR2 owner should first qualify instruction boundaries and downstream producer-to-marshaller dataflow. No new model reviewers were run because the fixed FreeBuff questions are unchanged and previously exercised. No game input, reload, process manipulation, addon/SavedVariables modification, desktop override or cross-project write occurred.
