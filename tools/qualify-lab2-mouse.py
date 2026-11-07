"""One reviewed reversible Lab-2 UI click using the existing RR2 controller.

No controller launch/recovery, keyboard input, casting, relative mouse motion,
or new input backend. Run interactively: inspect the printed original capture,
then provide the exact capture-ID review line within 40 seconds.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sys
import threading
import time
from types import SimpleNamespace
import uuid

ROOT = Path(__file__).resolve().parents[1]
RR2 = Path(r"C:\work\riftreader2")
sys.path.insert(0, str(RR2))
from scripts import run_xyz_workflow as common
from scripts import inspect_lab2_workflow as inspection
from scripts.control_client import ControlClient, _capture, _arm, _action
from scripts.ensure_controller import QUEUE
from scripts.nav_access_queue import AccessQueue
from scripts.capture_lab_hp_screenshot import ready_epoch, idle_queue, await_release
from scripts.run_movement_session import ManagedPinnedHost


def require(ok, reason):
    if not ok:
        raise ValueError(reason)


def run(args):
    output = args.output.resolve()
    require(output.is_relative_to(ROOT / "artifacts") and not output.exists(),
            "fresh RRE artifact output required")
    plan = json.loads(args.plan.read_text(encoding="utf-8-sig"))
    require(plan.get("lab") == "lab2" and plan.get("resource") == "vm:rift-lab-2",
            "only the managed Lab-2 resource is allowed")
    host = ManagedPinnedHost(args.plan)
    initial = host.status(require_armed=False)
    target = initial["guest"]["target"]
    require(target["machineName"] == "RIFT-LAB-2"
            and initial["guest"].get("targetedClickVersion") == 1,
            "Lab-2 targeted click unavailable")
    x, y, width, height = args.target
    require(0 <= x and 0 <= y and 4 <= width <= 128 and 4 <= height <= 128
            and x + width <= target["clientWidth"]
            and y + height <= target["clientHeight"], "invalid client rectangle")
    state = {"target": target, "vmIdentity": plan["vmIdentity"]}
    inspection.fresh(host, state)
    epoch = ready_epoch(initial, inspection.expected_game(state), "vm:rift-lab-2")
    output.mkdir(parents=True, exist_ok=False)
    (output / "before").mkdir()
    (output / "after").mkdir()
    (output / "settled").mkdir()
    common.save(output / "intent.json", {"purpose": args.purpose,
                "rectangle": args.target, "target": target,
                "adapterSha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest()})
    queue = AccessQueue(QUEUE)
    request = "rre-lab2-mouse-" + uuid.uuid4().hex
    with queue.dispatch_fence():
        idle_queue(queue, "vm:rift-lab-2", epoch)
        queue.submit(request, "rre-mouse", "C", {"vm:rift-lab-2": epoch},
                     ttl_ms=30000, max_ms=120000, estimated_ms=2000)
        try:
            grant = queue.dispatch(request_id=request)
            require(isinstance(grant, dict) and grant.get("request_id") == request,
                    "own queue grant unavailable")
        except BaseException:
            queue.cancel(request, "rre-mouse")
            raise
    token = grant["token"]
    client = ControlClient(host.config, access={"request_id": request, "token": token})
    done, lost = threading.Event(), threading.Event()

    def heartbeat():
        while not done.wait(8):
            try:
                queue.heartbeat(request, token)
            except Exception:
                lost.set()
                return

    worker = threading.Thread(target=heartbeat, daemon=True)
    worker.start()
    success = False
    try:
        before = datetime.now(timezone.utc)
        capture = _capture(client, output / "before" / "capture")
        inspection.validate_capture(output / "before", state, before, datetime.now(timezone.utc))
        print(json.dumps({"purpose": args.purpose, "clientRectangle": args.target}), flush=True)
        note = common.read_review(capture, timeout=40)
        require(not lost.is_set(), "lease heartbeat failed")
        current = host.status(require_armed=False)
        require(current["guest"]["target"] == target, "target or geometry drift")
        inspection.fresh(host, state)
        queue.heartbeat(request, token)
        _arm(client, output / "before/capture/capture.json", note,
             output / "arm.private.json", expected_capture_id=capture["captureId"])
        action = _action(client, SimpleNamespace(arm=output / "arm.private.json",
            keys="", hold_ms=100, mouse_button="left", dx=0, dy=0, wheel=0,
            click_target=args.target, output=output / "action.json"))
        result = action["result"]["result"]
        require(result["deliverySucceeded"] and result["releaseSucceeded"]
                and not result["targetLost"] and not result["stateUncertain"],
                "mouse delivery/release uncertain")
        before = datetime.now(timezone.utc)
        _capture(client, output / "after" / "capture")
        inspection.validate_capture(output / "after", state, before, datetime.now(timezone.utc))
        # A delivered/released click can precede the game's next visible UI frame.
        # Keep the immediate image and review a separate bounded settled image.
        time.sleep(0.35)
        before = datetime.now(timezone.utc)
        _capture(client, output / "settled" / "capture")
        inspection.validate_capture(output / "settled", state, before, datetime.now(timezone.utc))
        success = True
    finally:
        try:
            common.save(output / "stop.json", common.sanitize(
                client.request("/api/stop", method="POST", payload={})))
        finally:
            done.set()
            worker.join(timeout=10)
            queue.finish(request, token, "succeeded" if success else "failed",
                         [str(output / "intent.json")])
            terminal = await_release(queue, request, "vm:rift-lab-2", epoch, poll_seconds=0.025)
            released = idle_queue(queue, "vm:rift-lab-2", epoch)
            require(terminal == ("succeeded" if success else "failed")
                    and released.get("generation") == grant["lease"]["vm:rift-lab-2"]["generation"] + 1
                    and bool(released.get("cleanup_receipt")), "watchdog cleanup unverified")
            common.save(output / "cleanup.json", {"terminal": terminal,
                "generation": released["generation"], "cleanupReceipt": released["cleanup_receipt"],
                "stopVerified": True})
        final = host.status(require_armed=False)
        require(final["guest"]["target"] == target, "final target drift")
        inspection.fresh(host, state)
        common.save(output / "final-status.json", common.sanitize(final))
    result = {"deliveryVerified": True, "visualResponseVerified": False,
              "cleanupVerified": True, "output": str(output),
              "immediateImage": str(output / "after/capture/image.bmp"),
              "afterImage": str(output / "settled/capture/image.bmp")}
    common.save(output / "result.json", result)
    print(json.dumps(result), flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plan", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--purpose", choices=("open-browser", "close-browser"), required=True)
    parser.add_argument("--target", type=int, nargs=4, required=True)
    args = parser.parse_args()
    try:
        run(args)
    except Exception as error:
        print(json.dumps({"status": "blocked", "errorType": type(error).__name__,
                          "code": getattr(error, "code", None),
                          "output": str(args.output)}), file=sys.stderr)
        raise SystemExit(2)
