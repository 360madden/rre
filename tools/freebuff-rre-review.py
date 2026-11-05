"""Run two bounded RRE FreeBuff reviews via the already verified Windows ConPTY transport.

This adapter makes a pinned in-memory specialization of Workbridge's existing
ConPTY pilot. It does not edit Workbridge, install software, read credentials,
or grant FreeBuff RRE repo writes: reviewers see disposable source copies.
FreeBuff itself is NOT OS-sandboxed. Follow single-manager review gates.
"""
from __future__ import annotations
import hashlib
import json
import os
from pathlib import Path
import sys

MODES = {"sc103": "freebuff-review-pilot", "rc30": "freebuff-lifecycle-review",
         "sc306": "freebuff-review-pilot", "sc503": "freebuff-lifecycle-review",
         "slots": "freebuff-review-pilot", "file": "freebuff-lifecycle-review",
         "operator": "freebuff-lifecycle-review", "ability": "freebuff-review-pilot"}
UPSTREAM = Path(r"C:\work\workbridge-mcp\scripts\freebuff-conpty-probe.py")
UPSTREAM_SHA256 = "c29fbfd898c5fe54e86e34403a79ef4d1107761f4828deed153be4be3de3c07f"
ROOT = Path(__file__).resolve().parent.parent

def replace_once(source: str, old: str, new: str) -> str:
    n = source.count(old)
    if n != 1:
        raise RuntimeError(f"Upstream specialization anchor mismatch ({n}): {old[:70]}")
    return source.replace(old, new, 1)

