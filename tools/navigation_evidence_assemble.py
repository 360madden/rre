#!/usr/bin/env python3
"""NAV-006: strict file-only assembler of already-normalized trace fragments.

Caller supplies separate policy/frame/action/sample JSON files and a SHA256 manifest.
Never creates invented timestamps, player positions, clicks or native controls.
"""
from __future__ import annotations
import argparse, hashlib, json, sys
from pathlib import Path
from navigation_stop_evidence import decode, evaluate, _encoded
NAMES=("binding","policy","frame","actions","samples","observationEndMs")
MAX=2_097_152
def assemble(manifest: dict, root: Path) -> dict:
    if not isinstance(manifest,dict) or set(manifest)!={"schemaVersion","kind","files"} or type(manifest["schemaVersion"])!=int or manifest["schemaVersion"]!=1 or manifest["kind"] not in ("synthetic-fixture","recorded-normalized"):
        raise ValueError("invalid manifest")
    files=manifest["files"]
    if not isinstance(files,dict) or set(files)!=set(NAMES):raise ValueError("six source fragments required")
    trace={"schemaVersion":1,"kind":manifest["kind"]}
    receipts={}
    for name in NAMES:
        entry=files[name]
        if not isinstance(entry,dict) or set(entry)!={"path","sha256"}:raise ValueError("invalid source entry")
        rel=entry["path"]
        if not isinstance(rel,str) or not rel or Path(rel).is_absolute() or any(p in (".","..") for p in Path(rel).parts) or "\\" in rel:
            raise ValueError("source path must be relative under manifest directory")
        candidate=(root/rel).resolve()
        if not candidate.is_relative_to(root.resolve()):raise ValueError("source escaped root")
        if candidate.is_symlink():raise ValueError("symlink source rejected")
        raw=candidate.read_bytes()
        if len(raw)>MAX:raise ValueError("source too large")
        actual=hashlib.sha256(raw).hexdigest()
        if not isinstance(entry["sha256"],str) or actual!=entry["sha256"]:raise ValueError("source hash mismatch: "+name)
        trace[name]=decode(raw)
        receipts[name]={"path":rel,"sha256":actual}
    # Validate shape without interpreting success as game acceptance.
    result=evaluate(trace)
    if result["verdict"]=="invalid":raise ValueError("invalid normalized source: "+str(result["reason"]))
    return {"schemaVersion":1,"task":"NAV-006","trace":trace,"sourceReceipts":receipts,"evaluation":result,
            "gameInputSent":False,"liveAccepted":False,"independentReviewPerformed":False}
def main():
    p=argparse.ArgumentParser()
    p.add_argument("--manifest",required=True,type=Path);p.add_argument("--output",type=Path)
    args=p.parse_args()
    try:
        raw=args.manifest.read_bytes()
        if len(raw)>MAX:raise ValueError("manifest too large")
        m=decode(raw)
        out=assemble(m,args.manifest.resolve().parent)
        out["manifestSha256"]=hashlib.sha256(raw).hexdigest()
        data=_encoded(out)
        if args.output:
            with args.output.open("xb") as f:f.write(data)
        sys.stdout.buffer.write(_encoded({"assembled":True,"verdict":out["evaluation"]["verdict"],"telemetrySupportsStop":out["evaluation"]["telemetrySupportsStop"],"t0Accepted":False,"gameInputSent":False,"manifestSha256":out["manifestSha256"]}))
        return 0
    except (ValueError,OSError,TypeError,KeyError,OverflowError) as err:
        sys.stderr.buffer.write(_encoded({"assembled":False,"error":str(err),"gameInputSent":False}))
        return 2
if __name__=="__main__":raise SystemExit(main())
