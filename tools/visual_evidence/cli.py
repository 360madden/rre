"""Portable screenshot-evidence packages. No live capture, input or model calls."""
from __future__ import annotations
import argparse
import copy
import html
import io
import json
from pathlib import Path
import platform
import sys
import PIL
from PIL import Image, ImageDraw
from .evidence import (Assets, MAX_FILE, MAX_JSON, MAX_TOTAL, binding, bounded_read, decode_image,
                       digest, integer, journal_rows, json_bytes, load_actions, load_frames,
                       local_path, sha, text, token, vm_identity)
from .matcher import compare, require

VERSION = "1.0.0"
LIMITATIONS = [
    "Saved evidence only: not current VM or game state, and not source authenticity.",
    "A diagnostic pass applies only to selected texture patches and recorded identity linkage.",
    "Capture timestamps are recorded guest-clock claims; host/guest clock synchronization is not inferred.",
    "Manually selected regions may contain UI, animation or occlusion; inspect the preserved images.",
    "No player displacement, numerical camera calibration, entity ID, collision, visibility or pathfinding is qualified.",
    "Machine image checking is separate from independent code review and from a vision-model review.",
    "A consistent journal does not rule out unrecorded human input or unrelated scene animation.",
    "No vision model received these pixels unless a separate actual image-delivery receipt is recorded.",
    "Yellow preview boxes mark baseline sample locations, not tracked object bounds or calibrated landmarks."
]


def encoded(value):
    return (json.dumps(value, indent=2, sort_keys=True, ensure_ascii=True, allow_nan=False) + "\n").encode("utf-8")


def schema(spec):
    require(isinstance(spec, dict) and type(spec.get("schemaVersion")) is int and spec["schemaVersion"] == 1,
            "Unsupported visual evidence schema")
    require(spec.get("kind") == "rre-visual-evidence", "Wrong visual evidence kind")
    require(set(spec) <= {"schemaVersion", "kind", "experimentId", "sourceKind", "expectedVm", "journal", "frames",
                         "actions", "comparisons", "references"}, "Unknown spec member")
    token(spec.get("experimentId"), "experiment ID")
    require(spec.get("sourceKind") in ("recorded", "synthetic"), "Invalid source kind")
    if spec.get("expectedVm") is not None:
        vm_identity(spec["expectedVm"])


def evaluate(spec, root):
    schema(spec)
    assets = Assets(root)
    frames, actions = load_frames(spec, assets), load_actions(spec, assets)
    rows = journal_rows(spec.get("journal"), assets)
    checks = spec.get("comparisons")
    require(isinstance(checks, list) and 1 <= len(checks) <= 8, "Require one to eight comparisons")
    results, used_ids = [], set()
    for check in checks:
        require(isinstance(check, dict) and set(check) <= {"id", "before", "after", "actionIds", "expectation", "points", "settings"},
                "Invalid comparison")
        cid = token(check.get("id"), "comparison ID")
        require(cid not in used_ids, "Duplicate comparison ID")
        used_ids.add(cid)
        a, b = check.get("before"), check.get("after")
        require(isinstance(a, str) and isinstance(b, str) and a in frames and b in frames and a != b, "Invalid frame pair")
        ids = check.get("actionIds")
        require(isinstance(ids, list) and len(ids) <= 8 and all(isinstance(k, str) and k in actions for k in ids) and
                len(set(ids)) == len(ids), "Invalid comparison action IDs")
        selected = [actions[k] for k in ids]
        reasons, command_ids = binding(frames[a], frames[b], selected, rows, spec.get("expectedVm"))
        if frames[a]["image"].size != frames[b]["image"].size:
            metric = {"status": "inconclusive", "reason": "image-dimensions-differ", "patches": []}
        else:
            metric = compare(frames[a]["image"], frames[b]["image"], check.get("points"),
                             check.get("expectation"), check.get("settings", {}))
        results.append({"id": cid, "before": a, "after": b, "actionIds": ids, "commandIds": command_ids,
                        "status": "inconclusive" if reasons else metric["status"], "bindingReasons": reasons,
                        "recordedBinding": "consistent" if not reasons else "unqualified", "visualDiagnostic": metric,
                        "deliverySucceeded": [x["result"]["deliverySucceeded"] for x in selected],
                        "gameplayValidated": False})
    references = {}
    for row in spec.get("references", []):
        require(isinstance(row, dict) and set(row) == {"id", "image", "note"}, "Invalid reference screenshot")
        rid = token(row["id"], "reference ID")
        require(rid not in references and len(references) < 4, "Duplicate or excessive reference screenshots")
        text(row["note"], "reference note")
        references[rid] = {"image": decode_image(assets.get(row["image"])), "note": row["note"]}
    report = {"schemaVersion": 1, "kind": "rre-visual-report", "version": VERSION,
              "experimentId": spec["experimentId"], "sourceKind": spec["sourceKind"], "sourceKindVerification": "declared-by-spec", "live": False,
              "allPredicatesPassed": all(r["status"] == "passed" for r in results),
              "gameplayValidated": False, "independentCodeReviewComplete": False, "visionReview": "not-attempted",
              "runtime": {"python": platform.python_version(), "pillow": PIL.__version__},
              "expectedVm": spec.get("expectedVm"), "results": results, "limitations": LIMITATIONS,
              "frames": {k: {"sha256": f["sha256"], "captureId": f["capture"]["captureId"],
                              "capturedAtUtc": f["capture"]["capturedAtUtc"], "backend": f["capture"]["captureBackend"],
                              "target": f["target"], "preview": "preview-" + k + ".png"} for k, f in frames.items()},
              "references": {k: {"note": v["note"], "qualification": "context-only-unbound",
                                  "preview": "reference-"+k+".png"} for k, v in references.items()}}
    return report, assets, frames, references