def build(lane: str = "sc103"):
    raw = UPSTREAM.read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    if digest != UPSTREAM_SHA256:
        raise RuntimeError(f"ConPTY upstream drift: {digest}")
    source = raw.decode("utf-8")
    source = replace_once(
        source,
        'probe_dir = os.path.join(repo_root, "temp", probe_name)',
        'probe_dir = os.path.join(os.environ["TEMP"], "rre-" + probe_name)')
    source = replace_once(
        source,
        '            source = os.path.join(repo_root, "desktop", "Workbridge.ControlCenter",\n'
        '                                  "BoundedLineReader.cs")\n'
        '            shutil.copyfile(source, os.path.join(probe_dir, "BoundedLineReader.cs"))',
        '            for parts in (("tools", "sc103_luapad_hover_probe.lua"),\n'
        '                          ("tools", "test_sc103_luapad_hover_probe.lua"),\n'
        '                          ("tools", "sc103_luapad_copy_result.lua")):\n'
        '                target = os.path.join(probe_dir, *parts)\n'
        '                os.makedirs(os.path.dirname(target), exist_ok=True)\n'
        '                shutil.copyfile(os.path.join(repo_root, *parts), target)')
    source = replace_once(
        source,
        '                shutil.copyfile(src, os.path.join(probe_dir, source_parts[-1]))',
        '                target = os.path.join(probe_dir, *source_parts)\n'
        '                os.makedirs(os.path.dirname(target), exist_ok=True)\n'
        '                shutil.copyfile(src, target)')
    # Match tiny, unique literals rather than brittle multi-line indentation.
    mapping = (
        ('("desktop", "Workbridge.ControlCenter", "App.xaml.cs")',
         '("addons", "RRECollector", "ui.lua")'),
        ('("desktop", "Workbridge.ControlCenter", "MainWindow.xaml.cs")',
         '("tools", "verify-rrecollector-ui-pinning.lua")'),
        ('("desktop", "Workbridge.ControlCenter", "BoundedLineReader.cs")',
         '("docs", "RRECOLLECTOR-RC30-STALE-PIN-DISPLAY-2026-11-03.md")'),
        ('("scripts", "desktop-monitor.mjs")',
         '("docs", "RRECOLLECTOR-RC27-UNDO-CAPTURE-GUARD-2026-11-03.md")'),
        ('("scripts", "desktop-monitor-format.mjs")',
         '("docs", "RRECOLLECTOR-RC31-UI-AFFORDANCE-AUDIT-2026-11-03.md")'),
        ('b"Read BoundedLineReader.cs in this isolated folder only. "',
         'b"Read tools/sc103_luapad_hover_probe.lua and tools/test_sc103_luapad_hover_probe.lua. "'),
        ('b"Review its correctness; do not modify files or run shell commands. "',
         'b"Using copies only: find NEW defect besides repaired tooltip fault; "'),
        ('b"Give one concrete issue with a line number, or say NO_ISSUE. "',
         'b"cite line and test, or NO_NEW_ISSUE. No edits, shell or game. "'),
        ('b"Read App.xaml.cs, MainWindow.xaml.cs, BoundedLineReader.cs, "',
         'b"Read addons/RRECollector/ui.lua, tools/verify-rrecollector-ui-pinning.lua and "'),
        ('b"desktop-monitor.mjs and desktop-monitor-format.mjs in this isolated "',
         'b"docs/RRECOLLECTOR-RC30-STALE-PIN-DISPLAY-2026-11-03.md in this isolated "'),
        ('b"folder. Review for at most TWO serious correctness defects in "',
         'b"folder. Find at most TWO new valid-ID rollback risks; exclude "'),
        ('b"lifecycle, async races or status handling. Do not modify files "',
         'b"malformed data and external table replacement. No file edits "'),
        ('b"or run shell commands. Give exact filenames, line numbers, "',
         'b"or run shell commands or game input. Give exact filenames, lines, "'),
    )
    for old, new in mapping:
        source = replace_once(source, old, new)
    # A second fixed review pair addresses different, previously blocked research
    # questions using only pre-existing source-hashed evidence reports. No runtime
    # scanner or generic agent prompt-execution interface is exposed.
    if lane == "sc306":
        additions = (
            ('("tools", "sc103_luapad_hover_probe.lua")',
             '("docs", "REA-RIFT-SPELLCASTING-SC305-QUEUE-DOSSIER-2026-10-27.md")'),
            ('("tools", "test_sc103_luapad_hover_probe.lua")',
             '("docs", "REA-RIFT-SPELLCASTING-SC306-QUEUE-ENUM-GAP-2026-10-27.md")'),
            ('b"Read tools/sc103_luapad_hover_probe.lua and tools/test_sc103_luapad_hover_probe.lua. "',
             'b"Read docs/REA-RIFT-SPELLCASTING-SC305-QUEUE-DOSSIER-2026-10-27.md and "'),
            ('b"Using copies only: find NEW defect besides repaired tooltip fault; "',
             'b"docs/REA-RIFT-SPELLCASTING-SC306-QUEUE-ENUM-GAP-2026-10-27.md. Find "'),
            ('b"cite line and test, or NO_NEW_ISSUE. No edits, shell or game. "',
             'b"one NEW source-based enum discriminator or say NO_MAPPING. No game input. "'),
        )
        for old, new in additions:
            source = replace_once(source, old, new)
    elif lane == "sc503":
        additions = (
            ('("addons", "RRECollector", "ui.lua")',
             '("docs", "REA-RIFT-SPELLCASTING-SC303-TIMING-METADATA-2026-10-27.md")'),
            ('("tools", "verify-rrecollector-ui-pinning.lua")',
             '("docs", "REA-RIFT-SPELLCASTING-SC304-TIMING-2026-10-27.md")'),
            ('("docs", "RRECOLLECTOR-RC30-STALE-PIN-DISPLAY-2026-11-03.md")',
             '("docs", "REA-RIFT-SPELLCASTING-SC501-LOCAL-REJECTION-2026-10-27.md")'),
            ('("docs", "RRECOLLECTOR-RC27-UNDO-CAPTURE-GUARD-2026-11-03.md")',
             '("docs", "REA-RIFT-SPELLCASTING-SC502-OUTCOME-2026-11-01.md")'),
            ('("docs", "RRECOLLECTOR-RC31-UI-AFFORDANCE-AUDIT-2026-11-03.md")',
             '("docs", "REA-RIFT-SPELLCASTING-SC604-INTERIM-MECHANISM-2026-11-01.md")'),
            ('b"Read addons/RRECollector/ui.lua, tools/verify-rrecollector-ui-pinning.lua and "',
             'b"Read docs/REA-RIFT-SPELLCASTING-SC303-TIMING-METADATA-2026-10-27.md and "'),
            ('b"docs/RRECOLLECTOR-RC30-STALE-PIN-DISPLAY-2026-11-03.md in this isolated "',
             'b"docs/REA-RIFT-SPELLCASTING-SC502-OUTCOME-2026-11-01.md in this isolated "'),
            ('b"folder. Find at most TWO new valid-ID rollback risks; exclude "',
             'b"folder. Identify ONE falsifiable channel/proc/interrupt contrast; "'),
            ('b"malformed data and external table replacement. No file edits "',
             'b"existing evidence is not a new game test. No file edits "'),
        )
        for old, new in additions:
            source = replace_once(source, old, new)
    elif lane in ("slots", "file"):
        if lane == "slots":
            replacements = (
                ('("tools", "sc103_luapad_hover_probe.lua")',
                 '("tools", "rc30-saved-receipt.mjs")'),
                ('("tools", "test_sc103_luapad_hover_probe.lua")',
                 '("tools", "test-rc30-saved-receipt.mjs")'),
                ('b"Read tools/sc103_luapad_hover_probe.lua and tools/test_sc103_luapad_hover_probe.lua. "',
                 'b"Read tools/rc30-saved-receipt.mjs and tools/test-rc30-saved-receipt.mjs. "'),
                ('b"Using copies only: find NEW defect besides repaired tooltip fault; "',
                 'b"Inspect implicit Lua array indexing and ID redaction; report ONE bug "'),
                ('b"cite line and test, or NO_NEW_ISSUE. No edits, shell or game. "',
                 'b"with file line and test, or NO_NEW_ISSUE. No edits or game. "'),
            )
        else:
            replacements = (
                ('("addons", "RRECollector", "ui.lua")',
                 '("tools", "rc30-saved-receipt.mjs")'),
                ('("tools", "verify-rrecollector-ui-pinning.lua")',
                 '("tools", "test-rc30-saved-receipt.mjs")'),
                ('("docs", "RRECOLLECTOR-RC30-STALE-PIN-DISPLAY-2026-11-03.md")',
                 '("tools", "read-rrecollector-saved.mjs")'),
                ('("docs", "RRECOLLECTOR-RC27-UNDO-CAPTURE-GUARD-2026-11-03.md")',
                 '("docs", "RRECOLLECTOR-RC30-POSTSTART-SAVED-2026-11-03.md")'),
                ('b"Read addons/RRECollector/ui.lua, tools/verify-rrecollector-ui-pinning.lua and "',
                 'b"Read tools/rc30-saved-receipt.mjs and tools/read-rrecollector-saved.mjs and "'),
                ('b"docs/RRECOLLECTOR-RC30-STALE-PIN-DISPLAY-2026-11-03.md in this isolated "',
                 'b"tools/test-rc30-saved-receipt.mjs in this isolated "'),
                ('b"folder. Find at most TWO new valid-ID rollback risks; exclude "',
                 'b"folder. Audit read-once source identity and read races; check "'),
                ('b"malformed data and external table replacement. No file edits "',
                 'b"claim boundaries. Give one reproducible flaw. No file edits "'),
            )
        for old, new in replacements:
            source = replace_once(source, old, new)
    elif lane in ("operator", "ability"):
        if lane == "operator":
            replacements = (
                ('("tools", "verify-rrecollector-ui-pinning.lua")',
                 '("tools", "rc30-saved-receipt.mjs")'),
                ('("docs", "RRECOLLECTOR-RC30-STALE-PIN-DISPLAY-2026-11-03.md")',
                 '("docs", "RRECOLLECTOR-RC30-OPERATOR-ACCEPTANCE-2026-11-03.md")'),
                ('("docs", "RRECOLLECTOR-RC27-UNDO-CAPTURE-GUARD-2026-11-03.md")',
                 '("docs", "RRECOLLECTOR-RC30-EIGHT-SLOT-CORRECTION-2026-11-03.md")'),
                ('("docs", "RRECOLLECTOR-RC31-UI-AFFORDANCE-AUDIT-2026-11-03.md")',
                 '("docs", "RRECOLLECTOR-RC30-POSTSTART-SAVED-2026-11-03.md")'),
                ('b"Read addons/RRECollector/ui.lua, tools/verify-rrecollector-ui-pinning.lua and "',
                 'b"Read addons/RRECollector/ui.lua, tools/rc30-saved-receipt.mjs and "'),
                ('b"docs/RRECOLLECTOR-RC30-STALE-PIN-DISPLAY-2026-11-03.md in this isolated "',
                 'b"docs/RRECOLLECTOR-RC30-OPERATOR-ACCEPTANCE-2026-11-03.md in this isolated "'),
                ('b"folder. Find at most TWO new valid-ID rollback risks; exclude "',
                 'b"folder. Audit the operator A-B-C-D protocol: flag ONE missing "'),
                ('b"malformed data and external table replacement. No file edits "',
                 'b"safety/evidence gate or say NO_GAPS. No file edits or game input. "'),
            )
        else:
            replacements = (
                ('("tools", "test_sc103_luapad_hover_probe.lua")',
                 '("docs", "REA-RIFT-SPELLCASTING-SC103-LEGENDARY-SELECTION-2026-11-03.md")'),
                ('b"Read tools/sc103_luapad_hover_probe.lua and tools/test_sc103_luapad_hover_probe.lua. "',
                 'b"Read tools/sc103_luapad_hover_probe.lua and SC103 Legendary-selection docs. "'),
                ('b"Using copies only: find NEW defect besides repaired tooltip fault; "',
                 'b"Distinguish current normal-ID from unproven Legendary selection; "'),
                ('b"cite line and test, or NO_NEW_ISSUE. No edits, shell or game. "',
                 'b"give ONE new operator-safe discriminator or NO_NEW_EVIDENCE. No edits. "'),
            )
        for old, new in replacements:
            source = replace_once(source, old, new)
    # Reviewers must see the same relative paths as the source repository.
    # Flattened copies caused a prior FreeBuff false-positive about tools/ paths.
    for expected in ("target = os.path.join(probe_dir, *parts)",
                     "target = os.path.join(probe_dir, *source_parts)",
                     "os.makedirs(os.path.dirname(target), exist_ok=True)"):
        if expected not in source:
            raise RuntimeError("FreeBuff copied-source layout is not preserved")
    # Workbridge module imports its VT helper by bare module name.
    sys.path.insert(0, str(UPSTREAM.parent))
    ns = {"__file__": str(Path(__file__).resolve()),
          "__name__": "rre_freebuff_transport"}
    exec(compile(source, str(UPSTREAM), "exec"), ns)
    return ns, digest

