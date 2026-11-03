# RC-26 — Physical hover card and browser interaction checkpoint

**Date:** November 3, 2026 UTC. **Status:** read-only UI checks complete; pinned-slot mutation deliberately deferred. **Addon:** installed and running RRECollector v0.4.8 on the physical PC RIFT client, Atank.

## Bounded live interactions

Guarded Windows input first verified the exact physical process/window (RIFT x64 PID 17412, HWND 1382178 at the time, class TWNClientFramework, 2576x1408). Each operation restored the previously minimized RIFT window only briefly and minimized it again afterward. No VM or other addon was operated.

| Interaction | Observation | Physical evidence |
| --- | --- | --- |
| Hover icon slot 2 | Full **Shield of the Chosen** name and ability ID `A03F53003A62FFD1E» appeared below the toolbar, along with “Not checked this session” and “read-only; does not cast”. Text and tooltip were fully within the screen. | `artifacts/rc26-hover-slot2-full-20261103.png» SHA `b401c1da0eafc79d5cfe0fd856e41b54b0116b52daac62b75b372eaf67412efe»; actual crop `artifacts/rc26-hover-slot2-crop-20261103.jpg» SHA `ab05ca29b61557f9fd0f2765dc0c937f88138e1600952a058a9558fabd3f34ea» |
| Browse opens Known | UI displays `API-known | All | 69 entries | page 1/9» and eight rows, with Prev disabled and the Known tab active. | `artifacts/rc26-browser-known-open-20261103.jpg» SHA `9551a670e371ec79b21440da8c798e9a65a2e03b07335f91c86de7ffea860a29» |
| Candidates tab | UI switches to `Static candidates | All | 96 entries | page 1/12» with eight source-labeled rows and active Candidates tab. | `artifacts/rc26-browser-candidates-20261103.jpg» SHA `fdedb81c3dc3536b95fea45686d69d813743429cab5fede8e82079375431649c» |
| Known row selection | Clicking **Aggressive Block** selects/highlights it and populates detail text with its exact ID, saved API-listed status, Paladin soul, base CD unknown, and stored description. This was a local read-only UI selection; no Pin selected action. | `artifacts/rc26-browser-known-row-20261103.jpg» SHA `586b5f1fbb1eebc377a7cab8bd864fd67cb77404f8009d5c826bcafc249152e3» |
| Close | Browser hides and the original compact v0.4.8 toolbar remains visible. | `artifacts/rc26-browser-after-close-20261103.jpg» SHA `d7e2c7fce2ff44d569ff44110b38864f4703c68c2833b1bbc1eb47235c419bd2» |

The saved Atank character file remained byte-identical across all RC-26 interactions: SHA-256 `f90620596f5d3a445d61cd8c3c9b9ad377f64ac03d429e0681b4c64a2f4d8532», the v0.4.8 save obtained by the real secure Reload UI click in RC-25. The physical game window was returned to minimized state.

## Remaining RC-26 action

**Pin selected** writes `RRECollectorData.toolbarSlots» and changes the next pin index. The current eight tiles represent Joey's saved ability choices. Testing that button now would overwrite a character preference and has no simple UI-only undo for the same slot, so it was left untouched. Complete the remaining pinning test with an agreed reversible way to preserve and restore the exact original slots, or use an isolated test character/session. The rest of the in-game visual and read-only navigation checks are accepted.

No Lua, TOC or installed addon changes were needed during this checkpoint. RC-25 v0.4.8 commit `ae794ec» remains the running release.
