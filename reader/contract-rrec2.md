# RREC2 production memory publication contract v1 (SC622)

This is the separate RRECollector production contract, accepted for offline interoperability. RREC1 remains a fixture-only replay format. No deployment/load/live acceptance is implied by this document. Direction is addon→external consumer; no inbound commands, arbitrary dispatch, game action or memory write API is defined.

## Carrier frame

ASCII frame, at most8192bytes including markers:

```text
RREC2|<32lowerhex session>|<16uppercasehex sequence>|<8uppercasehex body length>|<body JSON>|ENDRREC2
```

The sequence is an integer1..2^53−1 encoded exactly in both header and body. The complete expected header session/sequence must be supplied by the consumer; no highest-counter-across-load selection. Context bytes after the suffix are allowed only at an explicitly bounded memory-copy boundary. Standalone frames reject trailing bytes.

Body has exactly these keys:

| Key | Rule |
| --- | --- |
| schemaVersion | integer2 |
| producer | `RRECollector` |
| addonVersion | exactly `0.4.12`, `0.4.13`, `0.4.14`, `0.4.15`, `0.4.16`, `0.4.17`, `0.4.18`, `0.4.19`, or `0.4.20`; all parts and the decoded document must agree |
| session | same32lowerhex as header |
| sequence | same safe positive integer as header |
| part / parts | integers1..parts /1..16 |
| encoding | `base64` |
| payloadBytes | whole decoded document length,1..65536 |
| adler32 | eight lowercase hex digits, whole decoded document Adler32 |
| data | canonical Base64 of this part's1..4096raw bytes |

