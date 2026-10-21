#!/usr/bin/env python3
"""Offline evidence bridge: authenticate saved RR2 capture bytes and classify actions.
Never emits a NAV-003 trial without original player samples and approved event/clock binding.
"""
import argparse,hashlib,json,math
from pathlib import Path
def obj(p):
    raw=Path(p).read_bytes()
    if len(raw)>2_097_152: raise ValueError("JSON too large")
    def pairs(kvs):
        d={}
        for k,v in kvs:
            if k in d: raise ValueError("duplicate key")
            d[k]=v
        return d
    return json.loads(raw,object_pairs_hook=pairs,parse_constant=lambda x: (_ for _ in ()).throw(ValueError("nonfinite number")))
def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def assess(capture,action,image_path):
    issues=[]
    if not isinstance(capture,dict) or not isinstance(action,dict):raise ValueError("object inputs required")
    expected=(capture.get("savedImage") or {}).get("sha256")
    img_hash=digest(image_path)
    valid_image=isinstance(expected,str) and len(expected)==64 and expected.lower()==img_hash
    if not valid_image:issues.append("image-hash-mismatch")
    ct=capture.get("target") or {};at=action.get("target") or {}
    identity_keys=("processId","processStartUtcTicks","windowHandle","executableSha256","clientWidth","clientHeight")
    identity=all(k in ct and k in at and ct[k]==at[k] for k in identity_keys)
    if not identity:issues.append("target-identity-mismatch")
    gesture=action.get("action") or {}
    result=action.get("result") or {}
    action_kind="keyboard" if gesture.get("keys") else ("mouse-button" if gesture.get("mouseButton") else ("wheel" if gesture.get("wheelNotches") else "unknown"))
    if action_kind!="mouse-button" or gesture.get("mouseButton")!="left":
        issues.append("not-a-ground-click-candidate")
    # Even a left mouse button is not enough: these RR2 actions lack reviewed client-point evidence.
    issues.append("no-reviewed-client-point-in-action")
    issues.append("no-current-player-trajectory-or-cancel")
    if not result.get("deliverySucceeded") or not result.get("releaseSucceeded"):issues.append("delivery-or-release-unconfirmed")
    capture_ts=capture.get("capturedAtUtc"); action_ts=action.get("startedAtUtc")
    from datetime import datetime
    gap=None
    try:
        c=datetime.fromisoformat(capture_ts.replace("Z","+00:00"))
        a=datetime.fromisoformat(action_ts.replace("Z","+00:00"))
        gap=(a-c).total_seconds()
        if gap<0 or gap>1:issues.append("capture-not-immediate")
    except (TypeError,ValueError,AttributeError):issues.append("capture-action-time-unqualified")
    return {"schemaVersion":1,"kind":"rr2-saved-capture-action-audit","imageSha256":img_hash,
            "imageBytesVerified":valid_image,"targetIdentityMatches":identity,"actionKind":action_kind,
            "captureToActionSeconds":gap,"issues":issues,"navigationTraceProduced":False,
            "trialReady":False,"gameInputSent":False,
            "note":"Image hash and matching target metadata do not certify actual behavior, destination, original visual review or live freshness."}
def main():
    p=argparse.ArgumentParser()
    p.add_argument("--capture",required=True);p.add_argument("--action",required=True);p.add_argument("--image",required=True);p.add_argument("--output")
    a=p.parse_args()
    try:
        r=assess(obj(a.capture),obj(a.action),a.image)
        r["sourceSha256"]={k:digest(v) for k,v in {"capture":a.capture,"action":a.action}.items()}
        out=json.dumps(r,indent=2,sort_keys=True)+"\n"
        if a.output:
            with open(a.output,"x",encoding="utf-8") as f:f.write(out)
        print(out,end="")
        return 0
    except (ValueError,OSError,TypeError) as e:
        print(json.dumps({"error":str(e),"trialReady":False,"gameInputSent":False}))
        return 2
if __name__=="__main__":raise SystemExit(main())