def render(report):
    esc = lambda value: html.escape(str(value), quote=True)
    parts = ["<!doctype html><html lang='en'><meta charset='utf-8'><meta name='viewport' content='width=device-width'>",
             "<meta http-equiv='Content-Security-Policy' content=\"default-src 'none'; img-src 'self'; style-src 'unsafe-inline'\">",
             "<title>RRE screenshot evidence</title><style>body{font:16px system-ui;max-width:1400px;margin:30px auto;padding:0 24px;background:#f5f7fa;color:#182b40}section{background:white;border:1px solid #ccd5df;padding:20px;margin:20px 0}img{max-width:100%;height:auto}figure{margin:0} .grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(380px,1fr));gap:20px}pre{white-space:pre-wrap;overflow-wrap:anywhere}code{overflow-wrap:anywhere}.passed{color:#146534}.failed{color:#a51d24}.inconclusive{color:#8a5900}</style>",
             "<h1>Screenshot evidence: " + esc(report["experimentId"]) + "</h1>",
             "<p><strong>" + esc(report["sourceKind"].upper()) + " / OFFLINE</strong> — diagnostic evidence, not live-world qualification.</p>",
             "<p>Command delivery, recorded identity linkage and observed pixel patterns are evaluated separately. Original images and metadata are retained beside this report. Verify complete.json before relying on the package.</p>"]
    for result in report["results"]:
        parts.append("<section><h2>"+esc(result["id"])+" — <span class='"+result["status"]+"'>"+result["status"].upper()+"</span></h2>")
        parts.append("<p>Recorded binding: "+esc(result["recordedBinding"])+". Delivery claims: "+esc(result["deliverySucceeded"])+".</p>")
        parts.append("<div class='grid'>")
        for label in ("before", "after"):
            key = result[label]
            f = report["frames"][key]
            parts.append("<figure><h3>"+label.title()+": "+esc(key)+"</h3><img src='"+f["preview"]+"' alt='"+esc(label+" "+key)+"'><figcaption>"+esc(f["capturedAtUtc"])+"<br><code>"+esc(f["sha256"])+"</code></figcaption></figure>")
        parts.append("</div><pre>"+esc(json.dumps(result, indent=2))+"</pre></section>")
    for key, ref in report["references"].items():
        parts.append("<section><h2>Context only: "+esc(key)+"</h2><p>"+esc(ref["note"])+"</p><img src='"+ref["preview"]+"' alt='Reference screenshot'></section>")
    parts.append("<section><h2>Limitations</h2><ul>"+"".join("<li>"+esc(s)+"</li>" for s in LIMITATIONS)+"</ul></section></html>\n")
    return "".join(parts).encode("utf-8")


def pin(recipe_path, source_root, output):
    """Fill path-only references with hashes without accepting a trial outcome."""
    recipe = json_bytes(bounded_read(recipe_path, MAX_JSON))
    schema(recipe)
    assets = Assets(source_root)
    def visit(value):
        if isinstance(value, dict):
            if set(value) == {"path"}:
                raw = bounded_read(local_path(assets.root, value["path"]))
                value["sha256"] = sha(raw)
                assets.get(value)
            elif set(value) == {"path", "sha256"}:
                assets.get(value)  # Existing pins must match, never silently repin.
            else:
                for item in value.values(): visit(item)
        elif isinstance(value, list):
            for item in value: visit(item)
    visit(recipe)
    evaluate(recipe, source_root)
    with output.open("xb") as stream: stream.write(encoded(recipe))
    return {"spec": str(output), "specSha256": sha(encoded(recipe)), "trialAccepted": False}


