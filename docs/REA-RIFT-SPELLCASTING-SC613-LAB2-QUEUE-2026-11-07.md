# SC-613 — Lab-2 native Ability Queue value 1 correlates with Short

**November 7, 2026, 10:56 EST. Accepted narrow observation:** the unchanged Lab-2 native **Ability Queue: Short** UI bracketed two read-only samples of **value 1** from the source-qualified settings field. This supplies the missing label for the observed raw value without assuming enum order or toggling a setting. **Values 0 and 2 remain unmapped; actual queue behavior, GCD and server timing are untested.**

The [machine receipt](REA-RIFT-SPELLCASTING-SC613-LAB2-QUEUE-2026-11-07.json) binds the original UI images, exact requests/reports, loaded bytes, source/build hashes, operation cleanup and limitations. This is SC-613 in the [casting register](REA-RIFT-SPELLCASTING-TASKS-2026-10-27.json), using the existing [SC-305 field finding](REA-RIFT-SPELLCASTING-SC305-QUEUE-DOSSIER-2026-10-27.md) and resolving one part of [SC-306's gap](REA-RIFT-SPELLCASTING-SC306-QUEUE-ENUM-GAP-2026-10-27.md). The broader enum gate stays open.

## Target, reused tools and scope

The [M2 routing contract](REA-RIFT-SPELLCASTING-OFFLINE-TOOL-ROUTING-M2-2026-11-03.md) requires a new discriminator before reopening a parked lead. The new discriminator here is an actual selected-mode UI observation on the sole live target, **RIFT-LAB-2**, paired with independent current-process reads. The [external mouse procedure](REA-RIFT-LAB2-EXTERNAL-MOUSE-2026-11-07.md) governs all UI input. Starting main was **e4585cc34a8505a38ff26d4711aecd1ffeb7cf89**.

Guest process **9752**, start UTC ticks **639294897826627677**, executable `C:\RIFT_TRANSFER\RIFT\rift_x64.exe`, **60,493,640 bytes**, SHA-256 **1935a05c9db6d468e34e0055014a4a99c1b5afceb1695884e24600f5c20a4be8** were freshly checked before the probe and revalidated by each native command. No historical physical-PC absolute pointer was reused.

Bounded inventory found an **already installed** RR2 `RiftReader2.Live.exe` under guest `...\codex-jobs\current-native-B8A725E6A9CE663C\`. Guest and existing host publication both hash **B8A725E6A9CE663C36CB836681ED660261B07FDA4118A0167262E92131B2373E**, **117,159,776 bytes**. Its existing **inspect-native, snapshot-native and follow-pointer** commands performed all process access. No new memory reader, deployment, package, debugger, privilege escalation, injection, memory write or RR2 source edit was needed. Tool commands were bounded hidden launches; the native input controller stayed stopped in external mode.

## UI and native correlation

Reviewed external hover identified **SYSTEM**. Reviewed clicks followed **Settings → Interface → Action Bars**. The page showed **Ability Queue: Short** with **Apply disabled**. The dropdown was never opened or changed. Original capture `queue-ui-pre-read/before.png` shows Short at approximately **10:51:21 EST**; `queue-ui-post-read/before.png` shows the same page/selection at approximately **10:52:15 EST**. These are displayed local clock readings; original hashes and file timestamps are retained separately.

| Acquisition, UTC | Existing-tool result | Supported conclusion |
| --- | --- | --- |
| Native inspection, preceding samples | Exact PID/start/build, module identity and pinned reader implementation | Fresh process/module binding; no copied physical-session base |
| Loaded-byte snapshot, within the UI bracket | Original 39-byte global-load/store window at `0xBD2DA7`, 6-byte getter at `0xBD7153`, 24-byte setting-key window at `0x26ECC70`, plus current 8-byte pointer at `0x33958C0` | Three code/literal chunks match the qualified guest executable; global RIP target is the declared settings root |
| **15:51:38.9134000Z** | Root RVA `0x33958C0`, one offset `0xA4`, terminal 4 bytes **01 00 00 00** | Unsigned little-endian value **1** |
| **15:51:47.4376733Z** | Same request, identity and settings-object pointer; same terminal bytes | Second value **1**, stable across the two observations |

The preserved SC-305 source maps `ActionBars_AbilityQueue` to the 32-bit object field at **+0xA4**. Fresh loaded-code matching requalifies that local source relationship. The existing reader resolved the root against its freshly inspected module base, then read only the requested pointer/field. Both follow reports have `resolution.status=complete`, expected/observed identities equal to the snapshot, and the same pointer bytes as the snapshot's settings root.

**Accepted association: native 1 ↔ displayed Short, for this exact build/session and stable UI bracket.** It is not an atomic screenshot/memory transaction, a controlled mode contrast, proof of the other enum values, or evidence of the actual spell-admission window. No ability or cast was issued. After the samples, a reviewed click on **Cancel** closed Settings without applying changes.

## Verification, execution receipts and limits

An independent standard-library verifier parsed the original PE section mapping, compared loaded bytes, decoded base64 and little-endian values, validated source/report hashes, exact identities, pointer hops/root/offset/terminal address, and both values. **38 checks passed, including two negative controls.** It did not access the game process. Three loaded code/literal chunks matched original disk bytes. Sampled agreement does not attest every loaded page.

Workbridge job **rre_20261107_sc613_existing_reader_queue_v1** exited **1** after successful native inspection: the existing transport rejected an oversized combined encoded PowerShell script **before the snapshot executed**. The successful inspection was preserved. Splitting request-data staging from command execution through the same supported transport fixed the size issue; no transport limit was weakened.

Continuation job **rre_20261107_sc613_existing_reader_queue_v2** exited **0**, untruncated, **15:51:22.418Z–15:51:52.305Z**. It completed the snapshot and both follows, preserving the original inspection. All RRE-owned temporary guest request/output JSON files were copied and hash-guard removed. The compact console printer used an older nested-status assumption and printed null for follow status; the authoritative persisted **resolution.status=complete** reports were explicitly inspected and verified.

Originals, requests and execution evidence remain under `artifacts/lab2-sc613-20261107-1044/`. Documentation integration checks original/action hashes, request binding, exact reader/source identity, JSON, links, unchanged unrelated tasks, roadmap and diff. No implementation changed, so the historical full research suite is unnecessary.

All three producer request digests independently match the actual staged guest JSON payloads. Host text copies append CRLF; that artifact line ending is removed only when reconstructing the exact payload written by the recorded staging command. Guest cleanup separately checked the SHA of those exact payload bytes. An initial host digest comparison removed LF alone and failed because it left CR; correcting that comparison required no acquisition retry or producer change.

The installed FreeBuff CLI was genuinely launched once through existing `tools/freebuff-rre-review.py sc306`, against the newly changed SC-305/306 text copies. Job **rre_20261107_sc613_freebuff_sc306_new_pair** exited 0, untruncated, **16:01:09.029Z–16:01:36.895Z**, and the adapter reported completion plus owned-process/workspace cleanup. However, its retained excerpt has a completion-marker mention in interim text and **no usable final verdict**. The manager therefore records **zero accepted model reviews**, not an independent approval of the native result. The visible UI model label was DeepSeek V4.1 Flash 10/17 through FreeBuff; no model setting was changed and no Ollama was used. Original images/reports were not delivered to that text-only reviewer. This is a review-transport limitation to fix or avoid before relying on that mode again; do not repeat the unchanged prompt.

## Remaining research

SC-306 now has a qualified current pair for **1**, while **0 and 2** remain open. Do not fill the table from dropdown ordering, assume either means Full/None, or transfer this to a different build without requalification. The next useful source question is a concrete label/value constructor or the real queue consumer; another broad settings-global scan would repeat the parked route. SC-103, broader SC-604, RC and NAV gates remain independent.

Only the declared RRE documents/register/handoff are writable. Preserve nine historical untracked paths, native controller stop state and other repository owners. No Ollama was used. The timestamped [session handoff](REA-RIFT-SPELLCASTING-SESSION-HANDOFF-2026-11-07.md) retains the active three-hour discovery goal; this milestone does not finish it.
