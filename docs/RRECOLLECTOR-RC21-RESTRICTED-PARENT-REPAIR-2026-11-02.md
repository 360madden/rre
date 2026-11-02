# RC-21: restricted Reload UI parent-context repair

Date 2026-11-02. Physical-PC RIFT. Installed target RRECollector v0.4.5, source and host scope only.

Four parallel research lanes examined the API contract, installed BotFight and Gadgets patterns, live character SavedVariables, and the collector source. API documentation states that a Frame cannot become restricted unless its parent is already restricted; EventMacroSet requires a restricted frame while the addon environment is unsecured. Reference: https://github-wiki-see.page/m/chrisbecke/Igor/wiki/RIFT-API-Documents . RiftUI community issue documenting Incorrect security mode: https://www.riftui.com/downloads/fileinfo.php?id=218&page=2&so=DESC .

The newest v0.4.4 saved character data (SHA-256 2d472f9af0fdc15d0cb0889a75edbef7eedbc8f4c315438264eee0ffedf96b2d) explicitly contains uiReloadMacro.status=failed, reason starting with Incorrect security mode. Old code incorrectly secured an ordinary toolbar child; v0.4.4's mouse-handler change did not repair this parent constraint.

v0.4.5 uses separate restricted UI.CreateContext, sets context secure mode first, then creates and secures a plain rectangular Frame and registers a click-only reloadui macro. Macro read-back via EventMacroGet is checked where available, with failed/registered/unverified status preserved. It follows the toolbar anchor and synchronizes visibility on Hide and Toggle. Normal toolbar buttons retain their plain styling.

Source commit 50ebab8d8248bb7cde76e3b2a47bea00383d316b; six focused source tests, strict TOC and diff checks passed. Deployed with old-file hash preflight, backup in docs/rc21-v045-host-backup-20261102, TOC last. Installed verifier rre_rc21_v045_installedgate_20261102 exited 0, all 10 files matching. No other addon changed.

Live v0.4.5 UI, macro registration result and successful physical click remain unverified. A source/install pass cannot be promoted to game-runtime success.
