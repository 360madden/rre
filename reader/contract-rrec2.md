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
| addonVersion | `0.4.12` |
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

`context` contains only the current snapshot's player, target, roleSlot, roleNames, clientVersion, frameTime, realTime, capabilities, scope, stats, statsTruncated when present. Player id/name/calling must be nonempty strings (128/256/128 UTF8 bytes), level finite positive, roleSlot finite number or nonempty string≤128bytes, frame/real clocks finite nonnegative and bounded so ×1000000/×1000 remain safe integers, capabilities.player=true. Player/target are maps of the existing20 unit fields with scalar values/strings≤2048bytes. Capabilities contains only the existing8 boolean flags. Role names/client-version maps contain at most32 scalar entries; stats at most256; map string values≤256bytes and keys≤128bytes. Client version may alternatively be a scalar≤256bytes. Scope is string≤4096bytes; statsTruncated is a nonnegative safe integer dropped-count. Nested maps/arrays in these scalar maps fail. No defaults are invented. The producer snapshots this data once; frame chunking is serialization, not repeated API acquisition.

## Lifecycle and binding

Only the existing manual Capture action publishes a new generation. Load clears retained frames. Every Capture attempt clears the previous wire before acquisition; failure leaves no current frames and emits a bounded reason. Existing prior-good SavedVariables preservation remains intact. Build all strings locally, then atomically assign one retained frame table only after the whole generation passes validation/bounds. No background polling or gameplay event subscription is added by this milestone.

A per-load session token is generated from bounded current clock/player/counter inputs on the first valid capture and shown with sequence/parts/byte count in a local completion receipt. This token correlates a load/publication; it is not a cryptographic nonce or authentication. No host nonce-delivery channel is assumed. Consumer binds exact VM/process/start/build and fresh UI/source receipt separately. Old strings surviving GC, source literals, copies, relocation and partial scan coverage remain possible; exact requested session/sequence and complete-generation validation are mandatory.

Reader `qualification.fixture` identifies the feasibility-only RREC1 contract; RREC2 sets it false consistently across carriers. This flag does not establish origin. Offline Lua fixtures retain explicit declared origin and independent test provenance; runtimeProducerVerified/sourceAuthenticityVerified and all live/freshness/build/atomic/restart qualifications remain false.

Live gate requires a Lab2-isolated install destination, source/package/installed/loaded version receipts, explicit reviewed external mouse action, full-prefix acquisition with pinned existing tools, coherent data vs current SavedVariables/API, and fresh identity checks. A transferred publication is not passive freshness, atomic API acquisition, restart qualification, cast acceptance or a server outcome.
