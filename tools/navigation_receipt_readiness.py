#!/usr/bin/env python3
"""NAV-004: read-only RR2 receipt readiness audit; never constructs trial data."""
from __future__ import annotations
import argparse, hashlib, json
from pathlib import Path

MAX_BYTES=2_097_152
FIELDS=("coordX","coordY","coordZ")
def load(path):
    raw=Path(path).read_bytes()
    if len(raw)>MAX_BYTES: raise ValueError("oversize")
    def pairs(items):
        out={}
        for k,v in items:
            if k in out: raise ValueError("duplicate key")
            out[k]=v
        return out
    return json.loads(raw,object_pairs_hook=pairs,parse_constant=lambda v: (_ for _ in ()).throw(ValueError("nonfinite")))
def audit(source):
    observations=source.get("observation") if isinstance(source,dict) else None
    rr=observations.get("riftReader2") if isinstance(observations,dict) else None
    inner=rr.get("observation") if isinstance(rr,dict) else None
    fields=inner.get("fields") if isinstance(inner,dict) else None
    player=inner.get("player") if isinstance(inner,dict) else None
    target=observations.get("target") if isinstance(observations,dict) else None
    valid_xyz=isinstance(fields,dict) and all(
        isinstance(fields.get(k),dict) and fields[k].get("status")=="ok"
        and type(fields[k].get("value")) in (int,float) and
        __import__("math").isfinite(fields[k]["value"]) for k in FIELDS)
    player_id=isinstance(player,dict) and player.get("status")=="ok" and isinstance(player.get("value"),str) and bool(player["value"])
    build=isinstance(target,dict) and isinstance(target.get("executableSha256"),str) and len(target["executableSha256"])==64
    has_process=isinstance(target,dict) and type(target.get("processId")) is int and type(target.get("processStartUtcTicks")) is int
    # A retained receipt is not a live freshness attestation.
    findings={
        "historicalPlayerIdentityPresent":bool(player_id),
        "historicalPlayerXYZPresent":bool(valid_xyz),
        "historicalProcessIdentityPresent":bool(has_process),
        "historicalBuildIdentityPresent":bool(build),
        "currentSessionFreshnessVerified":False,
        "sceneIdentityVerified":False,
        "currentC2MSettingVerified":False,
        "currentGestureAndCancelBindingVerified":False,
        "reviewedGroundClickPointVerified":False,
        "originalImageBytesAndActionAssociationVerified":False,
        "timeAlignedBaselineMovementPostCancelSeriesVerified":False,
        "calibratedPositionToleranceVerified":False,
        "exclusiveLiveControlVerified":False,
        "liveApprovalVerified":False
    }
    missing=[name for name,ok in findings.items() if not ok]
    return {"schemaVersion":1,"task":"NAV-004","sourceType":"saved-rr2-delivery-receipt",
            "findings":findings,"missing":missing,"trialReady":False,
            "normalizedTrialProduced":False,"gameInputSent":False,
            "note":"Historical availability is not current readiness; process target is not an entity target."}
def main():
    p=argparse.ArgumentParser()
    p.add_argument("--receipt",required=True)
    p.add_argument("--output",help="New report path only")
    args=p.parse_args()
    try:
        result=audit(load(args.receipt))
        result["receiptSha256"]=hashlib.sha256(Path(args.receipt).read_bytes()).hexdigest()
        raw=(json.dumps(result,indent=2,sort_keys=True)+"\n").encode()
        if args.output:
            with open(args.output,"xb") as f:f.write(raw)
        print(raw.decode(),end="")
        return 0
    except (OSError,ValueError,TypeError,KeyError) as e:
        print(json.dumps({"error":str(e),"trialReady":False,"gameInputSent":False}))
        return 2
if __name__=="__main__":raise SystemExit(main())
