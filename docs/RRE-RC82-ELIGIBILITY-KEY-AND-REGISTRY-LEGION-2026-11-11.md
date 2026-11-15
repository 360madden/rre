# RC-82/83 — eligibility transitions, lookup key and separate controller

**November 11, 2026, LEGION.** The C2M gate's root+0x358 byte now has source-qualified later set/clear paths, and the related root fields are distinguished. Precise player/actor identity remains unproved. Two independent Codex lanes each used bounded probes; the manager rehashed **25 original windows** and fully decoded all21 code windows. Four windows are data. [Evidence JSON](RRE-RC82-ELIGIBILITY-KEY-AND-REGISTRY-LEGION-2026-11-11.json).

Source: installed physical `rift_x64.exe`, 60,493,640 bytes, SHA256 `1935a05c9db6d468e34e0055014a4a99c1b5afceb1695884e24600f5c20a4be8`. All addresses are RVAs. No Workbridge, import, process attachment, input, VM or other-repository modification.

## Eligibility changes follow a key change and reference installation

`0x580580` accepts the root and an opaque64-bit value. When it differs from root+0x360 (`0x5805CE`), it resets root+0xB90-owned state and writes **root+0x358=0 at `0x580653`**; it stores the new value into root+0x360 at `0x580693`. Caller `0x7F258C→0x49A020`, followed by `0x7F2591/94/97`, explicitly supplies that root and value.

`0x580950` constructs a0x190-byte object via `0xF889C0`, passes a reference pair through `0x580A17→0x5807D0`, then writes **root+0x358=1 at `0x580A1C`**. Root-qualified caller `0x5F673C/41/48` takes this route only when another object's +0x318 equals root+0x360. This proves state transitions; it does not name the flag as focus, player-ready or gameplay-enabled.

The generic `0x77E400` setter also writes an offset+0x358, but its observed caller supplies an outer+0x2F8 subobject. It is not accepted as an alias of this root without further evidence.

## root+0x360 is a registry key; root+0x400 is a selected cached component

`0x6A0040` selects manager+0x50 and calls `0x58C990` with **the64-bit key at root+0x360**. That helper compares node+0x08 keys in a hash-bucket chain and returns a 24-byte iterator. `0x6A0040` reads the found-node pointer from iterator+0x10 at `0x6A0078`, extracts node+0x10 at `0x6A00A4`, then saves that container pointer at root+0x3F8 at `0x6A00B0`. This is not proof that the key itself is an actor pointer or that the lookup is specifically for the player.

The RC-81 resolver then reads one byte from the returned container using the signed registration index/offset at global `0x2F57850`, and selects from the container's +0x78 pointer table; byte0xFF means no component. Its result is cached at root+0x400. The file's original index value is -1; the runtime value is not inferred from that file image.

RC-83 found the actual registration writer: **`0x5DEC85`** stores EAX to `0x2F57850`; `0x5DEC7A` loaded EAX from counter `0x33DBB58`, then `0x5DEC90/92` increment/store that counter. The preceding path installs vtable `0x26B0840` on an allocated registry object, calls `0x5A0F80` and stores that object in the returned entry. This supplies a dynamic registration route. The adjacent RTTI COL pointer is zero; no class name is accepted. Literal `0x4F7D0B87` is not given an invented semantic name.

## The new0x190 object is installed at different root fields

`0x5807D0` installs the reference pair at **root+0x330/+0x338** (`0x580821/28`) with retain/release handling. It does not write root+0x400; equality/aliasing of those objects has not been proved.

Constructor `0xF889C0` installs vtable `0x2710518`, retains the original input-reference container at this+0x50, selects a component into this+0x58, and creates its own listener at this+0x150 with callback `0xF8AB10`. Its `0xF88CB9→0x7C1F30` call orders that listener before the previous controller's listener when available, otherwise the C2M anchor. It is an input-aware object distinct in storage from the root+0x400 cache.

Original UTF-16 configuration names include `useAltDistScale`, `distanceScale`, `distanceScaleAlt`, `maxDistanceScale`, `maxDistanceScaleAlt`, `pitch`, `yaw`, and `pd_`. They support a **camera/view-controller hypothesis only**. A qword before the vtable is UTF-16 text, so an attempted standard adjacent RTTI interpretation was rejected. Neither these names nor orientation writes prove player locomotion.

## Decision

Park these investigated source leads after the bounded probes. New work must use a discriminating source anchor or actual authorized runtime evidence; do not expand another generic native scan or label every controller as the player. RC-79's quest-journal exporter already provides a functional offline input, while its package/client validation request remains unanswered. Current live settings, actor identity, actual movement/stop and cast/quest completion remain unverified.
