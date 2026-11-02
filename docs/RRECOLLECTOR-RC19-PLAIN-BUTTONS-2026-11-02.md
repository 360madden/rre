# RC-19 — Plain buttons and non-stretched captions

Date: November 2, 2026. Target: physical-PC RIFT. Version: 0.4.3.

The user prefers ordinary rectangular buttons to the RIFT-themed skin and requested correct text proportions. All toolbar and browser controls now use plain Frame surfaces with hover, pressed and disabled backgrounds; captions are Text elements anchored CENTER, without a fixed text width or stretched texture. Font fitting uses a constrained 10–14-point size and GetFullWidth measurement where supported.

The Reload UI control uses a restricted standard Frame and secure click-only macro. A failed secure-macro setup is caught and the button is disabled rather than crashing the toolbar.

Source commit: 01146004386942a7d7e4f24c6eba03bb29b06cc8. Source tests: rc19_plainbuttons_tests_20261102, 6/6 pass. TOC: rc19_plainbuttons_toc_20261102 strict pass. Installed verifier: rc19_plainbuttons_installedgate_20261102, version 0.4.3 and 10/10 hashes. Changed addon files were installed with the manifest last. Previous host files backed up in docs/rc19-v043-host-backup-20261102. No other addon was modified.

Live runtime is pending: neither rendered 0.4.3 caption fit nor secure Reload UI click is verified in game. RC-08 candidateLookup remains open until a fresh source-qualified SavedVariables receipt.