def build(spec_path, source_root, output):
    source_raw = bounded_read(spec_path, MAX_JSON)
    spec = json_bytes(source_raw)
    report, assets, frames, references = evaluate(spec, source_root)
    files, remap = {}, {}
    for index, (name, raw) in enumerate(sorted(assets.raw.items())):
        suffix = Path(name).suffix.lower()
        require(suffix in (".json", ".jsonl", ".bmp", ".png", ".jpg", ".jpeg"), "Unsupported asset suffix")
        local = f"asset-{index:03d}" + suffix
        files[local] = raw
        remap[name] = local
    portable = copy.deepcopy(spec)
    def relocate(value):
        if isinstance(value, dict):
            if set(value) == {"path", "sha256"}:
                value["path"] = remap[value["path"]]
            else:
                for v in value.values(): relocate(v)
        elif isinstance(value, list):
            for v in value: relocate(v)
    relocate(portable)
    files["spec.json"], files["source-spec.json"] = encoded(portable), source_raw
    report["specSha256"] = sha(files["spec.json"])
    report["sourceSpecSha256"] = sha(source_raw)
    module_root = Path(__file__).parent
    report["toolSourceHashes"] = {p.name: sha(p.read_bytes()) for p in sorted(module_root.glob("*.py"))}
    report["toolSourceHashes"]["visual-evidence.py"] = sha((module_root.parent/"visual-evidence.py").read_bytes())
    for key, f in frames.items():
        image = f["image"].copy()
        draw = ImageDraw.Draw(image)
        points = {tuple(p) for c in spec["comparisons"] if key in (c["before"], c["after"]) for p in c["points"]}
        for index, (x, y) in enumerate(sorted(points)):
            draw.rectangle((x-7,y-7,x+7,y+7), outline="yellow", width=1)
            draw.text((x+9,y-9), str(index+1), fill="yellow")
        data = io.BytesIO(); image.save(data, format="PNG")
        files["preview-"+key+".png"] = data.getvalue()
    for key, ref in references.items():
        data = io.BytesIO(); ref["image"].save(data, format="PNG")
        files["reference-"+key+".png"] = data.getvalue()
    review = {"schemaVersion": 1, "kind": "rre-visual-review-packet", "specSha256": report["specSha256"],
              "deliveryStatus": "not-attempted", "reviewer": None,
              "instructions": "Review image pixels and exact recorded identities, not filenames. Distinguish visual observations from game semantics. Original frames are unannotated; previews mark manually selected regions. Return source hashes and limitations. No tool or game actions are requested.",
              "images": [{"role": f["id"], "original": f["image"], "preview": "preview-"+f["id"]+".png"} for f in portable["frames"]],
              "contextImages": [{"role": f["id"], "original": f["image"], "note": f["note"],
                                 "qualification": "context-only-unbound"} for f in portable.get("references", [])]}
    files["review-packet.json"], files["report.json"], files["report.html"] = encoded(review), encoded(report), render(report)
    require(len(files) <= 64 and all(0 < len(v) <= MAX_FILE for v in files.values()) and
            sum(map(len, files.values())) <= MAX_TOTAL, "Published package exceeds limits")
    # Prevalidation/encoding precedes directory creation. Failed writes retain an incomplete directory.
    output.mkdir(parents=False, exist_ok=False)
    for name, raw in files.items():
        with (output/name).open("xb") as stream: stream.write(raw)
    receipt = {"schemaVersion": 1, "kind": "rre-visual-publication", "specSha256": report["specSha256"],
               "files": {name: {"bytes": len(raw), "sha256": sha(raw)} for name, raw in files.items()}}
    with (output/"complete.json").open("xb") as stream: stream.write(encoded(receipt))
    return report


