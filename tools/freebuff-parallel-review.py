r"""One bounded Workbridge command for two *overlapping* FreeBuff ConPTY reviews.

Uses the established RRE FreeBuff adapter in separate child Python processes,
each with a unique disposable source-only workspace. No edits to source trees,
no game operations, no Ollama, no changes to Workbridge or FreeBuff installation.

Usage (from C:\work\rre):
  C:\Python314\python.exe -B tools\freebuff-parallel-review.py --check
  C:\Python314\python.exe -B tools\freebuff-parallel-review.py --self-test
  C:\Python314\python.exe -B tools\freebuff-parallel-review.py run

A passing session marker establishes a generated FreeBuff review response.
Two overlapping child lifetimes do NOT alone prove overlapping model inference.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parent.parent
ADAPTER = ROOT / "tools" / "freebuff-rre-review.py"
MODES = ("sc103", "rc30")
RESEARCH_MODES = ("sc306", "sc503")
MAX_CHILD_SECONDS = 172
MAX_OUTPUT_CHARS = 720_000
RUN_ID = "rre-freebuff-dual-review-20261103"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds")


def run_child(mode: str, args: list[str], timeout: int = MAX_CHILD_SECONDS) -> dict:
    if not mode or timeout < 1 or timeout > MAX_CHILD_SECONDS:
        raise ValueError("invalid bounded child")
    started = time.perf_counter()
    started_utc = utc_now()
    proc = subprocess.Popen(args, cwd=ROOT, stdin=subprocess.DEVNULL,
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                            text=True, encoding="utf-8", errors="replace",
                            shell=False)
    cleanup_fault = None
    try:
        out, err = proc.communicate(timeout=timeout)
        state = "settled"
    except subprocess.TimeoutExpired:
        state = "timed-out"
        # Only stop this newly created review process tree. Do not affect any
        # other FreeBuff sessions, Workbridge services or RIFT processes.
        if proc.poll() is None and os.name == "nt":
            try:
                result = subprocess.run([r"C:\Windows\System32\taskkill.exe", "/T",
                                         "/F", "/PID", str(proc.pid)],
                                        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                                        timeout=8, check=False)
                if result.returncode != 0:
                    cleanup_fault = "TASKKILL_FAILED"
            except (OSError, subprocess.TimeoutExpired):
                cleanup_fault = "TASKKILL_FAILED"
        if proc.poll() is None:
            try:
                proc.kill()  # Exact child fallback when taskkill failed.
            except OSError:
                cleanup_fault = "DIRECT_CHILD_KILL_FAILED"
        try:
            out, err = proc.communicate(timeout=7)
        except subprocess.TimeoutExpired:
            if proc.poll() is None:
                try:
                    proc.kill()
                except OSError:
                    cleanup_fault = "DIRECT_CHILD_KILL_FAILED"
            try:
                out, err = proc.communicate(timeout=2)
            except subprocess.TimeoutExpired:
                out, err = "", "CHILD_CLEANUP_UNCONFIRMED"
                cleanup_fault = "CHILD_STILL_RUNNING"
    elapsed = time.perf_counter() - started
    ended_utc = utc_now()
    trimmed = out[-MAX_OUTPUT_CHARS:]
    objects = []
    for line in trimmed.splitlines():
        if not line.startswith("{"):
            continue
        try:
            record = json.loads(line)
            if isinstance(record, dict):
                objects.append(record)
        except json.JSONDecodeError:
            pass
    model_record = next((r for r in objects if r.get("mode", "").startswith("freebuff-")), {})
    wrapper = next((r for r in objects if r.get("rreReview") == mode), {})
    return {
        "mode": mode,
        "state": state,
        "exitCode": proc.returncode,
        "pid": proc.pid,
        "startUtc": started_utc,
        "endUtc": ended_utc,
        "startedMonotonic": started,
        "endedMonotonic": time.perf_counter(),
        "elapsedSeconds": round(elapsed, 3),
        "receiptSha256": hashlib.sha256(out.encode("utf-8", errors="replace")).hexdigest(),
        "outputTruncated": len(out) > MAX_OUTPUT_CHARS or bool(model_record.get("rolling_tail_truncated")),
        "markerObserved": bool(model_record.get("review_final_marker_seen")),
        "markerMode": model_record.get("mode"),
        "modelObservationSeconds": model_record.get("review_observation_seconds"),
        "promptSent": bool(model_record.get("review_prompt_sent")),
        "ownedChildStopped": bool(model_record.get("owned_process_stopped")),
        "tempFolderCleaned": bool(model_record.get("probe_folder_cleaned")),
        "adapterCompletion": bool(wrapper.get("acceptedCompletion")),
        "reviewLines": relevant_lines(model_record),
        "errorTail": err[-650:] if state != "settled" or proc.returncode != 0 else "",
        "cleanupFault": cleanup_fault,
    }


def relevant_lines(record: dict) -> list[str]:
    candidates = (record.get("review_visible_lines") or []) + (record.get("review_visible_excerpt") or [])
    found = []
    for item in candidates:
        if not isinstance(item, str):
            continue
        line = item.strip()
        if len(line) < 10 or len(line) > 450:
            continue
        low = line.lower()
        if any(w in low for w in (
            "freebuff can", "connect hubspot", "session active", "hours remaining",
            "end session", "thinking", "working...", "may use data", "model select",
        )):
            continue
        if any(w in low for w in (
            "defect", "gap", "test:", "line ", "no_new_issue", "no_blockers",
            "review_end_", "lifecycle_done_", "failure", "source",
            "ui.lua:", "rollback", "state.", "candidate", "timeout",
            "no_mapping", "no_new_evidence", "queue", "channel",
            "interrupt", "sampling", "105ms", "insufficient",
        )) and line not in found:
            found.append(line[:250])
    return found[:11]


def overlap_seconds(records: list[dict]) -> float:
    if len(records) < 2:
        return 0.0
    return round(max(0.0, min(r["endedMonotonic"] for r in records) -
                     max(r["startedMonotonic"] for r in records)), 3)


def clean_summary(records: list[dict], run_id: str = RUN_ID) -> dict:
    safe = [{k: v for k, v in r.items()
             if k not in ("pid", "startedMonotonic", "endedMonotonic")}
            for r in records]
    overlap = overlap_seconds(records)
    def verified_worker(r: dict) -> bool:
        return bool(r.get("state") == "settled" and r.get("exitCode") == 0 and
                    r.get("promptSent") and r.get("markerObserved") and
                    r.get("adapterCompletion") and r.get("ownedChildStopped") and
                    r.get("tempFolderCleaned"))
    # all([]) is True in Python. Require the two distinct assigned reviewers
    # before accepting the aggregate, even when a worker result is missing.
    two_distinct = (len(records) == 2 and
                    len({r.get("mode") for r in records}) == 2 and
                    all(isinstance(r.get("mode"), str) and r["mode"] for r in records))
    all_pass = two_distinct and all(verified_worker(r) for r in records)
    return {
        "runId": run_id,
        "status": "completed" if all_pass else "incomplete",
        "actualChildProcessOverlapSeconds": overlap,
        "modelInferenceOverlapIndependentlyProved": False,
        "freebuffReviewSessions": len(records),
        "completedReviewSessions": sum(verified_worker(r) for r in records),
        "workers": safe,
        "gameActionsRequested": False,
        "modelOsSandboxVerified": False,
        "reviewersUseDisposableSourceCopies": True,
        "oneRreMainWriter": True,
    }


def start_real(modes: tuple[str, str] = MODES) -> dict:
    command = [sys.executable, "-B", str(ADAPTER), "check"]
    p = subprocess.run(command, cwd=ROOT, capture_output=True, text=True,
                       timeout=25, check=False)
    if p.returncode != 0:
        raise RuntimeError("adapter preflight failed: " + p.stderr[-350:])
    if modes not in (MODES, RESEARCH_MODES):
        raise ValueError("Only fixed, reviewed FreeBuff waves are supported")
    command_sets = [[sys.executable, "-B", str(ADAPTER), mode] for mode in modes]
    with ThreadPoolExecutor(max_workers=2) as executor:
        future_a = executor.submit(run_child, modes[0], command_sets[0])
        future_b = executor.submit(run_child, modes[1], command_sets[1])
        records = [future_a.result(), future_b.result()]
    suffix = "research-sc306-sc503" if modes == RESEARCH_MODES else "sc103-rc30"
    return clean_summary(records, RUN_ID + "-" + suffix)


def self_test() -> dict:
    # Each fake process sleeps independently; no FreeBuff or network involved.
    fake = ("import json,time; a=time.perf_counter(); time.sleep(0.85); "
            "print(json.dumps({'mode':'fake','started':a,"
            "'ended':time.perf_counter()}))")
    with ThreadPoolExecutor(max_workers=2) as executor:
        f1 = executor.submit(run_child, "fake-a", [sys.executable, "-B", "-c", fake], 8)
        f2 = executor.submit(run_child, "fake-b", [sys.executable, "-B", "-c", fake], 8)
        rec = [f1.result(), f2.result()]
    overlap = overlap_seconds(rec)
    if overlap < 0.30 or not all(r["exitCode"] == 0 for r in rec):
        raise AssertionError("supervisor failed to overlap isolated child processes")
    return {
        "status": "passed",
        "fakeWorkers": len(rec),
        "childLifetimeOverlapSeconds": overlap,
        "noModelCalls": True,
        "noSourceModification": True,
    }


def main(argv: list[str]) -> int:
    if argv == ["--check"]:
        if not ADAPTER.is_file():
            raise RuntimeError("RRE FreeBuff adapter missing")
        p = subprocess.run([sys.executable, "-B", str(ADAPTER), "check"],
                           cwd=ROOT, capture_output=True, text=True,
                           timeout=25, check=False)
        if p.returncode != 0:
            raise RuntimeError("FreeBuff adapter preflight failed: " + p.stderr[-400:])
        print(json.dumps({"status": "validated", "adapter": str(ADAPTER.relative_to(ROOT)),
                          "modes": MODES, "researchModes": RESEARCH_MODES,
                          "noModelExecution": True}))
        return 0
    if argv == ["--self-test"]:
        print(json.dumps(self_test(), ensure_ascii=True))
        return 0
    if argv in (["run"], ["research"]):
        modes = RESEARCH_MODES if argv == ["research"] else MODES
        result = start_real(modes)
        print(json.dumps(result, ensure_ascii=True))
        return 0 if result["status"] == "completed" else 2
    raise SystemExit("Usage: python -B tools/freebuff-parallel-review.py --check|--self-test|run|research")


if __name__ == "__main__":
    try:
        raise SystemExit(main(sys.argv[1:]))
    except Exception as exc:
        print(json.dumps({"status": "failed", "error": str(exc)[:500]}),
              file=sys.stderr)
        raise SystemExit(1)
