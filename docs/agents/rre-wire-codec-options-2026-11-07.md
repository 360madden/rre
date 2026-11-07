# SC627 — Reuse options: retain JSON and optimize acquisition first

Current live data is18226bytes/fiveparts; discovery scanned749.6MB in about5.1s while full40KiBsnapshot copying took about96.7ms. VMware RPC adds fixed overhead. A new serializer does not shrink the scanned address space or remove process/command setup. Keep the already qualified JSON/Base64 contract. [Decision/source receipt](rre-wire-codec-options-2026-11-07.json).

| Candidate | Primary-source capability | Decision |
| --- | --- | --- |
| [dkjson2.11](https://dkolf.de/dkjson-lua/documentation) | PureLua5.1–5.5, MIT, optionalLPeg, orderedkeys/null support | Convenience only; no size reduction; do not replace |
| [rxi/json.lua](https://github.com/rxi/json.lua) | Small pureLua5.1+, MIT; generic JSON behavior | No transport win; decodingnulltonil differs; do not replace |
| [lua-MessagePack](https://fperrad.frama.io/lua-MessagePack/) | PureLua5.1variant, MIT/X11; [C#implementation](https://github.com/MessagePack-CSharp/MessagePack-CSharp) adds package | Defer; stringkeys and outerBase64remain; integer/array/nullrules need qualification |
| [Lua-CBOR](https://www.zash.se/lua-cbor.html) | Lua5.1–5.4, optionalstruct/bitops; text detection uses5.3utf8 and generic table guessing | Not current fit; explicit adapters/license proof needed |
| [LibDeflate](https://github.com/SafeteeWoW/LibDeflate/blob/main/README.md) | Single pureLua DEFLATE/zlib implementation; [zlib license](https://github.com/SafeteeWoW/LibDeflate/blob/main/LICENSE.txt); .NET has [ZLibStream](https://learn.microsoft.com/en-us/dotnet/api/system.io.compression.zlibstream) | Best future exact-payload size trial, not current adoption |

Lua5.1 numbers and arbitrary byte strings still need explicit bounded integer/UTF8/schema rules; binary encoding does not remove them. Native C codecs need loading/compilation unavailable to a normal addon and are out of scope. No package or source was copied/installed.

If payload growth reaches a real part/64KiB ceiling, keep logical JSON, benchmark pinnedLibDeflate level1 on the exact retained payload under existingLua5.1, and test CPU/GC/size plus C#zlib roundtrip, truncated/bomb/length/checksum rejection. Use an explicit new encoding/version, never autodetect. Upstream unrelated benchmark ratios are not RRE measurements and are not used as a speed claim here.

Priority: narrow/cache/resume discovery and reduce VMware round trips, stabilize one acquisition adapter, preserve correctness, then measure compression only when bytes are demonstrably material. Source research is complete; no live operation or new backend was performed.