All nonfinal parts decode to4096bytes; final part decodes to the exact remainder. Count must equal ceil(payloadBytes/4096). Unknown/duplicate fields, unsupported versions, noncanonical encodings, wrong session/sequence, missing/extra/duplicate parts, mixed metadata, lengths and checksum errors fail closed. Base64 makes UTF8 splitting harmless: decode/reassemble bytes before parsing document text. Adler32 detects corruption/assembly mistakes; it is not authentication. Receiver records SHA256 of retained source and decoded payload. See [RFC1950](https://www.rfc-editor.org/info/rfc1950/) for Adler32.

## Decoded document

UTF8 JSON, maximum65536bytes and bounded object depth/entries, with exactly:

`schemaVersion`, `producer`, `addonVersion`, `session`, `sequence`, `source`, `counts`, `context`, `abilities`.

Version is1, producer/version/session/sequence repeat the frame metadata, source is `rift-api`. `counts` preserves the current RRECollector abilityList receipt: exact boolean apiAvailable/batchDetailAvailable/enumerationComplete and integer0..1024 rawEntries/uniqueCount/detailCount/detailFailures/duplicates/ignored/truncated/fallbackCalls. API and enumeration must be complete, zero failures/ignored/truncation,1..512unique/details equal the final ability-record count, rawEntries=uniqueCount+duplicates, fallbackCalls≤uniqueCount. Without batch Detail, fallbackCalls must equal uniqueCount. No claims of learnable/locked/usable/game-bound membership follow from this set.

`abilities` contains exact unique lookupId `A`+16uppercasehex and only bounded finite scalar Detail fields accepted by the host reader, including target when provided. False and zero are values; missing optional fields are unknown. Descriptions/strings are bounded; unsupported types, cycles, nonfinite values, oversized payloads or incomplete captures must produce an explicit publication failure rather than truncating the wire.

`context` contains only the current snapshot's player, target, roleSlot, roleNames, clientVersion, frameTime, realTime, capabilities, scope, stats, statsTruncated, and the v0.4.14+ optional experience map when present. Player id/name/calling must be nonempty strings (128/256/128 UTF8 bytes), level finite positive, roleSlot finite number or nonempty string≤128bytes, frame/real clocks finite nonnegative and bounded so ×1000000/×1000 remain safe integers, capabilities.player=true. Version0.4.12 player/target maps retain the original20 unit fields. Versions0.4.13,0.4.14,0.4.15,0.4.16,0.4.17,0.4.18 and0.4.19 allow exactly three additional optional fields, `race`, `raceName`, and `zone`, increasing each map bound to23. `race` is a documented player race token, `raceName` a localized player race name, and `zone` an opaque zone ID; no enum or zone display name is invented. The existing raw-scalar policy retains bounded strings, finite numbers and booleans; a non-string or empty value is present raw evidence, semantically unqualified. Missing fields remain unknown. `decoration` is not allowed. All versions bound unit strings to2048UTF8 bytes. Versions0.4.12/0.4.13 contain only the original8 boolean capability flags and reject Experience decoration. Versions0.4.14,0.4.15,0.4.16,0.4.17,0.4.18 and0.4.19 require boolean `capabilities.experience` as a ninth flag. When true, `context.experience` must be a plain object with at most three finite numeric fields from `accumulated`, `needed`, `rested` (including valid zero or an empty object); when false the map must be absent. Unknown, nested, string or array values fail. This is manual Capture-only; no passive Experience polling. Role names/client-version maps contain at most32 scalar entries; stats at most256; map string values≤256bytes and keys≤128bytes. Client version may alternatively be a scalar≤256bytes. Scope is string≤4096bytes; statsTruncated is a nonnegative safe integer dropped-count. Nested maps/arrays in these scalar maps fail. No defaults are invented. The producer snapshots this data once; frame chunking is serialization, not repeated API acquisition.

## Lifecycle and binding

Only the existing manual Capture action publishes a new generation. Load clears retained frames. Every Capture attempt clears the previous wire before acquisition; failure leaves no current frames and emits a bounded reason. Existing prior-good SavedVariables preservation remains intact. Build all strings locally, then atomically assign one retained frame table only after the whole generation passes validation/bounds. No background polling or gameplay event subscription is added by this milestone.

A per-load session token is generated from bounded current clock/player/counter inputs on the first valid capture and shown with sequence/parts/byte count in a local completion receipt. This token correlates a load/publication; it is not a cryptographic nonce or authentication. No host nonce-delivery channel is assumed. Consumer binds exact VM/process/start/build and fresh UI/source receipt separately. Old strings surviving GC, source literals, copies, relocation and partial scan coverage remain possible; exact requested session/sequence and complete-generation validation are mandatory.

Reader `qualification.fixture` identifies the feasibility-only RREC1 contract; RREC2 sets it false consistently across carriers. This flag does not establish origin. Offline Lua fixtures retain explicit declared origin and independent test provenance; runtimeProducerVerified/sourceAuthenticityVerified and all live/freshness/build/atomic/restart qualifications remain false.

Historical Lab2 live acquisition requires authorized guest addon destination, source/package/installed/loaded receipts, reviewed external mouse action, pinned full-prefix reader acquisition, fresh identity and coherent SavedVariables/API. On LEGION, only the local physical RIFT game is in scope; live acceptance requires its own current window/version/chat/SavedVariables proof, not a Lab2 transfer. The user allowed only RRECollector files to synchronize through the observed OneDrive addon root. SC622 accepted one bounded0.4.12 transfer, and the November7 SC625/SC628 work accepted one bounded0.4.13 Lab2 generation. Version0.4.14 reached 11/11 source-to-LEGION-OneDrive parity on November10, but its physical-game load/visibility is unverified; version0.4.15 reached 11/11 LEGION OneDrive parity November10 with no in-game proof, and version0.4.16 reached 11/11 LEGION OneDrive parity November10 and awaits a matching in-game UI/capture receipt. The v0.4.17 reader/source contract additionally admits a bounded, separate profession discovery receipt that is not part of the RREC2 payload; v0.4.17 physical game acceptance remains pending. The v0.4.18 release preserves the same RREC2 wire schema, strengthens bounded profession-document UTF-8 clipping and marks old/incomplete saved captures in the UI; its physical loaded-game acceptance is also pending. A transferred publication is not passive freshness, atomic API acquisition, restart qualification, cast acceptance or a server outcome. The v0.4.19 RREC2 reader acceptance is verified in source and offline regression checks, not by a version-matched physical-game load/capture receipt.

## v0.4.20 compatibility note

The .20 producer retains .19's existing ability/context/Experience contract; both versions remain admitted. `questSnapshot` and `questAttempt` are separate SavedVariables records and are not wire context or publication payload fields. Quest export does not establish current freshness, destination reachability or completed gameplay.
