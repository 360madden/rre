"""Host-only Lab-2 capture/move/left-click using the installed vncdotool.

Run with RR2's existing artifacts/tools/control-python/Scripts/python.exe.
Coordinates are pixels in the FULL VMware guest desktop capture, not the RIFT
client image. No guest package, helper installation, or guest-agent input.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys
import time
import uuid

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, r"C:\work\riftreader2")
from scripts import vm_console_native as native
from scripts.run_xyz_workflow import read_review

VMX = Path(r"C:\rift modding\VMs\RIFT-Lab-2\RIFT-Lab.vmx")
VMRUN = Path(r"C:\Program Files\VMware\VMware Workstation\vmrun.exe")


def save(path, value):
    with path.open("x", encoding="utf-8") as stream:
        json.dump(value, stream, indent=2)
        stream.write("\n")


def run(args):
    output = args.output.resolve()
    if not output.is_relative_to(ROOT / "artifacts") or output.exists():
        raise ValueError("fresh RRE artifacts output required")
    config = native.validate_config(VMX, 5962, VMRUN, output, require_files=True)
    output.mkdir(parents=True, exist_ok=False)
    result = {"action": args.action, "hostOnly": True, "backend": "vncdotool",
              "inputMayHaveBeenSent": False, "buttonReleaseSent": False,
              "connectionClosed": False, "consoleMutexReleased": False, "status": "pending"}
    client = None
    try:
        with native.ControlMutex(VMX) as owner:
            if owner.abandoned:
                raise native.Blocked("abandoned-console-owner-requires-review")
            result["beforeIdentity"] = native.collect_identity(config)
            client = native.connect(config)
            try:
                size = native._capture(client, output / "before.png")
                result["desktopSize"] = size
                capture = {"captureId": uuid.uuid4().hex, "image": str(output / "before.png"),
                           "imageSha256": hashlib.sha256((output / "before.png").read_bytes()).hexdigest(),
                           "action": args.action, "position": [args.x, args.y]}
                save(output / "capture.json", capture)
                if args.action != "capture":
                    if (type(args.x) is not int or type(args.y) is not int
                            or not 0 <= args.x < size[0] or not 0 <= args.y < size[1]):
                        raise ValueError("position outside reviewed guest desktop")
                    print(json.dumps({"action": args.action, "desktopPosition": [args.x, args.y]}), flush=True)
                    note = read_review(capture, timeout=40)
                    save(output / "review.json", {"captureId": capture["captureId"], "note": note})
                    native.verify_identity(config, result["beforeIdentity"])
                    # VNC coordinates are connection-local: move and click MUST share this client.
                    result["inputMayHaveBeenSent"] = True
                    client.mouseMove(args.x, args.y)
                    if args.action == "click":
                        try:
                            client.mouseDown(1)
                            time.sleep(0.1)
                        finally:
                            client.mouseUp(1)
                            result["buttonReleaseSent"] = True
                    time.sleep(0.35)
                    if native._capture(client, output / "after.png") != size:
                        raise ValueError("guest desktop geometry changed")
                    result["afterImageSha256"] = hashlib.sha256((output / "after.png").read_bytes()).hexdigest()
                result["afterIdentity"] = native.verify_identity(config, result["beforeIdentity"])
                result["status"] = "completed-awaiting-visual-review"
            finally:
                try:
                    if result["inputMayHaveBeenSent"]:
                        client.mouseUp(1)
                        result["buttonReleaseSent"] = True
                finally:
                    client.disconnect()
                    result["connectionClosed"] = True
                    client = None
        result["consoleMutexReleased"] = True
    except BaseException:
        result["status"] = "blocked"
        raise
    finally:
        save(output / "result.json", result)
    print(json.dumps({"status": result["status"], "output": str(output),
                      "image": str(output / ("before.png" if args.action == "capture" else "after.png")),
                      "hostOnly": True, "buttonReleaseSent": result["buttonReleaseSent"],
                      "connectionClosed": result["connectionClosed"]}), flush=True)
    return result


def parser():
    command = argparse.ArgumentParser(description=__doc__)
    command.add_argument("action", choices=("capture", "move", "click"))
    command.add_argument("x", type=int, nargs="?")
    command.add_argument("y", type=int, nargs="?")
    command.add_argument("--output", type=Path, required=True)
    return command


if __name__ == "__main__":
    args = parser().parse_args()
    try:
        run(args)
    except Exception as error:
        print(json.dumps({"status": "blocked", "errorType": type(error).__name__,
                          "reason": str(error) if isinstance(error, native.Blocked) else "operation failed; inspect retained receipt"}),
              file=sys.stderr)
        raise SystemExit(2)
