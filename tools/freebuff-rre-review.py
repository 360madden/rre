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

MODES = {"sc103": "freebuff-review-pilot", "rc30": "freebuff-lifecycle-review"}
UPSTREAM = Path(r"C:\work\workbridge-mcp\scripts\freebuff-conpty-probe.py")
UPSTREAM_SHA256 = "c29fbfd898c5fe54e86e34403a79ef4d1107761f4828deed153be4be3de3c07f"
ROOT = Path(__file__).resolve().parent.parent

def replace_once(source: str, old: str, new: str) -> str:
    n = source.count(old)
    if n != 1:
        raise RuntimeError(f"Upstream specialization anchor mismatch ({n}): {old[:70]}")
    return source.replace(old, new, 1)

def build():
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
        '                          ("tools", "test_sc103_luapad_hover_probe.lua")):\n'
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
        raise SystemExit("Usage: python tools/freebuff-rre-review.py check|sc103|rc30")
    ns, upstream_hash = build()
    if sys.argv[1] == "check":
        files = [
            ROOT / "tools" / "sc103_luapad_hover_probe.lua",
            ROOT / "tools" / "test_sc103_luapad_hover_probe.lua",
            ROOT / "addons" / "RRECollector" / "ui.lua",
            ROOT / "tools" / "verify-rrecollector-ui-pinning.lua",
            ROOT / "docs" / "RRECOLLECTOR-RC30-STALE-PIN-DISPLAY-2026-11-03.md",
        ]
        if not all(x.is_file() for x in files):
            raise RuntimeError("RRE source missing")
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