def verify(output):
    receipt = json_bytes(bounded_read(local_path(output, "complete.json"), MAX_JSON))
    require(isinstance(receipt, dict) and type(receipt.get("schemaVersion")) is int and receipt["schemaVersion"] == 1 and
            receipt.get("kind") == "rre-visual-publication", "Invalid completion receipt")
    files = receipt.get("files")
    require(isinstance(files, dict) and 5 <= len(files) <= 64, "Invalid publication file list")
    require({"spec.json", "source-spec.json", "report.json", "report.html", "review-packet.json"} <= set(files), "Missing required publication files")
    require({p.name for p in output.iterdir()} == set(files) | {"complete.json"}, "Unexpected or missing package entries")
    total = 0
    for name, item in files.items():
        require("/" not in name and isinstance(item, dict), "Invalid package file")
        raw = bounded_read(local_path(output, name))
        total += len(raw)
        require(total <= MAX_TOTAL, "Package total exceeds limit")
        require(integer(item.get("bytes"), "file size", 1, MAX_FILE) == len(raw) and digest(item.get("sha256")) == sha(raw),
                "Publication size/hash mismatch: " + name)
    spec_raw = bounded_read(output/"spec.json", MAX_JSON)
    spec = json_bytes(spec_raw); schema(spec)
    expected_files = {"spec.json", "source-spec.json", "report.json", "report.html", "review-packet.json"}
    def check_references(value):
        if isinstance(value, dict):
            if set(value) == {"path", "sha256"}:
                name = value["path"]
                require(isinstance(name, str) and "/" not in name and name in files, "Missing referenced asset")
                require(digest(value["sha256"]) == digest(files[name]["sha256"]), "Referenced asset hash mismatch")
                expected_files.add(name)
            else:
                for item in value.values(): check_references(item)
        elif isinstance(value, list):
            for item in value: check_references(item)
    check_references(spec)
    frames = spec.get("frames")
    require(isinstance(frames, list) and 2 <= len(frames) <= 8, "Invalid packaged frames")
    for frame in frames:
        require(isinstance(frame, dict), "Invalid packaged frame entry")
        expected_files.add("preview-"+token(frame.get("id"))+".png")
    references = spec.get("references", [])
    require(isinstance(references, list) and len(references) <= 4, "Invalid packaged references")
    for ref in references:
        require(isinstance(ref, dict), "Invalid packaged reference entry")
        expected_files.add("reference-"+token(ref.get("id"))+".png")
    require(set(files) == expected_files, "Incomplete or unexpected referenced package file set")
    report = json_bytes(bounded_read(output/"report.json", MAX_JSON))
    require(isinstance(report, dict) and type(report.get("schemaVersion")) is int and report["schemaVersion"] == 1 and
            report.get("kind") == "rre-visual-report", "Invalid report schema")
    require(digest(receipt.get("specSha256")) == sha(spec_raw) == report.get("specSha256"), "Publication spec mismatch")
    require(report.get("sourceSpecSha256") == sha(bounded_read(output/"source-spec.json", MAX_JSON)), "Original spec mismatch")
    # File-set verification is separate from recomputation; replay rechecks semantics.
    return {"publicationComplete": True, "specSha256": sha(spec_raw), "files": len(files),
            "meaning": "File-set integrity only, not source authenticity, freshness or gameplay validity"}


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest="command", required=True)
    prepare = sub.add_parser("pin"); prepare.add_argument("--recipe", required=True, type=Path)
    prepare.add_argument("--source-root", required=True, type=Path); prepare.add_argument("--output", required=True, type=Path)
    run = sub.add_parser("run"); run.add_argument("--spec", required=True, type=Path)
    run.add_argument("--source-root", required=True, type=Path); run.add_argument("--output-dir", required=True, type=Path)
    run.add_argument("--require-pass", action="store_true")
    check = sub.add_parser("verify"); check.add_argument("--bundle", required=True, type=Path)
    replay = sub.add_parser("replay"); replay.add_argument("--bundle", required=True, type=Path)
    replay.add_argument("--output-dir", required=True, type=Path)
    a = p.parse_args(argv)
    try:
        if a.command == "pin":
            print(json.dumps(pin(a.recipe, a.source_root, a.output))); return 0
        if a.command == "verify":
            print(json.dumps(verify(a.bundle))); return 0
        if a.command == "replay":
            verify(a.bundle)
            report = build(a.bundle/"spec.json", a.bundle, a.output_dir)
        else:
            report = build(a.spec, a.source_root, a.output_dir)
        verify(a.output_dir)
        states = {r["id"]: r["status"] for r in report["results"]}
        print(json.dumps({"publicationComplete": True, "comparisons": states, "gameplayValidated": False,
                          "report": str(a.output_dir/"report.html")}))
        if getattr(a, "require_pass", False):
            return 3 if "failed" in states.values() else 4 if "inconclusive" in states.values() else 0
        return 0
    except (OSError, ValueError, TypeError, KeyError, OverflowError, RecursionError, PIL.UnidentifiedImageError,
            Image.DecompressionBombWarning, Image.DecompressionBombError) as exc:
        print(json.dumps({"publicationComplete": False, "error": str(exc), "gameplayValidated": False}), file=sys.stderr)
        return 2