def main():
    if len(sys.argv) != 2 or sys.argv[1] not in {"check", *MODES}:
        raise SystemExit("Usage: python tools/freebuff-rre-review.py check|sc103|rc30|sc306|sc503|slots|file|operator|ability")
    ns, upstream_hash = build(sys.argv[1] if sys.argv[1] != "check" else "sc103")
    if sys.argv[1] == "check":
        files = [
            ROOT / "tools" / "sc103_luapad_hover_probe.lua",
            ROOT / "tools" / "test_sc103_luapad_hover_probe.lua",
            ROOT / "tools" / "sc103_luapad_copy_result.lua",
            ROOT / "addons" / "RRECollector" / "ui.lua",
            ROOT / "tools" / "verify-rrecollector-ui-pinning.lua",
            ROOT / "docs" / "RRECOLLECTOR-RC30-STALE-PIN-DISPLAY-2026-11-03.md",
        ]
        for addition in (
            "REA-RIFT-SPELLCASTING-SC305-QUEUE-DOSSIER-2026-10-27.md",
            "REA-RIFT-SPELLCASTING-SC306-QUEUE-ENUM-GAP-2026-10-27.md",
            "REA-RIFT-SPELLCASTING-SC303-TIMING-METADATA-2026-10-27.md",
            "REA-RIFT-SPELLCASTING-SC304-TIMING-2026-10-27.md",
            "REA-RIFT-SPELLCASTING-SC501-LOCAL-REJECTION-2026-10-27.md",
            "REA-RIFT-SPELLCASTING-SC502-OUTCOME-2026-11-01.md",
            "REA-RIFT-SPELLCASTING-SC604-INTERIM-MECHANISM-2026-11-01.md",
        ):
            files.append(ROOT / "docs" / addition)
        if not all(x.is_file() for x in files):
            raise RuntimeError("RRE source missing")
        for lane in ("sc306", "sc503", "slots", "file", "operator", "ability"):
            build(lane)
        for path in ("rc30-saved-receipt.mjs", "test-rc30-saved-receipt.mjs", "read-rrecollector-saved.mjs"):
            files.append(ROOT / "tools" / path)
        files.append(ROOT / "docs" / "RRECOLLECTOR-RC30-OPERATOR-ACCEPTANCE-2026-11-03.md")
        files.append(ROOT / "docs" / "RRECOLLECTOR-RC30-EIGHT-SLOT-CORRECTION-2026-11-03.md")
        files.append(ROOT / "docs" / "REA-RIFT-SPELLCASTING-SC103-LEGENDARY-SELECTION-2026-11-03.md")
        if not all(x.is_file() for x in files):
            raise RuntimeError("RC-30 read-only snapshot sources missing")
        print(json.dumps({"status":"validated","upstreamSha256":upstream_hash,
                          "availableModes":list(MODES),"sources":len(files),
                          "modelExecution":False}))
        return
    mode = MODES[sys.argv[1]]
    result = ns["run_test"](mode)
    success = bool(result["review_final_marker_seen"] and
                   result["owned_process_stopped"] and result["probe_folder_cleaned"] and
                   result["review_prompt_sent"])
    print(json.dumps({"rreReview":sys.argv[1],"acceptedCompletion":success,
                      "upstreamSha256":upstream_hash,
                      "actualFreeBuffResponse":result.get("review_visible_excerpt",[])}))
    if not success: raise SystemExit(2)

if __name__ == "__main__":
    main()
