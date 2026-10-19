#!/usr/bin/env python3
"""V7: run existing offline navigation scanners with immutable provenance receipts.

This does not run the Rift client, attach to a process, send input, import into REA,
modify the original helpers, or install Python packages. Every output is write-once.
"""
from __future__ import annotations

import argparse
import ast
from datetime import datetime, timezone
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import subprocess
import sys
import time

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[3]
SCANNER = {
    "static": ROOT / "tools" / "inspect-navigation-static.py",
    "names": ROOT / "tools" / "inspect-navigation-names.py",
}
EXPECTED_BUILD = "7c356c9dde9e12fcbff3c08d953b0630b48b1510a0ffb36e4ec164606e7b17bd"


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def inventory(wrapper: Path, helper: Path, limit: int = 36) -> dict:
    """Bounded local AST import inventory. Dynamic imports are not claimable."""
    roots = {wrapper.parent.resolve(), helper.parent.resolve()}
    pending = [wrapper.resolve(), helper.resolve()]
    found = {}
    truncated = False
    while pending:
        entry = pending.pop(0)
        if entry in found:
            continue
        if len(found) >= limit:
            truncated = True
            break
        payload = entry.read_bytes()
        found[entry] = {
            "path": str(entry), "sha256": digest(payload), "bytes": len(payload),
            "role": "wrapper" if entry == wrapper.resolve() else
                    "originalHelper" if entry == helper.resolve() else "localImport"
        }
        try:
            tree = ast.parse(payload.decode("utf-8-sig"))
        except (UnicodeError, SyntaxError) as error:
            raise RuntimeError(f"Could not inventory Python imports in {entry}: {error}") from error
        modules = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                modules.extend(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                modules.append(node.module)
        for module in modules:
            name = module.split(".")[0]
            for root in roots:
                candidate = root / (name + ".py")
                if candidate.is_file() and candidate.resolve() not in found and candidate.resolve() not in pending:
                    pending.append(candidate.resolve())
    return {"method": "AST static import graph inside wrapper/helper directories",
            "files": sorted(found.values(), key=lambda v: v["path"].casefold()),
            "completeWithinMethod": not truncated,
            "limitations": ["Dynamic imports and third-party package internals are not enumerated.",
                            "This inventory does not establish which conditional imports execute."]}


def environment_versions() -> dict:
    import pefile
    import capstone
    return {
        "python": sys.version.splitlines()[0],
        "pefile": {
            "moduleVersion": getattr(pefile, "__version__", None),
            "distributionVersion": importlib.metadata.version("pefile")
        },
        "capstone": {
            "moduleVersion": getattr(capstone, "__version__", None),
            "distributionVersion": importlib.metadata.version("capstone"),
            "engineVersion": list(capstone.cs_version())
        }
    }


def collect_parser_warnings(binary: Path) -> dict:
    import pefile
    pe = pefile.PE(str(binary), fast_load=True)
    try:
        pe.parse_data_directories(
            directories=[pefile.DIRECTORY_ENTRY["IMAGE_DIRECTORY_ENTRY_EXCEPTION"]])
        warnings = list(pe.get_warnings())
        roots = len(getattr(pe, "DIRECTORY_ENTRY_EXCEPTION", []))
        content = json.dumps(warnings, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
        return {
            "method": "pefile parse of IMAGE_DIRECTORY_ENTRY_EXCEPTION, unfiltered",
            "runtimeFunctionEntries": roots,
            "count": len(warnings),
            "sha256OfOrderedWarningsJson": digest(content),
            "warnings": warnings,
            "interpretation": "Warnings are retained as observations; no automatic suppression or global unwind correctness claim."
        }
    finally:
        pe.close()


def describe_artifact(kind: str, artifact: dict, anchors: list[str],
                      callers: list[str], references: list[str]) -> dict:
    if artifact.get("schemaVersion") != 1:
        raise ValueError("Unexpected upstream artifact schema version")
    required_safety = ["reaDecompilation", "gameInputSent", "gameProcessAttached", "targetExecuted"]
    for key in required_safety:
        if artifact.get(key, False) is not False:
            raise ValueError(f"Artifact indicates unsafe or unknown state for {key}")
    if kind == "static":
        functions = artifact.get("functions")
        if not isinstance(functions, list):
            raise ValueError("Missing native code window list")
        summary = artifact.get("callerSearchSummary")
        # Allow no caller targets, but require explicit coverage for each requested target.
        if callers and not isinstance(summary, list):
            raise ValueError("Hardened caller summary is missing")
        summary = summary or []
        requested = [hex(int(v, 0)) for v in anchors]
        queried = [hex(int(v, 0)) for v in callers]
        summarized = [e.get("targetRva") for e in summary]
        if summarized != queried:
            raise ValueError("Per-target caller coverage is absent or out of order")
        incomplete_windows = [{
            "beginRva": f["beginRva"],
            "decodedThroughRvaExclusive": f.get("decodedThroughRvaExclusive"),
            "windowTruncated": bool(f.get("windowTruncated")),
            "decodingIncomplete": not bool(f.get("instructionDecodingCoversWindow"))
        } for f in functions if f.get("windowTruncated") or not f.get("instructionDecodingCoversWindow")]
        pending = artifact.get("queueRemaining", None)
        if not isinstance(pending, int):
            raise ValueError("Missing queue completion status")
        accounted = {f.get("anchorRva") for f in functions}
        accounted.update(item.get("rva") for item in artifact.get("unresolvedAnchors", []))
        missing_anchors = [q for q in requested if q not in accounted]
        unscanned_callers = [e["targetRva"] for e in summary if e.get("scanComplete") is not True]
        clipped_callers = [e["targetRva"] for e in summary if e.get("qualifiedResultsTruncated") is True]
        coverage = {
            "requestedAnchors": requested, "unaccountedRequestedAnchors": missing_anchors,
            "callerTargets": queried,
            "callerCoverageByTarget": {
                q: next(({"rawCandidatesScanned": e.get("rawCandidatesScanned", 0),
                          "qualifiedCandidates": e.get("qualifiedCandidates", 0),
                          "qualifiedRetained": e.get("qualifiedRetained", 0),
                          "scanComplete": e.get("scanComplete"),
                          "resultsTruncated": e.get("qualifiedResultsTruncated")} for e in summary if e["targetRva"] == q),
                        {"rawCandidatesScanned": 0, "qualifiedCandidates": 0,
                         "qualifiedRetained": 0, "scanComplete": False,
                         "resultsTruncated": False}) for q in queried
            },
            "reportedFollowUnwindChains": artifact.get("followUnwindChains"),
            "capturedUnwindRegions": len(functions),
            "unresolvedAnchors": artifact.get("unresolvedAnchors", []),
            "pendingRegionQueue": pending,
            "incompleteWindows": incomplete_windows,
            "unscannedCallerTargets": unscanned_callers,
            "qualifiedCallerResultsClipped": clipped_callers,
            "boundedCaptureComplete": pending == 0 and not incomplete_windows and
                                      not unscanned_callers and not clipped_callers and
                                      not missing_anchors,
            "limits": {
                "unwindRegions": 40, "bytesPerRegion": 16384,
                "verifiedCallerSitesPerTarget": 64,
                "method": "Targeted direct E8 rel32; indirect/leaf/tail callers not exhaustively indexed"
            }
        }
        return coverage
    if kind == "names":
        found = artifact.get("references", [])
        ref = [hex(int(v, 0)) for v in references]
        if artifact.get("referenceTargets", []) != sorted(set(ref), key=lambda x: int(x, 0)):
            raise ValueError("Requested reference RVA targets differ from artifact")
        return {
            "referenceTargets": ref,
            "referenceMatchesByTarget": {
                q: sum(e.get("targetRva") == q for e in found) for q in ref
            },
            "queriedTerms": artifact.get("queryTerms", []),
            "termsWithZeroMatches": [k for k, v in artifact.get("termCounts", {}).items() if v == 0],
            "retainedTextMatches": len(artifact.get("stringMatches", [])),
            "stringMatchesTruncated": artifact.get("matchesTruncated") is True,
            "retainedReferenceMatches": len(found),
            "referenceSearchLimit": "RIP LEA / absolute stored pointers only; not exhaustive",
            "boundedCaptureComplete": artifact.get("matchesTruncated") is False,
            "limits": {"textMatchesRetained": 500, "stringScanning": "nonexecutable ASCII/UTF-16LE"}
        }
    raise ValueError(f"Unsupported scanner kind: {kind}")


def cli_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--kind", required=True, choices=sorted(SCANNER))
    p.add_argument("--binary", type=Path, required=True)
    p.add_argument("--helper", type=Path, required=True)
    p.add_argument("--expected-sha256", required=True)
    p.add_argument("--expected-helper-sha256", required=True)
    p.add_argument("--artifact", type=Path, required=True)
    p.add_argument("--manifest", type=Path, required=True)
    p.add_argument("--rva", action="append", default=[])
    p.add_argument("--caller-rva", action="append", default=[])
    p.add_argument("--reference-rva", action="append", default=[])
    p.add_argument("--depth", type=int, default=0, choices=(0, 1, 2))
    p.add_argument("--follow-unwind-chains", action="store_true")
    p.add_argument("--timeout-seconds", type=int, default=90)
    return p.parse_args()


def run(args: argparse.Namespace) -> int:
    artifact_path = args.artifact.resolve()
    manifest_path = args.manifest.resolve()
    if artifact_path == manifest_path:
        raise ValueError("Artifact and manifest must be distinct files")
    # Fail closed before the scanner can change any existing research output.
    if artifact_path.exists() or manifest_path.exists():
        raise FileExistsError("Evidence namespace already exists; choose fresh artifact and manifest paths")
    if not (5 <= args.timeout_seconds <= 300):
        raise ValueError("Timeout outside the bounded 5..300-second allowance")
    if args.kind == "static":
        if not args.rva or args.reference_rva:
            raise ValueError("Static scanner requires RVA anchors and forbids reference-rva")
    elif args.rva or args.caller_rva or args.follow_unwind_chains or args.depth != 0:
        raise ValueError("Names scanner accepts only reference-rva targets")
    if args.expected_sha256.lower() != EXPECTED_BUILD:
        raise ValueError("Not the pinned Rift research build")
    wrapper = SCANNER[args.kind].resolve()
    if not wrapper.is_file():
        raise FileNotFoundError(f"Missing scanner: {wrapper}")
    binary = args.binary.resolve()
    helper = args.helper.resolve()
    source_bytes = binary.read_bytes()
    original_hash = digest(source_bytes)
    helper_hash = digest(helper.read_bytes())
    if original_hash != args.expected_sha256.lower() or helper_hash != args.expected_helper_sha256.lower():
        raise ValueError("Binary/helper SHA256 mismatch; no scanner launched")
    versions = environment_versions()
    inventory_before = inventory(wrapper, helper)
    recorder_path = Path(__file__).resolve()
    recorder_hash = digest(recorder_path.read_bytes())
    cmd = [
        str(Path(sys.executable).resolve()), "-B", str(wrapper),
        "--binary", str(binary), "--helper", str(helper),
        "--output", str(artifact_path),
        "--expected-sha256", original_hash,
        "--expected-helper-sha256", helper_hash
    ]
    if args.kind == "static":
        for q in args.rva:
            cmd.extend(["--rva", q])
        for q in args.caller_rva:
            cmd.extend(["--caller-rva", q])
        cmd.extend(["--depth", str(args.depth)])
        if args.follow_unwind_chains:
            cmd.append("--follow-unwind-chains")
    else:
        for q in args.reference_rva:
            cmd.extend(["--reference-rva", q])
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    started = utc_now()
    start = time.monotonic()
    status = "failed"
    reasons = []
    artifact_metadata = None
    coverage = None
    source_changed = False
    stdout = b""
    stderr = b""
    exit_code = None
    try:
        completed = subprocess.run(
            cmd, cwd=ROOT, env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
            capture_output=True, timeout=args.timeout_seconds, check=False)
        exit_code = completed.returncode
        stdout, stderr = completed.stdout, completed.stderr
        if exit_code != 0:
            reasons.append("Upstream scanner exited nonzero")
        if artifact_path.exists():
            data = artifact_path.read_bytes()
            artifact = json.loads(data)
            artifact_metadata = {
                "path": str(artifact_path), "sha256": digest(data),
                "bytes": len(data), "upstreamSchemaVersion": artifact.get("schemaVersion")
            }
            if artifact.get("sha256") != original_hash or Path(artifact.get("helper", "")).resolve() != helper or \
                    artifact.get("helperSha256") != helper_hash:
                reasons.append("Artifact identity or helper was inconsistent")
            else:
                coverage = describe_artifact(
                    args.kind, artifact, args.rva, args.caller_rva, args.reference_rva)
        elif exit_code == 0:
            reasons.append("Scanner exited zero but wrote no artifact")
    except subprocess.TimeoutExpired as error:
        stdout, stderr = error.stdout or b"", error.stderr or b""
        reasons.append("Upstream scanner deadline exhausted")
        exit_code = None
    except (ValueError, KeyError, TypeError, json.JSONDecodeError) as error:
        reasons.append(f"Evidence parse or coverage failure: {error}")
    # The input and relevant transitive source bytes must remain unchanged
    # across the wrapped scan before their provenance is promoted.
    source_changed = (
        digest(binary.read_bytes()) != original_hash or
        inventory_before != inventory(wrapper, helper) or
        digest(recorder_path.read_bytes()) != recorder_hash
    )
    if source_changed:
        reasons.append("Source, wrapper or discovered local dependency changed during run")
    parser_warnings = collect_parser_warnings(binary)
    if not reasons and exit_code == 0 and coverage is not None:
        status = "completed" if (coverage["boundedCaptureComplete"] and
                                 inventory_before["completeWithinMethod"]) else "partial"
    if status != "completed":
        reasons += ["Coverage is limited or incomplete"] if status == "partial" else []
    manifest = {
        "schemaVersion": 2, "taskId": "M1-003", "purpose": "Exact-run offline source and coverage provenance",
        "status": status, "failuresOrLimitations": reasons,
        "startedUtc": started, "endedUtc": utc_now(),
        "durationMs": round((time.monotonic() - start) * 1000),
        "source": {
            "binary": str(binary), "sha256": original_hash, "bytes": len(source_bytes),
            "originalHelper": str(helper), "helperSha256": helper_hash,
            "sourceInventory": inventory_before, "unchangedDuringRun": not source_changed,
            "recorderTool": {"path": str(recorder_path), "sha256": recorder_hash,
                             "bytes": len(recorder_path.read_bytes())}
        },
        "versions": versions,
        "invocation": {
            "argv": cmd,
            "recorderInvocation": [str(Path(sys.executable).resolve()), "-B", str(recorder_path),
                                   *sys.argv[1:]],
            "workingDirectory": str(ROOT), "timeoutSeconds": args.timeout_seconds,
            "exitCode": exit_code, "stdoutSha256": digest(stdout), "stdoutBytes": len(stdout),
            "stderrSha256": digest(stderr), "stderrBytes": len(stderr),
            "stdoutExcerpt": stdout[:3000].decode("utf-8", errors="replace"),
            "stderrExcerpt": stderr[:3000].decode("utf-8", errors="replace")
        },
        "queries": {
            "kind": args.kind, "rvas": [hex(int(v, 0)) for v in args.rva],
            "callerRvas": [hex(int(v, 0)) for v in args.caller_rva],
            "referenceRvas": [hex(int(v, 0)) for v in args.reference_rva],
            "depth": args.depth, "followUnwindChains": args.follow_unwind_chains
        },
        "artifact": artifact_metadata,
        "coverage": coverage,
        "parserDiagnostics": parser_warnings,
        "safety": {
            "offlineOnly": True, "gameInputSent": False, "gameProcessAttached": False,
            "targetExecuted": False, "gameBinaryModified": False, "reaImport": False
        },
        "interpretation": "This captures a bounded offline search, not function reachability or native navigation operation."
    }
    with manifest_path.open("x", encoding="utf-8", newline="\n") as file:
        json.dump(manifest, file, indent=2, ensure_ascii=False)
        file.write("\n")
    print(json.dumps({
        "status": status, "manifest": str(manifest_path), "artifact": artifact_metadata,
        "warnings": parser_warnings["count"], "requested": manifest["queries"],
        "incomplete": reasons, "sourceCount": len(inventory_before["files"])
    }, ensure_ascii=False))
    return 0 if status == "completed" else 1


if __name__ == "__main__":
    try:
        raise SystemExit(run(cli_args()))
    except (OSError, ValueError) as error:
        print(json.dumps({"status": "preflight-rejected", "error": str(error)}), file=sys.stderr)
        raise SystemExit(2)
